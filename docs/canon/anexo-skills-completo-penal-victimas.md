# Anexo de Skills Completo (90) - Penal-Victimas

## 1) Fuentes canonicas de detalle por skill

Cada skill tiene su archivo tecnico editable en:

- `agente/skills/<skill-id>/SKILL.md`

Replica para uso de entorno Cursor:

- `.cursor/skills/<skill-id>/SKILL.md`

Detalle extendido ya consolidado (proposito, inputs, outputs, tools, guardrails, agentes):

- [`reporte-detallado-agentes-prompts-skills-rag.md`](./reporte-detallado-agentes-prompts-skills-rag.md)

Lista canónica con pasos operativos por skill:

- [`lista-aprobacion-agentes-skills-pasos.md`](./lista-aprobacion-agentes-skills-pasos.md)

## 2) Mapeo completo agente -> skills (con archivo por skill)

### `coordinador_expediente_penal` (11)

- `actualizar_tareas_responsable` -> `agente/skills/actualizar_tareas_responsable/SKILL.md`
- `clasificar_fuente_factual` -> `agente/skills/clasificar_fuente_factual/SKILL.md`
- `clasificar_tarea_y_etapa` -> `agente/skills/clasificar_tarea_y_etapa/SKILL.md`
- `crear_ruta_procesal_recomendada` -> `agente/skills/crear_ruta_procesal_recomendada/SKILL.md`
- `detectar_urgencia_penal` -> `agente/skills/detectar_urgencia_penal/SKILL.md`
- `detectar_vacios_factuales` -> `agente/skills/detectar_vacios_factuales/SKILL.md`
- `gestionar_faltantes_expediente` -> `agente/skills/gestionar_faltantes_expediente/SKILL.md`
- `identificar_etapa_procesal_ley906` -> `agente/skills/identificar_etapa_procesal_ley906/SKILL.md`
- `marcar_pendientes_verificacion` -> `agente/skills/marcar_pendientes_verificacion/SKILL.md`
- `priorizar_objetivos_representacion` -> `agente/skills/priorizar_objetivos_representacion/SKILL.md`
- `recomendar_via_constitucional_o_alternativa` -> `agente/skills/recomendar_via_constitucional_o_alternativa/SKILL.md`

### `analista_cronologia_hechos_penales` (9)

- `construir_cronologia_penal` -> `agente/skills/construir_cronologia_penal/SKILL.md`
- `crear_matriz_hecho_fuente` -> `agente/skills/crear_matriz_hecho_fuente/SKILL.md`
- `detectar_contradicciones_factuales` -> `agente/skills/detectar_contradicciones_factuales/SKILL.md`
- `detectar_vacios_factuales` -> `agente/skills/detectar_vacios_factuales/SKILL.md`
- `extraer_hechos_relevantes` -> `agente/skills/extraer_hechos_relevantes/SKILL.md`
- `generar_preguntas_aclaracion` -> `agente/skills/generar_preguntas_aclaracion/SKILL.md`
- `generar_preguntas_tipicidad` -> `agente/skills/generar_preguntas_tipicidad/SKILL.md`
- `identificar_actores_y_roles` -> `agente/skills/identificar_actores_y_roles/SKILL.md`
- `verificar_hechos_soportados` -> `agente/skills/verificar_hechos_soportados/SKILL.md`

### `analista_tipicidad_y_responsabilidad_penal` (9)

- `analizar_autoria_y_participacion` -> `agente/skills/analizar_autoria_y_participacion/SKILL.md`
- `analizar_dolo_culpa_elemento_subjetivo` -> `agente/skills/analizar_dolo_culpa_elemento_subjetivo/SKILL.md`
- `construir_matriz_hecho_prueba` -> `agente/skills/construir_matriz_hecho_prueba/SKILL.md`
- `descomponer_elementos_tipo_penal` -> `agente/skills/descomponer_elementos_tipo_penal/SKILL.md`
- `detectar_agravantes_atenuantes` -> `agente/skills/detectar_agravantes_atenuantes/SKILL.md`
- `detectar_riesgos_atipicidad` -> `agente/skills/detectar_riesgos_atipicidad/SKILL.md`
- `generar_preguntas_tipicidad` -> `agente/skills/generar_preguntas_tipicidad/SKILL.md`
- `identificar_conductas_punibles_preliminares` -> `agente/skills/identificar_conductas_punibles_preliminares/SKILL.md`
- `mapear_tipo_penal_hecho_prueba` -> `agente/skills/mapear_tipo_penal_hecho_prueba/SKILL.md`

