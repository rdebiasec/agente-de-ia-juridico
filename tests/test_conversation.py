"""Conversación multi-turno, trazas persistidas y pipeline de validación."""

import pytest

from src.agents.pipeline import attach_session_continuity, run_pre_validations, run_post_validations
from src.gateway.agent_session import RepositoryAgentSession
from src.storage import get_repository
from src.storage.memory import InMemoryRepository


def test_pre_validations_multi_turn():
    trace = {"timestamp": 1}
    history = [{"role": "user", "content": "hola"}, {"role": "assistant", "content": "bienvenida"}]
    ok, err = run_pre_validations("¿y la tutela?", history=history, expediente_resumen=None, trace=trace)
    assert ok is True
    assert err is None
    assert trace["turn_index"] == 2
    assert any(s["name"] == "Validación: diálogo multi-turno" for s in trace["spans"])


def test_attach_session_continuity_enriches_trace():
    from src.storage.memory import InMemoryRepository
    from src.storage.models import SessionTrace

    repo = InMemoryRepository()
    history = [
        {"role": "user", "content": "Quiero una tutela"},
        {"role": "assistant", "content": "Indíqueme el accionante"},
    ]
    prior = [
        SessionTrace(
            session_id="web:u1",
            trace_id="tr-prev",
            turn_index=1,
            payload={"input_summary": "Quiero una tutela", "sent_to_agent": "tutela_constitucional", "spans": [{}]},
        )
    ]
    trace = {"timestamp": 1, "spans": [], "steps": []}
    attach_session_continuity(trace, history=history, session_id="web:u1", prior_traces=prior)
    assert trace["session_message_count"] == 2
    assert trace["prior_traces_count"] == 1
    assert len(trace["session_flow"]) == 1
    assert any(s["kind"] == "session" and "Historial turno previo" in s["name"] for s in trace["spans"])
    assert any(s["name"] == "Sesión: encadenar turno anterior" for s in trace["spans"])


def test_expediente_sync_from_tutela_message():
    from src.services.expediente_sync import sync_expediente_from_chat
    from src.storage.memory import InMemoryRepository
    from src.gateway import expediente as exp_mod

    repo = InMemoryRepository()
    exp_mod.expediente_store.repo = repo
    msg = (
        "Accionante: Carlos Andrés Gómez Vega CC 71234567. "
        "Accionado: Cementerio Jardines de la Esperanza S.A.S. NIT 900.123.456-7. "
        "Quiero una tutela por vulneración del debido proceso. Radicado interno CE-PET-2026-0315."
    )
    trace = {"timestamp": 1, "spans": []}
    result = sync_expediente_from_chat("web:tut", msg, [], trace=trace)
    assert result["cambios"]
    assert "tutela" in result["resumen"].lower() or "Expediente" in result["resumen"]
    assert any(s["name"] == "Expediente: sincronización" for s in trace["spans"])


def test_post_validations_pide_datos_tutela():
    trace = {"timestamp": 1, "sent_to_agent": "tutela_constitucional"}
    text = run_post_validations("Redacte una tutela", "Borrador preliminar.", trace)
    assert "accionante" in text.lower() or trace.get("conversation_continues")


def test_session_and_trace_persist_in_memory():
    repo = InMemoryRepository()
    from src.storage import reset_repository

    reset_repository()
    # monkeypatch would be cleaner; test repo directly
    repo.append_chat_message("web:u1", channel="web", user_id="u1", role="user", content="Hola", max_messages=50)
    repo.append_chat_message("web:u1", channel="web", user_id="u1", role="assistant", content="Bienvenida", max_messages=50)
    session = repo.get_chat_session("web:u1")
    assert session is not None
    assert len(session.messages) == 2

    from src.storage.models import SessionTrace

    repo.add_session_trace(
        SessionTrace(session_id="web:u1", trace_id="tr-abc", turn_index=1, payload={"spans": [{"name": "test"}]})
    )
    traces = repo.list_session_traces("web:u1")
    assert len(traces) == 1
    assert traces[0].payload["spans"][0]["name"] == "test"


def test_repository_agent_session_roundtrip():
    import asyncio
    import uuid

    from src.storage import reset_repository

    reset_repository()
    sid = f"web:test-{uuid.uuid4().hex[:8]}"
    session = RepositoryAgentSession(sid, channel="web", user_id="u2")

    async def _run():
        await session.add_items([{"role": "user", "content": "Primera pregunta"}])
        items = await session.get_items()
        assert len(items) == 1
        assert items[0]["content"] == "Primera pregunta"

    asyncio.run(_run())


@pytest.mark.asyncio
async def test_chat_reset_endpoint_clears_session(monkeypatch):
    from httpx import ASGITransport, AsyncClient

    from src.gateway import reset as reset_module
    from src.main import app
    from src.storage.memory import InMemoryRepository
    from src.storage.models import SessionTrace

    repo = InMemoryRepository()
    monkeypatch.setattr(reset_module, "get_repository", lambda: repo)

    uid = "reset-user"
    sid = f"web:{uid}"
    repo.append_chat_message(sid, channel="web", user_id=uid, role="user", content="Hola", max_messages=50)
    repo.add_session_trace(SessionTrace(session_id=sid, trace_id="tr-1", turn_index=1, payload={"ok": True}))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/chat/reset", json={"channel": "web", "user_id": uid})

    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert data["session_id"] == sid
    assert data["cleared_messages"] is True
    assert data["cleared_traces"] == 1
    session = repo.get_chat_session(sid)
    assert session is not None
    assert session.messages == []
    assert repo.list_session_traces(sid) == []
