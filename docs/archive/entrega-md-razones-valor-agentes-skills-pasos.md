# Razones, valor y detalle por agente (versión simple)

## Antes de empezar: este sistema tiene 11 agentes

Estos son los 11 agentes:
- `coordinador_expediente_penal`
- `analista_cronologia_hechos_penales`
- `analista_tipicidad_y_responsabilidad_penal`
- `analista_ruta_procesal_ley906`
- `analista_representacion_victimas`
- `gestor_evidencia_y_soporte_probatorio`
- `preparador_estrategico_audiencias_penales`
- `redactor_documentos_juridicos_penales`
- `gestor_seguimiento_procesal_penal`
- `evaluador_derechos_fundamentales_tutela`
- `analista_calidad_juridica`

Cada uno tiene un trabajo específico para ayudar a la abogada a trabajar más rápido, con menos errores y con mejor control del caso.

## 1) Por qué estamos creando estos agentes

- Para ahorrar tiempo en tareas repetitivas (ordenar hechos, revisar pruebas, preparar borradores).
- Para mantener una forma de trabajo consistente en todos los casos penales de víctimas.
- Para reducir errores graves: hechos sin soporte, citas no verificadas o pasos fuera de tiempo.
- Para mejorar la preparación de audiencias y escritos con información clara y ordenada.
- Para que la abogada tenga control final con revisión humana antes de usar cualquier salida importante.

## 2) Qué valor aportan

- **Más productividad:** menos tiempo operativo y más tiempo para estrategia legal.
- **Más calidad:** mejores borradores iniciales y mejor trazabilidad de fuentes.
- **Menos riesgo:** controles para evitar inventar datos, normas o decisiones.
- **Mejor servicio a la víctima:** respuestas más claras y centradas en sus derechos.

## 3) Detalle por agente (propósito, prompt y skills con pasos)

### 3.1 `coordinador_expediente_penal`

- **Propósito del agente:** Es quien recibe la consulta y la envía al agente correcto según lo que la abogada necesite.
- **Prompt del agente en lenguaje simple:**
  - Solo trabaja en casos de penal-víctimas en Colombia.
  - Decide a qué especialista enviar cada consulta según necesidad del caso.
  - Si faltan datos importantes, primero los pide antes de dar una conclusión.
  - No inventes normas, sentencias, radicados ni hechos.
- **Skills de este agente:** 11

#### Skills y pasos (explicados simple)

- `actualizar_tareas_responsable`
  - **Archivo:** `agente/skills/actualizar_tareas_responsable/SKILL.md`
  - **Para qué sirve:** mantener lista de tareas por agente o abogado.
  - **Qué busca este skill:** Mantener lista de tareas por agente o abogado.
  - **Pasos del skill:**
    1. Actualizar actuaciones, número de proceso y estado operativo del caso.
    2. Gestionar términos, alertas y tareas por responsable.
    3. Emitir reporte interno/cliente con alertas accionables.

- `clasificar_fuente_factual`
  - **Archivo:** `agente/skills/clasificar_fuente_factual/SKILL.md`
  - **Para qué sirve:** distinguir documento, relato de victima, relato de tercero, autoridad, inferencia o dato pendiente.
  - **Qué busca este skill:** Distinguir documento, relato de victima, relato de tercero, autoridad, inferencia o dato pendiente.
  - **Pasos del skill:**
    1. Extraer hechos, actores y fechas con referencia de fuente.
    2. Contrastar inconsistencias y detectar vacíos factuales.
    3. Entregar cronología/matriz y preguntas de aclaración no inductivas.

- `clasificar_tarea_y_etapa`
  - **Archivo:** `agente/skills/clasificar_tarea_y_etapa/SKILL.md`
  - **Para qué sirve:** clasificar la solicitud del usuario interno y detectar la etapa aparente del caso.
  - **Qué busca este skill:** Clasificar la solicitud del usuario interno y detectar la etapa aparente del caso.
  - **Pasos del skill:**
    1. Levantar contexto del caso y validar datos faltantes mínimos.
    2. Ejecutar clasificación/priorización según el objetivo del turno.
    3. Registrar pendientes o tareas y escalar cuando aplique.

- `crear_ruta_procesal_recomendada`
  - **Archivo:** `agente/skills/crear_ruta_procesal_recomendada/SKILL.md`
  - **Para qué sirve:** crear plan de proximos pasos procesales para revision del abogado.
  - **Qué busca este skill:** Crear plan de proximos pasos procesales para revision del abogado.
  - **Pasos del skill:**
    1. Determinar etapa procesal y oportunidad de intervención.
    2. Evaluar actuaciones posibles, términos y riesgos procesales.
    3. Proponer ruta recomendada y tareas para ejecución.

- `detectar_urgencia_penal`
  - **Archivo:** `agente/skills/detectar_urgencia_penal/SKILL.md`
  - **Para qué sirve:** identificar si el caso requiere atencion humana inmediata.
  - **Qué busca este skill:** Identificar si el caso requiere atencion humana inmediata.
  - **Pasos del skill:**
    1. Levantar contexto del caso y validar datos faltantes mínimos.
    2. Ejecutar clasificación/priorización según el objetivo del turno.
    3. Registrar pendientes o tareas y escalar cuando aplique.

- `detectar_vacios_factuales`
  - **Archivo:** `agente/skills/detectar_vacios_factuales/SKILL.md`
  - **Para qué sirve:** identificar lo que falta para comprender o probar el caso.
  - **Qué busca este skill:** Identificar lo que falta para comprender o probar el caso.
  - **Pasos del skill:**
    1. Extraer hechos, actores y fechas con referencia de fuente.
    2. Contrastar inconsistencias y detectar vacíos factuales.
    3. Entregar cronología/matriz y preguntas de aclaración no inductivas.

- `gestionar_faltantes_expediente`
  - **Archivo:** `agente/skills/gestionar_faltantes_expediente/SKILL.md`
  - **Para qué sirve:** identificar datos y documentos faltantes antes de analizar o redactar.
  - **Qué busca este skill:** Identificar datos y documentos faltantes antes de analizar o redactar.
  - **Pasos del skill:**
    1. Levantar contexto del caso y validar datos faltantes mínimos.
    2. Ejecutar clasificación/priorización según el objetivo del turno.
    3. Registrar pendientes o tareas y escalar cuando aplique.

- `identificar_etapa_procesal_ley906`
  - **Archivo:** `agente/skills/identificar_etapa_procesal_ley906/SKILL.md`
  - **Para qué sirve:** determinar etapa del caso.
  - **Qué busca este skill:** Determinar etapa del caso.
  - **Pasos del skill:**
    1. Determinar etapa procesal y oportunidad de intervención.
    2. Evaluar actuaciones posibles, términos y riesgos procesales.
    3. Proponer ruta recomendada y tareas para ejecución.

- `marcar_pendientes_verificacion`
  - **Archivo:** `agente/skills/marcar_pendientes_verificacion/SKILL.md`
  - **Para qué sirve:** marcar cualquier dato, cita o hecho incompleto como `[PENDIENTE DE VERIFICAR]`.
  - **Qué busca este skill:** Marcar cualquier dato, cita o hecho incompleto como `[PENDIENTE DE VERIFICAR]`.
  - **Pasos del skill:**
    1. Levantar contexto del caso y validar datos faltantes mínimos.
    2. Ejecutar clasificación/priorización según el objetivo del turno.
    3. Registrar pendientes o tareas y escalar cuando aplique.

- `priorizar_objetivos_representacion`
  - **Archivo:** `agente/skills/priorizar_objetivos_representacion/SKILL.md`
  - **Para qué sirve:** ordenar objetivos de la representacion.
  - **Qué busca este skill:** Ordenar objetivos de la representacion.
  - **Pasos del skill:**
    1. Precisar intereses y derechos de la víctima en el caso concreto.
    2. Alinear teoría del caso con plan probatorio y enfoque diferencial.
    3. Mitigar hacer daño adicional a la víctima con el trato o lenguaje y priorizar objetivos de representación.

- `recomendar_via_constitucional_o_alternativa`
  - **Archivo:** `agente/skills/recomendar_via_constitucional_o_alternativa/SKILL.md`
  - **Para qué sirve:** recomendar tutela, derecho de peticion, solicitud procesal, queja u otra ruta.
  - **Qué busca este skill:** Recomendar tutela, derecho de peticion, solicitud procesal, queja u otra ruta.
  - **Pasos del skill:**
    1. Identificar derecho fundamental afectado y hechos de vulneración.
    2. Evaluar si realmente aplica (si no hay otra vía mejor, si se está actuando a tiempo y perjuicio).
    3. Recomendar tutela o vía alterna y preparar insumos de borrador.

### 3.2 `analista_cronologia_hechos_penales`

- **Propósito del agente:** Ordena los hechos del caso para que la historia quede clara y sin contradicciones.
- **Prompt del agente en lenguaje simple:**
  - Actúa con este rol especializado dentro del equipo penal-víctimas.
  - Su objetivo principal es: transformar relatos/documentos en línea de tiempo verificable,
  - No decides el fondo del caso ni inventas hechos; separa claramente:
- **Skills de este agente:** 9

#### Skills y pasos (explicados simple)

- `construir_cronologia_penal`
  - **Archivo:** `agente/skills/construir_cronologia_penal/SKILL.md`
  - **Para qué sirve:** ordenar hechos en linea de tiempo.
  - **Qué busca este skill:** Ordenar hechos en linea de tiempo.
  - **Pasos del skill:**
    1. Extraer hechos, actores y fechas con referencia de fuente.
    2. Contrastar inconsistencias y detectar vacíos factuales.
    3. Entregar cronología/matriz y preguntas de aclaración no inductivas.

- `crear_matriz_hecho_fuente`
  - **Archivo:** `agente/skills/crear_matriz_hecho_fuente/SKILL.md`
  - **Para qué sirve:** relacionar cada hecho con su fuente exacta.
  - **Qué busca este skill:** Relacionar cada hecho con su fuente exacta.
  - **Pasos del skill:**
    1. Extraer hechos, actores y fechas con referencia de fuente.
    2. Contrastar inconsistencias y detectar vacíos factuales.
    3. Entregar cronología/matriz y preguntas de aclaración no inductivas.

- `detectar_contradicciones_factuales`
  - **Archivo:** `agente/skills/detectar_contradicciones_factuales/SKILL.md`
  - **Para qué sirve:** encontrar inconsistencias entre versiones, documentos, fechas, valores o actores.
  - **Qué busca este skill:** Encontrar inconsistencias entre versiones, documentos, fechas, valores o actores.
  - **Pasos del skill:**
    1. Extraer hechos, actores y fechas con referencia de fuente.
    2. Contrastar inconsistencias y detectar vacíos factuales.
    3. Entregar cronología/matriz y preguntas de aclaración no inductivas.

- `detectar_vacios_factuales`
  - **Archivo:** `agente/skills/detectar_vacios_factuales/SKILL.md`
  - **Para qué sirve:** identificar lo que falta para comprender o probar el caso.
  - **Qué busca este skill:** Identificar lo que falta para comprender o probar el caso.
  - **Pasos del skill:**
    1. Extraer hechos, actores y fechas con referencia de fuente.
    2. Contrastar inconsistencias y detectar vacíos factuales.
    3. Entregar cronología/matriz y preguntas de aclaración no inductivas.

- `extraer_hechos_relevantes`
  - **Archivo:** `agente/skills/extraer_hechos_relevantes/SKILL.md`
  - **Para qué sirve:** extraer hechos relevantes de documentos, relatos, audios o comunicaciones.
  - **Qué busca este skill:** Extraer hechos relevantes de documentos, relatos, audios o comunicaciones.
  - **Pasos del skill:**
    1. Extraer hechos, actores y fechas con referencia de fuente.
    2. Contrastar inconsistencias y detectar vacíos factuales.
    3. Entregar cronología/matriz y preguntas de aclaración no inductivas.

