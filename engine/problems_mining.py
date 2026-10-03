"""Mine problems_processed.json for Re:Learn P1 items.

For each problem we:
1. Skip FalconCode entries (no public license per PRD).
2. Parse unit_tests → extract (call_expr, expected_value) pairs.
3. Run the reference solution against each test input to confirm it passes.
4. For each live misconception rewrite, apply the rewrite to the solution
   and run it on the same inputs.
5. If the rewritten solution produces a different output on at least one
   test input, the (problem, misconception) pair is a usable P1 item.

Output
------
``engine/data/mcminer/mined_problems.json`` — list of dicts:
    {
        "problem_id":   int,
        "title":        str,
        "source":       str,
        "description":  str,
        "solution":     str,          # reference solution code
        "unit_tests":   str,          # raw assert block
        "tags":         [str],
        "misconceptions": [           # families where rewrite changes output
            {
                "family":           str,
                "test_input":       str,   # call expression that differs
                "real_output":      str,
                "believed_output":  str,
            }
        ]
    }

Run directly:
    PYTHONPATH=. python -m engine.problems_mining
"""

from __future__ import annotations

import ast
import json
import pathlib
import re
import textwrap
from typing import Any

from engine.rewrites import LIVE_REGISTRY
from engine.sandbox import run_inprocess
from engine.signature import believed_source

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_DATA_DIR = pathlib.Path(__file__).parent / "data" / "mcminer"
_PROBLEMS_FILE = _DATA_DIR / "problems_processed.json"
_OUTPUT_FILE = _DATA_DIR / "mined_problems.json"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_EXCLUDED_SOURCES = {"falconcode"}  # no public license
_MAX_PROBLEMS = 30                  # PRD §14.1 step 7: keep best 15-30
_MIN_PROBLEMS = 15
_TIMEOUT = 2.0


# ---------------------------------------------------------------------------
# Unit-test parser
# ---------------------------------------------------------------------------

def _parse_unit_tests(unit_tests_str: str) -> list[tuple[str, str]]:
    """Parse ``assert <call> == <expected>`` lines into (call, expected) pairs.

    Returns a list of (call_expr_str, expected_str) tuples.
    Only handles simple equality assertions; skips complex ones.
    """
    pairs: list[tuple[str, str]] = []
    for line in unit_tests_str.splitlines():
        line = line.strip()
        if not line.startswith("assert "):
            continue
        # assert <lhs> == <rhs>
        m = re.match(r"assert\s+(.+?)\s*==\s*(.+)$", line)
        if not m:
            continue
        lhs = m.group(1).strip()
        rhs = m.group(2).strip()
        pairs.append((lhs, rhs))
    return pairs


# ---------------------------------------------------------------------------
# Safe test runner
# ---------------------------------------------------------------------------

def _run_with_solution(solution: str, call_expr: str) -> str:
    """Combine solution code + a print(call_expr) and run in sandbox."""
    src = solution + "\n" + f"print({call_expr})"
    return run_inprocess(src, timeout=_TIMEOUT)


def _run_with_believed(solution: str, call_expr: str, mid: str) -> str:
    """Apply rewrite *mid* to solution, run call_expr, return output."""
    try:
        bsrc = believed_source(solution, mid)
    except Exception:
        return "RewriteError"
    src = bsrc + "\n" + f"print({call_expr})"
    return run_inprocess(src, timeout=_TIMEOUT)


# ---------------------------------------------------------------------------
# Core miner
# ---------------------------------------------------------------------------

