"""OpenAPI/docs deshabilitados en Render/producción."""

from __future__ import annotations

import importlib

from fastapi.testclient import TestClient


def test_docs_disabled_when_render_env(monkeypatch):
    monkeypatch.setenv("RENDER", "true")
    monkeypatch.setenv("SITE_PASSWORD", "test-secret-pass-long")
    monkeypatch.setenv("SESSION_SECRET", "test-session-secret-key-32chars!!")
    monkeypatch.setenv("DEV_AUTO_LOGIN", "false")
    monkeypatch.setenv("SESSION_COOKIE_SECURE", "true")
    monkeypatch.delenv("DATABASE_URL", raising=False)

    import src.main as main

    importlib.reload(main)
    client = TestClient(main.app)
    assert client.get("/docs").status_code == 404
    assert client.get("/redoc").status_code == 404
    assert client.get("/openapi.json").status_code == 404


def test_docs_enabled_locally(monkeypatch):
    monkeypatch.delenv("RENDER", raising=False)
    monkeypatch.setenv("SITE_PASSWORD", "test-secret-pass-long")
    monkeypatch.setenv("SESSION_SECRET", "test-session-secret-key-32chars!!")
    monkeypatch.setenv("DEV_AUTO_LOGIN", "false")
    monkeypatch.setenv("SESSION_COOKIE_SECURE", "false")
    monkeypatch.delenv("DATABASE_URL", raising=False)

    import src.main as main

    importlib.reload(main)
    client = TestClient(main.app)
    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").status_code == 200
