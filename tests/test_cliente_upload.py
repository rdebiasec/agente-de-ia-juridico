"""Upload de adjuntos del canal víctima al expediente."""

from __future__ import annotations

import io

import pytest
from fastapi.testclient import TestClient

from src.storage.memory import InMemoryRepository


@pytest.fixture()
def repo(monkeypatch):
    mem = InMemoryRepository()
    monkeypatch.setattr("src.storage.get_repository", lambda: mem)
    monkeypatch.setattr("src.services.triple_chat.get_repository", lambda: mem)
    monkeypatch.setattr("src.services.cliente_uploads.get_repository", lambda: mem)
    return mem


def _auth_off(monkeypatch):
    from src.config import get_settings

    monkeypatch.setenv("WEB_AUTH_ENABLED", "false")
    monkeypatch.setenv("SITE_PASSWORD", "")
    monkeypatch.setenv("IP_ALLOWLIST_ENABLED", "false")
    get_settings.cache_clear()


def test_cliente_upload_lands_in_expediente_and_thread(repo, monkeypatch, tmp_path):
    _auth_off(monkeypatch)
    monkeypatch.setattr("src.services.cliente_uploads.UPLOAD_ROOT", tmp_path)

    from src.main import app

    client = TestClient(app)
    start = client.post(
        "/cliente/start",
        json={
            "nombre": "Ector",
            "consent_1581": True,
            "cliente_session_id": "upload-victima-1",
            "lawyer_session_id": "web:abogada",
        },
    )
    assert start.status_code == 200, start.text

    files = {"file": ("prueba.txt", io.BytesIO(b"captura de chat relevante"), "text/plain")}
    data = {
        "cliente_session_id": "upload-victima-1",
        "lawyer_session_id": "web:abogada",
    }
    up = client.post("/cliente/upload", data=data, files=files)
    assert up.status_code == 200, up.text
    body = up.json()
    assert body["attachment_id"]
    assert "prueba.txt" in body["filename"]

    msgs = client.get(
        "/cliente/messages", params={"cliente_session_id": "upload-victima-1"}
    )
    assert msgs.status_code == 200
    contents = [m["content"] for m in msgs.json()["messages"]]
    assert any("📎" in c and "prueba" in c.lower() for c in contents)

    desk = client.get("/abogado/cliente-thread", params={"session_id": "web:abogada"})
    assert desk.status_code == 200
    desk_body = desk.json()
    assert desk_body.get("anexos_cliente")
    assert desk_body["anexos_cliente"][-1]["id"] == body["attachment_id"]

    dl = client.get(
        f"/abogado/cliente-attachments/{body['attachment_id']}",
        params={"session_id": "web:abogada"},
    )
    assert dl.status_code == 200
    assert b"captura de chat relevante" in dl.content


def test_cliente_upload_rejects_bad_type(repo, monkeypatch, tmp_path):
    _auth_off(monkeypatch)
    monkeypatch.setattr("src.services.cliente_uploads.UPLOAD_ROOT", tmp_path)
    from src.main import app

    client = TestClient(app)
    client.post(
        "/cliente/start",
        json={
            "nombre": "Ana",
            "consent_1581": True,
            "cliente_session_id": "upload-bad",
            "lawyer_session_id": "web:abogada",
        },
    )
    files = {"file": ("malware.exe", io.BytesIO(b"xx"), "application/octet-stream")}
    up = client.post(
        "/cliente/upload",
        data={"cliente_session_id": "upload-bad", "lawyer_session_id": "web:abogada"},
        files=files,
    )
    assert up.status_code == 400
