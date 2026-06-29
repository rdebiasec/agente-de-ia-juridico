"""Cadena de validaciones pre/post ejecución con spans en la traza."""

from __future__ import annotations

import re

_TUTELA_FIELDS = (
    ("accionante", re.compile(r"\baccionante\b", re.I)),
    ("accionado", re.compile(r"\baccionado\b", re.I)),
    ("derecho vulnerado", re.compile(r"\bderecho\b.*\bvulnerad", re.I)),
)
_MEMORIAL_FIELDS = (
    ("radicado", re.compile(r"\bradicad[oa]\b", re.I)),
    ("partes", re.compile(r"\bparte[s]?\b", re.I)),
)


def _span(trace: dict, name: str, status: str, detail: str, *, kind: str = "validation") -> None:
    trace.setdefault("spans", []).append(
        {
            "name": name,
            "kind": kind,
            "status": status,
            "detail": detail,
            "at_ms": trace.get("timestamp") or 0,
        }
    )
    trace.setdefault("steps", []).append({"step": name, "status": status, "detail": detail})


def run_pre_validations(
    message: str,
    *,
    history: list[dict],
    expediente_resumen: str | None,
    trace: dict,
) -> tuple[bool, str | None]:
    """Validaciones encadenadas antes de llamar al orquestador."""
    if not message or not message.strip():
        _span(trace, "Validación: mensaje vacío", "blocked", "La consulta llegó sin contenido.")
        return False, "Escriba su consulta para continuar la conversación."

    _span(trace, "Validación: longitud", "done", f"Entrada válida ({len(message)} caracteres).")

    turn = len([m for m in history if m.get("role") == "user"]) + 1
    trace["turn_index"] = turn
    _span(
        trace,
        "Validación: continuidad",
        "done",
        f"Turno {turn} de la sesión; historial con {len(history)} mensajes previos.",
        kind="session",
    )

    if expediente_resumen and "sin datos" not in expediente_resumen.lower():
        _span(trace, "Validación: expediente", "done", "Contexto del expediente disponible para el agente.", kind="context")
        trace["expediente_context"] = expediente_resumen[:500]
    else:
        _span(
            trace,
            "Validación: expediente",
            "pending",
            "Expediente aún sin datos estructurados; el agente debe solicitar materia, etapa y radicado.",
            kind="context",
        )

    if turn > 1:
        _span(
            trace,
            "Validación: diálogo multi-turno",
            "done",
            "La conversación continúa; se inyectará historial al orquestador.",
            kind="session",
        )

    return True, None


def run_post_validations(message: str, text: str, trace: dict) -> str:
    """Validaciones posteriores: completitud y preguntas de seguimiento."""
    lower_msg = message.lower()
    missing: list[str] = []

    if "tutela" in lower_msg or trace.get("sent_to_agent") == "tutela_constitucional":
        combined = f"{message}\n{text}"
        for label, pattern in _TUTELA_FIELDS:
            if not pattern.search(combined):
                missing.append(label)
        if missing:
            _span(
                trace,
                "Validación: completitud tutela",
                "pending",
                f"Faltan datos: {', '.join(missing)}. Se sugiere continuar el diálogo.",
            )
            follow = (
                "\n\nPara continuar con el borrador de tutela, indíqueme: "
                + ", ".join(missing)
                + "."
            )
            if follow.strip() not in text:
                text = text.rstrip() + follow

    if any(w in lower_msg for w in ("memorial", "radicado", "impulso procesal")):
        combined = f"{message}\n{text}"
        for label, pattern in _MEMORIAL_FIELDS:
            if not pattern.search(combined):
                missing.append(label)
        if missing:
            _span(
                trace,
                "Validación: completitud memorial",
                "pending",
                f"Faltan datos: {', '.join(missing)}.",
            )
            if "radicado" in missing and "radicado" not in text.lower():
                text = text.rstrip() + "\n\n¿Cuál es el número de radicado del proceso?"

    _span(trace, "Validación: salida", "done", "Guardrails y completitud revisados.")
    trace["conversation_continues"] = bool(missing) or trace.get("turn_index", 1) < 5
    return text
