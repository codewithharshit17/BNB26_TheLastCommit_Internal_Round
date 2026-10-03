import pytest

from ml.posterior import update


def test_update_normalizes():
    result = update({"correct": 0.5, "unknown": 0.5}, {"real": "1", "unknown": "2"}, "1", 3)
    assert abs(sum(result.values()) - 1) < 1e-9


def test_single_clean_match_becomes_dominant():
    result = update(
        {"correct": 0.2, "index_1_based": 0.4, "range_1_to_n": 0.2, "unknown": 0.2},
        {"real": "20", "index_1_based": "10", "range_1_to_n": "30"},
        "10",
        3,
    )
    assert result["index_1_based"] == max(result.values())


def test_two_interpreters_tied_share_probability():
    result = update(
        {"correct": 0.1, "first": 0.45, "second": 0.45, "unknown": 0.0},
        {"real": "20", "first": "10", "second": "10"},
        "10",
        3,
    )
    assert result["first"] == pytest.approx(result["second"])
    assert result["first"] > result["correct"]


def test_no_interpreter_prediction_increases_unknown():
    result = update(
        {"correct": 0.25, "index_1_based": 0.25, "unknown": 0.5},
        {"real": "20", "index_1_based": "10"},
        "999",
        3,
    )
    assert result["unknown"] > 0.5


def test_correct_answer_increases_correct():
    result = update(
        {"correct": 0.25, "index_1_based": 0.5, "unknown": 0.25},
        {"real": "20", "index_1_based": "10"},
        "20",
        3,
    )
    assert result["correct"] > 0.25


def test_higher_confidence_strengthens_wrong_misconception_evidence():
    prior = {"correct": 0.5, "index_1_based": 0.4, "unknown": 0.1}
    sig = {"real": "20", "index_1_based": "10"}
    low = update(prior, sig, "10", 1)
    high = update(prior, sig, "10", 5)
    assert high["index_1_based"] > low["index_1_based"]


def test_invalid_priors_are_safe_and_normalized():
    result = update(
        {"correct": float("nan"), "index_1_based": -1, "unknown": "not-a-number"},
        {"real": "20", "index_1_based": "10"},
        "10",
        3,
    )
    assert all(value == value for value in result.values())
    assert sum(result.values()) == pytest.approx(1)
