"""Tests de autenticación web por contraseña."""

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_auth_disabled_when_no_password(monkeypatch):
    from src.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("SITE_PASSWORD", "")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        status = await client.get("/auth/status")
        assert status.status_code == 200
        assert status.json()["auth_enabled"] is False
        assert status.json()["authenticated"] is True

        chat = await client.post("/chat", json={"message": "hola", "user_id": "t"})
        assert chat.status_code == 200

    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_login_logout_and_protected_routes(monkeypatch):
    from src.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("SITE_PASSWORD", "test-secret-pass")
    monkeypatch.setenv("SITE_USERNAME", "despacho")
    monkeypatch.setenv("SESSION_SECRET", "test-session-secret-key-32chars")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        unauth = await client.post("/chat", json={"message": "hola", "user_id": "t"})
        assert unauth.status_code == 401

        bad = await client.post(
            "/auth/login",
            json={"username": "despacho", "password": "wrong"},
        )
        assert bad.status_code == 401

        login = await client.post(
            "/auth/login",
            json={"username": "despacho", "password": "test-secret-pass"},
        )
        assert login.status_code == 200
        cookie = login.cookies.get("agente_session")
        assert cookie

        authed = await client.post(
            "/chat",
            json={"message": "hola", "user_id": "t"},
            cookies={"agente_session": cookie},
        )
        assert authed.status_code == 200

        heartbeat = await client.post("/auth/heartbeat", cookies={"agente_session": cookie})
        assert heartbeat.status_code == 200

        logout = await client.post("/auth/logout", cookies={"agente_session": cookie})
        assert logout.status_code == 200
        set_cookie = logout.headers.get("set-cookie", "")
        assert "agente_session=" in set_cookie
        assert "Max-Age=0" in set_cookie or "expires=" in set_cookie.lower()

        again = await client.post("/chat", json={"message": "hola", "user_id": "t"})
        assert again.status_code == 401

    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_login_page_has_chrome_friendly_form():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/login")
    assert r.status_code == 200
    assert 'method="post"' in r.text
    assert 'action="/auth/login"' in r.text
    assert 'name="username"' in r.text
    assert 'name="password"' in r.text
    assert 'autocomplete="username"' in r.text
    assert 'autocomplete="current-password"' in r.text
    assert 'name="login"' in r.text
    assert "auth-logout-btn" not in r.text


@pytest.mark.asyncio
async def test_unauthenticated_root_redirects_to_login(monkeypatch):
    from src.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("SITE_PASSWORD", "test-secret-pass")
    monkeypatch.setenv("SITE_USERNAME", "despacho")
    monkeypatch.setenv("SESSION_SECRET", "test-session-secret-key-32chars")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=False) as client:
        r = await client.get("/")
    assert r.status_code == 302
    assert r.headers.get("location") == "/login"

    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_form_login_redirects_and_sets_cookie(monkeypatch):
    from src.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("SITE_PASSWORD", "test-secret-pass")
    monkeypatch.setenv("SITE_USERNAME", "despacho")
    monkeypatch.setenv("SESSION_SECRET", "test-session-secret-key-32chars")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=False) as client:
        bad = await client.post(
            "/auth/login",
            data={"username": "despacho", "password": "wrong"},
        )
        assert bad.status_code == 303
        assert bad.headers.get("location") == "/login?login_error=1"
        assert bad.cookies.get("agente_session") is None

        ok = await client.post(
            "/auth/login",
            data={"username": "despacho", "password": "test-secret-pass"},
        )
        assert ok.status_code == 303
        assert ok.headers.get("location") == "/"
        cookie = ok.cookies.get("agente_session")
        assert cookie

        authed = await client.post(
            "/chat",
            json={"message": "hola", "user_id": "t"},
            cookies={"agente_session": cookie},
        )
        assert authed.status_code == 200

    get_settings.cache_clear()
