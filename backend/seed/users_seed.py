from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.services.auth_service import hash_password

DEMO_USERS = [
    {
        "username": "admin.ti",
        "password": "Demo123!",
        "role": UserRole.admin_ti,
        "display_name": "Ana TI (Administradora TI)",
    },
    {
        "username": "analista.riesgo",
        "password": "Demo123!",
        "role": UserRole.analista_riesgo,
        "display_name": "Carlos Ríos (Analista de Riesgo)",
    },
    {
        "username": "directivo",
        "password": "Demo123!",
        "role": UserRole.directivo,
        "display_name": "Lic. Morales (Directivo)",
    },
]


async def seed_users(db: AsyncSession) -> None:
    for entry in DEMO_USERS:
        db.add(
            User(
                username=entry["username"],
                password_hash=hash_password(entry["password"]),
                role=entry["role"],
                display_name=entry["display_name"],
            )
        )
    await db.flush()
