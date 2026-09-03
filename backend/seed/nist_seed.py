from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.nist_assessment import NistAssessment, NistFunction
from app.services.nist_engine import QUESTION_CATALOG
from app.services.recommendation_engine.service import generate_for_nist_function

# Deliberadamente parcial (~68%): Identificar/Proteger fuertes, Detectar/Responder
# debiles, Recuperar moderado - para que el dashboard muestre areas fuertes y debiles.
ANSWERED_SCORES: dict[str, int] = {
    "ID-1": 4, "ID-2": 5, "ID-3": 4, "ID-4": 3,
    "PR-1": 4, "PR-2": 4, "PR-3": 5, "PR-4": 3,
    "DE-1": 2, "DE-2": 1, "DE-3": 2,
    "RS-1": 2, "RS-2": 1, "RS-4": 2,
    "RC-1": 3, "RC-2": 2, "RC-3": 3,
}


async def seed_nist(db: AsyncSession) -> None:
    now = datetime.now(timezone.utc)
    rows_by_function: dict[NistFunction, list[NistAssessment]] = {f: [] for f in NistFunction}

    for q in QUESTION_CATALOG:
        score = ANSWERED_SCORES.get(q["code"])
        row = NistAssessment(
            function=q["function"],
            question_code=q["code"],
            question_text=q["text"],
            score=score,
            evaluated_at=now if score is not None else None,
        )
        db.add(row)
        rows_by_function[q["function"]].append(row)

    await db.flush()

    for function, rows in rows_by_function.items():
        scores = [r.score for r in rows if r.score is not None]
        if scores:
            average = sum(scores) / len(scores)
            await generate_for_nist_function(db, function, average)

    await db.flush()
