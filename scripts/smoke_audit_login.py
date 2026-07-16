#!/usr/bin/env python3
"""Smoke de login auditoría (local y/o prod): gate session + progreso.

Lee plaintext de:
  SMOKE_SITE_PASSWORD env, o ~/Backups/agente-juridico/smoke.env / SITE_PASSWORD.txt

Uso:
  .venv/bin/python scripts/smoke_audit_login.py --local
  .venv/bin/python scripts/smoke_audit_login.py --prod
  .venv/bin/python scripts/smoke_audit_login.py --local --prod
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
VAULT = Path.home() / "Backups" / "agente-juridico"


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


def smoke_login(base: str, *, email: str, password: str, pin: str) -> dict:
    base = base.rstrip("/")
    out: dict = {"base": base, "ok": False}
    with httpx.Client(base_url=base, timeout=45.0, follow_redirects=True) as client:
        health = client.get("/health")
        out["health"] = health.status_code
        if health.status_code != 200:
            out["error"] = f"health HTTP {health.status_code}"
            return out

        gate = client.get("/auditoria/")
        out["gate_html"] = gate.status_code == 200 and "audit-auth-gate" in gate.text

        pre = client.post("/api/audit/prelogin", json={"email": email, "password": password})
        out["prelogin"] = pre.status_code
        if pre.status_code != 200:
            out["error"] = f"prelogin: {pre.text[:200]}"
            return out
        pre_body = pre.json()

        body: dict = {
            "email": email,
            "password": password,
            "accept_privacy": True,
            "accept_sensitive_data": True,
        }
        if pre_body.get("needs_pin_setup"):
            body["new_pin"] = pin
        else:
            body["pin"] = pin

        login = client.post("/api/audit/login", json=body)
        out["login"] = login.status_code
        if login.status_code != 200:
            out["error"] = f"login: {login.text[:200]}"
            return out

        session = client.get("/api/audit/session")
        out["session"] = session.status_code
        sess = session.json() if session.status_code == 200 else {}
        out["authenticated"] = bool(sess.get("authenticated"))
        out["email"] = sess.get("email")

        progress = client.get("/api/audit/progress")
        out["progress"] = progress.status_code
        # 404 = usuario nuevo sin progreso aún (válido).
        if progress.status_code == 200:
            pdata = progress.json()
            out["progress_keys"] = sorted(pdata.keys())[:12]

        # Logout must not break; localStorage wipe is frontend-only.
        logout = client.post("/api/audit/logout")
        out["logout"] = logout.status_code
        after = client.get("/api/audit/session")
        out["session_after_logout"] = after.json() if after.status_code == 200 else {}

        out["ok"] = bool(
            out.get("gate_html")
            and out.get("authenticated")
            and out.get("progress") in (200, 404)
            and out.get("logout") == 200
            and not out.get("session_after_logout", {}).get("authenticated")
        )
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_true")
    parser.add_argument("--prod", action="store_true")
    parser.add_argument("--local-url", default=os.environ.get("SMOKE_BASE_URL", "http://127.0.0.1:8000"))
    parser.add_argument(
        "--prod-url",
        default="https://agente-de-ia-juridico.onrender.com",
    )
    args = parser.parse_args()
    if not args.local and not args.prod:
        args.local = args.prod = True

    password = _load_vault_password()
    if not password:
        print("ERROR: falta SMOKE_SITE_PASSWORD o ~/Backups/agente-juridico/SITE_PASSWORD.txt", file=sys.stderr)
        return 2
    if password.startswith("pbkdf2_sha256$"):
        print("ERROR: la contraseña parece un hash; se necesita plaintext.", file=sys.stderr)
        return 2

    email = os.environ.get("SMOKE_AUDIT_EMAIL", "smoke.audit@dbxsolutions.com")
    pin = os.environ.get("SMOKE_AUDIT_PIN", "654321")

    results = []
    if args.local:
        results.append(smoke_login(args.local_url, email=email, password=password, pin=pin))
    if args.prod:
        results.append(smoke_login(args.prod_url, email=email, password=password, pin=pin))

    print(json.dumps(results, indent=2, ensure_ascii=False))
    if not all(r.get("ok") for r in results):
        return 1
    print("SMOKE_AUDIT_LOGIN_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
