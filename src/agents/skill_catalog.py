"""Catalogo de contratos de capacidad (skills) — Tool/Agent Registry (industria).

En este producto un "skill" NO es una tool que el LLM invoca
(`disable-model-invocation: true`). Es un **contrato de capacidad** del
registry (Patron Tool and Agent Registry / Ch10 Packt): declara inputs,
outputs, guardrails y agente responsable para planes HITL y auditoria.

Usar `skill_contract_brief()` al ejecutar un paso para anclar la fidelidad
de instrucciones (Persistent Instruction Anchoring / Ch6).
"""

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

# Alto riesgo: salida con efecto externo (memorial/tutela) — needs_approval + modelo fuerte.
HIGH_RISK_AGENTS = {
    "redactor_documentos_juridicos_penales",
    "evaluador_derechos_fundamentales_tutela",
}
# Salidas que siempre pasan por revision humana en planes (HITL calibration / Ch8).
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
    """Contrato primario del agente (para plan y anclaje de instrucciones)."""
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


def skill_contract_brief(skill_id: str | None, *, max_chars: int = 900) -> str:
    """Resumen del contrato para anclar el paso (no es tool invocable)."""
    if not skill_id:
        return ""
    data = get_skills_catalog().get(skill_id) or {}
    purpose = ""
    if data:
        purpose = (
            data.get("purpose")
            or data.get("blurb")
            or data.get("description")
            or ""
        ).strip()
    inputs, outputs = skill_io_lists(skill_id)
    lines = [
        "### Contrato de capacidad (registry — no invocable por el modelo)",
        f"- ID: `{skill_id}`",
    ]
    if purpose:
        lines.append(f"- Proposito: {purpose[:280]}")
    if inputs:
        lines.append("- Inputs esperados: " + "; ".join(inputs[:6]))
    if outputs:
        lines.append("- Outputs prometidos: " + "; ".join(outputs[:6]))
    lines.append(
        "- Regla: no inventar datos; marcar [PENDIENTE DE VERIFICAR] lo no soportado."
    )
    text = chr(10).join(lines)
    if len(text) > max_chars:
        return text[: max_chars - 3] + "..."
    return text


def agent_display_name(agent_id: str) -> str:
    return agent_titulo(agent_id) if agent_id in VALID_AGENT_IDS else agent_id


def desk_label(agent_id: str) -> str:
    """Etiqueta de despacho para planes/chat (sin IDs tecnicos como interlocutor)."""
    if agent_id == "coordinador_expediente_penal":
        return "Gerente del Caso Penal"
    name = agent_display_name(agent_id)
    if name == agent_id:
        return "Equipo interno"
    return f"Equipo interno · {name}"
