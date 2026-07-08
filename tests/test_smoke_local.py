"""Smoke HTTP local — requiere servidor en SMOKE_BASE_URL (orquestador capa 5)."""

from __future__ import annotations

import os
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]
SMOKE_BASE = os.environ.get("SMOKE_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
SMOKE_PASSWORD = os.environ.get("SMOKE_SITE_PASSWORD", os.environ.get("SITE_PASSWORD", "test-secret-pass"))
SMOKE_USERNAME = os.environ.get("SMOKE_SITE_USERNAME", os.environ.get("SITE_USERNAME", "despacho"))
SMOKE_TIMEOUT = float(os.environ.get("SMOKE_TIMEOUT", "30"))


def _server_reachable() -> bool:
    try:
        r = httpx.get(f"{SMOKE_BASE}/health", timeout=5.0)
        return r.status_code == 200
    except (httpx.HTTPError, OSError):
        return False


pytestmark = [
    pytest.mark.smoke,
    pytest.mark.skipif(not _server_reachable(), reason=f"Servidor no disponible en {SMOKE_BASE}"),
]


@pytest.fixture(scope="module")
def base_url() -> str:
    return SMOKE_BASE


@pytest.fixture(scope="module")
def web_session(base_url: str) -> dict[str, str]:
    with httpx.Client(base_url=base_url, timeout=SMOKE_TIMEOUT, follow_redirects=True) as client:
        status = client.get("/auth/status")
        if status.status_code == 200 and not status.json().get("auth_enabled"):
            return {}
        login = client.post(
            "/auth/login",
            json={"username": SMOKE_USERNAME, "password": SMOKE_PASSWORD},
        )
        assert login.status_code == 200, login.text
        cookie = login.cookies.get("agente_session")
        assert cookie
        return {"agente_session": cookie}


@pytest.fixture(scope="module")
def audit_cookies(base_url: str) -> dict[str, str]:
    email = os.environ.get("SMOKE_AUDIT_EMAIL", "smoke@despacho.com")
    with httpx.Client(base_url=base_url, timeout=SMOKE_TIMEOUT) as client:
        pre = client.post(
            "/api/audit/prelogin",
            json={"email": email, "password": SMOKE_PASSWORD},
        )
        assert pre.status_code == 200, pre.text
        body: dict = {
            "email": email,
            "password": SMOKE_PASSWORD,
            "accept_privacy": True,
            "accept_sensitive_data": True,
        }
        if pre.json().get("needs_pin_setup"):
            body["new_pin"] = os.environ.get("SMOKE_AUDIT_PIN", "654321")
        else:
            body["pin"] = os.environ.get("SMOKE_AUDIT_PIN", "654321")
        login = client.post("/api/audit/login", json=body)
        assert login.status_code == 200, login.text
        audit_cookie = login.cookies.get("audit_session")
        assert audit_cookie
        return {"audit_session": audit_cookie}


def test_health_ok(base_url: str):
    r = httpx.get(f"{base_url}/health", timeout=SMOKE_TIMEOUT)
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") in {"ok", "healthy", True} or "ok" in str(data).lower()


def test_login_page(base_url: str):
    r = httpx.get(f"{base_url}/login", timeout=SMOKE_TIMEOUT, follow_redirects=True)
    assert r.status_code == 200
    assert "password" in r.text.lower() or "contraseña" in r.text.lower() or "abogado" in r.text.lower()


def test_auditoria_static_has_auth_gate(base_url: str):
    r = httpx.get(f"{base_url}/auditoria/", timeout=SMOKE_TIMEOUT)
    assert r.status_code == 200
    assert "auth-gate" in r.text or "auth_gate" in r.text


def test_audit_login_and_progress(base_url: str, audit_cookies: dict[str, str]):
    with httpx.Client(base_url=base_url, timeout=SMOKE_TIMEOUT, cookies=audit_cookies) as client:
        session = client.get("/api/audit/session")
        assert session.status_code == 200
        assert session.json().get("authenticated") is True

        progress = client.get("/api/audit/progress")
        assert progress.status_code in {200, 404}


def test_audit_catalog_live(base_url: str):
    r = httpx.get(f"{base_url}/api/audit/catalog", timeout=SMOKE_TIMEOUT)
    assert r.status_code == 200
    data = r.json()
    assert len(data.get("skills") or []) == 90
    assert len(data.get("agentes") or []) == 11


def test_web_chat_with_trace(base_url: str, web_session: dict[str, str]):
    with httpx.Client(base_url=base_url, timeout=SMOKE_TIMEOUT, cookies=web_session) as client:
        r = client.post(
            "/chat",
            json={
                "message": "Necesito una cronología de hechos del expediente penal.",
                "channel": "web",
                "user_id": "smoke-runtime",
            },
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert "trace" in data
        assert data["trace"] is not None


def test_chat_plan_flow(base_url: str, web_session: dict[str, str]):
    with httpx.Client(base_url=base_url, timeout=SMOKE_TIMEOUT, cookies=web_session) as client:
        create = client.post(
            "/chat/plan",
            json={
                "message": "Cronología de hechos del caso para revisión.",
                "channel": "web",
                "user_id": "smoke-plan",
            },
        )
        assert create.status_code == 200, create.text
        plan_id = create.json().get("plan_id")
        assert plan_id

        detail = client.get(f"/chat/plan/{plan_id}")
        assert detail.status_code == 200

        approve = client.post(f"/chat/plan/{plan_id}/approve", json={"user_id": "smoke-plan"})
        assert approve.status_code == 200
