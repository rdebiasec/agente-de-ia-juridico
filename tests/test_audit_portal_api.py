"""Tests API del portal de auditoría — login y persistencia por correo."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.storage import get_repository, reset_repository


def _audit_env(monkeypatch) -> None:
    monkeypatch.setenv("SITE_PASSWORD", "audit-test-secret-pass")
    monkeypatch.setenv("SITE_USERNAME", "despacho")
    monkeypatch.setenv("SESSION_SECRET", "audit-test-session-secret-key-32chars")
    monkeypatch.setenv("SESSION_COOKIE_SECURE", "false")
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.delenv("RENDER", raising=False)
    from src.config import get_settings

    get_settings.cache_clear()
    reset_repository()


def _sample_payload() -> dict:
    return {
        "version": 3,
        "savedAt": "2026-07-06T12:00:00.000Z",
        "catalogGeneratedAt": "2026-07-06 12:00 UTC",
        "guardrails": {"g1": {"status": "APROBADO", "reason": "", "solution": ""}},
        "agentes": {},
        "pasos": {},
        "custom": None,
    }


@pytest.mark.asyncio
async def test_audit_login_session_and_progress(monkeypatch):
    _audit_env(monkeypatch)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/api/audit/session")
        assert r.status_code == 200
        assert r.json()["authenticated"] is False

        r = await client.post(
            "/api/audit/login",
            json={"email": "Abogada@Despacho.com", "password": "audit-test-secret-pass"},
        )
        assert r.status_code == 200
        assert r.json()["email"] == "abogada@despacho.com"
        assert "audit_session" in r.cookies

        r = await client.get("/api/audit/session")
        assert r.status_code == 200
        data = r.json()
        assert data["authenticated"] is True
        assert data["email"] == "abogada@despacho.com"

        r = await client.get("/api/audit/progress")
        assert r.status_code == 404

        payload = _sample_payload()
        r = await client.put("/api/audit/progress", json=payload)
        assert r.status_code == 200
        assert r.json()["email"] == "abogada@despacho.com"

        r = await client.get("/api/audit/progress")
        assert r.status_code == 200
        loaded = r.json()
        assert loaded["guardrails"]["g1"]["status"] == "APROBADO"

        r = await client.delete("/api/audit/progress")
        assert r.status_code == 200

        r = await client.get("/api/audit/progress")
        assert r.status_code == 404


@pytest.mark.asyncio
async def test_audit_progress_isolated_between_emails(monkeypatch):
    _audit_env(monkeypatch)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client_a:
        r = await client_a.post(
            "/api/audit/login",
            json={"email": "uno@despacho.com", "password": "audit-test-secret-pass"},
        )
        assert r.status_code == 200

        r = await client_a.put("/api/audit/progress", json=_sample_payload())
        assert r.status_code == 200

        r = await client_a.get("/api/audit/progress")
        assert r.status_code == 200

    async with AsyncClient(transport=transport, base_url="http://test") as client_b:
        r = await client_b.post(
            "/api/audit/login",
            json={"email": "dos@despacho.com", "password": "audit-test-secret-pass"},
        )
        assert r.status_code == 200

        r = await client_b.get("/api/audit/progress")
        assert r.status_code == 404


@pytest.mark.asyncio
async def test_audit_login_rejects_bad_password(monkeypatch):
    _audit_env(monkeypatch)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/api/audit/login",
            json={"email": "abogada@despacho.com", "password": "wrong-password"},
        )
        assert r.status_code == 401


@pytest.mark.asyncio
async def test_audit_login_rejects_invalid_email(monkeypatch):
    _audit_env(monkeypatch)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/api/audit/login",
            json={"email": "no-es-correo", "password": "audit-test-secret-pass"},
        )
        assert r.status_code == 400


@pytest.mark.asyncio
async def test_audit_unavailable_without_site_password(monkeypatch):
    monkeypatch.setenv("SITE_PASSWORD", "")
    from src.config import get_settings

    get_settings.cache_clear()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/api/audit/session")
        assert r.status_code == 200
        assert r.json()["auth_enabled"] is False

        r = await client.post(
            "/api/audit/login",
            json={"email": "abogada@despacho.com", "password": "anything"},
        )
        assert r.status_code == 503


@pytest.mark.asyncio
async def test_audit_logout_clears_session(monkeypatch):
    _audit_env(monkeypatch)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/api/audit/login",
            json={"email": "abogada@despacho.com", "password": "audit-test-secret-pass"},
        )
        assert r.status_code == 200

        r = await client.post("/api/audit/logout")
        assert r.status_code == 200

        r = await client.get("/api/audit/session")
        assert r.json()["authenticated"] is False


@pytest.mark.asyncio
async def test_auditoria_static_mount_when_dist_exists(monkeypatch):
    _audit_env(monkeypatch)
    from pathlib import Path

    dist = Path(__file__).resolve().parents[1] / "audit-portal" / "dist"
    if not dist.is_dir():
        pytest.skip("audit-portal/dist no generado — ejecute scripts/generar_audit_portal.py")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=True) as client:
        r = await client.get("/auditoria/")
        assert r.status_code == 200
        assert "Auditoría de Instrucciones" in r.text
