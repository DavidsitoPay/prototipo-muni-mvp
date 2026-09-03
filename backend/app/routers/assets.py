import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_db
from app.deps import get_current_user, require_role
from app.models.asset import Asset, AssetCriticality, AssetStatus, AssetType
from app.models.user import UserRole
from app.schemas.asset import AssetCreate, AssetDetailOut, AssetOut, AssetUpdate
from app.services.risk_engine import asset_risk_band

router = APIRouter(prefix="/api/assets", tags=["assets"])


async def get_asset_or_404(db: AsyncSession, asset_id: uuid.UUID) -> Asset:
    asset = await db.scalar(select(Asset).where(Asset.id == asset_id, Asset.deleted_at.is_(None)))
    if asset is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Activo no encontrado")
    return asset


def _asset_to_out(asset: Asset) -> AssetOut:
    data = AssetOut.model_validate(asset, from_attributes=True).model_dump()
    data["risk_band"] = asset_risk_band(asset.vulnerabilities)
    return AssetOut.model_validate(data)


@router.get("", response_model=list[AssetOut], dependencies=[Depends(get_current_user)])
async def list_assets(
    db: AsyncSession = Depends(get_db),
    type: AssetType | None = None,
    criticality: AssetCriticality | None = None,
    department: str | None = None,
    status_: AssetStatus | None = None,
    q: str | None = None,
) -> list[AssetOut]:
    stmt = select(Asset).options(selectinload(Asset.vulnerabilities)).where(Asset.deleted_at.is_(None))
    if type is not None:
        stmt = stmt.where(Asset.type == type)
    if criticality is not None:
        stmt = stmt.where(Asset.criticality == criticality)
    if department is not None:
        stmt = stmt.where(Asset.department == department)
    if status_ is not None:
        stmt = stmt.where(Asset.status == status_)
    if q:
        stmt = stmt.where(Asset.name.ilike(f"%{q}%"))
    stmt = stmt.order_by(Asset.created_at.desc())

    result = await db.scalars(stmt)
    return [_asset_to_out(asset) for asset in result.unique().all()]


@router.get("/{asset_id}", response_model=AssetDetailOut, dependencies=[Depends(get_current_user)])
async def get_asset(asset_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> AssetDetailOut:
    stmt = (
        select(Asset)
        .options(selectinload(Asset.vulnerabilities), selectinload(Asset.business_metrics))
        .where(Asset.id == asset_id, Asset.deleted_at.is_(None))
    )
    asset = await db.scalar(stmt)
    if asset is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Activo no encontrado")

    base = _asset_to_out(asset).model_dump()
    base["vulnerabilities"] = list(asset.vulnerabilities)
    base["business_metrics"] = list(asset.business_metrics)
    return AssetDetailOut.model_validate(base)


@router.post("", response_model=AssetOut, status_code=status.HTTP_201_CREATED)
async def create_asset(
    payload: AssetCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_role(UserRole.admin_ti)),
) -> AssetOut:
    asset = Asset(**payload.model_dump())
    db.add(asset)
    await db.commit()
    await db.refresh(asset, attribute_names=["vulnerabilities"])
    return _asset_to_out(asset)


@router.put("/{asset_id}", response_model=AssetOut)
async def update_asset(
    asset_id: uuid.UUID,
    payload: AssetUpdate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_role(UserRole.admin_ti)),
) -> AssetOut:
    asset = await db.scalar(
        select(Asset).options(selectinload(Asset.vulnerabilities)).where(Asset.id == asset_id, Asset.deleted_at.is_(None))
    )
    if asset is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Activo no encontrado")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(asset, field, value)

    await db.commit()
    await db.refresh(asset, attribute_names=["vulnerabilities"])
    return _asset_to_out(asset)


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    asset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_role(UserRole.admin_ti)),
) -> None:
    asset = await get_asset_or_404(db, asset_id)
    asset.deleted_at = datetime.now(timezone.utc)
    await db.commit()
