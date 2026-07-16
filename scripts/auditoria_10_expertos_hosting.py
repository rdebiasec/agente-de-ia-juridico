#!/usr/bin/env python3
"""Auditoría producción — 10 expertos (hosting seguro y reputación).

Perspectivas alineadas a OWASP ASVS / Secure Headers / backups / privacidad CO.
Uso:
  .venv/bin/python scripts/auditoria_10_expertos_hosting.py
  .venv/bin/python scripts/auditoria_10_expertos_hosting.py --base https://…
"""

from __future__ import annotations

import argparse
import json
import ssl
import subprocess
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_MD = ROOT / "docs" / "auditoria" / "dictamen-10-expertos-hosting-prod.md"
OUT_JSON = ROOT / "docs" / "auditoria" / "dictamen-10-expertos-hosting-prod.json"
PAGES = "https://rdebiasec.github.io/agente-de-ia-juridico"


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
    hdrs = {"User-Agent": "hosting-audit-10e/1.0"}
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


def run(base: str) -> tuple[list[Finding], dict]:
    findings: list[Finding] = []
    meta: dict = {
        "base": base,
        "pages": PAGES,
        "commit": git_head(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
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
        "# Dictamen 10 expertos — hosting seguro y reputación (producción)",
        "",
        f"**Fecha:** {meta['generated_at']}",
        f"**Commit:** `{meta['commit']}`",
        f"**Target:** {meta['base']}",
        f"**Pages:** {meta['pages']}",
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
    args = parser.parse_args()
    findings, meta = run(args.base.rstrip("/"))
    write_report(findings, meta)
    from collections import Counter

    c = Counter(f.status for f in findings)
    print(json.dumps({"counts": dict(c), "report": str(OUT_MD)}, ensure_ascii=False))
    for f in findings:
        print(f"{f.status:4} {f.expert_id} {f.test_id} {f.name}: {f.detail[:100]}")
    return 1 if c.get("FAIL") else 0


if __name__ == "__main__":
    raise SystemExit(main())
