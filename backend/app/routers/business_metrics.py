import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.deps import get_current_user
from app.models.business_metric import DemoBusinessMetric
from app.schemas.business_metric import BusinessMetricOut

router = APIRouter(tags=["business-metrics"])


@router.get(
    "/api/assets/{asset_id}/business-metrics",
    response_model=list[BusinessMetricOut],
    dependencies=[Depends(get_current_user)],
)
async def list_business_metrics(asset_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> list[DemoBusinessMetric]:
    result = await db.scalars(select(DemoBusinessMetric).where(DemoBusinessMetric.asset_id == asset_id))
    return list(result.all())