- `generar_preguntas_aclaracion`
  - **Archivo:** `agente/skills/generar_preguntas_aclaracion/SKILL.md`
  - **Para qué sirve:** crear preguntas para victima, testigos o abogado humano sin inducir respuestas.
  - **Qué busca este skill:** Crear preguntas para victima, testigos o abogado humano sin inducir respuestas.
  - **Pasos del skill:**
    1. Extraer hechos, actores y fechas con referencia de fuente.
    2. Contrastar inconsistencias y detectar vacíos factuales.
    3. Entregar cronología/matriz y preguntas de aclaración no inductivas.

- `generar_preguntas_tipicidad`
  - **Archivo:** `agente/skills/generar_preguntas_tipicidad/SKILL.md`
  - **Para qué sirve:** crear preguntas para completar elementos del tipo penal.
  - **Qué busca este skill:** Crear preguntas para completar elementos del tipo penal.
  - **Pasos del skill:**
    1. Mapear hipótesis típica y descomponer elementos jurídicos.
    2. Vincular hechos y pruebas a cada elemento del tipo penal.
    3. Identificar riesgos de riesgo de que no sea delito y definir preguntas de cierre.

- `identificar_actores_y_roles`
  - **Archivo:** `agente/skills/identificar_actores_y_roles/SKILL.md`
  - **Para qué sirve:** identificar victima, presunto responsable, testigos, autoridades, terceros y entidades.
  - **Qué busca este skill:** Identificar victima, presunto responsable, testigos, autoridades, terceros y entidades.
  - **Pasos del skill:**
    1. Extraer hechos, actores y fechas con referencia de fuente.
    2. Contrastar inconsistencias y detectar vacíos factuales.
    3. Entregar cronología/matriz y preguntas de aclaración no inductivas.

- `verificar_hechos_soportados`
  - **Archivo:** `agente/skills/verificar_hechos_soportados/SKILL.md`
  - **Para qué sirve:** revisar si cada afirmacion de hechos tiene fuente.
  - **Qué busca este skill:** Revisar si cada afirmacion de hechos tiene fuente.
  - **Pasos del skill:**
    1. Levantar contexto del caso y validar datos faltantes mínimos.
    2. Ejecutar clasificación/priorización según el objetivo del turno.
    3. Registrar pendientes o tareas y escalar cuando aplique.

### 3.3 `analista_tipicidad_y_responsabilidad_penal`

- **Propósito del agente:** Revisa si los hechos sí encajan en posibles delitos y qué riesgos jurídicos hay.
- **Prompt del agente en lenguaje simple:**
  - Actúa con este rol especializado dentro del equipo penal-víctimas.
  - Su objetivo principal es: analizar preliminarmente encaje de los hechos en un delito, elementos del tipo, autoría,
  - No afirmes conclusiones definitivas ni inventes normas/decisiones anteriores de jueces y altas cortes.
- **Skills de este agente:** 9

#### Skills y pasos (explicados simple)

- `analizar_autoria_y_participacion`
  - **Archivo:** `agente/skills/analizar_autoria_y_participacion/SKILL.md`
  - **Para qué sirve:** evaluar posibles roles de los intervinientes de manera preliminar.
  - **Qué busca este skill:** Evaluar posibles roles de los intervinientes de manera preliminar.
  - **Pasos del skill:**
    1. Mapear hipótesis típica y descomponer elementos jurídicos.
    2. Vincular hechos y pruebas a cada elemento del tipo penal.
    3. Identificar riesgos de riesgo de que no sea delito y definir preguntas de cierre.

- `analizar_dolo_culpa_elemento_subjetivo`
  - **Archivo:** `agente/skills/analizar_dolo_culpa_elemento_subjetivo/SKILL.md`
  - **Para qué sirve:** identificar hechos que podrian soportar dolo, culpa u otro elemento subjetivo.
  - **Qué busca este skill:** Identificar hechos que podrian soportar dolo, culpa u otro elemento subjetivo.
  - **Pasos del skill:**
    1. Mapear hipótesis típica y descomponer elementos jurídicos.
    2. Vincular hechos y pruebas a cada elemento del tipo penal.
    3. Identificar riesgos de riesgo de que no sea delito y definir preguntas de cierre.

- `construir_matriz_hecho_prueba`
  - **Archivo:** `agente/skills/construir_matriz_hecho_prueba/SKILL.md`
  - **Para qué sirve:** relacionar hechos con pruebas existentes y faltantes.
  - **Qué busca este skill:** Relacionar hechos con pruebas existentes y faltantes.
  - **Pasos del skill:**
    1. Inventariar y clasificar evidencia disponible por tipo y origen.
    2. Evaluar suficiencia, brechas y alertas de custodia/preservación.
    3. Construir plan de recaudo probatorio con responsables y prioridad.

- `descomponer_elementos_tipo_penal`
  - **Archivo:** `agente/skills/descomponer_elementos_tipo_penal/SKILL.md`
  - **Para qué sirve:** dividir un posible delito en elementos juridicos verificables.
  - **Qué busca este skill:** Dividir un posible delito en elementos juridicos verificables.
  - **Pasos del skill:**
    1. Mapear hipótesis típica y descomponer elementos jurídicos.
    2. Vincular hechos y pruebas a cada elemento del tipo penal.
    3. Identificar riesgos de riesgo de que no sea delito y definir preguntas de cierre.

- `detectar_agravantes_atenuantes`
  - **Archivo:** `agente/skills/detectar_agravantes_atenuantes/SKILL.md`
  - **Para qué sirve:** identificar circunstancias relevantes que puedan afectar gravedad juridica.
  - **Qué busca este skill:** Identificar circunstancias relevantes que puedan afectar gravedad juridica.
  - **Pasos del skill:**
    1. Mapear hipótesis típica y descomponer elementos jurídicos.
    2. Vincular hechos y pruebas a cada elemento del tipo penal.
    3. Identificar riesgos de riesgo de que no sea delito y definir preguntas de cierre.

- `detectar_riesgos_atipicidad`
  - **Archivo:** `agente/skills/detectar_riesgos_atipicidad/SKILL.md`
  - **Para qué sirve:** detectar cuando un caso puede ser atipico o tener naturaleza no penal.
  - **Qué busca este skill:** Detectar cuando un caso puede ser atipico o tener naturaleza no penal.
  - **Pasos del skill:**
    1. Mapear hipótesis típica y descomponer elementos jurídicos.
    2. Vincular hechos y pruebas a cada elemento del tipo penal.
    3. Identificar riesgos de riesgo de que no sea delito y definir preguntas de cierre.

- `generar_preguntas_tipicidad`
  - **Archivo:** `agente/skills/generar_preguntas_tipicidad/SKILL.md`
  - **Para qué sirve:** crear preguntas para completar elementos del tipo penal.
  - **Qué busca este skill:** Crear preguntas para completar elementos del tipo penal.
  - **Pasos del skill:**
    1. Mapear hipótesis típica y descomponer elementos jurídicos.
    2. Vincular hechos y pruebas a cada elemento del tipo penal.
    3. Identificar riesgos de riesgo de que no sea delito y definir preguntas de cierre.

- `identificar_conductas_punibles_preliminares`
  - **Archivo:** `agente/skills/identificar_conductas_punibles_preliminares/SKILL.md`
  - **Para qué sirve:** proponer posibles conductas punibles con base en hechos, sin conclusion definitiva.
  - **Qué busca este skill:** Proponer posibles conductas punibles con base en hechos, sin conclusion definitiva.
  - **Pasos del skill:**
    1. Mapear hipótesis típica y descomponer elementos jurídicos.
    2. Vincular hechos y pruebas a cada elemento del tipo penal.
    3. Identificar riesgos de riesgo de que no sea delito y definir preguntas de cierre.

- `mapear_tipo_penal_hecho_prueba`
  - **Archivo:** `agente/skills/mapear_tipo_penal_hecho_prueba/SKILL.md`
  - **Para qué sirve:** relacionar elementos del tipo con hechos y pruebas.
  - **Qué busca este skill:** Relacionar elementos del tipo con hechos y pruebas.
  - **Pasos del skill:**
    1. Mapear hipótesis típica y descomponer elementos jurídicos.
    2. Vincular hechos y pruebas a cada elemento del tipo penal.
    3. Identificar riesgos de riesgo de que no sea delito y definir preguntas de cierre.

### 3.4 `analista_ruta_procesal_ley906`

- **Propósito del agente:** Define en qué etapa va el proceso y qué se puede hacer en ese momento.
- **Prompt del agente en lenguaje simple:**
  - Actúa con este rol especializado dentro del equipo penal-víctimas.
  - Su objetivo principal es: identificar etapa procesal, oportunidades de intervención, términos
  - No hagas seguimiento operativo diario (eso lo hace seguimiento procesal).
- **Skills de este agente:** 13

#### Skills y pasos (explicados simple)

- `analizar_intervencion_victima`
  - **Archivo:** `agente/skills/analizar_intervencion_victima/SKILL.md`
  - **Para qué sirve:** definir intervencion posible de la victima en una actuacion o audiencia.
  - **Qué busca este skill:** Definir intervencion posible de la victima en una actuacion o audiencia.
  - **Pasos del skill:**
    1. Determinar etapa procesal y oportunidad de intervención.
    2. Evaluar actuaciones posibles, términos y riesgos procesales.
    3. Proponer ruta recomendada y tareas para ejecución.

- `clasificar_tarea_y_etapa`
  - **Archivo:** `agente/skills/clasificar_tarea_y_etapa/SKILL.md`
  - **Para qué sirve:** clasificar la solicitud del usuario interno y detectar la etapa aparente del caso.
  - **Qué busca este skill:** Clasificar la solicitud del usuario interno y detectar la etapa aparente del caso.
  - **Pasos del skill:**
    1. Levantar contexto del caso y validar datos faltantes mínimos.
    2. Ejecutar clasificación/priorización según el objetivo del turno.
    3. Registrar pendientes o tareas y escalar cuando aplique.

- `controlar_terminos_procesales_preliminares`
  - **Archivo:** `agente/skills/controlar_terminos_procesales_preliminares/SKILL.md`
  - **Para qué sirve:** identificar y alertar terminos relevantes. No reemplaza calculo humano.
  - **Qué busca este skill:** Identificar y alertar terminos relevantes. No reemplaza calculo humano.
  - **Pasos del skill:**
    1. Determinar etapa procesal y oportunidad de intervención.
    2. Evaluar actuaciones posibles, términos y riesgos procesales.
    3. Proponer ruta recomendada y tareas para ejecución.

- `crear_ruta_procesal_recomendada`
  - **Archivo:** `agente/skills/crear_ruta_procesal_recomendada/SKILL.md`
  - **Para qué sirve:** crear plan de proximos pasos procesales para revision del abogado.
  - **Qué busca este skill:** Crear plan de proximos pasos procesales para revision del abogado.
  - **Pasos del skill:**
    1. Determinar etapa procesal y oportunidad de intervención.
    2. Evaluar actuaciones posibles, términos y riesgos procesales.
    3. Proponer ruta recomendada y tareas para ejecución.

- `detectar_inactividad_procesal`
  - **Archivo:** `agente/skills/detectar_inactividad_procesal/SKILL.md`
  - **Para qué sirve:** alertar falta de movimientos por periodo relevante.
  - **Qué busca este skill:** Alertar falta de movimientos por periodo relevante.
  - **Pasos del skill:**
    1. Actualizar actuaciones, número de proceso y estado operativo del caso.
    2. Gestionar términos, alertas y tareas por responsable.
    3. Emitir reporte interno/cliente con alertas accionables.

- `detectar_riesgos_procesales`
  - **Archivo:** `agente/skills/detectar_riesgos_procesales/SKILL.md`
  - **Para qué sirve:** detectar riesgos de oportunidad, legitimacion, competencia, improcedencia o perdida de derechos.
  - **Qué busca este skill:** Detectar riesgos de oportunidad, legitimacion, competencia, improcedencia o perdida de derechos.
  - **Pasos del skill:**
    1. Determinar etapa procesal y oportunidad de intervención.
    2. Evaluar actuaciones posibles, términos y riesgos procesales.
    3. Proponer ruta recomendada y tareas para ejecución.

