"""Registro central de nombres SDK de agentes y etiquetas para UI/trazas."""

from __future__ import annotations

# --- Firma principal ---
AGENTE_COORDINADOR_PRINCIPAL = "agente_coordinador_principal"
AGENTE_CONOCIMIENTO_DERECHO = "agente_conocimiento_derecho"
AGENTE_RECEPCIONISTA = "agente_recepcionista"
AGENTE_ESTRATEGIA_CASOS = "agente_estrategia_casos"
AGENTE_SERVICIO_CLIENTE = "agente_servicio_cliente"
AGENTE_REDACTION_DOCUMENTAL = "agente_redaccion_documental"
AGENTE_CONCEPTOS_JURIDICOS = "agente_conceptos_juridicos"
AGENTE_TUTELA_CONSTITUCIONAL = "agente_tutela_constitucional"
AGENTE_SEGUIMIENTO_PROCESAL = "agente_seguimiento_procesal"

# --- Penal víctimas ---
AGENTE_COORDINADOR_PENAL = "agente_coordinador_penal"
SUBAGENTE_INVESTIGACION_VICTIMA = "subagente_investigacion_victima"
SUBAGENTE_PENAL_GARANTIAS = "subagente_penal_garantias"
SUBAGENTE_PENAL_JUICIOS = "subagente_penal_juicios"
SUBAGENTE_PENAL_PRUEBAS = "subagente_penal_pruebas"
SUBAGENTE_PENAL_REPARACION = "subagente_penal_reparacion"
SUBAGENTE_PENAL_NEGOCIACION = "subagente_penal_negociacion"
SUBAGENTE_PENAL_RECURSOS = "subagente_penal_recursos"

# --- Civil CGP ---
AGENTE_COORDINADOR_CIVIL = "agente_coordinador_civil"
AGENTE_CIVIL_DEMANDA = "agente_civil_demanda"
AGENTE_CIVIL_CONTESTACION = "agente_civil_contestacion"
AGENTE_CIVIL_AUDIENCIA_INICIAL = "agente_civil_audiencia_inicial"
AGENTE_CIVIL_INSTRUCCION = "agente_civil_instruccion"
AGENTE_CIVIL_PRUEBA = "agente_civil_prueba"
AGENTE_CIVIL_RECURSOS = "agente_civil_recursos"
AGENTE_CIVIL_EJECUCION = "agente_civil_ejecucion"

AGENT_LABELS: dict[str, str] = {
    AGENTE_COORDINADOR_PRINCIPAL: "Coordinador principal",
    AGENTE_CONOCIMIENTO_DERECHO: "Conocimiento del derecho",
    AGENTE_RECEPCIONISTA: "Recepcionista",
    AGENTE_ESTRATEGIA_CASOS: "Estrategia de casos",
    AGENTE_SERVICIO_CLIENTE: "Servicio al cliente",
    AGENTE_REDACTION_DOCUMENTAL: "Redacción documental",
    AGENTE_CONCEPTOS_JURIDICOS: "Conceptos jurídicos",
    AGENTE_TUTELA_CONSTITUCIONAL: "Tutela constitucional",
    AGENTE_SEGUIMIENTO_PROCESAL: "Seguimiento procesal",
    AGENTE_COORDINADOR_PENAL: "Coordinador penal (víctima)",
    SUBAGENTE_INVESTIGACION_VICTIMA: "Penal — Investigación víctima",
    SUBAGENTE_PENAL_GARANTIAS: "Penal — Garantías",
    SUBAGENTE_PENAL_JUICIOS: "Penal — Juicios",
    SUBAGENTE_PENAL_PRUEBAS: "Penal — Pruebas",
    SUBAGENTE_PENAL_REPARACION: "Penal — Reparación",
    SUBAGENTE_PENAL_NEGOCIACION: "Penal — Negociación",
    SUBAGENTE_PENAL_RECURSOS: "Penal — Recursos",
    AGENTE_COORDINADOR_CIVIL: "Coordinador civil (CGP)",
    AGENTE_CIVIL_DEMANDA: "Civil — Demanda",
    AGENTE_CIVIL_CONTESTACION: "Civil — Contestación",
    AGENTE_CIVIL_AUDIENCIA_INICIAL: "Civil — Audiencia inicial (372)",
    AGENTE_CIVIL_INSTRUCCION: "Civil — Instrucción (373)",
    AGENTE_CIVIL_PRUEBA: "Civil — Prueba",
    AGENTE_CIVIL_RECURSOS: "Civil — Recursos",
    AGENTE_CIVIL_EJECUCION: "Civil — Ejecución",
    "fallback": "Modo respaldo",
    "guardrail": "Bloqueo de seguridad",
    "error": "Ruta de error controlado",
}

