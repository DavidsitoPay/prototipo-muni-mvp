"""Pruebas unitarias del enriquecimiento via LLM (Gemini) con mock del
cliente HTTP. Justificacion del doble de prueba: llamar a la API real de
Gemini en cada corrida de pipeline consumiria cuota gratuita, dependeria
de red y de una GEMINI_API_KEY real, y volveria la prueba no determinista
(el texto generado por el LLM varia). Se aisla httpx.AsyncClient.post para
verificar unicamente la logica propia de llm_enricher.enrich: que arme el
prompt, parsee la respuesta esperada y degrade a None ante cualquier fallo,
tal como exige el comentario del modulo (el motor de reglas siempre queda
como fuente principal)."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.config import settings
from app.services.recommendation_engine.llm_enricher import enrich

pytestmark = pytest.mark.asyncio


def _fake_gemini_response(text: str) -> MagicMock:
    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.json.return_value = {"candidates": [{"content": {"parts": [{"text": text}]}}]}
    return response


async def test_enrich_returns_none_when_llm_disabled_and_makes_no_network_call(monkeypatch):
    monkeypatch.setattr(settings, "llm_enabled", False)
    with patch("app.services.recommendation_engine.llm_enricher.httpx.AsyncClient") as mock_client_cls:
        result = await enrich("texto base", {"asset_type": "servidor"})
    assert result is None
    mock_client_cls.assert_not_called()


async def test_enrich_returns_none_when_api_key_missing(monkeypatch):
    monkeypatch.setattr(settings, "llm_enabled", True)
    monkeypatch.setattr(settings, "gemini_api_key", "")
    with patch("app.services.recommendation_engine.llm_enricher.httpx.AsyncClient") as mock_client_cls:
        result = await enrich("texto base", {"asset_type": "servidor"})
    assert result is None
    mock_client_cls.assert_not_called()


async def test_enrich_returns_parsed_text_on_success(monkeypatch):
    monkeypatch.setattr(settings, "llm_enabled", True)
    monkeypatch.setattr(settings, "gemini_api_key", "fake-key")

    mock_http_client = AsyncMock()
    mock_http_client.post.return_value = _fake_gemini_response("  Texto reescrito por el LLM.  ")
    mock_http_client.__aenter__.return_value = mock_http_client
    mock_http_client.__aexit__.return_value = False

    with patch(
        "app.services.recommendation_engine.llm_enricher.httpx.AsyncClient",
        return_value=mock_http_client,
    ):
        result = await enrich("texto base", {"asset_type": "servidor"})

    assert result == "Texto reescrito por el LLM."
    mock_http_client.post.assert_awaited_once()


async def test_enrich_falls_back_to_none_on_http_error(monkeypatch):
    monkeypatch.setattr(settings, "llm_enabled", True)
    monkeypatch.setattr(settings, "gemini_api_key", "fake-key")

    mock_http_client = AsyncMock()
    mock_http_client.post.side_effect = httpx.ConnectTimeout("timeout simulado")
    mock_http_client.__aenter__.return_value = mock_http_client
    mock_http_client.__aexit__.return_value = False

    with patch(
        "app.services.recommendation_engine.llm_enricher.httpx.AsyncClient",
        return_value=mock_http_client,
    ):
        result = await enrich("texto base", {"asset_type": "servidor"})

    assert result is None


async def test_enrich_falls_back_to_none_on_malformed_response(monkeypatch):
    monkeypatch.setattr(settings, "llm_enabled", True)
    monkeypatch.setattr(settings, "gemini_api_key", "fake-key")

    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.json.return_value = {"candidates": []}  # sin parts[0] -> IndexError

    mock_http_client = AsyncMock()
    mock_http_client.post.return_value = response
    mock_http_client.__aenter__.return_value = mock_http_client
    mock_http_client.__aexit__.return_value = False

    with patch(
        "app.services.recommendation_engine.llm_enricher.httpx.AsyncClient",
        return_value=mock_http_client,
    ):
        result = await enrich("texto base", {"asset_type": "servidor"})

    assert result is None


async def test_enrich_returns_none_on_blank_text_response(monkeypatch):
    monkeypatch.setattr(settings, "llm_enabled", True)
    monkeypatch.setattr(settings, "gemini_api_key", "fake-key")

    mock_http_client = AsyncMock()
    mock_http_client.post.return_value = _fake_gemini_response("   ")
    mock_http_client.__aenter__.return_value = mock_http_client
    mock_http_client.__aexit__.return_value = False

    with patch(
        "app.services.recommendation_engine.llm_enricher.httpx.AsyncClient",
        return_value=mock_http_client,
    ):
        result = await enrich("texto base", {"asset_type": "servidor"})

    assert result is None
