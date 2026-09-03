import asyncio
from collections import Counter

from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_db
from app.deps import get_current_user
from app.models.asset import Asset, AssetCriticality, AssetType
from app.models.nist_assessment import NistAssessment, NistFunction
from app.models.vulnerability import RiskBand, Vulnerability
from app.services.nist_engine import maturity_percent
from app.services.pdf_service import render_pdf
from app.services.risk_engine import active_vulnerabilities, asset_risk_band, worst_active_vulnerability

router = APIRouter(prefix="/api/reports", tags=["reports"], dependencies=[Depends(get_current_user)])


def _filters_description(type: AssetType | None, criticality: AssetCriticality | None, department: str | None, q: str | None) -> str | None:
    parts = []
    if type is not None:
        parts.append(f"tipo={type.value}")
    if criticality is not None:
        parts.append(f"criticidad={criticality.value}")
    if department is not None:
        parts.append(f"dependencia={department}")
    if q:
        parts.append(f"búsqueda=\"{q}\"")
    return ", ".join(parts) if parts else None


async def _filtered_assets(
    db: AsyncSession,
    type: AssetType | None,
    criticality: AssetCriticality | None,
    department: str | None,
    q: str | None,
    with_recommendations: bool = False,
) -> list[Asset]:
    vuln_loader = selectinload(Asset.vulnerabilities)
    if with_recommendations:
        vuln_loader = vuln_loader.selectinload(Vulnerability.recommendations)

    stmt = select(Asset).options(vuln_loader).where(Asset.deleted_at.is_(None))
    if type is not None:
        stmt = stmt.where(Asset.type == type)
    if criticality is not None:
        stmt = stmt.where(Asset.criticality == criticality)
    if department is not None:
        stmt = stmt.where(Asset.department == department)
    if q:
        stmt = stmt.where(Asset.name.ilike(f"%{q}%"))
    stmt = stmt.order_by(Asset.criticality.desc(), Asset.name)
    result = await db.scalars(stmt)
    return list(result.unique().all())


def _pdf_response(pdf_bytes: bytes, filename: str) -> Response:
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/executive")
async def executive_report(
    db: AsyncSession = Depends(get_db),
    type: AssetType | None = None,
    criticality: AssetCriticality | None = None,
    department: str | None = None,
    q: str | None = None,
) -> Response:
    assets = await _filtered_assets(db, type, criticality, department, q)

    active_vulns = [v for a in assets for v in active_vulnerabilities(a.vulnerabilities)]
    band_counts = Counter(v.risk_band for v in active_vulns)
    vulnerabilities_by_risk_band = [{"risk_band": b.value, "count": band_counts.get(b, 0)} for b in RiskBand]
    critical_or_high = band_counts.get(RiskBand.alto, 0) + band_counts.get(RiskBand.critico, 0)

    top_risky = []
    for asset in assets:
        worst = worst_active_vulnerability(asset.vulnerabilities)
        if worst is None:
            continue
        top_risky.append(
            {
                "name": asset.name,
                "criticality": asset.criticality.value,
                "risk_band": worst.risk_band.value,
                "risk_score": worst.risk_score,
            }
        )
    top_risky.sort(key=lambda a: a["risk_score"], reverse=True)

    nist_rows = (await db.scalars(select(NistAssessment))).all()
    nist_global = maturity_percent([r.score for r in nist_rows if r.score is not None])
    nist_functions = [
        {
            "function": f.value,
            "maturity_percent": maturity_percent([r.score for r in nist_rows if r.function == f and r.score is not None]),
        }
        for f in NistFunction
    ]

    pdf_bytes = await asyncio.to_thread(
        render_pdf,
        "report_executive.html",
        {
            "filters_description": _filters_description(type, criticality, department, q),
            "total_assets": len(assets),
            "critical_or_high_vulnerabilities": critical_or_high,
            "vulnerabilities_by_risk_band": vulnerabilities_by_risk_band,
            "top_risky_assets": top_risky[:5],
            "nist_global_maturity_percent": nist_global,
            "nist_functions": nist_functions,
        },
    )
    return _pdf_response(pdf_bytes, "sgcm-reporte-ejecutivo.pdf")


@router.get("/technical")
async def technical_report(
    db: AsyncSession = Depends(get_db),
    type: AssetType | None = None,
    criticality: AssetCriticality | None = None,
    department: str | None = None,
    q: str | None = None,
) -> Response:
    assets = await _filtered_assets(db, type, criticality, department, q, with_recommendations=True)

    assets_ctx = []
    for asset in assets:
        band = asset_risk_band(asset.vulnerabilities)
        assets_ctx.append(
            {
                "name": asset.name,
                "type": asset.type.value,
                "department": asset.department,
                "criticality": asset.criticality.value,
                "status": asset.status.value,
                "risk_band": band.value if band else None,
                "vulnerabilities": [
                    {
                        "description": v.description,
                        "probability": v.probability,
                        "impact": v.impact,
                        "risk_score": v.risk_score,
                        "risk_band": v.risk_band.value,
                        "status": v.status.value,
                        "recommendations": [{"text": r.text} for r in v.recommendations],
                    }
                    for v in asset.vulnerabilities
                ],
            }
        )

    pdf_bytes = await asyncio.to_thread(
        render_pdf,
        "report_technical.html",
        {
            "filters_description": _filters_description(type, criticality, department, q),
            "assets": assets_ctx,
        },
    )
    return _pdf_response(pdf_bytes, "sgcm-reporte-tecnico.pdf")
