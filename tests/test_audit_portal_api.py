"""Tests API del portal de auditoría."""

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
    monkeypatch.delenv("RENDER", raising=False)
    from src.config import get_settings

    get_settings.cache_clear()
    reset_repository()


async def _login(client, email: str, *, pin: str = "123456", setup: bool = True):
    if setup:
        body = {
            "email": email,
            "password": "audit-test-secret-pass",
            "new_pin": pin,
            "accept_privacy": True,
            "accept_sensitive_data": True,
        }
    else:
        body = {"email": email, "password": "audit-test-secret-pass", "pin": pin}
    return await client.post("/api/audit/login", json=body)


@pytest.mark.asyncio
async def test_audit_policy_and_session(monkeypatch):
    _audit_env(monkeypatch)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/api/audit/policy")
        assert r.status_code == 200
        assert r.json()["version"] == "2026-07-07"

        r = await client.get("/api/audit/session")
        assert r.json()["authenticated"] is False

        r = await _login(client, "abogada@despacho.com")
        assert r.status_code == 200

        r = await client.get("/api/audit/session")
        assert r.json()["authenticated"] is True


@pytest.mark.asyncio
async def test_audit_progress_crud(monkeypatch):
    _audit_env(monkeypatch)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await _login(client, "prog@despacho.com")
        assert r.status_code == 200

        r = await client.get("/api/audit/progress")
        assert r.status_code == 404

        payload = {
            "version": 3,
            "guardrails": {"g1": {"status": "APROBADO", "reason": "", "solution": ""}},
            "agentes": {},
            "pasos": {},
        }
        r = await client.put("/api/audit/progress", json=payload)
        assert r.status_code == 200

        r = await client.get("/api/audit/progress")
        assert r.json()["guardrails"]["g1"]["status"] == "APROBADO"

        guias_payload = {
            "version": 4,
            "guardrails": {},
            "agentes": {},
            "guias": {
                "extraer_hechos_relevantes::instruccion": {
                    "status": "APROBADO",
                    "reason": "",
                    "solution": "",
                }
            },
            "pasos": {},
        }
        r = await client.put("/api/audit/progress", json=guias_payload)
        assert r.status_code == 200
        r = await client.get("/api/audit/progress")
        assert r.json()["guias"]["extraer_hechos_relevantes::instruccion"]["status"] == "APROBADO"

        r = await client.delete("/api/audit/progress")
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_audit_progress_rejects_empty_overwrite(monkeypatch):
    _audit_env(monkeypatch)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await _login(client, "wipe@despacho.com")
        assert r.status_code == 200

        payload = {
            "version": 4,
            "guardrails": {"g1": {"status": "APROBADO", "reason": "", "solution": ""}},
            "agentes": {},
            "guias": {},
            "pasos": {},
        }
        r = await client.put("/api/audit/progress", json=payload)
        assert r.status_code == 200

        empty = {
            "version": 4,
            "guardrails": {},
            "agentes": {},
            "guias": {},
            "pasos": {},
        }
        r = await client.put("/api/audit/progress", json=empty)
        assert r.status_code == 409

        r = await client.get("/api/audit/progress")
        assert r.json()["guardrails"]["g1"]["status"] == "APROBADO"


@pytest.mark.asyncio
async def test_audit_unavailable_without_site_password(monkeypatch):
    monkeypatch.setenv("SITE_PASSWORD", "")
    from src.config import get_settings

    get_settings.cache_clear()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/api/audit/login",
            json={"email": "a@b.com", "password": "x"},
        )
        assert r.status_code == 503
