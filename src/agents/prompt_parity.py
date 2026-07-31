"""Paridad prompt archivo baseline vs config store activo (G08)."""

from __future__ import annotations

import re
from pathlib import Path

_VERSION_RE = re.compile(
    r"<!--\s*config-version:\s*(\d+)\s*;\s*checksum:\s*([0-9a-fA-F]+)\s*-->"
)


def parse_file_prompt_header(text: str) -> tuple[int | None, str | None]:
    match = _VERSION_RE.search(text or "")
    if not match:
        return None, None
    return int(match.group(1)), match.group(2).lower()


def check_prompt_parity(agent_id: str = "coordinador_expediente_penal") -> dict:
    """Compara header del MD en disco con la versión activa en Postgres (si hay).

    No falla el boot: devuelve un dict con ok/mismatch/unavailable.
    """
    from src.config import get_settings

    root = get_settings().agente_dir / "prompts" / "agents" / f"{agent_id}.md"
    result: dict = {
        "agent_id": agent_id,
        "file_path": str(root),
        "ok": True,
        "status": "ok",
        "file_version": None,
        "file_checksum": None,
        "db_version": None,
        "db_checksum": None,
        "detail": "",
    }
    if not root.is_file():
        result["ok"] = False
        result["status"] = "missing_file"
        result["detail"] = "No existe el prompt baseline en disco."
        return result

    file_text = root.read_text(encoding="utf-8")
    file_ver, file_sum = parse_file_prompt_header(file_text)
    result["file_version"] = file_ver
    result["file_checksum"] = file_sum

    try:
        from src.config_store import KIND_PROMPT, get_active_content

        data = get_active_content(KIND_PROMPT, agent_id)
    except Exception as exc:
        result["status"] = "db_unavailable"
        result["detail"] = f"Config store no disponible ({type(exc).__name__}); se usa archivo."
        return result

    db_ver = data.get("version")
    db_sum = str(data.get("checksum") or "").lower() or None
    result["db_version"] = db_ver
    result["db_checksum"] = db_sum

    if file_ver is None:
        result["status"] = "no_file_header"
        result["detail"] = "Archivo sin header config-version/checksum."
        return result

    try:
        db_ver_int = int(db_ver) if db_ver is not None else None
    except (TypeError, ValueError):
        db_ver_int = None

    if db_ver_int is not None and db_ver_int != file_ver:
        result["ok"] = False
        result["status"] = "version_mismatch"
        result["detail"] = (
            f"Versión archivo={file_ver} vs DB={db_ver_int}. "
            "Sincronizar seed/editor /auditoria/."
        )
        return result

    if db_sum and file_sum and not db_sum.startswith(file_sum) and file_sum not in db_sum:
        # checksums pueden ser más largos en DB; comparación flexible.
        if file_sum[:8] not in db_sum and db_sum[:8] not in file_sum:
            result["ok"] = False
            result["status"] = "checksum_mismatch"
            result["detail"] = "Checksum archivo vs DB difieren; posible drift."
            return result

    result["detail"] = "Paridad OK (o DB ausente de checksum comparable)."
    return result


def log_prompt_parity_on_startup(logger) -> None:
    report = check_prompt_parity()
    if report["ok"]:
        logger.info(
            "Prompt parity Gerente: %s (file v%s / db v%s)",
            report["status"],
            report.get("file_version"),
            report.get("db_version"),
        )
    else:
        logger.warning(
            "Prompt parity Gerente: %s — %s",
            report["status"],
            report.get("detail") or "",
        )
