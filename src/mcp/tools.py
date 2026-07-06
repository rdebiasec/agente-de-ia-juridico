"""Herramientas de lectura de la base de conocimiento (grounding stateless)."""

from pathlib import Path

from agents import function_tool

from src.config import get_settings

AREA_FILES = {
    "penal": "penal.md",
    "normas": "normas-clave.md",
}

PLAYBOOK_FILES = {
    "penal": "proceso-penal-906.md",
}


def _read_kb_file(name: str) -> str:
    settings = get_settings()
    path = settings.agente_dir / "conocimiento" / name
    if not path.exists():
        return f"[No encontrado: {name}]"
    return path.read_text(encoding="utf-8")


def _list_areas() -> str:
    lines = ["Cobertura jurídica habilitada (modo penal-víctimas):"]
    for area, filename in AREA_FILES.items():
        if area != "normas":
            lines.append(f"- {area}: agente/conocimiento/{filename}")
    lines.append("- normas penales clave: agente/conocimiento/normas-clave.md")
    return "\n".join(lines)


@function_tool
def listar_areas_derecho() -> str:
    """Lista la cobertura habilitada en la base de conocimiento (solo penal-víctimas)."""
    return _list_areas()


@function_tool
def leer_area_derecho(area: str) -> str:
    """Lee el contenido habilitado: penal o normas."""
    key = area.strip().lower().replace(" ", "_")
    if key not in AREA_FILES:
        return f"Área no reconocida: {area}. Áreas habilitadas: penal, normas."
    return _read_kb_file(AREA_FILES[key])


@function_tool
def leer_playbook_proceso(materia: str) -> str:
    """Lee el playbook procesal habilitado para penal (Ley 906)."""
    key = materia.strip().lower()
    if key not in PLAYBOOK_FILES:
        return "Playbook no disponible. Materia habilitada: penal."
    return _read_kb_file(PLAYBOOK_FILES[key])


@function_tool
def leer_normas_clave() -> str:
    """Lee las normas penales clave para representación de víctimas."""
    return _read_kb_file(AREA_FILES["normas"])


@function_tool
def buscar_en_conocimiento(consulta: str) -> str:
    """Busca por similitud (RAG) en la base de conocimiento de la firma.

    Devuelve fragmentos citables para fundamentar la respuesta. Úsala antes de
    afirmar normas o criterios; cita las fuentes y no inventes.
    """
    from src.services.rag import buscar, contexto_para_prompt

    chunks = buscar(consulta, incluir_kb=True, k=5)
    return contexto_para_prompt(chunks)


@function_tool
def buscar_en_expediente(consulta: str, expediente_id: str) -> str:
    """Busca por similitud (RAG) en los documentos subidos de un expediente.

    Útil para responder con base en las pruebas y escritos del caso concreto.
    """
    from src.services.rag import buscar, contexto_para_prompt

    chunks = buscar(consulta, expediente_id=expediente_id, incluir_kb=False, k=5)
    return contexto_para_prompt(chunks)


def get_knowledge_tools():
    """Tools de grounding compartidas por los agentes."""
    return [
        listar_areas_derecho,
        leer_area_derecho,
        leer_playbook_proceso,
        leer_normas_clave,
        buscar_en_conocimiento,
        buscar_en_expediente,
    ]
