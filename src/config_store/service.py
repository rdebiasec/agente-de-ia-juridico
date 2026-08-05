"""Servicio de versiones de configuración (DB autoritativa + archivo export)."""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.config_store.paths import (
    AGENT_GUARDRAIL_CLASSES,
    KIND_AGENT_GUARDRAIL,
    KIND_GUARDRAIL,
    KIND_PROMPT,
    KIND_SKILL,
    VALID_KINDS,
    agent_guardrail_key,
    agent_guardrails_dir,
    agent_prompts_dir,
    guardrails_dir,
    parse_agent_guardrail_key,
    path_for,
    relative_path_for,
    skills_dir,
)
from src.storage import get_repository
from src.storage.models import ConfigActive, ConfigVersion

logger = logging.getLogger(__name__)

_HEADER_RE = re.compile(
    r"^<!--\s*config-version:\s*(\d+)\s*;\s*checksum:\s*([a-f0-9]+)\s*-->\s*\n?",
    re.IGNORECASE,
)


class ConfigValidationError(ValueError):
    """Contenido inválido o kind/key desconocidos."""


class ConfigConflictError(ValueError):
    """Conflicto de versión optimista (expected_version no coincide)."""


class ConfigNotFoundError(KeyError):
    """No hay configuración activa para kind/key."""


