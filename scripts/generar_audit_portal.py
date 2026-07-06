#!/usr/bin/env python3
"""Genera audit-data.json y copia audit-portal/site/ a audit-portal/dist/."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from lib.catalogo_aprobacion import (  # noqa: E402
    AGENTS,
    CATEGORY_DESCRIPTIONS,
    GUARDRAILS,
    agent_group,
    agent_skills_map,
    agent_titulo,
    build_skill_steps,
    infer_destinatario,
    load_skills_catalog,
    skill_flujo_pasos,
    skill_titulo_upper,
)

SITE_DIR = ROOT / "audit-portal" / "site"
DIST_DIR = ROOT / "audit-portal" / "dist"

# Login del portal: desactivado por defecto (local y GitHub Pages).
# Para reactivar: AUDIT_PORTAL_AUTH_ENABLED=1 y AUDIT_PORTAL_PASSWORD en el entorno de build.
def audit_auth_enabled() -> bool:
    return os.environ.get("AUDIT_PORTAL_AUTH_ENABLED", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def build_audit_data() -> dict:
    skills_raw = load_skills_catalog()
    skill_map = agent_skills_map(skills_raw)

    skills = []
    pasos_total = 0
    for sid in sorted(skills_raw):
        data = skills_raw[sid]
        desc = (data.get("purpose") or data.get("instruccion") or "").strip()
        if not desc:
            desc = "Skill atomico del sistema penal-victimas."
        steps = build_skill_steps(data.get("steps") or [])
        pasos_total += len(steps)
        agent_ids = data.get("agents") or []
        skills.append(
            {
                "id": sid,
                "name": sid,
                "titulo": skill_titulo_upper(
                    (data.get("instruccion") or "").strip(),
                    desc,
                ),
                "category": data.get("category") or "Sin categoria",
                "desc": desc,
                "instruccion": (data.get("instruccion") or "").strip(),
                "inputs": (data.get("inputs") or "").strip(),
                "outputs": (data.get("outputs") or "").strip(),
                "agents": agent_ids,
                "agentes_ejecutores": [agent_titulo(aid) for aid in agent_ids],
                "destinatario": infer_destinatario(agent_ids),
                "flujo_pasos": skill_flujo_pasos(steps),
                "step_count": len(steps),
                "steps": steps,
                "steps_missing": len(steps) == 0,
            }
        )

    agentes = []
    for a in AGENTS:
        aid = a["id"]
        skill_ids = sorted(skill_map.get(aid, []))
        agentes.append(
            {
                "id": aid,
                "name": aid,
                "nombre_corto": a["nombre_corto"],
                "titulo_profesional": a.get("titulo_profesional") or a["nombre_corto"].upper(),
                "desc": a["proposito"],
                "problema": a["problema"],
                "necesidad": a.get("necesidad", ""),
                "no_reemplaza": a["no_reemplaza"],
                "prompt_simple": a.get("prompt_simple") or [],
                "grupo": agent_group(aid),
                "skills_count": len(skill_ids),
                "skill_ids": skill_ids,
            }
        )

    categorias = []
    seen_cats: set[str] = set()
    for s in skills:
        cat = s["category"]
        if cat in seen_cats:
            continue
        seen_cats.add(cat)
        categorias.append(
            {
                "id": cat,
                "name": cat,
                "desc": CATEGORY_DESCRIPTIONS.get(cat, "Categoria funcional del catalogo de skills."),
            }
        )
    categorias.sort(key=lambda c: c["name"])

    guardrails_n = len(GUARDRAILS)
    agentes_n = len(agentes)
    items_total = guardrails_n + agentes_n + pasos_total

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return {
        "version": "2.0",
        "generated_at": now,
        "intro": {
            "agentes": agentes_n,
            "skills": len(skills),
            "guias_operativas": len(skills),
            "pasos_total": pasos_total,
            "guardrails": guardrails_n,
            "items_total": items_total,
        },
        "guardrails": GUARDRAILS,
        "agentes": agentes,
        "categorias": categorias,
        "skills": skills,
        "totals": {
            "guardrails": guardrails_n,
            "agentes": agentes_n,
            "skills": len(skills),
            "pasos": pasos_total,
            "items": items_total,
        },
    }


def audit_api_base() -> str:
    return os.environ.get("AUDIT_API_BASE", "").strip().rstrip("/")


def build_audit_api_config_js() -> str:
    base = audit_api_base()
    payload = {"base": base}
    return f"window.AUDIT_API_CONFIG={json.dumps(payload, ensure_ascii=False)};\n"


def write_audit_api_config() -> None:
    out = DIST_DIR / "audit-api-config.js"
    out.write_text(build_audit_api_config_js(), encoding="utf-8")
    base = audit_api_base()
    if base:
        print(f"  api: AUDIT_API_BASE={base}")
    else:
        print("  api: mismo origen (AUDIT_API_BASE vacío → /api/audit en el servidor)")


def build_auth_config_js() -> str:
    """Genera auth-config.js. Login legacy desactivado — auth vía API /api/audit/login."""
    return "window.AUDIT_AUTH_CONFIG={enabled:false};\n"


def _auth_config_enabled(content: str) -> bool:
    compact = content.replace(" ", "")
    return '"enabled":true' in compact or "enabled:true" in compact


def write_auth_config() -> None:
    out = DIST_DIR / "auth-config.js"
    out.write_text(build_auth_config_js(), encoding="utf-8")
    print("  auth: login vía API /api/audit (auth-config.js legacy desactivado)")


def copy_site_to_dist() -> None:
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    shutil.copytree(SITE_DIR, DIST_DIR)


def main() -> None:
    if not SITE_DIR.is_dir():
        raise SystemExit(f"Falta carpeta fuente: {SITE_DIR}")

    data = build_audit_data()
    copy_site_to_dist()

    out_json = DIST_DIR / "audit-data.json"
    out_json.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    write_auth_config()
    write_audit_api_config()

    step_sum = sum(s["step_count"] for s in data["skills"])
    totals = data["totals"]
    assert step_sum == totals["pasos"], f"pasos mismatch: {step_sum} != {totals['pasos']}"

    print(
        f"OK: {DIST_DIR} — "
        f"{totals['guardrails']} reglas, {totals['agentes']} agentes, "
        f"{totals['pasos']} pasos ({totals['items']} items auditable)"
    )


if __name__ == "__main__":
    main()