### `analista_ruta_procesal_ley906` (13)

- `analizar_intervencion_victima` -> `agente/skills/analizar_intervencion_victima/SKILL.md`
- `clasificar_tarea_y_etapa` -> `agente/skills/clasificar_tarea_y_etapa/SKILL.md`
- `controlar_terminos_procesales_preliminares` -> `agente/skills/controlar_terminos_procesales_preliminares/SKILL.md`
- `crear_ruta_procesal_recomendada` -> `agente/skills/crear_ruta_procesal_recomendada/SKILL.md`
- `detectar_inactividad_procesal` -> `agente/skills/detectar_inactividad_procesal/SKILL.md`
- `detectar_riesgos_procesales` -> `agente/skills/detectar_riesgos_procesales/SKILL.md`
- `evaluar_oportunidad_procesal` -> `agente/skills/evaluar_oportunidad_procesal/SKILL.md`
- `evaluar_solicitud_fiscalia_juez` -> `agente/skills/evaluar_solicitud_fiscalia_juez/SKILL.md`
- `generar_alertas_terminos_vencimientos` -> `agente/skills/generar_alertas_terminos_vencimientos/SKILL.md`
- `identificar_etapa_procesal_ley906` -> `agente/skills/identificar_etapa_procesal_ley906/SKILL.md`
- `mapear_actuaciones_posibles_victima` -> `agente/skills/mapear_actuaciones_posibles_victima/SKILL.md`
- `preparar_solicitudes_orales` -> `agente/skills/preparar_solicitudes_orales/SKILL.md`
- `redactar_recurso_o_intervencion_preliminar` -> `agente/skills/redactar_recurso_o_intervencion_preliminar/SKILL.md`

### `analista_representacion_victimas` (13)

- `alinear_estrategia_prueba_proceso` -> `agente/skills/alinear_estrategia_prueba_proceso/SKILL.md`
- `analizar_derechos_victima` -> `agente/skills/analizar_derechos_victima/SKILL.md`
- `analizar_enfoque_diferencial` -> `agente/skills/analizar_enfoque_diferencial/SKILL.md`
- `construir_teoria_caso_victima` -> `agente/skills/construir_teoria_caso_victima/SKILL.md`
- `controlar_no_revictimizacion` -> `agente/skills/controlar_no_revictimizacion/SKILL.md`
- `crear_plan_recaudo_probatorio` -> `agente/skills/crear_plan_recaudo_probatorio/SKILL.md`
- `detectar_riesgo_revictimizacion` -> `agente/skills/detectar_riesgo_revictimizacion/SKILL.md`
- `evaluar_dano_y_afectacion` -> `agente/skills/evaluar_dano_y_afectacion/SKILL.md`
- `evaluar_suficiencia_probatoria` -> `agente/skills/evaluar_suficiencia_probatoria/SKILL.md`
- `identificar_actores_y_roles` -> `agente/skills/identificar_actores_y_roles/SKILL.md`
- `identificar_intereses_victima` -> `agente/skills/identificar_intereses_victima/SKILL.md`
- `mapear_actuaciones_posibles_victima` -> `agente/skills/mapear_actuaciones_posibles_victima/SKILL.md`
- `priorizar_objetivos_representacion` -> `agente/skills/priorizar_objetivos_representacion/SKILL.md`

### `gestor_evidencia_y_soporte_probatorio` (13)

