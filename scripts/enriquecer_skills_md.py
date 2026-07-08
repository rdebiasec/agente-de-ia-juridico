#!/usr/bin/env python3
"""Enriquece SKILL.md sin ## Steps usando pasos_gerencia_matrix y catálogo."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from lib.catalogo_aprobacion import (  # noqa: E402
    AGENTS,
    CATEGORY_DESCRIPTIONS,
    SKILLS_DIR,
    load_skills_catalog,
    skill_tools_list,
)
from lib.pasos_gerencia_matrix import get_skill_pasos  # noqa: E402

PRIMARY: dict[str, str] = {
    "analista_representacion_victimas": "construir_teoria_caso_victima",
    "gestor_evidencia_y_soporte_probatorio": "inventariar_evidencia",
    "preparador_estrategico_audiencias_penales": "preparar_preguntas_audiencia",
    "redactor_documentos_juridicos_penales": "redactar_memorial_penal",
    "gestor_seguimiento_procesal_penal": "monitorear_radicado",
    "evaluador_derechos_fundamentales_tutela": "evaluar_procedencia_tutela",
    "analista_calidad_juridica": "revisar_coherencia_estrategica",
}

GUARDRAILS_STD = """## Guardrails (g1–g10)
- **g1:** No inventar hechos, normas, sentencias ni radicados.
- **g2:** Pedir datos faltantes (incl. plazos y etapa Ley 906) antes de concluir.
- **g3:** Separar hecho confirmado, narrado, inferido y pendiente.
- **g4:** HITL obligatorio en escritos, estrategia, tutela y reportes a cliente.
- **g5:** No revictimizar; lenguaje centrado en derechos de la víctima.
- **g6:** Minimizar datos sensibles innecesarios.
- **g7:** Fuera de alcance si no es penal-víctimas Colombia.
- **g8:** Aviso de revisión profesional en cada entrega.
- **g9:** Sin plazo o etapa Ley 906 verificados, no certificar oportunidad.
- **g10:** No sugerir descarte de evidencia sin revisar custodia y preservación."""

EXTRA_HITL: dict[str, str] = {
    "redactar_tutela_penal_preliminar": "- **Gate:** Solo si `evaluar_procedencia_tutela` recomendó tutela preliminarmente.",
    "preparar_borrador_tutela_preliminar": "- **Gate:** Requiere dictamen previo de procedencia tutela.",
    "evaluar_procedencia_tutela": "- **g4:** Dictamen preliminar; no autoriza radicación sin abogado.",
    "clasificar_aprobacion_juridica": "- **g4:** Último filtro antes de salida externa.",
}


def _frontmatter(body: str) -> tuple[str, str]:
    if not body.startswith("---"):
        return "", body
    parts = body.split("---", 2)
    if len(parts) < 3:
        return "", body
    return f"---{parts[1]}---", parts[2]


def _needs_enrich(text: str) -> bool:
    return "## Steps" not in text or "Depende del flujo" in text


def _agents_block(agents: list[str], sid: str) -> str:
    lines = ["## Used By Agents"]
    for a in agents:
        mark = " (skill primario del agente)" if PRIMARY.get(a) == sid else ""
        lines.append(f"- `{a}`{mark}")
    return "\n".join(lines)


def _tools_block(tools: list[str]) -> str:
    lines = ["## Tools"]
    if tools:
        lines.extend(f"- `{t}`" for t in tools)
    else:
        lines.append("- Sin herramientas obligatorias")
    return "\n".join(lines)


def _inputs_outputs(sid: str, category: str, instruccion: str) -> tuple[str, str]:
    inputs = [
        "- Insumos del expediente y del turno (documentos, relatos, radicado).",
        "- Etapa procesal y objetivo del análisis o documento.",
        "- Salidas previas de agentes upstream cuando existan.",
    ]
    outputs = [
        "- Salida estructurada según propósito del skill.",
        "- Elementos sin fuente marcados `[PENDIENTE DE VERIFICAR]`.",
        "- Recomendación de siguiente agente o skill si aplica.",
    ]
    if "redactar" in sid or "redaccion" in category.lower():
        outputs.append("- Etiqueta: `BORRADOR — NO RADICAR SIN FIRMA`.")
    if "tutela" in sid or "constitucional" in category.lower():
        outputs.append("- Etiqueta: `PRELIMINAR CONSTITUCIONAL — NO TUTELA SIN EVALUADOR`.")
    if "calidad" in category.lower():
        outputs.append("- Dictamen: aprobable | con cambios | rechazar | escalar.")
    return "\n".join(inputs), "\n".join(outputs)


def build_skill_md(sid: str, data: dict) -> str:
    meta = get_skill_pasos(sid)
    path = SKILLS_DIR / sid / "SKILL.md"
    raw = path.read_text(encoding="utf-8")
    fm, _ = _frontmatter(raw)

    if not fm:
        name = sid.replace("_", "-")
        desc = data.get("instruccion") or data.get("purpose") or sid
        fm = f"""---
name: {name}
description: Skill penal-victimas: {desc}. Use when the workflow requires `{sid}`.
disable-model-invocation: true
---"""

    category = data.get("category") or "Skills transversales"
    purpose = (data.get("purpose") or data.get("instruccion") or sid).strip()
    if purpose and not purpose[0].isupper():
        purpose = purpose[0].upper() + purpose[1:]

    agents = data.get("agents") or []
    primary = next((a for a, ps in PRIMARY.items() if ps == sid), None)
    role_lines = []
    if primary:
        role_lines.append(f"## Rol en {primary}")
        role_lines.append(f"Skill primario o núcleo del agente `{primary}`.")

    steps_lines = ["## Steps"]
    for i, step in enumerate(meta.pasos, 1):
        steps_lines.append(f"{i}. {step}")

    inputs, outputs = _inputs_outputs(sid, category, data.get("instruccion", ""))
    tools = skill_tools_list(data)
    extra = EXTRA_HITL.get(sid, "")

    body = f"""
# {sid}

## Scope
- Category: `{category}`
- Skill ID: `{sid}`
- Tier: `{meta.tier}`

{_agents_block(agents, sid)}

## Purpose
{purpose}

{chr(10).join(role_lines)}

## Inputs
{inputs}

## Outputs
{outputs}

{chr(10).join(steps_lines)}

{_tools_block(tools)}

{GUARDRAILS_STD}
{extra}

## Riesgo si se omite
{meta.riesgos_si_faltan}
"""
    return fm + "\n" + body.strip() + "\n"


def main() -> int:
    catalog = load_skills_catalog()
    updated = 0
    skipped = 0
    for sid, data in sorted(catalog.items()):
        path = SKILLS_DIR / sid / "SKILL.md"
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if not _needs_enrich(text):
            skipped += 1
            continue
        path.write_text(build_skill_md(sid, data), encoding="utf-8")
        updated += 1
    print(f"OK: {updated} skills enriquecidos, {skipped} ya completos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
