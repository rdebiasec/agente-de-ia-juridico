"""Dictamenes gerenciales y acceso a pasos propuestos por skill."""

from __future__ import annotations

from lib.pasos_gerencia_matrix import get_proposed_steps, get_skill_pasos

CATEGORY_DICTAMENS: dict[str, dict[str, str]] = {
    "Skills transversales": {
        "proposito_plantilla": "Coordinación inicial: contexto, clasificación y escalamiento.",
        "encajan": "Ninguno con plantilla genérica actual; cada skill tiene función distinta.",
        "no_encajan": "Los 5 skills comparten 3 pasos idénticos pese a objetivos distintos.",
        "faltan": "Escalamiento humano en urgencia; inventario estructurado en faltantes.",
        "sobran": "Paso genérico de clasificación/priorización que no describe la tarea real.",
        "dictamen": "REESCRIBIR — pasos específicos por skill (cantidad variable según criticidad).",
    },
    "Skills de hechos y cronologia": {
        "proposito_plantilla": "Extracción factual, contraste y entrega de cronología/matriz.",
        "encajan": "construir_cronologia_penal, extraer_hechos_relevantes, detectar_contradicciones_factuales.",
        "no_encajan": "clasificar_fuente_factual; generar_preguntas_aclaracion.",
        "faltan": "Clasificación de fuente y nivel de soporte en clasificar_fuente_factual.",
        "sobran": "Entrega de cronología completa en skills que solo clasifican o preguntan.",
        "dictamen": "REESCRIBIR — diferenciar clasificación, cronología, matriz y preguntas.",
    },
    "Skills de tipicidad y responsabilidad penal": {
        "proposito_plantilla": "Hipótesis típica, vinculación hecho-prueba, riesgos de atipicidad.",
        "encajan": "descomponer_elementos_tipo_penal, mapear_tipo_penal_hecho_prueba.",
        "no_encajan": "generar_preguntas_tipicidad.",
        "faltan": "Elemento subjetivo explícito en analizar_dolo_culpa_elemento_subjetivo.",
        "sobran": "Matriz completa en skills que solo generan preguntas.",
        "dictamen": "REESCRIBIR — ajustar a tipicidad, autoría, agravantes y preguntas.",
    },
    "Skills de ruta procesal Ley 906": {
        "proposito_plantilla": "Etapa, oportunidad, actuaciones y ruta recomendada.",
        "encajan": "crear_ruta_procesal_recomendada, identificar_etapa_procesal_ley906.",
        "no_encajan": "controlar_terminos_procesales_preliminares.",
        "faltan": "Cálculo/alerta de términos con disclaimer de verificación humana.",
        "sobran": "Ruta completa en skills de solo evaluación de oportunidad.",
        "dictamen": "REESCRIBIR — separar etapa, oportunidad, términos y actuaciones.",
    },
    "Skills de representacion de victimas": {
        "proposito_plantilla": "Intereses de la víctima, teoría del caso y revictimización.",
        "encajan": "construir_teoria_caso_victima, identificar_intereses_victima.",
        "no_encajan": "detectar_riesgo_revictimizacion.",
        "faltan": "Revisión lingüística focalizada en detectar_riesgo_revictimizacion.",
        "sobran": "Alineación de teoría completa en skills de solo detección de riesgo.",
        "dictamen": "REESCRIBIR — un eje central alineado al propósito de cada skill.",
    },
    "Skills de evidencia y soporte probatorio": {
        "proposito_plantilla": "Inventario, suficiencia, brechas y plan de recaudo.",
        "encajan": "inventariar_evidencia, crear_plan_recaudo_probatorio.",
        "no_encajan": "preservar_evidencia_digital, controlar_cadena_custodia_preliminar.",
        "faltan": "Hash, custodia y preservación en evidencia digital/física.",
        "sobran": "Plan de recaudo genérico en preservación y custodia.",
        "dictamen": "REESCRIBIR — custodia y preservación como pasos propios.",
    },
    "Skills de audiencias": {
        "proposito_plantilla": "Objetivo, guion, solicitudes y checklist.",
        "encajan": "preparar_guion_intervencion_oral, identificar_objetivo_audiencia.",
        "no_encajan": "crear_checklist_previo_audiencia.",
        "faltan": "Control de no revictimización en preguntas y guiones.",
        "sobran": "Secuencia idéntica en 9 skills distintos.",
        "dictamen": "REESCRIBIR — secuencia acorde a checklist, simulación o preguntas.",
    },
    "Skills de redaccion juridica penal": {
        "proposito_plantilla": "Tipo de pieza, estructura hechos-fundamentos-peticiones, control de tono.",
        "encajan": "redactar_memorial_penal, estructurar_hechos_fundamentos_solicitudes.",
        "no_encajan": "controlar_tono_juridico_documento.",
        "faltan": "Verificación de oportunidad procesal en recursos.",
        "sobran": "Redacción completa en skill de solo control editorial.",
        "dictamen": "REESCRIBIR — separar redacción de control editorial.",
    },
    "Skills de seguimiento procesal": {
        "proposito_plantilla": "Estado operativo, términos, tareas y reportes.",
        "encajan": "monitorear_radicado, crear_reporte_estado_caso.",
        "no_encajan": "registrar_actuacion_procesal.",
        "faltan": "Bitácora específica en registrar_actuacion_procesal.",
        "sobran": "Reporte a cliente en skills puramente operativos.",
        "dictamen": "REESCRIBIR — operación vs reporte vs alertas.",
    },
    "Skills constitucionales y tutela": {
        "proposito_plantilla": "Derecho fundamental, procedencia de tutela, vía alternativa.",
        "encajan": "evaluar_procedencia_tutela, revisar_mecanismos_ordinarios.",
        "no_encajan": "evaluar_derecho_peticion, preparar_borrador_tutela_preliminar.",
        "faltan": "Análisis específico de petición y de perjuicio irremediable.",
        "sobran": "Bloque tutela idéntico en los 9 skills de la categoría.",
        "dictamen": "REESCRIBIR — subsidiariedad, petición, perjuicio y borrador diferenciados.",
    },
    "Skills de calidad juridica": {
        "proposito_plantilla": "Auditoría de soporte, riesgos y clasificación de aprobación.",
        "encajan": "clasificar_aprobacion_juridica, detectar_alucinaciones_legales.",
        "no_encajan": "verificar_citas_normativas.",
        "faltan": "Validación específica por tipo de riesgo en cada skill.",
        "sobran": "Checklist completo repetido en skills de un solo foco.",
        "dictamen": "REESCRIBIR — un eje principal por skill de calidad.",
    },
}

