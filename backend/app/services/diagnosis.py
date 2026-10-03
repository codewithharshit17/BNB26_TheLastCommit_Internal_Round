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

from fastapi import HTTPException

from engine.signature import signature
from engine.items.generator import load as load_items
from ml.integration import LIVE_HYPOTHESES, diagnose_answer

from . import learner_store
from .resolution import next_state

HYPS = ["correct", *LIVE_HYPOTHESES, "unknown"]
ITEMS = {
    "i1": {"item_id": "i1", "kind": "diagnostic", "family": "indexing", "prompt": "What does this print?", "code": "a = [10, 20, 30]\nprint(a[1])", "problem_ref": None},
    "i2": {"item_id": "i2", "kind": "probe", "family": "indexing", "prompt": "What does this print?", "code": "a = [10, 20, 30]\nprint(a[2])", "problem_ref": None},
    "i3": {"item_id": "i3", "kind": "discriminator", "family": "indexing", "prompt": "What does this print?", "code": "values = [4, 8, 12]\nprint(values[0])", "problem_ref": None},
    "i4": {"item_id": "i4", "kind": "discriminator", "family": "indexing", "prompt": "What does this print?", "code": "word = 'cat'\nprint(word[1])", "problem_ref": None},
    "i5": {"item_id": "i5", "kind": "discriminator", "family": "indexing", "prompt": "What does this print?", "code": "digits = [3, 6, 9]\nprint(digits[2])", "problem_ref": None},
    "i6": {"item_id": "i6", "kind": "transfer", "family": "indexing", "prompt": "What does this print?", "code": "label = 'ReLearn'\nprint(label[0])", "problem_ref": None},
    "i7": {"item_id": "i7", "kind": "transfer", "family": "indexing", "prompt": "What does this print?", "code": "scores = [11, 22, 33]\nprint(scores[1])", "problem_ref": None},
    "i8": {"item_id": "i8", "kind": "retest", "family": "indexing", "prompt": "What does this print?", "code": "colors = ['red', 'green', 'blue']\nprint(colors[2])", "problem_ref": None},
    "i9": {"item_id": "i9", "kind": "diagnostic", "family": "range", "prompt": "What does this loop print?", "code": "for n in range(3):\n    print(n)", "problem_ref": None},
    "i10": {"item_id": "i10", "kind": "diagnostic", "family": "range", "prompt": "What does this loop print?", "code": "for n in range(2, 5):\n    print(n)", "problem_ref": None},
}
BANK_MAP = json.loads((Path(__file__).resolve().parents[3] / "engine" / "bank_map.json").read_text(encoding="utf-8"))
BANK_DATA = json.loads((Path(__file__).resolve().parents[3] / "engine" / "data" / "mcminer" / "misconception_bank.json").read_text(encoding="utf-8"))
BANK_DESCRIPTIONS = {str(entry["id"]): entry["description"] for entry in BANK_DATA}
CONTRASTS = {
    "index_1_based": ("values = [10, 20, 30]\nprint(values[0])\nprint(values[1])", "Count list positions from zero."),
    "range_1_to_n": ("for n in range(3):\n    print(n)", "range(3) starts at 0 and stops before 3."),
    "noop_method": ("word = 'cat'\nword.upper()\nprint(word)", "String methods such as upper return a new string."),
    "assign_copies": ("a = [1]\nb = a\nb.append(2)\nprint(a)", "Assignment binds another name to the same list."),
    "add_before_div": ("print(2 + 6 / 2)", "Division happens before addition."),
}


def start_session():
    session_id = str(uuid.uuid4())
    prior = {hyp: 1 / len(HYPS) for hyp in HYPS}
    learner_store.save_session(session_id, prior, "i1")
    return {"session_id": session_id, "item": ITEMS["i1"]}


def _probe_candidates(item_id):
    """Return probe items with engine signatures for the ML selector."""
    return [
        {**candidate, "signature": signature(candidate["code"])}
        for candidate in ITEMS.values()
        if candidate["kind"] == "probe" and candidate["item_id"] != item_id
    ]


