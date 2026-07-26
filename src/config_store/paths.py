"""Rutas canónicas de archivos de configuración."""

from __future__ import annotations

from pathlib import Path

from src.config import get_settings

KIND_PROMPT = "prompt"
KIND_GUARDRAIL = "guardrail"
KIND_SKILL = "skill"
KIND_AGENT_GUARDRAIL = "agent_guardrail"
VALID_KINDS = frozenset({KIND_PROMPT, KIND_GUARDRAIL, KIND_SKILL, KIND_AGENT_GUARDRAIL})

AGENT_GUARDRAIL_CLASSES = frozenset({"input", "output", "tools"})


def project_root() -> Path:
    return get_settings().project_root


def prompts_dir() -> Path:
    return project_root() / "agente" / "prompts"


def agent_prompts_dir() -> Path:
    return prompts_dir() / "agents"


def guardrails_dir() -> Path:
    return project_root() / "config" / "guardrails"


def agent_guardrails_dir() -> Path:
    return guardrails_dir() / "agents"


def skills_dir() -> Path:
    """Fuente canónica: `agente/skills`. `.cursor/skills` es espejo para el IDE."""
    root = project_root()
    canonical = root / "agente" / "skills"
    if canonical.is_dir() and any(canonical.glob("*/SKILL.md")):
        return canonical
    mirror = root / ".cursor" / "skills"
    if mirror.is_dir() and any(mirror.glob("*/SKILL.md")):
        return mirror
    return canonical


def agent_guardrail_key(agent_id: str, clase: str) -> str:
    return f"{agent_id}__{clase}"


def parse_agent_guardrail_key(key: str) -> tuple[str, str]:
    """Devuelve (agent_id, clase) o lanza ValueError."""
    if "__" not in (key or ""):
        raise ValueError(f"agent_guardrail key inválida: {key}")
    agent_id, clase = key.rsplit("__", 1)
    if not agent_id or clase not in AGENT_GUARDRAIL_CLASSES:
        raise ValueError(f"agent_guardrail key inválida: {key}")
    return agent_id, clase


def path_for(kind: str, key: str) -> Path:
    if kind == KIND_PROMPT:
        if key == "sistema":
            return prompts_dir() / "sistema.md"
        return agent_prompts_dir() / f"{key}.md"
    if kind == KIND_GUARDRAIL:
        return guardrails_dir() / f"{key}.md"
    if kind == KIND_AGENT_GUARDRAIL:
        agent_id, clase = parse_agent_guardrail_key(key)
        return agent_guardrails_dir() / agent_id / f"{clase}.md"
    if kind == KIND_SKILL:
        return skills_dir() / key / "SKILL.md"
    raise ValueError(f"kind desconocido: {kind}")


def relative_path_for(kind: str, key: str) -> str:
    return str(path_for(kind, key).relative_to(project_root()))


def kind_key_for_path(path: Path) -> tuple[str, str] | None:
    """Resuelve (kind, key) para un archivo del config store, o None si no aplica."""
    try:
        resolved = path.resolve()
        root = project_root().resolve()
        rel = resolved.relative_to(root)
    except (OSError, ValueError):
        return None
    parts = rel.parts
    if parts == ("agente", "prompts", "sistema.md"):
        return KIND_PROMPT, "sistema"
    if len(parts) == 4 and parts[:3] == ("agente", "prompts", "agents") and parts[3].endswith(".md"):
        return KIND_PROMPT, parts[3][:-3]
    if (
        len(parts) == 5
        and parts[:3] == ("config", "guardrails", "agents")
        and parts[4] in {f"{c}.md" for c in AGENT_GUARDRAIL_CLASSES}
    ):
        return KIND_AGENT_GUARDRAIL, agent_guardrail_key(parts[3], parts[4][:-3])
    if len(parts) == 3 and parts[:2] == ("config", "guardrails") and parts[2].endswith(".md"):
        return KIND_GUARDRAIL, parts[2][:-3]
    if (
        len(parts) == 4
        and parts[0] in {".cursor", "agente"}
        and parts[1] == "skills"
        and parts[3] == "SKILL.md"
    ):
        return KIND_SKILL, parts[2]
    return None
