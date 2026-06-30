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
async def test_soporte_desk_page():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/soporte")
    assert r.status_code == 200
    assert "Consola de soporte" in r.text
    assert "desk-soporte.js" in r.text


@pytest.mark.asyncio
async def test_support_operations_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/support/operations")
    assert r.status_code == 200
    data = r.json()
    assert "operations" in data
    assert isinstance(data["operations"], list)
