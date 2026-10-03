"""Small backend-facing adapters for the existing Re:Learn ML components.

The backend currently has its own diagnosis service. These functions provide a
stable contract for the next wiring step without changing the ML algorithms.
Held-out rewrite hypotheses are deliberately excluded from normal diagnosis.
"""

import json
from collections.abc import Mapping
from pathlib import Path

from engine.rewrites import LIVE_REGISTRY
from engine.bank import get_bank_entry
from engine.signature import believed_source, signature as make_signature
from ml.posterior import update
from ml.probes import select_probe


LIVE_HYPOTHESES = [entry["id"] for entry in LIVE_REGISTRY]
_BANK_MAP = json.loads((Path(__file__).resolve().parents[1] / "engine" / "bank_map.json").read_text(encoding="utf-8"))
_VALID_BANK_MAP = {
    hypothesis: [bank_id for bank_id in bank_ids if get_bank_entry(bank_id) is not None]
    for hypothesis, bank_ids in _BANK_MAP.items()
}


def _validate_attempt(attempt):
    if not isinstance(attempt, Mapping):
        raise ValueError("attempt must be a mapping")
    answer = attempt.get("answer")
    if not isinstance(answer, str):
        raise ValueError("attempt.answer must be a string")
    confidence = attempt.get("confidence")
    if not isinstance(confidence, int) or isinstance(confidence, bool) or not 1 <= confidence <= 5:
        raise ValueError("attempt.confidence must be an integer from 1 to 5")
    supplied = attempt.get("signature", attempt.get("sig"))
    if supplied is not None and not isinstance(supplied, Mapping):
        raise ValueError("attempt.signature must be a mapping")
    code = attempt.get("code")
    if supplied is None:
        if not isinstance(code, str) or not code:
            raise ValueError("attempt requires signature or non-empty code")
        supplied = make_signature(code)
    return answer, confidence, dict(supplied), code


def _live_signature(supplied):
    return {
        key: value
        for key, value in supplied.items()
        if key == "real" or key in LIVE_HYPOTHESES
    }


def _prior(prior):
    if prior is not None:
        if not isinstance(prior, Mapping):
            raise ValueError("prior must be a mapping")
        allowed = {"correct", *LIVE_HYPOTHESES, "unknown"}
        filtered = {key: value for key, value in prior.items() if key in allowed}
        if filtered:
            return filtered
    hypotheses = ["correct", *LIVE_HYPOTHESES, "unknown"]
    share = 1 / len(hypotheses)
    return {hypothesis: share for hypothesis in hypotheses}


def select_next_probe(posterior, candidate_items):
    """Select and return a JSON-safe probe item using existing probe logic."""
    selected = select_probe(posterior, candidate_items)
    return dict(selected) if isinstance(selected, Mapping) else selected


def diagnose_answer(attempt, prior=None, next_items=None):
    """Return a backend-safe diagnosis response for one answer attempt.

    Input schema: ``answer``, ``confidence`` and either ``signature`` or
    ``code``; ``code`` is also used to produce ``believed_source``.
    """
    answer, confidence, supplied_signature, code = _validate_attempt(attempt)
    live_signature = _live_signature(supplied_signature)
    posterior = update(_prior(prior), live_signature, answer, confidence)
    top = max(posterior, key=posterior.get)
    real_output = str(live_signature.get("real", ""))
    believed_output = str(live_signature.get(top, real_output))
    if top in LIVE_HYPOTHESES:
        if not isinstance(code, str) or not code:
            raise ValueError("attempt.code is required to produce believed_source")
        believed = believed_source(code, top)
    else:
        believed = code if isinstance(code, str) else real_output

    action = "intervene" if top not in {"correct", "unknown"} and posterior[top] >= 0.8 else "done"
    next_item = None
    if action == "done" and next_items:
        next_item = select_next_probe(posterior, next_items)
        if next_item is not None:
            action = "probe"
    next_misconception = top if action == "intervene" else None
    next_value = {"action": action, "item": next_item, "misconception": next_misconception}
    return {
        "posterior": {str(key): float(value) for key, value in posterior.items()},
        "top": str(top),
        "bank_ids": [int(value) for value in _VALID_BANK_MAP.get(top, [])],
        "real_output": real_output,
        "believed_output": believed_output,
        "believed_source": believed,
        "next_action": action,
        "next_item": next_item,
        "next_misconception": next_misconception,
        "next": next_value,
    }


def ensure_json_safe(value):
    """Validate that an adapter result can cross a JSON API boundary."""
    json.dumps(value, allow_nan=False)
    return value
