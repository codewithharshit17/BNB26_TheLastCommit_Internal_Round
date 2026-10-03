import hashlib
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class LLMConfigurationError(RuntimeError):
    """Raised when the zero-shot provider is not configured."""


def _hypothesis_list(hypotheses):
    if isinstance(hypotheses, dict):
        hypotheses = [{"id": key, "description": value} for key, value in hypotheses.items()]
    result = []
    for hypothesis in hypotheses or []:
        if isinstance(hypothesis, dict):
            identifier = hypothesis.get("id")
            description = hypothesis.get("description", "")
        elif isinstance(hypothesis, (tuple, list)) and len(hypothesis) >= 2:
            identifier, description = hypothesis[0], hypothesis[1]
        else:
            continue
        if identifier is not None:
            result.append((str(identifier), str(description)))
    return sorted(result)


def _attempt_values(attempt):
    if isinstance(attempt, str):
        return attempt, "", ""
    if not isinstance(attempt, dict):
        raise ValueError("attempt must be a mapping or prompt string")
    item = attempt.get("item") if isinstance(attempt.get("item"), dict) else {}
    signature = attempt.get("signature", attempt.get("sig", {}))
    if not isinstance(signature, dict):
        signature = {}
    code = attempt.get("code", item.get("code", ""))
    real_output = attempt.get("real_output", signature.get("real", ""))
    answer = attempt.get("answer", attempt.get("student_answer", ""))
    return str(code), str(real_output), str(answer)


def build_prompt(attempt, hypotheses):
    """Build the deterministic, answer-only baseline prompt."""
    code, real_output, answer = _attempt_values(attempt)
    entries = _hypothesis_list(hypotheses)
    hypothesis_text = "\n".join(
        f"- {identifier}: {description}" for identifier, description in entries
    ) or "- (no misconceptions available)"
    return (
        "Classify this introductory Python attempt for a zero-shot baseline.\n"
        "Return exactly ONE token: a listed misconception ID, unknown, or none.\n"
        "Do not invent IDs. Do not provide an explanation.\n\n"
        f"PYTHON CODE:\n{code}\n\n"
        f"REAL PYTHON OUTPUT:\n{real_output}\n\n"
        f"STUDENT ANSWER:\n{answer}\n\n"
        "AVAILABLE MISCONCEPTIONS:\n"
        f"{hypothesis_text}"
    )


def parse_response(raw_response, hypotheses):
    """Normalize a provider response to a known ID or ``unknown``."""
    known = {identifier.lower(): identifier for identifier, _ in _hypothesis_list(hypotheses)}
    text = str(raw_response or "").strip().strip("`\"' .,;:")
    lowered = text.lower()
    if lowered in {"unknown", "none"}:
        return "unknown"
    return known.get(lowered, "unknown")


def _default_provider(prompt, model, api_key, api_base):
    if not api_key:
        raise LLMConfigurationError(
            "LLM_API_KEY is not configured; set it or inject a provider for tests"
        )
    payload = json.dumps({
        "model": model,
        "temperature": 0,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")
    request = Request(
        api_base,
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            body = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"LLM provider request failed: {exc}") from exc
    try:
        return body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("LLM provider returned an unexpected response shape") from exc


def _cache_path(cache_dir, cache_key):
    directory = Path(cache_dir or os.getenv("LLM_CACHE_DIR", ".cache/relearn_llm"))
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f"{cache_key}.json"


def predict(attempt, hypotheses=None, api_key=None, model=None, cache_dir=None, provider=None):
    """Run the cached zero-shot baseline for one attempt.

    ``provider`` is an injectable callable for tests. It receives
    ``(prompt, model, api_key, api_base)`` and returns raw text.
    """
    hypothesis_list = _hypothesis_list(hypotheses)
    prompt = build_prompt(attempt, hypothesis_list)
    model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")
    api_base = os.getenv("LLM_API_BASE", "https://api.openai.com/v1/chat/completions")
    cache_input = {"model": model, "prompt": prompt, "hypotheses": hypothesis_list}
    cache_key = hashlib.sha256(
        json.dumps(cache_input, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    path = _cache_path(cache_dir, cache_key)
    if path.exists():
        cached = json.loads(path.read_text(encoding="utf-8"))
        cached["cached"] = True
        return cached

    if provider is None:
        raw_response = _default_provider(prompt, model, api_key or os.getenv("LLM_API_KEY"), api_base)
    else:
        raw_response = provider(prompt, model, api_key, api_base)
    result = {
        "prediction": parse_response(raw_response, hypothesis_list),
        "raw_response": str(raw_response),
        "model": model,
        "cached": False,
    }
    path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result
