from httpx import AsyncClient

from app.services.nist_engine import maturity_percent


def test_maturity_percent_excludes_unanswered() -> None:
    assert maturity_percent([]) is None
    assert maturity_percent([5, 5]) == 100.0
    assert maturity_percent([1, 5]) == 60.0  # promedio 3/5 -> 60%, nulls no incluidos en la lista


async def test_questions_catalog_has_25_questions(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    response = await client.get("/api/nist/questions", headers=admin_headers)
    assert response.status_code == 200
    questions = response.json()
    assert len(questions) == 25
    functions = {q["function"] for q in questions}
    assert functions == {"identify", "protect", "detect", "respond", "recover"}


async def test_put_assessment_persists_submitted_scores(
    client: AsyncClient, analista_headers: dict[str, str]
) -> None:
    answers = [
        {"question_code": "PR-1", "score": 5},
        {"question_code": "PR-2", "score": 3},
    ]
    update_resp = await client.put("/api/nist/assessment", json=answers, headers=analista_headers)
    assert update_resp.status_code == 200

    assessment_resp = await client.get("/api/nist/assessment", headers=analista_headers)
    rows = {r["question_code"]: r for r in assessment_resp.json()}
    assert rows["PR-1"]["score"] == 5
    assert rows["PR-2"]["score"] == 3
    assert rows["PR-1"]["evaluated_at"] is not None

    summary_resp = await client.get("/api/nist/summary", headers=analista_headers)
    protect_summary = next(f for f in summary_resp.json()["functions"] if f["function"] == "protect")
    assert protect_summary["answered_count"] >= 2  # al menos las 2 que este test respondio


async def test_weak_nist_function_generates_recommendation(
    client: AsyncClient, analista_headers: dict[str, str]
) -> None:
    answers = [{"question_code": "DE-1", "score": 1}]
    await client.put("/api/nist/assessment", json=answers, headers=analista_headers)

    recs_resp = await client.get("/api/nist/detect/recommendations", headers=analista_headers)
    assert recs_resp.status_code == 200
    recs = recs_resp.json()
    assert len(recs) >= 1
    assert recs[0]["nist_function"] == "detect"
