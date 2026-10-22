"""Pruebas unitarias puras del motor de riesgo (modulo critico #1 del E2,
seccion 2.6: "logica pura, facil de probar de forma aislada"). No usan DB
ni HTTP: instancian directamente las funciones y, cuando se necesita un
objeto Vulnerability, se construye en memoria sin persistirlo."""

import pytest

from app.models.vulnerability import RiskBand, Vulnerability, VulnerabilityStatus
from app.services.risk_engine import (
    active_vulnerabilities,
    asset_risk_band,
    compute_risk,
    highest_band,
    worst_active_vulnerability,
)


def _vuln(risk_band: RiskBand, risk_score: int, status: VulnerabilityStatus = VulnerabilityStatus.abierta) -> Vulnerability:
    return Vulnerability(risk_band=risk_band, risk_score=risk_score, status=status)


@pytest.mark.parametrize(
    "probability,impact,expected_score,expected_band",
    [
        (1, 1, 1, RiskBand.bajo),
        (1, 4, 4, RiskBand.bajo),
        (1, 5, 5, RiskBand.medio),
        (3, 3, 9, RiskBand.medio),
        (2, 5, 10, RiskBand.alto),
        (3, 5, 15, RiskBand.alto),
        (4, 4, 16, RiskBand.critico),
        (5, 5, 25, RiskBand.critico),
    ],
)
def test_compute_risk_boundaries(probability, impact, expected_score, expected_band):
    score, band = compute_risk(probability, impact)
    assert score == expected_score
    assert band == expected_band


def test_highest_band_empty_list_is_none():
    assert highest_band([]) is None


def test_highest_band_single_value():
    assert highest_band([RiskBand.medio]) == RiskBand.medio


def test_highest_band_picks_maximum():
    assert highest_band([RiskBand.bajo, RiskBand.critico, RiskBand.medio]) == RiskBand.critico


def test_highest_band_ties_return_that_band():
    assert highest_band([RiskBand.alto, RiskBand.alto]) == RiskBand.alto


def test_active_vulnerabilities_excludes_mitigada():
    vulns = [
        _vuln(RiskBand.critico, 25, VulnerabilityStatus.mitigada),
        _vuln(RiskBand.medio, 6, VulnerabilityStatus.abierta),
    ]
    active = active_vulnerabilities(vulns)
    assert len(active) == 1
    assert active[0].status == VulnerabilityStatus.abierta


def test_active_vulnerabilities_empty_input():
    assert active_vulnerabilities([]) == []


def test_asset_risk_band_ignores_mitigated_even_if_critical():
    vulns = [
        _vuln(RiskBand.critico, 25, VulnerabilityStatus.mitigada),
        _vuln(RiskBand.bajo, 2, VulnerabilityStatus.abierta),
    ]
    assert asset_risk_band(vulns) == RiskBand.bajo


def test_asset_risk_band_no_active_vulnerabilities_is_none():
    vulns = [_vuln(RiskBand.critico, 25, VulnerabilityStatus.mitigada)]
    assert asset_risk_band(vulns) is None


def test_asset_risk_band_no_vulnerabilities_at_all_is_none():
    assert asset_risk_band([]) is None


def test_worst_active_vulnerability_picks_highest_score():
    low = _vuln(RiskBand.bajo, 3)
    high = _vuln(RiskBand.alto, 12)
    medium = _vuln(RiskBand.medio, 6)
    assert worst_active_vulnerability([low, high, medium]) is high


def test_worst_active_vulnerability_skips_mitigated():
    mitigated_critical = _vuln(RiskBand.critico, 25, VulnerabilityStatus.mitigada)
    open_medium = _vuln(RiskBand.medio, 6)
    assert worst_active_vulnerability([mitigated_critical, open_medium]) is open_medium


def test_worst_active_vulnerability_no_vulnerabilities_is_none():
    assert worst_active_vulnerability([]) is None


def test_worst_active_vulnerability_all_mitigated_is_none():
    vulns = [_vuln(RiskBand.critico, 25, VulnerabilityStatus.mitigada)]
    assert worst_active_vulnerability(vulns) is None
