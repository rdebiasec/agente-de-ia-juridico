#!/usr/bin/env python3
"""Auditoría producción — 20 expertos (hosting seguro y reputación).

Perspectivas: AppSec, platform, identity, privacy, DR, secrets, availability,
reputation, CI/CD, CORS, TLS, sessions, rate-limit, deps, logging, privacy ops,
data integrity, isolation, continuity, legal-AI trust.

Uso:
  .venv/bin/python scripts/auditoria_20_expertos_hosting.py
  .venv/bin/python scripts/auditoria_20_expertos_hosting.py --wave 1
  .venv/bin/python scripts/auditoria_20_expertos_hosting.py --wave 1,2,3,4
"""

from __future__ import annotations

import argparse
import json
import re
import socket
import ssl
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_MD = ROOT / "docs" / "auditoria" / "dictamen-20-expertos-hosting-prod.md"
OUT_JSON = ROOT / "docs" / "auditoria" / "dictamen-20-expertos-hosting-prod.json"
PAGES = "https://rdebiasec.github.io/agente-de-ia-juridico"

WAVE_EXPERTS = {
    1: {"E01", "E02", "E03", "E04", "E05"},
    2: {"E06", "E07", "E08", "E09", "E10"},
    3: {"E11", "E12", "E13", "E14", "E15"},
    4: {"E16", "E17", "E18", "E19", "E20"},
}


@dataclass
class Finding:
    expert_id: str
    expert: str
    test_id: str
    name: str
    status: str  # PASS | WARN | FAIL | INFO
    detail: str
    evidence: str
    source: str


def fetch(
    url: str,
    method: str = "GET",
    data: dict | None = None,
    headers: dict | None = None,
    timeout: float = 45.0,
) -> tuple[int, dict[str, str], bytes]:
    hdrs = {"User-Agent": "hosting-audit-20e/1.0"}
    if headers:
        hdrs.update(headers)
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        hdrs.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            return r.status, {k.lower(): v for k, v in r.headers.items()}, r.read()
    except urllib.error.HTTPError as e:
        return e.code, {k.lower(): v for k, v in e.headers.items()}, e.read()
    except Exception as e:
        return 0, {}, str(e).encode()


def add(
    out: list[Finding],
    expert_id: str,
    expert: str,
    test_id: str,
    name: str,
    status: str,
    detail: str,
    evidence: str = "",
    source: str = "",
) -> None:
    out.append(
        Finding(expert_id, expert, test_id, name, status, detail, evidence, source)
    )


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        return "unknown"


