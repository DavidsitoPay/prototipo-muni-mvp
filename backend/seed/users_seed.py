import os

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.services.auth_service import hash_password

# Los passwords de los usuarios demo NUNCA se hardcodean aca (ni en texto plano
# ni como hash): este repo es publico y SonarCloud marca como secreto incluso
# un hash bcrypt versionado (regla secrets:S8215). Se leen de variables de
# entorno al momento de sembrar; el valor real vive solo en CREDENTIALS.md
# (gitignored) y en backend/.env (gitignored, local).
_ENV_VARS = {
    "admin.ti": "SEED_ADMIN_TI_PASSWORD",
    "analista.riesgo": "SEED_ANALISTA_RIESGO_PASSWORD",
    "directivo": "SEED_DIRECTIVO_PASSWORD",
}

DEMO_USERS = [
    {
        "username": "admin.ti",
        "role": UserRole.admin_ti,
        "display_name": "Ana TI (Administradora TI)",
    },
    {
        "username": "analista.riesgo",
        "role": UserRole.analista_riesgo,
        "display_name": "Carlos Ríos (Analista de Riesgo)",
    },
    {
        "username": "directivo",
        "role": UserRole.directivo,
        "display_name": "Lic. Morales (Directivo)",
    },
]


async def seed_users(db: AsyncSession) -> None:
    for entry in DEMO_USERS:
        env_var = _ENV_VARS[entry["username"]]
        password = os.environ.get(env_var)
        if not password:
            raise RuntimeError(
                f"Falta la variable de entorno {env_var} - ver CREDENTIALS.md "
                "para el valor real antes de sembrar usuarios."
            )
        db.add(
            User(
                username=entry["username"],
                password_hash=hash_password(password),
                role=entry["role"],
                display_name=entry["display_name"],
            )
        )
    await db.flush()
