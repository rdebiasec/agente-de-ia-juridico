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
    if request.module.__name__.endswith("test_auth") or request.module.__name__.endswith(
        "test_audit_portal_api"
    ) or request.module.__name__.endswith("test_compliance") or request.module.__name__.endswith(
        "test_access_control"
    ) or request.module.__name__.endswith("test_fase3_plan_product"):
        yield
        return

    monkeypatch.setenv("SITE_PASSWORD", "")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.delenv("RENDER", raising=False)
    from src.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
