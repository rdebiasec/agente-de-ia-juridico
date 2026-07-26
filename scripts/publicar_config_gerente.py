#!/usr/bin/env python3
"""Publica en el config store activo el prompt y los guardrails del Gerente del Caso.

Postgres es autoritativo en runtime, así que un archivo en disco no cambia el
comportamiento del agente hasta que se publica. Este script usa la misma vía
auditada del portal (`POST /api/audit/config/save`): queda versionado, con autor
y nota, y es reversible con `/restore`.

Contraseña desde SMOKE_SITE_PASSWORD o ~/Backups/agente-juridico/{smoke.env,SITE_PASSWORD.txt}.

Uso:
  .venv/bin/python scripts/publicar_config_gerente.py --prod --dry-run
  .venv/bin/python scripts/publicar_config_gerente.py --prod --apply
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
VAULT = Path.home() / "Backups" / "agente-juridico"
HEADER_RE = re.compile(r"^<!--\s*config-version:.*?-->\s*", re.DOTALL)

ITEMS: list[tuple[str, str, Path]] = [
    (
        "prompt",
        "coordinador_expediente_penal",
        ROOT / "agente/prompts/agents/coordinador_expediente_penal.md",
    ),
    (
        "agent_guardrail",
        "coordinador_expediente_penal__input",
        ROOT / "config/guardrails/agents/coordinador_expediente_penal/input.md",
    ),
    (
        "agent_guardrail",
        "coordinador_expediente_penal__output",
        ROOT / "config/guardrails/agents/coordinador_expediente_penal/output.md",
    ),
    (
        "agent_guardrail",
        "coordinador_expediente_penal__tools",
        ROOT / "config/guardrails/agents/coordinador_expediente_penal/tools.md",
    ),
]


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


def _body_without_header(path: Path) -> str:
    return HEADER_RE.sub("", path.read_text(encoding="utf-8"), count=1).strip()


def publish(base: str, *, email: str, password: str, pin: str, apply: bool) -> dict:
    base = base.rstrip("/")
    out: dict = {"base": base, "apply": apply, "items": [], "ok": False}

    with httpx.Client(base_url=base, timeout=90.0, follow_redirects=True) as client:
        pre = client.post("/api/audit/prelogin", json={"email": email, "password": password})
        if pre.status_code != 200:
            out["error"] = f"prelogin: {pre.text[:200]}"
            return out
        body: dict = {
            "email": email,
            "password": password,
            "accept_privacy": True,
            "accept_sensitive_data": True,
        }
        if pre.json().get("needs_pin_setup"):
            body["new_pin"] = pin
        else:
            body["pin"] = pin
        login = client.post("/api/audit/login", json=body)
        if login.status_code != 200:
            out["error"] = f"login: {login.text[:200]}"
            return out

        for kind, key, path in ITEMS:
            entry: dict = {"kind": kind, "key": key}
            if not path.is_file():
                entry["error"] = f"falta {path}"
                out["items"].append(entry)
                continue

            content = _body_without_header(path)
            current = client.get(f"/api/audit/config/{kind}/{key}")
            if current.status_code != 200:
                entry["error"] = f"lectura: HTTP {current.status_code} {current.text[:160]}"
                out["items"].append(entry)
                continue
            active = current.json()
            entry["version_activa"] = active.get("version")
            entry["ya_publicado"] = (active.get("content") or "").strip() == content

            if entry["ya_publicado"] or not apply:
                out["items"].append(entry)
                continue

            saved = client.post(
                "/api/audit/config/save",
                json={
                    "kind": kind,
                    "key": key,
                    "content": content,
                    "expected_version": active.get("version"),
                    "note": "publicación Gerente del Caso Penal desde archivos revisados",
                },
            )
            if saved.status_code != 200:
                entry["error"] = f"save: HTTP {saved.status_code} {saved.text[:200]}"
            else:
                entry["version_nueva"] = saved.json().get("version")
            out["items"].append(entry)

    out["ok"] = all("error" not in item for item in out["items"])
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_true")
    parser.add_argument("--prod", action="store_true")
    parser.add_argument("--apply", action="store_true", help="sin esta bandera solo reporta")
    parser.add_argument("--local-url", default=os.environ.get("SMOKE_BASE_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--prod-url", default="https://agente-de-ia-juridico.onrender.com")
    args = parser.parse_args()
    if not args.local and not args.prod:
        args.prod = True

    password = _load_vault_password()
    if not password:
        print("ERROR: falta SMOKE_SITE_PASSWORD o el archivo de bóveda.", file=sys.stderr)
        return 2

    email = os.environ.get("SMOKE_AUDIT_EMAIL", "smoke.audit@dbxsolutions.com")
    pin = os.environ.get("SMOKE_AUDIT_PIN", "654321")

    results = []
    if args.local:
        results.append(publish(args.local_url, email=email, password=password, pin=pin, apply=args.apply))
    if args.prod:
        results.append(publish(args.prod_url, email=email, password=password, pin=pin, apply=args.apply))

    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0 if all(r.get("ok") for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
