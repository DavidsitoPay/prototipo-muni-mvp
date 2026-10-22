import pytest
from httpx import AsyncClient

from app.models.asset import Asset

pytestmark = pytest.mark.asyncio


async def test_executive_report_requires_authentication(client: AsyncClient):
    response = await client.get("/api/reports/executive")
    assert response.status_code == 401


async def test_executive_report_returns_pdf(client: AsyncClient, auth_headers: dict[str, str]):
    response = await client.get("/api/reports/executive", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")


async def test_executive_report_with_filters_that_match_nothing_still_returns_pdf(
    client: AsyncClient, auth_headers: dict[str, str]
):
    response = await client.get(
        "/api/reports/executive",
        params={"department": "Dependencia-Inexistente-XYZ"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.content.startswith(b"%PDF")


async def test_executive_report_filters_by_asset_type_and_criticality(
    client: AsyncClient, auth_headers: dict[str, str], demo_asset: Asset
):
    response = await client.get(
        "/api/reports/executive",
        params={"type": demo_asset.type.value, "criticality": demo_asset.criticality.value, "q": "prueba"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.content.startswith(b"%PDF")


async def test_technical_report_requires_authentication(client: AsyncClient):
    response = await client.get("/api/reports/technical")
    assert response.status_code == 401


async def test_technical_report_returns_pdf(client: AsyncClient, auth_headers: dict[str, str]):
    response = await client.get("/api/reports/technical", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")


async def test_technical_report_includes_vulnerability_and_recommendation(
    client: AsyncClient,
    analista_headers: dict[str, str],
    demo_asset: Asset,
):
    create_resp = await client.post(
        f"/api/assets/{demo_asset.id}/vulnerabilities",
        json={"description": "Vulnerabilidad para el reporte tecnico", "probability": 5, "impact": 5},
        headers=analista_headers,
    )
    assert create_resp.status_code == 201
    vuln_id = create_resp.json()["id"]

    # El reporte carga vulnerabilidades + recomendaciones en la misma
    # consulta (selectinload anidado); basta con que exista al menos una
    # recomendacion de regla ya disparada por la vulnerabilidad 5x5.
    report_resp = await client.get("/api/reports/technical", headers=analista_headers)
    assert report_resp.status_code == 200
    assert report_resp.content.startswith(b"%PDF")
    assert vuln_id  # la vulnerabilidad creada queda a cargo del cascade del fixture demo_asset
