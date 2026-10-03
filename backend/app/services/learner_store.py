import json
from ..db import connect
def save_session(session_id):
    db = connect(); db.execute("insert or ignore into sessions values (?)", (session_id,)); db.commit(); db.close()
def save_attempt(session_id, item_id, answer, confidence, posterior):
    db = connect(); db.execute("insert into attempts values (?,?,?,?,?)", (session_id, item_id, answer, confidence, json.dumps(posterior))); db.commit(); db.close()
def learner(session_id):
    return {"misconceptions": []}
