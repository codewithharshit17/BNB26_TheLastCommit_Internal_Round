"""Tests for engine/interventions/builder.py"""
import pytest
from engine.interventions.builder import build, build_all, load


LIVE_FAMILIES = [
    "noop_method",
    "range_1_to_n",
    "index_1_based",
    "assign_copies",
    "add_before_div",
]

REQUIRED_KEYS = {
    "title",
    "bank_description",
    "contrast_code",
    "real_output",
    "believed_output",
    "steps",
    "takeaway",
}


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("mid", LIVE_FAMILIES)
def test_build_returns_required_keys(mid):
    iv = build(mid)
    missing = REQUIRED_KEYS - iv.keys()
    assert not missing, f"[{mid}] missing keys: {missing}"


@pytest.mark.parametrize("mid", LIVE_FAMILIES)
def test_build_steps_is_list_of_three(mid):
    iv = build(mid)
    assert isinstance(iv["steps"], list)
    assert len(iv["steps"]) == 3, f"[{mid}] expected 3 steps, got {len(iv['steps'])}"


@pytest.mark.parametrize("mid", LIVE_FAMILIES)
def test_build_outputs_are_strings(mid):
    iv = build(mid)
    assert isinstance(iv["real_output"], str)
    assert isinstance(iv["believed_output"], str)


@pytest.mark.parametrize("mid", LIVE_FAMILIES)
def test_build_outputs_are_nonempty(mid):
    iv = build(mid)
    assert iv["real_output"].strip(), f"[{mid}] real_output is empty"
    assert iv["believed_output"].strip(), f"[{mid}] believed_output is empty"


# ---------------------------------------------------------------------------
# Outputs are computed, not hand-typed
# ---------------------------------------------------------------------------

def test_noop_method_outputs():
    iv = build("noop_method")
    assert iv["real_output"] == "hello"
    assert iv["believed_output"] == "HELLO"


def test_range_1_to_n_outputs():
    iv = build("range_1_to_n")
    real_lines = iv["real_output"].splitlines()
    bel_lines = iv["believed_output"].splitlines()
    assert real_lines == ["0", "1", "2", "3", "4"]
    assert bel_lines == ["1", "2", "3", "4", "5"]


def test_index_1_based_outputs():
    iv = build("index_1_based")
    assert iv["real_output"] == "20"
    assert iv["believed_output"] == "10"


def test_assign_copies_outputs():
    iv = build("assign_copies")
    assert iv["real_output"] == "[1, 2, 3, 4]"
    assert iv["believed_output"] == "[1, 2, 3]"


def test_add_before_div_outputs():
    iv = build("add_before_div")
    assert iv["real_output"] == "20.0"
    assert iv["believed_output"] == "15.0"


# ---------------------------------------------------------------------------
# Held-out misconception
# ---------------------------------------------------------------------------

def test_held_out_raises():
    with pytest.raises(NotImplementedError):
        build("index_from_m1")


def test_unknown_id_raises():
    with pytest.raises(KeyError):
        build("made_up_id")


# ---------------------------------------------------------------------------
# build_all
# ---------------------------------------------------------------------------

def test_build_all_covers_all_live_families():
    data = build_all()
    for mid in LIVE_FAMILIES:
        assert mid in data, f"build_all() missing {mid}"


def test_build_all_excludes_held_out():
    data = build_all()
    assert "index_from_m1" not in data


# ---------------------------------------------------------------------------
# load
# ---------------------------------------------------------------------------

def test_load_returns_dict():
    data = load()
    assert isinstance(data, dict)
    assert len(data) >= 5


def test_load_has_required_keys_per_entry():
    data = load()
    for mid, iv in data.items():
        missing = REQUIRED_KEYS - iv.keys()
        assert not missing, f"[{mid}] missing in loaded data: {missing}"
