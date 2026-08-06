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

POC_AGENT_ID = "coordinador_caso"

# Ownership real del Gerente (resto marcado MOVE → especialista).
POC_OWNED_SKILLS = frozenset(
    {
        "clasificar_tarea_y_etapa",
        "gestionar_faltantes_expediente",
        "detectar_urgencia_penal",
        "marcar_pendientes_verificacion",
        "actualizar_tareas_responsable",
    }
)

# Dueños canónicos tras MOVE (si el archivo/DB aún listan al POC).
_MOVED_SKILL_OWNERS: dict[str, list[str]] = {
    "clasificar_fuente_factual": ["analista_cronologia_hechos"],
    "detectar_vacios_factuales": ["analista_cronologia_hechos"],
    "identificar_etapa_procesal_ley906": ["analista_ruta_procesal"],
    "crear_ruta_procesal_recomendada": ["analista_ruta_procesal"],
    "priorizar_objetivos_representacion": ["analista_representacion_victimas"],
}

# Alto riesgo: salida con efecto externo (memorial/petición) — needs_approval + modelo fuerte.
HIGH_RISK_AGENTS = {
    "redactor_documentos_juridicos",
}
# Salidas que siempre pasan por revision humana en planes (HITL calibration / Ch8).
HITL_OUTPUT_AGENTS = HIGH_RISK_AGENTS | {
    "analista_audiencias",
    "analista_seguimiento_procesal",
}


def _normalize_skill_agents(skills: dict[str, dict]) -> dict[str, dict]:
    """Alinea ownership POC vs MOVE aunque DB/archivo estén desfasados."""
    for sid, data in skills.items():
        agents = [a for a in (data.get("agents") or []) if a in VALID_AGENT_IDS]
        if sid in POC_OWNED_SKILLS:
            if POC_AGENT_ID not in agents:
                agents.insert(0, POC_AGENT_ID)
        else:
            agents = [a for a in agents if a != POC_AGENT_ID]
            if not agents and sid in _MOVED_SKILL_OWNERS:
                agents = list(_MOVED_SKILL_OWNERS[sid])
        data["agents"] = agents
    return skills


@lru_cache(maxsize=1)
def get_skills_catalog() -> dict[str, dict]:
    return _normalize_skill_agents(load_skills_catalog())


@lru_cache(maxsize=1)
def valid_skill_ids() -> frozenset[str]:
    return frozenset(get_skills_catalog().keys())


def primary_skill_for_agent(agent_id: str) -> str | None:
    """Contrato primario del agente (para plan y anclaje de instrucciones)."""
    preferred = {
        "coordinador_caso": "clasificar_tarea_y_etapa",
        "analista_cronologia_hechos": "construir_cronologia_penal",
        "analista_responsabilidad_tipicidad": "descomponer_elementos_tipo_penal",
        "analista_ruta_procesal": "identificar_etapa_procesal_ley906",
        "analista_representacion_victimas": "construir_teoria_caso_victima",
        "analista_evidencia": "inventariar_evidencia",
        "analista_audiencias": "preparar_preguntas_audiencia",
        "redactor_documentos_juridicos": "redactar_memorial_penal",
        "analista_seguimiento_procesal": "monitorear_radicado",
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


# Anclas secundarias cortas (primario + 2–3) sin explotar tokens.
_SECONDARY_SKILLS: dict[str, tuple[str, ...]] = {
    "analista_cronologia_hechos": (
        "extraer_hechos_relevantes",
        "detectar_contradicciones_factuales",
        "clasificar_fuente_factual",
    ),
    "analista_responsabilidad_tipicidad": (
        "identificar_conductas_punibles_preliminares",
        "analizar_dolo_culpa_elemento_subjetivo",
        "analizar_autoria_y_participacion",
    ),
    "analista_evidencia": (
        "clasificar_tipo_prueba",
        "construir_matriz_hecho_prueba",
        "detectar_brechas_probatorias",
    ),
    "redactor_documentos_juridicos": (
        "estructurar_hechos_fundamentos_solicitudes",
        "marcar_pendientes_verificacion",
        "controlar_tono_juridico_documento",
    ),
    "analista_calidad_juridica": (
        "detectar_alucinaciones_legales",
        "controlar_confidencialidad_datos_sensibles",
        "clasificar_aprobacion_juridica",
    ),
    "analista_ruta_procesal": (
        "evaluar_oportunidad_procesal",
        "crear_ruta_procesal_recomendada",
        "controlar_terminos_procesales_preliminares",
    ),
    "analista_representacion_victimas": (
        "analizar_derechos_victima",
        "detectar_riesgo_revictimizacion",
        "priorizar_objetivos_representacion",
    ),
    "analista_audiencias": (
        "identificar_objetivo_audiencia",
        "preparar_guion_intervencion_oral",
    ),
    "analista_seguimiento_procesal": (
        "generar_alertas_terminos_vencimientos",
        "detectar_inactividad_procesal",
    ),
}


def agent_capability_anchor(agent_id: str, *, max_chars: int = 1100) -> str:
    """Ancla multi-skill: primario + hasta 3 secundarios (briefs cortos)."""
    primary = primary_skill_for_agent(agent_id)
    parts = [skill_contract_brief(primary, max_chars=520)]
    valid = valid_skill_ids()
    for sid in _SECONDARY_SKILLS.get(agent_id, ())[:3]:
        if sid not in valid or sid == primary:
            continue
        data = get_skills_catalog().get(sid) or {}
        purpose = (data.get("purpose") or data.get("blurb") or "").strip()[:160]
        parts.append(f"- Ancilar `{sid}`: {purpose}" if purpose else f"- Ancilar `{sid}`")
    text = "\n".join(p for p in parts if p)
    if len(text) > max_chars:
        return text[: max_chars - 3] + "..."
    return text


def agent_display_name(agent_id: str) -> str:
    return agent_titulo(agent_id) if agent_id in VALID_AGENT_IDS else agent_id


def desk_label(agent_id: str) -> str:
    """Etiqueta de despacho para planes/chat (sin IDs tecnicos como interlocutor)."""
    if agent_id == "coordinador_caso":
        return "Coordinador del Caso"
    name = agent_display_name(agent_id)
    if name == agent_id:
        return "Equipo interno"
    return f"Equipo interno · {name}"
