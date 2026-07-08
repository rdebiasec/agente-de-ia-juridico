"""Catálogo vivo del portal de auditoría — misma fuente que generar_audit_portal.py."""

from __future__ import annotations

import json
import logging
import sys
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from lib.audit_data import build_audit_data  # noqa: E402

DIST_DIR = ROOT / "audit-portal" / "dist"


@lru_cache(maxsize=1)
def get_audit_catalog() -> dict:
    return build_audit_data()


def refresh_runtime_catalog_caches() -> None:
    """Limpia cachés del catálogo en API y en el runtime del agente."""
    get_audit_catalog.cache_clear()
    try:
        from src.agents.skill_catalog import get_skills_catalog, valid_skill_ids

        get_skills_catalog.cache_clear()
        valid_skill_ids.cache_clear()
    except Exception:
        logger.exception("No se pudo limpiar caché de skill_catalog")


def write_catalog_json(dist_dir: Path | None = None) -> dict:
    data = build_audit_data()
    target = dist_dir or DIST_DIR
    target.mkdir(parents=True, exist_ok=True)
    out = target / "audit-data.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    refresh_runtime_catalog_caches()
    return data


def build_live_audit_catalog() -> dict:
    """Catálogo siempre fresco desde fuentes canónicas (API /auditoria)."""
    return build_audit_data()
