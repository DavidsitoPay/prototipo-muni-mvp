from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.deps import get_current_user, require_role
from app.models.nist_assessment import NistAssessment, NistFunction
from app.models.user import UserRole
from app.schemas.nist import (
    NistAnswerIn,
    NistAssessmentOut,
    NistFunctionSummary,
    NistQuestionOut,
    NistSummaryOut,
)
from app.services.nist_engine import QUESTION_CATALOG, QUESTIONS_BY_CODE, average_score, maturity_percent
from app.services.recommendation_engine.service import generate_for_nist_function

router = APIRouter(prefix="/api/nist", tags=["nist"])


@router.get("/questions", response_model=list[NistQuestionOut], dependencies=[Depends(get_current_user)])
async def get_questions() -> list[NistQuestionOut]:
    return [NistQuestionOut(code=q["code"], function=q["function"], text=q["text"]) for q in QUESTION_CATALOG]


def _build_assessment_out(rows_by_code: dict[str, NistAssessment]) -> list[NistAssessmentOut]:
    out: list[NistAssessmentOut] = []
    for q in QUESTION_CATALOG:
        row = rows_by_code.get(q["code"])
        out.append(
            NistAssessmentOut(
                question_code=q["code"],
                function=q["function"],
                question_text=q["text"],
                score=row.score if row else None,
                evaluated_at=row.evaluated_at if row else None,
            )
        )
    return out


@router.get("/assessment", response_model=list[NistAssessmentOut], dependencies=[Depends(get_current_user)])
async def get_assessment(db: AsyncSession = Depends(get_db)) -> list[NistAssessmentOut]:
    result = await db.scalars(select(NistAssessment))
    return _build_assessment_out({row.question_code: row for row in result.all()})


@router.put("/assessment", response_model=list[NistAssessmentOut])
async def update_assessment(
    answers: list[NistAnswerIn],
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_role(UserRole.analista_riesgo, UserRole.admin_ti)),
) -> list[NistAssessmentOut]:
    existing_rows = {row.question_code: row for row in (await db.scalars(select(NistAssessment))).all()}
    touched_functions: set[NistFunction] = set()

    for answer in answers:
        catalog_entry = QUESTIONS_BY_CODE.get(answer.question_code)
        if catalog_entry is None:
            continue

        row = existing_rows.get(answer.question_code)
        if row is None:
            row = NistAssessment(
                function=catalog_entry["function"],
                question_code=answer.question_code,
                question_text=catalog_entry["text"],
            )
            db.add(row)
            existing_rows[answer.question_code] = row

        row.score = answer.score
        row.evaluated_at = datetime.now(timezone.utc)
        touched_functions.add(catalog_entry["function"])

    await db.flush()

    for function in touched_functions:
        scores = [
            row.score
            for row in existing_rows.values()
            if row.function == function and row.score is not None
        ]
        average = average_score(scores)
        if average is not None:
            await generate_for_nist_function(db, function, average)

    await db.commit()
    return _build_assessment_out(existing_rows)


@router.get("/summary", response_model=NistSummaryOut, dependencies=[Depends(get_current_user)])
async def get_summary(db: AsyncSession = Depends(get_db)) -> NistSummaryOut:
    result = await db.scalars(select(NistAssessment))
    rows = list(result.all())

    functions_summary: list[NistFunctionSummary] = []
    all_scores: list[int] = []

    for function in NistFunction:
        function_scores = [r.score for r in rows if r.function == function and r.score is not None]
        total_questions = sum(1 for q in QUESTION_CATALOG if q["function"] == function)
        all_scores.extend(function_scores)
        functions_summary.append(
            NistFunctionSummary(
                function=function,
                maturity_percent=maturity_percent(function_scores),
                answered_count=len(function_scores),
                total_questions=total_questions,
            )
        )

    return NistSummaryOut(
        global_maturity_percent=maturity_percent(all_scores),
        functions=functions_summary,
    )
