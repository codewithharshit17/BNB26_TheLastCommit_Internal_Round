import argparse
import json
import os
import random
from copy import deepcopy
from pathlib import Path

from engine.rewrites import LIVE_REGISTRY, REGISTRY
from engine.simulator.students import simulate_attempt
from ml.baselines.llm_zero_shot import LLMConfigurationError, predict as llm_predict
from ml.classifier import build_dataset, get_feature_names, grouped_split, predict as classifier_predict, train_models
from ml.posterior import update
from ml.probes import select_probe

from .metrics import report


SEED = 42
LIVE_HYPOTHESES = [entry["id"] for entry in LIVE_REGISTRY]
HELD_OUT = [entry["id"] for entry in REGISTRY if entry["held_out"]]


def _items():
    raw = [
        ("index-a", "indexing", "a = [10, 20, 30]\nprint(a[1])"),
        ("index-b", "indexing", "a = [10, 20, 30]\nprint(a[2])"),
        ("range-a", "range", "for i in range(3):\n    print(i)"),
        ("range-b", "range", "for i in range(4):\n    print(i)"),
        ("precedence-a", "precedence", "print(10 + 20 / 3)"),
        ("precedence-b", "precedence", "print(10 - 20 / 3)"),
    ]
    from engine.signature import signature
    return [{"item_id": item_id, "family": family, "code": code, "signature": signature(code)} for item_id, family, code in raw]


def _live_attempt(attempt):
    result = deepcopy(attempt)
    result["signature"] = {key: value for key, value in attempt["signature"].items() if key == "real" or key in LIVE_HYPOTHESES}
    return result


