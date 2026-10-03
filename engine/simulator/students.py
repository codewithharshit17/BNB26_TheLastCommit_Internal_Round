"""Simulated student answer generators for Re:Learn evaluation.

Each student type takes an item dict (with a precomputed ``signature`` field)
and returns an answer string.  Pass a ``numpy.random.Generator`` (from
``numpy.random.default_rng(seed)``) so that experiments are reproducible.

Student types
-------------
clean(M)
    Answers the believed output for misconception M with probability 0.85;
    otherwise slips and answers the real output.

noisy(M)
    Like clean but also occasionally returns a random wrong answer.

mixed(M1, M2)
    Holds two misconceptions simultaneously.  On items where both produce the
    same output, that output is returned with high probability.  Where they
    differ, one is chosen at random.

unknown(M_heldout)
    A student whose misconception is NOT in the live hypothesis set (used for
    the held-out / novel-misconception test).  Answers the believed output for
    the held-out misconception with probability 0.85.

patcher(M)
    After an intervention, the patcher corrects *only* the exact item they
    were shown.  On every other item they still apply the misconception.
    Tracks seen item_ids in a mutable ``patched_ids`` set that callers
    populate after the intervention.

true_learner(M)
    After an intervention, the true learner has dropped the misconception
    entirely and answers correctly on all items.  Tracks whether the
    intervention has been delivered via a mutable ``intervened`` flag.

Usage
-----
    import numpy as np
    from engine.simulator.students import make_student

    rng = np.random.default_rng(42)
    student = make_student("clean", misconception="noop_method")
    item = items_bank[0]   # dict with "signature" key
    answer = student(item, rng)
"""

from __future__ import annotations

import random
from typing import Any, Callable

# ---------------------------------------------------------------------------
# Type alias
# ---------------------------------------------------------------------------

Item = dict[str, Any]
RNG = Any  # numpy.random.Generator or random.Random — duck-typed

# ---------------------------------------------------------------------------
# Low-level answer samplers
# ---------------------------------------------------------------------------

_SLIP_RATE = 0.15          # P(answer real | hold misconception)
_NOISE_RATE = 0.10         # extra P(random wrong answer) for noisy students
_MISCONCEPTION_HIT = 0.85  # P(answer believed | hold misconception, item discriminates)


def _pick_random_wrong(real: str, believed: str, sig: dict[str, str], rng: RNG) -> str:
    """Return a random output from the signature that is neither real nor believed."""
    candidates = [v for v in sig.values() if v not in (real, believed)]
    if not candidates:
        return believed  # fallback
    idx = int(rng.integers(0, len(candidates)))
    return candidates[idx]


def _answer_for_misconception(
    mid: str,
    item: Item,
    rng: RNG,
    slip_rate: float = _SLIP_RATE,
    noise_rate: float = 0.0,
) -> str:
    """Core sampling logic shared by multiple student types."""
    sig = item.get("signature", {})
    real = sig.get("real", "")
    believed = sig.get(mid, real)  # if mid not in sig, believed == real
    discriminates = (real != believed)

    if not discriminates:
        # Item does not separate this misconception from correct understanding
        return real

    roll = float(rng.random())

    if noise_rate > 0 and roll < noise_rate:
        return _pick_random_wrong(real, believed, sig, rng)

    if roll < noise_rate + slip_rate:
        return real   # slip — answers correctly despite holding misconception

    return believed   # applies misconception


# ---------------------------------------------------------------------------
# Student factory
# ---------------------------------------------------------------------------

