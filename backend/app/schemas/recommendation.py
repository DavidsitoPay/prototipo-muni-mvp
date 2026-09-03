import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.nist_assessment import NistFunction
from app.models.recommendation import RecommendationSource


class RecommendationOut(BaseModel):
    id: uuid.UUID
    vulnerability_id: uuid.UUID | None
    nist_function: NistFunction | None
    source: RecommendationSource
    text: str
    created_at: datetime

    model_config = {"from_attributes": True}


class GenerateRecommendationIn(BaseModel):
    vulnerability_id: uuid.UUID | None = None
    nist_function: NistFunction | None = None
