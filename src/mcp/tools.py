"""Herramientas de lectura de la base de conocimiento (grounding stateless).

Política de exposición (Ola 0–2):
- Chat del Gerente (slim): solo `buscar_en_expediente` (+ KB search si no hay prefetch).
  Sin dumps MD ni `listar_areas_derecho`.
- Plan / especialistas: pueden usar `include_full_reads=True` y/o `include_list_areas=True`
  cuando el paso necesita playbook/área/normas o catálogo; no vuelca dumps al chat del POC.
"""

from __future__ import annotations

from typing import Literal

from agents import function_tool

from src.config import get_settings

AREA_FILES = {
    "penal": "penal.md",
    "normas": "normas-clave.md",
}

PLAYBOOK_FILES = {
    "penal": "proceso-penal-906.md",
}

AreaDerecho = Literal["penal", "normas"]
MateriaPlaybook = Literal["penal"]


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
def leer_area_derecho(
    area: AreaDerecho,
) -> str:
    """Lee el MD de área habilitada.

    Args:
        area: Área de conocimiento. Valores: `penal` (marco penal-víctimas) o
            `normas` (normas penales clave).
    """
    key = str(area).strip().lower().replace(" ", "_")
    if key not in AREA_FILES:
        return f"Área no reconocida: {area}. Áreas habilitadas: penal, normas."
    return _read_kb_file(AREA_FILES[key])


@function_tool
def leer_playbook_proceso(
    materia: MateriaPlaybook,
) -> str:
    """Lee el playbook procesal habilitado.

    Args:
        materia: Materia del playbook. Valor habilitado: `penal` (Ley 906 de 2004).
    """
    key = str(materia).strip().lower()
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
    from src.services.rag import (
        buscar,
        contexto_para_prompt,
        last_embed_used_local_fallback,
    )

    chunks = buscar(consulta, incluir_kb=True, k=5)
    if last_embed_used_local_fallback():
        return (
            "Grounding no disponible: el servicio de embeddings está degradado. "
            "No use resultados locales hash como fuente jurídica."
        )
    return contexto_para_prompt(chunks)


@function_tool
def buscar_en_expediente(consulta: str) -> str:
    """Busca por similitud (RAG) en los documentos del expediente de la sesión activa.

    No pide ID de expediente: el runtime enlaza solo el caso de la sesión en curso
    (sin lectura cruzada de otros casos).
    """
    from src.agents.session_context import resolve_expediente_id
    from src.services.rag import (
        buscar,
        contexto_para_prompt,
        last_embed_used_local_fallback,
    )

    bound_id = resolve_expediente_id("")
    if not bound_id:
        return (
            "Búsqueda de expediente denegada: no hay sesión activa vinculada "
            "al caso en curso."
        )
    chunks = buscar(consulta, expediente_id=bound_id, incluir_kb=False, k=5)
    if last_embed_used_local_fallback():
        return (
            "Grounding del expediente no disponible: embeddings degradados. "
            "Solicite reintento; no se inyectaron coincidencias no semánticas."
        )
    return contexto_para_prompt(chunks)


def get_knowledge_tools(
    *,
    include_kb_search: bool = True,
    include_full_reads: bool = True,
    include_list_areas: bool = False,
):
    """Tools de grounding compartidas por los agentes.

    include_kb_search: RAG sobre la KB (omitir en chat del gerente si ya hay prefetch).
    include_full_reads: lecturas de archivos completos (plan/especialistas; no chat slim).
    include_list_areas: catálogo estático de áreas (off en chat Gerente; on en plan/specs).
    """
    tools = [buscar_en_expediente]
    if include_list_areas:
        tools.insert(0, listar_areas_derecho)
    if include_kb_search:
        tools.append(buscar_en_conocimiento)
    if include_full_reads:
        tools.extend(
            [
                leer_area_derecho,
                leer_playbook_proceso,
                leer_normas_clave,
            ]
        )
    return tools


# Allowlist para CI / registry honesty (function_tools reales).
REAL_FUNCTION_TOOL_NAMES = frozenset(
    {
        "listar_areas_derecho",
        "leer_area_derecho",
        "leer_playbook_proceso",
        "leer_normas_clave",
        "buscar_en_conocimiento",
        "buscar_en_expediente",
    }
)
