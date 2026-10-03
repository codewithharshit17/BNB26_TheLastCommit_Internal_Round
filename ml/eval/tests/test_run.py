import json

import ml.eval.run as evaluation


def live_attempt(label="index_1_based", answer="10"):
    return {
        "item_id": "test",
        "family": "indexing",
        "signature": {"real": "20", "index_1_based": "10", "range_1_to_n": "30"},
        "answer": answer,
        "confidence": 5,
        "misconception": label,
        "student_type": "clean",
    }


def test_bayesian_evaluation_returns_metrics():
    result = evaluation.bayesian_predictions([live_attempt()])
    assert result["count"] == 1
    assert 0 <= result["accuracy"] <= 1


def test_classifier_evaluation_returns_metrics():
    attempts = [live_attempt("index_1_based"), live_attempt("range_1_to_n", "30"), live_attempt("add_before_div", "10")]
    result = evaluation.evaluate_classifier(attempts)
    assert {"logistic_regression", "gradient_boosting", "split"} <= result.keys()
    assert all(0 <= result[name]["accuracy"] <= 1 for name in ("logistic_regression", "gradient_boosting"))


def test_classifier_ablations_are_explicit():
    attempts = [live_attempt("index_1_based"), live_attempt("range_1_to_n", "30"), live_attempt("add_before_div", "10")]
    result = evaluation.evaluate_ablations(attempts)
    assert set(result) == {"full", "without_interpreter_match", "without_confidence"}


def test_probe_paths_return_zero_one_two_metrics():
    attempts = [live_attempt(), live_attempt("range_1_to_n", "30")]
    items = [{"item_id": "test", "signature": attempts[0]["signature"], "family": "indexing"}]
    for count in range(3):
        information_gain_result = evaluation.bayesian_predictions(attempts, count, "information_gain", items=items)
        random_result = evaluation.bayesian_predictions(attempts, count, "random", items=items)
        assert information_gain_result["count"] == random_result["count"] == 2


def test_false_resolution_returns_both_rates():
    result = evaluation.false_resolution_experiment()
    assert "naive_false_resolution_rate" in result
    assert "relearn_false_resolution_rate" in result
    assert result["naive_false_resolution_rate"] == 1.0
    assert result["relearn_false_resolution_rate"] == 0.0


def test_heldout_is_excluded_from_live_hypotheses_and_detected_unknown():
    assert "index_from_m1" not in evaluation.LIVE_HYPOTHESES
    attempt = live_attempt("index_from_m1", "30")
    attempt["signature"] = {"real": "20", "index_1_based": "10", "index_from_m1": "30"}
    result = evaluation.heldout_evaluation([attempt])
    assert result["unknown_fraction"] == 1.0
    assert result["confidently_mislabelled_fraction"] == 0.0


def test_run_writes_required_metrics_json(tmp_path):
    output = tmp_path / "metrics.json"
    result = evaluation.run(seed=3, output_path=output)
    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved["seed"] == 3
    assert saved["dataset_size"] == result["dataset_size"]
    assert {"bayesian", "classifier", "llm_zero_shot", "probes", "held_out"} <= saved.keys()