class Student:
    """Callable student object returned by ``make_student``."""

    def __init__(
        self,
        kind: str,
        misconception: str | None = None,
        misconception2: str | None = None,
        patched_ids: set[str] | None = None,
        intervened: bool = False,
    ) -> None:
        self.kind = kind
        self.misconception = misconception
        self.misconception2 = misconception2
        # mutable state — callers mutate these after the intervention
        self.patched_ids: set[str] = patched_ids if patched_ids is not None else set()
        self.intervened = intervened

    # ------------------------------------------------------------------
    def __call__(self, item: Item, rng: RNG) -> str:
        kind = self.kind
        if kind == "clean":
            return self._clean(item, rng)
        if kind == "noisy":
            return self._noisy(item, rng)
        if kind == "mixed":
            return self._mixed(item, rng)
        if kind == "unknown":
            return self._unknown(item, rng)
        if kind == "patcher":
            return self._patcher(item, rng)
        if kind == "true_learner":
            return self._true_learner(item, rng)
        raise ValueError(f"Unknown student type: {kind!r}")

    # ------------------------------------------------------------------
    def _clean(self, item: Item, rng: RNG) -> str:
        """Applies misconception with p=0.85, otherwise slips to real."""
        return _answer_for_misconception(
            self.misconception, item, rng, slip_rate=_SLIP_RATE
        )

    def _noisy(self, item: Item, rng: RNG) -> str:
        """Like clean but adds random-wrong-answer noise."""
        return _answer_for_misconception(
            self.misconception, item, rng,
            slip_rate=_SLIP_RATE, noise_rate=_NOISE_RATE,
        )

    def _mixed(self, item: Item, rng: RNG) -> str:
        """Holds two misconceptions; picks the one whose output differs from real."""
        sig = item.get("signature", {})
        real = sig.get("real", "")
        b1 = sig.get(self.misconception, real)
        b2 = sig.get(self.misconception2, real) if self.misconception2 else real

        # Both misconceptions agree — use that shared output (with slip)
        if b1 == b2:
            roll = float(rng.random())
            return real if roll < _SLIP_RATE else b1

        # They disagree — pick one misconception at random, then sample
        chosen = self.misconception if float(rng.random()) < 0.5 else self.misconception2
        return _answer_for_misconception(chosen, item, rng, slip_rate=_SLIP_RATE)

    def _unknown(self, item: Item, rng: RNG) -> str:
        """Held-out misconception — uses index_from_m1 (the held-out rewrite)."""
        return _answer_for_misconception(
            self.misconception, item, rng, slip_rate=_SLIP_RATE
        )

    def _patcher(self, item: Item, rng: RNG) -> str:
        """After intervention, only the exact patched items are answered correctly."""
        if self.intervened and item.get("item_id") in self.patched_ids:
            # Answers real output (with small residual slip)
            sig = item.get("signature", {})
            real = sig.get("real", "")
            roll = float(rng.random())
            return real if roll > 0.05 else sig.get(self.misconception, real)
        # Otherwise still applies misconception
        return _answer_for_misconception(
            self.misconception, item, rng, slip_rate=_SLIP_RATE
        )

    def _true_learner(self, item: Item, rng: RNG) -> str:
        """After intervention, drops misconception entirely — answers real."""
        sig = item.get("signature", {})
        real = sig.get("real", "")
        if self.intervened:
            # True learner answers correctly with p=0.95
            roll = float(rng.random())
            return real if roll < 0.95 else sig.get(self.misconception, real)
        # Before intervention — same as clean
        return _answer_for_misconception(
            self.misconception, item, rng, slip_rate=_SLIP_RATE
        )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def make_student(
    kind: str,
    misconception: str | None = None,
    misconception2: str | None = None,
) -> Student:
    """Create a Student callable.

    Args:
        kind:          One of clean, noisy, mixed, unknown, patcher, true_learner.
        misconception: Primary misconception id (e.g. ``"noop_method"``).
        misconception2: Secondary misconception id (for ``mixed`` only).

    Returns:
        A ``Student`` object.  Call it with ``(item, rng)`` to get an answer.
    """
    if kind not in {"clean", "noisy", "mixed", "unknown", "patcher", "true_learner"}:
        raise ValueError(f"Unknown student type: {kind!r}")
    return Student(kind=kind, misconception=misconception, misconception2=misconception2)


def simulate(student_type: str, item: Item, rng: RNG, **kwargs) -> str:
    """Convenience wrapper kept for backward-compat with the stub signature.

    For full control (mixed students, patcher state) use ``make_student``.

    Args:
        student_type: One of clean, noisy, mixed, unknown, patcher, true_learner.
        item:         Item dict with a ``signature`` key.
        rng:          A numpy ``default_rng`` or ``random.Random`` instance.
        **kwargs:     ``misconception``, ``misconception2`` forwarded to make_student.
    """
    if student_type not in {"clean", "noisy", "mixed", "unknown", "patcher", "true_learner"}:
        raise ValueError("unknown student type")

    misconception = kwargs.get("misconception", "noop_method")
    misconception2 = kwargs.get("misconception2", None)
    student = make_student(student_type, misconception=misconception, misconception2=misconception2)

    # Forward patcher/true_learner state if passed
    if "patched_ids" in kwargs:
        student.patched_ids = kwargs["patched_ids"]
    if "intervened" in kwargs:
        student.intervened = kwargs["intervened"]

    return student(item, rng)
