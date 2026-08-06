#!/usr/bin/env python3
"""Valida la estructura de la firma virtual jurídica (Fases A y B)."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQ_FILE = ROOT / "agente" / "requisitos" / "requisitos_asistente.json"
PROMPT = ROOT / "agente" / "prompts" / "sistema.md"
KB = ROOT / "agente" / "conocimiento"
AGENTS = ROOT / "src" / "agents"
GATEWAY = ROOT / "src" / "gateway"
STORAGE = ROOT / "src" / "storage"
HITL = ROOT / "src" / "hitl"
SERVICES = ROOT / "src" / "services"

KB_EXPECTED = [
    "penal.md",
    "normas-clave.md",
    "proceso-penal-906.md",
]

# REQ-038…042 (acciones de tutela) fueron retirados del producto el 2026-08-03.
REQ_ACTIVOS_ESPERADOS = 45
REQ_RETIRADOS = {f"REQ-{n:03d}" for n in range(38, 43)}

errors: list[str] = []

if not REQ_FILE.exists():
    errors.append(f"Falta {REQ_FILE}")
else:
    data = json.loads(REQ_FILE.read_text())
    requisitos = data["requisitos"]
    ids = {r["id"] for r in requisitos}
    if len(requisitos) != REQ_ACTIVOS_ESPERADOS:
        errors.append(
            f"Deben existir {REQ_ACTIVOS_ESPERADOS} REQ activos, hay {len(requisitos)}"
        )
    if data.get("total") != len(requisitos):
        errors.append(
            f"requisitos_asistente.json: 'total' ({data.get('total')}) "
            f"no coincide con los REQ listados ({len(requisitos)})"
        )
    reaparecidos = sorted(ids & REQ_RETIRADOS)
    if reaparecidos:
        errors.append(f"REQ retirados presentes de nuevo: {', '.join(reaparecidos)}")

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

# Fase B: persistencia, HITL y servicios.
for module in ("base.py", "memory.py", "sql.py", "models.py", "__init__.py"):
    if not (STORAGE / module).exists():
        errors.append(f"Falta storage: {module}")

for module in ("drafts.py", "slack_review.py"):
    if not (HITL / module).exists():
        errors.append(f"Falta hitl: {module}")

for module in ("plazos.py", "documentos.py", "rag.py", "scheduler.py"):
    if not (SERVICES / module).exists():
        errors.append(f"Falta services: {module}")

if not (ROOT / "alembic.ini").exists() or not (ROOT / "migrations" / "env.py").exists():
    errors.append("Falta configuración de Alembic (alembic.ini / migrations/env.py)")

for api in ("firma_api.py", "slack_interactivity.py"):
    if not (GATEWAY / api).exists():
        errors.append(f"Falta gateway API: {api}")

if errors:
    print("VALIDACIÓN FALLIDA:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print(
    f"OK: firma virtual (A+B) — {REQ_ACTIVOS_ESPERADOS} REQ activos, persona, KB, agentes, "
    "esquemas, persistencia, HITL y servicios presentes."
)
