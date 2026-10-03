import math
import random
from collections.abc import Mapping

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression


REAL_FEATURE = "answer_is_real"
CONFIDENCE_FEATURE = "confidence"
MATCH_COUNT_FEATURE = "matched_hypotheses"


def _signature(attempt):
    if not isinstance(attempt, Mapping):
        return {}
    value = attempt.get("signature", attempt.get("sig"))
    if value is None and isinstance(attempt.get("item"), Mapping):
        value = attempt["item"].get("signature")
    return value if isinstance(value, Mapping) else {}


def _family(attempt):
    if not isinstance(attempt, Mapping):
        return None
    family = attempt.get("family")
    if family is None and isinstance(attempt.get("item"), Mapping):
        family = attempt["item"].get("family")
    return str(family) if family is not None else None


def _hypotheses(signature):
    return sorted(
        hypothesis
        for hypothesis in signature
        if hypothesis not in {"real", "unknown"} and isinstance(hypothesis, str)
    )


def get_feature_names(hypotheses=(), families=()):
    """Return the deterministic feature order used by this module."""
    names = [f"match_{hypothesis}" for hypothesis in sorted(set(hypotheses))]
    names.extend([REAL_FEATURE, CONFIDENCE_FEATURE, MATCH_COUNT_FEATURE])
    names.extend(f"family_{family}" for family in sorted(set(families)))
    return names


def extract_features(attempt, hypotheses=None, families=None):
    """Extract an ordered feature dictionary from one simulated attempt.

    An attempt contains ``signature``, ``answer``, ``confidence`` and may
    contain ``family``. ``hypotheses`` and ``families`` freeze the schema for
    inference; when omitted they are inferred from this attempt.
    """
    signature = _signature(attempt)
    answer = attempt.get("answer") if isinstance(attempt, Mapping) else None
    selected_hypotheses = _hypotheses(signature) if hypotheses is None else sorted(set(hypotheses))
    selected_families = (
        [_family(attempt)] if _family(attempt) is not None else []
    ) if families is None else sorted(set(families))

    features = {}
    for hypothesis in selected_hypotheses:
        features[f"match_{hypothesis}"] = int(answer == signature.get(hypothesis))
    features[REAL_FEATURE] = int(answer == signature.get("real"))
    confidence = attempt.get("confidence", 0) if isinstance(attempt, Mapping) else 0
    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.0
    features[CONFIDENCE_FEATURE] = confidence if math.isfinite(confidence) else 0.0
    features[MATCH_COUNT_FEATURE] = sum(
        answer == signature.get(hypothesis) for hypothesis in selected_hypotheses
    )
    family = _family(attempt)
    for known_family in selected_families:
        features[f"family_{known_family}"] = int(family == known_family)
    return features


def _label(attempt):
    if not isinstance(attempt, Mapping):
        raise ValueError("attempt must be a mapping")
    for key in ("misconception", "misconception_id", "label", "target"):
        if key in attempt:
            return attempt[key]
    raise ValueError("attempt is missing a ground-truth misconception label")


def _schema(attempts):
    hypotheses = set()
    families = set()
    for attempt in attempts:
        hypotheses.update(_hypotheses(_signature(attempt)))
        family = _family(attempt)
        if family is not None:
            families.add(family)
    return sorted(hypotheses), sorted(families)


def build_dataset(attempts, hypotheses=None, families=None):
    """Convert simulated attempts into ``(X, y)`` using one shared schema."""
    attempts = list(attempts)
    inferred_hypotheses, inferred_families = _schema(attempts)
    hypotheses = inferred_hypotheses if hypotheses is None else sorted(set(hypotheses))
    families = inferred_families if families is None else sorted(set(families))
    names = get_feature_names(hypotheses, families)
    rows = [extract_features(attempt, hypotheses, families) for attempt in attempts]
    X = np.asarray([[row[name] for name in names] for row in rows], dtype=float)
    y = np.asarray([_label(attempt) for attempt in attempts])
    return X, y


def grouped_split(attempts, test_size=0.25, random_state=42):
    """Split attempts by misconception label, never by individual row.

    Returns ``train_attempts, test_attempts, train_ids, test_ids``. With fewer
    than two groups, all attempts remain in training and the test set is empty.
    """
    attempts = list(attempts)
    groups = sorted({_label(attempt) for attempt in attempts})
    if len(groups) < 2:
        return attempts, [], set(groups), set()

    count = max(1, math.ceil(len(groups) * float(test_size)))
    count = min(count, len(groups) - 1)
    shuffled = groups[:]
    random.Random(random_state).shuffle(shuffled)
    test_ids = set(shuffled[:count])
    train_ids = set(groups) - test_ids
    train = [attempt for attempt in attempts if _label(attempt) in train_ids]
    test = [attempt for attempt in attempts if _label(attempt) in test_ids]
    return train, test, train_ids, test_ids


def train_models(X, y=None, feature_names=None):
    """Train LogisticRegression and GradientBoostingClassifier models.

    Returns model bundles containing the estimator and feature metadata.
    """
    if y is None:
        attempts = list(X)
        hypotheses, families = _schema(attempts)
        X, y = build_dataset(attempts, hypotheses, families)
        if feature_names is None:
            feature_names = get_feature_names(hypotheses, families)
    X = np.asarray(X, dtype=float)
    y = np.asarray(y)
    if X.ndim != 2 or len(X) != len(y) or len(y) == 0:
        raise ValueError("X and y must contain the same non-zero number of rows")
    if len(set(y.tolist())) < 2:
        raise ValueError("at least two misconception classes are required")
    names = list(feature_names or [f"feature_{index}" for index in range(X.shape[1])])
    models = {
        "logistic_regression": LogisticRegression(max_iter=1000, random_state=42),
        "gradient_boosting": GradientBoostingClassifier(random_state=42),
    }
    return {
        name: {"model": model.fit(X, y), "feature_names": names, "model_name": name}
        for name, model in models.items()
    }


def _bundle_model(model):
    if isinstance(model, Mapping) and "model" in model:
        return model["model"], model
    return model, {"model_name": type(model).__name__, "feature_names": None}


def classify(features, model=None):
    """Classify one feature vector with a trained sklearn model."""
    if model is None:
        raise ValueError("a trained model is required")
    estimator, _ = _bundle_model(model)
    return estimator.predict(np.asarray(features, dtype=float).reshape(1, -1))[0]


def predict(attempt, trained_model):
    """Predict a misconception from one attempt and return model metadata."""
    estimator, bundle = _bundle_model(trained_model)
    names = bundle.get("feature_names")
    if names is None:
        raise ValueError("trained model is missing feature metadata")
    features = extract_features(attempt)
    vector = np.asarray([features.get(name, 0.0) for name in names], dtype=float).reshape(1, -1)
    result = {
        "predicted_misconception": estimator.predict(vector)[0],
        "model_name": bundle.get("model_name", type(estimator).__name__),
    }
    if hasattr(estimator, "predict_proba"):
        result["probabilities"] = dict(zip(estimator.classes_, estimator.predict_proba(vector)[0]))
    return result


split_by_misconception = grouped_split
feature_names = get_feature_names
