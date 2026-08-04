"""Bitácora append-only del expediente (Gerente maestra + notas de especialistas)."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any, Iterable

from src.gateway.expediente import expediente_store

logger = logging.getLogger(__name__)

_MAX_BITACORA = 200
_RESUMEN_MAX = 1200

_AREA_LABEL = {
    "analista_cronologia_hechos": "cronologia",
    "analista_responsabilidad_tipicidad": "tipicidad",
    "analista_ruta_procesal": "ruta906",
    "analista_representacion_victimas": "victimas",
    "analista_evidencia": "evidencia",
    "analista_audiencias": "audiencias",
    "analista_seguimiento_procesal": "seguimiento",
    "analista_calidad_juridica": "calidad",
    "redactor_documentos_juridicos": "redaccion",
    "coordinador_caso": "gerente",
}


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clip(text: str, max_chars: int = _RESUMEN_MAX) -> str:
    t = (text or "").strip()
    if len(t) <= max_chars:
        return t
    return t[: max_chars - 1].rstrip() + "…"


def area_label(agent_id: str | None) -> str:
    if not agent_id:
        return "equipo"
    try:
        from src.agents.agent_ids import resolve_agent_id

        agent_id = resolve_agent_id(agent_id) or agent_id
    except Exception:
        pass
    return _AREA_LABEL.get(agent_id, agent_id)


def normalize_entry(entry: dict[str, Any]) -> dict[str, Any]:
    """Normaliza una entrada de bitácora para persistencia."""
    autor = str(entry.get("autor") or "gerente_caso").strip() or "gerente_caso"
    tipo = str(entry.get("tipo") or "sintesis").strip() or "sintesis"
    confidencialidad = str(entry.get("confidencialidad") or "normal").strip()
    if confidencialidad not in {"normal", "sensible", "menor"}:
        confidencialidad = "normal"
    fuentes = entry.get("fuentes") or []
    if isinstance(fuentes, str):
        fuentes = [fuentes]
    pendientes = entry.get("pendientes") or []
    if isinstance(pendientes, str):
        pendientes = [pendientes]
    hallazgos = entry.get("hallazgos") or []
    if isinstance(hallazgos, str):
        hallazgos = [hallazgos]
    return {
        "ts": entry.get("ts") or _iso_now(),
        "autor": autor,
        "tipo": tipo,
        "resumen": _clip(str(entry.get("resumen") or "")),
        "fuentes": [str(f) for f in fuentes if str(f).strip()][:12],
        "pendientes": [str(p) for p in pendientes if str(p).strip()][:20],
        "hallazgos": [str(h) for h in hallazgos if str(h).strip()][:10],
        "confidencialidad": confidencialidad,
        "turno_ts": entry.get("turno_ts") or time.time(),
    }


def append_entries(session_id: str, entries: Iterable[dict[str, Any]]) -> list[dict]:
    """Append atómico de entradas; recorta a las últimas `_MAX_BITACORA`."""
    sid = (session_id or "").strip()
    if not sid:
        return []
    normalized = [normalize_entry(e) for e in entries if e]
    if not normalized:
        return []

    def _apply(exp) -> None:
        current = list(getattr(exp, "bitacora", None) or [])
        current.extend(normalized)
        if len(current) > _MAX_BITACORA:
            current = current[-_MAX_BITACORA:]
        exp.bitacora = current
        exp.actualizado_en = time.time()

    try:
        exp = expediente_store.mutate(sid, _apply)
        entries_out = list(getattr(exp, "bitacora", None) or [])
    except Exception:
        logger.exception("No se pudo persistir bitácora session=%s", sid)
        return []

    # Espejo Lexiatek (best-effort; no rompe el chat).
    try:
        from src.services.drive_bitacora import sync_expediente_bitacora

        sync_expediente_bitacora(sid)
    except Exception:
        logger.exception("Drive Lexiatek sync omitido session=%s", sid)

    return entries_out


def append_specialist_notas(
    session_id: str,
    *,
    agent_id: str,
    notas: Iterable[Any],
) -> int:
    """Persiste `notas_trabajo` de un output estructurado de especialista."""
    entries: list[dict[str, Any]] = []
    for nota in notas or []:
        if hasattr(nota, "model_dump"):
            data = nota.model_dump()
        elif isinstance(nota, dict):
            data = dict(nota)
        else:
            continue
        autor = str(data.get("autor") or agent_id)
        entries.append(
            {
                "autor": autor,
                "tipo": data.get("tipo") or "analisis",
                "resumen": data.get("resumen") or "",
                "hallazgos": data.get("hallazgos") or [],
                "pendientes": data.get("pendientes") or [],
                "fuentes": [area_label(agent_id)],
                "confidencialidad": data.get("confidencialidad") or "normal",
            }
        )
    if not entries:
        return 0
    append_entries(session_id, entries)
    return len(entries)


def record_gerente_turn(
    session_id: str,
    *,
    message: str,
    reply: str,
    route: str | None,
    backoffice_agent: str | None,
    blocked: bool = False,
    pending_review: bool = False,
    involucra_menor: bool = False,
    datos_sensibles: bool = False,
) -> list[dict]:
    """Genera entradas maestras del Gerente para el turno (post-hook)."""
    confidencialidad = "normal"
    if involucra_menor:
        confidencialidad = "menor"
    elif datos_sensibles:
        confidencialidad = "sensible"

    fuentes = ["abogado"]
    area = area_label(backoffice_agent)
    if backoffice_agent and backoffice_agent != "coordinador_caso":
        fuentes.append(area)

    entries: list[dict[str, Any]] = [
        {
            "autor": "gerente_caso",
            "tipo": "recepcion",
            "resumen": f"Pedido del abogado: {_clip(message, 400)}",
            "fuentes": ["abogado"],
            "pendientes": [],
            "confidencialidad": confidencialidad,
        }
    ]

    route = route or ""
    if blocked and route in {"pipeline_pre", "guardrail_input", "plan_required"}:
        tipo = "gate" if route != "plan_required" else "plan_hitl"
        entries.append(
            {
                "autor": "gerente_caso",
                "tipo": tipo,
                "resumen": _clip(reply, 600) or f"Turno bloqueado ({route}).",
                "fuentes": fuentes,
                "pendientes": ["Completar datos o aprobar plan HITL"]
                if route == "plan_required"
                else [],
                "confidencialidad": confidencialidad,
            }
        )
    else:
        if backoffice_agent and backoffice_agent not in {
            "coordinador_caso",
            "guardrail",
            "fallback",
            "error",
            "none",
            None,
        }:
            entries.append(
                {
                    "autor": "gerente_caso",
                    "tipo": "retorno_especialista",
                    "resumen": (
                        f"Consulté al área de {area} y consolidé su salida para el despacho."
                    ),
                    "fuentes": fuentes,
                    "pendientes": [],
                    "confidencialidad": confidencialidad,
                }
            )
        tipo_cierre = "plan_hitl" if pending_review else "sintesis"
        entries.append(
            {
                "autor": "gerente_caso",
                "tipo": tipo_cierre,
                "resumen": _clip(reply, 700)
                or "Síntesis de despacho entregada al abogado.",
                "fuentes": fuentes,
                "pendientes": ["Revisión humana del borrador"] if pending_review else [],
                "confidencialidad": confidencialidad,
            }
        )

    return append_entries(session_id, entries)


def extract_and_persist_specialist_output(
    session_id: str,
    *,
    agent_id: str,
    output: Any,
) -> int:
    """Si el output tiene notas_trabajo, las persiste; si no, crea nota mínima."""
    sid = (session_id or "").strip()
    if not sid or not agent_id:
        return 0

    notas = None
    if hasattr(output, "notas_trabajo"):
        notas = getattr(output, "notas_trabajo", None)
    elif isinstance(output, dict):
        notas = output.get("notas_trabajo")

    if notas:
        return append_specialist_notas(sid, agent_id=agent_id, notas=notas)

    # Fallback: una nota mínima desde el render/resumen del especialista.
    resumen = ""
    if hasattr(output, "model_dump"):
        data = output.model_dump()
        resumen = (
            str(data.get("resumen") or data.get("hipotesis_tipica") or data.get("titulo") or "")
            .strip()
        )
        pendientes = data.get("pendientes_verificacion") or []
    elif isinstance(output, str):
        resumen = output.strip()[:400]
        pendientes = []
    else:
        return 0

    if not resumen:
        return 0
    append_entries(
        sid,
        [
            {
                "autor": agent_id,
                "tipo": "analisis",
                "resumen": _clip(resumen, 600),
                "fuentes": [area_label(agent_id)],
                "pendientes": [str(p) for p in pendientes][:10],
                "hallazgos": [],
                "confidencialidad": "normal",
            }
        ],
    )
    return 1
