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
    root = project_root()
    for candidate in (root / ".cursor" / "skills", root / "agente" / "skills"):
        if candidate.is_dir() and any(candidate.glob("*/SKILL.md")):
            return candidate
    return root / ".cursor" / "skills"


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
