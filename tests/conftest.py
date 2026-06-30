"""Fixtures compartidos — desactiva auth web salvo en tests/test_auth.py."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def disable_web_auth_by_default(monkeypatch, request):
    if request.module.__name__.endswith("test_auth"):
        yield
        return

    monkeypatch.setenv("SITE_PASSWORD", "")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.delenv("RENDER", raising=False)
    from src.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
