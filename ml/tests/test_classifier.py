from ml.classifier import (
    build_dataset,
    extract_features,
    get_feature_names,
    grouped_split,
    predict,
    train_models,
)


def attempt(label="index_1_based", answer="10", family="indexing", confidence=4):
    return {
        "signature": {"real": "20", "index_1_based": "10", "range_1_to_n": "30"},
        "answer": answer,
        "confidence": confidence,
        "family": family,
        "misconception": label,
    }


def training_attempts():
    return [
        attempt("index_1_based", "10", "indexing"),
        attempt("index_1_based", "10", "indexing", 5),
        attempt("range_1_to_n", "30", "range"),
        attempt("range_1_to_n", "30", "range", 2),
    ]


def test_feature_extraction_marks_real_and_misconception_matches():
    features = extract_features(attempt())
    assert features["answer_is_real"] == 0
    assert features["match_index_1_based"] == 1


def test_matched_hypothesis_count():
    candidate = attempt(answer="10")
    candidate["signature"]["range_1_to_n"] = "10"
    assert extract_features(candidate)["matched_hypotheses"] == 2


def test_target_label_is_not_a_feature():
    features = extract_features(attempt())
    assert "index_1_based" not in features
    assert "misconception" not in features


def test_feature_ordering_is_deterministic():
    names = get_feature_names(["range_1_to_n", "index_1_based"], ["range", "indexing"])
    assert names == get_feature_names(["index_1_based", "range_1_to_n"], ["indexing", "range"])
    assert names[:2] == ["match_index_1_based", "match_range_1_to_n"]


def test_grouped_split_has_no_misconception_overlap():
    train, test, train_ids, test_ids = grouped_split(training_attempts(), test_size=0.5)
    assert train_ids.isdisjoint(test_ids)
    assert {item["misconception"] for item in train} == train_ids
    assert {item["misconception"] for item in test} == test_ids


def test_logistic_regression_trains():
    X, y = build_dataset(training_attempts())
    models = train_models(X, y)
    assert "logistic_regression" in models
    assert models["logistic_regression"]["model"].classes_.size == 2


def test_gradient_boosting_trains():
    X, y = build_dataset(training_attempts())
    models = train_models(X, y)
    assert "gradient_boosting" in models
    assert models["gradient_boosting"]["model"].classes_.size == 2


def test_prediction_returns_supported_class_and_model_name():
    attempts = training_attempts()
    X, y = build_dataset(attempts)
    names = list(extract_features(attempts[0], ["index_1_based", "range_1_to_n"], ["indexing", "range"]).keys())
    models = train_models(X, y, names)
    result = predict(attempts[0], models["logistic_regression"])
    assert result["predicted_misconception"] in set(y)
    assert result["model_name"] == "logistic_regression"


def test_training_from_attempts_preserves_feature_metadata_for_prediction():
    attempts = training_attempts()
    models = train_models(attempts)
    result = predict(attempts[0], models["gradient_boosting"])
    assert result["predicted_misconception"] in {"index_1_based", "range_1_to_n"}
