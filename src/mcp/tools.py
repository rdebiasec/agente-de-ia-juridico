"""Herramientas de lectura de la base de conocimiento (grounding stateless)."""

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

PLAYBOOK_FILES = {
    "civil": "proceso-civil-cgp.md",
    "penal": "proceso-penal-906.md",
}


def _read_kb_file(name: str) -> str:
    settings = get_settings()
    path = settings.agente_dir / "conocimiento" / name
    if not path.exists():
        return f"[No encontrado: {name}]"
    return path.read_text(encoding="utf-8")


def _list_areas() -> str:
    lines = ["Áreas del derecho cubiertas por el despacho:"]
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
def leer_playbook_proceso(materia: str) -> str:
    """Lee el playbook procesal de una materia: 'civil' (CGP) o 'penal' (Ley 906)."""
    key = materia.strip().lower()
    if key not in PLAYBOOK_FILES:
        return "Playbook no disponible. Materias con playbook: civil, penal."
    return _read_kb_file(PLAYBOOK_FILES[key])


@function_tool
def leer_normas_clave() -> str:
    """Lee las normas clave del despacho (Código Civil, Código de Comercio, etc.)."""
    return _read_kb_file(AREA_FILES["normas"])


def get_knowledge_tools():
    """Tools de grounding compartidas por los agentes."""
    return [listar_areas_derecho, leer_area_derecho, leer_playbook_proceso, leer_normas_clave]
