from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_db
from app.deps import get_current_user
from app.models.asset import Asset, AssetCriticality
from app.models.nist_assessment import NistAssessment, NistFunction
from app.models.vulnerability import RiskBand
from app.schemas.dashboard import (
    AssetsByCriticality,
    DashboardSummaryOut,
    HeatmapCell,
    HeatmapOut,
    NistRadarOut,
    NistRadarPoint,
    TopRiskyAsset,
    VulnerabilitiesByRiskBand,
)
from app.services.nist_engine import maturity_percent
from app.services.risk_engine import active_vulnerabilities, worst_active_vulnerability

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"], dependencies=[Depends(get_current_user)])


async def _active_assets_with_vulnerabilities(db: AsyncSession) -> list[Asset]:
    """Activos no eliminados con sus vulnerabilidades cargadas. Se reutiliza en
    summary/heatmap para no repetir el query y para que ambos excluyan
    consistentemente activos dados de baja (soft delete)."""
    result = await db.scalars(
        select(Asset).options(selectinload(Asset.vulnerabilities)).where(Asset.deleted_at.is_(None))
    )
    return list(result.unique().all())


@router.get("/summary", response_model=DashboardSummaryOut)
async def summary(db: AsyncSession = Depends(get_db)) -> DashboardSummaryOut:
    assets = await _active_assets_with_vulnerabilities(db)

    crit_counts = Counter(a.criticality for a in assets)
    assets_by_criticality = [
        AssetsByCriticality(criticality=c, count=crit_counts.get(c, 0)) for c in AssetCriticality
    ]

    active_vulns = [v for a in assets for v in active_vulnerabilities(a.vulnerabilities)]
    band_counts = Counter(v.risk_band for v in active_vulns)
    vulnerabilities_by_risk_band = [
        VulnerabilitiesByRiskBand(risk_band=b, count=band_counts.get(b, 0)) for b in RiskBand
    ]

    nist_rows = (await db.scalars(select(NistAssessment))).all()
    nist_global = maturity_percent([r.score for r in nist_rows if r.score is not None])

    top_risky_assets: list[TopRiskyAsset] = []
    for asset in assets:
        worst = worst_active_vulnerability(asset.vulnerabilities)
        if worst is None:
            continue
        top_risky_assets.append(
            TopRiskyAsset(
                asset_id=asset.id,
                name=asset.name,
                criticality=asset.criticality,
                risk_band=worst.risk_band,
                risk_score=worst.risk_score,
            )
        )
    top_risky_assets.sort(key=lambda a: a.risk_score, reverse=True)

    return DashboardSummaryOut(
        total_assets=len(assets),
        assets_by_criticality=assets_by_criticality,
        vulnerabilities_by_risk_band=vulnerabilities_by_risk_band,
        nist_global_maturity_percent=nist_global,
        top_risky_assets=top_risky_assets[:5],
    )


@router.get("/heatmap", response_model=HeatmapOut)
async def heatmap(db: AsyncSession = Depends(get_db)) -> HeatmapOut:
    assets = await _active_assets_with_vulnerabilities(db)
    active_vulns = [v for a in assets for v in active_vulnerabilities(a.vulnerabilities)]
    counts = Counter((v.probability, v.impact) for v in active_vulns)
    cells = [
        HeatmapCell(probability=p, impact=i, count=counts.get((p, i), 0))
        for p in range(1, 6)
        for i in range(1, 6)
    ]
    return HeatmapOut(cells=cells)


@router.get("/nist-radar", response_model=NistRadarOut)
async def nist_radar(db: AsyncSession = Depends(get_db)) -> NistRadarOut:
    rows = (await db.scalars(select(NistAssessment))).all()
    points = [
        NistRadarPoint(
            function=function,
            maturity_percent=maturity_percent([r.score for r in rows if r.function == function and r.score is not None]),
        )
        for function in NistFunction
    ]
    return NistRadarOut(points=points)
