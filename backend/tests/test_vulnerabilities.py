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


async def test_list_asset_vulnerabilities_returns_created_vulnerability(
    client: AsyncClient, analista_headers: dict[str, str], demo_asset: Asset
) -> None:
    create_resp = await client.post(
        f"/api/assets/{demo_asset.id}/vulnerabilities",
        json={"description": "Para listar", "probability": 2, "impact": 2},
        headers=analista_headers,
    )
    vuln_id = create_resp.json()["id"]

    list_resp = await client.get(f"/api/assets/{demo_asset.id}/vulnerabilities", headers=analista_headers)
    assert list_resp.status_code == 200
    ids = [v["id"] for v in list_resp.json()]
    assert vuln_id in ids


async def test_list_asset_vulnerabilities_404_for_unknown_asset(
    client: AsyncClient, analista_headers: dict[str, str]
) -> None:
    import uuid

    response = await client.get(f"/api/assets/{uuid.uuid4()}/vulnerabilities", headers=analista_headers)
    assert response.status_code == 404


async def test_list_vulnerabilities_filters_by_risk_band_and_status(
    client: AsyncClient, analista_headers: dict[str, str], demo_asset: Asset
) -> None:
    create_resp = await client.post(
        f"/api/assets/{demo_asset.id}/vulnerabilities",
        json={"description": "Filtrable", "probability": 5, "impact": 5},
        headers=analista_headers,
    )
    vuln_id = create_resp.json()["id"]

    by_band = await client.get("/api/vulnerabilities", params={"risk_band": "critico"}, headers=analista_headers)
    assert by_band.status_code == 200
    assert any(v["id"] == vuln_id for v in by_band.json())

    by_status = await client.get("/api/vulnerabilities", params={"status_": "abierta"}, headers=analista_headers)
    assert by_status.status_code == 200
    assert any(v["id"] == vuln_id for v in by_status.json())


async def test_update_vulnerability_recomputes_risk_on_band_change(
    client: AsyncClient, analista_headers: dict[str, str], demo_asset: Asset
) -> None:
    create_resp = await client.post(
        f"/api/assets/{demo_asset.id}/vulnerabilities",
        json={"description": "Editable", "probability": 1, "impact": 1},
        headers=analista_headers,
    )
    vuln_id = create_resp.json()["id"]
    assert create_resp.json()["risk_band"] == "bajo"

    update_resp = await client.put(
        f"/api/vulnerabilities/{vuln_id}",
        json={"probability": 5, "impact": 5},
        headers=analista_headers,
    )
    assert update_resp.status_code == 200
    body = update_resp.json()
    assert body["risk_score"] == 25
    assert body["risk_band"] == "critico"

    recs_resp = await client.get(f"/api/vulnerabilities/{vuln_id}/recommendations", headers=analista_headers)
    assert len(recs_resp.json()) >= 1


async def test_update_vulnerability_description_only_does_not_require_band_change(
    client: AsyncClient, analista_headers: dict[str, str], demo_asset: Asset
) -> None:
    create_resp = await client.post(
        f"/api/assets/{demo_asset.id}/vulnerabilities",
        json={"description": "Original", "probability": 2, "impact": 2},
        headers=analista_headers,
    )
    vuln_id = create_resp.json()["id"]

    update_resp = await client.put(
        f"/api/vulnerabilities/{vuln_id}",
        json={"description": "Descripcion actualizada"},
        headers=analista_headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["description"] == "Descripcion actualizada"
    assert update_resp.json()["risk_band"] == "bajo"


async def test_update_vulnerability_404_for_unknown_id(client: AsyncClient, analista_headers: dict[str, str]) -> None:
    import uuid

    response = await client.put(
        f"/api/vulnerabilities/{uuid.uuid4()}",
        json={"description": "x"},
        headers=analista_headers,
    )
    assert response.status_code == 404


async def test_directivo_cannot_update_vulnerability(
    client: AsyncClient, directivo_headers: dict[str, str], analista_headers: dict[str, str], demo_asset: Asset
) -> None:
    create_resp = await client.post(
        f"/api/assets/{demo_asset.id}/vulnerabilities",
        json={"description": "Protegida", "probability": 2, "impact": 2},
        headers=analista_headers,
    )
    vuln_id = create_resp.json()["id"]

    response = await client.put(
        f"/api/vulnerabilities/{vuln_id}",
        json={"description": "No deberia poder"},
        headers=directivo_headers,
    )
    assert response.status_code == 403


async def test_delete_vulnerability_requires_admin_role(
    client: AsyncClient, analista_headers: dict[str, str], demo_asset: Asset
) -> None:
    create_resp = await client.post(
        f"/api/assets/{demo_asset.id}/vulnerabilities",
        json={"description": "No borrable por analista", "probability": 2, "impact": 2},
        headers=analista_headers,
    )
    vuln_id = create_resp.json()["id"]

    response = await client.delete(f"/api/vulnerabilities/{vuln_id}", headers=analista_headers)
    assert response.status_code == 403


async def test_delete_vulnerability_success_as_admin(
    client: AsyncClient, admin_headers: dict[str, str], analista_headers: dict[str, str], demo_asset: Asset
) -> None:
    create_resp = await client.post(
        f"/api/assets/{demo_asset.id}/vulnerabilities",
        json={"description": "Para borrar", "probability": 2, "impact": 2},
        headers=analista_headers,
    )
    vuln_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/api/vulnerabilities/{vuln_id}", headers=admin_headers)
    assert delete_resp.status_code == 204

    follow_up = await client.delete(f"/api/vulnerabilities/{vuln_id}", headers=admin_headers)
    assert follow_up.status_code == 404


async def test_delete_vulnerability_404_for_unknown_id(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    import uuid

    response = await client.delete(f"/api/vulnerabilities/{uuid.uuid4()}", headers=admin_headers)
    assert response.status_code == 404
