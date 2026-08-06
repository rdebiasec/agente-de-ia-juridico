"""Notepads por especialista — plantillas repo + render desde Expediente.bitacora.

Modelo dual (decisión #2 / F5–F-08):
- Autorativo: Postgres `Expediente.bitacora` (+ `notas_trabajo` vía bitacora.py).
- Espejo: Drive `casos/<id>/notepads/{agent_id}.md` (vía drive_bitacora).
- Plantillas canónicas: `agente/notepads/{agent_id}.md`.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.agents.agent_ids import (
    AGENT_DISPLAY_LABELS,
    agent_display_label,
    resolve_agent_id,
)

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
NOTEPADS_DIR = ROOT / "agente" / "notepads"
_TEMPLATE_NAME = "_TEMPLATE.md"

# Especialistas canónicos con notepad (mismo set que prompts/agents).
NOTEPAD_AGENT_IDS: tuple[str, ...] = tuple(sorted(AGENT_DISPLAY_LABELS.keys()))

_EMPTY = "_Sin contenido aún (piloto / sesión vacía)._"


def templates_dir() -> Path:
    return NOTEPADS_DIR


def template_path(agent_id: str) -> Path:
    aid = resolve_agent_id(agent_id) or (agent_id or "").strip()
    return NOTEPADS_DIR / f"{aid}.md"


def load_base_template() -> str:
    path = NOTEPADS_DIR / _TEMPLATE_NAME
    if not path.is_file():
        raise FileNotFoundError(f"Falta plantilla base: {path}")
    return path.read_text(encoding="utf-8")


def ensure_agent_template(agent_id: str) -> Path:
    """Asegura `agente/notepads/{agent_id}.md` (copia de _TEMPLATE con agent fijo)."""
    aid = resolve_agent_id(agent_id) or (agent_id or "").strip()
    if not aid or aid not in AGENT_DISPLAY_LABELS:
        raise ValueError(f"agent_id no canónico para notepad: {agent_id!r}")
    dest = template_path(aid)
    NOTEPADS_DIR.mkdir(parents=True, exist_ok=True)
    if dest.is_file():
        return dest
    label = agent_display_label(aid)
    body = load_base_template()
    body = body.replace("{{agent_id}}", aid).replace("{{agent_label}}", label)
    dest.write_text(body, encoding="utf-8")
    return dest


def ensure_all_templates() -> list[Path]:
    return [ensure_agent_template(aid) for aid in NOTEPAD_AGENT_IDS]


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _bullet_block(items: list[str]) -> str:
    cleaned = [str(x).strip() for x in items if str(x).strip()]
    if not cleaned:
        return _EMPTY
    return "\n".join(f"- {x}" for x in cleaned)


def entries_for_agent(bitacora: list[Any] | None, agent_id: str) -> list[dict[str, Any]]:
    """Filtra entradas cuyo autor resuelve al agent_id (o gerente→coordinador)."""
    aid = resolve_agent_id(agent_id) or (agent_id or "").strip()
    out: list[dict[str, Any]] = []
    for entry in bitacora or []:
        if not isinstance(entry, dict):
            continue
        autor = resolve_agent_id(str(entry.get("autor") or "")) or str(
            entry.get("autor") or ""
        )
        if aid == "coordinador_caso":
            if autor in {"coordinador_caso", "gerente_caso", "gerente"}:
                out.append(entry)
        elif autor == aid:
            out.append(entry)
    return out


def render_notepad_md(
    agent_id: str,
    *,
    session_id: str,
    bitacora: list[Any] | None = None,
    eval_or_session: str | None = None,
    updated_at: str | None = None,
) -> str:
    """Renderiza markdown de notepad desde plantilla + entradas filtradas."""
    aid = resolve_agent_id(agent_id) or (agent_id or "").strip()
    label = agent_display_label(aid) or aid
    ensure_agent_template(aid)
    tpl = template_path(aid).read_text(encoding="utf-8")

    entries = entries_for_agent(bitacora, aid)
    hechos: list[str] = []
    inferencias: list[str] = []
    pendientes: list[str] = []
    citas: list[str] = []
    hitl: list[str] = []
    preguntas: list[str] = []
    entradas_md: list[str] = []

    for i, entry in enumerate(entries, 1):
        tipo = str(entry.get("tipo") or "")
        resumen = str(entry.get("resumen") or "").strip()
        fuentes = [str(f) for f in (entry.get("fuentes") or []) if str(f).strip()]
        halls = [str(h) for h in (entry.get("hallazgos") or []) if str(h).strip()]
        pends = [str(p) for p in (entry.get("pendientes") or []) if str(p).strip()]
        if resumen:
            if tipo in {"analisis", "inventario", "sintesis", "recepcion", "retorno_especialista"}:
                hechos.append(f"{resumen}" + (f" _(fuentes: {', '.join(fuentes)})_" if fuentes else ""))
            elif tipo in {"alerta"}:
                inferencias.append(resumen)
            else:
                inferencias.append(f"[{tipo}] {resumen}")
        for h in halls:
            inferencias.append(h)
        for p in pends:
            if "PENDIENTE" not in p.upper() and "verificar" not in p.lower():
                pendientes.append(f"[PENDIENTE DE VERIFICAR] {p}")
            else:
                pendientes.append(p)
            if "?" in p or p.lower().startswith("confirmar"):
                preguntas.append(p)
        for f in fuentes:
            if f not in citas and f not in {"abogado", "equipo"}:
                citas.append(f)
        if tipo in {"gate", "plan_hitl"}:
            hitl.append(resumen or f"HITL ({tipo})")
        ts = entry.get("ts") or ""
        entradas_md.append(f"### {i}. [{tipo}] {entry.get('autor') or ''}")
        if ts:
            entradas_md.append(f"- **ts:** {ts}")
        if resumen:
            entradas_md.append(f"- **resumen:** {resumen}")
        if halls:
            entradas_md.append("- **hallazgos:**")
            entradas_md.extend(f"  - {h}" for h in halls)
        if pends:
            entradas_md.append("- **pendientes:**")
            entradas_md.extend(f"  - {p}" for p in pends)
        entradas_md.append("")

    sid = (session_id or "").strip() or "_sin_sesion"
    replacements = {
        "{{caso_id}}": sid,
        "{{agent_id}}": aid,
        "{{agent_label}}": label,
        "{{updated_at}}": updated_at or _iso_now(),
        "{{eval_or_session}}": eval_or_session or sid,
        "{{hechos_usados}}": _bullet_block(hechos),
        "{{inferencias}}": _bullet_block(inferencias),
        "{{pendientes}}": _bullet_block(pendientes),
        "{{citas_kb}}": _bullet_block(citas),
        "{{hitl}}": _bullet_block(hitl),
        "{{proxima_pregunta}}": _bullet_block(preguntas),
        "{{entradas}}": "\n".join(entradas_md).rstrip() if entradas_md else _EMPTY,
    }
    out = tpl
    for key, val in replacements.items():
        out = out.replace(key, val)
    return out


def render_all_notepads(
    *,
    session_id: str,
    bitacora: list[Any] | None = None,
    eval_or_session: str | None = None,
) -> dict[str, str]:
    """Renderiza un MD por agent_id canónico."""
    ts = _iso_now()
    return {
        aid: render_notepad_md(
            aid,
            session_id=session_id,
            bitacora=bitacora,
            eval_or_session=eval_or_session,
            updated_at=ts,
        )
        for aid in NOTEPAD_AGENT_IDS
    }
