import uuid

from pydantic import BaseModel


class BusinessMetricOut(BaseModel):
    id: uuid.UUID
    asset_id: uuid.UUID
    label: str
    value: float
    period: str
    unit: str

    model_config = {"from_attributes": True}