def checksum_content(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def strip_header(content: str) -> str:
    return _HEADER_RE.sub("", content or "", count=1)


def parse_header(content: str) -> tuple[int | None, str | None]:
    """Devuelve (version, checksum) del header, o (None, None) si no lo tiene."""
    match = _HEADER_RE.match(content or "")
    if not match:
        return None, None
    return int(match.group(1)), match.group(2)


def with_header(content: str, *, version: int, checksum: str) -> str:
    body = strip_header(content).rstrip() + "\n"
    return f"<!-- config-version: {version}; checksum: {checksum} -->\n{body}"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _validate_kind_key(kind: str, key: str) -> None:
    if kind not in VALID_KINDS:
        raise ConfigValidationError(f"kind inválido: {kind}")
    key = (key or "").strip()
    if not key or "/" in key or ".." in key or "\\" in key:
        raise ConfigValidationError(f"key inválida: {key}")
    if kind == KIND_PROMPT and key != "sistema" and not re.fullmatch(r"[a-z0-9_]+", key):
        raise ConfigValidationError(f"prompt key inválida: {key}")
    if kind == KIND_GUARDRAIL and not re.fullmatch(r"g\d+", key):
        raise ConfigValidationError(f"guardrail key inválida: {key}")
    if kind == KIND_AGENT_GUARDRAIL:
        try:
            agent_id, _clase = parse_agent_guardrail_key(key)
        except ValueError as exc:
            raise ConfigValidationError(str(exc)) from exc
        if not re.fullmatch(r"[a-z0-9_]+", agent_id):
            raise ConfigValidationError(f"agent_guardrail key inválida: {key}")
    if kind == KIND_SKILL and not re.fullmatch(r"[a-z0-9_]+", key):
        raise ConfigValidationError(f"skill key inválida: {key}")


def _read_file_body(path: Path) -> str:
    if not path.is_file():
        return ""
    return strip_header(path.read_text(encoding="utf-8"))


def _write_file(path: Path, content: str, *, version: int, checksum: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(with_header(content, version=version, checksum=checksum), encoding="utf-8")


def _resolve_config_key(kind: str, key: str) -> str:
    """Map legacy agent IDs in prompt / agent_guardrail keys to canonical names."""
    if kind == KIND_PROMPT and key != "sistema":
        try:
            from src.agents.agent_ids import resolve_agent_id

            return resolve_agent_id(key) or key
        except Exception:
            return key
    if kind == KIND_AGENT_GUARDRAIL:
        try:
            from src.agents.agent_ids import resolve_agent_id

            agent_id, clase = parse_agent_guardrail_key(key)
            return agent_guardrail_key(resolve_agent_id(agent_id) or agent_id, clase)
        except Exception:
            return key
    return key


def get_active_content(kind: str, key: str, *, prefer_db: bool = True) -> dict[str, Any]:
    """Devuelve contenido activo. DB primero; fallback a archivo seed."""
    key = _resolve_config_key(kind, key)
    _validate_kind_key(kind, key)
    repo = get_repository()
    active = repo.get_config_active(kind, key) if prefer_db else None
    if active:
        version_row = repo.get_config_version(kind, key, active.active_version)
        if version_row:
            return {
                "kind": kind,
                "key": key,
                "version": version_row.version,
                "content": version_row.content,
                "checksum": version_row.checksum,
                "path": active.path,
                "updated_at": active.updated_at.isoformat(),
                "updated_by": active.updated_by,
                "source": "db",
            }
    path = path_for(kind, key)
    body = _read_file_body(path)
    if not body and kind == KIND_AGENT_GUARDRAIL:
        try:
            agent_id, clase = parse_agent_guardrail_key(key)
            body = default_agent_guardrail_content(agent_id, clase)
        except ValueError:
            body = ""
    if not body and kind != KIND_SKILL:
        raise ConfigNotFoundError(f"{kind}/{key}")
    if not body and kind == KIND_SKILL and not path.is_file():
        raise ConfigNotFoundError(f"{kind}/{key}")
    chk = checksum_content(body)
    return {
        "kind": kind,
        "key": key,
        "version": 0,
        "content": body,
        "checksum": chk,
        "path": relative_path_for(kind, key),
        "updated_at": None,
        "updated_by": None,
        "source": "file",
    }


def list_versions(kind: str, key: str, *, limit: int = 50) -> list[dict[str, Any]]:
    _validate_kind_key(kind, key)
    rows = get_repository().list_config_versions(kind, key, limit=limit)
    return [
        {
            "kind": r.kind,
            "key": r.key,
            "version": r.version,
            "checksum": r.checksum,
            "author_email": r.author_email,
            "note": r.note,
            "created_at": r.created_at.isoformat(),
            "content_preview": (r.content or "")[:240],
        }
        for r in rows
    ]


def save_version(
    kind: str,
    key: str,
    content: str,
    *,
    author_email: str,
    note: str = "",
    expected_version: int | None = None,
    write_file: bool = True,
) -> dict[str, Any]:
    _validate_kind_key(kind, key)
    body = strip_header(content or "").strip()
    if not body:
        raise ConfigValidationError("El contenido no puede estar vacío.")
    if len(body) > 400_000:
        raise ConfigValidationError("Contenido demasiado largo.")

    repo = get_repository()
    active = repo.get_config_active(kind, key)
    current_version = active.active_version if active else 0
    if expected_version is not None and expected_version != current_version:
        raise ConfigConflictError(
            f"Versión esperada {expected_version}, activa {current_version}."
        )

    # Si hay versiones huérfanas (activas atrás del max), no colisionar.
    latest = repo.list_config_versions(kind, key, limit=1)
    max_stored = latest[0].version if latest else 0
    next_version = max(current_version, max_stored) + 1
    chk = checksum_content(body)
    row = ConfigVersion(
        kind=kind,
        key=key,
        version=next_version,
        content=body,
        checksum=chk,
        author_email=author_email,
        note=note or "",
        created_at=_now(),
    )
    repo.add_config_version(row)
    rel = relative_path_for(kind, key)
    repo.upsert_config_active(
        ConfigActive(
            kind=kind,
            key=key,
            active_version=next_version,
            checksum=chk,
            path=rel,
            updated_at=_now(),
            updated_by=author_email,
        )
    )
    file_exported = False
    file_export_error: str | None = None
    if write_file:
        try:
            _write_file(path_for(kind, key), body, version=next_version, checksum=chk)
            file_exported = True
        except OSError as exc:
            logger.exception("No se pudo exportar archivo %s/%s (DB sí quedó activa)", kind, key)
            file_export_error = str(exc)

    return {
        "kind": kind,
        "key": key,
        "version": next_version,
        "checksum": chk,
        "path": rel,
        "author_email": author_email,
        "source": "db",
        "file_exported": file_exported if write_file else None,
        "file_export_error": file_export_error,
    }


def restore_version(
    kind: str,
    key: str,
    version: int,
    *,
    author_email: str,
    note: str = "",
    write_file: bool = True,
) -> dict[str, Any]:
    _validate_kind_key(kind, key)
    repo = get_repository()
    row = repo.get_config_version(kind, key, version)
    if row is None:
        raise ConfigNotFoundError(f"No existe {kind}/{key} v{version}")
    restore_note = note or f"Restaurado desde v{version}"
    return save_version(
        kind,
        key,
        row.content,
        author_email=author_email,
        note=restore_note,
        expected_version=None,
        write_file=write_file,
    )


def load_prompt_text(key: str) -> str:
    """Carga texto de prompt activo (DB → archivo)."""
    data = get_active_content(KIND_PROMPT, key)
    return data["content"]


# Alias de portal (g*) → política desk canónica. Enforcement real: I/O/T + SDK + HITL.
_G_ALIAS_META: dict[str, dict[str, str]] = {
    "g1": {"policy_id": "no_inventar", "iot_layer": "output", "status": "deprecated"},
    "g2": {"policy_id": "pedir_faltantes", "iot_layer": "input", "status": "deprecated"},
    "g3": {
        "policy_id": "hecho_vs_inferencia",
        "iot_layer": "output",
        "status": "deprecated",
    },
    "g4": {"policy_id": "hitl", "iot_layer": "tools/HITL", "status": "deprecated"},
    "g5": {"policy_id": "no_revictimizar", "iot_layer": "output", "status": "deprecated"},
    "g6": {
        "policy_id": "confidencialidad",
        "iot_layer": "output+tools",
        "status": "deprecated",
    },
    "g7": {"policy_id": "fuera_de_alcance", "iot_layer": "input", "status": "deprecated"},
    "g8": {"policy_id": "aviso_borrador", "iot_layer": "output", "status": "deprecated"},
    "g9": {"policy_id": "terminos_906", "iot_layer": "output", "status": "deprecated"},
    "g10": {
        "policy_id": "integridad_probatoria",
        "iot_layer": "output+tools",
        "status": "deprecated",
    },
}


def load_guardrail_policies() -> list[dict[str, str]]:
    """Lista de políticas (id alias g*, policy_id canónico, name, desc, status).

    Fuente de enforcement: desk_policies + I/O/T por agente + SDK.
    Los archivos/keys g* son stubs deprecados (alias de portal/progreso).
    """
    items: list[dict[str, str]] = []
    actives = get_repository().list_config_active(kind=KIND_GUARDRAIL)
    keys = [a.key for a in actives] if actives else sorted(
        p.stem for p in guardrails_dir().glob("g*.md")
    )
    for key in keys:
        try:
            data = get_active_content(KIND_GUARDRAIL, key)
        except ConfigNotFoundError:
            continue
        parsed = _parse_guardrail_markdown(data["content"], fallback_id=key)
        # Preferir metadatos de stub en disco (status/policy_id) sobre DB legacy.
        disk = guardrails_dir() / f"{key}.md"
        if disk.is_file():
            disk_parsed = _parse_guardrail_markdown(
                _read_file_body(disk), fallback_id=key
            )
            for field in ("status", "policy_id", "iot_layer"):
                if disk_parsed.get(field):
                    parsed[field] = disk_parsed[field]
            if disk_parsed.get("status") == "deprecated" and disk_parsed.get("desc"):
                # Mantener desc corto del stub si DB aún tiene el texto largo legacy.
                if len(disk_parsed["desc"]) < len(parsed.get("desc") or "") or "DEPRECATED" in (
                    data["content"] or ""
                ):
                    if not disk_parsed["desc"].startswith("**DEPRECATED"):
                        parsed["desc"] = disk_parsed["desc"]
        alias = _G_ALIAS_META.get(parsed["id"]) or _G_ALIAS_META.get(key)
        if alias:
            parsed.setdefault("policy_id", alias["policy_id"])
            parsed.setdefault("iot_layer", alias["iot_layer"])
            parsed["status"] = alias["status"]
        items.append(parsed)
    items.sort(key=lambda g: int(re.sub(r"\D", "", g["id"]) or 0))
    return items


def _parse_guardrail_markdown(content: str, *, fallback_id: str) -> dict[str, str]:
    lines = [ln.rstrip() for ln in content.splitlines()]
    name = fallback_id
    gid = fallback_id
    policy_id = ""
    status = "active"
    iot_layer = ""
    body_lines: list[str] = []
    resumen = ""
    for ln in lines:
        if ln.startswith("# "):
            name = ln[2:].strip() or name
            continue
        low = ln.lower()
        if low.startswith("id:"):
            gid = ln.split(":", 1)[1].strip() or gid
            continue
        if low.startswith("name:"):
            name = ln.split(":", 1)[1].strip() or name
            continue
        if low.startswith("status:"):
            status = ln.split(":", 1)[1].strip() or status
            continue
        if low.startswith("policy_id:"):
            policy_id = ln.split(":", 1)[1].strip()
            continue
        if low.startswith("iot_layer:"):
            iot_layer = ln.split(":", 1)[1].strip()
            continue
        if low.startswith("resumen:"):
            resumen = ln.split(":", 1)[1].strip()
            continue
        if ln.strip() == "":
            if body_lines:
                body_lines.append("")
            continue
        body_lines.append(ln)
    desc = resumen or "\n".join(body_lines).strip()
    # Preferir resumen corto; si el body es stub DEPRECATED, acotar.
    if status == "deprecated" and resumen:
        desc = resumen
    elif status == "deprecated" and "DEPRECATED" in desc:
        # Extraer última línea útil si no hay Resumen:
        useful = [
            ln for ln in body_lines
            if ln.strip() and not ln.strip().startswith("**DEPRECATED")
            and not ln.strip().startswith("- Política")
            and not ln.strip().startswith("- Mapa:")
            and not ln.strip().startswith("- Enforcement:")
        ]
        if useful:
            desc = useful[-1].removeprefix("Resumen:").strip()
    out: dict[str, str] = {"id": gid, "name": name, "desc": desc}
    if policy_id:
        out["policy_id"] = policy_id
    if status:
        out["status"] = status
    if iot_layer:
        out["iot_layer"] = iot_layer
    return out


def _agent_ids_from_prompts() -> list[str]:
    return sorted(p.stem for p in agent_prompts_dir().glob("*.md"))


def _desk_policies_bundle() -> str:
    """Texto canónico de políticas del despacho para seeds I/O/T."""
    path = guardrails_dir() / "_shared" / "desk_policies.md"
    if path.is_file():
        return _read_file_body(path).strip()
    return ""


def _legacy_guardrail_bundle() -> str:
    """Compat: preferir desk_policies; si falta, concatenar stubs g*."""
    desk = _desk_policies_bundle()
    if desk:
        return desk
    parts: list[str] = []
    for path in sorted(
        guardrails_dir().glob("g*.md"),
        key=lambda p: int(re.sub(r"\D", "", p.stem) or 0),
    ):
        body = _read_file_body(path).strip()
        if body:
            parts.append(body)
    return "\n\n---\n\n".join(parts).strip()


def default_agent_guardrail_content(agent_id: str, clase: str) -> str:
    """Plantilla seed para Input/Output/Tools por agente."""
    if clase == "input":
        bundle = _desk_policies_bundle() or _legacy_guardrail_bundle()
        header = (
            f"# Guardrails de entrada — {agent_id}\n\n"
            "Políticas aplicadas al input del agente. "
            "Punto de partida: desk_policies + capas I/O/T (editable por agente).\n\n"
        )
        return f"{header}{bundle}" if bundle else (
            f"{header}(Sin desk_policies en disco; complete esta sección.)\n"
        )
    if clase == "output":
        return (
            f"# Guardrails de salida — {agent_id}\n\n"
            "Políticas aplicadas a la salida del agente.\n\n"
            "- No inventar normas, radicados ni jurisprudencia.\n"
            "- Separar hecho de inferencia.\n"
            "- Marcar pendientes de verificación.\n"
            "- No prometer resultados judiciales.\n"
        )
    if clase == "tools":
        return (
            f"# Guardrails de tools — {agent_id}\n\n"
            "Políticas aplicadas al uso de tools / agentes-como-tools.\n\n"
            "- Solo invocar tools pertinentes a la consulta.\n"
            "- No exponer datos sensibles en argumentos de tools.\n"
            "- Si falta contexto, pedir aclaración antes de invocar.\n"
        )
    raise ValueError(f"clase de agent_guardrail desconocida: {clase}")


def ensure_agent_guardrail_seeds(
    *, author_email: str = "system@seed", write_file: bool = False
) -> int:
    """Crea seed v1 de Input/Output/Tools por agente si aún no existen en DB."""
    repo = get_repository()
    created = 0
    for agent_id in _agent_ids_from_prompts():
        for clase in sorted(AGENT_GUARDRAIL_CLASSES):
            key = agent_guardrail_key(agent_id, clase)
            if repo.get_config_active(KIND_AGENT_GUARDRAIL, key):
                continue
            path = path_for(KIND_AGENT_GUARDRAIL, key)
            body = _read_file_body(path).strip() or default_agent_guardrail_content(agent_id, clase)
            save_version(
                KIND_AGENT_GUARDRAIL,
                key,
                body,
                author_email=author_email,
                note="seed v1 agent_guardrail",
                expected_version=0,
                write_file=write_file,
            )
            created += 1
    return created


def seed_from_filesystem(*, author_email: str = "system@seed", write_file: bool = False) -> dict[str, int]:
    """Siembra version=1 desde archivos cuando no hay activo en DB.

    Por defecto no reescribe archivos (evita ensuciar el working tree en local).
    """
    counts = {
        "prompt": 0,
        "guardrail": 0,
        "agent_guardrail": 0,
        "skill": 0,
        "skipped": 0,
    }
    repo = get_repository()

    # sistema + agents
    prompt_keys = ["sistema"] + _agent_ids_from_prompts()
    for key in prompt_keys:
        path = path_for(KIND_PROMPT, key)
        if not path.is_file():
            continue
        if repo.get_config_active(KIND_PROMPT, key):
            counts["skipped"] += 1
            continue
        save_version(
            KIND_PROMPT,
            key,
            _read_file_body(path),
            author_email=author_email,
            note="seed v1",
            expected_version=0,
            write_file=write_file,
        )
        counts["prompt"] += 1

    for path in sorted(guardrails_dir().glob("g*.md")):
        key = path.stem
        if repo.get_config_active(KIND_GUARDRAIL, key):
            counts["skipped"] += 1
            continue
        save_version(
            KIND_GUARDRAIL,
            key,
            _read_file_body(path),
            author_email=author_email,
            note="seed v1",
            expected_version=0,
            write_file=write_file,
        )
        counts["guardrail"] += 1

    for path in sorted(skills_dir().glob("*/SKILL.md")):
        key = path.parent.name
        if repo.get_config_active(KIND_SKILL, key):
            counts["skipped"] += 1
            continue
        save_version(
            KIND_SKILL,
            key,
            _read_file_body(path),
            author_email=author_email,
            note="seed v1",
            expected_version=0,
            write_file=write_file,
        )
        counts["skill"] += 1

    counts["agent_guardrail"] = ensure_agent_guardrail_seeds(
        author_email=author_email, write_file=write_file
    )
    return counts


def validate_config_store() -> list[str]:
    """Chequeos de arranque: activos con checksum coherente."""
    errors: list[str] = []
    repo = get_repository()
    actives = repo.list_config_active()
    if not actives:
        return errors  # vacío = operar con archivos seed
    for active in actives:
        row = repo.get_config_version(active.kind, active.key, active.active_version)
        if row is None:
            errors.append(f"Falta versión activa {active.kind}/{active.key} v{active.active_version}")
            continue
        if row.checksum != active.checksum:
            errors.append(f"Checksum mismatch {active.kind}/{active.key}")
        if checksum_content(row.content) != row.checksum:
            errors.append(f"Contenido corrupto {active.kind}/{active.key} v{row.version}")
    return errors


def list_agent_guardrail_keys() -> list[str]:
    """Keys conocidas: archivos en disco + activos DB + 11 agentes × 3 clases."""
    keys: set[str] = set()
    root = agent_guardrails_dir()
    if root.is_dir():
        for path in root.glob("*/*.md"):
            if path.stem in AGENT_GUARDRAIL_CLASSES:
                keys.add(agent_guardrail_key(path.parent.name, path.stem))
    for agent_id in _agent_ids_from_prompts():
        for clase in AGENT_GUARDRAIL_CLASSES:
            keys.add(agent_guardrail_key(agent_id, clase))
    return sorted(keys)


def retire_config_key(
    kind: str,
    key: str,
    *,
    purge_versions: bool = True,
) -> dict[str, int | bool]:
    """Retira una key del catálogo activo (y opcionalmente su historial).

    Usar para agentes/skills/guardrails eliminados del filesystem (p. ej. tutela).
    """
    repo = get_repository()
    removed_active = repo.delete_config_active(kind, key)
    removed_versions = repo.delete_config_versions(kind, key) if purge_versions else 0
    return {
        "removed_active": bool(removed_active),
        "removed_versions": int(removed_versions),
    }


def list_orphan_config_keys() -> list[tuple[str, str]]:
    """Keys activas en DB sin archivo canónico en disco."""
    orphans: list[tuple[str, str]] = []
    for active in get_repository().list_config_active():
        if not path_for(active.kind, active.key).is_file():
            orphans.append((active.kind, active.key))
    return sorted(set(orphans))


def list_catalog_items() -> dict[str, list[dict[str, Any]]]:
    """Inventario editable: prompts, guardrails, agent_guardrails y skills.

    Solo keys con archivo canónico en disco (no resucita huérfanos de DB).
    """
    repo = get_repository()
    actives = {(a.kind, a.key): a for a in repo.list_config_active()}

    prompt_keys = ["sistema"] + _agent_ids_from_prompts()
    guard_keys = sorted(p.stem for p in guardrails_dir().glob("g*.md"))
    skill_keys = sorted(p.parent.name for p in skills_dir().glob("*/SKILL.md"))
    root = agent_guardrails_dir()
    if root.is_dir():
        agent_guard_keys = sorted(
            agent_guardrail_key(path.parent.name, path.stem)
            for path in root.glob("*/*.md")
            if path.stem in AGENT_GUARDRAIL_CLASSES
        )
    else:
        agent_guard_keys = sorted(list_agent_guardrail_keys())

    def _item(kind: str, key: str) -> dict[str, Any]:
        active = actives.get((kind, key))
        return {
            "kind": kind,
            "key": key,
            "path": relative_path_for(kind, key),
            "active_version": active.active_version if active else 0,
            "checksum": active.checksum if active else None,
            "updated_at": active.updated_at.isoformat() if active and active.updated_at else None,
            "updated_by": active.updated_by if active else None,
        }

    return {
        "prompt": [_item(KIND_PROMPT, k) for k in prompt_keys],
        "guardrail": [_item(KIND_GUARDRAIL, k) for k in guard_keys],
        "agent_guardrail": [_item(KIND_AGENT_GUARDRAIL, k) for k in agent_guard_keys],
        "skill": [_item(KIND_SKILL, k) for k in skill_keys],
    }


# re-export constants for callers
__all__ = [
    "KIND_PROMPT",
    "KIND_GUARDRAIL",
    "KIND_AGENT_GUARDRAIL",
    "KIND_SKILL",
    "ConfigConflictError",
    "ConfigNotFoundError",
    "ConfigValidationError",
    "checksum_content",
    "default_agent_guardrail_content",
    "ensure_agent_guardrail_seeds",
    "get_active_content",
    "list_catalog_items",
    "list_orphan_config_keys",
    "list_versions",
    "load_guardrail_policies",
    "load_prompt_text",
    "path_for",
    "restore_version",
    "retire_config_key",
    "save_version",
    "seed_from_filesystem",
    "validate_config_store",
]
