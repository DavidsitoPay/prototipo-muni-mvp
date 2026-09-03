from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import AssetType
from app.models.nist_assessment import NistFunction
from app.models.recommendation import Recommendation, RecommendationSource
from app.models.vulnerability import RiskBand, Vulnerability
from app.services.recommendation_engine import llm_enricher
from app.services.recommendation_engine.rules import (
    RISK_BANDS_THAT_TRIGGER_RECOMMENDATION,
    recommend_for_nist_function,
    recommend_for_vulnerability,
)


async def generate_for_vulnerability(
    db: AsyncSession, vulnerability: Vulnerability, asset_type: AssetType
) -> Recommendation | None:
    if vulnerability.risk_band not in RISK_BANDS_THAT_TRIGGER_RECOMMENDATION:
        return None

    rule_text = recommend_for_vulnerability(asset_type, vulnerability.risk_band)
    recommendation = Recommendation(
        vulnerability_id=vulnerability.id,
        source=RecommendationSource.regla,
        text=rule_text,
    )
    db.add(recommendation)

    enriched = await llm_enricher.enrich(
        rule_text, {"asset_type": asset_type.value, "risk_band": vulnerability.risk_band.value}
    )
    if enriched:
        db.add(
            Recommendation(
                vulnerability_id=vulnerability.id,
                source=RecommendationSource.llm,
                text=enriched,
            )
        )

    return recommendation


async def generate_for_nist_function(
    db: AsyncSession, function: NistFunction, average_score: float
) -> Recommendation | None:
    rule_text = recommend_for_nist_function(function, average_score)
    if rule_text is None:
        return None

    recommendation = Recommendation(nist_function=function, source=RecommendationSource.regla, text=rule_text)
    db.add(recommendation)

    enriched = await llm_enricher.enrich(rule_text, {"nist_function": function.value})
    if enriched:
        db.add(Recommendation(nist_function=function, source=RecommendationSource.llm, text=enriched))

    return recommendation
