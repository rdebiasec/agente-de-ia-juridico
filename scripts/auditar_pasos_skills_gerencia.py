#!/usr/bin/env python3
"""Auditoría gerencial de pasos por skill — matriz v2 con reasoning y pasos variables."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from lib.catalogo_aprobacion import (  # noqa: E402
    AGENTS,
    CATEGORY_DESCRIPTIONS,
    LISTA,
    agent_skills_map,
    load_skills_catalog,
)
from lib.pasos_gerencia_matrix import get_proposed_steps, get_skill_pasos, validate_matrix  # noqa: E402
from lib.pasos_propuestos_gerencia import (  # noqa: E402
    CATEGORY_DICTAMENS,
    CATEGORY_ORDER,
    PRIORITY_SKILLS,
    skill_priority,
)

OUT = ROOT / "docs" / "auditoria" / "auditoria-pasos-skills-gerencia-penal.md"


def _tokens(text: str) -> set[str]:
    return {w.lower() for w in re.findall(r"[a-záéíóúñü0-9]+", text, re.I) if len(w) > 2}


def _step_texts(steps: list) -> list[str]:
    out: list[str] = []
    for s in steps:
        if isinstance(s, dict):
            out.append(str(s.get("text", "")))
        else:
            out.append(str(s))
    return out


def alignment_score(instruccion: str, purpose: str, steps: list) -> float:
    ref = _tokens(f"{instruccion} {purpose}")
    step_t = _tokens(" ".join(_step_texts(steps)))
    if not ref or not step_t:
        return 0.0
    return len(ref & step_t) / len(ref)


def apply_steps_to_lista(proposed: dict[str, list[str]]) -> int:
    text = LISTA.read_text(encoding="utf-8")
    updated = 0
    for sid, steps in proposed.items():
        steps_block = "\n".join(f"    {i}. {s}" for i, s in enumerate(steps, 1)) + "\n"
        pattern = (
            rf"(- `{re.escape(sid)}`\n"
            rf"(?:  - [^\n]+\n)*?)"
            rf"  - Pasos(?: \([^)]+\))?:\n"
            rf"(?:(?:    \d+\. .+\n)|(?:  - Pasos(?: \([^)]+\))?:\n(?:    \d+\. .+\n)+))*"
        )
        repl = rf"\1  - Pasos:\n{steps_block}"
        new_text, n = re.subn(pattern, repl, text, count=1)
        if n:
            text = new_text
            updated += 1
    LISTA.write_text(text, encoding="utf-8")
    return updated


def step_histogram(skills: dict[str, dict], use_proposed: bool = False) -> dict[int, int]:
    c: Counter[int] = Counter()
    for sid, data in skills.items():
        if use_proposed:
            n = len(get_proposed_steps(sid, data.get("category", ""), data.get("instruccion", "")))
        else:
            n = len(data.get("steps", []))
        c[n] += 1
    return dict(sorted(c.items()))


def generate_markdown(skills: dict[str, dict], agent_map: dict[str, list[str]]) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines: list[str] = []
    w = lines.append

    hist_antes = step_histogram(skills, use_proposed=False)
    hist_prop = step_histogram(skills, use_proposed=True)
    total_antes = sum(len(d.get("steps", [])) for d in skills.values())
    total_prop = sum(
        len(get_proposed_steps(sid, d.get("category", ""), d.get("instruccion", "")))
        for sid, d in skills.items()
    )

    w("# Auditoría gerencial de pasos por skill — Penal víctimas (Colombia) v2")
    w("")
    w(f"**Generado:** {now}  ")
    w("**Audiencia:** Gerencia del despacho y abogada líder  ")
    w("**Fuente canónica:** `docs/canon/lista-aprobacion-agentes-skills-pasos.md` + `scripts/lib/pasos_gerencia_matrix.py`")
    w("")
    w("---")
    w("")
    w("## Resumen ejecutivo")
    w("")
    w(f"- **Skills auditados:** {len(skills)}")
    w(f"- **Pasos totales (catálogo al auditar):** {total_antes}")
    w(f"- **Pasos totales (propuesta gerencia v2):** {total_prop}")
    w(f"- **Δ pasos:** {total_prop - total_antes:+d}")
    w("")
    w("### Distribución por cantidad de pasos (histograma)")
    w("")
    w("| Pasos/skill | Antes (n skills) | Propuesta v2 (n skills) |")
    w("|---:|---:|---:|")
    all_sizes = sorted(set(hist_antes) | set(hist_prop))
    for n in all_sizes:
        w(f"| {n} | {hist_antes.get(n, 0)} | {hist_prop.get(n, 0)} |")
    w("")
    w(f"- **Tallas distintas en propuesta:** {len(hist_prop)} (mín. 2, sin tope fijo)")
    w(f"- **Skill con más pasos:** `{max(skills, key=lambda s: len(get_proposed_steps(s, skills[s].get('category',''), skills[s].get('instruccion',''))))}`")
    w("")
    suben = bajan = igual = 0
    for sid, data in skills.items():
        a = len(data.get("steps", []))
        p = len(get_proposed_steps(sid, data.get("category", ""), data.get("instruccion", "")))
        if p > a:
            suben += 1
        elif p < a:
            bajan += 1
        else:
            igual += 1
    w(f"- **Skills que suben pasos:** {suben} · **bajan:** {bajan} · **igual:** {igual}")
    w("")
    w("---")
    w("")
    w("## Fase 1 — Matriz de 90 skills (con reasoning gerencial)")
    w("")

    by_category: dict[str, list[str]] = defaultdict(list)
    for sid, data in skills.items():
        by_category[data.get("category", "Sin categoría")].append(sid)

    for cat in CATEGORY_ORDER:
        w(f"### {cat}")
        w("")
        for sid in sorted(by_category.get(cat, [])):
            data = skills[sid]
            steps = data.get("steps", [])
            meta = get_skill_pasos(sid)
            prop = meta.pasos
            score = alignment_score(data.get("instruccion", ""), data.get("purpose", ""), steps)
            w(f"#### `{sid}`")
            w("")
            w(f"- **Categoría:** {cat}")
            w(f"- **Agentes:** {', '.join(f'`{a}`' for a in data.get('agents', []))}")
            w(f"- **Prioridad:** {skill_priority(sid)}")
            w(f"- **Tier gerencial:** `{meta.tier}`")
            w(f"- **Instrucción tipo:** {data.get('instruccion', '')}")
            w(f"- **Purpose (SKILL.md):** {data.get('purpose', '')}")
            w(f"- **Pasos:** {len(steps)} → **{len(prop)}** (propuesta v2)")
            w(f"- **Score alineación (pasos actuales vs instrucción):** {score:.2f}")
            w(f"- **Reasoning gerencial:** {meta.reasoning}")
            w(f"- **Por qué {len(prop)} pasos:** {meta.por_que_n}")
            w(f"- **Riesgos si se recortan pasos:** {meta.riesgos_si_faltan}")
            w("- **Pasos actuales (al auditar):**")
            for i, s in enumerate(_step_texts(steps), 1):
                w(f"  {i}. {s}")
            w("- **Pasos propuestos v2:**")
            for i, s in enumerate(prop, 1):
                w(f"  {i}. {s}")
            w("- **Aprobación abogada:** [ ] Pendiente")
            w("")

    w("---")
    w("")
    w("## Fase 2 — Dictamen gerencial por categoría")
    w("")
    for i, cat in enumerate(CATEGORY_ORDER, 1):
        d = CATEGORY_DICTAMENS[cat]
        w(f"### {i}. {cat}")
        w("")
        w(f"*{CATEGORY_DESCRIPTIONS.get(cat, '')}*")
        w("")
        w(f"- **Propósito plantilla anterior:** {d['proposito_plantilla']}")
        w(f"- **Skills que encajaban:** {d['encajan']}")
        w(f"- **Skills que no encajaban:** {d['no_encajan']}")
        w(f"- **Faltaba a nivel categoría:** {d['faltan']}")
        w(f"- **Sobraba:** {d['sobran']}")
        w(f"- **Dictamen:** **{d['dictamen']}**")
        w("")

    w("---")
    w("")
    w("## Fase 3 — Prioridad P0/P1")
    w("")
    for level in ("P0", "P1"):
        w(f"### {level}")
        w("")
        for sid in PRIORITY_SKILLS[level]:
            meta = get_skill_pasos(sid)
            w(f"#### `{sid}` — tier `{meta.tier}`, **{len(meta.pasos)} pasos**")
            w("")
            w(f"- **Reasoning:** {meta.reasoning}")
            for i, s in enumerate(meta.pasos, 1):
                w(f"  {i}. {s}")
            w("- **Aprobación abogada:** [ ] Pendiente")
            w("")

    w("---")
    w("")
    w("## Resumen por agente")
    w("")
    for agent in AGENTS:
        aid = agent["id"]
        assigned = agent_map.get(aid, [])
        w(f"### `{aid}` — {agent['nombre_corto']}")
        w(f"- **Skills:** {len(assigned)} · **Flujo:** {agent['proposito']}")
        w("")

    return "\n".join(lines)


def run_check(skills: dict[str, dict]) -> int:
    errors = []
    for sid, data in skills.items():
        prop = get_proposed_steps(sid, data.get("category", ""), data.get("instruccion", ""))
        if _step_texts(data.get("steps", [])) != prop:
            errors.append(sid)
    if errors:
        print(f"CHECK FAIL: {len(errors)} skills (ej. {errors[:3]})")
        return 1
    validate_matrix()
    print(f"CHECK OK: {len(skills)} skills + matriz variable validada")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Auditoría gerencial pasos por skill v2")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--regenerar", action="store_true")
    args = parser.parse_args()

    validate_matrix()
    skills = load_skills_catalog()
    agent_map = agent_skills_map(skills)

    if args.check:
        return run_check(skills)

    proposed = {
        sid: get_proposed_steps(sid, d.get("category", ""), d.get("instruccion", ""))
        for sid, d in skills.items()
    }

    md = generate_markdown(skills, agent_map)
    OUT.write_text(md, encoding="utf-8")
    if not args.apply:
        c = Counter(len(v) for v in proposed.values())
        print(f"OK: {OUT} — distribución {dict(sorted(c.items()))}, total {sum(c.values())} pasos")

    if args.apply:
        n = apply_steps_to_lista(proposed)
        print(f"OK: lista-aprobacion — {n}/{len(proposed)} skills")
        skills = load_skills_catalog()
        md = generate_markdown(skills, agent_skills_map(skills))
        OUT.write_text(md, encoding="utf-8")

    if args.apply and args.regenerar:
        subprocess.run([sys.executable, str(ROOT / "scripts" / "generar_documento_unico_aprobacion.py")], check=True)
        subprocess.run([sys.executable, str(ROOT / "scripts" / "generar_audit_portal.py")], check=True)

    if args.apply:
        return run_check(skills)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
