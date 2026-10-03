"""Item bank generator for Re:Learn.

Builds a list of diagnostic items by:
1. Defining templates (code strings with placeholders) per misconception family.
2. Filling templates with varied constants/names to produce surface-different items.
3. Calling signature() on every generated item so real + believed outputs are stored.
4. Tagging each item with kind: diagnostic | probe | transfer | discriminator | retest.
5. Filtering out non-discriminating items (believed == real for the target family).

Run directly to (re-)generate engine/items/items_bank.json:

    PYTHONPATH=. python -m engine.items.generator

Contract for each item dict (mirrors contracts/item.schema.json):
    {
        "item_id":    "i_0042",
        "kind":       "diagnostic|probe|transfer|discriminator|retest",
        "family":     "noop_method",
        "prompt":     "What does this program print?",
        "code":       "<python source>",
        "problem_ref": null,
        "signature":  {"real": "...", "noop_method": "...", ...},
        "discriminates": true   # believed_output != real_output for this family
    }
"""

from __future__ import annotations

import json
import pathlib
from typing import Any

from engine.signature import signature as compute_signature
from engine.rewrites import REGISTRY

# ---------------------------------------------------------------------------
# Template definitions
# ---------------------------------------------------------------------------
# Each template is a dict:
#   family   : str            hypothesis id this template targets
#   kind     : str            diagnostic | probe | transfer | discriminator | retest
#   variants : list[dict]     each variant provides substitution kwargs
#   template : str            Python source with {placeholder} slots