PRIORITY_SKILLS: dict[str, list[str]] = {
    "P0": [
        "clasificar_fuente_factual",
        "marcar_pendientes_verificacion",
        "controlar_cadena_custodia_preliminar",
        "evaluar_procedencia_tutela",
        "detectar_riesgo_improcedencia_tutela",
    ],
    "P1": [
        "preparar_guion_intervencion_oral",
        "controlar_no_revictimizacion",
        "identificar_etapa_procesal_ley906",
        "evaluar_oportunidad_procesal",
    ],
}

CATEGORY_ORDER = [
    "Skills transversales",
    "Skills de hechos y cronologia",
    "Skills de tipicidad y responsabilidad penal",
    "Skills de ruta procesal Ley 906",
    "Skills de representacion de victimas",
    "Skills de evidencia y soporte probatorio",
    "Skills de audiencias",
    "Skills de redaccion juridica penal",
    "Skills de seguimiento procesal",
    "Skills constitucionales y tutela",
    "Skills de calidad juridica",
]


def get_proposed_steps(skill_id: str, category: str = "", instruccion: str = "") -> list[str]:
    return list(get_skill_pasos(skill_id).pasos)


def skill_priority(skill_id: str) -> str:
    for level, ids in PRIORITY_SKILLS.items():
        if skill_id in ids:
            return level
    return "P2"


def skill_dictamen_gerencial(skill_id: str, category: str, desalineado: bool) -> str:
    if desalineado or skill_priority(skill_id) in ("P0", "P1"):
        return "REESCRIBIR"
    return "REESCRIBIR"  # auditoría gerencial: todos pasan de plantilla a pasos específicos


def por_que_gerencia(skill_id: str, category: str, instruccion: str, steps_actuales: list[str]) -> str:
    cat = CATEGORY_DICTAMENS.get(category, {})
    if skill_id in PRIORITY_SKILLS.get("P0", []):
        return (
            f"Skill de impacto crítico ({skill_id}): la plantilla de categoría "
            f"no ejecuta «{instruccion}»."
        )
    if cat.get("no_encajan") and skill_id in cat.get("no_encajan", ""):
        return f"Incluido en «no encajan» de {category}: pasos genéricos no reflejan el propósito."
    return (
        f"Plantilla compartida de {category} ({len(steps_actuales)} pasos idénticos en el grupo); "
        f"se requieren pasos alineados a: {instruccion}."
    )
