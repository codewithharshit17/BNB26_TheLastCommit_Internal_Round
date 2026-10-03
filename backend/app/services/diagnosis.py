"""Diagnosis service — wires the engine, item bank, and ML posterior together.

ITEMS is loaded from the pre-generated items_bank.json at startup.
Falls back to generate() on the fly if the JSON file is missing so the
server stays bootable even in a fresh checkout.

Session posterior is kept in memory (SESSIONS dict).  The backend persists
it to SQLite via learner_store so it survives restarts.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path

from engine.signature import believed_source, signature
from engine.items.generator import load as load_items
from ml.posterior import info_gain, update

# ---------------------------------------------------------------------------
# Hypothesis set (excluding held-out index_from_m1)
# ---------------------------------------------------------------------------

HYPS = [
    "correct",
    "noop_method",
    "range_1_to_n",
    "index_1_based",
    "assign_copies",
    "add_before_div",
    "unknown",
]

# ---------------------------------------------------------------------------
# Item bank — keyed by item_id for O(1) lookup
# ---------------------------------------------------------------------------

def _load_item_bank() -> dict[str, dict]:
    """Load items and index by item_id."""
    items = load_items()
    return {item["item_id"]: item for item in items}


ITEMS: dict[str, dict] = _load_item_bank()

# First diagnostic item across all families (one per family, ordered by family)
_FIRST_ITEMS: dict[str, str] = {}
for _item in ITEMS.values():
    if _item["kind"] == "diagnostic" and _item["family"] not in _FIRST_ITEMS:
        _FIRST_ITEMS[_item["family"]] = _item["item_id"]
# Default first item: first diagnostic item in the bank
_DEFAULT_START_ITEM_ID: str = next(
    (iid for iid, it in ITEMS.items() if it["kind"] == "diagnostic"),
    next(iter(ITEMS))
)

# ---------------------------------------------------------------------------
# Bank map  {hypothesis_id: [bank_ids]}
# ---------------------------------------------------------------------------

BANK_MAP: dict[str, list[int]] = json.loads(
    (Path(__file__).resolve().parents[3] / "engine" / "bank_map.json")
    .read_text(encoding="utf-8")
)

# ---------------------------------------------------------------------------
# In-memory session store
# ---------------------------------------------------------------------------

SESSIONS: dict[str, dict[str, float]] = {}


# ---------------------------------------------------------------------------
# Service functions
# ---------------------------------------------------------------------------

def _flat_prior() -> dict[str, float]:
    return {h: 1.0 / len(HYPS) for h in HYPS}


def start_session() -> dict:
    """Create a new session and return {session_id, item}."""
    sid = str(uuid.uuid4())
    SESSIONS[sid] = _flat_prior()

    # Return the first diagnostic item
    start_item = ITEMS[_DEFAULT_START_ITEM_ID]
    # Strip internal fields not in the API schema
    return {
        "session_id": sid,
        "item": _to_api_item(start_item),
    }


def answer(payload) -> dict:
    """Process a student answer and return the posterior + next action."""
    from fastapi import HTTPException

    if payload.session_id not in SESSIONS:
        raise HTTPException(404, "unknown session")
    if payload.item_id not in ITEMS:
        raise HTTPException(404, "unknown item")

    item = ITEMS[payload.item_id]

    # Use stored signature when available (avoids re-running the sandbox)
    if "signature" in item:
        sig = item["signature"]
    else:
        sig = signature(item["code"])

    # Update posterior
    post = update(
        SESSIONS[payload.session_id],
        sig,
        payload.answer.strip(),
        payload.confidence,
    )
    SESSIONS[payload.session_id] = post

    top = max(post, key=post.get)

    # Determine next action
    nxt = _next_action(post, top, payload.item_id, sig)

    # Build believed_source (only meaningful for live misconceptions)
    if top not in {"correct", "unknown"}:
        bsrc = believed_source(item["code"], top)
    else:
        bsrc = item["code"]

    return {
        "posterior": post,
        "top": top,
        "bank_ids": BANK_MAP.get(top, []),
        "real_output": sig["real"],
        "believed_output": sig.get(top, sig["real"]),
        "believed_source": bsrc,
        "next": nxt,
    }


def _next_action(
    post: dict[str, float],
    top: str,
    current_item_id: str,
    current_sig: dict,
) -> dict:
    """Decide what to do next based on the current posterior."""
    top_prob = post[top]

    # Confident diagnosis of a misconception → intervene
    if top_prob >= 0.8 and top not in {"correct", "unknown"}:
        return {"action": "intervene", "item": None, "misconception": top}

    # Confident correct → done
    if top_prob >= 0.8 and top == "correct":
        return {"action": "done", "item": None, "misconception": None}

    # Ambiguous — find best probe by information gain
    best_probe = _best_probe(post, current_item_id)
    if best_probe is not None:
        return {"action": "probe", "item": _to_api_item(ITEMS[best_probe]), "misconception": None}

    # No good probe found — reassess
    return {"action": "reassess", "item": None, "misconception": top}


def _best_probe(
    post: dict[str, float],
    exclude_item_id: str,
) -> str | None:
    """Return the item_id of the highest-information-gain item, or None."""
    best_id = None
    best_ig = -1.0

    for iid, item in ITEMS.items():
        if iid == exclude_item_id:
            continue
        if item["kind"] not in {"probe", "discriminator"}:
            continue
        sig = item.get("signature", {})
        if not sig:
            continue
        try:
            ig = info_gain(post, sig)
        except Exception:
            continue
        if ig > best_ig:
            best_ig = ig
            best_id = iid

    return best_id if best_ig > 0 else None


def _to_api_item(item: dict) -> dict:
    """Strip internal-only fields before returning to the API layer."""
    return {
        "item_id": item["item_id"],
        "kind": item["kind"],
        "family": item["family"],
        "prompt": item.get("prompt", "What does this program print?"),
        "code": item["code"],
        "problem_ref": item.get("problem_ref"),
    }