- `evaluar_oportunidad_procesal`
  - **Archivo:** `agente/skills/evaluar_oportunidad_procesal/SKILL.md`
  - **Para qué sirve:** determinar si una solicitud o intervencion es oportuna, prematura o extemporanea.
  - **Qué busca este skill:** Determinar si una solicitud o intervencion es oportuna, prematura o extemporanea.
  - **Pasos del skill:**
    1. Determinar etapa procesal y oportunidad de intervención.
    2. Evaluar actuaciones posibles, términos y riesgos procesales.
    3. Proponer ruta recomendada y tareas para ejecución.

- `evaluar_solicitud_fiscalia_juez`
  - **Archivo:** `agente/skills/evaluar_solicitud_fiscalia_juez/SKILL.md`
  - **Para qué sirve:** evaluar si una solicitud a Fiscalia o juez es procedente y conveniente.
  - **Qué busca este skill:** Evaluar si una solicitud a Fiscalia o juez es procedente y conveniente.
  - **Pasos del skill:**
    1. Determinar etapa procesal y oportunidad de intervención.
    2. Evaluar actuaciones posibles, términos y riesgos procesales.
    3. Proponer ruta recomendada y tareas para ejecución.

- `generar_alertas_terminos_vencimientos`
  - **Archivo:** `agente/skills/generar_alertas_terminos_vencimientos/SKILL.md`
  - **Para qué sirve:** crear alertas de posibles vencimientos.
  - **Qué busca este skill:** Crear alertas de posibles vencimientos.
  - **Pasos del skill:**
    1. Actualizar actuaciones, número de proceso y estado operativo del caso.
    2. Gestionar términos, alertas y tareas por responsable.
    3. Emitir reporte interno/cliente con alertas accionables.

- `identificar_etapa_procesal_ley906`
  - **Archivo:** `agente/skills/identificar_etapa_procesal_ley906/SKILL.md`
  - **Para qué sirve:** determinar etapa del caso.
  - **Qué busca este skill:** Determinar etapa del caso.
  - **Pasos del skill:**
    1. Determinar etapa procesal y oportunidad de intervención.
    2. Evaluar actuaciones posibles, términos y riesgos procesales.
    3. Proponer ruta recomendada y tareas para ejecución.

- `mapear_actuaciones_posibles_victima`
  - **Archivo:** `agente/skills/mapear_actuaciones_posibles_victima/SKILL.md`
  - **Para qué sirve:** indicar que puede hacer la representacion de victimas segun etapa.
  - **Qué busca este skill:** Indicar que puede hacer la representacion de victimas segun etapa.
  - **Pasos del skill:**
    1. Determinar etapa procesal y oportunidad de intervención.
    2. Evaluar actuaciones posibles, términos y riesgos procesales.
    3. Proponer ruta recomendada y tareas para ejecución.

- `preparar_solicitudes_orales`
  - **Archivo:** `agente/skills/preparar_solicitudes_orales/SKILL.md`
  - **Para qué sirve:** formular solicitudes orales posibles segun etapa.
  - **Qué busca este skill:** Formular solicitudes orales posibles segun etapa.
  - **Pasos del skill:**
    1. Definir objetivo de audiencia y escenario procesal.
    2. Preparar guion, solicitudes, preguntas y contraargumentos.
    3. Cerrar con checklist y matriz de riesgos de intervención.

- `redactar_recurso_o_intervencion_preliminar`
  - **Archivo:** `agente/skills/redactar_recurso_o_intervencion_preliminar/SKILL.md`
  - **Para qué sirve:** crear borrador preliminar de recurso o intervencion, sujeto a revision procesal.
  - **Qué busca este skill:** Crear borrador preliminar de recurso o intervencion, sujeto a revision procesal.
  - **Pasos del skill:**
    1. Definir tipo de pieza y datos críticos exigibles.
    2. Redactar estructura hechos-fundamentos-peticiones y anexos.
    3. Aplicar control de tono/fuentes y marcar pendientes de verificación.

### 3.5 `analista_representacion_victimas`

- **Propósito del agente:** Cuida que la estrategia esté enfocada en los derechos e intereses de la víctima.
- **Prompt del agente en lenguaje simple:**
  - Actúa con este rol especializado dentro del equipo penal-víctimas.
  - Su objetivo principal es: construir teoría del caso desde derechos e intereses de la víctima,
  - No prometas resultados judiciales ni uses lenguaje revictimizante.
- **Skills de este agente:** 13

#### Skills y pasos (explicados simple)

- `alinear_estrategia_prueba_proceso`
  - **Archivo:** `agente/skills/alinear_estrategia_prueba_proceso/SKILL.md`
  - **Para qué sirve:** alinear teoria de victima con ruta procesal y plan probatorio.
  - **Qué busca este skill:** Alinear teoria de victima con ruta procesal y plan probatorio.
  - **Pasos del skill:**
    1. Precisar intereses y derechos de la víctima en el caso concreto.
    2. Alinear teoría del caso con plan probatorio y enfoque diferencial.
    3. Mitigar hacer daño adicional a la víctima con el trato o lenguaje y priorizar objetivos de representación.

- `analizar_derechos_victima`
  - **Archivo:** `agente/skills/analizar_derechos_victima/SKILL.md`
  - **Para qué sirve:** mapear derechos de victima aplicables al caso.
  - **Qué busca este skill:** Mapear derechos de victima aplicables al caso.
  - **Pasos del skill:**
    1. Precisar intereses y derechos de la víctima en el caso concreto.
    2. Alinear teoría del caso con plan probatorio y enfoque diferencial.
    3. Mitigar hacer daño adicional a la víctima con el trato o lenguaje y priorizar objetivos de representación.

- `analizar_enfoque_diferencial`
  - **Archivo:** `agente/skills/analizar_enfoque_diferencial/SKILL.md`
  - **Para qué sirve:** identificar sujetos de especial proteccion y necesidades diferenciadas.
  - **Qué busca este skill:** Identificar sujetos de especial proteccion y necesidades diferenciadas.
  - **Pasos del skill:**
    1. Precisar intereses y derechos de la víctima en el caso concreto.
    2. Alinear teoría del caso con plan probatorio y enfoque diferencial.
    3. Mitigar hacer daño adicional a la víctima con el trato o lenguaje y priorizar objetivos de representación.

- `construir_teoria_caso_victima`
  - **Archivo:** `agente/skills/construir_teoria_caso_victima/SKILL.md`
  - **Para qué sirve:** formular teoria preliminar desde la victima.
  - **Qué busca este skill:** Formular teoria preliminar desde la victima.
  - **Pasos del skill:**
    1. Precisar intereses y derechos de la víctima en el caso concreto.
    2. Alinear teoría del caso con plan probatorio y enfoque diferencial.
    3. Mitigar hacer daño adicional a la víctima con el trato o lenguaje y priorizar objetivos de representación.

- `controlar_no_revictimizacion`
  - **Archivo:** `agente/skills/controlar_no_revictimizacion/SKILL.md`
  - **Para qué sirve:** revisar que la salida no culpe ni exponga indebidamente a la victima.
  - **Qué busca este skill:** Revisar que la salida no culpe ni exponga indebidamente a la victima.
  - **Pasos del skill:**
    1. Auditar soporte de hechos, normativo y jurisprudencial.
    2. Detectar riesgos de alucinación, confidencialidad, tono y hacer daño adicional a la víctima con el trato o lenguaje.
    3. Clasificar aprobación y cambios obligatorios para revisión humana.

- `crear_plan_recaudo_probatorio`
  - **Archivo:** `agente/skills/crear_plan_recaudo_probatorio/SKILL.md`
  - **Para qué sirve:** proponer plan para obtener pruebas faltantes.
  - **Qué busca este skill:** Proponer plan para obtener pruebas faltantes.
  - **Pasos del skill:**
    1. Inventariar y clasificar evidencia disponible por tipo y origen.
    2. Evaluar suficiencia, brechas y alertas de custodia/preservación.
    3. Construir plan de recaudo probatorio con responsables y prioridad.

- `detectar_riesgo_revictimizacion`
  - **Archivo:** `agente/skills/detectar_riesgo_revictimizacion/SKILL.md`
  - **Para qué sirve:** identificar lenguaje, preguntas, acciones o estrategias que puedan revictimizar.
  - **Qué busca este skill:** Identificar lenguaje, preguntas, acciones o estrategias que puedan revictimizar.
  - **Pasos del skill:**
    1. Precisar intereses y derechos de la víctima en el caso concreto.
    2. Alinear teoría del caso con plan probatorio y enfoque diferencial.
    3. Mitigar hacer daño adicional a la víctima con el trato o lenguaje y priorizar objetivos de representación.

- `evaluar_dano_y_afectacion`
  - **Archivo:** `agente/skills/evaluar_dano_y_afectacion/SKILL.md`
  - **Para qué sirve:** organizar danos y afectaciones alegadas.
  - **Qué busca este skill:** Organizar danos y afectaciones alegadas.
  - **Pasos del skill:**
    1. Precisar intereses y derechos de la víctima en el caso concreto.
    2. Alinear teoría del caso con plan probatorio y enfoque diferencial.
    3. Mitigar hacer daño adicional a la víctima con el trato o lenguaje y priorizar objetivos de representación.

- `evaluar_suficiencia_probatoria`
  - **Archivo:** `agente/skills/evaluar_suficiencia_probatoria/SKILL.md`
  - **Para qué sirve:** evaluar preliminarmente fuerza de soporte probatorio.
  - **Qué busca este skill:** Evaluar preliminarmente fuerza de soporte probatorio.
  - **Pasos del skill:**
    1. Inventariar y clasificar evidencia disponible por tipo y origen.
    2. Evaluar suficiencia, brechas y alertas de custodia/preservación.
    3. Construir plan de recaudo probatorio con responsables y prioridad.

- `identificar_actores_y_roles`
  - **Archivo:** `agente/skills/identificar_actores_y_roles/SKILL.md`
  - **Para qué sirve:** identificar victima, presunto responsable, testigos, autoridades, terceros y entidades.
  - **Qué busca este skill:** Identificar victima, presunto responsable, testigos, autoridades, terceros y entidades.
  - **Pasos del skill:**
    1. Extraer hechos, actores y fechas con referencia de fuente.
    2. Contrastar inconsistencias y detectar vacíos factuales.
    3. Entregar cronología/matriz y preguntas de aclaración no inductivas.

- `identificar_intereses_victima`
  - **Archivo:** `agente/skills/identificar_intereses_victima/SKILL.md`
  - **Para qué sirve:** aclarar el objetivo real de la victima.
  - **Qué busca este skill:** Aclarar el objetivo real de la victima.
  - **Pasos del skill:**
    1. Precisar intereses y derechos de la víctima en el caso concreto.
    2. Alinear teoría del caso con plan probatorio y enfoque diferencial.
    3. Mitigar hacer daño adicional a la víctima con el trato o lenguaje y priorizar objetivos de representación.

- `mapear_actuaciones_posibles_victima`
  - **Archivo:** `agente/skills/mapear_actuaciones_posibles_victima/SKILL.md`
  - **Para qué sirve:** indicar que puede hacer la representacion de victimas segun etapa.
  - **Qué busca este skill:** Indicar que puede hacer la representacion de victimas segun etapa.
  - **Pasos del skill:**
    1. Determinar etapa procesal y oportunidad de intervención.
    2. Evaluar actuaciones posibles, términos y riesgos procesales.
    3. Proponer ruta recomendada y tareas para ejecución.