def generate_dataset(seed=SEED, repetitions=25, items=None):
    """Generate a small deterministic dataset from real engine signatures."""
    rng = random.Random(seed)
    items = _items() if items is None else items
    attempts = []
    for item in items:
        for target in LIVE_HYPOTHESES:
            if item["signature"].get(target) == item["signature"].get("real"):
                continue
            target_item = {**item, "misconception": target}
            for _ in range(repetitions):
                attempts.append(_live_attempt(simulate_attempt("clean", target_item, rng)))
                attempts.append(_live_attempt(simulate_attempt("noisy", target_item, rng)))
            mixed = {**item, "misconceptions": [target, "index_1_based" if target != "index_1_based" else "range_1_to_n"]}
            attempts.append(_live_attempt(simulate_attempt("mixed", mixed, rng)))
        learner_item = {**item, "misconception": target, "intervened": True}
        learner_attempt = simulate_attempt("true_learner", learner_item, rng)
        learner_attempt["misconception"] = "correct"
        attempts.append(_live_attempt(learner_attempt))
        patcher_item = {**item, "misconception": target, "intervened": True}
        transfer_item = {**item, "misconception": target, "intervened": True, "is_transfer": True}
        attempts.append(_live_attempt(simulate_attempt("patcher", patcher_item, rng)))
        attempts.append(_live_attempt(simulate_attempt("patcher", transfer_item, rng)))
    heldout = HELD_OUT[0] if HELD_OUT else "index_from_m1"
    for item in items[:2]:
        target_item = {**item, "misconception": heldout}
        for _ in range(max(2, repetitions // 2)):
            attempts.append(simulate_attempt("unknown", target_item, rng))
    return attempts


def _prior():
    hypotheses = ["correct", *LIVE_HYPOTHESES, "unknown"]
    share = 1 / len(hypotheses)
    return {hypothesis: share for hypothesis in hypotheses}


def bayesian_predictions(attempts, probes=0, probe_mode=None, seed=SEED, items=None):
    rng = random.Random(seed)
    items = _items() if items is None else items
    predictions = []
    labels = []
    for attempt in attempts:
        posterior = update(_prior(), attempt.get("signature", {}), attempt.get("answer"), attempt.get("confidence", 3))
        candidates = [_live_attempt(item) for item in items if item["item_id"] != attempt.get("item_id")]
        used = set()
        for _ in range(probes):
            available = [item for item in candidates if item["item_id"] not in used]
            if not available:
                break
            if probe_mode == "random":
                probe = rng.choice(available)
            else:
                probe = select_probe(posterior, available)
            if probe is None:
                break
            used.add(probe["item_id"])
            probe_attempt = simulate_attempt(attempt.get("student_type", "clean"), {**probe, "misconception": attempt.get("misconception")}, rng)
            posterior = update(posterior, probe["signature"], probe_attempt["answer"], probe_attempt["confidence"])
        predictions.append(max(posterior, key=posterior.get))
        labels.append(attempt.get("misconception"))
    return report(predictions, labels)


def evaluate_classifier(attempts):
    supported = [attempt for attempt in attempts if attempt.get("misconception") in LIVE_HYPOTHESES]
    train, test, train_ids, test_ids = grouped_split(supported, test_size=0.25, random_state=SEED)
    families = sorted({attempt.get("family") for attempt in supported})
    supported_train, supported_test, supported_metadata = _supported_label_split(supported)
    return {
        "supported_label": _fit_classifier_split(supported_train, supported_test, LIVE_HYPOTHESES, families, supported_metadata),
        "held_out_generalization": _fit_classifier_split(
            train, test, LIVE_HYPOTHESES, families,
            {"train_ids": sorted(train_ids), "test_ids": sorted(test_ids), "train_count": len(train), "test_count": len(test)},
        ),
    }


def _fit_classifier_split(train, test, hypotheses, families, split_metadata=None):
    names = get_feature_names(hypotheses, families)
    X, y = build_dataset(train, hypotheses, families)
    models = train_models(X, y, names)
    result = {}
    for name, bundle in models.items():
        predictions = [classifier_predict(attempt, bundle)["predicted_misconception"] for attempt in test]
        result[name] = report(predictions, [attempt["misconception"] for attempt in test])
    result["split"] = split_metadata or {"train_count": len(train), "test_count": len(test)}
    return result


def _supported_label_split(attempts):
    """Hold out one item group per supported label while retaining labels."""
    grouped = {}
    for attempt in attempts:
        grouped.setdefault(attempt.get("misconception"), {}).setdefault(attempt.get("item_id"), []).append(attempt)
    train, test = [], []
    train_items, test_items = set(), set()
    for label in sorted(grouped):
        item_ids = sorted(grouped[label])
        if len(item_ids) < 2:
            for rows in grouped[label].values():
                train.extend(rows)
            train_items.update(item_ids)
            continue
        held_item = item_ids[-1]
        for item_id, rows in grouped[label].items():
            (test if item_id == held_item else train).extend(rows)
            (test_items if item_id == held_item else train_items).add(item_id)
    return train, test, {"train_item_ids": sorted(train_items), "test_item_ids": sorted(test_items), "train_count": len(train), "test_count": len(test)}


def evaluate_ablations(attempts):
    supported = [attempt for attempt in attempts if attempt.get("misconception") in LIVE_HYPOTHESES]
    train, test, _ = _supported_label_split(supported)
    families = sorted({attempt.get("family") for attempt in supported})
    full_names = get_feature_names(LIVE_HYPOTHESES, families)
    variants = {
        "full": full_names,
        "without_interpreter_match": [name for name in full_names if not name.startswith("match_")],
        "without_confidence": [name for name in full_names if name != "confidence"],
    }
    result = {}
    for variant, names in variants.items():
        X, y = build_dataset(train, LIVE_HYPOTHESES, families)
        indices = [full_names.index(name) for name in names]
        models = train_models(X[:, indices], y, names)
        result[variant] = {}
        for model_name, bundle in models.items():
            predictions = []
            for attempt in test:
                features = build_dataset([attempt], LIVE_HYPOTHESES, families)[0][:, indices]
                predictions.append(bundle["model"].predict(features)[0])
            result[variant][model_name] = report(predictions, [attempt["misconception"] for attempt in test])
    return result


def evaluate_llm(attempts, seed=SEED, limit=200):
    subset = attempts[:limit]
    if not os.getenv("LLM_API_KEY"):
        return {"status": "skipped", "count": 0, "reason": "LLM_API_KEY is not configured"}
    predictions = []
    labels = []
    hypotheses = [{"id": key, "description": key} for key in LIVE_HYPOTHESES]
    for attempt in subset:
        try:
            result = llm_predict(attempt, hypotheses)
        except LLMConfigurationError as exc:
            return {"status": "skipped", "count": 0, "reason": str(exc)}
        predictions.append(result["prediction"])
        labels.append(attempt.get("misconception"))
    result = report(predictions, labels)
    result.update({"status": "complete", "count": len(subset)})
    return result


def confusable_subset(attempts):
    families = {"indexing", "range", "precedence"}
    result = []
    for attempt in attempts:
        if attempt.get("family") not in families:
            continue
        signature = _live_attempt(attempt)["signature"]
        matches = [hypothesis for hypothesis in LIVE_HYPOTHESES if signature.get(hypothesis) == attempt.get("answer")]
        if attempt.get("answer") == signature.get("real"):
            matches.append("correct")
        if len(set(matches)) >= 2:
            result.append(attempt)
    return result


def probe_candidate_pool(items, item_id=None):
    """Return the common live candidate pool used by both probe strategies."""
    return sorted(item["item_id"] for item in items if item["item_id"] != item_id)


def false_resolution_experiment(seed=SEED, discriminator_passes=2, surface_forms=2):
    item = _items()[0]
    patcher = {**item, "misconception": "index_1_based", "intervened": True}
    rng = random.Random(seed)
    exact = simulate_attempt("patcher", patcher, rng)["answer"] == item["signature"]["real"]
    transfer = {**item, "misconception": "index_1_based", "intervened": True, "is_transfer": True}
    transfer_wrong = simulate_attempt("patcher", transfer, rng)["answer"] != item["signature"]["real"]
    naive_false = int(exact and transfer_wrong)
    relearn_false = int(exact and discriminator_passes >= 2 and surface_forms >= 2 and not transfer_wrong)
    return {"naive_false_resolution_rate": float(naive_false), "relearn_false_resolution_rate": float(relearn_false), "thresholds": {"discriminator_passes": discriminator_passes, "surface_forms": surface_forms, "delayed_retest": True}}


def heldout_evaluation(attempts, threshold=0.8):
    heldout = [attempt for attempt in attempts if attempt.get("misconception") in HELD_OUT]
    unknown = 0
    confident_mislabel = 0
    for attempt in heldout:
        posterior = update(_prior(), _live_attempt(attempt)["signature"], attempt["answer"], attempt["confidence"])
        top = max(posterior, key=posterior.get)
        if top == "unknown":
            unknown += 1
        elif posterior[top] >= threshold:
            confident_mislabel += 1
    count = len(heldout)
    return {"count": count, "unknown_fraction": unknown / count if count else None, "confidently_mislabelled_fraction": confident_mislabel / count if count else None, "confidence_threshold": threshold}


def run(seed=SEED, output_path=None):
    items = _items()
    attempts = generate_dataset(seed, items=items)
    confusable = confusable_subset(attempts)
    confusable_eval = [a for a in confusable if a.get("misconception") in LIVE_HYPOTHESES or a.get("misconception") == "correct"]
    metrics = {
        "seed": seed,
        "dataset_size": len(attempts),
        "misconception_ids": LIVE_HYPOTHESES,
        "held_out_ids": HELD_OUT,
        "models": ["bayesian", "logistic_regression", "gradient_boosting", "llm_zero_shot"],
        "bayesian": bayesian_predictions([a for a in attempts if a.get("misconception") in LIVE_HYPOTHESES], items=items),
        "classifier": evaluate_classifier(attempts),
        "ablations": evaluate_ablations(attempts),
        "llm_zero_shot": evaluate_llm([a for a in attempts if a.get("misconception") in LIVE_HYPOTHESES], seed),
        "confusable": {"families": sorted({a.get("family") for a in confusable}), "count": len(confusable), "bayesian": bayesian_predictions(confusable_eval, items=items), "probes": {str(n): {"information_gain": bayesian_predictions(confusable_eval, n, "information_gain", seed, items), "random": bayesian_predictions(confusable_eval, n, "random", seed, items)} for n in range(3)}},
        "probe_candidate_pool": probe_candidate_pool(items),
        "probes": {str(n): {"information_gain": bayesian_predictions([a for a in attempts if a.get("misconception") in LIVE_HYPOTHESES], n, "information_gain", seed, items), "random": bayesian_predictions([a for a in attempts if a.get("misconception") in LIVE_HYPOTHESES], n, "random", seed, items)} for n in range(3)},
        "false_resolution": false_resolution_experiment(seed),
        "held_out": heldout_evaluation(attempts),
    }
    output = Path(output_path or "eval/out/metrics.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8")
    return metrics


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--output", default="eval/out/metrics.json")
    args = parser.parse_args(argv)
    metrics = run(args.seed, args.output)
    print(json.dumps({"output": args.output, "dataset_size": metrics["dataset_size"]}))


if __name__ == "__main__":
    main()
