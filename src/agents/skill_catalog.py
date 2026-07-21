"""Catálogo de skills en runtime (compartido con scripts de build del portal)."""

from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from lib.catalogo_aprobacion import (  # noqa: E402
    AGENTS,
    AGENT_TITULOS,
    agent_titulo,
    load_skills_catalog,
)

VALID_AGENT_IDS = {a["id"] for a in AGENTS}
HIGH_RISK_AGENTS = {
    "redactor_documentos_juridicos_penales",
    "evaluador_derechos_fundamentales_tutela",
}
HITL_OUTPUT_AGENTS = HIGH_RISK_AGENTS | {
    "preparador_estrategico_audiencias_penales",
    "gestor_seguimiento_procesal_penal",
}


@lru_cache(maxsize=1)
def get_skills_catalog() -> dict[str, dict]:
    return load_skills_catalog()


@lru_cache(maxsize=1)
def valid_skill_ids() -> frozenset[str]:
    return frozenset(get_skills_catalog().keys())


def primary_skill_for_agent(agent_id: str) -> str | None:
    """Primer skill del catálogo que lista al agente."""
    preferred = {
        "coordinador_expediente_penal": "clasificar_tarea_y_etapa",
        "analista_cronologia_hechos_penales": "construir_cronologia_penal",
        "analista_tipicidad_y_responsabilidad_penal": "descomponer_elementos_tipo_penal",
        "analista_ruta_procesal_ley906": "identificar_etapa_procesal_ley906",
        "analista_representacion_victimas": "construir_teoria_caso_victima",
        "gestor_evidencia_y_soporte_probatorio": "inventariar_evidencia",
        "preparador_estrategico_audiencias_penales": "preparar_preguntas_audiencia",
        "redactor_documentos_juridicos_penales": "redactar_memorial_penal",
        "gestor_seguimiento_procesal_penal": "monitorear_radicado",
        "evaluador_derechos_fundamentales_tutela": "evaluar_procedencia_tutela",
        "analista_calidad_juridica": "revisar_coherencia_estrategica",
    }
    if agent_id in preferred and preferred[agent_id] in valid_skill_ids():
        return preferred[agent_id]
    for sid, data in get_skills_catalog().items():
        if agent_id in (data.get("agents") or []):
            return sid
    return None


def skill_io_lists(skill_id: str | None) -> tuple[list[str], list[str]]:
    if not skill_id:
        return [], []
    data = get_skills_catalog().get(skill_id) or {}
    inputs = [line.strip() for line in (data.get("inputs") or "").split(",") if line.strip()]
    if not inputs and data.get("inputs"):
        inputs = [data["inputs"][:120]]
    outputs = [line.strip() for line in (data.get("outputs") or "").split(",") if line.strip()]
    if not outputs and data.get("outputs"):
        outputs = [data["outputs"][:120]]
    return inputs, outputs


def agent_display_name(agent_id: str) -> str:
    return agent_titulo(agent_id) if agent_id in VALID_AGENT_IDS else agent_id


def desk_label(agent_id: str) -> str:
    """Etiqueta de despacho para planes/chat (sin IDs técnicos como interlocutor)."""
    if agent_id == "coordinador_expediente_penal":
        return "Coordinador del expediente"
    name = agent_display_name(agent_id)
    if name == agent_id:
        return "Equipo interno"
    return f"Equipo interno · {name}"
