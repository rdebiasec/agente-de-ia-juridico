"""Atribución debug (Fase 4): solo chat abogado↔Gerente, nunca al cliente."""

from __future__ import annotations

import re

from src.storage import get_repository
from src.storage.models import InternalTranscriptEntry

_ATTRIBUTION_RE = re.compile(
    r"(?:"
    r"de\s+d[oó]nde\s+(?:sale|sali[oó]|viene|viene\s+eso)|"
    r"qui[eé]n\s+(?:dijo|aport[oó]|sugiri[oó]|concluy[oó]|lo\s+dijo)|"
    r"(?:qu[eé]|cu[aá]l)\s+(?:especialista|[aá]rea|equipo)|"
    r"atribuci[oó]n|"
    r"fuente\s+interna|"
    r"c[oó]mo\s+llegaron\s+a|"
    r"de\s+qu[eé]\s+[aá]rea"
    r")",
    re.I,
)


def is_attribution_question(message: str) -> bool:
    return bool(_ATTRIBUTION_RE.search(message or ""))


def _actor_label(actor: str) -> str:
    from src.agents.agent_ids import (
        AGENT_DISPLAY_LABELS,
        LEGACY_AGENT_ALIASES,
        resolve_agent_id,
    )

    raw = (actor or "").strip()
    if raw in LEGACY_AGENT_ALIASES or resolve_agent_id(raw) == "coordinador_caso":
        if raw in {
            "gerente",
            "gerente_caso",
            "coordinador_expediente_penal",
            "coordinador_caso",
        }:
            return AGENT_DISPLAY_LABELS["coordinador_caso"]
    if raw.startswith("especialista:"):
        agent_id = resolve_agent_id(raw.split(":", 1)[1])
        if agent_id in AGENT_DISPLAY_LABELS:
            return AGENT_DISPLAY_LABELS[agent_id]
        try:
            from src.services.bitacora import area_label

            return area_label(agent_id)
        except Exception:
            return agent_id
    canonical = resolve_agent_id(raw)
    if canonical in AGENT_DISPLAY_LABELS:
        return AGENT_DISPLAY_LABELS[canonical]
    try:
        from src.services.bitacora import area_label

        return area_label(canonical)
    except Exception:
        return raw or "equipo"


def _clip(text: str, limit: int = 320) -> str:
    normalized = " ".join((text or "").split())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[: limit - 3]}..."


def load_recent_exchanges(session_id: str, *, limit: int = 8) -> list[InternalTranscriptEntry]:
    sid = (session_id or "").strip()
    if not sid:
        return []
    entries = get_repository().list_internal_transcript(sid, limit=50)
    return entries[-limit:]


def format_attribution_context(session_id: str, *, limit: int = 8) -> str:
    """Bloque para el LLM (solo canal abogado)."""
    entries = load_recent_exchanges(session_id, limit=limit)
    lines = [
        "[ATRIBUCION_INTERNA — solo para el abogado; no inventes áreas]",
        "Si pregunta de dónde salió un hallazgo, cita el área del transcript o bitácora.",
        "No uses IDs técnicos ni nombres de schemas en la respuesta al abogado.",
    ]
    if not entries:
        lines.append("- (sin consultas internas registradas en esta sesión)")
    else:
        for e in entries:
            area = _actor_label(e.to_actor)
            lines.append(
                f"- Área {area}: pedido«{_clip(e.pedido, 160)}» → retorno«{_clip(e.respuesta, 220)}»"
            )

    # Bitácora reciente (fuentes humanas)
    try:
        exp = get_repository().get_expediente(session_id)
        bitacora = list(getattr(exp, "bitacora", None) or [])[-5:]
        if bitacora:
            lines.append("- Notas de bitácora recientes:")
            for note in bitacora:
                fuentes = ", ".join(note.get("fuentes") or []) or "n/a"
                lines.append(
                    f"  · fuentes={fuentes}; resumen«{_clip(str(note.get('resumen') or ''), 180)}»"
                )
    except Exception:
        pass

    return "\n".join(lines) + "\n"


def answer_attribution(
    message: str,
    *,
    session_id: str,
    channel: str = "web",
) -> str | None:
    """
    Respuesta determinista de atribución.
    None si no aplica (no es pregunta de atribución o canal cliente).
    """
    if (channel or "").strip().lower() in {"cliente", "victim", "victima"}:
        return None
    if not is_attribution_question(message):
        return None

    entries = load_recent_exchanges(session_id, limit=8)
    closing = (
        "\n\nBorrador informativo — requiere revisión y aprobación del abogado."
    )
    if not entries:
        return (
            "Aún no hay consultas internas registradas en esta sesión. "
            "Cuando el Coordinador del Caso delegue a un área del equipo, podré decirle "
            "qué especialista aportó cada hallazgo."
            + closing
        )

    # Preferir área cuyo retorno solape términos de la pregunta.
    tokens = {
        t
        for t in re.findall(r"[a-záéíóúñ0-9]{4,}", (message or "").lower())
        if t
        not in {
            "donde",
            "dónde",
            "sale",
            "viene",
            "dijo",
            "quien",
            "quién",
            "area",
            "área",
            "esto",
            "esa",
            "ese",
            "hallazgo",
            "conclus",
        }
    }
    best = entries[-1]
    best_score = -1
    for e in entries:
        blob = f"{e.pedido} {e.respuesta}".lower()
        score = sum(1 for t in tokens if t in blob)
        if score > best_score:
            best_score = score
            best = e

    area = _actor_label(best.to_actor)
    areas = []
    for e in entries:
        label = _actor_label(e.to_actor)
        if label not in areas:
            areas.append(label)

    body = (
        f"Eso lo aportó el área de {area}. "
        f"En el transcript interno figura: «{_clip(best.respuesta, 400)}». "
        f"En esta sesión también consulté: {', '.join(areas)}."
    )
    return body + closing
