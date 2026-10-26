"""Pruebas unitarias puras del motor de recomendaciones (modulo critico #5
del E2, seccion 2.6). Verifica el criterio de aceptacion de RF-16 (toda
vulnerabilidad alta/critica tiene recomendacion, incluso con un tipo de
activo sin entrada especifica en el catalogo) y los umbrales 2.5/3.5 de
RF-17 para las funciones NIST."""

import pytest

from app.models.asset import AssetType
from app.models.nist_assessment import NistFunction
from app.models.vulnerability import RiskBand
from app.services.recommendation_engine.catalog import GENERIC_RISK_FALLBACK
from app.services.recommendation_engine.rules import (
    nist_score_band,
    recommend_for_nist_function,
    recommend_for_vulnerability,
)


def test_recommend_for_vulnerability_uses_specific_catalog_entry():
    text = recommend_for_vulnerability(AssetType.servidor, RiskBand.critico)
    assert "servidor" in text.lower() or "aislar" in text.lower()


def test_recommend_for_vulnerability_falls_back_to_wildcard_when_no_specific_entry():
    # "red" no tiene entrada para banda "medio" en el catalogo especifico,
    # pero *tampoco* la tiene el wildcard para "medio" -> debe caer al
    # fallback generico, nunca a un string vacio o None.
    text = recommend_for_vulnerability(AssetType.red, RiskBand.medio)
    assert text == GENERIC_RISK_FALLBACK[0]


@pytest.mark.parametrize("asset_type", list(AssetType))
def test_recommend_for_vulnerability_always_returns_text_for_critico(asset_type):
    # RF-16: toda vulnerabilidad critica debe tener recomendacion, sin
    # importar el tipo de activo.
    text = recommend_for_vulnerability(asset_type, RiskBand.critico)
    assert isinstance(text, str) and len(text) > 0


def test_recommend_for_vulnerability_always_returns_text_for_alto():
    for asset_type in AssetType:
        text = recommend_for_vulnerability(asset_type, RiskBand.alto)
        assert isinstance(text, str) and len(text) > 0


@pytest.mark.parametrize(
    "score,expected_band",
    [
        (1.0, "debil"),
        (2.49, "debil"),
        (2.5, "moderado"),
        (3.0, "moderado"),
        (3.49, "moderado"),
        (3.5, "fuerte"),
        (5.0, "fuerte"),
    ],
)
def test_nist_score_band_boundaries(score, expected_band):
    assert nist_score_band(score) == expected_band


def test_recommend_for_nist_function_fuerte_has_no_recommendation():
    # RF-17: solo se genera recomendacion si el promedio es menor a 3.5.
    assert recommend_for_nist_function(NistFunction.identify, 4.0) is None


def test_recommend_for_nist_function_debil_returns_text():
    text = recommend_for_nist_function(NistFunction.protect, 2.0)
    assert text is not None and len(text) > 0


def test_recommend_for_nist_function_moderado_returns_text():
    text = recommend_for_nist_function(NistFunction.recover, 3.0)
    assert text is not None and len(text) > 0


def test_recommend_for_nist_function_covers_all_functions_for_debil():
    # Las 5 funciones NIST deben tener al menos recomendacion para banda
    # "debil"; si falta una entrada en el catalogo para alguna funcion,
    # esta prueba la detecta.
    for function in NistFunction:
        text = recommend_for_nist_function(function, 1.0)
        assert text is not None, f"Falta entrada 'debil' en el catalogo para {function}"
