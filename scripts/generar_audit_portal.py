#!/usr/bin/env python3
"""Genera audit-data.json y copia audit-portal/site/ a audit-portal/dist/."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from lib.audit_data import build_audit_data  # noqa: E402

SITE_DIR = ROOT / "audit-portal" / "site"
DIST_DIR = ROOT / "audit-portal" / "dist"


def audit_auth_enabled() -> bool:
    return os.environ.get("AUDIT_PORTAL_AUTH_ENABLED", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def audit_api_base() -> str:
    return os.environ.get("AUDIT_API_BASE", "").strip().rstrip("/")


def build_audit_api_config_js() -> str:
    base = audit_api_base()
    payload = {"base": base}
    return f"window.AUDIT_API_CONFIG={json.dumps(payload, ensure_ascii=False)};\n"


def write_audit_api_config(dist_dir: Path | None = None) -> None:
    out = (dist_dir or DIST_DIR) / "audit-api-config.js"
    out.write_text(build_audit_api_config_js(), encoding="utf-8")
    base = audit_api_base()
    if base:
        print(f"  api: AUDIT_API_BASE={base}")
    else:
        print("  api: mismo origen (AUDIT_API_BASE vacío → /api/audit en el servidor)")


def build_auth_config_js() -> str:
    """Genera auth-config.js. Login legacy desactivado — auth vía API /api/audit/login."""
    return "window.AUDIT_AUTH_CONFIG={enabled:false};\n"


def write_auth_config(dist_dir: Path | None = None) -> None:
    out = (dist_dir or DIST_DIR) / "auth-config.js"
    out.write_text(build_auth_config_js(), encoding="utf-8")
    print("  auth: login vía API /api/audit (auth-config.js legacy desactivado)")


def copy_site_to_dist() -> None:
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    shutil.copytree(SITE_DIR, DIST_DIR)


def validate_portal_js() -> None:
    """Falla el build si app.js o auth-gate.js tienen error de sintaxis."""
    for rel in ("app.js", "auth-gate.js"):
        path = SITE_DIR / rel
        if not path.is_file():
            raise SystemExit(f"Falta JS del portal: {path}")
        proc = subprocess.run(
            ["node", "--check", str(path)],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            err = (proc.stderr or proc.stdout or "syntax error").strip()
            raise SystemExit(f"Error de sintaxis en {rel}: {err}")


def write_catalog_artifact(dist_dir: Path | None = None) -> dict:
    data = build_audit_data()
    target = dist_dir or DIST_DIR
    target.mkdir(parents=True, exist_ok=True)
    (target / "audit-data.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return data


def ensure_audit_portal_artifacts(*, full_if_missing: bool = True) -> dict:
    """Regenera audit-data.json; build completo del portal si falta dist/."""
    needs_full = full_if_missing and (
        not DIST_DIR.is_dir() or not (DIST_DIR / "index.html").is_file()
    )
    if needs_full:
        if not SITE_DIR.is_dir():
            raise FileNotFoundError(f"Falta carpeta fuente: {SITE_DIR}")
        validate_portal_js()
        copy_site_to_dist()
    data = write_catalog_artifact()
    write_auth_config()
    write_audit_api_config()

    step_sum = sum(s["step_count"] for s in data["skills"])
    totals = data["totals"]
    if step_sum != totals["pasos"]:
        raise ValueError(f"pasos mismatch: {step_sum} != {totals['pasos']}")

    try:
        from src.gateway.audit_catalog import refresh_runtime_catalog_caches

        refresh_runtime_catalog_caches()
    except Exception:
        pass

    return data


def main() -> None:
    if not SITE_DIR.is_dir():
        raise SystemExit(f"Falta carpeta fuente: {SITE_DIR}")

    validate_portal_js()
    copy_site_to_dist()
    data = write_catalog_artifact()
    write_auth_config()
    write_audit_api_config()

    step_sum = sum(s["step_count"] for s in data["skills"])
    totals = data["totals"]
    if step_sum != totals["pasos"]:
        raise SystemExit(f"pasos mismatch: {step_sum} != {totals['pasos']}")

    try:
        from src.gateway.audit_catalog import refresh_runtime_catalog_caches

        refresh_runtime_catalog_caches()
    except Exception:
        pass

    print(
        f"OK: {DIST_DIR} — "
        f"{totals['guardrails']} reglas, {totals['agentes']} agentes, "
        f"{totals['pasos']} pasos ({totals['items']} items auditable)"
    )


if __name__ == "__main__":
    main()
