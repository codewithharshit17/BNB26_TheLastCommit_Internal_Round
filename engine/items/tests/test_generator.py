"""Tests for engine/items/generator.py

Uses load() (pre-generated items_bank.json) for all structural checks so
tests run in milliseconds without re-running the sandbox on every item.
generate() is only called in the one test that explicitly needs it.
"""
import pytest
from engine.items.generator import generate, load


# ---------------------------------------------------------------------------
# Fixtures — use the pre-built bank for speed
# ---------------------------------------------------------------------------

def _items():
    """Load from items_bank.json (fast — no sandbox calls)."""
    return load()


# ---------------------------------------------------------------------------
# Structural / count tests  (use load())
# ---------------------------------------------------------------------------

def test_load_returns_list():
    assert isinstance(_items(), list)


def test_minimum_count():
    """Must contain at least 40 items."""
    items = _items()
    assert len(items) >= 40, f"Only {len(items)} items in bank"


def test_minimum_count_58():
    items = _items()
    assert len(items) >= 58, f"Only {len(items)} items (expected >=58)"


def test_item_schema():
    """Every item must have required keys with correct types."""
    required_keys = {"item_id", "kind", "family", "prompt", "code",
                     "problem_ref", "signature", "discriminates"}
    valid_kinds = {"diagnostic", "probe", "transfer", "discriminator", "retest"}
    for item in _items():
        assert required_keys <= item.keys(), f"Missing keys in {item['item_id']}"
        assert item["kind"] in valid_kinds, f"Bad kind: {item['kind']}"
        assert isinstance(item["signature"], dict)
        assert "real" in item["signature"]
        assert isinstance(item["code"], str) and item["code"].strip()


def test_all_items_are_discriminating():
    """All items in the bank must be discriminating (non-discriminating filtered out)."""
    for item in _items():
        family = item["family"]
        sig = item["signature"]
        assert sig.get(family) != sig["real"], (
            f"Non-discriminating item {item['item_id']} slipped through"
        )


def test_discriminates_flag_consistent():
    for item in _items():
        family = item["family"]
        sig = item["signature"]
        expected = sig.get(family) != sig["real"]
        assert item["discriminates"] == expected


def test_item_ids_are_unique():
    items = _items()
    ids = [i["item_id"] for i in items]
    assert len(ids) == len(set(ids)), "Duplicate item_ids found"


def test_per_family_discriminator_count():
    """Each live family must have at least 3 discriminator items."""
    from collections import defaultdict
    by_family: dict = defaultdict(lambda: defaultdict(int))
    for item in _items():
        by_family[item["family"]][item["kind"]] += 1

    live_families = {"noop_method", "range_1_to_n", "index_1_based",
                     "assign_copies", "add_before_div"}
    for fam in live_families:
        disc = by_family[fam].get("discriminator", 0)
        assert disc >= 3, f"{fam} has only {disc} discriminator items (need >=3)"


def test_per_family_transfer_count():
    """Each live family must have at least 2 transfer items."""
    from collections import defaultdict
    by_family: dict = defaultdict(lambda: defaultdict(int))
    for item in _items():
        by_family[item["family"]][item["kind"]] += 1

    live_families = {"noop_method", "range_1_to_n", "index_1_based",
                     "assign_copies", "add_before_div"}
    for fam in live_families:
        trans = by_family[fam].get("transfer", 0)
        assert trans >= 2, f"{fam} has only {trans} transfer items (need >=2)"


def test_signature_has_all_hypothesis_keys():
    """Every signature must contain keys for all 6 hypothesis families."""
    from engine.rewrites import REGISTRY
    expected = {e["id"] for e in REGISTRY} | {"real"}
    for item in _items():
        missing = expected - set(item["signature"].keys())
        assert not missing, f"Item {item['item_id']} signature missing: {missing}"


def test_load_returns_same_as_json():
    """load() returns a list of dicts with the required structure."""
    items = _items()
    assert isinstance(items, list)
    assert len(items) >= 40
    assert "item_id" in items[0]
    assert "signature" in items[0]


# ---------------------------------------------------------------------------
# generate() behaviour tests  (one call — verifies the logic, not all items)
# ---------------------------------------------------------------------------

def test_generate_returns_list():
    """generate() returns a list (runs sandbox — keep scope minimal)."""
    # Use a single-template subset to avoid running all ~400 sandbox calls.
    # We monkeypatch _TEMPLATES to just one template with one variant.
    import engine.items.generator as mod
    original = mod._TEMPLATES
    mod._TEMPLATES = [{
        "family": "noop_method",
        "kind": "diagnostic",
        "template": 'x = "hello"\nx.upper()\nprint(x)',
        "variants": [{}],
    }]
    try:
        items = mod.generate()
        assert isinstance(items, list)
        assert len(items) >= 1
    finally:
        mod._TEMPLATES = original


def test_generate_non_discriminating_filter():
    """Non-discriminating items are excluded from default generate()."""
    import engine.items.generator as mod
    original = mod._TEMPLATES
    # Template where noop_method does NOT change output (method already assigned)
    mod._TEMPLATES = [{
        "family": "noop_method",
        "kind": "diagnostic",
        "template": 'x = "hello"\nx = x.upper()\nprint(x)',
        "variants": [{}],
    }]
    try:
        items = mod.generate(include_non_discriminating=False)
        assert len(items) == 0   # should be filtered out — same output both ways
    finally:
        mod._TEMPLATES = original


def test_generate_include_non_discriminating_flag():
    """include_non_discriminating=True keeps all items."""
    import engine.items.generator as mod
    original = mod._TEMPLATES
    mod._TEMPLATES = [{
        "family": "noop_method",
        "kind": "diagnostic",
        "template": 'x = "hello"\nx = x.upper()\nprint(x)',
        "variants": [{}],
    }]
    try:
        items_all = mod.generate(include_non_discriminating=True)
        assert len(items_all) >= 1
    finally:
        mod._TEMPLATES = original
