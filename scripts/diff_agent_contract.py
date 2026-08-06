#!/usr/bin/env python3
"""F-04 — Diff contractual prompt ↔ guardrails I/O/T ↔ schema.

Detecta drift enforceable (nombres de schema, mención fuentes_kb, tools).
No edita archivos; exit 1 si hay drift P0 (schema ausente en prompt/output).

Uso:
  python scripts/diff_agent_contract.py
  python scripts/diff_agent_contract.py --json
  python scripts/diff_agent_contract.py --agent analista_responsabilidad_tipicidad
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PROMPTS = ROOT / "agente" / "prompts" / "agents"
GUARDRAILS = ROOT / "config" / "guardrails" / "agents"

# agent_id → clase Pydantic esperada (salida estructurada).
# coordinador_caso: chat POC en prosa; TriageResult solo planner (no exigir en prompt).
AGENT_SCHEMA: dict[str, str | None] = {
    "coordinador_caso": None,
    "analista_cronologia_hechos": "CronologiaPenal",
    "analista_responsabilidad_tipicidad": "MatrizTipicidad",
    "analista_ruta_procesal": "RutaProcesalLey906",
    "analista_representacion_victimas": "RepresentacionVictimas",
    "analista_evidencia": "InventarioEvidencia",
    "analista_audiencias": "PreparacionAudiencia",
    "redactor_documentos_juridicos": "BorradorDocumentoPenal",
    "analista_seguimiento_procesal": "SeguimientoProcesal",
    "analista_calidad_juridica": "DictamenCalidad",
}

SCHEMA_EXPECTS_FUENTES_KB = {
    k for k, v in AGENT_SCHEMA.items() if v and k != "coordinador_caso"
}


def _schema_classes() -> set[str]:
    import src.agents.schemas as schemas

    return {
        name
        for name, obj in vars(schemas).items()
        if isinstance(obj, type) and hasattr(obj, "model_fields")
    }


def diff_agent(agent_id: str, *, schema_names: set[str]) -> dict:
    prompt_path = PROMPTS / f"{agent_id}.md"
    out_path = GUARDRAILS / agent_id / "output.md"
    tools_path = GUARDRAILS / agent_id / "tools.md"
    in_path = GUARDRAILS / agent_id / "input.md"
    expected = AGENT_SCHEMA.get(agent_id)

    issues: list[dict] = []
    prompt = prompt_path.read_text(encoding="utf-8") if prompt_path.is_file() else ""
    output = out_path.read_text(encoding="utf-8") if out_path.is_file() else ""
    tools = tools_path.read_text(encoding="utf-8") if tools_path.is_file() else ""

    if not prompt_path.is_file():
        issues.append({"sev": "P0", "msg": "falta prompt"})
    if not out_path.is_file():
        issues.append({"sev": "P0", "msg": "falta guardrail output.md"})
    if not tools_path.is_file():
        issues.append({"sev": "P1", "msg": "falta guardrail tools.md"})
    if not in_path.is_file():
        issues.append({"sev": "P1", "msg": "falta guardrail input.md"})

    if expected:
        if expected not in schema_names:
            issues.append(
                {"sev": "P0", "msg": f"schema {expected} no existe en schemas.py"}
            )
        if expected not in prompt:
            issues.append(
                {"sev": "P0", "msg": f"prompt no menciona schema `{expected}`"}
            )
        if expected not in output:
            issues.append(
                {"sev": "P0", "msg": f"output.md no menciona schema `{expected}`"}
            )

    if agent_id in SCHEMA_EXPECTS_FUENTES_KB:
        if "fuentes_kb" not in prompt:
            issues.append({"sev": "P1", "msg": "prompt sin fuentes_kb"})
        if "fuentes_kb" not in output and "fuentes_kb" not in prompt:
            issues.append({"sev": "P1", "msg": "contrato output sin fuentes_kb"})

    for name in ("buscar_en_conocimiento", "leer_normas_clave", "leer_area_derecho"):
        if name in prompt and tools and "function" in tools.lower():
            if not re.search(rf"`{name}`|{name}", tools):
                issues.append(
                    {
                        "sev": "P2",
                        "msg": f"prompt usa `{name}` pero tools.md no la lista",
                    }
                )

    p0 = sum(1 for i in issues if i["sev"] == "P0")
    return {
        "agent_id": agent_id,
        "schema": expected,
        "files": {
            "prompt": prompt_path.is_file(),
            "input": in_path.is_file(),
            "output": out_path.is_file(),
            "tools": tools_path.is_file(),
        },
        "issues": issues,
        "ok": p0 == 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--agent", default="")
    args = parser.parse_args()

    schema_names = _schema_classes()
    agents = [args.agent] if args.agent else sorted(AGENT_SCHEMA.keys())
    rows = [diff_agent(a, schema_names=schema_names) for a in agents]
    failed = [r for r in rows if not r["ok"]]
    payload = {
        "total": len(rows),
        "failed_p0": len(failed),
        "agents": rows,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"agents={payload['total']} failed_p0={payload['failed_p0']}")
        for r in rows:
            status = "OK" if r["ok"] else "DRIFT"
            n = len(r["issues"])
            print(f"  [{status}] {r['agent_id']} schema={r['schema']} issues={n}")
            for iss in r["issues"]:
                print(f"      {iss['sev']}: {iss['msg']}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