- `clasificar_tipo_prueba` -> `agente/skills/clasificar_tipo_prueba/SKILL.md`
- `construir_matriz_hecho_prueba` -> `agente/skills/construir_matriz_hecho_prueba/SKILL.md`
- `controlar_cadena_custodia_preliminar` -> `agente/skills/controlar_cadena_custodia_preliminar/SKILL.md`
- `crear_plan_recaudo_probatorio` -> `agente/skills/crear_plan_recaudo_probatorio/SKILL.md`
- `detectar_brechas_probatorias` -> `agente/skills/detectar_brechas_probatorias/SKILL.md`
- `evaluar_dano_y_afectacion` -> `agente/skills/evaluar_dano_y_afectacion/SKILL.md`
- `evaluar_suficiencia_probatoria` -> `agente/skills/evaluar_suficiencia_probatoria/SKILL.md`
- `extraer_hechos_relevantes` -> `agente/skills/extraer_hechos_relevantes/SKILL.md`
- `generar_preguntas_aclaracion` -> `agente/skills/generar_preguntas_aclaracion/SKILL.md`
- `generar_preguntas_testigos_peritos` -> `agente/skills/generar_preguntas_testigos_peritos/SKILL.md`
- `inventariar_evidencia` -> `agente/skills/inventariar_evidencia/SKILL.md`
- `mapear_tipo_penal_hecho_prueba` -> `agente/skills/mapear_tipo_penal_hecho_prueba/SKILL.md`
- `preservar_evidencia_digital` -> `agente/skills/preservar_evidencia_digital/SKILL.md`

### `preparador_estrategico_audiencias_penales` (16)

- `analizar_intervencion_victima` -> `agente/skills/analizar_intervencion_victima/SKILL.md`
- `construir_cronologia_penal` -> `agente/skills/construir_cronologia_penal/SKILL.md`
- `construir_matriz_hecho_prueba` -> `agente/skills/construir_matriz_hecho_prueba/SKILL.md`
- `construir_teoria_caso_victima` -> `agente/skills/construir_teoria_caso_victima/SKILL.md`
- `controlar_audiencias` -> `agente/skills/controlar_audiencias/SKILL.md`
- `crear_checklist_previo_audiencia` -> `agente/skills/crear_checklist_previo_audiencia/SKILL.md`
- `crear_resumen_ejecutivo_litigante` -> `agente/skills/crear_resumen_ejecutivo_litigante/SKILL.md`
- `detectar_riesgo_revictimizacion` -> `agente/skills/detectar_riesgo_revictimizacion/SKILL.md`
- `detectar_riesgos_audiencia` -> `agente/skills/detectar_riesgos_audiencia/SKILL.md`
- `generar_preguntas_testigos_peritos` -> `agente/skills/generar_preguntas_testigos_peritos/SKILL.md`
- `identificar_objetivo_audiencia` -> `agente/skills/identificar_objetivo_audiencia/SKILL.md`
- `preparar_contraargumentos` -> `agente/skills/preparar_contraargumentos/SKILL.md`
- `preparar_guion_intervencion_oral` -> `agente/skills/preparar_guion_intervencion_oral/SKILL.md`
- `preparar_preguntas_audiencia` -> `agente/skills/preparar_preguntas_audiencia/SKILL.md`
- `preparar_solicitudes_orales` -> `agente/skills/preparar_solicitudes_orales/SKILL.md`
- `simular_escenarios_audiencia` -> `agente/skills/simular_escenarios_audiencia/SKILL.md`

### `redactor_documentos_juridicos_penales` (16)

