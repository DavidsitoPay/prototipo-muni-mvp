from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole

# Password en texto plano de cada usuario demo: ver CREDENTIALS.md (gitignored).
# Aca solo se versiona el hash bcrypt, nunca el password real, porque este repo
# es publico. Rotados 2026-09-23 porque el password anterior habia quedado
# expuesto en texto plano en el historial de git de README.md.
DEMO_USERS = [
    {
        "username": "admin.ti",
        "password_hash": "$2b$12$rhxO6oGq2qX2/76DcW5LoOAcdpsCvBTYKeGlf1hN/5o2i75eEJdlW",
        "role": UserRole.admin_ti,
        "display_name": "Ana TI (Administradora TI)",
    },
    {
        "username": "analista.riesgo",
        "password_hash": "$2b$12$00PIvWc5CIanNW0.STotdeH80X6Z4xh3ENV/Vf2rcP/6.Za0ChrN6",
        "role": UserRole.analista_riesgo,
        "display_name": "Carlos Ríos (Analista de Riesgo)",
    },
    {
        "username": "directivo",
        "password_hash": "$2b$12$KX/l0B43suCRIin6kQy/ueWPAm/FSt9lPwMT.vpDeOcpuGYujKcZm",
        "role": UserRole.directivo,
        "display_name": "Lic. Morales (Directivo)",
    },
]


async def seed_users(db: AsyncSession) -> None:
    for entry in DEMO_USERS:
        db.add(
            User(
                username=entry["username"],
                password_hash=entry["password_hash"],
                role=entry["role"],
                display_name=entry["display_name"],
            )
        )
    await db.flush()