_TEMPLATES: list[dict[str, Any]] = [

    # =========================================================================
    # noop_method  (bank ids 6, 7, 8, 9, 10, 34, 36)
    # Belief: method call mutates the variable in place
    # =========================================================================

    # --- upper ---
    {
        "family": "noop_method", "kind": "diagnostic",
        "template": 'name = "{word}"\nname.upper()\nprint(name)',
        "variants": [
            {"word": "hello"},
            {"word": "world"},
            {"word": "python"},
        ],
    },
    {
        "family": "noop_method", "kind": "discriminator",
        "template": 'greeting = "{word}"\ngreeting.upper()\nprint(greeting)',
        "variants": [
            {"word": "hi"},
            {"word": "bye"},
        ],
    },
    {
        "family": "noop_method", "kind": "transfer",
        "template": 'city = "{word}"\ncity.upper()\nprint(city)',
        "variants": [
            {"word": "mumbai"},
            {"word": "delhi"},
        ],
    },
    # --- lower ---
    {
        "family": "noop_method", "kind": "discriminator",
        "template": 'msg = "{word}"\nmsg.lower()\nprint(msg)',
        "variants": [
            {"word": "HELLO"},
            {"word": "PYTHON"},
        ],
    },
    # --- strip ---
    {
        "family": "noop_method", "kind": "discriminator",
        "template": 's = "  {word}  "\ns.strip()\nprint(s)',
        "variants": [
            {"word": "hello"},
            {"word": "test"},
        ],
    },
    # --- split ---
    {
        "family": "noop_method", "kind": "transfer",
        "template": 'text = "{w1} {w2} {w3}"\ntext.split()\nprint(text)',
        "variants": [
            {"w1": "a", "w2": "b", "w3": "c"},
            {"w1": "one", "w2": "two", "w3": "three"},
        ],
    },
    # --- replace ---
    {
        "family": "noop_method", "kind": "discriminator",
        "template": 's = "{src}"\ns.replace("{old}", "{new}")\nprint(s)',
        "variants": [
            {"src": "hello", "old": "hello", "new": "world"},
            {"src": "cat", "old": "cat", "new": "dog"},
        ],
    },
    # probe: two families produce different outputs here (noop_method vs range_1_to_n)
    {
        "family": "noop_method", "kind": "probe",
        "template": 'words = "{w1} {w2}"\nwords.split()\nprint(words)',
        "variants": [
            {"w1": "x", "w2": "y"},
        ],
    },
    # retest: same surface but different constants
    {
        "family": "noop_method", "kind": "retest",
        "template": 'label = "{word}"\nlabel.upper()\nprint(label)',
        "variants": [
            {"word": "relearn"},
            {"word": "kiro"},
        ],
    },

    # =========================================================================
    # range_1_to_n  (bank id 1)
    # Belief: range(n) yields 1 .. n
    # =========================================================================

    {
        "family": "range_1_to_n", "kind": "diagnostic",
        "template": "for i in range({n}):\n    print(i)",
        "variants": [
            {"n": 3},
            {"n": 5},
        ],
    },
    {
        "family": "range_1_to_n", "kind": "discriminator",
        "template": "total = 0\nfor i in range({n}):\n    total += i\nprint(total)",
        "variants": [
            {"n": 4},
            {"n": 3},
            {"n": 5},
        ],
    },
    {
        "family": "range_1_to_n", "kind": "probe",
        "template": "nums = list(range({n}))\nprint(nums[0])",
        "variants": [
            {"n": 5},
            {"n": 3},
        ],
    },
    # transfer items: different surface forms (different variable names / constructs)
    {
        "family": "range_1_to_n", "kind": "transfer",
        "template": "nums = []\nfor k in range({n}):\n    nums.append(k)\nprint(nums)",
        "variants": [
            {"n": 3},
            {"n": 4},
        ],
    },
    {
        "family": "range_1_to_n", "kind": "transfer",
        "template": "evens = [x for x in range({n}) if x % 2 == 0]\nprint(evens)",
        "variants": [
            {"n": 6},
        ],
    },
    {
        "family": "range_1_to_n", "kind": "transfer",
        "template": "count = 0\nfor _ in range({n}):\n    count += 1\nprint(count)",
        "variants": [
            {"n": 4},
            {"n": 6},
        ],
    },
    {
        "family": "range_1_to_n", "kind": "discriminator",
        "template": "vals = []\nfor i in range({n}):\n    vals.append(i)\nprint(vals[0])",
        "variants": [
            {"n": 5},
        ],
    },
    {
        "family": "range_1_to_n", "kind": "retest",
        "template": "for x in range({n}):\n    print(x)",
        "variants": [
            {"n": 2},
        ],
    },

    # =========================================================================
    # index_1_based  (bank ids 15, 66)
    # Belief: first element is at index 1
    # =========================================================================

    {
        "family": "index_1_based", "kind": "diagnostic",
        "template": "a = [{v0}, {v1}, {v2}]\nprint(a[1])",
        "variants": [
            {"v0": 10, "v1": 20, "v2": 30},
            {"v0": 5,  "v1": 10, "v2": 15},
        ],
    },
    {
        "family": "index_1_based", "kind": "diagnostic",
        "template": 's = "{word}"\nprint(s[1])',
        "variants": [
            {"word": "hello"},
            {"word": "python"},
        ],
    },
    {
        "family": "index_1_based", "kind": "discriminator",
        "template": "a = [{v0}, {v1}, {v2}, {v3}]\nprint(a[3])",
        "variants": [
            {"v0": 100, "v1": 200, "v2": 300, "v3": 400},
            {"v0": 1,   "v1": 2,   "v2": 3,   "v3": 4},
        ],
    },
    {
        "family": "index_1_based", "kind": "discriminator",
        "template": "a = [{v0}, {v1}, {v2}]\nprint(a[2])",
        "variants": [
            {"v0": 7, "v1": 8, "v2": 9},
        ],
    },
    {
        "family": "index_1_based", "kind": "transfer",
        "template": "nums = [{v0}, {v1}, {v2}, {v3}, {v4}]\nprint(nums[2])",
        "variants": [
            {"v0": 10, "v1": 20, "v2": 30, "v3": 40, "v4": 50},
        ],
    },
    {
        "family": "index_1_based", "kind": "transfer",
        "template": 'letters = "{word}"\nprint(letters[2])',
        "variants": [
            {"word": "abcde"},
        ],
    },
    {
        "family": "index_1_based", "kind": "probe",
        "template": "seq = [{v0}, {v1}, {v2}]\nfirst = seq[1]\nprint(first)",
        "variants": [
            {"v0": 99, "v1": 88, "v2": 77},
        ],
    },
    {
        "family": "index_1_based", "kind": "retest",
        "template": "data = [{v0}, {v1}, {v2}, {v3}]\nprint(data[1])",
        "variants": [
            {"v0": 2, "v1": 4, "v2": 6, "v3": 8},
            {"v0": 11, "v1": 22, "v2": 33, "v3": 44},
        ],
    },

    # =========================================================================
    # assign_copies  (bank ids 13, 55)
    # Belief: b = a makes an independent copy of the list
    # =========================================================================

    {
        "family": "assign_copies", "kind": "diagnostic",
        "template": "a = [{v0}, {v1}, {v2}]\nb = a\na.append({v3})\nprint(b)",
        "variants": [
            {"v0": 1, "v1": 2, "v2": 3, "v3": 4},
            {"v0": 10, "v1": 20, "v2": 30, "v3": 40},
        ],
    },
    {
        "family": "assign_copies", "kind": "discriminator",
        "template": "x = [{v0}, {v1}]\ny = x\nx.insert(0, {v2})\nprint(y)",
        "variants": [
            {"v0": 5, "v1": 6, "v2": 0},
            {"v0": 9, "v1": 10, "v2": 1},
        ],
    },
    {
        "family": "assign_copies", "kind": "discriminator",
        "template": "original = [{v0}, {v1}, {v2}]\nbackup = original\noriginal.pop()\nprint(backup)",
        "variants": [
            {"v0": 1, "v1": 2, "v2": 3},
        ],
    },
    {
        "family": "assign_copies", "kind": "transfer",
        "template": "lst = [{v0}, {v1}, {v2}]\ncopy_lst = lst\nlst[0] = {v3}\nprint(copy_lst)",
        "variants": [
            {"v0": 1, "v1": 2, "v2": 3, "v3": 99},
        ],
    },
    {
        "family": "assign_copies", "kind": "transfer",
        "template": "nums = [{v0}, {v1}]\nalias = nums\nalias.append({v2})\nprint(nums)",
        "variants": [
            {"v0": 7, "v1": 8, "v2": 9},
        ],
    },
    {
        "family": "assign_copies", "kind": "probe",
        "template": "a = [{v0}, {v1}, {v2}]\nb = a\nb.append({v3})\nprint(a)",
        "variants": [
            {"v0": 1, "v1": 2, "v2": 3, "v3": 4},
        ],
    },
    {
        "family": "assign_copies", "kind": "retest",
        "template": "p = [{v0}, {v1}]\nq = p\np += [{v2}]\nprint(q)",
        "variants": [
            {"v0": 10, "v1": 20, "v2": 30},
        ],
    },

    # =========================================================================
    # add_before_div  (bank ids 63, 64, 65)
    # Belief: a + b / c  is evaluated as  (a + b) / c
    # =========================================================================

    {
        "family": "add_before_div", "kind": "diagnostic",
        "template": "print({a} + {b} / {c})",
        "variants": [
            {"a": 10, "b": 20, "c": 2},
            {"a": 1,  "b": 8,  "c": 4},
        ],
    },
    {
        "family": "add_before_div", "kind": "discriminator",
        "template": "print({a} - {b} * {c})",
        "variants": [
            {"a": 10, "b": 2, "c": 3},
            {"a": 20, "b": 4, "c": 2},
        ],
    },
    {
        "family": "add_before_div", "kind": "discriminator",
        "template": "x = {a} + {b} / {c}\nprint(x)",
        "variants": [
            {"a": 5, "b": 6, "c": 2},
            {"a": 3, "b": 12, "c": 4},
        ],
    },
    {
        "family": "add_before_div", "kind": "transfer",
        "template": "a = {a}\nb = {b}\nc = {c}\nprint(a + b / c)",
        "variants": [
            {"a": 10, "b": 20, "c": 5},
        ],
    },
    {
        "family": "add_before_div", "kind": "transfer",
        "template": "result = {a} + {b} / {c}\nprint(result)",
        "variants": [
            {"a": 100, "b": 50, "c": 5},
        ],
    },
    {
        "family": "add_before_div", "kind": "probe",
        "template": "ans = {a} + {b} / {c}\nprint(round(ans, 1))",
        "variants": [
            {"a": 2, "b": 9, "c": 3},
        ],
    },
    {
        "family": "add_before_div", "kind": "probe",
        "template": "print(round({a} + {b} / {c}, 2))",
        "variants": [
            {"a": 1, "b": 5, "c": 2},
        ],
    },
    {
        "family": "add_before_div", "kind": "retest",
        "template": "print({a} + {b} / {c})",
        "variants": [
            {"a": 6, "b": 4, "c": 2},
            {"a": 0, "b": 10, "c": 5},
        ],
    },
]


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

