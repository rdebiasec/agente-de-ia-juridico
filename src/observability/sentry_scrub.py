"""Scrub PII / datos de caso antes de enviar a Sentry (B15 / Ley 1581)."""

from __future__ import annotations

import re
from typing import Any

_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_PHONE_RE = re.compile(r"\b(?:\+?57[\s-]?)?(?:3\d{2}|60\d)[\s-]?\d{3}[\s-]?\d{4}\b")
_RADICADO_RE = re.compile(r"\b\d{15,23}\b")


def _scrub_text(value: str) -> str:
    text = _EMAIL_RE.sub("[email]", value)
    text = _PHONE_RE.sub("[telefono]", text)
    text = _RADICADO_RE.sub("[radicado]", text)
    # Conservador: no sustituir todos los números cortos (rompen IDs internos).
    return text


def _scrub_obj(obj: Any, depth: int = 0) -> Any:
    if depth > 6:
        return "[truncated]"
    if isinstance(obj, str):
        return _scrub_text(obj)
    if isinstance(obj, dict):
        out = {}
        for key, val in obj.items():
            key_l = str(key).lower()
            if key_l in {
                "message",
                "content",
                "input",
                "prompt",
                "system_prompt",
                "input_preview",
                "text",
                "body",
                "query",
                "expediente",
                "hechos",
            }:
                out[key] = _scrub_text(str(val)) if val is not None else val
            elif key_l in {"email", "user_email", "correo"}:
                out[key] = "[email]"
            else:
                out[key] = _scrub_obj(val, depth + 1)
        return out
    if isinstance(obj, list):
        return [_scrub_obj(item, depth + 1) for item in obj[:40]]
    return obj


def sentry_before_send(event: dict[str, Any], hint: dict[str, Any] | None = None) -> dict[str, Any] | None:
    """Callback Sentry: enmascara PII/caso; nunca subir sample sin scrub."""
    del hint  # unused; firma SDK
    try:
        if "request" in event and isinstance(event["request"], dict):
            req = event["request"]
            if "data" in req:
                req["data"] = _scrub_obj(req["data"])
            if "query_string" in req and isinstance(req["query_string"], str):
                req["query_string"] = _scrub_text(req["query_string"])
            if "headers" in req and isinstance(req["headers"], dict):
                for h in ("Authorization", "Cookie", "X-Session", "X-CSRF"):
                    if h in req["headers"]:
                        req["headers"][h] = "[redacted]"
        if "extra" in event:
            event["extra"] = _scrub_obj(event["extra"])
        if "contexts" in event:
            event["contexts"] = _scrub_obj(event["contexts"])
        if "message" in event and isinstance(event["message"], str):
            event["message"] = _scrub_text(event["message"])
        # Breadcrumbs pueden llevar texto de chat.
        for crumb in event.get("breadcrumbs", {}).get("values", []) or []:
            if isinstance(crumb, dict) and "message" in crumb:
                crumb["message"] = _scrub_text(str(crumb["message"]))
            if isinstance(crumb, dict) and "data" in crumb:
                crumb["data"] = _scrub_obj(crumb["data"])
    except Exception:
        # Si el scrub falla, descartar el evento (preferible a filtrar mal).
        return None
    return event
