"""Cadena de validaciones pre/post ejecución con spans en la traza."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.storage.models import Expediente

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


def _preview(content: str, limit: int = 120) -> str:
    text = " ".join((content or "").split())
    if len(text) <= limit:
        return text
    return f"{text[: limit - 3]}..."


def attach_session_continuity(
    trace: dict,
    *,
    history: list[dict],
    session_id: str,
    prior_traces: list | None = None,
) -> None:
    """Inyecta contexto de sesión multi-turno y spans de historial en la traza."""
    from src.storage import get_repository

    if prior_traces is None:
        prior_traces = get_repository().list_session_traces(session_id, limit=40)

    user_msgs = [m for m in history if m.get("role") == "user"]
    assistant_msgs = [m for m in history if m.get("role") == "assistant"]
    trace["session_message_count"] = len(history)
    trace["session_user_turns"] = len(user_msgs)
    trace["prior_traces_count"] = len(prior_traces)
    trace["session_history_preview"] = [
        {"role": m.get("role", "?"), "preview": _preview(str(m.get("content", "")))}
        for m in history[-12:]
    ]
    trace["session_flow"] = [
        {
            "turn_index": t.turn_index,
            "trace_id": t.trace_id,
            "input_summary": (t.payload or {}).get("input_summary", ""),
            "sent_to_agent": (t.payload or {}).get("sent_to_agent", ""),
            "spans_count": len((t.payload or {}).get("spans", [])),
            "conversation_continues": (t.payload or {}).get("conversation_continues", False),
        }
        for t in prior_traces
    ]

    _span(
        trace,
        "Sesión: cargar historial",
        "done",
        f"{len(history)} mensajes en memoria ({len(user_msgs)} usuario / {len(assistant_msgs)} asistente).",
        kind="session",
    )
    _span(
        trace,
        "Sesión: trazas previas",
        "done",
        f"{len(prior_traces)} turno(s) ya persistido(s) en esta sesión.",
        kind="session",
    )

    if not history:
        _span(trace, "Sesión: primer turno", "done", "Inicio de conversación sin historial previo.", kind="session")
    else:
        for idx, msg in enumerate(history[-8:], start=max(1, len(history) - 7)):
            role = str(msg.get("role", "?"))
            _span(
                trace,
                f"Historial turno previo [{idx}]",
                "done",
                f"{role}: {_preview(str(msg.get('content', '')))}",
                kind="session",
            )

    if len(prior_traces) >= 1:
        last = prior_traces[-1]
        payload = last.payload or {}
        _span(
            trace,
            "Sesión: encadenar turno anterior",
            "done",
            (
                f"Turno {last.turn_index} → {payload.get('sent_to_agent', 'n/a')}; "
                f"continúa={payload.get('conversation_continues', False)}."
            ),
            kind="session",
        )


def run_pre_validations(
    message: str,
    *,
    history: list[dict],
    expediente_resumen: str | None,
    trace: dict,
    expediente: Expediente | None = None,
    destination: str | None = None,
) -> tuple[bool, str | None]:
    """Validaciones encadenadas antes de llamar al coordinador penal."""
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
            "Expediente aún sin datos estructurados; el agente debe solicitar rol de víctima, etapa y radicado.",
            kind="context",
        )

    if expediente is not None and destination:
        from src.agents.completeness import (
            assess_completeness,
            format_missing_request,
            persist_verification,
        )

        verification = assess_completeness(
            message,
            destination=destination,
            expediente=expediente,
        )
        persist_verification(expediente, verification, destination=destination)
        trace["gerencia_verification"] = {
            "puede_continuar": verification.puede_continuar,
            "faltantes": verification.faltantes,
            "destination": destination,
        }
        if not verification.puede_continuar:
            _span(
                trace,
                "Gerencia: verificación de completitud",
                "blocked",
                f"Delegación detenida; faltan: {', '.join(verification.faltantes)}.",
                kind="guardrail",
            )
            return False, format_missing_request(verification.faltantes)
        _span(
            trace,
            "Gerencia: verificación de completitud",
            "done",
            "El expediente cumple los mínimos para el destino solicitado.",
            kind="guardrail",
        )

    if turn > 1:
        _span(
            trace,
            "Validación: diálogo multi-turno",
            "done",
            "La conversación continúa; se inyectará historial al coordinador penal.",
            kind="session",
        )

    return True, None


def run_post_validations(message: str, text: str, trace: dict) -> str:
    """Validaciones posteriores: completitud, groundedness blanda y seguimiento."""
    lower_msg = message.lower()
    missing: list[str] = []

    if "tutela" in lower_msg or trace.get("sent_to_agent") in {
        "evaluador_derechos_fundamentales_tutela",
        "tutela_constitucional",  # compatibilidad con trazas legacy
    }:
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

    # C6 — gate blando de calidad/groundedness en el path de chat
    from src.agents.sdk_guardrails import citation_hints_without_pending
    from src.agents.skill_catalog import HITL_OUTPUT_AGENTS, HIGH_RISK_AGENTS

    sent = str(trace.get("sent_to_agent") or "")
    actionable = sent in (HIGH_RISK_AGENTS | HITL_OUTPUT_AGENTS) or bool(
        re.search(r"\b(memorial|tutela|recurso|guion)\b", lower_msg, re.I)
    )
    needs_pending = citation_hints_without_pending(text) and actionable
    if needs_pending:
        _span(
            trace,
            "Calidad: groundedness",
            "pending",
            "Hay indicios de citas/radicados sin [PENDIENTE DE VERIFICAR]; se marca para revision.",
            kind="guardrail",
        )
        if "[PENDIENTE DE VERIFICAR]" not in text:
            text = (
                text.rstrip()
                + "\n\n[PENDIENTE DE VERIFICAR] Citas, normas o radicados mencionados "
                "requieren confirmacion del abogado antes de uso externo."
            )
        if "control de calidad" not in text.lower():
            text = (
                text.rstrip()
                + "\n\nRecomendación del Gerente: antes de uso externo, solicite un paso "
                "de control de calidad jurídica en el plan de ejecución."
            )
        trace["quality_check"] = {
            "status": "pending_markers_added",
            "reason": "citation_hints_without_pending",
        }
    else:
        _span(trace, "Calidad: groundedness", "done", "Sin indicios de citas sin ancla de pendiente.")
        trace["quality_check"] = {"status": "ok"}

    _span(trace, "Validación: salida", "done", "Guardrails y completitud revisados.")
    trace["conversation_continues"] = bool(missing) or trace.get("turn_index", 1) < 5
    return text
