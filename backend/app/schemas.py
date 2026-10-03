from typing import Any, Literal
from pydantic import BaseModel, Field

class Item(BaseModel):
    item_id: str
    kind: Literal["diagnostic", "probe", "transfer", "discriminator", "retest"]
    family: str
    prompt: str
    code: str
    problem_ref: str | None

class AnswerRequest(BaseModel):
    session_id: str
    item_id: str
    answer: str
    confidence: int = Field(ge=1, le=5)

class NextAction(BaseModel):
    action: Literal["probe", "intervene", "reassess", "done"]
    item: Item | None = None
    misconception: str | None = None

class AnswerResponse(BaseModel):
    posterior: dict[str, float]
    top: str
    bank_ids: list[int]
    real_output: str
    believed_output: str
    believed_source: str
    next: NextAction
    next_action: Literal["probe", "intervene", "reassess", "done"] | None = None
    next_item: Item | None = None
    next_misconception: str | None = None

class LearnerResponse(BaseModel):
    misconceptions: list[dict[str, Any]]

class InterventionResponse(BaseModel):
    title: str
    bank_description: str
    contrast_code: str
    real_output: str
    believed_output: str
    steps: list[str]
    takeaway: str
