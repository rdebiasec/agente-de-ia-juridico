#!/usr/bin/env python3
"""Smoke funcional del gate del Coordinador del Caso (local o producción).

Verifica sobre HTTP autenticado que la verificación de completitud sea un
invariante de runtime y no una promesa del prompt:

1. Un caso incompleto de alto riesgo queda en `awaiting_input`, con un único
   paso del gerente y sin especialistas.
2. Ese plan no se puede aprobar.
3. Un caso con los mínimos completos llega a `pending_approval` e incluye al
   especialista correspondiente.

Contraseña (plaintext) desde SMOKE_SITE_PASSWORD o
~/Backups/agente-juridico/{smoke.env,SITE_PASSWORD.txt}.

Uso:
  .venv/bin/python scripts/smoke_gerencia_prod.py --local
  .venv/bin/python scripts/smoke_gerencia_prod.py --prod
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from pathlib import Path

import httpx

VAULT = Path.home() / "Backups" / "agente-juridico"

MENSAJE_INCOMPLETO = "Redacte un memorial de impulso para la víctima."
MENSAJE_COMPLETO = (
    "Redacte memorial de impulso. Radicado 11001-60-00-2026-123456. "
    "La víctima denunció lesiones y aportó el relato. Tengo poder firmado. "
    "Última actuación: audiencia de imputación. Partes: víctima y procesado."
)
GERENTE = "coordinador_caso"


def _load_vault_password() -> str:
    if os.environ.get("SMOKE_SITE_PASSWORD"):
        return os.environ["SMOKE_SITE_PASSWORD"].strip()
    smoke = VAULT / "smoke.env"
    if smoke.is_file():
        for line in smoke.read_text(encoding="utf-8").splitlines():
            if line.startswith("SMOKE_SITE_PASSWORD="):
                return line.split("=", 1)[1].strip().strip("'\"")
    plain = VAULT / "SITE_PASSWORD.txt"
    if plain.is_file():
        return plain.read_text(encoding="utf-8").strip()
    return ""


def _plan_agents(plan: dict) -> list[str]:
    return [str(step.get("agent_id", "")) for step in plan.get("steps", [])]


def smoke_gerencia(base: str, *, username: str, password: str) -> dict:
    base = base.rstrip("/")
    out: dict = {"base": base, "ok": False, "checks": {}}
    suffix = uuid.uuid4().hex[:8]

    with httpx.Client(base_url=base, timeout=120.0, follow_redirects=False) as client:
        login = client.post(
            "/auth/login",
            json={
                "username": username,
                "password": password,
                "accept_privacy": True,
                "accept_sensitive_data": True,
            },
            headers={"content-type": "application/json"},
        )
        out["login"] = login.status_code
        if login.status_code != 200:
            out["error"] = f"login: {login.text[:200]}"
            return out

        incompleto = client.post(
            "/chat/plan",
            json={
                "message": MENSAJE_INCOMPLETO,
                "channel": "web",
                "user_id": f"smoke-gate-inc-{suffix}",
            },
        )
        if incompleto.status_code != 200:
            out["error"] = f"plan incompleto: HTTP {incompleto.status_code} {incompleto.text[:200]}"
            return out
        inc_body = incompleto.json()
        inc_plan = inc_body.get("plan", {})
        inc_agents = _plan_agents(inc_plan)
        out["checks"]["incompleto_awaiting_input"] = inc_body.get("status") == "awaiting_input"
        out["checks"]["incompleto_sin_especialistas"] = inc_agents == [GERENTE]
        out["checks"]["incompleto_reporta_faltantes"] = bool(
            inc_plan.get("triage_snapshot", {}).get("datos_faltantes_bloqueantes")
        )
        out["incompleto"] = {
            "status": inc_body.get("status"),
            "agents": inc_agents,
            "faltantes": inc_plan.get("triage_snapshot", {}).get("datos_faltantes_bloqueantes"),
        }

        aprobar = client.post(
            f"/chat/plan/{inc_body['plan_id']}/approve",
            json={"user_id": f"smoke-gate-inc-{suffix}"},
        )
        out["checks"]["incompleto_no_aprobable"] = aprobar.status_code >= 400
        out["aprobacion_bloqueada"] = {
            "http": aprobar.status_code,
            "detalle": aprobar.text[:160],
        }

        completo = client.post(
            "/chat/plan",
            json={
                "message": MENSAJE_COMPLETO,
                "channel": "web",
                "user_id": f"smoke-gate-ok-{suffix}",
            },
        )
        if completo.status_code != 200:
            out["error"] = f"plan completo: HTTP {completo.status_code} {completo.text[:200]}"
            return out
        ok_body = completo.json()
        ok_agents = _plan_agents(ok_body.get("plan", {}))
        out["checks"]["completo_pending_approval"] = ok_body.get("status") == "pending_approval"
        out["checks"]["completo_incluye_especialista"] = any(
            agent != GERENTE for agent in ok_agents
        )
        out["completo"] = {"status": ok_body.get("status"), "agents": ok_agents}

    out["ok"] = all(out["checks"].values())
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_true")
    parser.add_argument("--prod", action="store_true")
    parser.add_argument("--local-url", default=os.environ.get("SMOKE_BASE_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--prod-url", default="https://agente-de-ia-juridico.onrender.com")
    args = parser.parse_args()
    if not args.local and not args.prod:
        args.local = args.prod = True

    password = _load_vault_password()
    if not password:
        print(
            "ERROR: falta SMOKE_SITE_PASSWORD o ~/Backups/agente-juridico/SITE_PASSWORD.txt",
            file=sys.stderr,
        )
        return 2
    if password.startswith("pbkdf2_sha256$"):
        print("ERROR: la contraseña parece un hash; se necesita plaintext.", file=sys.stderr)
        return 2

    username = os.environ.get("SMOKE_SITE_USERNAME", "despacho")

    results = []
    if args.local:
        results.append(smoke_gerencia(args.local_url, username=username, password=password))
    if args.prod:
        results.append(smoke_gerencia(args.prod_url, username=username, password=password))

    print(json.dumps(results, indent=2, ensure_ascii=False))
    if not all(r.get("ok") for r in results):
        return 1
    print("SMOKE_GERENCIA_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