- `priorizar_objetivos_representacion`
  - **Archivo:** `agente/skills/priorizar_objetivos_representacion/SKILL.md`
  - **Para qué sirve:** ordenar objetivos de la representacion.
  - **Qué busca este skill:** Ordenar objetivos de la representacion.
  - **Pasos del skill:**
    1. Precisar intereses y derechos de la víctima en el caso concreto.
    2. Alinear teoría del caso con plan probatorio y enfoque diferencial.
    3. Mitigar hacer daño adicional a la víctima con el trato o lenguaje y priorizar objetivos de representación.

### 3.6 `gestor_evidencia_y_soporte_probatorio`

- **Propósito del agente:** Organiza pruebas y detecta qué evidencia falta para fortalecer el caso.
- **Prompt del agente en lenguaje simple:**
  - Actúa con este rol especializado dentro del equipo penal-víctimas.
  - Su objetivo principal es: inventariar evidencia, construir matriz hecho-prueba, detectar brechas
- **Skills de este agente:** 13

#### Skills y pasos (explicados simple)

- `clasificar_tipo_prueba`
  - **Archivo:** `agente/skills/clasificar_tipo_prueba/SKILL.md`
  - **Para qué sirve:** clasificar evidencia como documental, testimonial, digital, fisica, pericial, institucional o pendiente.
  - **Qué busca este skill:** Clasificar evidencia como documental, testimonial, digital, fisica, pericial, institucional o pendiente.
  - **Pasos del skill:**
    1. Inventariar y clasificar evidencia disponible por tipo y origen.
    2. Evaluar suficiencia, brechas y alertas de custodia/preservación.
    3. Construir plan de recaudo probatorio con responsables y prioridad.

- `construir_matriz_hecho_prueba`
  - **Archivo:** `agente/skills/construir_matriz_hecho_prueba/SKILL.md`
  - **Para qué sirve:** relacionar hechos con pruebas existentes y faltantes.
  - **Qué busca este skill:** Relacionar hechos con pruebas existentes y faltantes.
  - **Pasos del skill:**
    1. Inventariar y clasificar evidencia disponible por tipo y origen.
    2. Evaluar suficiencia, brechas y alertas de custodia/preservación.
    3. Construir plan de recaudo probatorio con responsables y prioridad.

- `controlar_cadena_custodia_preliminar`
  - **Archivo:** `agente/skills/controlar_cadena_custodia_preliminar/SKILL.md`
  - **Para qué sirve:** alertar si la evidencia puede requerir cadena de custodia.
  - **Qué busca este skill:** Alertar si la evidencia puede requerir cadena de custodia.
  - **Pasos del skill:**
    1. Inventariar y clasificar evidencia disponible por tipo y origen.
    2. Evaluar suficiencia, brechas y alertas de custodia/preservación.
    3. Construir plan de recaudo probatorio con responsables y prioridad.

- `crear_plan_recaudo_probatorio`
  - **Archivo:** `agente/skills/crear_plan_recaudo_probatorio/SKILL.md`
  - **Para qué sirve:** proponer plan para obtener pruebas faltantes.
  - **Qué busca este skill:** Proponer plan para obtener pruebas faltantes.
  - **Pasos del skill:**
    1. Inventariar y clasificar evidencia disponible por tipo y origen.
    2. Evaluar suficiencia, brechas y alertas de custodia/preservación.
    3. Construir plan de recaudo probatorio con responsables y prioridad.

- `detectar_brechas_probatorias`
  - **Archivo:** `agente/skills/detectar_brechas_probatorias/SKILL.md`
  - **Para qué sirve:** identificar hechos relevantes sin soporte suficiente.
  - **Qué busca este skill:** Identificar hechos relevantes sin soporte suficiente.
  - **Pasos del skill:**
    1. Inventariar y clasificar evidencia disponible por tipo y origen.
    2. Evaluar suficiencia, brechas y alertas de custodia/preservación.
    3. Construir plan de recaudo probatorio con responsables y prioridad.

- `evaluar_dano_y_afectacion`
  - **Archivo:** `agente/skills/evaluar_dano_y_afectacion/SKILL.md`
  - **Para qué sirve:** organizar danos y afectaciones alegadas.
  - **Qué busca este skill:** Organizar danos y afectaciones alegadas.
  - **Pasos del skill:**
    1. Precisar intereses y derechos de la víctima en el caso concreto.
    2. Alinear teoría del caso con plan probatorio y enfoque diferencial.
    3. Mitigar hacer daño adicional a la víctima con el trato o lenguaje y priorizar objetivos de representación.

- `evaluar_suficiencia_probatoria`
  - **Archivo:** `agente/skills/evaluar_suficiencia_probatoria/SKILL.md`
  - **Para qué sirve:** evaluar preliminarmente fuerza de soporte probatorio.
  - **Qué busca este skill:** Evaluar preliminarmente fuerza de soporte probatorio.
  - **Pasos del skill:**
    1. Inventariar y clasificar evidencia disponible por tipo y origen.
    2. Evaluar suficiencia, brechas y alertas de custodia/preservación.
    3. Construir plan de recaudo probatorio con responsables y prioridad.

- `extraer_hechos_relevantes`
  - **Archivo:** `agente/skills/extraer_hechos_relevantes/SKILL.md`
  - **Para qué sirve:** extraer hechos relevantes de documentos, relatos, audios o comunicaciones.
  - **Qué busca este skill:** Extraer hechos relevantes de documentos, relatos, audios o comunicaciones.
  - **Pasos del skill:**
    1. Extraer hechos, actores y fechas con referencia de fuente.
    2. Contrastar inconsistencias y detectar vacíos factuales.
    3. Entregar cronología/matriz y preguntas de aclaración no inductivas.

- `generar_preguntas_aclaracion`
  - **Archivo:** `agente/skills/generar_preguntas_aclaracion/SKILL.md`
  - **Para qué sirve:** crear preguntas para victima, testigos o abogado humano sin inducir respuestas.
  - **Qué busca este skill:** Crear preguntas para victima, testigos o abogado humano sin inducir respuestas.
  - **Pasos del skill:**
    1. Extraer hechos, actores y fechas con referencia de fuente.
    2. Contrastar inconsistencias y detectar vacíos factuales.
    3. Entregar cronología/matriz y preguntas de aclaración no inductivas.

- `generar_preguntas_testigos_peritos`
  - **Archivo:** `agente/skills/generar_preguntas_testigos_peritos/SKILL.md`
  - **Para qué sirve:** preparar preguntas neutrales para testigos o peritos.
  - **Qué busca este skill:** Preparar preguntas neutrales para testigos o peritos.
  - **Pasos del skill:**
    1. Inventariar y clasificar evidencia disponible por tipo y origen.
    2. Evaluar suficiencia, brechas y alertas de custodia/preservación.
    3. Construir plan de recaudo probatorio con responsables y prioridad.

- `inventariar_evidencia`
  - **Archivo:** `agente/skills/inventariar_evidencia/SKILL.md`
  - **Para qué sirve:** crear inventario de todos los elementos disponibles.
  - **Qué busca este skill:** Crear inventario de todos los elementos disponibles.
  - **Pasos del skill:**
    1. Inventariar y clasificar evidencia disponible por tipo y origen.
    2. Evaluar suficiencia, brechas y alertas de custodia/preservación.
    3. Construir plan de recaudo probatorio con responsables y prioridad.

- `mapear_tipo_penal_hecho_prueba`
  - **Archivo:** `agente/skills/mapear_tipo_penal_hecho_prueba/SKILL.md`
  - **Para qué sirve:** relacionar elementos del tipo con hechos y pruebas.
  - **Qué busca este skill:** Relacionar elementos del tipo con hechos y pruebas.
  - **Pasos del skill:**
    1. Mapear hipótesis típica y descomponer elementos jurídicos.
    2. Vincular hechos y pruebas a cada elemento del tipo penal.
    3. Identificar riesgos de riesgo de que no sea delito y definir preguntas de cierre.

- `preservar_evidencia_digital`
  - **Archivo:** `agente/skills/preservar_evidencia_digital/SKILL.md`
  - **Para qué sirve:** definir medidas para proteger evidencia digital sin alterarla.
  - **Qué busca este skill:** Definir medidas para proteger evidencia digital sin alterarla.
  - **Pasos del skill:**
    1. Inventariar y clasificar evidencia disponible por tipo y origen.
    2. Evaluar suficiencia, brechas y alertas de custodia/preservación.
    3. Construir plan de recaudo probatorio con responsables y prioridad.

### 3.7 `preparador_estrategico_audiencias_penales`

- **Propósito del agente:** Prepara audiencia: objetivo, guion, preguntas y solicitudes.
- **Prompt del agente en lenguaje simple:**
  - Actúa con este rol especializado dentro del equipo penal-víctimas.
  - Su objetivo principal es: preparar objetivos, guiones, solicitudes, preguntas y checklist para
  - No reemplazas la intervención oral del abogado en audiencia.
- **Skills de este agente:** 16

#### Skills y pasos (explicados simple)

- `analizar_intervencion_victima`
  - **Archivo:** `agente/skills/analizar_intervencion_victima/SKILL.md`
  - **Para qué sirve:** definir intervencion posible de la victima en una actuacion o audiencia.
  - **Qué busca este skill:** Definir intervencion posible de la victima en una actuacion o audiencia.
  - **Pasos del skill:**
    1. Determinar etapa procesal y oportunidad de intervención.
    2. Evaluar actuaciones posibles, términos y riesgos procesales.
    3. Proponer ruta recomendada y tareas para ejecución.

- `construir_cronologia_penal`
  - **Archivo:** `agente/skills/construir_cronologia_penal/SKILL.md`
  - **Para qué sirve:** ordenar hechos en linea de tiempo.
  - **Qué busca este skill:** Ordenar hechos en linea de tiempo.
  - **Pasos del skill:**
    1. Extraer hechos, actores y fechas con referencia de fuente.
    2. Contrastar inconsistencias y detectar vacíos factuales.
    3. Entregar cronología/matriz y preguntas de aclaración no inductivas.

- `construir_matriz_hecho_prueba`
  - **Archivo:** `agente/skills/construir_matriz_hecho_prueba/SKILL.md`
  - **Para qué sirve:** relacionar hechos con pruebas existentes y faltantes.
  - **Qué busca este skill:** Relacionar hechos con pruebas existentes y faltantes.
  - **Pasos del skill:**
    1. Inventariar y clasificar evidencia disponible por tipo y origen.
    2. Evaluar suficiencia, brechas y alertas de custodia/preservación.
    3. Construir plan de recaudo probatorio con responsables y prioridad.

- `construir_teoria_caso_victima`
  - **Archivo:** `agente/skills/construir_teoria_caso_victima/SKILL.md`
  - **Para qué sirve:** formular teoria preliminar desde la victima.
  - **Qué busca este skill:** Formular teoria preliminar desde la victima.
  - **Pasos del skill:**
    1. Precisar intereses y derechos de la víctima en el caso concreto.
    2. Alinear teoría del caso con plan probatorio y enfoque diferencial.
    3. Mitigar hacer daño adicional a la víctima con el trato o lenguaje y priorizar objetivos de representación.

- `controlar_audiencias`
  - **Archivo:** `agente/skills/controlar_audiencias/SKILL.md`
  - **Para qué sirve:** administrar fechas, horas, enlaces y preparacion de audiencias.
  - **Qué busca este skill:** Administrar fechas, horas, enlaces y preparacion de audiencias.
  - **Pasos del skill:**
    1. Actualizar actuaciones, número de proceso y estado operativo del caso.
    2. Gestionar términos, alertas y tareas por responsable.
    3. Emitir reporte interno/cliente con alertas accionables.

- `crear_checklist_previo_audiencia`
  - **Archivo:** `agente/skills/crear_checklist_previo_audiencia/SKILL.md`
  - **Para qué sirve:** listar requisitos antes de audiencia.
  - **Qué busca este skill:** Listar requisitos antes de audiencia.
  - **Pasos del skill:**
    1. Definir objetivo de audiencia y escenario procesal.
    2. Preparar guion, solicitudes, preguntas y contraargumentos.
    3. Cerrar con checklist y matriz de riesgos de intervención.

