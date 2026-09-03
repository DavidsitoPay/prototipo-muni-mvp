from datetime import datetime

from pydantic import BaseModel, Field

from app.models.nist_assessment import NistFunction


class NistQuestionOut(BaseModel):
    code: str
    function: NistFunction
    text: str


class NistAnswerIn(BaseModel):
    question_code: str
    score: int = Field(ge=1, le=5)


class NistAssessmentOut(BaseModel):
    question_code: str
    function: NistFunction
    question_text: str
    score: int | None
    evaluated_at: datetime | None


class NistFunctionSummary(BaseModel):
    function: NistFunction
    maturity_percent: float | None
    answered_count: int
    total_questions: int


class NistSummaryOut(BaseModel):
    global_maturity_percent: float | None
    functions: list[NistFunctionSummary]