LEGACY_AGENT_ALIASES: dict[str, str] = {
    # Firma — nombres históricos
    "orquestador": AGENTE_COORDINADOR_PRINCIPAL,
    "socio_coordinador": AGENTE_COORDINADOR_PRINCIPAL,
    "conocimiento_areas": AGENTE_CONOCIMIENTO_DERECHO,
    "areas_derecho": AGENTE_CONOCIMIENTO_DERECHO,
    "intake": AGENTE_RECEPCIONISTA,
    "recepcion_casos": AGENTE_RECEPCIONISTA,
    "estratega": AGENTE_ESTRATEGIA_CASOS,
    "estrategia_caso": AGENTE_ESTRATEGIA_CASOS,
    "comunicacion_clientes": AGENTE_SERVICIO_CLIENTE,
    "atencion_cliente": AGENTE_SERVICIO_CLIENTE,
    "redaccion_documental": AGENTE_REDACTION_DOCUMENTAL,
    "redaccion_escritos": AGENTE_REDACTION_DOCUMENTAL,
    "conceptos": AGENTE_CONCEPTOS_JURIDICOS,
    "conceptos_juridicos": AGENTE_CONCEPTOS_JURIDICOS,
    "tutela": AGENTE_TUTELA_CONSTITUCIONAL,
    "tutela_constitucional": AGENTE_TUTELA_CONSTITUCIONAL,
    "dependiente_judicial": AGENTE_SEGUIMIENTO_PROCESAL,
    "seguimiento_procesal": AGENTE_SEGUIMIENTO_PROCESAL,
    # Penal
    "litigante_orquestador_penal": AGENTE_COORDINADOR_PENAL,
    "coordinador_penal": AGENTE_COORDINADOR_PENAL,
    "litigante_investigacion_victima": SUBAGENTE_INVESTIGACION_VICTIMA,
    "penal_fiscalia": SUBAGENTE_INVESTIGACION_VICTIMA,
    "litigante_garantias": SUBAGENTE_PENAL_GARANTIAS,
    "penal_garantias": SUBAGENTE_PENAL_GARANTIAS,
    "litigante_conocimiento": SUBAGENTE_PENAL_JUICIOS,
    "penal_juicio": SUBAGENTE_PENAL_JUICIOS,
    "litigante_prueba": SUBAGENTE_PENAL_PRUEBAS,
    "penal_prueba": SUBAGENTE_PENAL_PRUEBAS,
    "litigante_reparacion_integral": SUBAGENTE_PENAL_REPARACION,
    "penal_reparacion": SUBAGENTE_PENAL_REPARACION,
    "litigante_negociacion_victima": SUBAGENTE_PENAL_NEGOCIACION,
    "penal_negociacion": SUBAGENTE_PENAL_NEGOCIACION,
    "litigante_recursos_penales": SUBAGENTE_PENAL_RECURSOS,
    "penal_recursos": SUBAGENTE_PENAL_RECURSOS,
    # Civil
    "litigante_civil": AGENTE_COORDINADOR_CIVIL,
    "coordinador_civil": AGENTE_COORDINADOR_CIVIL,
    "civil_demanda": AGENTE_CIVIL_DEMANDA,
    "civil_contestacion": AGENTE_CIVIL_CONTESTACION,
    "civil_audiencia_inicial": AGENTE_CIVIL_AUDIENCIA_INICIAL,
    "civil_instruccion": AGENTE_CIVIL_INSTRUCCION,
    "civil_prueba": AGENTE_CIVIL_PRUEBA,
    "civil_recursos": AGENTE_CIVIL_RECURSOS,
    "civil_ejecucion": AGENTE_CIVIL_EJECUCION,
}


def normalize_agent_name(name: str | None) -> str:
    if not name:
        return AGENTE_COORDINADOR_PRINCIPAL
    return LEGACY_AGENT_ALIASES.get(name, name)


def agent_label(name: str | None) -> str:
    key = normalize_agent_name(name)
    return AGENT_LABELS.get(key, key)