def mine(
    problems_path: str | None = None,
    max_problems: int = _MAX_PROBLEMS,
    verbose: bool = False,
) -> list[dict[str, Any]]:
    """Mine usable P1 problems from problems_processed.json.

    For each problem:
    - Confirm at least one reference solution passes its own unit tests
      (filters out broken/incomplete problems).
    - For each live misconception rewrite, check whether applying the rewrite
      to the solution changes the output on at least one test input.
    - Keep problems that are discriminating for at least one misconception.

    Args:
        problems_path: Override path to problems_processed.json.
        max_problems:  Maximum number of problems to return (PRD: 15-30).
        verbose:       Print progress to stdout.

    Returns:
        List of mined problem dicts with a ``misconceptions`` field.
    """
    if problems_path is None:
        problems_path = str(_PROBLEMS_FILE)

    p = pathlib.Path(problems_path)
    if not p.exists():
        raise FileNotFoundError(
            f"problems_processed.json not found at {problems_path}.\n"
            "Run:  Invoke-WebRequest https://raw.githubusercontent.com/"
            "taisazero/mcminer/main/dataset/problems_processed.json "
            "-OutFile engine/data/mcminer/problems_processed.json"
        )

    problems: list[dict] = json.loads(p.read_text(encoding="utf-8"))
    if verbose:
        print(f"Loaded {len(problems)} problems.")

    results: list[dict[str, Any]] = []

    for prob in problems:
        # Skip FalconCode (no public license)
        source = prob.get("source", "")
        if any(ex in source.lower() for ex in _EXCLUDED_SOURCES):
            continue

        solutions: list[str] = prob.get("solutions", [])
        if not solutions:
            continue

        unit_tests_str: str = prob.get("unit_tests", "").strip()
        if not unit_tests_str:
            continue

        # Parse test cases
        test_pairs = _parse_unit_tests(unit_tests_str)
        if not test_pairs:
            continue

        # Find a reference solution that passes at least 2 of its own tests
        working_solution: str | None = None
        for sol in solutions:
            passes = 0
            for call_expr, expected in test_pairs[:5]:  # check up to 5
                out = _run_with_solution(sol, call_expr)
                # Normalise: compare str representation
                try:
                    expected_val = str(eval(expected))  # noqa: S307 — trusted data
                except Exception:
                    expected_val = expected
                if out == expected_val:
                    passes += 1
            if passes >= min(2, len(test_pairs)):
                working_solution = sol
                break

        if working_solution is None:
            continue

        # Check each live misconception
        discriminating: list[dict[str, Any]] = []
        for entry in LIVE_REGISTRY:
            mid = entry["id"]
            for call_expr, _ in test_pairs[:5]:
                real_out = _run_with_solution(working_solution, call_expr)
                if real_out in ("Timeout", "SecurityError", "NoOutput"):
                    continue
                believed_out = _run_with_believed(working_solution, call_expr, mid)
                if believed_out in ("Timeout", "SecurityError", "NoOutput", "RewriteError"):
                    continue
                if real_out != believed_out:
                    discriminating.append({
                        "family": mid,
                        "test_input": call_expr,
                        "real_output": real_out,
                        "believed_output": believed_out,
                    })
                    break  # one discriminating input per family is enough

        if not discriminating:
            continue

        results.append({
            "problem_id": prob["id"],
            "title": prob.get("title", ""),
            "source": source,
            "description": prob.get("description", ""),
            "solution": working_solution,
            "unit_tests": unit_tests_str,
            "tags": prob.get("tags", []),
            "misconceptions": discriminating,
        })

        if verbose:
            families = [d["family"] for d in discriminating]
            print(f"  [OK] id={prob['id']:3d}  {prob.get('title','')[:45]:<45}  {families}")

        if len(results) >= max_problems:
            break

    return results


# ---------------------------------------------------------------------------
# Save / load
# ---------------------------------------------------------------------------

def save(
    problems_path: str | None = None,
    output_path: str | None = None,
    max_problems: int = _MAX_PROBLEMS,
    verbose: bool = True,
) -> list[dict[str, Any]]:
    """Mine and save results to mined_problems.json."""
    if output_path is None:
        output_path = str(_OUTPUT_FILE)

    results = mine(problems_path=problems_path, max_problems=max_problems, verbose=verbose)

    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(results)} mined problems to {output_path}")

    # Summary
    from collections import Counter
    family_counts: Counter = Counter()
    for r in results:
        for m in r["misconceptions"]:
            family_counts[m["family"]] += 1
    print("\nDiscriminating problems per misconception family:")
    for fam, count in sorted(family_counts.items()):
        print(f"  {fam:20s}: {count}")

    return results


def load(path: str | None = None) -> list[dict[str, Any]]:
    """Load pre-mined results, running mine() if the file is missing."""
    if path is None:
        path = str(_OUTPUT_FILE)
    p = pathlib.Path(path)
    if not p.exists():
        return save(output_path=path)
    return json.loads(p.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    save(verbose=True)
