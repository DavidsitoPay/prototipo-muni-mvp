import pytest
from httpx import AsyncClient

from app.models.asset import Asset

pytestmark = pytest.mark.asyncio


async def test_dashboard_summary_reflects_seeded_asset(
    client: AsyncClient, analista_headers: dict[str, str], demo_asset: Asset
) -> None:
    await client.post(
        f"/api/assets/{demo_asset.id}/vulnerabilities",
        json={"description": "riesgo alto", "probability": 5, "impact": 4},
        headers=analista_headers,
    )

    summary_resp = await client.get("/api/dashboard/summary", headers=analista_headers)
    assert summary_resp.status_code == 200
    summary = summary_resp.json()
    assert summary["total_assets"] >= 1
    assert any(a["asset_id"] == str(demo_asset.id) for a in summary["top_risky_assets"])


async def test_heatmap_counts_probability_impact(
    client: AsyncClient, analista_headers: dict[str, str], demo_asset: Asset
) -> None:
    await client.post(
        f"/api/assets/{demo_asset.id}/vulnerabilities",
        json={"description": "celda especifica", "probability": 2, "impact": 3},
        headers=analista_headers,
    )

    heatmap_resp = await client.get("/api/dashboard/heatmap", headers=analista_headers)
    assert heatmap_resp.status_code == 200
    cells = heatmap_resp.json()["cells"]
    assert len(cells) == 25
    target = next(c for c in cells if c["probability"] == 2 and c["impact"] == 3)
    assert target["count"] >= 1


async def test_nist_radar_has_all_functions(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    response = await client.get("/api/dashboard/nist-radar", headers=admin_headers)
    assert response.status_code == 200
    points = response.json()["points"]
    assert {p["function"] for p in points} == {"identify", "protect", "detect", "respond", "recover"}
