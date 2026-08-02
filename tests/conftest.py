"""Fixtures compartidos — desactiva auth web salvo en tests/test_auth.py."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def reset_rate_limits_between_tests():
    from src.middleware.rate_limit import reset_all_rate_limits

    reset_all_rate_limits()
    yield
    reset_all_rate_limits()


@pytest.fixture(autouse=True)
def disable_web_auth_by_default(monkeypatch, request):
    auth_modules = (
        "test_auth",
        "test_audit_portal_api",
        "test_compliance",
        "test_access_control",
        "test_fase3_plan_product",
    )
    if any(request.module.__name__.endswith(name) for name in auth_modules):
        # Estos tests ejercen el gate; forzar ON aunque .env local lo tenga en false.
        monkeypatch.setenv("WEB_AUTH_ENABLED", "true")
        from src.config import get_settings

        get_settings.cache_clear()
        yield
        get_settings.cache_clear()
        return

    monkeypatch.setenv("SITE_PASSWORD", "")
    monkeypatch.setenv("WEB_AUTH_ENABLED", "false")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.delenv("RENDER", raising=False)
    from src.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
