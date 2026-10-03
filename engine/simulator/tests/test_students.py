import random

from engine.simulator.students import simulate, simulate_attempt


def test_student_simulation_is_reproducible():
    item = {"signature": {"real": "20", "index_1_based": "10"}, "misconception": "index_1_based"}
    assert simulate_attempt("clean", item, random.Random(7)) == simulate_attempt("clean", item, random.Random(7))


def test_clean_student_uses_misconception_prediction():
    item = {"signature": {"real": "20", "index_1_based": "10"}, "misconception": "index_1_based"}
    answers = [simulate_attempt("clean", item, random.Random(seed))["answer"] for seed in range(20)]
    assert answers.count("10") >= 15


def test_patcher_and_true_learner_differ_on_transfer():
    item = {"signature": {"real": "20", "index_1_based": "10"}, "misconception": "index_1_based", "intervened": True, "is_transfer": True}
    patcher = [simulate_attempt("patcher", item, random.Random(seed))["answer"] for seed in range(20)]
    learner = [simulate_attempt("true_learner", item, random.Random(seed))["answer"] for seed in range(20)]
    assert patcher.count("10") >= 15
    assert learner.count("20") >= 19
"""Tests for engine/simulator/students.py"""
import pytest

try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False

from engine.simulator.students import make_student, simulate


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _rng(seed=0):
    """Return a numpy or stdlib RNG depending on availability."""
    if _HAS_NUMPY:
        return np.random.default_rng(seed)
    import random
    r = random.Random(seed)
    r.random = r.random        # already has .random()
    r.integers = lambda lo, hi: int(r.randint(lo, hi - 1))
    return r


def _item(family: str, real: str, believed: str) -> dict:
    """Build a minimal item dict with a signature."""
    return {
        "item_id": "i_test",
        "kind": "discriminator",
        "family": family,
        "code": "",
        "signature": {
            "real": real,
            family: believed,
        },
        "discriminates": real != believed,
    }


# ---------------------------------------------------------------------------
# make_student / simulate API
# ---------------------------------------------------------------------------

def test_make_student_returns_callable():
    s = make_student("clean", misconception="noop_method")
    assert callable(s)


def test_invalid_student_type_raises():
    with pytest.raises(ValueError):
        make_student("wizard", misconception="noop_method")


def test_simulate_compat_raises_on_bad_type():
    with pytest.raises(ValueError):
        simulate("robot", {}, _rng())


# ---------------------------------------------------------------------------
# clean student
# ---------------------------------------------------------------------------

class TestCleanStudent:
    def test_mostly_believed(self):
        """clean student answers believed output most of the time."""
        item = _item("noop_method", real="hello", believed="HELLO")
        s = make_student("clean", misconception="noop_method")
        rng = _rng(42)
        answers = [s(item, rng) for _ in range(200)]
        believed_count = answers.count("HELLO")
        # Should be around 85% ± noise
        assert believed_count >= 130, f"Only {believed_count}/200 believed answers"

    def test_non_discriminating_item_always_real(self):
        """On a non-discriminating item, clean student always returns real."""
        item = _item("noop_method", real="hello", believed="hello")
        s = make_student("clean", misconception="noop_method")
        rng = _rng(0)
        answers = {s(item, rng) for _ in range(50)}
        assert answers == {"hello"}

    def test_slips_occasionally(self):
        """clean student sometimes returns real even on discriminating items."""
        item = _item("noop_method", real="hello", believed="HELLO")
        s = make_student("clean", misconception="noop_method")
        rng = _rng(7)
        answers = [s(item, rng) for _ in range(200)]
        real_count = answers.count("hello")
        assert real_count >= 5, "Expected some slips"


# ---------------------------------------------------------------------------
# noisy student
# ---------------------------------------------------------------------------

class TestNoisyStudent:
    def test_returns_valid_outputs(self):
        """noisy student only returns values present in the signature."""
        item = _item("range_1_to_n", real="0\n1\n2", believed="1\n2\n3")
        s = make_student("noisy", misconception="range_1_to_n")
        rng = _rng(1)
        for _ in range(100):
            ans = s(item, rng)
            assert ans in ("0\n1\n2", "1\n2\n3"), f"Unexpected answer: {ans!r}"

    def test_noise_reduces_believed_proportion(self):
        """noisy student answers believed less often than clean student."""
        item = _item("noop_method", real="hello", believed="HELLO")
        rng_clean = _rng(42)
        rng_noisy = _rng(42)
        clean = make_student("clean", misconception="noop_method")
        noisy = make_student("noisy", misconception="noop_method")
        clean_believed = sum(clean(item, rng_clean) == "HELLO" for _ in range(300))
        noisy_believed = sum(noisy(item, rng_noisy) == "HELLO" for _ in range(300))
        assert noisy_believed <= clean_believed


# ---------------------------------------------------------------------------
# mixed student
# ---------------------------------------------------------------------------

