"""Small, reproducible simulated-student implementations."""

from __future__ import annotations

import random
from typing import Any

from engine.signature import signature as make_signature

Item = dict[str, Any]
RNG = Any
STUDENT_TYPES = {"clean", "noisy", "mixed", "unknown", "patcher", "true_learner"}
_SLIP_RATE = 0.15
_NOISE_RATE = 0.10


def _rng_float(rng: RNG) -> float:
    return float(rng.random())


def _rng_int(rng: RNG, low: int, high: int) -> int:
    if hasattr(rng, "integers"):
        return int(rng.integers(low, high + 1))
    return int(rng.randint(low, high))


def _rng_index(rng: RNG, size: int) -> int:
    if hasattr(rng, "integers"):
        return int(rng.integers(0, size))
    return int(rng.randrange(size))


def _signature(item: Item) -> dict[str, str]:
    value = item.get("signature") if isinstance(item, dict) else None
    if isinstance(value, dict):
        return {str(key): str(output) for key, output in value.items()}
    code = item.get("code", "") if isinstance(item, dict) else ""
    return {str(key): str(output) for key, output in make_signature(code).items()}


def _item_with_signature(item: Item) -> Item:
    result = dict(item) if isinstance(item, dict) else {}
    result["signature"] = _signature(result)
    return result


def _targets(item: Item) -> list[str]:
    values = item.get("misconceptions", item.get("targets"))
    if values is None:
        values = [item.get("misconception", item.get("target"))]
    if isinstance(values, str):
        values = [values]
    return [str(value) for value in values if value is not None]


def _pick_random_wrong(real: str, believed: str, sig: dict[str, str], rng: RNG) -> str:
    candidates = sorted({value for value in sig.values() if value not in (real, believed)})
    return candidates[_rng_index(rng, len(candidates))] if candidates else believed


def _answer_for_misconception(mid: str | None, item: Item, rng: RNG, slip_rate: float = _SLIP_RATE, noise_rate: float = 0.0) -> str:
    sig = item.get("signature", {})
    real = str(sig.get("real", ""))
    believed = str(sig.get(mid, real)) if mid else real
    if real == believed:
        return real
    roll = _rng_float(rng)
    if noise_rate > 0 and roll < noise_rate:
        return _pick_random_wrong(real, believed, sig, rng)
    return real if roll < noise_rate + slip_rate else believed


class Student:
    """Callable stateful student; calling it returns an answer string."""

    def __init__(self, kind: str, misconception: str | None = None, misconception2: str | None = None, patched_ids: set[str] | None = None, intervened: bool = False) -> None:
        self.kind = kind
        self.misconception = misconception
        self.misconception2 = misconception2
        self.patched_ids = patched_ids if patched_ids is not None else set()
        self.intervened = intervened

    def __call__(self, item: Item, rng: RNG) -> str:
        item = _item_with_signature(item)
        if self.kind == "clean":
            return _answer_for_misconception(self.misconception, item, rng)
        if self.kind == "noisy":
            return _answer_for_misconception(self.misconception, item, rng, noise_rate=_NOISE_RATE)
        if self.kind == "mixed":
            sig = item["signature"]
            real = str(sig.get("real", ""))
            first = str(sig.get(self.misconception, real)) if self.misconception else real
            second = str(sig.get(self.misconception2, real)) if self.misconception2 else real
            if first == second:
                return real if _rng_float(rng) < _SLIP_RATE else first
            chosen = self.misconception if _rng_float(rng) < 0.5 else self.misconception2
            return _answer_for_misconception(chosen, item, rng)
        if self.kind == "unknown":
            return _answer_for_misconception(self.misconception, item, rng)
        if self.kind == "patcher":
            if self.intervened and item.get("item_id") in self.patched_ids:
                real = str(item["signature"].get("real", ""))
                return real if _rng_float(rng) > 0.05 else str(item["signature"].get(self.misconception, real))
            return _answer_for_misconception(self.misconception, item, rng)
        if self.kind == "true_learner":
            if self.intervened:
                real = str(item["signature"].get("real", ""))
                return real if _rng_float(rng) < 0.95 else str(item["signature"].get(self.misconception, real))
            return _answer_for_misconception(self.misconception, item, rng)
        raise ValueError(f"Unknown student type: {self.kind!r}")


def make_student(kind: str, misconception: str | None = None, misconception2: str | None = None) -> Student:
    """Create a callable stateful student for one of the six supported types."""
    if kind not in STUDENT_TYPES:
        raise ValueError(f"Unknown student type: {kind!r}")
    return Student(kind, misconception, misconception2)


def simulate(student_type: str, item: Item, rng: RNG, **kwargs: Any) -> str:
    """Return one answer string, preserving the incoming simulator API."""
    student = make_student(student_type, misconception=kwargs.get("misconception", item.get("misconception", "noop_method")), misconception2=kwargs.get("misconception2", item.get("misconception2")))
    if "patched_ids" in kwargs:
        student.patched_ids = kwargs["patched_ids"]
    if "intervened" in kwargs:
        student.intervened = bool(kwargs["intervened"])
    return student(item, rng)


def simulate_attempt(student_type: str, item: Item, rng: RNG, **kwargs: Any) -> dict[str, Any]:
    """Return the complete attempt record consumed by ML evaluation."""
    normalized = _item_with_signature(item)
    targets = _targets(normalized)
    target = targets[0] if targets else None
    is_transfer = bool(normalized.get("is_transfer", False))
    intervened = bool(normalized.get("intervened", False))
    sig = normalized["signature"]
    real = str(sig.get("real", ""))
    predicted = sig.get(target) if target else None
    predicted = str(predicted) if predicted is not None else None
    if student_type not in STUDENT_TYPES:
        raise ValueError("unknown student type")
    # Keep the pre-merge evaluator's attempt-generation behavior.  The
    # stateful Student API above remains the incoming answer-string API.
    if student_type == "true_learner" and intervened:
        answer = real
    elif student_type == "patcher" and intervened:
        answer = real if not is_transfer else (predicted if predicted and predicted != real else real)
    elif student_type == "noisy" and _rng_float(rng) < 0.30:
        answer = _pick_random_wrong(real, real, sig, rng)
    elif student_type == "mixed":
        predictions = [str(sig.get(misconception)) for misconception in targets if sig.get(misconception) is not None and str(sig.get(misconception)) != real]
        answer = predictions[_rng_index(rng, len(predictions))] if predictions and _rng_float(rng) < 0.85 else real
    else:
        answer = predicted if predicted and predicted != real and _rng_float(rng) < 0.85 else real
    return {"item_id": normalized.get("item_id"), "code": normalized.get("code", ""), "signature": sig, "answer": answer, "real_output": real, "confidence": _rng_int(rng, 1, 5), "family": normalized.get("family"), "misconception": target, "student_type": student_type, "is_transfer": is_transfer, "intervened": intervened}
