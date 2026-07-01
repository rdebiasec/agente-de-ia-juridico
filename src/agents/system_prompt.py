"""Carga del prompt de sistema compartido por todos los agentes."""

from src.config import get_settings


def load_system_prompt() -> str:
    settings = get_settings()
    path = settings.agente_dir / "prompts" / "sistema.md"
    return path.read_text(encoding="utf-8")
