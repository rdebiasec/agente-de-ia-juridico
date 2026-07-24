"""API tests for config store save/restore."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.storage import reset_repository


def _audit_env(monkeypatch) -> None:
    monkeypatch.setenv("SITE_PASSWORD", "audit-test-secret-pass")
    monkeypatch.setenv("SITE_USERNAME", "despacho")
    monkeypatch.setenv("SESSION_SECRET", "audit-test-session-secret-key-32chars")
    monkeypatch.setenv("SESSION_COOKIE_SECURE", "false")
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setenv("AUDIT_CONFIG_WRITE_FILE", "0")
    monkeypatch.delenv("RENDER", raising=False)
    from src.config import get_settings

    get_settings.cache_clear()
    reset_repository()


async def _login(client, email: str = "editor@despacho.com"):
    body = {
        "email": email,
        "password": "audit-test-secret-pass",
        "new_pin": "123456",
        "accept_privacy": True,
        "accept_sensitive_data": True,
    }
    return await client.post("/api/audit/login", json=body)


@pytest.mark.asyncio
async def test_config_save_and_restore_api(monkeypatch):
    _audit_env(monkeypatch)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        assert (await _login(client)).status_code == 200

        save1 = await client.post(
            "/api/audit/config/save",
            json={
                "kind": "prompt",
                "key": "analista_calidad_juridica",
                "content": "Rol: calidad API v1\nMisión: test.",
                "expected_version": 0,
                "note": "api-v1",
            },
        )
        assert save1.status_code == 200, save1.text
        assert save1.json()["version"] == 1

        save2 = await client.post(
            "/api/audit/config/save",
            json={
                "kind": "prompt",
                "key": "analista_calidad_juridica",
                "content": "Rol: calidad API v2\nMisión: test.",
                "expected_version": 1,
            },
        )
        assert save2.status_code == 200
        assert save2.json()["version"] == 2

        got = await client.get("/api/audit/config/prompt/analista_calidad_juridica")
        assert got.status_code == 200
        assert "v2" in got.json()["content"]

        versions = await client.get(
            "/api/audit/config/prompt/analista_calidad_juridica/versions"
        )
        assert versions.status_code == 200
        assert len(versions.json()["versions"]) >= 2

        conflict = await client.post(
            "/api/audit/config/save",
            json={
                "kind": "prompt",
                "key": "analista_calidad_juridica",
                "content": "conflicto",
                "expected_version": 1,
            },
        )
        assert conflict.status_code == 409

        restore = await client.post(
            "/api/audit/config/prompt/analista_calidad_juridica/restore",
            json={"version": 1, "note": "rollback"},
        )
        assert restore.status_code == 200
        assert restore.json()["version"] == 3
        got2 = await client.get("/api/audit/config/prompt/analista_calidad_juridica")
        assert "v1" in got2.json()["content"]

        status = await client.get("/api/audit/config/status")
        assert status.status_code == 200
        assert "config_store" in status.json()
