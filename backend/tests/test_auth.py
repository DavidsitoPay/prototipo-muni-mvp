import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User

pytestmark = pytest.mark.asyncio


async def test_login_success(client: AsyncClient, demo_user: User) -> None:
    response = await client.post(
        "/api/auth/login", json={"username": demo_user.username, "password": "Demo123!"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["user"]["username"] == demo_user.username
    assert "access_token" in body


async def test_login_wrong_password(client: AsyncClient, demo_user: User) -> None:
    response = await client.post(
        "/api/auth/login", json={"username": demo_user.username, "password": "incorrecta"}
    )
    assert response.status_code == 401


async def test_login_unknown_user(client: AsyncClient) -> None:
    response = await client.post(
        "/api/auth/login", json={"username": "no.existe", "password": "Demo123!"}
    )
    assert response.status_code == 401


async def test_me_requires_token(client: AsyncClient) -> None:
    response = await client.get("/api/auth/me")
    assert response.status_code == 401


async def test_me_with_valid_token(client: AsyncClient, auth_headers: dict[str, str], demo_user: User) -> None:
    response = await client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == demo_user.username
