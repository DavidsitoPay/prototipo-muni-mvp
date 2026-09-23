import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import settings
from app.db import get_db
from app.main import app
from app.models.asset import Asset, AssetCriticality, AssetLocation, AssetType
from app.models.user import User, UserRole
from app.services.auth_service import create_access_token, hash_password


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Fresh engine + NullPool per test: pytest-asyncio gives each test
    function its own event loop, and asyncpg connections cannot be reused
    across loops. NullPool guarantees no connection outlives this test."""
    test_engine = create_async_engine(
        settings.database_url,
        poolclass=NullPool,
        connect_args={"ssl": "require", "statement_cache_size": 0},
    )
    session_factory = async_sessionmaker(bind=test_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await test_engine.dispose()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


async def _make_user(db_session: AsyncSession, role: UserRole) -> AsyncGenerator[User, None]:
    user = User(
        username=f"test.{role.value}.{uuid.uuid4().hex[:8]}",
        password_hash=hash_password("Demo123!"),
        role=role,
        display_name=f"Usuario de prueba ({role.value})",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    yield user
    await db_session.delete(user)
    await db_session.commit()


@pytest_asyncio.fixture
async def demo_user(db_session: AsyncSession) -> AsyncGenerator[User, None]:
    async for user in _make_user(db_session, UserRole.admin_ti):
        yield user


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> AsyncGenerator[User, None]:
    async for user in _make_user(db_session, UserRole.admin_ti):
        yield user


@pytest_asyncio.fixture
async def analista_user(db_session: AsyncSession) -> AsyncGenerator[User, None]:
    async for user in _make_user(db_session, UserRole.analista_riesgo):
        yield user


@pytest_asyncio.fixture
async def directivo_user(db_session: AsyncSession) -> AsyncGenerator[User, None]:
    async for user in _make_user(db_session, UserRole.directivo):
        yield user


def _headers_for(user: User) -> dict[str, str]:
    token = create_access_token(user.id, user.role.value)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers(demo_user: User) -> dict[str, str]:
    return _headers_for(demo_user)


@pytest.fixture
def admin_headers(admin_user: User) -> dict[str, str]:
    return _headers_for(admin_user)


@pytest.fixture
def analista_headers(analista_user: User) -> dict[str, str]:
    return _headers_for(analista_user)


@pytest.fixture
def directivo_headers(directivo_user: User) -> dict[str, str]:
    return _headers_for(directivo_user)


@pytest_asyncio.fixture
async def demo_asset(db_session: AsyncSession) -> AsyncGenerator[Asset, None]:
    asset = Asset(
        name=f"Activo de prueba {uuid.uuid4().hex[:6]}",
        type=AssetType.servidor,
        department="Direccion de Pruebas",
        criticality=AssetCriticality.alta,
        owner="Responsable de Pruebas",
        location=AssetLocation.on_prem,
    )
    db_session.add(asset)
    await db_session.commit()
    await db_session.refresh(asset)
    yield asset
    await db_session.delete(asset)
    await db_session.commit()
