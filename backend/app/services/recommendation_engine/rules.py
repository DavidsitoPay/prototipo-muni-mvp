from app.models.asset import AssetType
from app.models.nist_assessment import NistFunction
from app.models.vulnerability import RiskBand
from app.services.recommendation_engine.catalog import (
    ASSET_RISK_CATALOG,
    GENERIC_RISK_FALLBACK,
    NIST_FUNCTION_CATALOG,
)

RISK_BANDS_THAT_TRIGGER_RECOMMENDATION = {RiskBand.alto, RiskBand.critico}


def recommend_for_vulnerability(asset_type: AssetType, risk_band: RiskBand) -> str:
    """Siempre retorna al menos un texto (fallback generico), garantizando el
    criterio de aceptacion: toda vulnerabilidad alta/critica tiene recomendacion."""
    texts = (
        ASSET_RISK_CATALOG.get((asset_type.value, risk_band.value))
        or ASSET_RISK_CATALOG.get(("*", risk_band.value))
        or GENERIC_RISK_FALLBACK
    )
    return texts[0]


def nist_score_band(average_score: float) -> str:
    if average_score < 2.5:
        return "debil"
    if average_score < 3.5:
        return "moderado"
    return "fuerte"


def recommend_for_nist_function(function: NistFunction, average_score: float) -> str | None:
    band = nist_score_band(average_score)
    if band == "fuerte":
        return None
    texts = NIST_FUNCTION_CATALOG.get((function.value, band))
    return texts[0] if texts else None
