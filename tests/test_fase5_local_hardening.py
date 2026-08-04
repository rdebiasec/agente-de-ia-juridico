"""Fase 5 local: cookie cliente ≠ abogado; smoke sin prod."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.auth.cliente_session import (
    CLIENTE_COOKIE_NAME,
    create_cliente_session_token,
    cliente_subject_from_token,
)
from src.auth.gate import COOKIE_NAME as LAWYER_COOKIE
from src.storage.memory import InMemoryRepository


def test_cliente_and_lawyer_cookies_are_different_names():
    assert CLIENTE_COOKIE_NAME != LAWYER_COOKIE
    assert CLIENTE_COOKIE_NAME == "lexiatek_cliente_session"
    assert LAWYER_COOKIE == "agente_session"


def test_cliente_token_roundtrip():
    token = create_cliente_session_token("secret-for-tests-32chars!!", subject_id="victima-x")
    assert cliente_subject_from_token("secret-for-tests-32chars!!", token) == "victima-x"
    assert cliente_subject_from_token("secret-for-tests-32chars!!", None) is None


@pytest.fixture()
def repo(monkeypatch):
    mem = InMemoryRepository()
    monkeypatch.setattr("src.storage.get_repository", lambda: mem)
    monkeypatch.setattr("src.services.triple_chat.get_repository", lambda: mem)
    return mem


def test_cliente_chat_sets_cliente_cookie_not_lawyer(repo, monkeypatch):
    from src.config import get_settings

    monkeypatch.setenv("WEB_AUTH_ENABLED", "false")
    monkeypatch.setenv("SITE_PASSWORD", "")
    monkeypatch.setenv("IP_ALLOWLIST_ENABLED", "false")
    monkeypatch.setenv("SESSION_SECRET", "test-session-secret-key-32chars!!")
    get_settings.cache_clear()

    from src.main import app

    client = TestClient(app)
    res = client.post(
        "/cliente/chat",
        json={
            "message": "Hola despacho",
            "cliente_session_id": "fase5-v",
            "lawyer_session_id": "web:abogada",
        },
    )
    assert res.status_code == 200, res.text
    # TestClient guarda cookies; debe existir la de cliente, no confundirse con abogado.
    assert CLIENTE_COOKIE_NAME in client.cookies or CLIENTE_COOKIE_NAME in (
        res.headers.get("set-cookie") or ""
    )
    assert LAWYER_COOKIE not in (res.headers.get("set-cookie") or "")

    info = client.get("/cliente/session")
    assert info.status_code == 200
    body = info.json()
    assert body["cookies_are_separate"] is True
    assert body["cliente_cookie_name"] == CLIENTE_COOKIE_NAME


def test_runbook_mentions_cliente_front_office():
    text = Path("docs/operaciones/RUNBOOK_CUMPLIMIENTO_1581.md").read_text(encoding="utf-8")
    assert "/cliente" in text
    assert "lexiatek_cliente_session" in text
    assert "agente_session" in text


def test_smoke_script_exists():
    assert Path("scripts/smoke_triple_chat_local.py").is_file()