def run(base: str, *, waves: set[int] | None = None) -> tuple[list[Finding], dict]:
    findings: list[Finding] = []
    allowed: set[str] | None = None
    if waves:
        allowed = set()
        for w in waves:
            allowed |= WAVE_EXPERTS.get(w, set())
    meta: dict = {
        "base": base,
        "pages": PAGES,
        "commit": git_head(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "waves": sorted(waves) if waves else [1, 2, 3, 4],
    }

    # --- E01 AppSec ---
    e, n = "E01", "AppSec (OWASP)"
    code, hdrs, raw = fetch(f"{base}/auditoria/")
    csp = hdrs.get("content-security-policy", "")
    add(
        findings,
        e,
        n,
        "E01-01",
        "CSP en /auditoria/",
        "PASS" if "default-src" in csp and "tailwindcss.com" in csp else "FAIL",
        csp[:160] or "missing",
        f"{base}/auditoria/",
        "https://owasp.org/www-project-secure-headers/",
    )
    hsts = hdrs.get("strict-transport-security", "")
    add(
        findings,
        e,
        n,
        "E01-02",
        "HSTS",
        "PASS" if "max-age" in hsts else "FAIL",
        hsts or "missing",
        f"{base}/auditoria/",
        "https://owasp.org/www-project-secure-headers/",
    )
    xfo = hdrs.get("x-frame-options", "")
    add(
        findings,
        e,
        n,
        "E01-03",
        "X-Frame-Options",
        "PASS" if xfo.upper() == "DENY" or "frame-ancestors" in csp else "WARN",
        xfo or "missing",
        f"{base}/auditoria/",
        "https://owasp.org/www-project-secure-headers/",
    )
    code_d, _, _ = fetch(f"{base}/docs")
    code_o, _, _ = fetch(f"{base}/openapi.json")
    add(
        findings,
        e,
        n,
        "E01-04",
        "OpenAPI oculto en prod",
        "PASS" if code_d == 404 and code_o == 404 else "WARN",
        f"docs={code_d} openapi={code_o}",
        f"{base}/docs",
        "https://owasp.org/www-project-application-security-verification-standard/",
    )

    # --- E02 Platform / hosting ---
    e, n = "E02", "Platform / hosting"
    code, _, raw = fetch(f"{base}/health")
    health = json.loads(raw) if code == 200 else {}
    meta["health"] = health
    add(
        findings,
        e,
        n,
        "E02-01",
        "Health production + postgres",
        "PASS"
        if health.get("environment") == "production" and health.get("persistencia") == "postgres"
        else "FAIL",
        str(
            {
                k: health.get(k)
                for k in (
                    "status",
                    "environment",
                    "persistencia",
                    "openai_configured",
                )
            }
        ),
        f"{base}/health",
        "https://render.com/docs",
    )
    add(
        findings,
        e,
        n,
        "E02-02",
        "DEV_AUTO_LOGIN off",
        "PASS" if health.get("dev_auto_login") is False else "FAIL",
        f"dev_auto_login={health.get('dev_auto_login')}",
        f"{base}/health",
        "https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html",
    )
    # TLS
    code_http, _, _ = fetch(base.replace("https://", "http://", 1) + "/health")
    add(
        findings,
        e,
        n,
        "E02-03",
        "HTTPS servicio alcanzable",
        "PASS" if code == 200 else "FAIL",
        f"https_health={code} http_probe={code_http}",
        base,
        "https://owasp.org/www-project-application-security-verification-standard/",
    )

    # --- E03 Identity ---
    e, n = "E03", "Identity & access"
    code, _, _ = fetch(
        f"{base}/api/audit/prelogin",
        method="POST",
        data={"email": "x@y.com"},
    )
    add(
        findings,
        e,
        n,
        "E03-01",
        "Prelogin exige password",
        "PASS" if code == 422 else "WARN",
        f"HTTP {code}",
        f"{base}/api/audit/prelogin",
        "https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html",
    )
    code, _, raw = fetch(
        f"{base}/api/audit/prelogin",
        method="POST",
        data={"email": "x@y.com", "password": "wrong-password-xyz-!!"},
    )
    add(
        findings,
        e,
        n,
        "E03-02",
        "Bad password → 401",
        "PASS" if code == 401 else "FAIL",
        f"HTTP {code}",
        f"{base}/api/audit/prelogin",
        "https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html",
    )
    code, _, _ = fetch(f"{base}/api/audit/progress")
    add(
        findings,
        e,
        n,
        "E03-03",
        "Progress sin sesión → 401",
        "PASS" if code in (401, 403) else "FAIL",
        f"HTTP {code}",
        f"{base}/api/audit/progress",
        "https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html",
    )
    code, _, _ = fetch(f"{base}/chat", method="POST", data={"message": "ping"})
    add(
        findings,
        e,
        n,
        "E03-04",
        "Chat sin sesión → 401",
        "PASS" if code in (401, 403) else "WARN",
        f"HTTP {code}",
        f"{base}/chat",
        "https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html",
    )

    # --- E04 Data protection ---
    e, n = "E04", "Data protection / privacy"
    code_p, _, _ = fetch(f"{base}/legal/privacidad")
    code_c, _, _ = fetch(f"{base}/legal/tratamiento-datos-casos")
    add(
        findings,
        e,
        n,
        "E04-01",
        "Aviso privacidad publicado",
        "PASS" if code_p == 200 else "FAIL",
        f"HTTP {code_p}",
        f"{base}/legal/privacidad",
        "https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=49981",
    )
    add(
        findings,
        e,
        n,
        "E04-02",
        "Tratamiento datos de casos",
        "PASS" if code_c == 200 else "FAIL",
        f"HTTP {code_c}",
        f"{base}/legal/tratamiento-datos-casos",
        "https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=49981",
    )
    code, _, raw = fetch(f"{base}/api/audit/policy")
    pol = json.loads(raw) if code == 200 else {}
    contact = (pol.get("controller") or {}).get("contact_email", "")
    add(
        findings,
        e,
        n,
        "E04-03",
        "Policy API + contacto ARCO",
        "PASS" if code == 200 and "privacidad@" in contact else "WARN",
        f"contact={contact}",
        f"{base}/api/audit/policy",
        "https://sedeelectronica.sic.gov.co/transparencia/normativa/ley-1581",
    )

    # --- E05 Backup / DR ---
    e, n = "E05", "Backup & disaster recovery"
    # Evidence from repo + gh if available
    wf = ROOT / ".github" / "workflows" / "backup-postgres.yml"
    add(
        findings,
        e,
        n,
        "E05-01",
        "Workflow backup Postgres→R2",
        "PASS" if wf.is_file() else "FAIL",
        str(wf.relative_to(ROOT)) if wf.is_file() else "missing",
        str(wf),
        "https://render.com/docs/postgresql-backups",
    )
    plan = ROOT / "docs" / "operaciones" / "PLAN_DESASTRE.md"
    add(
        findings,
        e,
        n,
        "E05-02",
        "Plan de desastre documentado",
        "PASS" if plan.is_file() else "FAIL",
        "PLAN_DESASTRE.md" if plan.is_file() else "missing",
        str(plan),
        "https://csrc.nist.gov/pubs/sp/800/34/r1/final",
    )
    # Recent GH Actions success (best-effort)
    try:
        out = subprocess.check_output(
            [
                "gh",
                "run",
                "list",
                "--workflow=backup-postgres.yml",
                "--limit",
                "1",
                "--json",
                "conclusion,displayTitle,createdAt",
            ],
            cwd=ROOT,
            text=True,
            timeout=30,
        )
        runs = json.loads(out)
        ok = bool(runs) and runs[0].get("conclusion") == "success"
        add(
            findings,
            e,
            n,
            "E05-03",
            "Último backup Actions success",
            "PASS" if ok else "WARN",
            json.dumps(runs[:1], ensure_ascii=False)[:200],
            "gh workflow backup-postgres.yml",
            "https://render.com/docs/postgresql-backups",
        )
    except Exception as exc:
        add(
            findings,
            e,
            n,
            "E05-03",
            "Último backup Actions success",
            "INFO",
            f"no verificado: {exc}",
            "",
            "https://render.com/docs/postgresql-backups",
        )

    # --- E06 Secrets ---
    e, n = "E06", "Secrets management"
    # No secrets in git
    tracked_env = subprocess.run(
        ["git", "ls-files", ".env", "*.pem", "*credentials*"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    leaked = [x for x in tracked_env.stdout.splitlines() if x.strip()]
    add(
        findings,
        e,
        n,
        "E06-01",
        ".env no trackeado en git",
        "PASS" if not leaked else "FAIL",
        f"tracked={leaked or 'none'}",
        ".gitignore",
        "https://owasp.org/www-project-application-security-verification-standard/",
    )
    add(
        findings,
        e,
        n,
        "E06-02",
        "Auth web habilitada en prod",
        "PASS" if health.get("web_auth_enabled") is True else "FAIL",
        f"web_auth_enabled={health.get('web_auth_enabled')}",
        f"{base}/health",
        "https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html",
    )
    # PBKDF2 support evidenced by tests in repo
    hash_script = ROOT / "scripts" / "hash_site_password.py"
    add(
        findings,
        e,
        n,
        "E06-03",
        "Herramienta hash SITE_PASSWORD",
        "PASS" if hash_script.is_file() else "WARN",
        "hash_site_password.py",
        str(hash_script),
        "https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html",
    )

    # --- E07 Availability ---
    e, n = "E07", "Availability & reliability"
    lat = []
    for _ in range(3):
        import time

        t0 = time.time()
        c, _, _ = fetch(f"{base}/health")
        lat.append(int((time.time() - t0) * 1000) if c == 200 else 99999)
    add(
        findings,
        e,
        n,
        "E07-01",
        "Health latency x3 < 15s",
        "PASS" if all(x < 15000 for x in lat) else "WARN",
        f"ms={lat}",
        f"{base}/health",
        "https://render.com/docs",
    )
    add(
        findings,
        e,
        n,
        "E07-02",
        "OpenAI configurado",
        "PASS" if health.get("openai_configured") else "WARN",
        f"openai={health.get('openai_configured')}",
        f"{base}/health",
        "ops",
    )
    add(
        findings,
        e,
        n,
        "E07-03",
        "Slack HITL canal",
        "INFO" if not health.get("slack_configured") else "PASS",
        f"slack={health.get('slack_configured')}",
        f"{base}/health",
        "ops",
    )

    # --- E08 Reputation / legal-tech ---
    e, n = "E08", "Reputation / legal-tech trust"
    code, _, raw = fetch(f"{base}/abogado")
    html = raw.decode("utf-8", "errors") if code == 200 else ""
    add(
        findings,
        e,
        n,
        "E08-01",
        "Chat abogado alcanzable",
        "PASS" if code == 200 else "FAIL",
        f"HTTP {code}",
        f"{base}/abogado",
        "producto",
    )
    # Anti-wipe markers in prod JS
    code, _, raw = fetch(f"{base}/auditoria/app.js")
    js = raw.decode("utf-8", "errors") if code == 200 else ""
    add(
        findings,
        e,
        n,
        "E08-02",
        "Anti-wipe merge en portal",
        "PASS" if "mergePersistPayload" in js else "FAIL",
        f"merge={'mergePersistPayload' in js}",
        f"{base}/auditoria/app.js",
        "integridad de datos",
    )
    code, _, raw = fetch(f"{base}/auditoria/auth-gate.js")
    ag = raw.decode("utf-8", "errors") if code == 200 else ""
    wipe = "localStorage.clear" in ag or "clearAuditLocalCache" in ag
    add(
        findings,
        e,
        n,
        "E08-03",
        "Logout no borra cache local",
        "PASS" if not wipe else "FAIL",
        f"wipe_helpers={wipe}",
        f"{base}/auditoria/auth-gate.js",
        "integridad de datos",
    )

    # --- E09 Supply chain / CI ---
    e, n = "E09", "Supply chain / CI-CD"
    ci = ROOT / ".github" / "workflows" / "ci.yml"
    add(
        findings,
        e,
        n,
        "E09-01",
        "CI workflow presente",
        "PASS" if ci.is_file() else "WARN",
        "ci.yml" if ci.is_file() else "missing",
        str(ci),
        "https://owasp.org/www-project-application-security-verification-standard/",
    )
    try:
        out = subprocess.check_output(
            [
                "gh",
                "run",
                "list",
                "--workflow=ci.yml",
                "--limit",
                "1",
                "--json",
                "conclusion,headSha,createdAt",
            ],
            cwd=ROOT,
            text=True,
            timeout=30,
        )
        runs = json.loads(out)
        ok = bool(runs) and runs[0].get("conclusion") in {"success", None, ""}
        # pending ok as INFO
        conclusion = runs[0].get("conclusion") if runs else None
        status = (
            "PASS"
            if conclusion == "success"
            else ("INFO" if conclusion in (None, "") else "WARN")
        )
        add(
            findings,
            e,
            n,
            "E09-02",
            "Último CI",
            status,
            json.dumps(runs[:1], ensure_ascii=False)[:220],
            "gh workflow ci.yml",
            "https://owasp.org/www-project-application-security-verification-standard/",
        )
    except Exception as exc:
        add(findings, e, n, "E09-02", "Último CI", "INFO", str(exc)[:120], "", "CI")

    deploy_portal = ROOT / ".github" / "workflows" / "deploy-audit-portal.yml"
    add(
        findings,
        e,
        n,
        "E09-03",
        "Deploy portal Pages workflow",
        "PASS" if deploy_portal.is_file() else "WARN",
        "deploy-audit-portal.yml",
        str(deploy_portal),
        "GitHub Pages",
    )

    # --- E10 CORS / abuse boundary ---
    e, n = "E10", "Boundary / CORS / abuse"
    code, hdrs, _ = fetch(
        f"{base}/api/audit/policy",
        headers={"Origin": "https://rdebiasec.github.io"},
    )
    acao = hdrs.get("access-control-allow-origin", "")
    add(
        findings,
        e,
        n,
        "E10-01",
        "CORS allowlist Pages",
        "PASS" if "rdebiasec.github.io" in acao else "FAIL",
        f"ACAO={acao!r}",
        f"{base}/api/audit/policy",
        "https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html",
    )
    code, hdrs, _ = fetch(
        f"{base}/api/audit/policy",
        headers={"Origin": "https://evil.example"},
    )
    acao = hdrs.get("access-control-allow-origin", "")
    add(
        findings,
        e,
        n,
        "E10-02",
        "CORS rechaza origen evil",
        "PASS" if "evil.example" not in acao else "FAIL",
        f"ACAO={acao!r}",
        f"{base}/api/audit/policy",
        "https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html",
    )
    # Catalog parity Pages
    code, _, raw = fetch(f"{PAGES}/audit-data.json")
    data = json.loads(raw) if code == 200 else {}
    tot = data.get("totals") or {}
    add(
        findings,
        e,
        n,
        "E10-03",
        "Catálogo Pages 10/90/402",
        "PASS"
        if tot.get("guardrails") == 10 and tot.get("skills") == 90 and tot.get("pasos") == 402
        else "WARN",
        str(tot),
        f"{PAGES}/audit-data.json",
        "integridad publicación",
    )
    code, _, raw = fetch(f"{PAGES}/app.js")
    pjs = raw.decode("utf-8", "errors") if code == 200 else ""
    add(
        findings,
        e,
        n,
        "E10-04",
        "Anti-wipe en GitHub Pages",
        "PASS" if "mergePersistPayload" in pjs else "FAIL",
        f"merge={'mergePersistPayload' in pjs}",
        f"{PAGES}/app.js",
        "integridad publicación",
    )

    # --- E11 TLS / transport ---
    e, n = "E11", "TLS / transport"
    host = base.replace("https://", "").replace("http://", "").split("/")[0]
    tls_ok = False
    tls_detail = ""
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=15) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                tls_ok = bool(cert)
                not_after = cert.get("notAfter", "") if cert else ""
                tls_detail = f"tls={ssock.version()} notAfter={not_after}"
    except Exception as exc:
        tls_detail = f"error={exc}"
    add(
        findings,
        e,
        n,
        "E11-01",
        "Certificado TLS válido",
        "PASS" if tls_ok else "FAIL",
        tls_detail,
        base,
        "https://owasp.org/www-project-application-security-verification-standard/",
    )
    code_h, hdrs_h, _ = fetch(f"{base}/auditoria/")
    csp_h = hdrs_h.get("content-security-policy", "")
    script_src = ""
    if "script-src" in csp_h:
        script_src = csp_h.split("script-src", 1)[1].split(";", 1)[0]
    add(
        findings,
        e,
        n,
        "E11-02",
        "CSP sin http:// en script-src",
        "PASS" if "http://" not in script_src else "WARN",
        script_src[:160] or csp_h[:160],
        f"{base}/auditoria/",
        "https://owasp.org/www-project-secure-headers/",
    )
    # portal HTML should not load http:// assets
    html_a = ""
    if code_h == 200:
        _, _, raw_a = fetch(f"{base}/auditoria/")
        html_a = raw_a.decode("utf-8", "errors")
    http_assets = len(re.findall(r"http://(?!localhost|127\.0\.0\.1)", html_a))
    add(
        findings,
        e,
        n,
        "E11-03",
        "Portal sin assets http://",
        "PASS" if http_assets == 0 else "WARN",
        f"http_asset_refs={http_assets}",
        f"{base}/auditoria/",
        "https://owasp.org/www-project-secure-headers/",
    )

    # --- E12 Session & cookies ---
    e, n = "E12", "Session & cookies"
    auth_deps = (ROOT / "src" / "auth" / "deps.py").read_text(encoding="utf-8")
    audit_api = (ROOT / "src" / "gateway" / "audit_portal_api.py").read_text(encoding="utf-8")
    httponly_ok = "httponly=True" in auth_deps and "httponly=True" in audit_api
    secure_ok = "cookie_secure(settings)" in auth_deps and "cookie_secure(settings)" in audit_api
    add(
        findings,
        e,
        n,
        "E12-01",
        "Cookies HttpOnly en código",
        "PASS" if httponly_ok else "FAIL",
        f"httponly_web={('httponly=True' in auth_deps)} httponly_audit={('httponly=True' in audit_api)}",
        "src/auth/deps.py + audit_portal_api.py",
        "https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html",
    )
    add(
        findings,
        e,
        n,
        "E12-02",
        "Cookies Secure vía cookie_secure()",
        "PASS" if secure_ok else "WARN",
        f"secure_helper={secure_ok}",
        "src/auth/deps.py",
        "https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html",
    )
    # Successful cookie flags only visible after real login; check Set-Cookie absent on 401 (no session leak)
    code, hdrs, _ = fetch(
        f"{base}/api/audit/login",
        method="POST",
        data={
            "email": "x@y.com",
            "password": "wrong",
            "pin": "000000",
            "accept_privacy": True,
            "accept_sensitive_data": True,
        },
    )
    set_cookie = hdrs.get("set-cookie", "")
    add(
        findings,
        e,
        n,
        "E12-03",
        "Login fallido no setea sesión",
        "PASS" if "audit_session" not in set_cookie and "agente_session" not in set_cookie else "FAIL",
        f"HTTP {code} set-cookie_present={bool(set_cookie)}",
        f"{base}/api/audit/login",
        "https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html",
    )

    # --- E13 Rate limiting ---
    e, n = "E13", "Rate limiting / abuse"
    rl_file = ROOT / "src" / "middleware" / "rate_limit.py"
    add(
        findings,
        e,
        n,
        "E13-01",
        "Middleware rate_limit presente",
        "PASS" if rl_file.is_file() else "FAIL",
        str(rl_file.relative_to(ROOT)),
        str(rl_file),
        "https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html",
    )
    add(
        findings,
        e,
        n,
        "E13-02",
        "Audit login usa check_rate_limit",
        "PASS" if "check_rate_limit" in audit_api and "LOGIN_RATE" in audit_api else "WARN",
        "audit_portal_api rate hooks",
        "src/gateway/audit_portal_api.py",
        "https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html",
    )
    codes = []
    for i in range(6):
        c, _, _ = fetch(
            f"{base}/api/audit/prelogin",
            method="POST",
            data={"email": f"rate{i}@dbxsolutions.com", "password": "definitely-wrong-pass!!"},
        )
        codes.append(c)
    # Expect sustained 401 (or eventual 429). Not 500.
    ok_rl = all(c in (401, 429, 422) for c in codes) and 500 not in codes
    add(
        findings,
        e,
        n,
        "E13-03",
        "Ráfaga prelogin fallido estable",
        "PASS" if ok_rl else "WARN",
        f"codes={codes}",
        f"{base}/api/audit/prelogin",
        "https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html",
    )

    # --- E14 Dependency / supply ---
    e, n = "E14", "Dependency / supply risk"
    pyproject = ROOT / "pyproject.toml"
    add(
        findings,
        e,
        n,
        "E14-01",
        "pyproject.toml presente",
        "PASS" if pyproject.is_file() else "FAIL",
        "pyproject.toml",
        str(pyproject),
        "https://owasp.org/www-project-application-security-verification-standard/",
    )
    ci_text = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8") if (ROOT / ".github" / "workflows" / "ci.yml").is_file() else ""
    add(
        findings,
        e,
        n,
        "E14-02",
        "CI instala dependencias",
        "PASS" if "pip install" in ci_text or "uv sync" in ci_text else "WARN",
        "ci.yml install step",
        ".github/workflows/ci.yml",
        "https://owasp.org/www-project-application-security-verification-standard/",
    )
    # No hardcoded secrets in workflow files
    wf_secrets_leak = False
    leak_hits = []
    for wf in (ROOT / ".github" / "workflows").glob("*.yml"):
        txt = wf.read_text(encoding="utf-8")
        if re.search(r"(sk-|ghp_|AKIA)[A-Za-z0-9]{10,}", txt):
            wf_secrets_leak = True
            leak_hits.append(wf.name)
    add(
        findings,
        e,
        n,
        "E14-03",
        "Workflows sin secretos hardcodeados",
        "PASS" if not wf_secrets_leak else "FAIL",
        f"hits={leak_hits or 'none'}",
        ".github/workflows/",
        "https://owasp.org/www-project-application-security-verification-standard/",
    )

    # --- E15 Logging & forensics ---
    e, n = "E15", "Logging & forensics"
    add(
        findings,
        e,
        n,
        "E15-01",
        "Access log audit en API",
        "PASS" if "_log_access" in audit_api else "WARN",
        "audit_portal_access_log hooks",
        "src/gateway/audit_portal_api.py",
        "https://owasp.org/www-project-application-security-verification-standard/",
    )
    # 404/401 should not dump secrets
    code, _, raw = fetch(f"{base}/api/audit/progress")
    body = raw.decode("utf-8", "errors").lower()
    leak_markers = ["openai", "sk-", "password=", "session_secret", "traceback (most recent"]
    leaked_resp = any(m in body for m in leak_markers)
    add(
        findings,
        e,
        n,
        "E15-02",
        "401 progress sin leak de secretos",
        "PASS" if code in (401, 403) and not leaked_resp else "WARN",
        f"HTTP {code} body_snip={body[:80]!r}",
        f"{base}/api/audit/progress",
        "https://owasp.org/www-project-application-security-verification-standard/",
    )
    sql_storage = (ROOT / "src" / "storage" / "sql.py").read_text(encoding="utf-8") if (ROOT / "src" / "storage" / "sql.py").is_file() else ""
    add(
        findings,
        e,
        n,
        "E15-03",
        "Modelo access_log / historial en storage",
        "PASS" if "audit_portal_access_log" in sql_storage or "AccessLog" in sql_storage or "access_log" in sql_storage else "WARN",
        "sql.py audit access/history tables",
        "src/storage/sql.py",
        "forensics",
    )

    # --- E16 Privacy ops ---
    e, n = "E16", "Privacy ops (Ley 1581)"
    add(
        findings,
        e,
        n,
        "E16-01",
        "Consentimiento 428 sin accept",
        "PASS" if "428" in audit_api and "accept_privacy" in audit_api else "FAIL",
        "login gates privacy+case data",
        "src/gateway/audit_portal_api.py",
        "https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=49981",
    )
    code, _, raw = fetch(f"{base}/api/audit/policy")
    pol = json.loads(raw) if code == 200 else {}
    contact = (pol.get("controller") or {}).get("contact_email", "")
    add(
        findings,
        e,
        n,
        "E16-02",
        "Contacto ARCO en policy",
        "PASS" if "privacidad@" in contact else "FAIL",
        f"contact={contact}",
        f"{base}/api/audit/policy",
        "https://sedeelectronica.sic.gov.co/transparencia/normativa/ley-1581",
    )
    add(
        findings,
        e,
        n,
        "E16-03",
        "Páginas legales accesibles",
        "PASS"
        if fetch(f"{base}/legal/privacidad")[0] == 200
        and fetch(f"{base}/legal/tratamiento-datos-casos")[0] == 200
        else "FAIL",
        "privacidad + tratamiento-datos-casos",
        f"{base}/legal/privacidad",
        "https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=49981",
    )

    # --- E17 Data integrity ---
    e, n = "E17", "Data integrity"
    merge_src = (ROOT / "src" / "gateway" / "audit_progress.py").read_text(encoding="utf-8")
    add(
        findings,
        e,
        n,
        "E17-01",
        "merge_audit_progress en servidor",
        "PASS" if "def merge_audit_progress" in merge_src else "FAIL",
        "src/gateway/audit_progress.py",
        "src/gateway/audit_progress.py",
        "integridad",
    )
    add(
        findings,
        e,
        n,
        "E17-02",
        "PUT progress usa merge",
        "PASS" if "merge_audit_progress" in audit_api else "FAIL",
        "put_audit_progress merge call",
        "src/gateway/audit_portal_api.py",
        "integridad",
    )
    merge_tests = ROOT / "tests" / "test_audit_progress_merge.py"
    add(
        findings,
        e,
        n,
        "E17-03",
        "Tests anti-wipe merge",
        "PASS" if merge_tests.is_file() else "WARN",
        "test_audit_progress_merge.py",
        str(merge_tests),
        "integridad",
    )
    # live anti-wipe marker
    code, _, raw = fetch(f"{base}/auditoria/app.js")
    js = raw.decode("utf-8", "errors") if code == 200 else ""
    add(
        findings,
        e,
        n,
        "E17-04",
        "Anti-wipe frontend en prod",
        "PASS" if "mergePersistPayload" in js else "FAIL",
        f"merge={'mergePersistPayload' in js}",
        f"{base}/auditoria/app.js",
        "integridad",
    )

    # --- E18 Multi-tenant isolation ---
    e, n = "E18", "Multi-tenant isolation"
    iso_test = ROOT / "tests" / "test_compliance.py"
    iso_txt = iso_test.read_text(encoding="utf-8") if iso_test.is_file() else ""
    add(
        findings,
        e,
        n,
        "E18-01",
        "Test isolation progreso audit",
        "PASS" if "isolation" in iso_txt else "WARN",
        "test_audit_progress_history_and_isolation",
        str(iso_test),
        "https://owasp.org/www-project-application-security-verification-standard/",
    )
    add(
        findings,
        e,
        n,
        "E18-02",
        "Progress exige auth",
        "PASS" if fetch(f"{base}/api/audit/progress")[0] in (401, 403) else "FAIL",
        "unauth progress denied",
        f"{base}/api/audit/progress",
        "https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html",
    )
    access_test = ROOT / "tests" / "test_access_control.py"
    add(
        findings,
        e,
        n,
        "E18-03",
        "Test cross-subject access control",
        "PASS" if access_test.is_file() and "cross_subject" in access_test.read_text(encoding="utf-8") else "WARN",
        "test_plan_bola_blocks_cross_subject",
        str(access_test),
        "https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html",
    )

    # --- E19 Business continuity ---
    e, n = "E19", "Business continuity"
    recover_wf = ROOT / ".github" / "workflows" / "recover-from-r2.yml"
    add(
        findings,
        e,
        n,
        "E19-01",
        "Workflow recover-from-r2",
        "PASS" if recover_wf.is_file() else "WARN",
        "recover-from-r2.yml (manual, no auto-restore)",
        str(recover_wf),
        "https://csrc.nist.gov/pubs/sp/800/34/r1/final",
    )
    recover_sh = ROOT / "scripts" / "dr" / "recover_from_r2.sh"
    add(
        findings,
        e,
        n,
        "E19-02",
        "Script recover_from_r2.sh",
        "PASS" if recover_sh.is_file() else "WARN",
        str(recover_sh.relative_to(ROOT)) if recover_sh.is_file() else "missing",
        str(recover_sh),
        "https://render.com/docs/postgresql-backups",
    )
    # R2 prod LATEST via awscli if backup.env present
    r2_ok = False
    r2_detail = "backup.env missing"
    backup_env = Path.home() / "Backups" / "agente-juridico" / "backup.env"
    if backup_env.is_file():
        try:
            env = {}
            for line in backup_env.read_text(encoding="utf-8").splitlines():
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip().strip("'\"")
            import os

            os.environ["AWS_ACCESS_KEY_ID"] = env.get("R2_ACCESS_KEY_ID", "")
            os.environ["AWS_SECRET_ACCESS_KEY"] = env.get("R2_SECRET_ACCESS_KEY", "")
            os.environ["AWS_DEFAULT_REGION"] = "auto"
            endpoint = f"https://{env['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com"
            out = subprocess.check_output(
                [
                    str(ROOT / ".venv" / "bin" / "python"),
                    "-m",
                    "awscli",
                    "s3",
                    "ls",
                    f"s3://{env['R2_BUCKET']}/prod/",
                    "--endpoint-url",
                    endpoint,
                ],
                text=True,
                timeout=45,
            )
            r2_ok = "LATEST.txt" in out or "postgres/" in out
            r2_detail = out.strip().replace("\n", " | ")[:200]
        except Exception as exc:
            r2_detail = f"error={exc}"
    add(
        findings,
        e,
        n,
        "E19-03",
        "R2 prod/ reachable",
        "PASS" if r2_ok else "WARN",
        r2_detail,
        "s3://…/prod/",
        "https://render.com/docs/postgresql-backups",
    )

    # --- E20 Reputational / legal AI ---
    e, n = "E20", "Reputational / legal AI"
    code, _, raw = fetch(f"{PAGES}/audit-data.json")
    data = json.loads(raw) if code == 200 else {}
    gids = sorted((g.get("id") or "") for g in (data.get("guardrails") or []))
    add(
        findings,
        e,
        n,
        "E20-01",
        "Guardrails g1–g10 en catálogo",
        "PASS" if set(gids) >= {f"g{i}" for i in range(1, 11)} else "FAIL",
        str(gids),
        f"{PAGES}/audit-data.json",
        "reputación jurídica",
    )
    code, _, raw = fetch(f"{base}/abogado")
    html = raw.decode("utf-8", "errors") if code == 200 else ""
    _, _, firma_js = fetch(f"{base}/static/firma.js")
    _, _, chat_js = fetch(f"{base}/static/chat.js")
    surface = (html + firma_js.decode("utf-8", "errors") + chat_js.decode("utf-8", "errors")).lower()
    hitl_markers = any(
        x in surface
        for x in ("hitl", "borrador", "bandeja", "aprob", "revis", "humano", "firma")
    )
    add(
        findings,
        e,
        n,
        "E20-02",
        "Superficie chat con señal humana/HITL",
        "PASS" if code == 200 and hitl_markers else "WARN",
        f"HTTP {code} hitl_markers={hitl_markers}",
        f"{base}/abogado + static/firma.js|chat.js",
        "IA propone; abogado aprueba",
    )
    add(
        findings,
        e,
        n,
        "E20-03",
        "Slack HITL gap conocido",
        "INFO" if not health.get("slack_configured") else "PASS",
        f"slack_configured={health.get('slack_configured')}",
        f"{base}/health",
        "ops",
    )

    if allowed is not None:
        findings = [f for f in findings if f.expert_id in allowed]
    return findings, meta


def write_report(findings: list[Finding], meta: dict) -> None:
    from collections import Counter, defaultdict

    by_status = Counter(f.status for f in findings)
    by_expert: dict[str, list[Finding]] = defaultdict(list)
    for f in findings:
        by_expert[f.expert_id].append(f)

    fails = by_status.get("FAIL", 0)
    warns = by_status.get("WARN", 0)
    if fails:
        verdict = "NO-GO"
    elif warns:
        verdict = "GO CONDICIONAL"
    else:
        verdict = "GO"

    lines = [
        "# Dictamen 20 expertos — hosting seguro y reputación (producción)",
        "",
        f"**Fecha:** {meta['generated_at']}",
        f"**Commit:** `{meta['commit']}`",
        f"**Target:** {meta['base']}",
        f"**Pages:** {meta['pages']}",
        f"**Oleadas:** {meta.get('waves')}",
        f"**Veredicto:** **{verdict}** — PASS={by_status.get('PASS',0)} WARN={warns} FAIL={fails} INFO={by_status.get('INFO',0)}",
        "",
        "## Panel",
        "",
        "| ID | Experto | Resultado | Notas |",
        "|----|---------|-----------|-------|",
    ]
    for eid in sorted(by_expert):
        items = by_expert[eid]
        statuses = Counter(i.status for i in items)
        if statuses.get("FAIL"):
            res = "FAIL"
        elif statuses.get("WARN"):
            res = "WARN"
        elif statuses.get("PASS") and not statuses.get("FAIL"):
            res = "PASS"
        else:
            res = "INFO"
        note = "; ".join(
            f"{i.test_id}:{i.status}" for i in items if i.status in {"FAIL", "WARN", "INFO"}
        ) or "todos PASS"
        lines.append(f"| {eid} | {items[0].expert} | {res} | {note} |")

    lines.extend(["", "## Hallazgos", ""])
    lines.append("| Experto | Test | Estado | Detalle | Fuente |")
    lines.append("|---------|------|--------|---------|--------|")
    for f in findings:
        lines.append(
            f"| {f.expert_id} | {f.test_id} {f.name} | {f.status} | {f.detail.replace('|', '/')} | {f.source} |"
        )

    lines.extend(
        [
            "",
            "## Fuentes de método",
            "",
            "- OWASP ASVS — https://owasp.org/www-project-application-security-verification-standard/",
            "- OWASP Secure Headers — https://owasp.org/www-project-secure-headers/",
            "- OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html",
            "- NIST SP 800-34 — https://csrc.nist.gov/pubs/sp/800/34/r1/final",
            "- Render Postgres backups — https://render.com/docs/postgresql-backups",
            "- Ley 1581/2012 — https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=49981",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    OUT_JSON.write_text(
        json.dumps(
            {"meta": meta, "verdict": verdict, "counts": dict(by_status), "findings": [asdict(f) for f in findings]},
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base",
        default="https://agente-de-ia-juridico.onrender.com",
    )
    parser.add_argument(
        "--wave",
        default="",
        help="Oleadas a incluir, ej. 1 o 1,2,3,4 (vacío = todas)",
    )
    args = parser.parse_args()
    waves: set[int] | None = None
    if args.wave.strip():
        waves = {int(x.strip()) for x in args.wave.split(",") if x.strip()}
    findings, meta = run(args.base.rstrip("/"), waves=waves)
    write_report(findings, meta)
    from collections import Counter

    c = Counter(f.status for f in findings)
    print(json.dumps({"counts": dict(c), "waves": meta.get("waves"), "report": str(OUT_MD)}, ensure_ascii=False))
    for f in findings:
        print(f"{f.status:4} {f.expert_id} {f.test_id} {f.name}: {f.detail[:100]}")
    return 1 if c.get("FAIL") else 0


if __name__ == "__main__":
    raise SystemExit(main())
