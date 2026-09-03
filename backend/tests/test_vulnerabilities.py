import pytest
from httpx import AsyncClient

from app.models.asset import Asset

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "probability,impact,expected_band",
    [
        (1, 4, "bajo"),  # score 4 -> limite superior de "bajo"
        (1, 5, "medio"),  # score 5 -> limite inferior de "medio"
        (3, 3, "medio"),  # score 9 -> limite superior de "medio"
        (2, 5, "alto"),  # score 10 -> limite inferior de "alto"
        (3, 5, "alto"),  # score 15 -> limite superior de "alto"
        (4, 4, "critico"),  # score 16 -> limite inferior de "critico"
        (5, 5, "critico"),  # score 25 -> maximo
    ],
)
async def test_risk_band_boundaries(
    client: AsyncClient,
    analista_headers: dict[str, str],
    demo_asset: Asset,
    probability: int,
    impact: int,
    expected_band: str,
) -> None:
    response = await client.post(
        f"/api/assets/{demo_asset.id}/vulnerabilities",
        json={"description": "Vulnerabilidad de prueba", "probability": probability, "impact": impact},
        headers=analista_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["risk_score"] == probability * impact
    assert body["risk_band"] == expected_band


@pytest.mark.parametrize("probability,impact", [(5, 5), (5, 3)])
async def test_high_or_critical_vulnerability_gets_recommendation(
    client: AsyncClient, analista_headers: dict[str, str], demo_asset: Asset, probability: int, impact: int
) -> None:
    create_resp = await client.post(
        f"/api/assets/{demo_asset.id}/vulnerabilities",
        json={"description": "Vulnerabilidad de riesgo alto", "probability": probability, "impact": impact},
        headers=analista_headers,
    )
    vuln_id = create_resp.json()["id"]

    recs_resp = await client.get(f"/api/vulnerabilities/{vuln_id}/recommendations", headers=analista_headers)
    assert recs_resp.status_code == 200
    recs = recs_resp.json()
    assert len(recs) >= 1
    assert recs[0]["source"] == "regla"


async def test_low_risk_vulnerability_has_no_recommendation(
    client: AsyncClient, analista_headers: dict[str, str], demo_asset: Asset
) -> None:
    create_resp = await client.post(
        f"/api/assets/{demo_asset.id}/vulnerabilities",
        json={"description": "Vulnerabilidad de riesgo bajo", "probability": 1, "impact": 2},
        headers=analista_headers,
    )
    vuln_id = create_resp.json()["id"]

    recs_resp = await client.get(f"/api/vulnerabilities/{vuln_id}/recommendations", headers=analista_headers)
    assert recs_resp.json() == []


async def test_directivo_cannot_create_vulnerability(
    client: AsyncClient, directivo_headers: dict[str, str], demo_asset: Asset
) -> None:
    response = await client.post(
        f"/api/assets/{demo_asset.id}/vulnerabilities",
        json={"description": "x", "probability": 3, "impact": 3},
        headers=directivo_headers,
    )
    assert response.status_code == 403


async def test_asset_detail_reflects_highest_risk_band(
    client: AsyncClient, analista_headers: dict[str, str], demo_asset: Asset
) -> None:
    await client.post(
        f"/api/assets/{demo_asset.id}/vulnerabilities",
        json={"description": "baja", "probability": 1, "impact": 1},
        headers=analista_headers,
    )
    await client.post(
        f"/api/assets/{demo_asset.id}/vulnerabilities",
        json={"description": "critica", "probability": 5, "impact": 5},
        headers=analista_headers,
    )

    detail = await client.get(f"/api/assets/{demo_asset.id}", headers=analista_headers)
    assert detail.status_code == 200
    body = detail.json()
    assert body["risk_band"] == "critico"
    assert len(body["vulnerabilities"]) == 2
