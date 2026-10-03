from fastapi import APIRouter, HTTPException, Query

from .. import mock, use_mock
from ..schemas import AnswerRequest, AnswerResponse, InterventionResponse, LearnerResponse
from ..services import diagnosis, learner_store

router = APIRouter()
_mock_answers = 0


@router.get("/health")
def health():
    return {"ok": True}


@router.post("/session/start")
def start():
    if use_mock():
        global _mock_answers
        _mock_answers = 0
        return mock("start.json")
    return diagnosis.start_session()


@router.post("/answer", response_model=AnswerResponse)
def answer(payload: AnswerRequest):
    if use_mock():
        global _mock_answers
        script = [
            "answer_probe.json",
            "answer_intervene.json",
            "answer_reassess.json",
            "answer_other_topic_1.json",
            "answer_other_topic_2.json",
            "answer_retest.json",
            "answer_resolved.json",
        ]
        name = script[_mock_answers] if _mock_answers < len(script) else script[-1]
        _mock_answers += 1
        return mock(name)
    result = diagnosis.answer(payload)
    return result


@router.get("/learner/{session_id}", response_model=LearnerResponse)
def learner(session_id: str):
    if use_mock():
        if _mock_answers >= 7:
            return mock("learner_confirmed.json")
        return mock("learner.json") if _mock_answers >= 3 else mock("learner_empty.json")
    return learner_store.learner(session_id)


@router.get("/intervention/{misconception_id}", response_model=InterventionResponse)
def intervention(misconception_id: str, item_id: str = Query(default="i1"), session_id: str | None = None):
    if use_mock():
        return mock("intervention.json")
    result = diagnosis.intervention(misconception_id, item_id)
    if session_id:
        diagnosis.record_intervention(session_id, misconception_id)
    return result
