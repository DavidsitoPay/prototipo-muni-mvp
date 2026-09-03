import uuid

from pydantic import BaseModel

from app.models.asset import AssetCriticality
from app.models.nist_assessment import NistFunction
from app.models.vulnerability import RiskBand


class AssetsByCriticality(BaseModel):
    criticality: AssetCriticality
    count: int


class VulnerabilitiesByRiskBand(BaseModel):
    risk_band: RiskBand
    count: int


class TopRiskyAsset(BaseModel):
    asset_id: uuid.UUID
    name: str
    criticality: AssetCriticality
    risk_band: RiskBand
    risk_score: int


class DashboardSummaryOut(BaseModel):
    total_assets: int
    assets_by_criticality: list[AssetsByCriticality]
    vulnerabilities_by_risk_band: list[VulnerabilitiesByRiskBand]
    nist_global_maturity_percent: float | None
    top_risky_assets: list[TopRiskyAsset]


class HeatmapCell(BaseModel):
    probability: int
    impact: int
    count: int


class HeatmapOut(BaseModel):
    cells: list[HeatmapCell]


class NistRadarPoint(BaseModel):
    function: NistFunction
    maturity_percent: float | None


class NistRadarOut(BaseModel):
    points: list[NistRadarPoint]
