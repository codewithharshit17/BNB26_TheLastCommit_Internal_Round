import json

from fastapi import HTTPException

from ..db import connect


def save_session(session_id: str, posterior: dict[str, float], item_id: str) -> None:
    with connect() as db:
        db.execute(
            "insert into sessions (session_id, posterior, current_item) values (?, ?, ?)",
            (session_id, json.dumps(posterior), item_id),
        )


def get_session(session_id: str) -> dict:
    with connect() as db:
        row = db.execute("select * from sessions where session_id = ?", (session_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="unknown session")
    return {**dict(row), "posterior": json.loads(row["posterior"])}


def set_session(session_id: str, posterior: dict[str, float], item_id: str | None = None) -> None:
    with connect() as db:
        cursor = db.execute(
            "update sessions set posterior = ?, current_item = coalesce(?, current_item) where session_id = ?",
            (json.dumps(posterior), item_id, session_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="unknown session")


def save_attempt(session_id: str, item_id: str, answer: str, confidence: int, posterior: dict[str, float]) -> None:
    with connect() as db:
        db.execute(
            "insert into attempts (session, item, answer, conf, posterior) values (?, ?, ?, ?, ?)",
            (session_id, item_id, answer, confidence, json.dumps(posterior)),
        )


def attempt_count(session_id: str) -> int:
    with connect() as db:
        row = db.execute("select count(*) as count from attempts where session = ?", (session_id,)).fetchone()
    return int(row["count"])


def misconception(session_id: str, misconception_id: str) -> dict | None:
    with connect() as db:
        row = db.execute(
            "select * from misconception_state where session = ? and misconception = ?",
            (session_id, misconception_id),
        ).fetchone()
    if row is None:
        return None
    return {
        "id": row["misconception"],
        "state": row["state"],
        "posterior_history": json.loads(row["posterior_history"]),
        "evidence": json.loads(row["evidence"]),
    }


def save_misconception(session_id: str, misconception_id: str, state: str,
                       posterior: float, evidence: dict) -> None:
    previous = misconception(session_id, misconception_id)
    history = previous["posterior_history"] if previous else []
    history.append(float(posterior))
    with connect() as db:
        db.execute(
            "insert into misconception_state values (?, ?, ?, ?, ?) "
            "on conflict(session, misconception) do update set state=excluded.state, "
            "posterior_history=excluded.posterior_history, evidence=excluded.evidence",
            (session_id, misconception_id, state, json.dumps(history), json.dumps(evidence)),
        )


def learner(session_id: str) -> dict:
    get_session(session_id)  # Validate the session even when it has no diagnosis yet.
    with connect() as db:
        rows = db.execute(
            "select misconception, state, posterior_history, evidence "
            "from misconception_state where session = ? order by misconception",
            (session_id,),
        ).fetchall()
    return {"misconceptions": [
        {"id": row["misconception"], "state": row["state"],
         "posterior_history": json.loads(row["posterior_history"]),
         "evidence": json.loads(row["evidence"])}
        for row in rows
    ]}
