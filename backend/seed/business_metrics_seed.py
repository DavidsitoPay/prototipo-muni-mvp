from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset
from app.models.business_metric import DemoBusinessMetric

PERIOD = "2026-08"

METRICS_DATA = [
    dict(label="Total de multas", value=450000, period=PERIOD, unit="Q"),
    dict(label="Monto pagado", value=310000, period=PERIOD, unit="Q"),
    dict(label="Monto pendiente de pago", value=140000, period=PERIOD, unit="Q"),
    dict(label="Cantidad de multas emitidas", value=1240, period=PERIOD, unit="unidades"),
]


async def seed_business_metrics(db: AsyncSession, assets_by_name: dict[str, Asset]) -> None:
    asset = assets_by_name["Sistema de Remisiones/Multas"]
    for data in METRICS_DATA:
        db.add(DemoBusinessMetric(asset_id=asset.id, **data))
    await db.flush()
