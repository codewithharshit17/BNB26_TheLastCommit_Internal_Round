import math

import pytest

from ml.probes import info_gain, next_probe, select_probe


POSTERIOR = {"h1": 0.5, "h2": 0.5}


def test_identical_predictions_have_zero_information_gain():
    signature = {"h1": "same", "h2": "same"}
    assert info_gain(POSTERIOR, signature) == pytest.approx(0)


def test_discriminating_probe_has_more_information_gain():
    identical = info_gain(POSTERIOR, {"h1": "same", "h2": "same"})
    different = info_gain(POSTERIOR, {"h1": "one", "h2": "two"})
    assert different > identical


def test_information_gain_is_deterministic_for_same_signature():
    signature = {"h1": "one", "h2": "two", "real": "real"}
    assert info_gain(POSTERIOR, signature) == info_gain(POSTERIOR, signature)


def test_ambiguous_posterior_gets_useful_information_gain():
    assert info_gain({"h1": 0.5, "h2": 0.5}, {"h1": "one", "h2": "two"}) > 0


def test_confident_posterior_gets_less_information_gain():
    balanced = info_gain({"h1": 0.5, "h2": 0.5}, {"h1": "one", "h2": "two"})
    confident = info_gain({"h1": 0.95, "h2": 0.05}, {"h1": "one", "h2": "two"})
    assert confident < balanced


def test_selector_returns_highest_information_candidate():
    candidates = [
        {"item_id": "same", "signature": {"h1": "x", "h2": "x"}},
        {"item_id": "useful", "signature": {"h1": "x", "h2": "y"}},
    ]
    assert select_probe(POSTERIOR, candidates)["item_id"] == "useful"


def test_selector_preserves_input_order_for_equal_gain():
    first = {"item_id": "first", "signature": {"h1": "x", "h2": "y"}}
    second = {"item_id": "second", "signature": {"h1": "x", "h2": "y"}}
    assert next_probe(POSTERIOR, [first, second]) is first


def test_empty_and_malformed_candidates_are_safe():
    assert select_probe(POSTERIOR, []) is None
    assert info_gain(POSTERIOR, None) == 0.0
    selected = select_probe(POSTERIOR, [None, {"item_id": "bad", "signature": None}])
    assert selected is None or selected["item_id"] == "bad"
    assert math.isfinite(info_gain({}, {}))
