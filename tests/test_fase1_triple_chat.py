"""Fase 1: hilos cliente, drafts outbound HITL, transcript interno."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.storage.memory import InMemoryRepository


@pytest.fixture()
def repo(monkeypatch):
    mem = InMemoryRepository()
    monkeypatch.setattr("src.storage.get_repository", lambda: mem)
    monkeypatch.setattr("src.services.triple_chat.get_repository", lambda: mem)
    return mem


def _start(tc, *, subject: str, lawyer: str = "web:abogada", nombre: str = "Víctima"):
    return tc.start_cliente_session(
        nombre=nombre,
        consent_1581=True,
        cliente_subject=subject,
        lawyer_session_id=lawyer,
    )


def test_enqueue_does_not_publish_gerente_to_client(repo):
    from src.services import triple_chat as tc

    _start(tc, subject="victima-01")
    out = tc.enqueue_client_message(
        message="Necesito saber el estado de mi denuncia",
        cliente_subject="victima-01",
        lawyer_session_id="web:abogada",
    )
    assert out["status"] == "en_revision"
    assert out["draft_id"]

    visible = tc.list_cliente_visible_messages("victima-01")
    roles = [m["role"] for m in visible["messages"]]
    assert "cliente" in roles
    assert visible["status"] == "en_revision"
    # Bienvenida + inbound; sin propuesta pending
    assert all(m.get("visibility") != "pending_hitl" for m in visible["messages"])

    inbox = tc.list_cliente_inbox(status="proposed")
    assert len(inbox["drafts"]) == 1
    assert "TriageResult" not in inbox["drafts"][0]["proposed_text"]

    exp = repo.get_expediente("web:abogada")
    assert exp is not None
    assert exp.cliente_session_id == "cliente:victima-01"
    assert exp.lawyer_session_id == "web:abogada"


def test_approve_publishes_to_client(repo):
    from src.services import triple_chat as tc

    _start(tc, subject="victima-02")
    out = tc.enqueue_client_message(
        message="¿Cuándo es la audiencia?",
        cliente_subject="victima-02",
        lawyer_session_id="web:abogada",
    )
    approved = tc.approve_outbound_draft(
        out["draft_id"],
        revisor="abogada",
        edited_text="La audiencia está pendiente de confirmación del despacho.",
    )
    assert approved["ok"] is True
    assert approved["draft"]["status"] == "sent"

    visible = tc.list_cliente_visible_messages("victima-02")
    texts = [m["content"] for m in visible["messages"] if m["role"] == "gerente"]
    assert "La audiencia está pendiente de confirmación del despacho." in texts
    assert visible["status"] == "respuesta_lista"


def test_reject_keeps_client_without_gerente_reply(repo):
    from src.services import triple_chat as tc

    _start(tc, subject="victima-03")
    out = tc.enqueue_client_message(
        message="Consulta",
        cliente_subject="victima-03",
        lawyer_session_id="web:abogada",
    )
    tc.reject_outbound_draft(out["draft_id"], revisor="abogada", comentario="Rehacer tono")
    visible = tc.list_cliente_visible_messages("victima-03")
    # Bienvenida del Coordinador puede existir; no hay respuesta al inbound
    cliente_msgs = [m for m in visible["messages"] if m["role"] == "cliente"]
    assert len(cliente_msgs) == 1
    # Solo bienvenida de gerente (no draft aprobado)
    gerente = [m for m in visible["messages"] if m["role"] == "gerente"]
    assert len(gerente) == 1


def test_internal_transcript_roundtrip(repo):
    from src.services import triple_chat as tc

    entry = tc.append_internal_transcript(
        session_id="web:abogada",
        from_actor="gerente",
        to_actor="especialista:analista_cronologia_hechos",
        pedido="Ordenar hechos del 12-ene",
        respuesta="3 eventos; 1 contradicción de fechas",
    )
    listed = tc.list_internal_transcript("web:abogada")
    assert listed["entries"][0]["id"] == entry.id
    assert "cronologia" in listed["entries"][0]["to_actor"]


def test_lawyer_impersonation_meta_and_bitacora(repo):
    from src.services import triple_chat as tc

    _start(tc, subject="victima-imp", lawyer="web:abogada", nombre="Carla")
    out = tc.enqueue_lawyer_as_client(
        message="Texto del despacho como víctima",
        lawyer_session_id="web:abogada",
        lawyer_actor_id="abogada",
    )
    assert out["authored_by"] == "lawyer_impersonation"
    desk = tc.list_lawyer_cliente_thread("web:abogada")
    assert any(m.get("badge") == "escrito_por_despacho" for m in desk["messages"])
    assert any(m.get("badge") == "borrador_pendiente" for m in desk["messages"])
    exp = repo.get_expediente("web:abogada")
    assert exp is not None
    bit = list(getattr(exp, "bitacora", None) or [])
    assert any("impersonación" in (e.get("resumen") or "").lower() for e in bit)


def test_api_cliente_chat_and_inbox(repo, monkeypatch):
    from src.config import get_settings

    monkeypatch.setenv("WEB_AUTH_ENABLED", "false")
    monkeypatch.setenv("SITE_PASSWORD", "")
    monkeypatch.setenv("IP_ALLOWLIST_ENABLED", "false")
    get_settings.cache_clear()

    from src.main import app

    client = TestClient(app)
    start = client.post(
        "/cliente/start",
        json={
            "nombre": "API User",
            "consent_1581": True,
            "cliente_session_id": "api-user-1",
            "lawyer_session_id": "web:abogada",
        },
    )
    assert start.status_code == 200, start.text

    res = client.post(
        "/cliente/chat",
        json={
            "message": "Hola, quiero avances de mi caso",
            "cliente_session_id": "api-user-1",
            "lawyer_session_id": "web:abogada",
        },
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["status"] == "en_revision"
    draft_id = body["draft_id"]

    msgs = client.get("/cliente/messages", params={"cliente_session_id": "api-user-1"})
    assert msgs.status_code == 200
    assert all(m["role"] in {"cliente", "gerente"} for m in msgs.json()["messages"])

    inbox = client.get("/abogado/cliente-inbox")
    assert inbox.status_code == 200
    assert any(d["id"] == draft_id for d in inbox.json()["drafts"])

    approve = client.post(
        f"/abogado/cliente-drafts/{draft_id}/approve",
        json={"revisor": "abogada", "edited_text": "Respuesta aprobada del Gerente."},
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["draft"]["status"] == "sent"

    msgs2 = client.get("/cliente/messages", params={"cliente_session_id": "api-user-1"})
    gerente = [m for m in msgs2.json()["messages"] if m["role"] == "gerente"]
    assert any(m["content"] == "Respuesta aprobada del Gerente." for m in gerente)
