"""Pruebas unitarias de autorizacion (modulo critico #2 del E2, seccion 2.6:
auth_service.py + deps.py). A diferencia de test_auth.py (que valida el
flujo completo via HTTP), estas pruebas aislan get_current_user/require_role
de la base de datos real con un mock de AsyncSession: el objetivo es
verificar la logica de autorizacion en si misma, no la integracion con
Postgres (que ya cubren las pruebas de API existentes)."""

import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.deps import get_current_user, require_role
from app.models.user import User, UserRole
from app.services.auth_service import create_access_token

def _fake_user(role: UserRole = UserRole.admin_ti, is_active: bool = True) -> User:
    return User(
        id=uuid.uuid4(),
        username="usuario.prueba",
        password_hash="irrelevante-para-esta-prueba",
        role=role,
        display_name="Usuario de prueba",
        is_active=is_active,
    )


def _bearer(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


@pytest.mark.asyncio
async def test_get_current_user_rejects_missing_credentials():
    db = AsyncMock()
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials=None, db=db)
    assert exc_info.value.status_code == 401
    db.scalar.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_current_user_rejects_garbage_token():
    db = AsyncMock()
    credentials = _bearer("no-es-un-jwt")
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials=credentials, db=db)
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_rejects_token_with_non_uuid_subject():
    # Un JWT valido pero cuyo "sub" no es un UUID (no deberia poder darse
    # con create_access_token, pero defiende contra un secreto comprometido
    # o un token forjado con otra forma de "sub").
    from jose import jwt

    from app.config import settings

    token = jwt.encode({"sub": "no-es-un-uuid", "role": "admin_ti"}, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    db = AsyncMock()
    credentials = _bearer(token)
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials=credentials, db=db)
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_rejects_user_not_found_or_inactive():
    token = create_access_token(uuid.uuid4(), "admin_ti")
    db = AsyncMock()
    db.scalar.return_value = None  # el usuario no existe o is_active=False
    credentials = _bearer(token)
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials=credentials, db=db)
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_returns_user_on_valid_token():
    fake_user = _fake_user()
    token = create_access_token(fake_user.id, fake_user.role.value)
    db = AsyncMock()
    db.scalar.return_value = fake_user
    result = await get_current_user(credentials=_bearer(token), db=db)
    assert result is fake_user
    db.scalar.assert_awaited_once()


def test_require_role_allows_user_with_matching_role():
    dependency = require_role(UserRole.admin_ti, UserRole.analista_riesgo)
    user = _fake_user(role=UserRole.analista_riesgo)
    assert dependency(user=user) is user


def test_require_role_rejects_user_without_matching_role():
    dependency = require_role(UserRole.admin_ti)
    user = _fake_user(role=UserRole.directivo)
    with pytest.raises(HTTPException) as exc_info:
        dependency(user=user)
    assert exc_info.value.status_code == 403


def test_require_role_with_no_roles_rejects_everyone():
    dependency = require_role()
    user = _fake_user(role=UserRole.admin_ti)
    with pytest.raises(HTTPException):
        dependency(user=user)
