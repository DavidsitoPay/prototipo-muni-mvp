import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_db
from app.deps import get_current_user, require_role
from app.models.asset import Asset
from app.models.user import UserRole
from app.models.vulnerability import RiskBand, Vulnerability, VulnerabilityStatus
from app.routers.assets import get_asset_or_404
from app.schemas.vulnerability import VulnerabilityCreate, VulnerabilityOut, VulnerabilityUpdate
from app.services.recommendation_engine.service import generate_for_vulnerability
from app.services.risk_engine import compute_risk

router = APIRouter(tags=["vulnerabilities"])


@router.get(
    "/api/assets/{asset_id}/vulnerabilities",
    response_model=list[VulnerabilityOut],
    dependencies=[Depends(get_current_user)],
)
async def list_asset_vulnerabilities(asset_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> list[Vulnerability]:
    await get_asset_or_404(db, asset_id)
    result = await db.scalars(
        select(Vulnerability).where(Vulnerability.asset_id == asset_id).order_by(Vulnerability.created_at.desc())
    )
    return list(result.all())


@router.get("/api/vulnerabilities", response_model=list[VulnerabilityOut], dependencies=[Depends(get_current_user)])
async def list_vulnerabilities(
    db: AsyncSession = Depends(get_db),
    risk_band: RiskBand | None = None,
    status_: VulnerabilityStatus | None = None,
) -> list[Vulnerability]:
    stmt = select(Vulnerability).join(Asset, Vulnerability.asset_id == Asset.id).where(Asset.deleted_at.is_(None))
    if risk_band is not None:
        stmt = stmt.where(Vulnerability.risk_band == risk_band)
    if status_ is not None:
        stmt = stmt.where(Vulnerability.status == status_)
    stmt = stmt.order_by(Vulnerability.created_at.desc())
    result = await db.scalars(stmt)
    return list(result.all())


@router.post(
    "/api/assets/{asset_id}/vulnerabilities",
    response_model=VulnerabilityOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_vulnerability(
    asset_id: uuid.UUID,
    payload: VulnerabilityCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_role(UserRole.analista_riesgo, UserRole.admin_ti)),
) -> Vulnerability:
    asset = await get_asset_or_404(db, asset_id)

    score, band = compute_risk(payload.probability, payload.impact)
    vulnerability = Vulnerability(
        asset_id=asset_id,
        description=payload.description,
        probability=payload.probability,
        impact=payload.impact,
        risk_score=score,
        risk_band=band,
    )
    db.add(vulnerability)
    await db.flush()

    await generate_for_vulnerability(db, vulnerability, asset.type)

    await db.commit()
    await db.refresh(vulnerability)
    return vulnerability


@router.put("/api/vulnerabilities/{vulnerability_id}", response_model=VulnerabilityOut)
async def update_vulnerability(
    vulnerability_id: uuid.UUID,
    payload: VulnerabilityUpdate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_role(UserRole.analista_riesgo, UserRole.admin_ti)),
) -> Vulnerability:
    vulnerability = await db.scalar(
        select(Vulnerability).options(selectinload(Vulnerability.asset)).where(Vulnerability.id == vulnerability_id)
    )
    if vulnerability is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Vulnerabilidad no encontrada")

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(vulnerability, field, value)

    recompute = "probability" in data or "impact" in data
    if recompute:
        score, band = compute_risk(vulnerability.probability, vulnerability.impact)
        vulnerability.risk_score = score
        was_triggering_band = vulnerability.risk_band
        vulnerability.risk_band = band
        if band != was_triggering_band:
            await generate_for_vulnerability(db, vulnerability, vulnerability.asset.type)

    await db.commit()
    await db.refresh(vulnerability)
    return vulnerability


@router.delete("/api/vulnerabilities/{vulnerability_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vulnerability(
    vulnerability_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_role(UserRole.admin_ti)),
) -> None:
    vulnerability = await db.scalar(select(Vulnerability).where(Vulnerability.id == vulnerability_id))
    if vulnerability is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Vulnerabilidad no encontrada")

    await db.delete(vulnerability)
    await db.commit()