class TestMixedStudent:
    def test_answers_one_of_two_outputs(self):
        """mixed student only returns real or one of the two believed outputs."""
        item = {
            "item_id": "i_m",
            "family": "noop_method",
            "code": "",
            "signature": {
                "real": "hello",
                "noop_method": "HELLO",
                "index_1_based": "10",
            },
            "discriminates": True,
        }
        s = make_student("mixed", misconception="noop_method", misconception2="index_1_based")
        rng = _rng(3)
        valid = {"hello", "HELLO", "10"}
        for _ in range(100):
            assert s(item, rng) in valid


# ---------------------------------------------------------------------------
# unknown (held-out) student
# ---------------------------------------------------------------------------

class TestUnknownStudent:
    def test_uses_heldout_misconception(self):
        """unknown student answers believed output for the held-out misconception."""
        item = {
            "item_id": "i_u",
            "family": "index_from_m1",
            "code": "",
            "signature": {
                "real": "20",
                "index_from_m1": "30",
                "noop_method": "20",
            },
            "discriminates": True,
        }
        s = make_student("unknown", misconception="index_from_m1")
        rng = _rng(5)
        answers = [s(item, rng) for _ in range(200)]
        believed_count = answers.count("30")
        assert believed_count >= 130


# ---------------------------------------------------------------------------
# patcher student
# ---------------------------------------------------------------------------

class TestPatcherStudent:
    def _make_item(self, item_id: str) -> dict:
        return _item("noop_method", real="hello", believed="HELLO") | {"item_id": item_id}

    def test_before_intervention_behaves_like_clean(self):
        """Before intervention patcher is indistinguishable from clean."""
        item = self._make_item("i_0001")
        s = make_student("patcher", misconception="noop_method")
        rng = _rng(42)
        answers = [s(item, rng) for _ in range(200)]
        assert answers.count("HELLO") >= 130

    def test_after_intervention_correct_on_patched_item(self):
        """After intervention, patcher answers correctly on patched items."""
        item = self._make_item("i_0001")
        s = make_student("patcher", misconception="noop_method")
        s.intervened = True
        s.patched_ids = {"i_0001"}
        rng = _rng(0)
        answers = [s(item, rng) for _ in range(50)]
        real_count = answers.count("hello")
        assert real_count >= 45

    def test_after_intervention_still_wrong_on_transfer(self):
        """Patcher still applies misconception on unpatch-ed transfer items."""
        item = self._make_item("i_9999")   # different item_id
        s = make_student("patcher", misconception="noop_method")
        s.intervened = True
        s.patched_ids = {"i_0001"}         # only i_0001 is patched
        rng = _rng(42)
        answers = [s(item, rng) for _ in range(200)]
        assert answers.count("HELLO") >= 130


# ---------------------------------------------------------------------------
# true_learner student
# ---------------------------------------------------------------------------

class TestTrueLearner:
    def _item(self) -> dict:
        return _item("noop_method", real="hello", believed="HELLO")

    def test_before_intervention_behaves_like_clean(self):
        s = make_student("true_learner", misconception="noop_method")
        rng = _rng(42)
        item = self._item()
        answers = [s(item, rng) for _ in range(200)]
        assert answers.count("HELLO") >= 130

    def test_after_intervention_mostly_correct(self):
        """After intervention true_learner answers correctly ~95% of the time."""
        s = make_student("true_learner", misconception="noop_method")
        s.intervened = True
        rng = _rng(0)
        item = self._item()
        answers = [s(item, rng) for _ in range(200)]
        real_count = answers.count("hello")
        assert real_count >= 170, f"Only {real_count}/200 correct after intervention"

    def test_after_intervention_correct_on_transfer(self):
        """True learner is also correct on transfer items (unlike patcher)."""
        s = make_student("true_learner", misconception="noop_method")
        s.intervened = True
        rng = _rng(1)
        # Transfer item — different surface form
        item = _item("noop_method", real="world", believed="WORLD") | {"item_id": "i_transfer"}
        answers = [s(item, rng) for _ in range(200)]
        assert answers.count("world") >= 170


# ---------------------------------------------------------------------------
# simulate() convenience wrapper
# ---------------------------------------------------------------------------

def test_simulate_clean():
    item = _item("noop_method", real="hello", believed="HELLO")
    rng = _rng(42)
    answers = [simulate("clean", item, rng, misconception="noop_method") for _ in range(200)]
    assert answers.count("HELLO") >= 130


def test_simulate_patcher_with_state():
    item = _item("noop_method", real="hello", believed="HELLO") | {"item_id": "i_0001"}
    rng = _rng(0)
    answers = [
        simulate(
            "patcher", item, rng,
            misconception="noop_method",
            intervened=True,
            patched_ids={"i_0001"},
        )
        for _ in range(50)
    ]
    assert answers.count("hello") >= 45
