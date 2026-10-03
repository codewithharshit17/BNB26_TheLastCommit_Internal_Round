from fastapi.testclient import TestClient
from backend.app.main import app
def test_health():
    assert TestClient(app).get("/health").json() == {"ok": True}
