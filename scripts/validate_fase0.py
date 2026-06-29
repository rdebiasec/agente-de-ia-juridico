#!/usr/bin/env python3
"""Valida la estructura base de la firma virtual jurídica (Fase A)."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQ_FILE = ROOT / "agente" / "requisitos" / "requisitos_asistente.json"
PROMPT = ROOT / "agente" / "prompts" / "sistema.md"
KB = ROOT / "agente" / "conocimiento"
AGENTS = ROOT / "src" / "agents"
GATEWAY = ROOT / "src" / "gateway"

KB_EXPECTED = [
    "civil.md",
    "familia.md",
    "societario.md",
    "penal.md",
    "consumidor.md",
    "comercial.md",
    "laboral.md",
    "normas-clave.md",
    "proceso-civil-cgp.md",
    "proceso-penal-906.md",
]

errors: list[str] = []

if not REQ_FILE.exists():
    errors.append(f"Falta {REQ_FILE}")
else:
    data = json.loads(REQ_FILE.read_text())
    if len(data["requisitos"]) != 50:
        errors.append(f"Deben existir 50 REQ, hay {len(data['requisitos'])}")

if not PROMPT.exists():
    errors.append("Falta agente/prompts/sistema.md (persona del experto)")

for f in KB_EXPECTED:
    if not (KB / f).exists():
        errors.append(f"Falta KB: {f}")

for module in ("orchestrator.py", "runner.py", "guardrails.py", "schemas.py"):
    if not (AGENTS / module).exists():
        errors.append(f"Falta agente: {module}")

if not (GATEWAY / "expediente.py").exists():
    errors.append("Falta src/gateway/expediente.py")

if errors:
    print("VALIDACIÓN FALLIDA:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print("OK: firma virtual — 50 REQ, persona, KB con playbooks, agentes, esquemas y expediente presentes.")
