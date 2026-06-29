"""Tests de validación Fase 1 — probes dinámicos y rúbrica."""

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.validation.rubric import total_weight
from src.validation.probes import generate_probes


@pytest.mark.asyncio
async def test_validation_rubric():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/validation/rubric")
    assert r.status_code == 200
    data = r.json()
    assert data["total_weight"] == 100
    assert len(data["blocks"]) == 6
    assert data["connection"]["weight"] == 10


def test_rubric_weights_sum_to_100():
    assert total_weight() == 100


@pytest.mark.asyncio
async def test_generate_probes_fallback():
    result = await generate_probes(user_id="test-py", probes_per_block=2)
    assert "session_id" in result
    assert result["source"] in ("fallback", "llm")
    assert "communication" in result["blocks"]
    assert len(result["blocks"]["communication"]) >= 1


@pytest.mark.asyncio
async def test_generate_probes_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/validation/generate-probes",
            json={"user_id": "test-api", "probes_per_block": 2},
        )
    assert r.status_code == 200
    data = r.json()
    assert "blocks" in data
    assert "analysis" in data["blocks"]


@pytest.mark.asyncio
async def test_chat_page_has_score_ui():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=True) as client:
        r = await client.get("/")
    assert r.status_code == 200
    if "validation-score" in r.text:
        assert "Panel de Pruebas" in r.text
        assert "session-report-body" in r.text
        assert "reset-score-btn" in r.text


def test_compute_metrics_and_rules():
    from src.validation.report import build_rules_insights, compute_metrics

    session = {
        "sessionId": "sess-test",
        "startedAt": "2026-06-20T10:00:00",
        "lastActivityAt": "2026-06-20T10:30:00",
        "marks": {"communication": "pass", "phase-block": "fail"},
        "checklistChecked": {"0": True, "1": True},
        "chatLog": [
            {"role": "user", "text": "Hola", "via": "manual"},
            {"role": "assistant", "text": "Respuesta", "latencyMs": 1200},
        ],
        "events": [{"type": "mark", "blockId": "communication", "mark": "pass"}],
    }
    metrics = compute_metrics(session)
    assert metrics["score"] == 18
    assert metrics["chat_turns"] == 1
    assert metrics["sections_failed"] == 1
    assert metrics["duration_minutes"] == 30.0

    insights = build_rules_insights(session)
    assert any("CRÍTICO" in i for i in insights)
    assert any("Puntaje" in i for i in insights)


@pytest.mark.asyncio
async def test_session_report_llm_status_without_llm():
    session = {
        "sessionId": "sess-llm-status",
        "startedAt": "2026-06-20T10:00:00",
        "lastActivityAt": "2026-06-20T10:05:00",
        "marks": {"connection": "pass"},
        "chatLog": [],
        "events": [],
        "checklistChecked": {},
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/validation/session-report",
            json={"user_id": "test-llm-status", "session": session, "include_llm": False},
        )
    assert r.status_code == 200
    data = r.json()
    assert data["llm_status"] == "skipped_no_key"
    assert "llm_message" in data
    assert data["metrics"]["score"] == 10


