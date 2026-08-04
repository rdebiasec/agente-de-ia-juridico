"""Deliberación mediada Gerente↔especialistas (opción A) — schema de trace."""

from __future__ import annotations

import re
import time
from typing import Any, Literal

from src.agents.pii import mask_pii

DELIBERATION_PROTOCOL = "gerente_especialista_v1"
DELIBERATION_TEXT_CAP = 2400

DeliberationKind = Literal["consult", "findings", "synthesize", "escalate"]

_PENDIENTE_RE = re.compile(r"\[PENDIENTE DE VERIFICAR\]", re.IGNORECASE)


def empty_deliberation() -> dict[str, Any]:
    return {
        "protocol": DELIBERATION_PROTOCOL,
        "turns": [],
        "summary": {},
    }


def clip_deliberation_text(text: str | None, *, limit: int = DELIBERATION_TEXT_CAP) -> str:
    normalized = " ".join((text or "").split())
    masked = mask_pii(normalized)
    if len(masked) <= limit:
        return masked
    return f"{masked[: limit - 3]}..."


def ensure_deliberation(trace: dict) -> dict[str, Any]:
    block = trace.setdefault("deliberation", empty_deliberation())
    if not isinstance(block, dict):
        block = empty_deliberation()
        trace["deliberation"] = block
    block.setdefault("protocol", DELIBERATION_PROTOCOL)
    block.setdefault("turns", [])
    block.setdefault("summary", {})
    return block


def next_ronda_for(trace: dict, specialist_id: str) -> int:
    """Número de consult al mismo especialista en este turno (1-based)."""
    turns = ensure_deliberation(trace).get("turns") or []
    n = sum(
        1
        for t in turns
        if isinstance(t, dict)
        and t.get("kind") == "consult"
        and t.get("specialist_id") == specialist_id
    )
    return n + 1


def append_deliberation_turn(
    trace: dict,
    *,
    kind: DeliberationKind,
    specialist_id: str = "",
    pedido: str = "",
    respuesta: str = "",
    reasoning: str = "",
    ronda: int | None = None,
) -> dict[str, Any]:
    block = ensure_deliberation(trace)
    turn: dict[str, Any] = {
        "kind": kind,
        "specialist_id": specialist_id or "",
        "pedido": clip_deliberation_text(pedido),
        "respuesta": clip_deliberation_text(respuesta),
        "reasoning": clip_deliberation_text(reasoning, limit=800),
        "ronda": int(ronda or 0) or None,
        "at_ms": int(time.time() * 1000),
    }
    block["turns"].append(turn)
    return turn


def _extract_pendientes(text: str) -> list[str]:
    if not text or not _PENDIENTE_RE.search(text):
        return []
    # Heurística: líneas o fragmentos que contienen el marcador.
    found: list[str] = []
    for raw in re.split(r"[\n;•]+", text):
        chunk = " ".join(raw.split()).strip()
        if _PENDIENTE_RE.search(chunk):
            found.append(clip_deliberation_text(chunk, limit=220))
    if not found:
        found.append("[PENDIENTE DE VERIFICAR] (detectado en hallazgos)")
    return found[:8]


def finalize_deliberation_summary(trace: dict) -> dict[str, Any]:
    """Cierra summary + turno synthesize si hubo consultas backoffice."""
    block = ensure_deliberation(trace)
    turns = [t for t in (block.get("turns") or []) if isinstance(t, dict)]
    consults = [t for t in turns if t.get("kind") == "consult"]
    findings = [t for t in turns if t.get("kind") == "findings"]

    specialists: list[str] = []
    for t in consults:
        sid = str(t.get("specialist_id") or "").strip()
        if sid and sid not in specialists:
            specialists.append(sid)

    open_pendientes: list[str] = []
    for t in findings:
        for p in _extract_pendientes(str(t.get("respuesta") or "")):
            if p not in open_pendientes:
                open_pendientes.append(p)

    rounds = len(consults)
    summary = {
        "specialists_consulted": specialists,
        "rounds": rounds,
        "open_pendientes": open_pendientes[:12],
    }
    block["summary"] = summary

    if rounds >= 1 and not any(t.get("kind") == "synthesize" for t in turns):
        areas = ", ".join(specialists) if specialists else "(ninguno)"
        pendientes_note = (
            f" Pendientes marcados: {len(open_pendientes)}."
            if open_pendientes
            else ""
        )
        append_deliberation_turn(
            trace,
            kind="synthesize",
            specialist_id="",
            pedido="",
            respuesta="",
            reasoning=(
                f"Síntesis de junta interna: {rounds} consulta(s) a {areas}."
                f"{pendientes_note}"
            ),
            ronda=rounds,
        )
    return summary
