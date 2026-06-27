"""Fixtures compartidos — desactiva auth web salvo en tests/test_auth.py."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def disable_web_auth_by_default(monkeypatch, request):
    monkeypatch.setenv("ACTIVE_PHASE", "1")
    if request.module.__name__.endswith("test_auth"):
        yield
        return

    monkeypatch.setenv("SITE_PASSWORD", "")
    from src.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
