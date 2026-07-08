"""Tests de cumplimiento — PIN, consentimiento y API de auditoría."""

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
        "guardrails": {"g1": {"status": "APROBADO", "reason": "", "solution": ""}},
        "agentes": {},
        "pasos": {},
        "custom": None,
    }


@pytest.mark.asyncio
async def test_audit_login_requires_pin_setup_and_consent(monkeypatch):
    _audit_env(monkeypatch)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/api/audit/prelogin",
            json={"email": "nueva@despacho.com", "password": "audit-test-secret-pass"},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["needs_pin_setup"] is True
        assert data["needs_consent"] is True

        r = await client.post(
            "/api/audit/login",
            json={
                "email": "nueva@despacho.com",
                "password": "audit-test-secret-pass",
                "new_pin": "123456",
                "accept_privacy": True,
                "accept_sensitive_data": True,
            },
        )
        assert r.status_code == 200
        assert "audit_session" in r.cookies

        r = await client.post(
            "/api/audit/login",
            json={
                "email": "nueva@despacho.com",
                "password": "audit-test-secret-pass",
                "pin": "999999",
            },
        )
        assert r.status_code == 401

        r = await client.post(
            "/api/audit/login",
            json={
                "email": "nueva@despacho.com",
                "password": "audit-test-secret-pass",
                "pin": "123456",
            },
        )
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_audit_progress_history_and_isolation(monkeypatch):
    _audit_env(monkeypatch)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for email, pin in (("uno@despacho.com", "111111"), ("dos@despacho.com", "222222")):
            r = await client.post(
                "/api/audit/login",
                json={
                    "email": email,
                    "password": "audit-test-secret-pass",
                    "new_pin": pin,
                    "accept_privacy": True,
                    "accept_sensitive_data": True,
                },
            )
            assert r.status_code == 200

        r = await client.post(
            "/api/audit/login",
            json={"email": "uno@despacho.com", "password": "audit-test-secret-pass", "pin": "111111"},
        )
        cookies_a = dict(r.cookies)
        r = await client.put("/api/audit/progress", json=_sample_payload(), cookies=cookies_a)
        assert r.status_code == 200

        r = await client.post(
            "/api/audit/login",
            json={"email": "dos@despacho.com", "password": "audit-test-secret-pass", "pin": "222222"},
        )
        cookies_b = dict(r.cookies)
        r = await client.get("/api/audit/progress", cookies=cookies_b)
        assert r.status_code == 404


@pytest.mark.asyncio
async def test_web_consent_endpoint(monkeypatch):
    _audit_env(monkeypatch)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/api/compliance/web-consent",
            json={"username": "despacho", "accept_privacy": True, "accept_sensitive_data": True},
        )
        assert r.status_code == 200
        repo = get_repository()
        assert repo.has_valid_compliance_consent(
            "web:despacho", context="web_chat", policy_version="2026-07-07"
        )


@pytest.mark.asyncio
async def test_legal_pages_public(monkeypatch):
    _audit_env(monkeypatch)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/legal/privacidad")
        assert r.status_code == 200
        assert "Ley 1581" in r.text
        r = await client.get("/legal/tratamiento-datos-casos")
        assert r.status_code == 200
        assert "datos de casos" in r.text.lower()
