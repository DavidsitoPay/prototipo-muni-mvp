import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_db
from app.deps import get_current_user, require_role
from app.models.nist_assessment import NistAssessment, NistFunction
from app.models.recommendation import Recommendation
from app.models.user import UserRole
from app.models.vulnerability import Vulnerability
from app.schemas.recommendation import GenerateRecommendationIn, RecommendationOut
from app.services.nist_engine import average_score
from app.services.recommendation_engine.service import generate_for_nist_function, generate_for_vulnerability

router = APIRouter(tags=["recommendations"])


@router.get(
    "/api/vulnerabilities/{vulnerability_id}/recommendations",
    response_model=list[RecommendationOut],
    dependencies=[Depends(get_current_user)],
)
async def get_vulnerability_recommendations(
    vulnerability_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> list[Recommendation]:
    result = await db.scalars(
        select(Recommendation).where(Recommendation.vulnerability_id == vulnerability_id)
    )
    return list(result.all())


@router.get(
    "/api/nist/{function}/recommendations",
    response_model=list[RecommendationOut],
    dependencies=[Depends(get_current_user)],
)
async def get_nist_recommendations(function: NistFunction, db: AsyncSession = Depends(get_db)) -> list[Recommendation]:
    result = await db.scalars(select(Recommendation).where(Recommendation.nist_function == function))
    return list(result.all())


@router.post(
    "/api/recommendations/generate",
    response_model=RecommendationOut,
    status_code=status.HTTP_201_CREATED,
)
async def generate_recommendation(
    payload: GenerateRecommendationIn,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_role(UserRole.analista_riesgo, UserRole.admin_ti)),
) -> Recommendation:
    if payload.vulnerability_id is not None:
        vulnerability = await db.scalar(
            select(Vulnerability)
            .options(selectinload(Vulnerability.asset))
            .where(Vulnerability.id == payload.vulnerability_id)
        )
        if vulnerability is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Vulnerabilidad no encontrada")

        recommendation = await generate_for_vulnerability(db, vulnerability, vulnerability.asset.type)
        if recommendation is None:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "El riesgo de la vulnerabilidad no amerita recomendacion"
            )
        await db.commit()
        await db.refresh(recommendation)
        return recommendation

    if payload.nist_function is not None:
        rows = await db.scalars(
            select(NistAssessment).where(NistAssessment.function == payload.nist_function)
        )
        scores = [r.score for r in rows.all() if r.score is not None]
        average = average_score(scores)
        if average is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "La funcion NIST no tiene respuestas aun")
        recommendation = await generate_for_nist_function(db, payload.nist_function, average)
        if recommendation is None:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "La madurez de la funcion NIST no amerita recomendacion"
            )
        await db.commit()
        await db.refresh(recommendation)
        return recommendation

    raise HTTPException(status.HTTP_400_BAD_REQUEST, "Debe indicar vulnerability_id o nist_function")
