import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.asset import AssetCriticality, AssetLocation, AssetStatus, AssetType
from app.models.vulnerability import RiskBand
from app.schemas.business_metric import BusinessMetricOut
from app.schemas.vulnerability import VulnerabilityOut


class AssetBase(BaseModel):
    name: str
    type: AssetType
    department: str
    criticality: AssetCriticality
    status: AssetStatus = AssetStatus.activo
    owner: str
    location: AssetLocation


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    name: str | None = None
    type: AssetType | None = None
    department: str | None = None
    criticality: AssetCriticality | None = None
    status: AssetStatus | None = None
    owner: str | None = None
    location: AssetLocation | None = None


class AssetOut(AssetBase):
    id: uuid.UUID
    created_at: datetime
    risk_band: RiskBand | None = None

    model_config = {"from_attributes": True}


class AssetDetailOut(AssetOut):
    vulnerabilities: list[VulnerabilityOut] = []
    business_metrics: list[BusinessMetricOut] = []
