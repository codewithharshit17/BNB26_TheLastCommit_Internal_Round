import pytest

from ml.baselines.llm_zero_shot import (
    LLMConfigurationError,
    build_prompt,
    parse_response,
    predict,
)


HYPOTHESES = [
    {"id": "index_1_based", "description": "The first list element is at index 1."},
    {"id": "range_1_to_n", "description": "range(n) includes n."},
]


def sample_attempt(answer="10"):
    return {
        "code": "a = [10, 20]\nprint(a[1])",
        "real_output": "20",
        "answer": answer,
        "confidence": 4,
    }


def test_prompt_contains_attempt_and_hypotheses():
    prompt = build_prompt(sample_attempt(), HYPOTHESES)
    assert "a = [10, 20]" in prompt
    assert "20" in prompt
    assert "10" in prompt
    assert "index_1_based" in prompt
    assert "The first list element is at index 1." in prompt
    assert "exactly ONE token" in prompt


def test_valid_id_is_parsed():
    assert parse_response("index_1_based", HYPOTHESES) == "index_1_based"


def test_unknown_and_none_are_normalized():
    assert parse_response("unknown", HYPOTHESES) == "unknown"
    assert parse_response("none", HYPOTHESES) == "unknown"


def test_invalid_id_becomes_unknown():
    assert parse_response("made_up_misconception", HYPOTHESES) == "unknown"
    assert parse_response("The answer is index_1_based", HYPOTHESES) == "unknown"


def test_cached_request_avoids_second_provider_call(tmp_path):
    calls = []

    def provider(prompt, model, api_key, api_base):
        calls.append(prompt)
        return "index_1_based"

    first = predict(sample_attempt(), HYPOTHESES, model="test-model", cache_dir=tmp_path, provider=provider)
    second = predict(sample_attempt(), HYPOTHESES, model="test-model", cache_dir=tmp_path, provider=provider)
    assert first["cached"] is False
    assert second["cached"] is True
    assert second["prediction"] == "index_1_based"
    assert len(calls) == 1


def test_different_prompts_use_different_cache_keys(tmp_path):
    calls = []

    def provider(prompt, model, api_key, api_base):
        calls.append(prompt)
        return "unknown"

    predict(sample_attempt("10"), HYPOTHESES, cache_dir=tmp_path, provider=provider)
    predict(sample_attempt("30"), HYPOTHESES, cache_dir=tmp_path, provider=provider)
    assert len(calls) == 2


def test_missing_api_configuration_fails_clearly(tmp_path, monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    with pytest.raises(LLMConfigurationError, match="LLM_API_KEY"):
        predict(sample_attempt(), HYPOTHESES, cache_dir=tmp_path)


def test_result_has_normalized_fields(tmp_path):
    result = predict(
        sample_attempt(),
        HYPOTHESES,
        cache_dir=tmp_path,
        provider=lambda prompt, model, api_key, api_base: "none",
    )
    assert set(result) == {"prediction", "raw_response", "model", "cached"}
    assert result["prediction"] == "unknown"
    assert result["cached"] is False