- `crear_resumen_ejecutivo_litigante`
  - **Archivo:** `agente/skills/crear_resumen_ejecutivo_litigante/SKILL.md`
  - **Para qué sirve:** crear resumen de una pagina para el abogado que interviene.
  - **Qué busca este skill:** Crear resumen de una pagina para el abogado que interviene.
  - **Pasos del skill:**
    1. Definir objetivo de audiencia y escenario procesal.
    2. Preparar guion, solicitudes, preguntas y contraargumentos.
    3. Cerrar con checklist y matriz de riesgos de intervención.

- `detectar_riesgo_revictimizacion`
  - **Archivo:** `agente/skills/detectar_riesgo_revictimizacion/SKILL.md`
  - **Para qué sirve:** identificar lenguaje, preguntas, acciones o estrategias que puedan revictimizar.
  - **Qué busca este skill:** Identificar lenguaje, preguntas, acciones o estrategias que puedan revictimizar.
  - **Pasos del skill:**
    1. Precisar intereses y derechos de la víctima en el caso concreto.
    2. Alinear teoría del caso con plan probatorio y enfoque diferencial.
    3. Mitigar hacer daño adicional a la víctima con el trato o lenguaje y priorizar objetivos de representación.

- `detectar_riesgos_audiencia`
  - **Archivo:** `agente/skills/detectar_riesgos_audiencia/SKILL.md`
  - **Para qué sirve:** detectar riesgos de intervencion, oportunidad, revelacion de estrategia o revictimizacion.
  - **Qué busca este skill:** Detectar riesgos de intervencion, oportunidad, revelacion de estrategia o revictimizacion.
  - **Pasos del skill:**
    1. Definir objetivo de audiencia y escenario procesal.
    2. Preparar guion, solicitudes, preguntas y contraargumentos.
    3. Cerrar con checklist y matriz de riesgos de intervención.

- `generar_preguntas_testigos_peritos`
  - **Archivo:** `agente/skills/generar_preguntas_testigos_peritos/SKILL.md`
  - **Para qué sirve:** preparar preguntas neutrales para testigos o peritos.
  - **Qué busca este skill:** Preparar preguntas neutrales para testigos o peritos.
  - **Pasos del skill:**
    1. Inventariar y clasificar evidencia disponible por tipo y origen.
    2. Evaluar suficiencia, brechas y alertas de custodia/preservación.
    3. Construir plan de recaudo probatorio con responsables y prioridad.

- `identificar_objetivo_audiencia`
  - **Archivo:** `agente/skills/identificar_objetivo_audiencia/SKILL.md`
  - **Para qué sirve:** definir objetivo juridico y tactico de la audiencia para la victima.
  - **Qué busca este skill:** Definir objetivo juridico y tactico de la audiencia para la victima.
  - **Pasos del skill:**
    1. Definir objetivo de audiencia y escenario procesal.
    2. Preparar guion, solicitudes, preguntas y contraargumentos.
    3. Cerrar con checklist y matriz de riesgos de intervención.

- `preparar_contraargumentos`
  - **Archivo:** `agente/skills/preparar_contraargumentos/SKILL.md`
  - **Para qué sirve:** anticipar argumentos de defensa, Fiscalia u otros intervinientes.
  - **Qué busca este skill:** Anticipar argumentos de defensa, Fiscalia u otros intervinientes.
  - **Pasos del skill:**
    1. Definir objetivo de audiencia y escenario procesal.
    2. Preparar guion, solicitudes, preguntas y contraargumentos.
    3. Cerrar con checklist y matriz de riesgos de intervención.

- `preparar_guion_intervencion_oral`
  - **Archivo:** `agente/skills/preparar_guion_intervencion_oral/SKILL.md`
  - **Para qué sirve:** estructurar intervencion oral clara y breve.
  - **Qué busca este skill:** Estructurar intervencion oral clara y breve.
  - **Pasos del skill:**
    1. Definir objetivo de audiencia y escenario procesal.
    2. Preparar guion, solicitudes, preguntas y contraargumentos.
    3. Cerrar con checklist y matriz de riesgos de intervención.

- `preparar_preguntas_audiencia`
  - **Archivo:** `agente/skills/preparar_preguntas_audiencia/SKILL.md`
  - **Para qué sirve:** sugerir preguntas para victima, testigos o peritos.
  - **Qué busca este skill:** Sugerir preguntas para victima, testigos o peritos.
  - **Pasos del skill:**
    1. Definir objetivo de audiencia y escenario procesal.
    2. Preparar guion, solicitudes, preguntas y contraargumentos.
    3. Cerrar con checklist y matriz de riesgos de intervención.

- `preparar_solicitudes_orales`
  - **Archivo:** `agente/skills/preparar_solicitudes_orales/SKILL.md`
  - **Para qué sirve:** formular solicitudes orales posibles segun etapa.
  - **Qué busca este skill:** Formular solicitudes orales posibles segun etapa.
  - **Pasos del skill:**
    1. Definir objetivo de audiencia y escenario procesal.
    2. Preparar guion, solicitudes, preguntas y contraargumentos.
    3. Cerrar con checklist y matriz de riesgos de intervención.

- `simular_escenarios_audiencia`
  - **Archivo:** `agente/skills/simular_escenarios_audiencia/SKILL.md`
  - **Para qué sirve:** plantear escenarios probables y preparacion del abogado.
  - **Qué busca este skill:** Plantear escenarios probables y preparacion del abogado.
  - **Pasos del skill:**
    1. Definir objetivo de audiencia y escenario procesal.
    2. Preparar guion, solicitudes, preguntas y contraargumentos.
    3. Cerrar con checklist y matriz de riesgos de intervención.

### 3.8 `redactor_documentos_juridicos_penales`

