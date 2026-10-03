import json
from pathlib import Path
from engine.signature import believed_source, signature
from ml.posterior import info_gain, update

HYPS = ["correct", "index_1_based", "index_from_m1", "range_1_to_n", "noop_method", "assign_copies", "add_before_div", "unknown"]
ITEMS = {"i1": {"item_id":"i1","kind":"diagnostic","family":"indexing","prompt":"What does this print?","code":"a = [10, 20, 30]\nprint(a[1])","problem_ref":None}, "i2": {"item_id":"i2","kind":"probe","family":"indexing","prompt":"What does this print?","code":"a = [10, 20, 30]\nprint(a[2])","problem_ref":None}}
SESSIONS = {}
BANK_MAP = json.loads((Path(__file__).resolve().parents[3] / "engine" / "bank_map.json").read_text(encoding="utf-8"))
def start_session():
    import uuid
    sid = str(uuid.uuid4()); SESSIONS[sid] = {h: 1 / len(HYPS) for h in HYPS}; return {"session_id": sid, "item": ITEMS["i1"]}
def answer(payload):
    from fastapi import HTTPException
    if payload.session_id not in SESSIONS or payload.item_id not in ITEMS: raise HTTPException(404, "unknown session or item")
    item = ITEMS[payload.item_id]; sig = signature(item["code"]); post = update(SESSIONS[payload.session_id], sig, payload.answer.strip(), payload.confidence); SESSIONS[payload.session_id] = post
    top = max(post, key=post.get)
    nxt = {"action": "intervene" if post[top] >= .8 and top != "correct" else "done", "item": None, "misconception": top}
    return {"posterior":post,"top":top,"bank_ids":BANK_MAP.get(top, []),"real_output":sig["real"],"believed_output":sig.get(top, sig["real"]),"believed_source":believed_source(item["code"], top) if top not in {"correct","unknown"} else item["code"],"next":nxt}
