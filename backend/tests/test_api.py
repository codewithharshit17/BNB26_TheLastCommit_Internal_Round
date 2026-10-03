from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def _session():
    response = client.post("/session/start")
    assert response.status_code == 200
    return response.json()


def _answer(session, answer, item_id="i1"):
    return client.post("/answer", json={
        "session_id": session["session_id"],
        "item_id": item_id,
        "answer": answer,
        "confidence": 5,
    })


def test_health():
    assert client.get("/health").json() == {"ok": True}


def test_correct_answer_uses_ml_adapter_and_preserves_contract():
    response = _answer(_session(), "20")
    body = response.json()
    assert response.status_code == 200
    assert body["top"] == "correct"
    assert set(("posterior", "top", "believed_output", "next_action")).issubset(body | {"next_action": body["next"]["action"]})
    assert body["next"]["action"] == "probe"
    assert body["next"]["item"]["item_id"] == "i2"


def test_known_misconception_is_diagnosed():
    body = _answer(_session(), "10").json()
    assert body["top"] == "index_1_based"
    assert body["bank_ids"] == [15, 66]
    assert body["next"]["action"] == "intervene"


def test_runtime_error_answer_is_safe():
    response = _answer(_session(), "NameError")
    assert response.status_code == 200
    assert response.json()["real_output"] == "20"


def test_held_out_and_missing_bank_ids_do_not_leak():
    body = _answer(_session(), "30").json()
    assert "index_from_m1" not in body["posterior"]
    assert body["top"] != "index_from_m1"
    assert 34 not in body["bank_ids"]


def test_ambiguous_response_contains_probe_item():
    body = _answer(_session(), "20").json()
    assert body["next"]["action"] == "probe"
    assert body["next"]["item"]["kind"] == "probe"
