"""Fase 3: front-office /cliente + HITL visible en desk (solo local/dev)."""

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


def test_cliente_static_assets_exist():
    assert Path("static/desk/cliente.html").is_file()
    assert Path("static/cliente.js").is_file()
    assert Path("static/cliente.css").is_file()
    html = Path("static/desk/cliente.html").read_text(encoding="utf-8")
    assert "Ley 1581" in html
    assert "Coordinador del Caso" in html
    assert "TriageResult" not in html
    js = Path("static/cliente.js").read_text(encoding="utf-8")
    assert "/cliente/chat" in js
    assert "/cliente/messages" in js
    assert "plan" not in js.lower() or "plan propuesto" not in js.lower()


def test_abogado_has_cliente_inbox_slot():
    html = Path("static/desk/abogado.html").read_text(encoding="utf-8")
    assert 'id="tab-cliente-inbox"' in html
    assert "Respuestas al cliente" in html
    firma = Path("static/firma.js").read_text(encoding="utf-8")
    assert "/abogado/cliente-inbox" in firma
    assert "cliente-drafts" in firma


def test_e2e_cliente_to_approve_to_visible(repo, monkeypatch):
    from src.config import get_settings

    monkeypatch.setenv("WEB_AUTH_ENABLED", "false")
    monkeypatch.setenv("SITE_PASSWORD", "")
    monkeypatch.setenv("IP_ALLOWLIST_ENABLED", "false")
    get_settings.cache_clear()

    from src.main import app

    client = TestClient(app)

    page = client.get("/cliente")
    assert page.status_code == 200
    assert "Coordinador del Caso" in page.text

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
    assert before.status_code == 200
    roles = [m["role"] for m in before.json()["messages"]]
    assert roles == ["cliente"]

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
    gerente = [m for m in after.json()["messages"] if m["role"] == "gerente"]
    assert gerente
    assert "seguimiento" in gerente[0]["content"].lower()
