"""Fase 3+: webchat consumidor /cliente + HITL desk + Canal víctima."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.storage.memory import InMemoryRepository


@pytest.fixture()
def repo(monkeypatch):
    mem = InMemoryRepository()
    monkeypatch.setattr("src.storage.get_repository", lambda: mem)
    monkeypatch.setattr("src.services.triple_chat.get_repository", lambda: mem)
    return mem


def _auth_off(monkeypatch):
    from src.config import get_settings

    monkeypatch.setenv("WEB_AUTH_ENABLED", "false")
    monkeypatch.setenv("SITE_PASSWORD", "")
    monkeypatch.setenv("IP_ALLOWLIST_ENABLED", "false")
    get_settings.cache_clear()


def test_cliente_static_assets_exist():
    assert Path("static/desk/cliente.html").is_file()
    assert Path("static/cliente.js").is_file()
    assert Path("static/cliente.css").is_file()
    html = Path("static/desk/cliente.html").read_text(encoding="utf-8")
    assert "Ley 1581" in html
    assert "Comenzar consulta" in html
    assert "Coordinador del Caso" in html
    assert "TriageResult" not in html
    js = Path("static/cliente.js").read_text(encoding="utf-8")
    assert "/cliente/start" in js
    assert "/cliente/chat" in js
    assert "/cliente/messages" in js
    assert "plan" not in js.lower() or "plan propuesto" not in js.lower()


def test_abogado_has_cliente_inbox_and_canal_victima():
    html = Path("static/desk/abogado.html").read_text(encoding="utf-8")
    assert 'id="tab-cliente-inbox"' in html
    assert "Respuestas al cliente" in html
    assert "Canal víctima" in html
    assert 'id="tab-canal-victima"' in html
    assert "Registrar mensaje recibido de la víctima" in html
    assert Path("static/canal-victima.js").is_file()
    firma = Path("static/firma.js").read_text(encoding="utf-8")
    assert "/abogado/cliente-inbox" in firma
    assert "cliente-drafts" in firma
    canal = Path("static/canal-victima.js").read_text(encoding="utf-8")
    assert "/abogado/cliente-thread" in canal
    assert "/abogado/cliente-as-client" in canal
    assert "Escrito por el despacho" in canal or "escrito_por_despacho" in canal


def test_webchat_alias_and_start_screen(repo, monkeypatch):
    _auth_off(monkeypatch)
    from src.main import app

    client = TestClient(app)
    for path in ("/cliente", "/webchat"):
        page = client.get(path)
        assert page.status_code == 200, path
        assert "Comenzar consulta" in page.text
        assert "Ley 1581" in page.text


def test_start_consent_then_chat(repo, monkeypatch):
    _auth_off(monkeypatch)
    from src.main import app

    client = TestClient(app)

    denied = client.post(
        "/cliente/chat",
        json={
            "message": "Hola sin consentimiento",
            "cliente_session_id": "fase3-no-consent",
            "lawyer_session_id": "web:abogada",
        },
    )
    assert denied.status_code == 400

    start = client.post(
        "/cliente/start",
        json={
            "nombre": "Ana Víctima",
            "consent_1581": True,
            "telefono": "3001234567",
            "cliente_session_id": "fase3-victima",
            "lawyer_session_id": "web:abogada",
        },
    )
    assert start.status_code == 200, start.text
    body = start.json()
    assert body["started"] is True
    assert body["client_display_name"] == "Ana Víctima"
    assert body["consent_at"]
    assert "lexiatek_cliente_session" in client.cookies

    msgs = client.get(
        "/cliente/messages", params={"cliente_session_id": "fase3-victima"}
    )
    assert msgs.status_code == 200
    data = msgs.json()
    assert data["started"] is True
    gerente = [m for m in data["messages"] if m["role"] == "gerente"]
    assert gerente, "debe haber bienvenida del Coordinador"
    assert "authored_by" not in gerente[0]
    assert "junta" not in str(data).lower()

    post = client.post(
        "/cliente/chat",
        json={
            "message": "Quiero saber el estado de mi denuncia",
            "cliente_session_id": "fase3-victima",
            "lawyer_session_id": "web:abogada",
        },
    )
    assert post.status_code == 200, post.text
    draft_id = post.json()["draft_id"]
    assert post.json()["status"] == "en_revision"

    before = client.get(
        "/cliente/messages", params={"cliente_session_id": "fase3-victima"}
    )
    roles = [m["role"] for m in before.json()["messages"]]
    assert "cliente" in roles
    assert all(m.get("visibility", "client_visible") == "client_visible" for m in before.json()["messages"])
    # Cliente nunca ve pending_hitl
    assert "pending_hitl" not in str(before.json())

    approve = client.post(
        f"/abogado/cliente-drafts/{draft_id}/approve",
        json={
            "revisor": "abogada",
            "edited_text": "Su denuncia está en seguimiento del despacho.",
        },
    )
    assert approve.status_code == 200, approve.text

    after = client.get(
        "/cliente/messages", params={"cliente_session_id": "fase3-victima"}
    )
    gerente2 = [m for m in after.json()["messages"] if m["role"] == "gerente"]
    assert any("seguimiento" in (m["content"] or "").lower() for m in gerente2)


def test_lawyer_as_client_hitl_then_client_sees(repo, monkeypatch):
    _auth_off(monkeypatch)
    from src.main import app

    client = TestClient(app)

    start = client.post(
        "/cliente/start",
        json={
            "nombre": "Luis",
            "consent_1581": True,
            "cliente_session_id": "victima-impersonate",
            "lawyer_session_id": "web:abogada",
        },
    )
    assert start.status_code == 200, start.text

    as_client = client.post(
        "/abogado/cliente-as-client",
        json={
            "text": "Mensaje dictado por el despacho en nombre de la víctima",
            "session_id": "web:abogada",
        },
    )
    assert as_client.status_code == 200, as_client.text
    draft_id = as_client.json()["draft_id"]
    assert as_client.json()["authored_by"] == "lawyer_impersonation"

    desk = client.get("/abogado/cliente-thread", params={"session_id": "web:abogada"})
    assert desk.status_code == 200, desk.text
    desk_data = desk.json()
    assert desk_data["thread_id"]
    badges = {m.get("badge") for m in desk_data["messages"]}
    assert "escrito_por_despacho" in badges
    assert "borrador_pendiente" in badges
    assert "webchat_url" in desk_data
    assert "caso=" in desk_data["webchat_url"]

    # Cliente ve el inbound impersonado como mensaje propio (Usted), no ve pending
    visible = client.get(
        "/cliente/messages", params={"cliente_session_id": "victima-impersonate"}
    )
    assert visible.status_code == 200
    v = visible.json()
    assert "pending_hitl" not in str(v)
    assert all(m["role"] in {"cliente", "gerente"} for m in v["messages"])
    assert any(
        "dictado por el despacho" in (m["content"] or "").lower()
        for m in v["messages"]
        if m["role"] == "cliente"
    )

    approve = client.post(
        f"/abogado/cliente-drafts/{draft_id}/approve",
        json={"revisor": "abogada", "edited_text": "Respuesta aprobada tras impersonación."},
    )
    assert approve.status_code == 200, approve.text

    after = client.get(
        "/cliente/messages", params={"cliente_session_id": "victima-impersonate"}
    )
    texts = [m["content"] for m in after.json()["messages"] if m["role"] == "gerente"]
    assert any("impersonación" in t.lower() or "aprobada" in t.lower() for t in texts)


def test_client_never_sees_junta(repo, monkeypatch):
    _auth_off(monkeypatch)
    from src.main import app
    from src.services import triple_chat as tc

    client = TestClient(app)
    client.post(
        "/cliente/start",
        json={
            "nombre": "María",
            "consent_1581": True,
            "cliente_session_id": "no-junta",
            "lawyer_session_id": "web:abogada",
        },
    )
    tc.append_internal_transcript(
        session_id="web:abogada",
        from_actor="gerente",
        to_actor="especialista:analista_evidencia",
        pedido="secreto junta",
        respuesta="hallazgo interno",
    )
    msgs = client.get("/cliente/messages", params={"cliente_session_id": "no-junta"})
    blob = str(msgs.json()).lower()
    assert "junta" not in blob
    assert "secreto junta" not in blob
    assert "hallazgo interno" not in blob
    assert "especialista" not in blob