@pytest.mark.asyncio
async def test_session_rules_endpoint():
    from src.validation.report import build_rules_insights

    session = {
        "sessionId": "sess-rules",
        "marks": {"communication": "pass"},
        "chatLog": [{"role": "user", "text": "Hola", "blockId": "communication"}],
        "events": [],
        "checklistChecked": {},
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post("/validation/session-rules", json={"session": session})
    assert r.status_code == 200
    data = r.json()
    assert "rules_insights" in data
    assert data["rules_insights"] == build_rules_insights(session)


@pytest.mark.asyncio
async def test_session_export_translated_marks():
    session = {
        "sessionId": "sess-export-marks",
        "startedAt": "2026-06-20T10:00:00",
        "lastActivityAt": "2026-06-20T10:05:00",
        "marks": {"communication": "pass"},
        "markNotes": {"communication": "Cumple criterios"},
        "chatLog": [],
        "events": [],
        "checklistChecked": {},
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/validation/session-export",
            json={"user_id": "test-export-marks", "session": session},
        )
    assert r.status_code == 200
    body = r.content.decode("utf-8")
    assert "Aprobada" in body
    assert "Cumple criterios" in body


@pytest.mark.asyncio
async def test_chat_page_reset_clears_chat_guard():
    """Regression: reset must clear chat and ignore stale async saves."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/static/chat.js")
    assert r.status_code == 200
    body = r.text
    assert "resetChatConversation" in body
    assert "chatEpoch" in body
    assert "chatLog: chatLog.slice()" in body


@pytest.mark.asyncio
async def test_report_panel_hides_disclaimer_and_session_id():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/static/report.js")
    assert r.status_code == 200
    body = r.text
    assert "Borrador analítico — requiere revisión humana. No constituye dictamen legal." not in body
    assert 'Sesión <code>${escapeHtml(session.sessionId || "—")}</code>' not in body
    assert "Sesión iniciada — aún no hay secciones evaluadas." not in body


@pytest.mark.asyncio
async def test_linked_messages_count_only_user_validation_messages():
    """Mensajes vinculados: contar solo envíos de validación, no respuestas del asistente."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        chat_js = await client.get("/static/chat.js")
        report_js = await client.get("/static/report.js")
    assert chat_js.status_code == 200
    assert report_js.status_code == 200
    assert 'm.blockId === blockId && m.role === "user"' in chat_js.text
    assert 'm.blockId === test.id && m.role === "user"' in report_js.text


@pytest.mark.asyncio
async def test_chat_page_has_report_and_reset_buttons():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/")
    assert r.status_code == 200
    assert "trace-body" in r.text
    assert "trace-toggle" in r.text
    assert "reset-chat-btn" in r.text
    assert "Reiniciar chat" in r.text
    assert "btn-export-doc" not in r.text
    assert "Descargar informe (.doc)" not in r.text
    assert "Imprimir / Guardar PDF" in r.text


@pytest.mark.asyncio
async def test_session_report_endpoint():
    from src.validation.report import build_session_report

    session = {
        "sessionId": "sess-api",
        "startedAt": "2026-06-20T10:00:00",
        "lastActivityAt": "2026-06-20T10:05:00",
        "marks": {"connection": "pass"},
        "chatLog": [],
        "events": [],
        "checklistChecked": {},
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/validation/session-report",
            json={"user_id": "test-report", "session": session, "include_llm": False},
        )
    assert r.status_code == 200
    data = r.json()
    assert "metrics" in data
    assert "rules_insights" in data
    assert "llm_status" in data
    assert data["source"] == "rules"
    assert data["metrics"]["score"] == 10

    report = await build_session_report(session, include_llm=False)
    assert report["metrics"]["session_id"] == "sess-api"


@pytest.mark.asyncio
async def test_session_export_endpoint():
    session = {
        "sessionId": "sess-export",
        "startedAt": "2026-06-20T10:00:00",
        "lastActivityAt": "2026-06-20T10:05:00",
        "marks": {},
        "chatLog": [{"role": "user", "text": "Prueba"}],
        "events": [],
        "checklistChecked": {},
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/validation/session-export",
            json={"user_id": "test-export", "session": session},
        )
    assert r.status_code == 200
    assert "application/msword" in r.headers.get("content-type", "")
    assert b"Reporte anal" in r.content
    assert b"Prueba" in r.content


@pytest.mark.asyncio
async def test_manual_page_and_app_link():
    """Manual de uso: enlace desde la app y secciones clave en /help."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        index_r = await client.get("/")
        manual_r = await client.get("/help")

    assert index_r.status_code == 200
    assert 'href="/help"' in index_r.text
    assert "Manual de Uso" in index_r.text
    assert "help-panel" not in index_r.text
    assert "btn-help-toggle" not in index_r.text

    assert manual_r.status_code == 200
    manual = manual_r.text
    assert "Manual de uso — Fase 1" in manual
    assert 'class="manual-page"' in manual
    assert "Capacidades habilitadas" in manual
    assert "Capacidades fuera de alcance" in manual
    assert "Reglas inmutables" in manual
    assert "la ia propone" in manual.lower()
    assert 'href="/"' in manual
    assert "Volver a Herramienta" in manual
