"""F4 P0 — defaults seguros de auth y blueprint de producción."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from src.auth.dev import audit_login_required
from src.config import Settings


def test_settings_field_defaults_require_auth():
    """Defaults de código (sin .env): auth ON; open-access OFF."""
    assert Settings.model_fields["web_auth_enabled"].default is True
    assert Settings.model_fields["audit_require_login"].default is True
    assert Settings.model_fields["dev_auto_login"].default is False


def test_audit_login_forced_on_render_even_if_opt_out(monkeypatch):
    monkeypatch.setenv("RENDER", "true")
    settings = SimpleNamespace(audit_require_login=False, session_cookie_secure=False)
    assert audit_login_required(settings) is True  # type: ignore[arg-type]


def test_audit_login_local_opt_out_allowed(monkeypatch):
    monkeypatch.delenv("RENDER", raising=False)
    settings = SimpleNamespace(audit_require_login=False, session_cookie_secure=False)
    assert audit_login_required(settings) is False  # type: ignore[arg-type]


def test_audit_login_forced_when_session_cookie_secure(monkeypatch):
    monkeypatch.delenv("RENDER", raising=False)
    settings = SimpleNamespace(audit_require_login=False, session_cookie_secure=True)
    assert audit_login_required(settings) is True  # type: ignore[arg-type]


def test_render_yaml_requires_web_and_audit_auth():
    text = Path("render.yaml").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert (
        '      - key: WEB_AUTH_ENABLED\n'
        '        value: "true"'
    ) in text
    assert (
        '      - key: AUDIT_REQUIRE_LOGIN\n'
        '        value: "true"'
    ) in text
    assert (
        '      - key: DEV_AUTO_LOGIN\n'
        '        value: "false"'
    ) in text
    assert (
        '      - key: WEB_AUTH_ENABLED\n'
        '        value: "false"'
    ) not in text
