# Backend

FastAPI exposes `POST /session/start`, `POST /answer`, `GET /learner/{session_id}`,
`GET /intervention/{misconception_id}`, and `GET /health`. It consumes the engine
signature API and ML posterior update, and stores sessions, attempts, and
misconception evidence in SQLite.

Run from the repository root:

```powershell
$env:PYTHONPATH = "."
uvicorn backend.app.main:app --reload
```

Set `MOCK=1` to serve the canned demo sequence from `contracts/mocks/`. The
sequence shows a probe, an intervention, reassessment, two items from another
topic, and a delayed retest. Set `RELEARN_DB_PATH` to choose a different SQLite
file. When requesting an intervention for an active learner, pass both
`item_id` and `session_id` query parameters so its state is persisted.