- `controlar_separacion_hecho_inferencia` -> `agente/skills/controlar_separacion_hecho_inferencia/SKILL.md`
- `controlar_tono_juridico_documento` -> `agente/skills/controlar_tono_juridico_documento/SKILL.md`
- `controlar_tono_riesgo_reputacional` -> `agente/skills/controlar_tono_riesgo_reputacional/SKILL.md`
- `estructurar_hechos_fundamentos_solicitudes` -> `agente/skills/estructurar_hechos_fundamentos_solicitudes/SKILL.md`
- `evaluar_derecho_peticion` -> `agente/skills/evaluar_derecho_peticion/SKILL.md`
- `evaluar_solicitud_fiscalia_juez` -> `agente/skills/evaluar_solicitud_fiscalia_juez/SKILL.md`
- `extraer_hechos_relevantes` -> `agente/skills/extraer_hechos_relevantes/SKILL.md`
- `preparar_borrador_tutela_preliminar` -> `agente/skills/preparar_borrador_tutela_preliminar/SKILL.md`
- `redactar_ampliacion_denuncia` -> `agente/skills/redactar_ampliacion_denuncia/SKILL.md`
- `redactar_derecho_peticion_penal` -> `agente/skills/redactar_derecho_peticion_penal/SKILL.md`
- `redactar_memorial_penal` -> `agente/skills/redactar_memorial_penal/SKILL.md`
- `redactar_recurso_o_intervencion_preliminar` -> `agente/skills/redactar_recurso_o_intervencion_preliminar/SKILL.md`
- `redactar_solicitud_impulso_procesal` -> `agente/skills/redactar_solicitud_impulso_procesal/SKILL.md`
- `redactar_tutela_penal_preliminar` -> `agente/skills/redactar_tutela_penal_preliminar/SKILL.md`
- `verificar_citas_normativas` -> `agente/skills/verificar_citas_normativas/SKILL.md`
- `verificar_hechos_soportados` -> `agente/skills/verificar_hechos_soportados/SKILL.md`

### `gestor_seguimiento_procesal_penal` (12)

- `actualizar_tareas_responsable` -> `agente/skills/actualizar_tareas_responsable/SKILL.md`
- `controlar_audiencias` -> `agente/skills/controlar_audiencias/SKILL.md`
- `controlar_terminos_procesales_preliminares` -> `agente/skills/controlar_terminos_procesales_preliminares/SKILL.md`
- `crear_checklist_previo_audiencia` -> `agente/skills/crear_checklist_previo_audiencia/SKILL.md`
- `crear_reporte_estado_caso` -> `agente/skills/crear_reporte_estado_caso/SKILL.md`
- `detectar_inactividad_procesal` -> `agente/skills/detectar_inactividad_procesal/SKILL.md`
- `detectar_urgencia_penal` -> `agente/skills/detectar_urgencia_penal/SKILL.md`
- `generar_alertas_terminos_vencimientos` -> `agente/skills/generar_alertas_terminos_vencimientos/SKILL.md`
- `monitorear_radicado` -> `agente/skills/monitorear_radicado/SKILL.md`
- `preparar_resumen_operativo_cliente` -> `agente/skills/preparar_resumen_operativo_cliente/SKILL.md`
- `registrar_actuacion_procesal` -> `agente/skills/registrar_actuacion_procesal/SKILL.md`
- `seguimiento_documentos_radicados` -> `agente/skills/seguimiento_documentos_radicados/SKILL.md`

### `evaluador_derechos_fundamentales_tutela` (13)

- `analizar_derechos_victima` -> `agente/skills/analizar_derechos_victima/SKILL.md`
- `analizar_enfoque_diferencial` -> `agente/skills/analizar_enfoque_diferencial/SKILL.md`
- `analizar_perjuicio_irremediable` -> `agente/skills/analizar_perjuicio_irremediable/SKILL.md`
- `crear_matriz_hecho_derecho_fundamental` -> `agente/skills/crear_matriz_hecho_derecho_fundamental/SKILL.md`
- `detectar_riesgo_improcedencia_tutela` -> `agente/skills/detectar_riesgo_improcedencia_tutela/SKILL.md`
- `evaluar_derecho_peticion` -> `agente/skills/evaluar_derecho_peticion/SKILL.md`
- `evaluar_procedencia_tutela` -> `agente/skills/evaluar_procedencia_tutela/SKILL.md`
- `identificar_derecho_fundamental_afectado` -> `agente/skills/identificar_derecho_fundamental_afectado/SKILL.md`
- `preparar_borrador_tutela_preliminar` -> `agente/skills/preparar_borrador_tutela_preliminar/SKILL.md`
- `recomendar_via_constitucional_o_alternativa` -> `agente/skills/recomendar_via_constitucional_o_alternativa/SKILL.md`
- `redactar_derecho_peticion_penal` -> `agente/skills/redactar_derecho_peticion_penal/SKILL.md`
- `redactar_tutela_penal_preliminar` -> `agente/skills/redactar_tutela_penal_preliminar/SKILL.md`
- `revisar_mecanismos_ordinarios` -> `agente/skills/revisar_mecanismos_ordinarios/SKILL.md`