def answer(payload):
    session = learner_store.get_session(payload.session_id)
    item = ITEMS.get(payload.item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="unknown item")
    attempts_before = learner_store.attempt_count(payload.session_id)
    if item["kind"] == "retest":
        pending = [learner_store.misconception(payload.session_id, h) for h in HYPS if h not in {"correct", "unknown"}]
        pending = [record for record in pending if record and record["state"] in {"intervened", "suspected_resolved"}]
        if pending and max(int(record["evidence"].get("other_topic_attempts", 0)) for record in pending) < 2:
            raise HTTPException(status_code=409, detail="delayed retest requires two intervening items on other topics")
    sig = signature(item["code"])
    diagnosis = diagnose_answer(
        {
            "answer": payload.answer.strip(),
            "confidence": payload.confidence,
            "code": item["code"],
            "signature": sig,
        },
        prior=session["posterior"],
        next_items=_probe_candidates(payload.item_id),
    )
    posterior = diagnosis["posterior"]
    top = diagnosis["top"]

    for hypothesis, probability in posterior.items():
        if hypothesis in {"correct", "unknown"}:
            continue
        existing = learner_store.misconception(payload.session_id, hypothesis)
        current = existing or {
            "state": "active", "evidence": {"discriminator_passes": 0, "surface_forms": [], "delayed_retest": False}
        }
        if existing is None and probability < 0.6:
            continue
        evidence = {
            **current["evidence"],
            "passed": payload.answer.strip() == sig["real"],
            "informative": sig.get(hypothesis, sig["real"]) != sig["real"],
            "surface_form": f"{item['kind']}:{item['code']}",
        }
        family = "range" if hypothesis == "range_1_to_n" else "indexing"
        if item["family"] != family:
            evidence["other_topic_attempts"] = int(evidence.get("other_topic_attempts", 0)) + 1
        state, evidence = next_state(current["state"], evidence, item["kind"], probability)
        learner_store.save_misconception(payload.session_id, hypothesis, state, probability, evidence)

    learner_store.set_session(payload.session_id, posterior)
    learner_store.save_attempt(payload.session_id, payload.item_id, payload.answer, payload.confidence, posterior)

    # Resolution evidence follows the diagnosed misconception, even when the
    # correct interpreter becomes the posterior's top hypothesis.
    tracked = [learner_store.misconception(payload.session_id, h) for h in HYPS if h not in {"correct", "unknown"}]
    tracked = [record for record in tracked if record is not None]
    resolution_record = max(tracked, key=lambda record: posterior.get(record["id"], 0.0), default=None)
    if resolution_record and resolution_record["state"] in {"intervened", "suspected_resolved"}:
        misconception = resolution_record["id"]
        evidence = resolution_record["evidence"]
        if evidence.get("discriminator_passes", 0) < 3:
            candidates = [candidate for candidate in ITEMS.values() if candidate["kind"] == "discriminator"]
            next_item = next((candidate for candidate in candidates if f"discriminator:{candidate['code']}" not in evidence.get("surface_forms", [])), None)
        elif not any(form.startswith("transfer:") for form in evidence.get("surface_forms", [])):
            candidates = [candidate for candidate in ITEMS.values() if candidate["kind"] == "transfer"]
            next_item = next((candidate for candidate in candidates if f"transfer:{candidate['code']}" not in evidence.get("surface_forms", [])), None)
        else:
            other_topics = int(evidence.get("other_topic_attempts", 0))
            if other_topics < 2:
                next_item = ITEMS["i9"] if other_topics == 0 else ITEMS["i10"]
            else:
                next_item = ITEMS["i8"] if not evidence.get("delayed_retest") else None
        action = "reassess"
        if next_item is None:
            action = "done"
    else:
        action = diagnosis["next_action"]
        next_item = diagnosis["next_item"]
        misconception = diagnosis["next_misconception"]

    return {
        "posterior": posterior,
        "top": top,
        "bank_ids": diagnosis["bank_ids"],
        "real_output": diagnosis["real_output"],
        "believed_output": diagnosis["believed_output"],
        "believed_source": diagnosis["believed_source"],
        "next_action": action,
        "next_item": next_item,
        "next_misconception": misconception,
        "next": {"action": action, "item": next_item, "misconception": misconception},
    }


def intervention(misconception_id: str, item_id: str):
    item = ITEMS.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="unknown item")
    if misconception_id not in LIVE_HYPOTHESES:
        raise HTTPException(status_code=404, detail="unknown misconception")
    contrast_code, takeaway = CONTRASTS.get(misconception_id, CONTRASTS["index_1_based"])
    contrast = signature(contrast_code)
    bank_ids = [bank_id for bank_id in BANK_MAP[misconception_id] if str(bank_id) in BANK_DESCRIPTIONS]
    title = f"Understanding {misconception_id.replace('_', ' ')}"
    if misconception_id == "index_1_based":
        title = "Python indexes start at zero"
    return {
        "title": title,
        "bank_description": BANK_DESCRIPTIONS.get(str(bank_ids[0]), f"Misconception family {misconception_id}."),
        "contrast_code": contrast_code,
        "real_output": contrast["real"],
        "believed_output": contrast.get(misconception_id, contrast["real"]),
        "steps": ["Run the real and believed versions and compare their outputs.", "Identify the Python rule that makes the outputs differ.", "Apply that rule to a new example before moving on."],
        "takeaway": takeaway,
    }


def record_intervention(session_id: str, misconception_id: str) -> None:
    session = learner_store.get_session(session_id)
    current = learner_store.misconception(session_id, misconception_id) or {
        "evidence": {"discriminator_passes": 0, "surface_forms": [], "delayed_retest": False}
    }
    evidence = {**current["evidence"], "intervention_attempt": learner_store.attempt_count(session_id)}
    probability = float(session["posterior"].get(misconception_id, 0.0))
    learner_store.save_misconception(session_id, misconception_id, "intervened", probability, evidence)
