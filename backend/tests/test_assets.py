import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

ASSET_PAYLOAD = {
    "name": "Servidor de correo institucional",
    "type": "servidor",
    "department": "Direccion de Informatica",
    "criticality": "alta",
    "owner": "Equipo de Infraestructura",
    "location": "on_prem",
}


async def test_create_list_update_delete_asset(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    create_resp = await client.post("/api/assets", json=ASSET_PAYLOAD, headers=admin_headers)
    assert create_resp.status_code == 201
    asset = create_resp.json()
    asset_id = asset["id"]
    assert asset["risk_band"] is None

    list_resp = await client.get("/api/assets", headers=admin_headers)
    assert list_resp.status_code == 200
    assert any(a["id"] == asset_id for a in list_resp.json())

    filtered_resp = await client.get("/api/assets", params={"q": "correo"}, headers=admin_headers)
    assert any(a["id"] == asset_id for a in filtered_resp.json())

    update_resp = await client.put(
        f"/api/assets/{asset_id}", json={"criticality": "critica"}, headers=admin_headers
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["criticality"] == "critica"

    delete_resp = await client.delete(f"/api/assets/{asset_id}", headers=admin_headers)
    assert delete_resp.status_code == 204

    list_after_delete = await client.get("/api/assets", headers=admin_headers)
    assert not any(a["id"] == asset_id for a in list_after_delete.json())


async def test_directivo_cannot_create_asset(client: AsyncClient, directivo_headers: dict[str, str]) -> None:
    response = await client.post("/api/assets", json=ASSET_PAYLOAD, headers=directivo_headers)
    assert response.status_code == 403


async def test_directivo_can_read_assets(client: AsyncClient, directivo_headers: dict[str, str]) -> None:
    response = await client.get("/api/assets", headers=directivo_headers)
    assert response.status_code == 200


async def test_list_assets_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/api/assets")
    assert response.status_code == 401
