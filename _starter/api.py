import sqlite3, uuid, json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from engine import signature
from posterior import update, info_gain, entropy

app = FastAPI(title="Re:Learn API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

db = sqlite3.connect("relearn.db", check_same_thread=False)
db.execute("create table if not exists attempts(session text, item text, answer text, conf int, posterior text)")

# ITEMS is produced by Sukhada's generator: {item_id: {"code":..., "family":..., "kind": "diagnostic|probe|transfer|discriminator|retest"}}
ITEMS = {"i1": {"code": "a = [10, 20, 30]\nprint(a[1])", "kind": "diagnostic"},
         "i2": {"code": "a = [10, 20, 30]\nprint(a[2])", "kind": "probe"}}
HYPS = ["correct", "index_1_based", "index_from_m1", "range_1_to_n", "noop_method", "assign_copies", "add_before_div", "unknown"]
SESSIONS = {}   # session_id -> posterior dict

class Answer(BaseModel):
    session_id: str
    item_id: str
    answer: str
    confidence: int  # 1-5

@app.post("/session/start")
def start():
    sid = str(uuid.uuid4()); SESSIONS[sid] = {h: 1/len(HYPS) for h in HYPS}
    return {"session_id": sid, "item": {"item_id": "i1", "code": ITEMS["i1"]["code"]}}

@app.post("/answer")
def answer(a: Answer):
    if a.session_id not in SESSIONS or a.item_id not in ITEMS: raise HTTPException(404, "unknown session or item")
    sig = signature(ITEMS[a.item_id]["code"])
    post = update(SESSIONS[a.session_id], sig, a.answer.strip(), a.confidence)
    SESSIONS[a.session_id] = post
    db.execute("insert into attempts values (?,?,?,?,?)", (a.session_id, a.item_id, a.answer, a.confidence, json.dumps(post))); db.commit()
    top = max(post, key=post.get)
    # next action: probe if ambiguous, intervene if confident, else done
    if post[top] < 0.8:
        best = max((i for i in ITEMS if i != a.item_id), key=lambda i: info_gain(post, signature(ITEMS[i]["code"])))
        nxt = {"action": "probe", "item": {"item_id": best, "code": ITEMS[best]["code"]}}
    else:
        nxt = {"action": "intervene" if top != "correct" else "done", "misconception": top}
    return {"posterior": post, "top": top, "real_output": sig["real"], "believed_output": sig.get(top), "next": nxt}

@app.get("/health")
def health(): return {"ok": True}
