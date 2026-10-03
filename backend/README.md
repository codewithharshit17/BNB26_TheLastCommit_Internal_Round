# Re:Learn Backend

The backend provides the HTTP API for Re:Learn, a prototype that diagnoses Python misconceptions from a learner's predicted program output. It combines the engine's executable code rewrites with the ML package's Bayesian posterior update, then stores session and misconception evidence in SQLite.

## Stack

- Python 3.11 or newer
- FastAPI and Uvicorn for the API
- Pydantic for request and response validation
- SQLite for sessions, attempts, and learner state
- The repository's `engine/` and `ml/` packages for signatures and diagnosis

## Run locally

Run commands from the repository root. On Windows PowerShell:

```powershell
python -m pip install -r requirements.txt
$env:PYTHONPATH = "."
uvicorn backend.app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`. FastAPI's interactive API page is at `http://127.0.0.1:8000/docs`.

To run the backend tests:

```powershell
$env:PYTHONPATH = "."
python -m pytest backend/tests backend/app
```

## Mock mode

Set `MOCK=1` before starting Uvicorn to use the canned JSON responses in `contracts/mocks/` instead of live diagnosis. The scripted demo progresses through a probe, intervention, reassessment, other-topic items, and a delayed retest.

```powershell
$env:PYTHONPATH = "."
$env:MOCK = "1"
uvicorn backend.app.main:app --reload
```

Mock mode is intended for the UI demo; it returns a fixed sequence rather than computing answers from the submitted text.

## API routes

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Deployment health check |
| `POST` | `/session/start` | Create a learner session and return the first item |
| `POST` | `/answer` | Score an answer, update the posterior, persist the attempt, and return the next action |
| `GET` | `/learner/{session_id}` | Read misconception states, posterior history, and resolution evidence |
| `GET` | `/intervention/{misconception_id}` | Return a computed contrast explanation for a misconception |

For `/intervention/{misconception_id}`, pass `item_id` to identify the active item. Pass `session_id` as well to persist that the intervention was delivered:

```text
GET /intervention/index_1_based?item_id=i1&session_id=<session-id>
```

Request and response fields are defined by `backend/app/schemas.py` and the JSON Schemas in `contracts/`.

## Configuration and storage

- `MOCK=1` enables canned responses. The default, `MOCK=0`, uses live diagnosis.
- `RELEARN_DB_PATH` selects the SQLite database file. By default, it is `relearn.db` at the repository root.
- CORS allows all origins for local development. Restrict origins before a production deployment.

SQLite tables store sessions and their current posterior, answer attempts, and per-misconception state/evidence. Existing scaffold databases are upgraded when the database connection is initialized.

## Resolution behavior

A correct answer only contributes resolution evidence when the item distinguishes the misconception's predicted output from real Python output. A learner first becomes `suspected_resolved`; confirmation requires at least three informative discriminator passes, multiple surface forms, and a passed delayed retest. A confirmed misconception can become `relapsed` when its posterior rises to `0.4` or higher.

The current live item set is a small prototype set. The broader item-generation pipeline is owned by `engine/` and is not yet connected to this API.
