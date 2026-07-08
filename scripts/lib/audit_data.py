"""Catálogo JSON del portal de auditoría (fuente compartida: build, API y runtime)."""

from __future__ import annotations

from datetime import datetime, timezone

from lib.catalogo_aprobacion import (
    AGENTS,
    CATEGORY_DESCRIPTIONS,
    GUARDRAILS,
    agent_group,
    agent_skills_map,
    agent_titulo,
    build_skill_steps,
    guia_audit_key,
    infer_destinatario,
    load_skills_catalog,
    skill_flujo_pasos,
    skill_guardrails_list,
    skill_titulo_upper,
    skill_tools_display,
    skill_tools_list,
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
        tools = skill_tools_list(data)
        guardrails = skill_guardrails_list(data)
        source_path = data.get("path") or f".cursor/skills/{sid}/SKILL.md"
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
                "purpose": (data.get("purpose") or "").strip(),
                "inputs": (data.get("inputs") or "").strip(),
                "outputs": (data.get("outputs") or "").strip(),
                "tier": (data.get("tier") or "").strip(),
                "rol": (data.get("rol") or "").strip(),
                "no_duplicar": (data.get("no_duplicar") or "").strip(),
                "handoff": (data.get("handoff") or "").strip(),
                "riesgo": (data.get("riesgo") or "").strip(),
                "agents": agent_ids,
                "agentes_ejecutores": [agent_titulo(aid) for aid in agent_ids],
                "destinatario": infer_destinatario(agent_ids),
                "flujo_pasos": skill_flujo_pasos(steps),
                "step_count": len(steps),
                "steps": steps,
                "steps_missing": len(steps) == 0,
                "tools": tools,
                "tools_text": skill_tools_display(data),
                "guardrails": guardrails,
                "source_path": source_path,
                "audit_keys": {
                    "instruccion": guia_audit_key(sid, "instruccion"),
                    "tools": guia_audit_key(sid, "tools"),
                    "guardrails": guia_audit_key(sid, "guardrails"),
                },
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
    guias_contexto_total = len(skills) * 3
    items_total = guardrails_n + agentes_n + guias_contexto_total + pasos_total

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return {
        "version": "2.1",
        "generated_at": now,
        "intro": {
            "agentes": agentes_n,
            "skills": len(skills),
            "guias_operativas": len(skills),
            "guias_contexto": guias_contexto_total,
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
            "guias_contexto": guias_contexto_total,
            "pasos": pasos_total,
            "items": items_total,
        },
    }
