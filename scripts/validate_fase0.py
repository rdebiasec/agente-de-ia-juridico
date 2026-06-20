#!/usr/bin/env python3
"""Valida cobertura REQ Fase 0 vs estructura del proyecto."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQ_FILE = ROOT / "agente" / "requisitos" / "requisitos_asistente.json"
FASE0 = ROOT / "agente" / "fases" / "FASE_0.md"
KB = ROOT / "agente" / "conocimiento"
AGENTS = ROOT / "src" / "agents"

KB_EXPECTED = [
    "civil.md",
    "familia.md",
    "societario.md",
    "penal.md",
    "consumidor.md",
    "comercial.md",
    "laboral.md",
    "normas-clave.md",
]

errors: list[str] = []

if not REQ_FILE.exists():
    errors.append(f"Falta {REQ_FILE}")
else:
    data = json.loads(REQ_FILE.read_text())
    fase0 = [r for r in data["requisitos"] if r["fase"] == 0]
    if len(fase0) != 11:
        errors.append(f"Fase 0 debe tener 11 REQ, tiene {len(fase0)}")

if not FASE0.exists():
    errors.append(f"Falta {FASE0}")

for f in KB_EXPECTED:
    if not (KB / f).exists():
        errors.append(f"Falta KB: {f}")

for module in ("orchestrator.py", "runner.py", "guardrails.py"):
    if not (AGENTS / module).exists():
        errors.append(f"Falta agente: {module}")

if errors:
    print("VALIDACIÓN FALLIDA:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print("OK: Fase 0 — 11 REQ, KB, agentes y fases presentes.")
