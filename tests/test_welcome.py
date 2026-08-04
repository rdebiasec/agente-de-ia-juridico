"""Saludo de bienvenida del escritorio abogado (TZ del despacho)."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from src.services.welcome import (
    DEFAULT_DESPACHO_TZ,
    WELCOME_DISPLAY_NAME,
    greeting_for_hour,
    lawyer_welcome_payload,
    normalize_despacho_tz,
    resolve_despacho_tz,
)


@pytest.mark.parametrize(
    "hour,expected",
    [
        (5, "Buenos días"),
        (11, "Buenos días"),
        (12, "Buenas tardes"),
        (18, "Buenas tardes"),
        (19, "Buenas noches"),
        (0, "Buenas noches"),
        (4, "Buenas noches"),
    ],
)
def test_greeting_for_hour(hour: int, expected: str):
    assert greeting_for_hour(hour) == expected


def test_normalize_despacho_tz_defaults_and_supported():
    assert normalize_despacho_tz(None) == DEFAULT_DESPACHO_TZ
    assert normalize_despacho_tz("") == DEFAULT_DESPACHO_TZ
    assert normalize_despacho_tz("America/Bogota") == "America/Bogota"
    assert normalize_despacho_tz("America/New_York") == "America/New_York"
    assert normalize_despacho_tz("Not/AZone") == DEFAULT_DESPACHO_TZ


def test_resolve_despacho_tz_agent_tz_override(monkeypatch):
    monkeypatch.setenv("AGENT_TZ", "America/New_York")
    monkeypatch.delenv("DESPACHO_TZ", raising=False)
    assert resolve_despacho_tz() == "America/New_York"


def test_lawyer_welcome_morning_bogota():
    now = datetime(2026, 8, 3, 10, 30, tzinfo=ZoneInfo("America/Bogota"))
    payload = lawyer_welcome_payload(now=now, tz_name="America/Bogota")
    assert payload["display_name"] == WELCOME_DISPLAY_NAME
    assert payload["greeting"] == "Buenos días"
    assert payload["message"] == (
        "Buenos días. Soy el Coordinador del Caso, "
        "asistente de IA penal del despacho."
    )
    assert "cronología" not in payload["message"].lower()
    assert "¿En qué punto" not in payload["message"]


def test_lawyer_welcome_afternoon_and_night():
    tarde = datetime(2026, 8, 3, 15, 0, tzinfo=ZoneInfo("America/Bogota"))
    noche = datetime(2026, 8, 3, 21, 0, tzinfo=ZoneInfo("America/Bogota"))
    assert lawyer_welcome_payload(now=tarde, tz_name="America/Bogota")["greeting"] == (
        "Buenas tardes"
    )
    assert lawyer_welcome_payload(now=noche, tz_name="America/Bogota")["greeting"] == (
        "Buenas noches"
    )


def test_desk_welcome_endpoint():
    from fastapi.testclient import TestClient

    from src.main import app

    client = TestClient(app)
    res = client.get("/api/desk/welcome")
    assert res.status_code == 200
    data = res.json()
    assert data["display_name"] == "Coordinador del Caso"
    assert "asistente de IA penal" in data["message"]
    assert data["greeting"] in {"Buenos días", "Buenas tardes", "Buenas noches"}
    assert isinstance(data["tz"], str) and data["tz"]
