import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_chat_page():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/")
    assert r.status_code == 200
    assert "Asistente Jurídico" in r.text
    assert "validation-blocks" in r.text
    assert "validation-tests.js" in r.text


@pytest.mark.asyncio
async def test_validation_tests_static():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/static/validation-tests.js")
    assert r.status_code == 200
    assert "VALIDATION_TESTS" in r.text


@pytest.mark.asyncio
async def test_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["fase_activa"] == 0
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_chat_areas_derecho_fallback():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/chat",
            json={"message": "¿Qué áreas del derecho maneja el despacho?", "user_id": "test"},
        )
    assert r.status_code == 200
    data = r.json()
    assert "civil" in data["text"].lower() or "familia" in data["text"].lower()
    assert "revisión" in data["text"].lower() or "aprobación" in data["text"].lower()


@pytest.mark.asyncio
async def test_chat_fase1_blocked():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/chat",
            json={"message": "Redacta un contrato de prestación de servicios", "user_id": "test"},
        )
    assert r.status_code == 200
    data = r.json()
    assert "no está activa" in data["text"].lower() or "fase" in data["text"].lower()


@pytest.mark.asyncio
async def test_chat_fase1_strategy_blocked():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/chat",
            json={"message": "Analiza los riesgos del caso y define estrategia procesal", "user_id": "test"},
        )
    assert r.status_code == 200
    data = r.json()
    assert "fase" in data["text"].lower()
    assert "no" in data["text"].lower() and "activa" in data["text"].lower()


@pytest.mark.asyncio
async def test_chat_mixed_scope_is_blocked():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/chat",
            json={"message": "¿Qué áreas manejan y me redactas un contrato?", "user_id": "test"},
        )
    assert r.status_code == 200
    data = r.json()
    assert "fase" in data["text"].lower()
    assert "no" in data["text"].lower() and "activa" in data["text"].lower()


@pytest.mark.asyncio
async def test_guardrails_disclaimer():
    from src.agents.guardrails import apply_output_guardrails

    out = apply_output_guardrails("Respuesta de prueba.")
    assert "revisión" in out.lower() or "aprobación" in out.lower()


@pytest.mark.asyncio
async def test_guardrails_disclaimer_deduplicates():
    from src.agents.guardrails import DISCLAIMER_TEXT, apply_output_guardrails

    duplicated = (
        "Respuesta de prueba.\n\n"
        "*Borrador informativo — requiere revisión y aprobación del abogado.*\n"
        "---\n"
        "*Borrador informativo — requiere revisión y aprobación del abogado.*\n"
        "Fase 0 · Borrador"
    )
    out = apply_output_guardrails(duplicated)
    assert out.count(DISCLAIMER_TEXT) == 1
    assert "Fase 0 · Borrador" not in out
