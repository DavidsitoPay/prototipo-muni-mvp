"""Entry point for seeding demo data. Run as `python -m seed.seed_data`.

Idempotent per entity: each table is only seeded if it is currently empty,
so re-running (e.g. on every `docker compose up`) never duplicates data.
"""

import asyncio

from sqlalchemy import func, select

from app.db import AsyncSessionLocal
from app.models.asset import Asset
from app.models.nist_assessment import NistAssessment
from app.models.user import User
from seed.assets_seed import seed_assets
from seed.business_metrics_seed import seed_business_metrics
from seed.nist_seed import seed_nist
from seed.users_seed import seed_users
from seed.vulnerabilities_seed import seed_vulnerabilities


async def _is_empty(db, model) -> bool:
    count = await db.scalar(select(func.count()).select_from(model))
    return count == 0


async def run() -> None:
    async with AsyncSessionLocal() as db:
        if await _is_empty(db, User):
            await seed_users(db)
            await db.commit()
            print("[seed] usuarios de demo sembrados")
        else:
            print("[seed] usuarios ya existen - omitiendo")

        if await _is_empty(db, Asset):
            assets_by_name = await seed_assets(db)
            await seed_vulnerabilities(db, assets_by_name)
            await seed_business_metrics(db, assets_by_name)
            await db.commit()
            print("[seed] activos, vulnerabilidades y metricas de multas sembrados")
        else:
            print("[seed] activos ya existen - omitiendo")

        if await _is_empty(db, NistAssessment):
            await seed_nist(db)
            await db.commit()
            print("[seed] cuestionario NIST sembrado")
        else:
            print("[seed] evaluacion NIST ya existe - omitiendo")


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
