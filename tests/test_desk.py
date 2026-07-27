import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_abogado_desk_page():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=False) as client:
        root = await client.get("/")
        assert root.status_code == 302
        assert root.headers["location"] == "/abogado"
        r = await client.get("/abogado")
    assert r.status_code == 200
    assert "Escritorio del abogado" in r.text
    assert "reset-chat-btn-header" in r.text
    assert "desk.css" in r.text


@pytest.mark.asyncio
async def test_soporte_redirects_to_abogado_actividad():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=False) as client:
        r = await client.get("/soporte")
    assert r.status_code == 302
    assert r.headers["location"] == "/abogado#actividad"


@pytest.mark.asyncio
async def test_abogado_has_unified_actividad_tab():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/abogado")
    assert r.status_code == 200
    assert 'data-tab="actividad"' in r.text
    assert "activity-ops-list" in r.text
    assert "activity-live-toggle" in r.text


@pytest.mark.asyncio
async def test_support_operations_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/support/operations")
    assert r.status_code == 200
    data = r.json()
    assert "operations" in data
    assert isinstance(data["operations"], list)
