import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_chat_page():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=False) as client:
        r = await client.get("/abogado")
    assert r.status_code == 200
    assert "Escritorio del abogado" in r.text or "Asistente Jurídico" in r.text
    assert "trace-body" in r.text
    assert "workspace-layout" in r.text or "desk-layout" in r.text
    assert "workspace.js" in r.text


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
    assert data["modo"] == "firma"
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_chat_penal_scope_fallback():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/chat",
            json={"message": "¿Cómo apoyan la representación de víctimas en este caso penal?", "user_id": "test"},
        )
    assert r.status_code == 200
    data = r.json()
    lowered = data["text"].lower()
    assert "penal" in lowered or "víctima" in lowered or "victima" in lowered
    assert "revisión" in data["text"].lower() or "aprobación" in data["text"].lower()
    assert isinstance(data.get("trace"), dict)
    assert data["trace"].get("route")
    assert isinstance(data["trace"].get("steps"), list)


@pytest.mark.asyncio
async def test_chat_non_penal_request_is_out_of_scope():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/chat",
            json={"message": "Necesito asesoría sobre un arrendamiento habitacional.", "user_id": "test"},
        )
    assert r.status_code == 200
    data = r.json()
    lowered = data["text"].lower()
    assert "fuera de alcance penal-víctimas" in lowered
    assert data["pending_review"] is False
    assert data["trace"].get("sent_to_agent") == "coordinador_expediente_penal"


@pytest.mark.asyncio
async def test_chat_fase1_strategy_allowed():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/chat",
            json={"message": "Analiza los riesgos del caso y define estrategia procesal", "user_id": "test"},
        )
    assert r.status_code == 200
    data = r.json()
    assert "no está activa" not in data["text"].lower()
    assert data["pending_review"] is True


@pytest.mark.asyncio
async def test_chat_mixed_scope_reconduces_to_penal():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/chat",
            json={"message": "Tengo un conflicto de arrendamiento y además un caso penal por lesiones. ¿Cómo seguimos?", "user_id": "test"},
        )
    assert r.status_code == 200
    data = r.json()
    lowered = data["text"].lower()
    assert "fuera de alcance penal-víctimas" not in lowered
    assert "penal" in lowered or "víctima" in lowered or "victima" in lowered
    assert data["trace"].get("sent_to_agent") in {"coordinador_expediente_penal", "analista_ruta_procesal_ley906"}


@pytest.mark.asyncio
async def test_chat_seguimiento_capability_is_active():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/chat",
            json={"message": "Haga seguimiento mensual al radicado y envíe informe", "user_id": "test"},
        )
    assert r.status_code == 200
    data = r.json()
    lowered = data["text"].lower()
    assert "no está activa" not in lowered
    assert data["pending_review"] is True
    assert data["trace"].get("sent_to_agent") == "gestor_seguimiento_procesal_penal"


@pytest.mark.asyncio
async def test_chat_tutela_capability_is_active():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/chat",
            json={"message": "Redacta una tutela por derecho de petición", "user_id": "test"},
        )
    assert r.status_code == 200
    data = r.json()
    lowered = data["text"].lower()
    assert "no está activa" not in lowered
    assert data["pending_review"] is True
    assert data["trace"].get("sent_to_agent") == "evaluador_derechos_fundamentales_tutela"


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
        "Fase 1 · Borrador"
    )
    out = apply_output_guardrails(duplicated)
    assert out.count(DISCLAIMER_TEXT) == 1
    assert "Fase 1 · Borrador" not in out