### `analista_calidad_juridica` (26)

- `alinear_estrategia_prueba_proceso` -> `agente/skills/alinear_estrategia_prueba_proceso/SKILL.md`
- `clasificar_aprobacion_juridica` -> `agente/skills/clasificar_aprobacion_juridica/SKILL.md`
- `controlar_cadena_custodia_preliminar` -> `agente/skills/controlar_cadena_custodia_preliminar/SKILL.md`
- `controlar_confidencialidad_datos_sensibles` -> `agente/skills/controlar_confidencialidad_datos_sensibles/SKILL.md`
- `controlar_no_revictimizacion` -> `agente/skills/controlar_no_revictimizacion/SKILL.md`
- `controlar_separacion_hecho_inferencia` -> `agente/skills/controlar_separacion_hecho_inferencia/SKILL.md`
- `controlar_tono_juridico_documento` -> `agente/skills/controlar_tono_juridico_documento/SKILL.md`
- `controlar_tono_riesgo_reputacional` -> `agente/skills/controlar_tono_riesgo_reputacional/SKILL.md`
- `crear_matriz_hecho_fuente` -> `agente/skills/crear_matriz_hecho_fuente/SKILL.md`
- `detectar_alucinaciones_legales` -> `agente/skills/detectar_alucinaciones_legales/SKILL.md`
- `detectar_brechas_probatorias` -> `agente/skills/detectar_brechas_probatorias/SKILL.md`
- `detectar_contradicciones_factuales` -> `agente/skills/detectar_contradicciones_factuales/SKILL.md`
- `detectar_riesgo_improcedencia_tutela` -> `agente/skills/detectar_riesgo_improcedencia_tutela/SKILL.md`
- `detectar_riesgo_revictimizacion` -> `agente/skills/detectar_riesgo_revictimizacion/SKILL.md`
- `detectar_riesgos_atipicidad` -> `agente/skills/detectar_riesgos_atipicidad/SKILL.md`
- `detectar_riesgos_audiencia` -> `agente/skills/detectar_riesgos_audiencia/SKILL.md`
- `detectar_riesgos_procesales` -> `agente/skills/detectar_riesgos_procesales/SKILL.md`
- `detectar_urgencia_penal` -> `agente/skills/detectar_urgencia_penal/SKILL.md`
- `evaluar_oportunidad_procesal` -> `agente/skills/evaluar_oportunidad_procesal/SKILL.md`
- `evaluar_procedencia_tutela` -> `agente/skills/evaluar_procedencia_tutela/SKILL.md`
- `mapear_tipo_penal_hecho_prueba` -> `agente/skills/mapear_tipo_penal_hecho_prueba/SKILL.md`
- `preparar_resumen_operativo_cliente` -> `agente/skills/preparar_resumen_operativo_cliente/SKILL.md`
- `revisar_coherencia_estrategica` -> `agente/skills/revisar_coherencia_estrategica/SKILL.md`
- `verificar_citas_normativas` -> `agente/skills/verificar_citas_normativas/SKILL.md`
- `verificar_hechos_soportados` -> `agente/skills/verificar_hechos_soportados/SKILL.md`
- `verificar_jurisprudencia` -> `agente/skills/verificar_jurisprudencia/SKILL.md`

## 3) Nota para revision juridica

Para modificar cualquier skill sin tocar codigo Python, la abogada puede editar directamente el archivo `SKILL.md` correspondiente.

Orden recomendado de revision:

1. Proposito.
2. Inputs y outputs.
3. Tools permitidas.
4. Guardrails.
5. Agentes que lo usan.