- **Propósito del agente:** Convierte el análisis en borradores de escritos penales listos para revisión.
- **Prompt del agente en lenguaje simple:**
  - Actúa con este rol especializado dentro del equipo penal-víctimas.
  - Su objetivo principal es: convertir análisis en borradores revisables (memoriales, solicitudes,
  - No inventes hechos, citas, radicados ni anexos; marca pendientes de verificación.
- **Skills de este agente:** 16

#### Skills y pasos (explicados simple)

- `controlar_separacion_hecho_inferencia`
  - **Archivo:** `agente/skills/controlar_separacion_hecho_inferencia/SKILL.md`
  - **Para qué sirve:** verificar que no se confundan hechos probados, narrados, inferidos y pendientes.
  - **Qué busca este skill:** Verificar que no se confundan hechos probados, narrados, inferidos y pendientes.
  - **Pasos del skill:**
    1. Auditar soporte de hechos, normativo y jurisprudencial.
    2. Detectar riesgos de alucinación, confidencialidad, tono y hacer daño adicional a la víctima con el trato o lenguaje.
    3. Clasificar aprobación y cambios obligatorios para revisión humana.

- `controlar_tono_juridico_documento`
  - **Archivo:** `agente/skills/controlar_tono_juridico_documento/SKILL.md`
  - **Para qué sirve:** asegurar tono formal, preciso, no agresivo y no especulativo.
  - **Qué busca este skill:** Asegurar tono formal, preciso, no agresivo y no especulativo.
  - **Pasos del skill:**
    1. Definir tipo de pieza y datos críticos exigibles.
    2. Redactar estructura hechos-fundamentos-peticiones y anexos.
    3. Aplicar control de tono/fuentes y marcar pendientes de verificación.

- `controlar_tono_riesgo_reputacional`
  - **Archivo:** `agente/skills/controlar_tono_riesgo_reputacional/SKILL.md`
  - **Para qué sirve:** revisar tono profesional y evitar lenguaje riesgoso.
  - **Qué busca este skill:** Revisar tono profesional y evitar lenguaje riesgoso.
  - **Pasos del skill:**
    1. Auditar soporte de hechos, normativo y jurisprudencial.
    2. Detectar riesgos de alucinación, confidencialidad, tono y hacer daño adicional a la víctima con el trato o lenguaje.
    3. Clasificar aprobación y cambios obligatorios para revisión humana.

- `estructurar_hechos_fundamentos_solicitudes`
  - **Archivo:** `agente/skills/estructurar_hechos_fundamentos_solicitudes/SKILL.md`
  - **Para qué sirve:** ordenar cualquier documento juridico.
  - **Qué busca este skill:** Ordenar cualquier documento juridico.
  - **Pasos del skill:**
    1. Definir tipo de pieza y datos críticos exigibles.
    2. Redactar estructura hechos-fundamentos-peticiones y anexos.
    3. Aplicar control de tono/fuentes y marcar pendientes de verificación.

- `evaluar_derecho_peticion`
  - **Archivo:** `agente/skills/evaluar_derecho_peticion/SKILL.md`
  - **Para qué sirve:** revisar si existe derecho de peticion incumplido.
  - **Qué busca este skill:** Revisar si existe derecho de peticion incumplido.
  - **Pasos del skill:**
    1. Identificar derecho fundamental afectado y hechos de vulneración.
    2. Evaluar si realmente aplica (si no hay otra vía mejor, si se está actuando a tiempo y perjuicio).
    3. Recomendar tutela o vía alterna y preparar insumos de borrador.

- `evaluar_solicitud_fiscalia_juez`
  - **Archivo:** `agente/skills/evaluar_solicitud_fiscalia_juez/SKILL.md`
  - **Para qué sirve:** evaluar si una solicitud a Fiscalia o juez es procedente y conveniente.
  - **Qué busca este skill:** Evaluar si una solicitud a Fiscalia o juez es procedente y conveniente.
  - **Pasos del skill:**
    1. Determinar etapa procesal y oportunidad de intervención.
    2. Evaluar actuaciones posibles, términos y riesgos procesales.
    3. Proponer ruta recomendada y tareas para ejecución.

- `extraer_hechos_relevantes`
  - **Archivo:** `agente/skills/extraer_hechos_relevantes/SKILL.md`
  - **Para qué sirve:** extraer hechos relevantes de documentos, relatos, audios o comunicaciones.
  - **Qué busca este skill:** Extraer hechos relevantes de documentos, relatos, audios o comunicaciones.
  - **Pasos del skill:**
    1. Extraer hechos, actores y fechas con referencia de fuente.
    2. Contrastar inconsistencias y detectar vacíos factuales.
    3. Entregar cronología/matriz y preguntas de aclaración no inductivas.

- `preparar_borrador_tutela_preliminar`
  - **Archivo:** `agente/skills/preparar_borrador_tutela_preliminar/SKILL.md`
  - **Para qué sirve:** preparar insumos para borrador de tutela.
  - **Qué busca este skill:** Preparar insumos para borrador de tutela.
  - **Pasos del skill:**
    1. Identificar derecho fundamental afectado y hechos de vulneración.
    2. Evaluar si realmente aplica (si no hay otra vía mejor, si se está actuando a tiempo y perjuicio).
    3. Recomendar tutela o vía alterna y preparar insumos de borrador.

- `redactar_ampliacion_denuncia`
  - **Archivo:** `agente/skills/redactar_ampliacion_denuncia/SKILL.md`
  - **Para qué sirve:** estructurar hechos nuevos, pruebas y anexos para ampliar denuncia.
  - **Qué busca este skill:** Estructurar hechos nuevos, pruebas y anexos para ampliar denuncia.
  - **Pasos del skill:**
    1. Definir tipo de pieza y datos críticos exigibles.
    2. Redactar estructura hechos-fundamentos-peticiones y anexos.
    3. Aplicar control de tono/fuentes y marcar pendientes de verificación.

- `redactar_derecho_peticion_penal`
  - **Archivo:** `agente/skills/redactar_derecho_peticion_penal/SKILL.md`
  - **Para qué sirve:** redactar derecho de peticion relacionado con autoridad o informacion del caso.
  - **Qué busca este skill:** Redactar derecho de peticion relacionado con autoridad o informacion del caso.
  - **Pasos del skill:**
    1. Definir tipo de pieza y datos críticos exigibles.
    2. Redactar estructura hechos-fundamentos-peticiones y anexos.
    3. Aplicar control de tono/fuentes y marcar pendientes de verificación.

- `redactar_memorial_penal`
  - **Archivo:** `agente/skills/redactar_memorial_penal/SKILL.md`
  - **Para qué sirve:** crear borrador de memorial penal.
  - **Qué busca este skill:** Crear borrador de memorial penal.
  - **Pasos del skill:**
    1. Definir tipo de pieza y datos críticos exigibles.
    2. Redactar estructura hechos-fundamentos-peticiones y anexos.
    3. Aplicar control de tono/fuentes y marcar pendientes de verificación.

- `redactar_recurso_o_intervencion_preliminar`
  - **Archivo:** `agente/skills/redactar_recurso_o_intervencion_preliminar/SKILL.md`
  - **Para qué sirve:** crear borrador preliminar de recurso o intervencion, sujeto a revision procesal.
  - **Qué busca este skill:** Crear borrador preliminar de recurso o intervencion, sujeto a revision procesal.
  - **Pasos del skill:**
    1. Definir tipo de pieza y datos críticos exigibles.
    2. Redactar estructura hechos-fundamentos-peticiones y anexos.
    3. Aplicar control de tono/fuentes y marcar pendientes de verificación.

- `redactar_solicitud_impulso_procesal`
  - **Archivo:** `agente/skills/redactar_solicitud_impulso_procesal/SKILL.md`
  - **Para qué sirve:** crear borrador para solicitar impulso procesal o actuaciones.
  - **Qué busca este skill:** Crear borrador para solicitar impulso procesal o actuaciones.
  - **Pasos del skill:**
    1. Definir tipo de pieza y datos críticos exigibles.
    2. Redactar estructura hechos-fundamentos-peticiones y anexos.
    3. Aplicar control de tono/fuentes y marcar pendientes de verificación.

- `redactar_tutela_penal_preliminar`
  - **Archivo:** `agente/skills/redactar_tutela_penal_preliminar/SKILL.md`
  - **Para qué sirve:** crear borrador de tutela solo si el evaluador constitucional lo recomienda preliminarmente.
  - **Qué busca este skill:** Crear borrador de tutela solo si el evaluador constitucional lo recomienda preliminarmente.
  - **Pasos del skill:**
    1. Definir tipo de pieza y datos críticos exigibles.
    2. Redactar estructura hechos-fundamentos-peticiones y anexos.
    3. Aplicar control de tono/fuentes y marcar pendientes de verificación.

- `verificar_citas_normativas`
  - **Archivo:** `agente/skills/verificar_citas_normativas/SKILL.md`
  - **Para qué sirve:** verificar que normas, articulos y leyes citadas existan en el RAG o esten marcadas pendientes.
  - **Qué busca este skill:** Verificar que normas, articulos y leyes citadas existan en el RAG o esten marcadas pendientes.
  - **Pasos del skill:**
    1. Auditar soporte de hechos, normativo y jurisprudencial.
    2. Detectar riesgos de alucinación, confidencialidad, tono y hacer daño adicional a la víctima con el trato o lenguaje.
    3. Clasificar aprobación y cambios obligatorios para revisión humana.

- `verificar_hechos_soportados`
  - **Archivo:** `agente/skills/verificar_hechos_soportados/SKILL.md`
  - **Para qué sirve:** revisar si cada afirmacion de hechos tiene fuente.
  - **Qué busca este skill:** Revisar si cada afirmacion de hechos tiene fuente.
  - **Pasos del skill:**
    1. Levantar contexto del caso y validar datos faltantes mínimos.
    2. Ejecutar clasificación/priorización según el objetivo del turno.
    3. Registrar pendientes o tareas y escalar cuando aplique.

### 3.9 `gestor_seguimiento_procesal_penal`

- **Propósito del agente:** Lleva control de radicados, actuaciones, tareas y vencimientos.
- **Prompt del agente en lenguaje simple:**
  - Actúa con este rol especializado dentro del equipo penal-víctimas.
  - Su objetivo principal es: monitorear radicados, actuaciones, audiencias, términos operativos,
- **Skills de este agente:** 12

#### Skills y pasos (explicados simple)

- `actualizar_tareas_responsable`
  - **Archivo:** `agente/skills/actualizar_tareas_responsable/SKILL.md`
  - **Para qué sirve:** mantener lista de tareas por agente o abogado.
  - **Qué busca este skill:** Mantener lista de tareas por agente o abogado.
  - **Pasos del skill:**
    1. Actualizar actuaciones, número de proceso y estado operativo del caso.
    2. Gestionar términos, alertas y tareas por responsable.
    3. Emitir reporte interno/cliente con alertas accionables.

- `controlar_audiencias`
  - **Archivo:** `agente/skills/controlar_audiencias/SKILL.md`
  - **Para qué sirve:** administrar fechas, horas, enlaces y preparacion de audiencias.
  - **Qué busca este skill:** Administrar fechas, horas, enlaces y preparacion de audiencias.
  - **Pasos del skill:**
    1. Actualizar actuaciones, número de proceso y estado operativo del caso.
    2. Gestionar términos, alertas y tareas por responsable.
    3. Emitir reporte interno/cliente con alertas accionables.

- `controlar_terminos_procesales_preliminares`
  - **Archivo:** `agente/skills/controlar_terminos_procesales_preliminares/SKILL.md`
  - **Para qué sirve:** identificar y alertar terminos relevantes. No reemplaza calculo humano.
  - **Qué busca este skill:** Identificar y alertar terminos relevantes. No reemplaza calculo humano.
  - **Pasos del skill:**
    1. Determinar etapa procesal y oportunidad de intervención.
    2. Evaluar actuaciones posibles, términos y riesgos procesales.
    3. Proponer ruta recomendada y tareas para ejecución.

- `crear_checklist_previo_audiencia`
  - **Archivo:** `agente/skills/crear_checklist_previo_audiencia/SKILL.md`
  - **Para qué sirve:** listar requisitos antes de audiencia.
  - **Qué busca este skill:** Listar requisitos antes de audiencia.
  - **Pasos del skill:**
    1. Definir objetivo de audiencia y escenario procesal.
    2. Preparar guion, solicitudes, preguntas y contraargumentos.
    3. Cerrar con checklist y matriz de riesgos de intervención.

- `crear_reporte_estado_caso`
  - **Archivo:** `agente/skills/crear_reporte_estado_caso/SKILL.md`
  - **Para qué sirve:** crear reporte interno periodico.
  - **Qué busca este skill:** Crear reporte interno periodico.
  - **Pasos del skill:**
    1. Actualizar actuaciones, número de proceso y estado operativo del caso.
    2. Gestionar términos, alertas y tareas por responsable.
    3. Emitir reporte interno/cliente con alertas accionables.

- `detectar_inactividad_procesal`
  - **Archivo:** `agente/skills/detectar_inactividad_procesal/SKILL.md`
  - **Para qué sirve:** alertar falta de movimientos por periodo relevante.
  - **Qué busca este skill:** Alertar falta de movimientos por periodo relevante.
  - **Pasos del skill:**
    1. Actualizar actuaciones, número de proceso y estado operativo del caso.
    2. Gestionar términos, alertas y tareas por responsable.
    3. Emitir reporte interno/cliente con alertas accionables.

- `detectar_urgencia_penal`
  - **Archivo:** `agente/skills/detectar_urgencia_penal/SKILL.md`
  - **Para qué sirve:** identificar si el caso requiere atencion humana inmediata.
  - **Qué busca este skill:** Identificar si el caso requiere atencion humana inmediata.
  - **Pasos del skill:**
    1. Levantar contexto del caso y validar datos faltantes mínimos.
    2. Ejecutar clasificación/priorización según el objetivo del turno.
    3. Registrar pendientes o tareas y escalar cuando aplique.

- `generar_alertas_terminos_vencimientos`
  - **Archivo:** `agente/skills/generar_alertas_terminos_vencimientos/SKILL.md`
  - **Para qué sirve:** crear alertas de posibles vencimientos.
  - **Qué busca este skill:** Crear alertas de posibles vencimientos.
  - **Pasos del skill:**
    1. Actualizar actuaciones, número de proceso y estado operativo del caso.
    2. Gestionar términos, alertas y tareas por responsable.
    3. Emitir reporte interno/cliente con alertas accionables.

- `monitorear_radicado`
  - **Archivo:** `agente/skills/monitorear_radicado/SKILL.md`
  - **Para qué sirve:** consultar o registrar estado de número de proceso.
  - **Qué busca este skill:** Consultar o registrar estado de número de proceso.
  - **Pasos del skill:**
    1. Actualizar actuaciones, número de proceso y estado operativo del caso.
    2. Gestionar términos, alertas y tareas por responsable.
    3. Emitir reporte interno/cliente con alertas accionables.

- `preparar_resumen_operativo_cliente`
  - **Archivo:** `agente/skills/preparar_resumen_operativo_cliente/SKILL.md`
  - **Para qué sirve:** crear version simple del estado del proceso para cliente, sin estrategia sensible.
  - **Qué busca este skill:** Crear version simple del estado del proceso para cliente, sin estrategia sensible.
  - **Pasos del skill:**
    1. Actualizar actuaciones, número de proceso y estado operativo del caso.
    2. Gestionar términos, alertas y tareas por responsable.
    3. Emitir reporte interno/cliente con alertas accionables.

- `registrar_actuacion_procesal`
  - **Archivo:** `agente/skills/registrar_actuacion_procesal/SKILL.md`
  - **Para qué sirve:** registrar una actuacion nueva en la bitacora del caso.
  - **Qué busca este skill:** Registrar una actuacion nueva en la bitacora del caso.
  - **Pasos del skill:**
    1. Actualizar actuaciones, número de proceso y estado operativo del caso.
    2. Gestionar términos, alertas y tareas por responsable.
    3. Emitir reporte interno/cliente con alertas accionables.

- `seguimiento_documentos_radicados`
  - **Archivo:** `agente/skills/seguimiento_documentos_radicados/SKILL.md`
  - **Para qué sirve:** controlar documentos enviados y respuestas pendientes.
  - **Qué busca este skill:** Controlar documentos enviados y respuestas pendientes.
  - **Pasos del skill:**
    1. Actualizar actuaciones, número de proceso y estado operativo del caso.
    2. Gestionar términos, alertas y tareas por responsable.
    3. Emitir reporte interno/cliente con alertas accionables.

### 3.10 `evaluador_derechos_fundamentales_tutela`

- **Propósito del agente:** Evalúa si una tutela sí aplica o si conviene otra vía.
- **Prompt del agente en lenguaje simple:**
  - Actúa con este rol especializado dentro del equipo penal-víctimas.
  - Su objetivo principal es: evaluar derechos fundamentales y si realmente aplica preliminar de tutela
  - No conviertas todo en tutela; revisa si no hay otra vía mejor, si se está actuando a tiempo y riesgos.
- **Skills de este agente:** 13

#### Skills y pasos (explicados simple)

- `analizar_derechos_victima`
  - **Archivo:** `agente/skills/analizar_derechos_victima/SKILL.md`
  - **Para qué sirve:** mapear derechos de victima aplicables al caso.
  - **Qué busca este skill:** Mapear derechos de victima aplicables al caso.
  - **Pasos del skill:**
    1. Precisar intereses y derechos de la víctima en el caso concreto.
    2. Alinear teoría del caso con plan probatorio y enfoque diferencial.
    3. Mitigar hacer daño adicional a la víctima con el trato o lenguaje y priorizar objetivos de representación.

- `analizar_enfoque_diferencial`
  - **Archivo:** `agente/skills/analizar_enfoque_diferencial/SKILL.md`
  - **Para qué sirve:** identificar sujetos de especial proteccion y necesidades diferenciadas.
  - **Qué busca este skill:** Identificar sujetos de especial proteccion y necesidades diferenciadas.
  - **Pasos del skill:**
    1. Precisar intereses y derechos de la víctima en el caso concreto.
    2. Alinear teoría del caso con plan probatorio y enfoque diferencial.
    3. Mitigar hacer daño adicional a la víctima con el trato o lenguaje y priorizar objetivos de representación.

- `analizar_perjuicio_irremediable`
  - **Archivo:** `agente/skills/analizar_perjuicio_irremediable/SKILL.md`
  - **Para qué sirve:** identificar urgencia constitucional.
  - **Qué busca este skill:** Identificar urgencia constitucional.
  - **Pasos del skill:**
    1. Identificar derecho fundamental afectado y hechos de vulneración.
    2. Evaluar si realmente aplica (si no hay otra vía mejor, si se está actuando a tiempo y perjuicio).
    3. Recomendar tutela o vía alterna y preparar insumos de borrador.

- `crear_matriz_hecho_derecho_fundamental`
  - **Archivo:** `agente/skills/crear_matriz_hecho_derecho_fundamental/SKILL.md`
  - **Para qué sirve:** relacionar hechos con derechos afectados.
  - **Qué busca este skill:** Relacionar hechos con derechos afectados.
  - **Pasos del skill:**
    1. Identificar derecho fundamental afectado y hechos de vulneración.
    2. Evaluar si realmente aplica (si no hay otra vía mejor, si se está actuando a tiempo y perjuicio).
    3. Recomendar tutela o vía alterna y preparar insumos de borrador.

- `detectar_riesgo_improcedencia_tutela`
  - **Archivo:** `agente/skills/detectar_riesgo_improcedencia_tutela/SKILL.md`
  - **Para qué sirve:** detectar si tutela puede ser prematura, subsidiaria o improcedente.
  - **Qué busca este skill:** Detectar si tutela puede ser prematura, subsidiaria o improcedente.
  - **Pasos del skill:**
    1. Identificar derecho fundamental afectado y hechos de vulneración.
    2. Evaluar si realmente aplica (si no hay otra vía mejor, si se está actuando a tiempo y perjuicio).
    3. Recomendar tutela o vía alterna y preparar insumos de borrador.

- `evaluar_derecho_peticion`
  - **Archivo:** `agente/skills/evaluar_derecho_peticion/SKILL.md`
  - **Para qué sirve:** revisar si existe derecho de peticion incumplido.
  - **Qué busca este skill:** Revisar si existe derecho de peticion incumplido.
  - **Pasos del skill:**
    1. Identificar derecho fundamental afectado y hechos de vulneración.
    2. Evaluar si realmente aplica (si no hay otra vía mejor, si se está actuando a tiempo y perjuicio).
    3. Recomendar tutela o vía alterna y preparar insumos de borrador.

- `evaluar_procedencia_tutela`
  - **Archivo:** `agente/skills/evaluar_procedencia_tutela/SKILL.md`
  - **Para qué sirve:** evaluar legitimacion, si no hay otra vía mejor, si se está actuando a tiempo y relevancia constitucional.
  - **Qué busca este skill:** Evaluar legitimacion, si no hay otra vía mejor, si se está actuando a tiempo y relevancia constitucional.
  - **Pasos del skill:**
    1. Identificar derecho fundamental afectado y hechos de vulneración.
    2. Evaluar si realmente aplica (si no hay otra vía mejor, si se está actuando a tiempo y perjuicio).
    3. Recomendar tutela o vía alterna y preparar insumos de borrador.

- `identificar_derecho_fundamental_afectado`
  - **Archivo:** `agente/skills/identificar_derecho_fundamental_afectado/SKILL.md`
  - **Para qué sirve:** identificar posibles derechos fundamentales comprometidos.
  - **Qué busca este skill:** Identificar posibles derechos fundamentales comprometidos.
  - **Pasos del skill:**
    1. Identificar derecho fundamental afectado y hechos de vulneración.
    2. Evaluar si realmente aplica (si no hay otra vía mejor, si se está actuando a tiempo y perjuicio).
    3. Recomendar tutela o vía alterna y preparar insumos de borrador.

- `preparar_borrador_tutela_preliminar`
  - **Archivo:** `agente/skills/preparar_borrador_tutela_preliminar/SKILL.md`
  - **Para qué sirve:** preparar insumos para borrador de tutela.
  - **Qué busca este skill:** Preparar insumos para borrador de tutela.
  - **Pasos del skill:**
    1. Identificar derecho fundamental afectado y hechos de vulneración.
    2. Evaluar si realmente aplica (si no hay otra vía mejor, si se está actuando a tiempo y perjuicio).
    3. Recomendar tutela o vía alterna y preparar insumos de borrador.

- `recomendar_via_constitucional_o_alternativa`
  - **Archivo:** `agente/skills/recomendar_via_constitucional_o_alternativa/SKILL.md`
  - **Para qué sirve:** recomendar tutela, derecho de peticion, solicitud procesal, queja u otra ruta.
  - **Qué busca este skill:** Recomendar tutela, derecho de peticion, solicitud procesal, queja u otra ruta.
  - **Pasos del skill:**
    1. Identificar derecho fundamental afectado y hechos de vulneración.
    2. Evaluar si realmente aplica (si no hay otra vía mejor, si se está actuando a tiempo y perjuicio).
    3. Recomendar tutela o vía alterna y preparar insumos de borrador.

- `redactar_derecho_peticion_penal`
  - **Archivo:** `agente/skills/redactar_derecho_peticion_penal/SKILL.md`
  - **Para qué sirve:** redactar derecho de peticion relacionado con autoridad o informacion del caso.
  - **Qué busca este skill:** Redactar derecho de peticion relacionado con autoridad o informacion del caso.
  - **Pasos del skill:**
    1. Definir tipo de pieza y datos críticos exigibles.
    2. Redactar estructura hechos-fundamentos-peticiones y anexos.
    3. Aplicar control de tono/fuentes y marcar pendientes de verificación.

- `redactar_tutela_penal_preliminar`
  - **Archivo:** `agente/skills/redactar_tutela_penal_preliminar/SKILL.md`
  - **Para qué sirve:** crear borrador de tutela solo si el evaluador constitucional lo recomienda preliminarmente.
  - **Qué busca este skill:** Crear borrador de tutela solo si el evaluador constitucional lo recomienda preliminarmente.
  - **Pasos del skill:**
    1. Definir tipo de pieza y datos críticos exigibles.
    2. Redactar estructura hechos-fundamentos-peticiones y anexos.
    3. Aplicar control de tono/fuentes y marcar pendientes de verificación.

- `revisar_mecanismos_ordinarios`
  - **Archivo:** `agente/skills/revisar_mecanismos_ordinarios/SKILL.md`
  - **Para qué sirve:** verificar si hay vias ordinarias antes de tutela.
  - **Qué busca este skill:** Verificar si hay vias ordinarias antes de tutela.
  - **Pasos del skill:**
    1. Identificar derecho fundamental afectado y hechos de vulneración.
    2. Evaluar si realmente aplica (si no hay otra vía mejor, si se está actuando a tiempo y perjuicio).
    3. Recomendar tutela o vía alterna y preparar insumos de borrador.

### 3.11 `analista_calidad_juridica`

- **Propósito del agente:** Hace revisión final para evitar errores y riesgos antes de enviar algo afuera.
- **Prompt del agente en lenguaje simple:**
  - Actúa con este rol especializado dentro del equipo penal-víctimas.
  - Su objetivo principal es: verificar soporte de hechos, citas normativas, consistencia estratégica,
- **Skills de este agente:** 26

#### Skills y pasos (explicados simple)

- `alinear_estrategia_prueba_proceso`
  - **Archivo:** `agente/skills/alinear_estrategia_prueba_proceso/SKILL.md`
  - **Para qué sirve:** alinear teoria de victima con ruta procesal y plan probatorio.
  - **Qué busca este skill:** Alinear teoria de victima con ruta procesal y plan probatorio.
  - **Pasos del skill:**
    1. Precisar intereses y derechos de la víctima en el caso concreto.
    2. Alinear teoría del caso con plan probatorio y enfoque diferencial.
    3. Mitigar hacer daño adicional a la víctima con el trato o lenguaje y priorizar objetivos de representación.

- `clasificar_aprobacion_juridica`
  - **Archivo:** `agente/skills/clasificar_aprobacion_juridica/SKILL.md`
  - **Para qué sirve:** clasificar la salida como aprobable, aprobable con cambios, rechazada o escalar.
  - **Qué busca este skill:** Clasificar la salida como aprobable, aprobable con cambios, rechazada o escalar.
  - **Pasos del skill:**
    1. Auditar soporte de hechos, normativo y jurisprudencial.
    2. Detectar riesgos de alucinación, confidencialidad, tono y hacer daño adicional a la víctima con el trato o lenguaje.
    3. Clasificar aprobación y cambios obligatorios para revisión humana.

- `controlar_cadena_custodia_preliminar`
  - **Archivo:** `agente/skills/controlar_cadena_custodia_preliminar/SKILL.md`
  - **Para qué sirve:** alertar si la evidencia puede requerir cadena de custodia.
  - **Qué busca este skill:** Alertar si la evidencia puede requerir cadena de custodia.
  - **Pasos del skill:**
    1. Inventariar y clasificar evidencia disponible por tipo y origen.
    2. Evaluar suficiencia, brechas y alertas de custodia/preservación.
    3. Construir plan de recaudo probatorio con responsables y prioridad.

- `controlar_confidencialidad_datos_sensibles`
  - **Archivo:** `agente/skills/controlar_confidencialidad_datos_sensibles/SKILL.md`
  - **Para qué sirve:** detectar datos sensibles o innecesarios.
  - **Qué busca este skill:** Detectar datos sensibles o innecesarios.
  - **Pasos del skill:**
    1. Auditar soporte de hechos, normativo y jurisprudencial.
    2. Detectar riesgos de alucinación, confidencialidad, tono y hacer daño adicional a la víctima con el trato o lenguaje.
    3. Clasificar aprobación y cambios obligatorios para revisión humana.

- `controlar_no_revictimizacion`
  - **Archivo:** `agente/skills/controlar_no_revictimizacion/SKILL.md`
  - **Para qué sirve:** revisar que la salida no culpe ni exponga indebidamente a la victima.
  - **Qué busca este skill:** Revisar que la salida no culpe ni exponga indebidamente a la victima.
  - **Pasos del skill:**
    1. Auditar soporte de hechos, normativo y jurisprudencial.
    2. Detectar riesgos de alucinación, confidencialidad, tono y hacer daño adicional a la víctima con el trato o lenguaje.
    3. Clasificar aprobación y cambios obligatorios para revisión humana.

- `controlar_separacion_hecho_inferencia`
  - **Archivo:** `agente/skills/controlar_separacion_hecho_inferencia/SKILL.md`
  - **Para qué sirve:** verificar que no se confundan hechos probados, narrados, inferidos y pendientes.
  - **Qué busca este skill:** Verificar que no se confundan hechos probados, narrados, inferidos y pendientes.
  - **Pasos del skill:**
    1. Auditar soporte de hechos, normativo y jurisprudencial.
    2. Detectar riesgos de alucinación, confidencialidad, tono y hacer daño adicional a la víctima con el trato o lenguaje.
    3. Clasificar aprobación y cambios obligatorios para revisión humana.

- `controlar_tono_juridico_documento`
  - **Archivo:** `agente/skills/controlar_tono_juridico_documento/SKILL.md`
  - **Para qué sirve:** asegurar tono formal, preciso, no agresivo y no especulativo.
  - **Qué busca este skill:** Asegurar tono formal, preciso, no agresivo y no especulativo.
  - **Pasos del skill:**
    1. Definir tipo de pieza y datos críticos exigibles.
    2. Redactar estructura hechos-fundamentos-peticiones y anexos.
    3. Aplicar control de tono/fuentes y marcar pendientes de verificación.

- `controlar_tono_riesgo_reputacional`
  - **Archivo:** `agente/skills/controlar_tono_riesgo_reputacional/SKILL.md`
  - **Para qué sirve:** revisar tono profesional y evitar lenguaje riesgoso.
  - **Qué busca este skill:** Revisar tono profesional y evitar lenguaje riesgoso.
  - **Pasos del skill:**
    1. Auditar soporte de hechos, normativo y jurisprudencial.
    2. Detectar riesgos de alucinación, confidencialidad, tono y hacer daño adicional a la víctima con el trato o lenguaje.
    3. Clasificar aprobación y cambios obligatorios para revisión humana.

- `crear_matriz_hecho_fuente`
  - **Archivo:** `agente/skills/crear_matriz_hecho_fuente/SKILL.md`
  - **Para qué sirve:** relacionar cada hecho con su fuente exacta.
  - **Qué busca este skill:** Relacionar cada hecho con su fuente exacta.
  - **Pasos del skill:**
    1. Extraer hechos, actores y fechas con referencia de fuente.
    2. Contrastar inconsistencias y detectar vacíos factuales.
    3. Entregar cronología/matriz y preguntas de aclaración no inductivas.

- `detectar_alucinaciones_legales`
  - **Archivo:** `agente/skills/detectar_alucinaciones_legales/SKILL.md`
  - **Para qué sirve:** detectar fuentes, hechos, conclusiones o citas inventadas.
  - **Qué busca este skill:** Detectar fuentes, hechos, conclusiones o citas inventadas.
  - **Pasos del skill:**
    1. Auditar soporte de hechos, normativo y jurisprudencial.
    2. Detectar riesgos de alucinación, confidencialidad, tono y hacer daño adicional a la víctima con el trato o lenguaje.
    3. Clasificar aprobación y cambios obligatorios para revisión humana.

- `detectar_brechas_probatorias`
  - **Archivo:** `agente/skills/detectar_brechas_probatorias/SKILL.md`
  - **Para qué sirve:** identificar hechos relevantes sin soporte suficiente.
  - **Qué busca este skill:** Identificar hechos relevantes sin soporte suficiente.
  - **Pasos del skill:**
    1. Inventariar y clasificar evidencia disponible por tipo y origen.
    2. Evaluar suficiencia, brechas y alertas de custodia/preservación.
    3. Construir plan de recaudo probatorio con responsables y prioridad.

- `detectar_contradicciones_factuales`
  - **Archivo:** `agente/skills/detectar_contradicciones_factuales/SKILL.md`
  - **Para qué sirve:** encontrar inconsistencias entre versiones, documentos, fechas, valores o actores.
  - **Qué busca este skill:** Encontrar inconsistencias entre versiones, documentos, fechas, valores o actores.
  - **Pasos del skill:**
    1. Extraer hechos, actores y fechas con referencia de fuente.
    2. Contrastar inconsistencias y detectar vacíos factuales.
    3. Entregar cronología/matriz y preguntas de aclaración no inductivas.

- `detectar_riesgo_improcedencia_tutela`
  - **Archivo:** `agente/skills/detectar_riesgo_improcedencia_tutela/SKILL.md`
  - **Para qué sirve:** detectar si tutela puede ser prematura, subsidiaria o improcedente.
  - **Qué busca este skill:** Detectar si tutela puede ser prematura, subsidiaria o improcedente.
  - **Pasos del skill:**
    1. Identificar derecho fundamental afectado y hechos de vulneración.
    2. Evaluar si realmente aplica (si no hay otra vía mejor, si se está actuando a tiempo y perjuicio).
    3. Recomendar tutela o vía alterna y preparar insumos de borrador.

- `detectar_riesgo_revictimizacion`
  - **Archivo:** `agente/skills/detectar_riesgo_revictimizacion/SKILL.md`
  - **Para qué sirve:** identificar lenguaje, preguntas, acciones o estrategias que puedan revictimizar.
  - **Qué busca este skill:** Identificar lenguaje, preguntas, acciones o estrategias que puedan revictimizar.
  - **Pasos del skill:**
    1. Precisar intereses y derechos de la víctima en el caso concreto.
    2. Alinear teoría del caso con plan probatorio y enfoque diferencial.
    3. Mitigar hacer daño adicional a la víctima con el trato o lenguaje y priorizar objetivos de representación.

- `detectar_riesgos_atipicidad`
  - **Archivo:** `agente/skills/detectar_riesgos_atipicidad/SKILL.md`
  - **Para qué sirve:** detectar cuando un caso puede ser atipico o tener naturaleza no penal.
  - **Qué busca este skill:** Detectar cuando un caso puede ser atipico o tener naturaleza no penal.
  - **Pasos del skill:**
    1. Mapear hipótesis típica y descomponer elementos jurídicos.
    2. Vincular hechos y pruebas a cada elemento del tipo penal.
    3. Identificar riesgos de riesgo de que no sea delito y definir preguntas de cierre.

- `detectar_riesgos_audiencia`
  - **Archivo:** `agente/skills/detectar_riesgos_audiencia/SKILL.md`
  - **Para qué sirve:** detectar riesgos de intervencion, oportunidad, revelacion de estrategia o revictimizacion.
  - **Qué busca este skill:** Detectar riesgos de intervencion, oportunidad, revelacion de estrategia o revictimizacion.
  - **Pasos del skill:**
    1. Definir objetivo de audiencia y escenario procesal.
    2. Preparar guion, solicitudes, preguntas y contraargumentos.
    3. Cerrar con checklist y matriz de riesgos de intervención.

- `detectar_riesgos_procesales`
  - **Archivo:** `agente/skills/detectar_riesgos_procesales/SKILL.md`
  - **Para qué sirve:** detectar riesgos de oportunidad, legitimacion, competencia, improcedencia o perdida de derechos.
  - **Qué busca este skill:** Detectar riesgos de oportunidad, legitimacion, competencia, improcedencia o perdida de derechos.
  - **Pasos del skill:**
    1. Determinar etapa procesal y oportunidad de intervención.
    2. Evaluar actuaciones posibles, términos y riesgos procesales.
    3. Proponer ruta recomendada y tareas para ejecución.

- `detectar_urgencia_penal`
  - **Archivo:** `agente/skills/detectar_urgencia_penal/SKILL.md`
  - **Para qué sirve:** identificar si el caso requiere atencion humana inmediata.
  - **Qué busca este skill:** Identificar si el caso requiere atencion humana inmediata.
  - **Pasos del skill:**
    1. Levantar contexto del caso y validar datos faltantes mínimos.
    2. Ejecutar clasificación/priorización según el objetivo del turno.
    3. Registrar pendientes o tareas y escalar cuando aplique.

- `evaluar_oportunidad_procesal`
  - **Archivo:** `agente/skills/evaluar_oportunidad_procesal/SKILL.md`
  - **Para qué sirve:** determinar si una solicitud o intervencion es oportuna, prematura o extemporanea.
  - **Qué busca este skill:** Determinar si una solicitud o intervencion es oportuna, prematura o extemporanea.
  - **Pasos del skill:**
    1. Determinar etapa procesal y oportunidad de intervención.
    2. Evaluar actuaciones posibles, términos y riesgos procesales.
    3. Proponer ruta recomendada y tareas para ejecución.

- `evaluar_procedencia_tutela`
  - **Archivo:** `agente/skills/evaluar_procedencia_tutela/SKILL.md`
  - **Para qué sirve:** evaluar legitimacion, si no hay otra vía mejor, si se está actuando a tiempo y relevancia constitucional.
  - **Qué busca este skill:** Evaluar legitimacion, si no hay otra vía mejor, si se está actuando a tiempo y relevancia constitucional.
  - **Pasos del skill:**
    1. Identificar derecho fundamental afectado y hechos de vulneración.
    2. Evaluar si realmente aplica (si no hay otra vía mejor, si se está actuando a tiempo y perjuicio).
    3. Recomendar tutela o vía alterna y preparar insumos de borrador.

- `mapear_tipo_penal_hecho_prueba`
  - **Archivo:** `agente/skills/mapear_tipo_penal_hecho_prueba/SKILL.md`
  - **Para qué sirve:** relacionar elementos del tipo con hechos y pruebas.
  - **Qué busca este skill:** Relacionar elementos del tipo con hechos y pruebas.
  - **Pasos del skill:**
    1. Mapear hipótesis típica y descomponer elementos jurídicos.
    2. Vincular hechos y pruebas a cada elemento del tipo penal.
    3. Identificar riesgos de riesgo de que no sea delito y definir preguntas de cierre.

- `preparar_resumen_operativo_cliente`
  - **Archivo:** `agente/skills/preparar_resumen_operativo_cliente/SKILL.md`
  - **Para qué sirve:** crear version simple del estado del proceso para cliente, sin estrategia sensible.
  - **Qué busca este skill:** Crear version simple del estado del proceso para cliente, sin estrategia sensible.
  - **Pasos del skill:**
    1. Actualizar actuaciones, número de proceso y estado operativo del caso.
    2. Gestionar términos, alertas y tareas por responsable.
    3. Emitir reporte interno/cliente con alertas accionables.

- `revisar_coherencia_estrategica`
  - **Archivo:** `agente/skills/revisar_coherencia_estrategica/SKILL.md`
  - **Para qué sirve:** asegurar que documento o recomendacion sea coherente con la estrategia aprobada.
  - **Qué busca este skill:** Asegurar que documento o recomendacion sea coherente con la estrategia aprobada.
  - **Pasos del skill:**
    1. Auditar soporte de hechos, normativo y jurisprudencial.
    2. Detectar riesgos de alucinación, confidencialidad, tono y hacer daño adicional a la víctima con el trato o lenguaje.
    3. Clasificar aprobación y cambios obligatorios para revisión humana.

- `verificar_citas_normativas`
  - **Archivo:** `agente/skills/verificar_citas_normativas/SKILL.md`
  - **Para qué sirve:** verificar que normas, articulos y leyes citadas existan en el RAG o esten marcadas pendientes.
  - **Qué busca este skill:** Verificar que normas, articulos y leyes citadas existan en el RAG o esten marcadas pendientes.
  - **Pasos del skill:**
    1. Auditar soporte de hechos, normativo y jurisprudencial.
    2. Detectar riesgos de alucinación, confidencialidad, tono y hacer daño adicional a la víctima con el trato o lenguaje.
    3. Clasificar aprobación y cambios obligatorios para revisión humana.

- `verificar_hechos_soportados`
  - **Archivo:** `agente/skills/verificar_hechos_soportados/SKILL.md`
  - **Para qué sirve:** revisar si cada afirmacion de hechos tiene fuente.
  - **Qué busca este skill:** Revisar si cada afirmacion de hechos tiene fuente.
  - **Pasos del skill:**
    1. Levantar contexto del caso y validar datos faltantes mínimos.
    2. Ejecutar clasificación/priorización según el objetivo del turno.
    3. Registrar pendientes o tareas y escalar cuando aplique.

- `verificar_jurisprudencia`
  - **Archivo:** `agente/skills/verificar_jurisprudencia/SKILL.md`
  - **Para qué sirve:** revisar sentencias, radicados, fechas y organos judiciales.
  - **Qué busca este skill:** Revisar sentencias, radicados, fechas y organos judiciales.
  - **Pasos del skill:**
    1. Auditar soporte de hechos, normativo y jurisprudencial.
    2. Detectar riesgos de alucinación, confidencialidad, tono y hacer daño adicional a la víctima con el trato o lenguaje.
    3. Clasificar aprobación y cambios obligatorios para revisión humana.

## 4) Nota para edición de la abogada

- Si quieres cambiar el comportamiento de un skill, edita su archivo `SKILL.md`.
- Si quieres ajustar cómo habla o decide un agente, se ajusta su prompt correspondiente.
- Se recomienda revisar en este orden: propósito -> pasos -> salida esperada -> riesgos.