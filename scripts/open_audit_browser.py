#!/usr/bin/env python3
"""Abre /auditoria/ con sesión ya autenticada (local y/o prod).

Credenciales (nunca en git; solo vault / env):
  SMOKE_SITE_PASSWORD  o  ~/Backups/agente-juridico/{smoke.env,SITE_PASSWORD.txt}
  SMOKE_AUDIT_EMAIL, SMOKE_AUDIT_PIN

Uso:
  .venv/bin/python scripts/open_audit_browser.py --local
  .venv/bin/python scripts/open_audit_browser.py --prod
  .venv/bin/python scripts/open_audit_browser.py --local --prod
  OPEN_AUDIT_BROWSER=1 ./scripts/start-local.sh

Local con DEV_AUTO_LOGIN: por defecto usa el browser del sistema (`open`).
Prod (o local sin auto-login): Playwright headed con cookie tras login API.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import httpx

ROOT = Path(__file__).resolve().parents[1]
VAULT = Path.home() / "Backups" / "agente-juridico"
AUDIT_COOKIE = "audit_session"
DEFAULT_LOCAL = "http://127.0.0.1:8000"
DEFAULT_PROD = "https://agente-de-ia-juridico.onrender.com"


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


def _load_vault_email_pin() -> tuple[str, str]:
    email = os.environ.get("SMOKE_AUDIT_EMAIL", "").strip()
    pin = os.environ.get("SMOKE_AUDIT_PIN", "").strip()
    smoke = VAULT / "smoke.env"
    if smoke.is_file():
        for line in smoke.read_text(encoding="utf-8").splitlines():
            if not email and line.startswith("SMOKE_AUDIT_EMAIL="):
                email = line.split("=", 1)[1].strip().strip("'\"")
            if not pin and line.startswith("SMOKE_AUDIT_PIN="):
                pin = line.split("=", 1)[1].strip().strip("'\"")
    if not email:
        email = "smoke.audit@dbxsolutions.com"
    if not pin:
        pin = "654321"
    return email, pin


def _cookie_domain(base: str) -> str:
    host = urlparse(base).hostname or "127.0.0.1"
    return host


def _login_cookie(base: str, *, email: str, password: str, pin: str) -> str:
    base = base.rstrip("/")
    with httpx.Client(base_url=base, timeout=45.0, follow_redirects=True) as client:
        health = client.get("/health")
        if health.status_code != 200:
            raise RuntimeError(f"health HTTP {health.status_code} en {base}")

        pre = client.post("/api/audit/prelogin", json={"email": email, "password": password})
        if pre.status_code != 200:
            raise RuntimeError(f"prelogin {pre.status_code}: {pre.text[:200]}")
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
        if login.status_code != 200:
            raise RuntimeError(f"login {login.status_code}: {login.text[:200]}")

        token = client.cookies.get(AUDIT_COOKIE)
        if not token:
            # Algunos jars exponen el nombre con dominio; buscar a mano.
            for cookie in client.cookies.jar:
                if cookie.name == AUDIT_COOKIE and cookie.value:
                    token = cookie.value
                    break
        if not token:
            raise RuntimeError("login OK pero no llegó cookie audit_session")
        return token


def _local_dev_auto_login(base: str) -> bool:
    try:
        with httpx.Client(timeout=10.0) as client:
            health = client.get(f"{base.rstrip('/')}/health")
            if health.status_code != 200:
                return False
            return bool(health.json().get("dev_auto_login"))
    except Exception:
        return False


def _open_system(url: str) -> None:
    if sys.platform == "darwin":
        subprocess.Popen(["open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif sys.platform.startswith("linux"):
        subprocess.Popen(["xdg-open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        subprocess.Popen(["cmd", "/c", "start", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"OPEN_SYSTEM {url}")


def _open_playwright(base: str, token: str, *, keep_open: bool) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(
            "Falta playwright. Instale: .venv/bin/pip install playwright "
            "&& .venv/bin/playwright install chromium"
        ) from exc

    base = base.rstrip("/")
    url = f"{base}/auditoria/"
    secure = urlparse(base).scheme == "https"
    cookie = {
        "name": AUDIT_COOKIE,
        "value": token,
        "domain": _cookie_domain(base),
        "path": "/",
        "httpOnly": True,
        "secure": secure,
        "sameSite": "None" if secure else "Lax",
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        context.add_cookies([cookie])
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=60_000)
        # Confirmar gate oculto / sesión
        page.wait_for_timeout(800)
        gate_hidden = page.evaluate(
            "() => document.getElementById('audit-auth-gate')?.classList.contains('gate-hidden')"
        )
        print(f"OPEN_PLAYWRIGHT {url} gate_hidden={gate_hidden}")
        if not keep_open:
            browser.close()
            return
        print("Sesión abierta. Cierre la ventana del navegador para terminar este proceso.")
        try:
            while browser.is_connected():
                time.sleep(0.5)
                if not context.pages:
                    break
        except KeyboardInterrupt:
            pass
        finally:
            try:
                browser.close()
            except Exception:
                pass


def _will_use_system(base: str, *, prefer_system: bool, force_playwright: bool) -> bool:
    is_local = "127.0.0.1" in base or "localhost" in base
    return bool(
        prefer_system
        and is_local
        and not force_playwright
        and _local_dev_auto_login(base)
    )


def open_target(
    base: str,
    *,
    email: str,
    password: str,
    pin: str,
    prefer_system: bool,
    keep_open: bool,
    force_playwright: bool,
) -> None:
    base = base.rstrip("/")
    if _will_use_system(base, prefer_system=prefer_system, force_playwright=force_playwright):
        _open_system(f"{base}/auditoria/")
        return

    token = _login_cookie(base, email=email, password=password, pin=pin)
    _open_playwright(base, token, keep_open=keep_open)


def main() -> int:
    parser = argparse.ArgumentParser(description="Abrir /auditoria/ con sesión autenticada")
    parser.add_argument("--local", action="store_true")
    parser.add_argument("--prod", action="store_true")
    parser.add_argument("--local-url", default=os.environ.get("SMOKE_BASE_URL", DEFAULT_LOCAL))
    parser.add_argument("--prod-url", default=DEFAULT_PROD)
    parser.add_argument(
        "--prefer-system",
        action="store_true",
        default=True,
        help="Local + DEV_AUTO_LOGIN → open del sistema (default)",
    )
    parser.add_argument(
        "--no-prefer-system",
        action="store_false",
        dest="prefer_system",
        help="Forzar login+Playwright también en local",
    )
    parser.add_argument(
        "--playwright",
        action="store_true",
        help="Forzar Playwright (ignora open del sistema)",
    )
    parser.add_argument(
        "--no-keep-open",
        action="store_true",
        help="Cerrar Playwright al cargar (útil en smoke)",
    )
    args = parser.parse_args()
    if not args.local and not args.prod:
        args.local = True

    password = _load_vault_password()
    email, pin = _load_vault_email_pin()

    targets: list[str] = []
    if args.local:
        targets.append(args.local_url.rstrip("/"))
    if args.prod:
        targets.append(args.prod_url.rstrip("/"))

    needs_password = any(
        not _will_use_system(
            base, prefer_system=args.prefer_system, force_playwright=args.playwright
        )
        for base in targets
    )
    if needs_password:
        if not password:
            print(
                "ERROR: falta SMOKE_SITE_PASSWORD o ~/Backups/agente-juridico/SITE_PASSWORD.txt",
                file=sys.stderr,
            )
            return 2
        if password.startswith("pbkdf2_sha256$"):
            print("ERROR: la contraseña parece un hash; se necesita plaintext.", file=sys.stderr)
            return 2

    keep_open = not args.no_keep_open
    # Si hay varios targets con Playwright, solo el último bloquea el proceso.
    playwright_idxs = [
        i
        for i, base in enumerate(targets)
        if not _will_use_system(
            base, prefer_system=args.prefer_system, force_playwright=args.playwright
        )
    ]
    last_pw = playwright_idxs[-1] if playwright_idxs else -1

    for i, base in enumerate(targets):
        try:
            open_target(
                base,
                email=email,
                password=password,
                pin=pin,
                prefer_system=args.prefer_system,
                keep_open=keep_open and i == last_pw,
                force_playwright=args.playwright,
            )
        except Exception as exc:
            print(f"ERROR abriendo {base}: {exc}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
