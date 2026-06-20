"""Herramientas de lectura de la base de conocimiento (equivalente MCP Fase 0)."""

from pathlib import Path

from agents import function_tool

from src.config import get_settings

AREA_FILES = {
    "civil": "civil.md",
    "familia": "familia.md",
    "societario": "societario.md",
    "penal": "penal.md",
    "consumidor": "consumidor.md",
    "comercial": "comercial.md",
    "laboral": "laboral.md",
    "normas": "normas-clave.md",
}


def _read_kb_file(name: str) -> str:
    settings = get_settings()
    path = settings.agente_dir / "conocimiento" / name
    if not path.exists():
        return f"[No encontrado: {name}]"
    return path.read_text(encoding="utf-8")


def _list_areas() -> str:
    lines = ["Áreas del derecho cubiertas por el despacho (Fase 0):"]
    for area, filename in AREA_FILES.items():
        if area != "normas":
            lines.append(f"- {area}: agente/conocimiento/{filename}")
    lines.append("- normas clave: agente/conocimiento/normas-clave.md")
    return "\n".join(lines)


@function_tool
def listar_areas_derecho() -> str:
    """Lista las áreas del derecho disponibles en la base de conocimiento."""
    return _list_areas()


@function_tool
def leer_area_derecho(area: str) -> str:
    """Lee el contenido de un área: civil, familia, societario, penal, consumidor, comercial, laboral o normas."""
    key = area.strip().lower().replace(" ", "_")
    if key not in AREA_FILES:
        return f"Área no reconocida: {area}. Use listar_areas_derecho."
    return _read_kb_file(AREA_FILES[key])


@function_tool
def leer_fase_activa() -> str:
    """Lee la definición de la fase activa del proyecto."""
    settings = get_settings()
    path = settings.agente_dir / "fases" / f"FASE_{settings.active_phase}.md"
    return path.read_text(encoding="utf-8")


def get_knowledge_tools():
    return [listar_areas_derecho, leer_area_derecho, leer_fase_activa]
