"""Pruebas unitarias puras de autenticacion (modulo critico #2 del E2,
seccion 2.6). Hash/verificacion de contrasenas y emision/decodificacion
de JWT, sin tocar la base de datos ni el stack HTTP."""

import uuid

from app.services.auth_service import create_access_token, decode_access_token, hash_password, verify_password


def test_hash_password_produces_bcrypt_hash():
    hashed = hash_password("Demo123!")
    assert hashed.startswith("$2b$")
    assert hashed != "Demo123!"


def test_verify_password_accepts_correct_password():
    hashed = hash_password("Demo123!")
    assert verify_password("Demo123!", hashed) is True


def test_verify_password_rejects_incorrect_password():
    hashed = hash_password("Demo123!")
    assert verify_password("otra-contrasena", hashed) is False


def test_hash_password_is_salted_and_not_deterministic():
    first_hash = hash_password("Demo123!")
    second_hash = hash_password("Demo123!")
    assert first_hash != second_hash


def test_create_and_decode_access_token_roundtrip():
    user_id = uuid.uuid4()
    token = create_access_token(user_id, "admin_ti")
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == str(user_id)
    assert payload["role"] == "admin_ti"


def test_decode_access_token_rejects_garbage_token():
    assert decode_access_token("esto-no-es-un-jwt-valido") is None


def test_decode_access_token_rejects_tampered_token():
    token = create_access_token(uuid.uuid4(), "directivo")
    tampered = token[:-4] + ("A" * 4)
    assert decode_access_token(tampered) is None
