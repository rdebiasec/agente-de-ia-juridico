"""Twilio SMS para alertas de plazos (no-op sin credenciales)."""

from __future__ import annotations

from datetime import date, timedelta

from src.services.twilio_notify import (
    formatear_alerta_plazos,
    normalizar_e164,
    notificar_texto_sms,
    twilio_habilitado,
)
from src.storage.models import Deadline


def test_normalizar_e164_colombia():
    assert normalizar_e164("3001234567") == "+573001234567"
    assert normalizar_e164("+573001234567") == "+573001234567"
    assert normalizar_e164("invalid") is None


def test_formatear_alerta_plazos():
    hoy = date.today()
    vencidos = [Deadline(descripcion="Impugnacion tutela", fecha_limite=hoy - timedelta(days=1))]
    proximos = [Deadline(descripcion="Traslado", fecha_limite=hoy + timedelta(days=2))]
    texto = formatear_alerta_plazos(vencidos, proximos, referencia=hoy)
    assert "VENCIDO: Impugnacion tutela" in texto
    assert "Por vencer en 2 dia(s): Traslado" in texto


def test_twilio_noop_sin_credenciales(monkeypatch):
    monkeypatch.delenv("TWILIO_ACCOUNT_SID", raising=False)
    monkeypatch.delenv("TWILIO_AUTH_TOKEN", raising=False)
    from src.config import get_settings

    get_settings.cache_clear()
    assert twilio_habilitado() is False
    assert notificar_texto_sms("Hola") is None


def test_notificar_texto_sms_mock(monkeypatch):
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "AC" + "a" * 32)
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "secret")
    monkeypatch.setenv("TWILIO_FROM_NUMBER", "+15551234567")
    monkeypatch.setenv("TWILIO_ALERT_TO", "3001234567")
    monkeypatch.delenv("TWILIO_STATUS_CALLBACK", raising=False)
    monkeypatch.delenv("RENDER_EXTERNAL_URL", raising=False)
    from src.config import get_settings

    get_settings.cache_clear()

    class FakeMessage:
        sid = "SM" + "b" * 32

    class FakeMessages:
        def create(self, **kwargs):
            assert kwargs["to"] == "+573001234567"
            assert kwargs["from_"] == "+15551234567"
            assert "Alerta" in kwargs["body"]
            assert "status_callback" not in kwargs
            return FakeMessage()

    class FakeClient:
        messages = FakeMessages()

    monkeypatch.setattr("twilio.rest.Client", lambda *a, **k: FakeClient())
    sid = notificar_texto_sms("Alerta de terminos procesales\nVENCIDO: test")
    assert sid == "SM" + "b" * 32
    get_settings.cache_clear()
