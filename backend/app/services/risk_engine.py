from app.models.vulnerability import RiskBand, Vulnerability, VulnerabilityStatus


def compute_risk(probability: int, impact: int) -> tuple[int, RiskBand]:
    """probabilidad x impacto -> (score, banda). Bandas: 1-4 bajo, 5-9 medio, 10-15 alto, 16-25 critico."""
    score = probability * impact
    if score <= 4:
        return score, RiskBand.bajo
    if score <= 9:
        return score, RiskBand.medio
    if score <= 15:
        return score, RiskBand.alto
    return score, RiskBand.critico


_BAND_ORDER = {RiskBand.bajo: 0, RiskBand.medio: 1, RiskBand.alto: 2, RiskBand.critico: 3}


def highest_band(bands: list[RiskBand]) -> RiskBand | None:
    if not bands:
        return None
    return max(bands, key=lambda b: _BAND_ORDER[b])


def active_vulnerabilities(vulnerabilities: list[Vulnerability]) -> list[Vulnerability]:
    """Vulnerabilidades no mitigadas: son las que deben impulsar el riesgo
    visible de un activo (una vulnerabilidad ya remediada no debe mantener
    el activo marcado como critico)."""
    return [v for v in vulnerabilities if v.status != VulnerabilityStatus.mitigada]


def asset_risk_band(vulnerabilities: list[Vulnerability]) -> RiskBand | None:
    return highest_band([v.risk_band for v in active_vulnerabilities(vulnerabilities)])


def worst_active_vulnerability(vulnerabilities: list[Vulnerability]) -> Vulnerability | None:
    active = active_vulnerabilities(vulnerabilities)
    if not active:
        return None
    return max(active, key=lambda v: v.risk_score)
