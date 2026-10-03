"""Intervention content builder for Re:Learn.

For each of the 5 live misconception families this module provides:
  - A plain-language title and bank description
  - A contrast code snippet (verified by actually running it)
  - The real output and believed output (computed, never typed by hand)
  - Three plain-language correction steps
  - A one-line takeaway

``build(misconception_id)`` → dict matching the InterventionResponse schema.
``save()`` → writes ``engine/interventions/interventions.json``.
``load()`` → loads the pre-built JSON (or builds on the fly if missing).
"""

from __future__ import annotations

import json
import pathlib
from typing import Any

from engine.sandbox import run
from engine.signature import believed_source

# ---------------------------------------------------------------------------
# Intervention content database
# ---------------------------------------------------------------------------
# Each entry is a template dict. ``contrast_code`` is the snippet used to
# illustrate the difference.  real_output and believed_output are computed
# at build time by running the code through the sandbox.

_INTERVENTION_TEMPLATES: dict[str, dict[str, Any]] = {

    "noop_method": {
        "title": "String methods don't change the original — they return a new value",
        "bank_description": (
            "Student believes that calling a string method (such as .upper(), "
            ".lower(), .strip(), .replace(), or .split()) modifies the original "
            "string variable in place, like list.append() does."
        ),
        "contrast_code": (
            'name = "hello"\n'
            'name.upper()\n'
            'print(name)          # student expects "HELLO"\n'
            '\n'
            '# Fix: capture the return value\n'
            'name = name.upper()\n'
            'print(name)          # now prints "HELLO"'
        ),
        "steps": [
            "Strings in Python are immutable — they can never be changed in place.",
            "Methods like .upper() create and RETURN a brand-new string; "
            "the original variable is untouched unless you assign the result back.",
            'Write  name = name.upper()  (capture the return value) '
            "instead of just  name.upper()  (which discards it).",
        ],
        "takeaway": (
            "Every string method returns a new string — "
            "always assign the result if you want to keep it."
        ),
        # Snippet used to compute real vs believed outputs
        "_demo_code": 'name = "hello"\nname.upper()\nprint(name)',
    },

    "range_1_to_n": {
        "title": "range(n) starts at 0, not 1 — and stops before n",
        "bank_description": (
            "Student believes that range(n) produces the sequence 1, 2, ..., n "
            "(like a 1-based count), when it actually produces 0, 1, ..., n-1."
        ),
        "contrast_code": (
            "for i in range(5):\n"
            "    print(i)   # prints 0 1 2 3 4  NOT 1 2 3 4 5\n"
            "\n"
            "# To get 1..5 write:\n"
            "for i in range(1, 6):\n"
            "    print(i)   # prints 1 2 3 4 5"
        ),
        "steps": [
            "range(n) always starts at 0 — the first value is 0, not 1.",
            "range(n) stops BEFORE n — it never includes n itself.",
            "To get 1 through n use range(1, n+1).  "
            "To get k through m-1 use range(k, m).",
        ],
        "takeaway": (
            "range(n) gives you exactly n numbers: 0, 1, 2, ..., n-1."
        ),
        "_demo_code": "for i in range(5):\n    print(i)",
    },

    "index_1_based": {
        "title": "Python lists and strings start at index 0, not 1",
        "bank_description": (
            "Student believes the first element of a list or string is at index 1, "
            "so a[1] is the first element, a[2] is the second, and so on."
        ),
        "contrast_code": (
            "a = [10, 20, 30]\n"
            "print(a[0])   # 10  — the FIRST element\n"
            "print(a[1])   # 20  — the SECOND element\n"
            "print(a[2])   # 30  — the THIRD element"
        ),
        "steps": [
            "Python uses 0-based indexing: the very first element is always at index 0.",
            "a[1] is the SECOND element, a[2] is the THIRD, and so on.",
            "To access the first element write a[0]; "
            "the last element of a length-n list is at a[n-1] (or a[-1]).",
        ],
        "takeaway": (
            "Index 0 = first element. Index 1 = second. Always subtract 1 from your intuition."
        ),
        "_demo_code": "a = [10, 20, 30]\nprint(a[1])",
    },

    "assign_copies": {
        "title": "Assigning a list variable creates an alias, not a copy",
        "bank_description": (
            "Student believes that writing b = a creates an independent copy of "
            "the list stored in a, so later changes to a do not affect b."
        ),
        "contrast_code": (
            "a = [1, 2, 3]\n"
            "b = a          # b is an ALIAS — same list in memory\n"
            "a.append(4)\n"
            "print(b)       # [1, 2, 3, 4]  — b sees the change too\n"
            "\n"
            "# To make an independent copy:\n"
            "b = a.copy()   # or b = list(a) or b = a[:]\n"
            "a.append(5)\n"
            "print(b)       # [1, 2, 3, 4]  — unchanged"
        ),
        "steps": [
            "In Python, lists are objects stored in memory.  "
            "b = a copies the REFERENCE (address), not the data — "
            "both names now point to the same list.",
            "Any mutation through either name (a.append, b.pop, etc.) "
            "affects the single shared list.",
            "To get an independent copy use a.copy(), list(a), or a[:].",
        ],
        "takeaway": (
            "b = a makes two names for one list. Use b = a.copy() to get two separate lists."
        ),
        "_demo_code": "a = [1, 2, 3]\nb = a\na.append(4)\nprint(b)",
    },

    "add_before_div": {
        "title": "Python follows standard operator precedence: * and / before + and -",
        "bank_description": (
            "Student believes that addition (+) is evaluated before division (/), "
            "so  a + b / c  is computed as  (a + b) / c  instead of  a + (b / c)."
        ),
        "contrast_code": (
            "print(10 + 20 / 2)    # 20.0  NOT 15.0\n"
            "#  Python evaluates: 10 + (20 / 2) = 10 + 10.0 = 20.0\n"
            "#  Student expects:  (10 + 20) / 2 = 30 / 2   = 15.0\n"
            "\n"
            "# Use parentheses to force the order you want:\n"
            "print((10 + 20) / 2)  # 15.0"
        ),
        "steps": [
            "Python (like maths) evaluates * and / BEFORE + and -, "
            "so  a + b / c  means  a + (b / c).",
            "If you want addition first, use explicit parentheses: (a + b) / c.",
            "When in doubt, add parentheses — they make the intent clear and prevent bugs.",
        ],
        "takeaway": (
            "Division binds tighter than addition. Write (a+b)/c if you mean that."
        ),
        "_demo_code": "print(10 + 20 / 2)",
    },
}


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

