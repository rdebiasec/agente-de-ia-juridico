"""Matriz gerencial de pasos por skill — fuente canónica (cantidad variable)."""

from __future__ import annotations

from dataclasses import dataclass

HITL = (
    "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado "
    "y someter a revisión humana."
)


@dataclass
class SkillPasosGerencia:
    tier: str
    pasos: list[str]
    reasoning: str
    por_que_n: str
    riesgos_si_faltan: str


_RAW: dict = {
  "actualizar_tareas_responsable": {
    "tier": "atomico",
    "pasos": [
      "Actualizar estado, plazo y responsable de cada tarea abierta del caso.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill atómico («Mantener lista de tareas por agente o abogado.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "2 pasos (1 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "alinear_estrategia_prueba_proceso": {
    "tier": "estrategico",
    "pasos": [
      "Contrastar teoría del caso con etapa procesal y prueba disponible.",
      "Detectar desalineaciones entre ruta 906 y plan probatorio.",
      "Proponer ajustes coordinados para representación de la víctima.",
      "Profundizar análisis de «Alinear teoria de victima con ruta procesal y plan probatorio» con referencia al expediente y norma aplicable.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill estratégico («Alinear teoria de victima con ruta procesal y plan probatorio.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "analizar_autoria_y_participacion": {
    "tier": "operativo",
    "pasos": [
      "Identificar posibles autores, coautores y partícipes según hechos.",
      "Evaluar preliminarmente conductas de cada interviniente.",
      "Señalar vacíos probatorios en autoria/participación.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Evaluar posibles roles de los intervinientes de manera preliminar.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "analizar_derechos_victima": {
    "tier": "operativo",
    "pasos": [
      "Mapear derechos de participación, información, reparación y protección aplicables.",
      "Relacionar derechos con hechos y etapa del proceso.",
      "Priorizar derechos más vulnerados o urgentes.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Mapear derechos de victima aplicables al caso.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "analizar_dolo_culpa_elemento_subjetivo": {
    "tier": "operativo",
    "pasos": [
      "Analizar elementos subjetivos (dolo, culpa) según hechos narrados.",
      "Distinguir intención, conocimiento y negligencia preliminarmente.",
      "No afirmar elemento subjetivo sin soporte suficiente.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Identificar hechos que podrian soportar dolo, culpa u otro elemento subjetivo.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "analizar_enfoque_diferencial": {
    "tier": "operativo",
    "pasos": [
      "Identificar factores de especial protección (género, edad, discapacidad, etnia, etc.).",
      "Ajustar recomendaciones a necesidades diferenciadas de la víctima.",
      "Evitar estereotipos y proteger datos sensibles.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Identificar sujetos de especial proteccion y necesidades diferenciadas.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "analizar_intervencion_victima": {
    "tier": "estrategico",
    "pasos": [
      "Identificar actuación o audiencia específica y marco Ley 906.",
      "Determinar formas de intervención de la víctima procedentes.",
      "Proponer contenido y momento de la intervención.",
      "Profundizar análisis de «Definir intervencion posible de la victima en una actuacion o audiencia» con referencia al expediente y norma aplicable.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill estratégico («Definir intervencion posible de la victima en una actuacion o audiencia.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "analizar_perjuicio_irremediable": {
    "tier": "estrategico",
    "pasos": [
      "Identificar el perjuicio alegado y su carácter actual o inminente.",
      "Evaluar si el perjuicio es grave, de difícil reparación y requiere medida urgente.",
      "Contrastar con mecanismos ordinarios y plazos procesales vigentes.",
      "Profundizar análisis de «Identificar urgencia constitucional» con referencia al expediente y norma aplicable.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill estratégico («Identificar urgencia constitucional.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "clasificar_aprobacion_juridica": {
    "tier": "operativo",
    "pasos": [
      "Revisar soporte fáctico, normativo y jurisprudencial de la salida.",
      "Aplicar checklist de riesgos (alucinación, confidencialidad, tono, revictimización).",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Clasificar la salida como aprobable, aprobable con cambios, rechazada o escalar.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "3 pasos (2 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "clasificar_fuente_factual": {
    "tier": "estrategico",
    "pasos": [
      "Inventariar cada afirmación factual en los insumos del turno.",
      "Clasificar fuente: documento, relato víctima, tercero, autoridad, inferencia o pendiente.",
      "Asignar nivel de soporte sin mezclar hecho confirmado, narrado e inferido.",
      "Construir matriz hecho-fuente preliminar (no cronología completa).",
      "Señalar afirmaciones sin fuente para verificación humana.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill estratégico («Distinguir documento, relato de victima, relato de tercero, autoridad, inferencia o dato pendiente.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "6 pasos (5 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "clasificar_tarea_y_etapa": {
    "tier": "operativo",
    "pasos": [
      "Analizar solicitud del usuario y objetivo del turno.",
      "Clasificar tipo de tarea y etapa procesal aparente del caso.",
      "Derivar al agente especialista correcto o pedir datos faltantes.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Clasificar la solicitud del usuario interno y detectar la etapa aparente del caso.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "clasificar_tipo_prueba": {
    "tier": "operativo",
    "pasos": [
      "Inventariar elementos probatorios y clasificar por tipo (documental, testimonial, digital, pericial, etc.).",
      "Registrar origen, fecha y custodia preliminar de cada elemento.",
      "Señalar elementos sin clasificación definitiva como pendientes.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Clasificar evidencia como documental, testimonial, digital, fisica, pericial, institucional o pendiente.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "construir_cronologia_penal": {
    "tier": "estrategico",
    "pasos": [
      "Extraer hechos con fecha, hora y actores de fuentes verificadas.",
      "Ordenar línea de tiempo y señalar eventos sin fecha exacta.",
      "Marcar inconsistencias entre versiones.",
      "Profundizar análisis de «Ordenar hechos en linea de tiempo» con referencia al expediente y norma aplicable.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill estratégico («Ordenar hechos en linea de tiempo.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "construir_matriz_hecho_prueba": {
    "tier": "operativo",
    "pasos": [
      "Listar hechos relevantes para la teoría del caso.",
      "Vincular cada hecho con prueba existente, faltante o en trámite.",
      "Priorizar brechas que afecten tipicidad o audiencia.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Relacionar hechos con pruebas existentes y faltantes.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "construir_teoria_caso_victima": {
    "tier": "critico",
    "pasos": [
      "Precisar intereses y objetivos de la víctima en el caso concreto.",
      "Sintetizar narrativa factual centrada en la víctima con fuentes.",
      "Vincular teoría con tipicidad preliminar y elementos del tipo.",
      "Integrar plan probatorio y actuaciones Ley 906 disponibles.",
      "Identificar fortalezas, debilidades y riesgos de la postura.",
      "Alinear con enfoque diferencial y no revictimización.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill crítico («Formular teoria preliminar desde la victima.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "7 pasos (6 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "controlar_audiencias": {
    "tier": "operativo",
    "pasos": [
      "Registrar fechas, horas, enlaces y tipo de audiencia.",
      "Vincular audiencia con checklist de preparación.",
      "Alertar conflictos de agenda o datos incompletos.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Administrar fechas, horas, enlaces y preparacion de audiencias.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "controlar_cadena_custodia_preliminar": {
    "tier": "critico",
    "pasos": [
      "Identificar evidencia que exija cadena de custodia formal.",
      "Revisar recolección: quién, cuándo, dónde y protocolo usado.",
      "Verificar traslado, almacenamiento y cadena de acceso documentada.",
      "Detectar rupturas o vacíos que afecten admisibilidad.",
      "Alertar necesidad de perito, cadena certificada u oficio urgente.",
      "Proponer medidas correctivas sin alterar el elemento probatorio.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill crítico («Alertar si la evidencia puede requerir cadena de custodia.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "7 pasos (6 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "controlar_confidencialidad_datos_sensibles": {
    "tier": "operativo",
    "pasos": [
      "Detectar PII y datos sensibles innecesarios en la salida.",
      "Proponer redacción alternativa o anonimización.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Detectar datos sensibles o innecesarios.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "3 pasos (2 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "controlar_no_revictimizacion": {
    "tier": "critico",
    "pasos": [
      "Revisar lenguaje que culpe, minimice o exponga indebidamente a la víctima.",
      "Evaluar preguntas y estrategias propuestas con enfoque de derechos.",
      "Detectar exposición innecesaria de datos sensibles o relato gráfico.",
      "Proponer reformulaciones respetuosas y centradas en derechos.",
      "Documentar riesgos residuales para decisión del abogado.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill crítico («Revisar que la salida no culpe ni exponga indebidamente a la victima.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "6 pasos (5 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "controlar_separacion_hecho_inferencia": {
    "tier": "operativo",
    "pasos": [
      "Etiquetar cada afirmación como hecho confirmado, narrado, inferido o pendiente.",
      "Detectar conclusiones presentadas como hechos sin soporte.",
      "Exigir corrección o marcación antes de uso externo.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Verificar que no se confundan hechos probados, narrados, inferidos y pendientes.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "controlar_terminos_procesales_preliminares": {
    "tier": "operativo",
    "pasos": [
      "Identificar términos relevantes según etapa y actuación pendiente.",
      "Calcular o estimar fechas límite con advertencia de verificación humana.",
      "Generar alertas con acción recomendada.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Identificar y alertar terminos relevantes. No reemplaza calculo humano.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "controlar_tono_juridico_documento": {
    "tier": "operativo",
    "pasos": [
      "Revisar borrador completo con criterios de tono formal y preciso.",
      "Detectar agresividad, especulación o lenguaje no profesional.",
      "Proponer correcciones manteniendo contenido jurídico.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Asegurar tono formal, preciso, no agresivo y no especulativo.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "controlar_tono_riesgo_reputacional": {
    "tier": "operativo",
    "pasos": [
      "Evaluar tono formal, preciso y no especulativo del documento.",
      "Detectar expresiones agresivas, promesas de resultado o riesgo reputacional.",
      "Sugerir ajustes de redacción profesional.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Revisar tono profesional y evitar lenguaje riesgoso.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "crear_checklist_previo_audiencia": {
    "tier": "operativo",
    "pasos": [
      "Listar documentos, pruebas y autorizaciones requeridas para la audiencia.",
      "Verificar fecha, enlace/sala, participantes y rol de la víctima.",
      "Cerrar checklist con responsables y plazos de preparación.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Listar requisitos antes de audiencia.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "crear_matriz_hecho_derecho_fundamental": {
    "tier": "estrategico",
    "pasos": [
      "Listar hechos verificables y narrados relevantes para la vulneración alegada.",
      "Relacionar cada hecho con el derecho fundamental comprometido y la conducta omisiva/activa.",
      "Señalar vacíos probatorios y norma constitucional de soporte preliminar.",
      "Profundizar análisis de «Relacionar hechos con derechos afectados» con referencia al expediente y norma aplicable.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill estratégico («Relacionar hechos con derechos afectados.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "crear_matriz_hecho_fuente": {
    "tier": "operativo",
    "pasos": [
      "Listar hechos relevantes uno a uno.",
      "Vincular cada hecho con fuente exacta (documento, folio, timestamp).",
      "Señalar hechos sin fuente como pendientes.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Relacionar cada hecho con su fuente exacta.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "crear_plan_recaudo_probatorio": {
    "tier": "estrategico",
    "pasos": [
      "Listar pruebas faltantes críticas según matriz hecho-prueba.",
      "Asignar responsable, plazo y vía de obtención (oficio, solicitud, peritaje).",
      "Ordenar por impacto procesal y urgencia.",
      "Profundizar análisis de «Proponer plan para obtener pruebas faltantes» con referencia al expediente y norma aplicable.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill estratégico («Proponer plan para obtener pruebas faltantes.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "crear_reporte_estado_caso": {
    "tier": "operativo",
    "pasos": [
      "Consolidar actuaciones recientes, etapa y alertas del caso.",
      "Estructurar reporte interno periódico para el despacho.",
      "Excluir estrategia sensible no apta para todo el equipo.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Crear reporte interno periodico.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "crear_resumen_ejecutivo_litigante": {
    "tier": "operativo",
    "pasos": [
      "Sintetizar objetivo, etapa procesal y postura de la víctima en una página.",
      "Incluir hechos clave, riesgos y decisiones tácticas pendientes.",
      "Formato listo para lectura previa del abogado en estrados.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Crear resumen de una pagina para el abogado que interviene.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "crear_ruta_procesal_recomendada": {
    "tier": "estrategico",
    "pasos": [
      "Sintetizar etapa actual y actuaciones pendientes.",
      "Proponer secuencia de próximos pasos con responsables y plazos.",
      "Incluir riesgos procesales de la ruta propuesta.",
      "Profundizar análisis de «Crear plan de proximos pasos procesales para revision del abogado» con referencia al expediente y norma aplicable.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill estratégico («Crear plan de proximos pasos procesales para revision del abogado.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "descomponer_elementos_tipo_penal": {
    "tier": "estrategico",
    "pasos": [
      "Seleccionar tipos penales hipotéticos aplicables.",
      "Descomponer conducta, resultado, nexo y elementos normativos.",
      "Documentar dudas de tipicidad.",
      "Profundizar análisis de «Dividir un posible delito en elementos juridicos verificables» con referencia al expediente y norma aplicable.",
      "Profundizar análisis de «Dividir un posible delito en elementos juridicos verificables» con referencia al expediente y norma aplicable.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill estratégico («Dividir un posible delito en elementos juridicos verificables.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "6 pasos (5 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "detectar_agravantes_atenuantes": {
    "tier": "operativo",
    "pasos": [
      "Revisar hechos que configuren agravantes o atenuantes aplicables.",
      "Vincular con norma penal y prueba disponible.",
      "Marcar elementos no acreditados como pendientes.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Identificar circunstancias relevantes que puedan afectar gravedad juridica.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "detectar_alucinaciones_legales": {
    "tier": "operativo",
    "pasos": [
      "Cruzar citas normativas, sentencias y radicados con fuentes verificables.",
      "Marcar referencias inventadas o no localizadas en RAG.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Detectar fuentes, hechos, conclusiones o citas inventadas.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "3 pasos (2 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "detectar_brechas_probatorias": {
    "tier": "operativo",
    "pasos": [
      "Contrastar hechos relevantes con soporte probatorio disponible.",
      "Clasificar brechas por gravedad (crítica, media, baja).",
      "Proponer acciones de cierre de brecha.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Identificar hechos relevantes sin soporte suficiente.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "detectar_contradicciones_factuales": {
    "tier": "operativo",
    "pasos": [
      "Comparar versiones de víctima, testigos, documentos y autoridades.",
      "Documentar contradicciones por hecho, fecha, monto o actor.",
      "Sugerir preguntas de aclaración no inductivas.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Encontrar inconsistencias entre versiones, documentos, fechas, valores o actores.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "detectar_inactividad_procesal": {
    "tier": "operativo",
    "pasos": [
      "Comparar última actuación con plazos razonables de la etapa.",
      "Alertar periodos sin movimiento relevante.",
      "Sugerir actuación de impulso si corresponde.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Alertar falta de movimientos por periodo relevante.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "detectar_riesgo_improcedencia_tutela": {
    "tier": "critico",
    "pasos": [
      "Inventariar vías ordinarias disponibles en la etapa penal actual.",
      "Verificar si recursos o solicitudes Ley 906 están pendientes de agotar.",
      "Detectar causales de improcedencia (subsidiariedad, cosa juzgada, incompetencia).",
      "Evaluar si el daño es actual o remediabile por vía ordinaria.",
      "Documentar probabilidad de rechazo y costo de tutela prematura.",
      "Recomendar vía alternativa preferente si la tutela es improcedente.",
      "Señalar plazo y actuación ordinaria recomendada antes de tutela.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill crítico («Detectar si tutela puede ser prematura, subsidiaria o improcedente.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "8 pasos (7 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "detectar_riesgo_revictimizacion": {
    "tier": "operativo",
    "pasos": [
      "Analizar preguntas, estrategias y lenguaje propuestos.",
      "Identificar conductas o formulaciones que revictimicen.",
      "Proponer alternativas respetuosas y centradas en derechos.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Identificar lenguaje, preguntas, acciones o estrategias que puedan revictimizar.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "detectar_riesgos_atipicidad": {
    "tier": "operativo",
    "pasos": [
      "Evaluar si faltan elementos objetivos o subjetivos del tipo.",
      "Identificar conductas alternativas más ajustadas.",
      "Alertar riesgo de atipicidad antes de actuación.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Detectar cuando un caso puede ser atipico o tener naturaleza no penal.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "detectar_riesgos_audiencia": {
    "tier": "operativo",
    "pasos": [
      "Identificar riesgos de oportunidad, revelación de estrategia y revictimización.",
      "Evaluar impacto de preguntas, solicitudes y exposición de la víctima.",
      "Proponer mitigaciones y líneas rojas para la intervención.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Detectar riesgos de intervencion, oportunidad, revelacion de estrategia o revictimizacion.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "detectar_riesgos_procesales": {
    "tier": "estrategico",
    "pasos": [
      "Revisar oportunidad, legitimación, competencia e improcedencia.",
      "Documentar riesgos de pérdida de derechos o extemporaneidad.",
      "Priorizar riesgos críticos para decisión inmediata.",
      "Profundizar análisis de «Detectar riesgos de oportunidad, legitimacion, competencia, improcedencia o perdida de derechos» con referencia al expediente y norma aplicable.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill estratégico («Detectar riesgos de oportunidad, legitimacion, competencia, improcedencia o perdida de derechos.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "detectar_urgencia_penal": {
    "tier": "estrategico",
    "pasos": [
      "Evaluar indicios de riesgo inminente (términos, libertad, integridad, evidencia).",
      "Clasificar nivel de urgencia y necesidad de atención humana inmediata.",
      "Escalar con notificación si aplica.",
      "Profundizar análisis de «Identificar si el caso requiere atencion humana inmediata» con referencia al expediente y norma aplicable.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill estratégico («Identificar si el caso requiere atencion humana inmediata.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "detectar_vacios_factuales": {
    "tier": "operativo",
    "pasos": [
      "Identificar información faltante para comprender el caso o sostener actuación.",
      "Priorizar vacíos por impacto en tipicidad, prueba o oportunidad procesal.",
      "Formular solicitud de datos al abogado o cliente.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Identificar lo que falta para comprender o probar el caso.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "estructurar_hechos_fundamentos_solicitudes": {
    "tier": "operativo",
    "pasos": [
      "Definir tipo de documento y secciones obligatorias.",
      "Organizar hechos, fundamentos normativos y peticiones en orden lógico.",
      "Verificar coherencia interna y remisiones a anexos.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Ordenar cualquier documento juridico.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "evaluar_dano_y_afectacion": {
    "tier": "operativo",
    "pasos": [
      "Organizar daños materiales, morales y afectaciones psicosociales alegadas.",
      "Vincular daño con prueba disponible o pendiente.",
      "Evitar minimizar o dramatizar sin soporte.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Organizar danos y afectaciones alegadas.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "evaluar_derecho_peticion": {
    "tier": "estrategico",
    "pasos": [
      "Verificar existencia de petición previa, destinatario y objeto solicitado.",
      "Constatar plazo de respuesta y silencio administrativo si aplica.",
      "Determinar si procede derecho de petición, tutela u otra vía según el caso.",
      "Profundizar análisis de «Revisar si existe derecho de peticion incumplido» con referencia al expediente y norma aplicable.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill estratégico («Revisar si existe derecho de peticion incumplido.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "evaluar_oportunidad_procesal": {
    "tier": "critico",
    "pasos": [
      "Ubicar la actuación propuesta en la etapa exacta del proceso penal.",
      "Verificar plazos y términos aplicables con advertencia de cálculo humano.",
      "Contrastar con actuaciones previas y estado del radicado.",
      "Determinar si es oportuna, prematura o extemporánea para la víctima.",
      "Evaluar consecuencias de actuar o no actuar en este momento.",
      "Sugerir fecha o actuación alternativa si no es oportuna.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill crítico («Determinar si una solicitud o intervencion es oportuna, prematura o extemporanea.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "7 pasos (6 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "evaluar_procedencia_tutela": {
    "tier": "critico",
    "pasos": [
      "Verificar legitimación por activa (titular del derecho y vínculo con el caso).",
      "Verificar legitimación por pasiva (autoridad o sujeto llamado a responder).",
      "Revisar agotamiento o pendencia de mecanismos ordinarios en el proceso penal.",
      "Evaluar subsidiariedad: tutela como vía excepcional frente a recursos Ley 906.",
      "Evaluar inmediatez del perjuicio y necesidad de medida urgente.",
      "Evaluar conexidad constitucional y relevancia del derecho invocado.",
      "Documentar requisitos faltantes y riesgo de improcedencia.",
      "Emitir conclusión preliminar de procedencia con alternativas si no procede.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill crítico («Evaluar legitimacion, subsidiariedad, inmediatez y relevancia constitucional.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "9 pasos (8 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "evaluar_solicitud_fiscalia_juez": {
    "tier": "operativo",
    "pasos": [
      "Verificar procedencia formal de la solicitud a Fiscalía o juez.",
      "Evaluar conveniencia estratégica para la víctima.",
      "Listar requisitos y anexos necesarios.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Evaluar si una solicitud a Fiscalia o juez es procedente y conveniente.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "evaluar_suficiencia_probatoria": {
    "tier": "estrategico",
    "pasos": [
      "Evaluar fuerza preliminar del soporte (directo, indirecto, circunstancial).",
      "Identificar elementos del tipo penal con soporte débil o ausente.",
      "Conclusión preliminar de suficiencia sin afirmar certeza judicial.",
      "Profundizar análisis de «Evaluar preliminarmente fuerza de soporte probatorio» con referencia al expediente y norma aplicable.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill estratégico («Evaluar preliminarmente fuerza de soporte probatorio.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "extraer_hechos_relevantes": {
    "tier": "operativo",
    "pasos": [
      "Procesar documentos, relatos, audios o mensajes del expediente.",
      "Extraer hechos materiales con referencia de fuente.",
      "Filtrar opiniones e inferencias no soportadas.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Extraer hechos relevantes de documentos, relatos, audios o comunicaciones.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "generar_alertas_terminos_vencimientos": {
    "tier": "operativo",
    "pasos": [
      "Identificar vencimientos próximos en calendario procesal.",
      "Clasificar alertas por criticidad.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Crear alertas de posibles vencimientos.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "3 pasos (2 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "generar_preguntas_aclaracion": {
    "tier": "operativo",
    "pasos": [
      "Identificar puntos ambiguos o incompletos en la narrativa.",
      "Redactar preguntas abiertas y no inductivas para víctima, testigos o abogado.",
      "Ordenar preguntas por prioridad probatoria.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Crear preguntas para victima, testigos o abogado humano sin inducir respuestas.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "generar_preguntas_testigos_peritos": {
    "tier": "operativo",
    "pasos": [
      "Seleccionar testigos/peritos según hechos a esclarecer.",
      "Formular preguntas neutrales alineadas con matriz hecho-prueba.",
      "Evitar preguntas inductivas o revictimizantes.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Preparar preguntas neutrales para testigos o peritos.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "generar_preguntas_tipicidad": {
    "tier": "operativo",
    "pasos": [
      "Identificar vacíos en elementos del tipo penal.",
      "Formular preguntas para víctima, testigos o abogado.",
      "Evitar preguntas que presupongan culpabilidad.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Crear preguntas para completar elementos del tipo penal.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "gestionar_faltantes_expediente": {
    "tier": "operativo",
    "pasos": [
      "Inventariar datos y documentos mínimos para el análisis solicitado.",
      "Listar faltantes por prioridad (bloqueante vs deseable).",
      "Solicitar al abogado completar antes de concluir.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Identificar datos y documentos faltantes antes de analizar o redactar.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "identificar_actores_y_roles": {
    "tier": "operativo",
    "pasos": [
      "Extraer personas y entidades mencionadas en las fuentes.",
      "Asignar rol procesal preliminar (víctima, imputado, testigo, autoridad, tercero).",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Identificar victima, presunto responsable, testigos, autoridades, terceros y entidades.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "3 pasos (2 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "identificar_conductas_punibles_preliminares": {
    "tier": "operativo",
    "pasos": [
      "Mapear conductas descritas contra tipos penales del catálogo.",
      "Priorizar hipótesis más sólidas y descartar atipicidad evidente.",
      "Presentar como hipótesis, no conclusión.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Proponer posibles conductas punibles con base en hechos, sin conclusion definitiva.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "identificar_derecho_fundamental_afectado": {
    "tier": "operativo",
    "pasos": [
      "Mapear hechos del caso contra catálogo de derechos fundamentales aplicables.",
      "Precisar titular del derecho y autoridad o sujeto vulnerador.",
      "Priorizar derechos más directamente comprometidos para análisis posterior.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Identificar posibles derechos fundamentales comprometidos.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "identificar_etapa_procesal_ley906": {
    "tier": "estrategico",
    "pasos": [
      "Revisar actuaciones y estado del radicado.",
      "Determinar etapa procesal según Ley 906 (indagación, investigación, juicio, etc.).",
      "Señalar incertidumbres si el expediente es incompleto.",
      "Profundizar análisis de «Determinar etapa del caso» con referencia al expediente y norma aplicable.",
      "Profundizar análisis de «Determinar etapa del caso» con referencia al expediente y norma aplicable.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill estratégico («Determinar etapa del caso.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "6 pasos (5 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "identificar_intereses_victima": {
    "tier": "operativo",
    "pasos": [
      "Aclarar objetivos reales de la víctima (justicia, reparación, celeridad, protección).",
      "Distinguir intereses de la víctima de objetivos procesales técnicos.",
      "Priorizar intereses para decisiones estratégicas.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Aclarar el objetivo real de la victima.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "identificar_objetivo_audiencia": {
    "tier": "estrategico",
    "pasos": [
      "Precisar tipo de audiencia y marco normativo Ley 906 aplicable.",
      "Definir objetivo jurídico y táctico para la representación de la víctima.",
      "Alinear objetivo con teoría del caso y prueba disponible.",
      "Profundizar análisis de «Definir objetivo juridico y tactico de la audiencia para la victima» con referencia al expediente y norma aplicable.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill estratégico («Definir objetivo juridico y tactico de la audiencia para la victima.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "inventariar_evidencia": {
    "tier": "operativo",
    "pasos": [
      "Recopilar todos los elementos disponibles (documentos, audios, mensajes, objetos).",
      "Registrar metadatos, hash y ubicación de custodia preliminar.",
      "Emitir inventario numerado para el expediente.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Crear inventario de todos los elementos disponibles.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "mapear_actuaciones_posibles_victima": {
    "tier": "operativo",
    "pasos": [
      "Listar actuaciones que la representación de víctimas puede promover en la etapa actual.",
      "Indicar requisitos, oportunidad y efectos esperados de cada una.",
      "Priorizar según intereses de la víctima.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Indicar que puede hacer la representacion de victimas segun etapa.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "mapear_tipo_penal_hecho_prueba": {
    "tier": "estrategico",
    "pasos": [
      "Relacionar cada elemento del tipo con hechos y pruebas.",
      "Visualizar fortalezas y debilidades por elemento.",
      "Proponer recaudo orientado a elementos débiles.",
      "Profundizar análisis de «Relacionar elementos del tipo con hechos y pruebas» con referencia al expediente y norma aplicable.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill estratégico («Relacionar elementos del tipo con hechos y pruebas.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "marcar_pendientes_verificacion": {
    "tier": "atomico",
    "pasos": [
      "Recorrer salida e insertar `[PENDIENTE DE VERIFICAR]` en cada dato, cita o hecho sin fuente.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill atómico («Marcar cualquier dato, cita o hecho incompleto como `[PENDIENTE DE VERIFICAR]`.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "2 pasos (1 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "monitorear_radicado": {
    "tier": "atomico",
    "pasos": [
      "Consultar o registrar estado del radicado con fuente y timestamp de la consulta.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill atómico («Consultar o registrar estado de radicado.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "2 pasos (1 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "preparar_borrador_tutela_preliminar": {
    "tier": "estrategico",
    "pasos": [
      "Consolidar hechos, derechos afectados y pretensiones con fuentes.",
      "Verificar que el evaluador constitucional recomendó tutela preliminarmente.",
      "Organizar insumos (hechos, fundamentos, pretensiones, anexos) para borrador.",
      "Profundizar análisis de «Preparar insumos para borrador de tutela» con referencia al expediente y norma aplicable.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill estratégico («Preparar insumos para borrador de tutela.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "preparar_contraargumentos": {
    "tier": "operativo",
    "pasos": [
      "Anticipar líneas de defensa, Fiscalía y otros intervinientes probables.",
      "Formular réplicas con soporte fáctico y normativo preliminar.",
      "Priorizar contraargumentos según objetivo de audiencia.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Anticipar argumentos de defensa, Fiscalia u otros intervinientes.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "preparar_guion_intervencion_oral": {
    "tier": "critico",
    "pasos": [
      "Definir objetivo jurídico y táctico de la intervención en audiencia.",
      "Ubicar etapa procesal y norma Ley 906 que habilita la intervención.",
      "Estructurar apertura breve con postura de la víctima.",
      "Desarrollar núcleo argumentativo solo con hechos soportados.",
      "Anticipar réplicas a defensa y Fiscalía en puntos críticos.",
      "Revisar lenguaje para evitar revictimización y filtración de estrategia.",
      "Cerrar con peticiones concretas alineadas al objetivo de audiencia.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill crítico («Estructurar intervencion oral clara y breve.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "8 pasos (7 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "preparar_preguntas_audiencia": {
    "tier": "critico",
    "pasos": [
      "Definir objetivo probatorio de cada bloque de preguntas.",
      "Seleccionar destinatario (víctima, testigo, perito) según matriz hecho-prueba.",
      "Redactar preguntas neutrales, no inductivas y en orden lógico.",
      "Revisar cada pregunta con criterio de no revictimización.",
      "Señalar preguntas de alto riesgo y alternativas más seguras.",
      "Alinear preguntas con solicitudes orales previstas en la audiencia.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill crítico («Sugerir preguntas para victima, testigos o peritos.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "7 pasos (6 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "preparar_resumen_operativo_cliente": {
    "tier": "operativo",
    "pasos": [
      "Sintetizar estado del proceso en lenguaje accesible.",
      "Incluir próximos pasos sin revelar estrategia sensible.",
      "Marcar para revisión humana antes de envío al cliente.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Crear version simple del estado del proceso para cliente, sin estrategia sensible.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "preparar_solicitudes_orales": {
    "tier": "operativo",
    "pasos": [
      "Identificar solicitudes orales procedentes según etapa y tipo de audiencia.",
      "Formular peticiones con fundamento normativo preliminar.",
      "Ordenar por prioridad y dependencias probatorias.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Formular solicitudes orales posibles segun etapa.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "preservar_evidencia_digital": {
    "tier": "critico",
    "pasos": [
      "Identificar archivos, mensajes o medios vulnerables a alteración o pérdida.",
      "Generar hash y metadatos de integridad sin modificar el original.",
      "Definir copia forense o resguardo seguro y quién custodia.",
      "Documentar cadena de custodia preliminar y accesos autorizados.",
      "Escalar a perito o autoridad si la evidencia es crítica para el caso.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill crítico («Definir medidas para proteger evidencia digital sin alterarla.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "6 pasos (5 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "priorizar_objetivos_representacion": {
    "tier": "operativo",
    "pasos": [
      "Listar objetivos posibles de la representación en el caso.",
      "Ordenar por urgencia, viabilidad y alineación con intereses de la víctima.",
      "Documentar trade-offs para decisión del abogado.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Ordenar objetivos de la representacion.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "recomendar_via_constitucional_o_alternativa": {
    "tier": "operativo",
    "pasos": [
      "Inventariar vías disponibles: tutela, petición, solicitud Ley 906, queja, etc.",
      "Comparar oportunidad, celeridad y probabilidad de éxito de cada vía.",
      "Recomendar ruta preferente con justificación y riesgos.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Recomendar tutela, derecho de peticion, solicitud procesal, queja u otra ruta.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "redactar_ampliacion_denuncia": {
    "tier": "operativo",
    "pasos": [
      "Identificar hechos nuevos y pruebas no incorporadas en denuncia previa.",
      "Estructurar ampliación con hechos, fundamentos y anexos.",
      "Marcar hechos no verificados como pendientes.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Estructurar hechos nuevos, pruebas y anexos para ampliar denuncia.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "redactar_derecho_peticion_penal": {
    "tier": "operativo",
    "pasos": [
      "Precisar destinatario, objeto y hechos que motivan la petición.",
      "Redactar peticiones claras con fundamento constitucional/legal.",
      "Incluir anexos y plazo de respuesta esperado.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Redactar derecho de peticion relacionado con autoridad o informacion del caso.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "redactar_memorial_penal": {
    "tier": "estrategico",
    "pasos": [
      "Recopilar hechos soportados y pretensiones de la víctima.",
      "Redactar memorial con estructura hechos-fundamentos-peticiones.",
      "Verificar citas y marcar pendientes antes de firma humana.",
      "Profundizar análisis de «Crear borrador de memorial penal» con referencia al expediente y norma aplicable.",
      "Profundizar análisis de «Crear borrador de memorial penal» con referencia al expediente y norma aplicable.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill estratégico («Crear borrador de memorial penal.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "6 pasos (5 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "redactar_recurso_o_intervencion_preliminar": {
    "tier": "operativo",
    "pasos": [
      "Confirmar oportunidad procesal y tipo de recurso/intervención.",
      "Redactar borrador con argumentos y peticiones procedentes.",
      "Alertar términos y requisitos de forma pendientes de verificación.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Crear borrador preliminar de recurso o intervencion, sujeto a revision procesal.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "redactar_solicitud_impulso_procesal": {
    "tier": "operativo",
    "pasos": [
      "Identificar inactividad o actuación omitida por Fiscalía o juez.",
      "Redactar solicitud de impulso con hechos y fundamento Ley 906.",
      "Proponer peticiones concretas y plazos.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Crear borrador para solicitar impulso procesal o actuaciones.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "redactar_tutela_penal_preliminar": {
    "tier": "critico",
    "pasos": [
      "Confirmar dictamen previo de procedencia tutela (no redactar si improcedente).",
      "Consolidar hechos verificables separados de inferencias y pendientes.",
      "Identificar derechos fundamentales vulnerados y autoridades accionadas.",
      "Redactar fundamentos constitucionales con citas verificadas en RAG.",
      "Formular pretensiones claras, medibles y proporcionales.",
      "Listar pruebas y anexos; marcar faltantes como pendientes.",
      "Revisar no revictimización en relato y peticiones.",
      "Control de competencia, direccionamiento y tono profesional.",
      "Entregar borrador numerado listo para revisión de firma (sin radicar).",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill crítico («Crear borrador de tutela solo si el evaluador constitucional lo recomienda preliminarmente.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "10 pasos (9 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "registrar_actuacion_procesal": {
    "tier": "atomico",
    "pasos": [
      "Registrar en bitácora: fecha, tipo, resumen y fuente de la actuación nueva.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill atómico («Registrar una actuacion nueva en la bitacora del caso.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "2 pasos (1 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "revisar_coherencia_estrategica": {
    "tier": "operativo",
    "pasos": [
      "Contrastar salida con teoría del caso y objetivos aprobados de la víctima.",
      "Detectar contradicciones internas o con actuaciones previas.",
      "Recomendar alineación o escalamiento estratégico.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Asegurar que documento o recomendacion sea coherente con la estrategia aprobada.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "revisar_mecanismos_ordinarios": {
    "tier": "estrategico",
    "pasos": [
      "Identificar recursos y actuaciones ordinarias en el proceso penal vigente.",
      "Verificar si están pendientes de interponer o ya agotados.",
      "Determinar si la tutela es subsidiaria respecto de dichos mecanismos.",
      "Profundizar análisis de «Verificar si hay vias ordinarias antes de tutela» con referencia al expediente y norma aplicable.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill estratégico («Verificar si hay vias ordinarias antes de tutela.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "seguimiento_documentos_radicados": {
    "tier": "operativo",
    "pasos": [
      "Listar documentos enviados y respuestas pendientes.",
      "Controlar versiones y fechas de radicación.",
      "Alertar plazos de respuesta institucional.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Controlar documentos enviados y respuestas pendientes.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "simular_escenarios_audiencia": {
    "tier": "estrategico",
    "pasos": [
      "Plantear escenarios favorable, intermedio y adverso probables.",
      "Definir respuesta táctica para cada escenario.",
      "Listar señales en audiencia que indiquen cambio de escenario.",
      "Profundizar análisis de «Plantear escenarios probables y preparacion del abogado» con referencia al expediente y norma aplicable.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill estratégico («Plantear escenarios probables y preparacion del abogado.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "verificar_citas_normativas": {
    "tier": "operativo",
    "pasos": [
      "Validar existencia de leyes, artículos y decretos citados.",
      "Verificar vigencia y pertinencia al caso penal-víctimas.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Verificar que normas, articulos y leyes citadas existan en el RAG o esten marcadas pendientes.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "3 pasos (2 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "verificar_hechos_soportados": {
    "tier": "operativo",
    "pasos": [
      "Listar afirmaciones factuales en el texto o análisis.",
      "Cruzar cada afirmación con fuente documental o expediente.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Revisar si cada afirmacion factual tiene fuente.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "3 pasos (2 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  },
  "verificar_jurisprudencia": {
    "tier": "operativo",
    "pasos": [
      "Validar sentencias, radicados, fechas y órganos judiciales citados.",
      "Confirmar que el precedente es pertinente al problema jurídico.",
      "Marcar jurisprudencia no verificada como pendiente.",
      "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana."
    ],
    "reasoning": "Gerencia penal-víctimas: skill operativo («Revisar sentencias, radicados, fechas y organos judiciales.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.",
    "por_que_n": "4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.",
    "riesgos_si_faltan": "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente."
  }
}


def _load() -> dict[str, SkillPasosGerencia]:
    return {
        sid: SkillPasosGerencia(
            tier=v["tier"],
            pasos=list(v["pasos"]),
            reasoning=v["reasoning"],
            por_que_n=v["por_que_n"],
            riesgos_si_faltan=v["riesgos_si_faltan"],
        )
        for sid, v in _RAW.items()
    }


MATRIX: dict[str, SkillPasosGerencia] = _load()


def get_skill_pasos(skill_id: str) -> SkillPasosGerencia:
    if skill_id not in MATRIX:
        raise KeyError(skill_id)
    return MATRIX[skill_id]


def get_proposed_steps(skill_id: str, category: str = "", instruccion: str = "") -> list[str]:
    return list(get_skill_pasos(skill_id).pasos)


def all_skills() -> dict[str, SkillPasosGerencia]:
    return dict(MATRIX)


def validate_matrix() -> None:
    counts = {len(v.pasos) for v in MATRIX.values()}
    if len(counts) < 3:
        raise ValueError(f"Matriz demasiado uniforme: tallas {counts}")
    for sid, v in MATRIX.items():
        if len(v.pasos) < 2:
            raise ValueError(f"{sid}: menos de 2 pasos")
        if v.pasos[-1] != HITL:
            raise ValueError(f"{sid}: HITL debe ser último paso")


if __name__ == "__main__":
    validate_matrix()
    from collections import Counter
    c = Counter(len(v.pasos) for v in MATRIX.values())
    print("OK", len(MATRIX), "skills", dict(sorted(c.items())), "total", sum(len(v.pasos) for v in MATRIX.values()))
