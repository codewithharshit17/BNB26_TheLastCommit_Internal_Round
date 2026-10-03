import json, os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import AnswerRequest, AnswerResponse, InterventionResponse, LearnerResponse
from .services import diagnosis, learner_store
from engine.interventions.builder import load as load_interventions

# Instruct the sandbox to use subprocess-level isolation for live student
# code so CPU-bound infinite loops are actually killed by process.kill().
# This is safe here because uvicorn is a properly guarded entry-point.
os.environ.setdefault("RELEARN_SANDBOX", "subprocess")

app = FastAPI(title="Re:Learn API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

MOCK_DIR = Path(__file__).resolve().parents[2] / "contracts" / "mocks"
def mock(name): return json.loads((MOCK_DIR / name).read_text(encoding="utf-8"))
def use_mock(): return os.getenv("MOCK", "0") == "1"

# Load intervention content once at startup (real data, execution-verified outputs)
_INTERVENTIONS: dict = load_interventions()

@app.get("/health")
def health(): return {"ok": True}

@app.post("/session/start")
def start():
    if use_mock(): return mock("start.json")
    result = diagnosis.start_session()
    learner_store.save_session(result["session_id"])
    return result

@app.post("/answer", response_model=AnswerResponse)
def answer(payload: AnswerRequest):
    if use_mock(): return mock("answer_probe.json")
    result = diagnosis.answer(payload)
    learner_store.save_attempt(
        payload.session_id, payload.item_id,
        payload.answer, payload.confidence, result["posterior"]
    )
    return result

@app.get("/learner/{session_id}", response_model=LearnerResponse)
def learner(session_id: str):
    return mock("learner.json") if use_mock() else learner_store.learner(session_id)

@app.get("/intervention/{id}", response_model=InterventionResponse)
def intervention(id: str):
    if use_mock():
        return mock("intervention.json")
    # Look up from execution-verified interventions.json
    if id not in _INTERVENTIONS:
        raise HTTPException(
            status_code=404,
            detail=f"No intervention found for misconception '{id}'. "
                   f"Available: {list(_INTERVENTIONS.keys())}"
        )
    return _INTERVENTIONS[id]
