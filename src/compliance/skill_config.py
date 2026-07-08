"""Configuración aprobada de skills — única fuente operativa tras publicar en auditoría."""

from __future__ import annotations

import copy
import hashlib
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from lib.catalogo_aprobacion import (  # noqa: E402
    GUARDRAILS,
    build_skill_steps,
    guia_audit_key,
)

from lib.approved_skill_config import APPROVED_PATH, load_approved_config  # noqa: E402

GUIA_PARTS = ("instruccion", "tools", "guardrails")


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def save_approved_config(payload: dict) -> None:
    APPROVED_PATH.parent.mkdir(parents=True, exist_ok=True)
    APPROVED_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _checksum(data: dict) -> str:
    raw = json.dumps(data, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _parse_list_field(text: str) -> list[str]:
    text = (text or "").strip()
    if not text:
        return []
    lines = []
    for line in text.splitlines():
        cleaned = re.sub(r"^[\s\-*•]+", "", line.strip())
        if cleaned:
            lines.append(cleaned)
    return lines if lines else [text]


def _paso_key(skill_id: str, num_or_id: str | int) -> str:
    return f"{skill_id}::{num_or_id}"


def _effective_steps(skill: dict, skill_id: str, progress: dict) -> list[dict]:
    custom = progress.get("custom") or {}
    pasos_log = progress.get("pasos") or {}
    removed = set(custom.get("pasosRemoved") or [])
    added = custom.get("pasosAdded") or {}
    merged: list[dict] = []
    for st in skill.get("steps") or []:
        num = st.get("num")
        key = _paso_key(skill_id, num)
        if key in removed:
            continue
        state = pasos_log.get(key) or {}
        text = (state.get("solution") or "").strip() or st.get("text", "")
        merged.append({"num": len(merged) + 1, "text": text, "modo": st.get("modo", "serial")})
    for item in added.get(skill_id) or []:
        cid = item.get("id", "")
        key = _paso_key(skill_id, cid)
        state = pasos_log.get(key) or {}
        text = (state.get("solution") or "").strip() or item.get("text", "")
        if text:
            merged.append({"num": len(merged) + 1, "text": text, "modo": "serial"})
    return build_skill_steps(merged)


def _effective_guardrails(catalog_guardrails: list[dict], progress: dict) -> list[dict]:
    custom = progress.get("custom") or {}
    removed = set(custom.get("guardrailsRemoved") or [])
    added = custom.get("guardrailsAdded") or []
    base = [g for g in catalog_guardrails if g.get("id") not in removed]
    for g in added:
        gid = g.get("id") or f"custom_{len(base)}"
        state = (progress.get("guardrails") or {}).get(gid) or {}
        desc = (state.get("solution") or "").strip() or g.get("desc", "")
        base.append({"id": gid, "name": g.get("name", gid), "desc": desc, "custom": True})
    gr_log = progress.get("guardrails") or {}
    out = []
    for g in base:
        state = gr_log.get(g["id"]) or {}
        desc = (state.get("solution") or "").strip() or g.get("desc", "")
        out.append({**g, "desc": desc})
    return out


def _apply_context_overrides(skill: dict, progress: dict) -> None:
    guias = progress.get("guias") or {}
    sid = skill["id"]
    for part in GUIA_PARTS:
        key = guia_audit_key(sid, part)
        state = guias.get(key) or {}
        sol = (state.get("solution") or "").strip()
        if state.get("status") != "APROBADO" or not sol:
            continue
        if part == "instruccion":
            skill["instruccion"] = sol
            if not skill.get("purpose"):
                skill["purpose"] = sol
        elif part == "tools":
            skill["tools"] = _parse_list_field(sol)
        elif part == "guardrails":
            skill["guardrails"] = _parse_list_field(sol)


def merge_progress_into_catalog(catalog: dict, progress: dict) -> dict:
    """Materializa el catálogo efectivo según decisiones del portal."""
    out = copy.deepcopy(catalog)
    out["guardrails"] = _effective_guardrails(out.get("guardrails") or GUARDRAILS, progress)
    for agent in out.get("agentes") or []:
        state = (progress.get("agentes") or {}).get(agent["id"]) or {}
        sol = (state.get("solution") or "").strip()
        if state.get("status") == "APROBADO" and sol:
            agent["desc"] = sol
    for skill in out.get("skills") or []:
        _apply_context_overrides(skill, progress)
        sid = skill["id"]
        skill["steps"] = _effective_steps(skill, sid, progress)
        skill["step_count"] = len(skill["steps"])
    return out


def _iter_audit_items(catalog: dict, progress: dict) -> list[tuple[str, str]]:
    """(bucket, id) de todos los ítems auditables."""
    items: list[tuple[str, str]] = []
    merged = merge_progress_into_catalog(catalog, progress)
    for g in merged.get("guardrails") or []:
        items.append(("guardrails", g["id"]))
    for a in merged.get("agentes") or []:
        items.append(("agentes", a["id"]))
    for skill in merged.get("skills") or []:
        sid = skill["id"]
        for part in GUIA_PARTS:
            items.append(("guias", guia_audit_key(sid, part)))
        for st in skill.get("steps") or []:
            items.append(("pasos", _paso_key(sid, st["num"])))
    custom = progress.get("custom") or {}
    for sid, added in (custom.get("pasosAdded") or {}).items():
        for st in added:
            items.append(("pasos", _paso_key(sid, st.get("id", ""))))
    return items


def validate_publish_progress(catalog: dict, progress: dict) -> list[str]:
    errors: list[str] = []
    for bucket, item_id in _iter_audit_items(catalog, progress):
        state = (progress.get(bucket) or {}).get(item_id) or {}
        status = state.get("status", "PENDIENTE")
        if status == "PENDIENTE":
            errors.append(f"Pendiente de revisión: {bucket}/{item_id}")
        elif status == "AJUSTAR":
            errors.append(f"Requiere aprobación tras ajuste: {bucket}/{item_id}")
    return errors


def _skill_snapshot(skill: dict) -> dict:
    return {
        "instruccion": skill.get("instruccion", ""),
        "purpose": skill.get("purpose", ""),
        "inputs": skill.get("inputs", ""),
        "outputs": skill.get("outputs", ""),
        "tier": skill.get("tier", ""),
        "rol": skill.get("rol", ""),
        "no_duplicar": skill.get("no_duplicar", ""),
        "handoff": skill.get("handoff", ""),
        "riesgo": skill.get("riesgo", ""),
        "tools": skill.get("tools") or [],
        "guardrails": skill.get("guardrails") or [],
        "steps": skill.get("steps") or [],
        "agents": skill.get("agents") or [],
        "category": skill.get("category", ""),
    }


def publish_skill_config(catalog: dict, progress: dict, *, email: str) -> dict:
    errors = validate_publish_progress(catalog, progress)
    if errors:
        raise ValueError("; ".join(errors[:8]) + (f" (+{len(errors) - 8} más)" if len(errors) > 8 else ""))

    merged = merge_progress_into_catalog(catalog, progress)
    prev = load_approved_config() or {}
    version = int(prev.get("version") or 0) + 1
    skills_payload = {s["id"]: _skill_snapshot(s) for s in merged.get("skills") or []}
    body = {
        "version": version,
        "published_at": _now_utc(),
        "published_by": email,
        "catalog_version": catalog.get("version", ""),
        "catalog_generated_at": catalog.get("generated_at", ""),
        "skills": skills_payload,
        "guardrails": merged.get("guardrails") or [],
        "agents": {
            a["id"]: {
                "desc": a.get("desc", ""),
                "problema": a.get("problema", ""),
                "necesidad": a.get("necesidad", ""),
                "no_reemplaza": a.get("no_reemplaza", ""),
            }
            for a in merged.get("agentes") or []
        },
    }
    body["checksum"] = _checksum(body)
    save_approved_config(body)
    return body


def apply_approved_to_skills_raw(skills_raw: dict[str, dict]) -> dict[str, dict]:
    from lib.approved_skill_config import apply_approved_to_skills_raw as _apply

    return _apply(skills_raw)


def validate_runtime_skill_config() -> list[str]:
    """Validación al arranque del servicio."""
    errors: list[str] = []
    from lib.audit_data import build_audit_data  # noqa: E402

    try:
        catalog = build_audit_data()
    except Exception as exc:
        return [f"No se pudo construir catálogo: {exc}"]

    skills = catalog.get("skills") or []
    if len(skills) != 90:
        errors.append(f"Se esperaban 90 skills, hay {len(skills)}")

    approved = load_approved_config()
    if approved:
        if not approved.get("checksum"):
            errors.append("Config aprobada sin checksum")
        expected = approved.get("skills") or {}
        missing = [sid for sid in expected if sid not in {s["id"] for s in skills}]
        if missing:
            errors.append(f"Skills aprobados ausentes en catálogo: {', '.join(missing[:5])}")
        for skill in skills:
            if not (skill.get("instruccion") or "").strip():
                errors.append(f"Skill sin instrucción: {skill['id']}")
            if not skill.get("steps"):
                errors.append(f"Skill sin pasos: {skill['id']}")
    else:
        logger.info("Sin config aprobada publicada; operando con baseline SKILL.md")

    return errors


def config_status() -> dict[str, Any]:
    approved = load_approved_config()
    if not approved:
        return {
            "published": False,
            "version": 0,
            "published_at": None,
            "published_by": None,
            "checksum": None,
            "skills_count": 0,
        }
    return {
        "published": True,
        "version": approved.get("version", 0),
        "published_at": approved.get("published_at"),
        "published_by": approved.get("published_by"),
        "checksum": approved.get("checksum"),
        "skills_count": len(approved.get("skills") or {}),
        "catalog_generated_at": approved.get("catalog_generated_at"),
    }