def build(misconception_id: str) -> dict[str, Any]:
    """Build an intervention dict for *misconception_id*.

    Returns a dict matching the ``InterventionResponse`` Pydantic schema:
        title, bank_description, contrast_code,
        real_output, believed_output, steps, takeaway.

    Raises ``KeyError`` if the id is unknown, ``NotImplementedError`` if this
    is the held-out misconception (index_from_m1).
    """
    if misconception_id == "index_from_m1":
        raise NotImplementedError(
            "TODO(Sukhada): index_from_m1 is held out — no intervention content"
        )

    if misconception_id not in _INTERVENTION_TEMPLATES:
        raise KeyError(f"No intervention content for misconception: {misconception_id!r}")

    tmpl = _INTERVENTION_TEMPLATES[misconception_id]
    demo = tmpl["_demo_code"]

    real_out = run(demo)
    believed_out = run(believed_source(demo, misconception_id))

    return {
        "title": tmpl["title"],
        "bank_description": tmpl["bank_description"],
        "contrast_code": tmpl["contrast_code"],
        "real_output": real_out,
        "believed_output": believed_out,
        "steps": tmpl["steps"],
        "takeaway": tmpl["takeaway"],
    }


def build_all() -> dict[str, dict[str, Any]]:
    """Build interventions for all live misconception families."""
    result: dict[str, dict[str, Any]] = {}
    for mid in _INTERVENTION_TEMPLATES:
        if mid == "index_from_m1":
            continue
        result[mid] = build(mid)
    return result


def save(path: str | None = None) -> dict[str, dict[str, Any]]:
    """Build all interventions and write to ``engine/interventions/interventions.json``."""
    if path is None:
        path = str(pathlib.Path(__file__).parent / "interventions.json")

    data = build_all()
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)

    print(f"Saved interventions for {list(data.keys())} to {path}")
    return data


def load(path: str | None = None) -> dict[str, dict[str, Any]]:
    """Load pre-built interventions JSON, generating it first if missing."""
    if path is None:
        path = str(pathlib.Path(__file__).parent / "interventions.json")

    p = pathlib.Path(path)
    if not p.exists():
        return save(path)

    return json.loads(p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    saved = save()
    for mid, iv in saved.items():
        print(f"\n{'='*60}")
        print(f"[{mid}] {iv['title']}")
        print(f"  real_output:    {iv['real_output']!r}")
        print(f"  believed_output:{iv['believed_output']!r}")
