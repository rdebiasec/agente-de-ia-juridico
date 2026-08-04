"""Canonical agent IDs, legacy aliases, and display labels.

Legacy IDs (and gerente synonyms) resolve to the current canonical IDs so
stored sessions, traces, and UI can keep rendering after the rename.
"""

from __future__ import annotations

# old_id → new_id (plus gerente synonyms → coordinador_caso)
# Keys MUST stay as the pre-rename IDs.
LEGACY_AGENT_ALIASES: dict[str, str] = {
    "coordinador_expediente_penal": "coordinador_caso",
    "gerente": "coordinador_caso",
    "gerente_caso": "coordinador_caso",
    "analista_cronologia_hechos_penales": "analista_cronologia_hechos",
    "analista_tipicidad_y_responsabilidad_penal": "analista_responsabilidad_tipicidad",
    "analista_ruta_procesal_ley906": "analista_ruta_procesal",
    "gestor_evidencia_y_soporte_probatorio": "analista_evidencia",
    "preparador_estrategico_audiencias_penales": "analista_audiencias",
    "redactor_documentos_juridicos_penales": "redactor_documentos_juridicos",
    "gestor_seguimiento_procesal_penal": "analista_seguimiento_procesal",
}

POC_AGENT_ID = "coordinador_caso"

# Canonical display labels (product UI / docs)
AGENT_DISPLAY_LABELS: dict[str, str] = {
    "coordinador_caso": "Coordinador del Caso",
    "analista_cronologia_hechos": "Cronología y Hechos",
    "analista_responsabilidad_tipicidad": "Tipicidad y Responsabilidad",
    "analista_ruta_procesal": "Ruta Procesal Ley 906",
    "analista_representacion_victimas": "Representación de Víctimas",
    "analista_evidencia": "Evidencia y Pruebas",
    "analista_audiencias": "Audiencias Penales",
    "redactor_documentos_juridicos": "Redacción Documentos",
    "analista_seguimiento_procesal": "Seguimiento Procesal",
    "analista_calidad_juridica": "Control de Calidad Jurídica",
}


def resolve_agent_id(agent_id: str | None) -> str:
    """Map legacy / synonym IDs to the canonical agent id."""
    raw = (agent_id or "").strip()
    if not raw:
        return ""
    return LEGACY_AGENT_ALIASES.get(raw, raw)


def agent_display_label(agent_id: str | None) -> str:
    """Human label for an agent id (resolves legacy first)."""
    canonical = resolve_agent_id(agent_id)
    if not canonical:
        return ""
    return AGENT_DISPLAY_LABELS.get(canonical, canonical)
