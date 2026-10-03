import json

import pytest

from ml.integration import LIVE_HYPOTHESES, diagnose_answer, ensure_json_safe, select_next_probe


def attempt(answer="20", confidence=3, signature=None):
    return {
        "code": "a = [10, 20, 30]\nprint(a[1])",
        "signature": signature or {"real": "20", "index_1_based": "10", "range_1_to_n": "20"},
        "answer": answer,
        "confidence": confidence,
    }


def test_correct_answer_returns_correct_and_bank_safe_output():
    result = diagnose_answer(attempt("20", 5))
    assert result["top"] == "correct"
    assert result["bank_ids"] == []
    ensure_json_safe(result)


def test_clean_misconception_match_returns_live_bank_ids():
    result = diagnose_answer(attempt("10", 5))
    assert result["top"] == "index_1_based"
    assert result["bank_ids"] == [15, 66]


def test_ambiguous_signature_preserves_all_live_posterior_keys():
    result = diagnose_answer(attempt("20", 3))
    assert set(LIVE_HYPOTHESES) <= result["posterior"].keys()
    assert result["top"] in {"correct", "range_1_to_n", "noop_method", "assign_copies", "add_before_div"}


def test_unknown_answer_is_not_converted_to_known_heldout_id():
    result = diagnose_answer(attempt("not predicted", 5))
    assert result["top"] == "unknown"
    assert "index_from_m1" not in result["posterior"]


def test_confidence_changes_posterior_deterministically():
    low = diagnose_answer(attempt("10", 1))
    high = diagnose_answer(attempt("10", 5))
    assert high["posterior"]["index_1_based"] > low["posterior"]["index_1_based"]


def test_probe_selection_returns_original_json_item():
    candidates = [{"item_id": "p1", "signature": {"h1": "a", "h2": "a"}}, {"item_id": "p2", "signature": {"h1": "a", "h2": "b"}}]
    selected = select_next_probe({"h1": 0.5, "h2": 0.5}, candidates)
    assert selected["item_id"] == "p2"
    ensure_json_safe(selected)


def test_runtime_error_output_is_serializable():
    result = diagnose_answer(attempt("NameError", 3, {"real": "NameError", "index_1_based": "NameError"}))
    json.dumps(result, allow_nan=False)
    assert result["real_output"] == "NameError"


def test_invalid_input_fails_clearly():
    with pytest.raises(ValueError, match="confidence"):
        diagnose_answer({"answer": "20", "confidence": 6, "signature": {"real": "20"}})
    with pytest.raises(ValueError, match="signature or non-empty code"):
        diagnose_answer({"answer": "20", "confidence": 3})


def test_repeated_call_is_deterministic():
    first = diagnose_answer(attempt("10", 4))
    second = diagnose_answer(attempt("10", 4))
    assert first == second