def generate(include_non_discriminating: bool = False) -> list[dict[str, Any]]:
    """Generate all items, compute signatures, filter non-discriminating ones.

    Args:
        include_non_discriminating: if True, keep items where believed==real
            for the target family (useful for testing that the filter works).

    Returns:
        List of item dicts, each with a stable ``item_id`` of the form
        ``i_NNNN`` (zero-padded 4-digit integer).
    """
    items: list[dict[str, Any]] = []
    counter = 0

    for tmpl in _TEMPLATES:
        family = tmpl["family"]
        kind = tmpl["kind"]
        code_template = tmpl["template"]

        for variant in tmpl["variants"]:
            code = code_template.format(**variant)
            sig = compute_signature(code)

            real_out = sig["real"]
            believed_out = sig.get(family, real_out)
            discriminates = (real_out != believed_out)

            if not discriminates and not include_non_discriminating:
                continue  # useless item for this family — skip

            counter += 1
            item_id = f"i_{counter:04d}"

            items.append({
                "item_id": item_id,
                "kind": kind,
                "family": family,
                "prompt": "What does this program print?",
                "code": code,
                "problem_ref": None,
                "signature": sig,
                "discriminates": discriminates,
            })

    return items


def save(path: str | None = None) -> list[dict[str, Any]]:
    """Generate items and save to ``engine/items/items_bank.json``."""
    if path is None:
        path = str(pathlib.Path(__file__).parent / "items_bank.json")

    items = generate()
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(items, fh, indent=2, ensure_ascii=False)

    print(f"Saved {len(items)} items to {path}")
    return items


def load(path: str | None = None) -> list[dict[str, Any]]:
    """Load items from the pre-generated JSON bank.

    Falls back to generating on the fly if the file doesn't exist yet.
    """
    if path is None:
        path = str(pathlib.Path(__file__).parent / "items_bank.json")

    p = pathlib.Path(path)
    if not p.exists():
        return save(path)

    return json.loads(p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    saved = save()
    families = {}
    kinds = {}
    for item in saved:
        families[item["family"]] = families.get(item["family"], 0) + 1
        kinds[item["kind"]] = kinds.get(item["kind"], 0) + 1

    print("\nItems per family:")
    for k, v in sorted(families.items()):
        print(f"  {k:20s}: {v}")

    print("\nItems per kind:")
    for k, v in sorted(kinds.items()):
        print(f"  {k:14s}: {v}")
