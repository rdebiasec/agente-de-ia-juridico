# REPORTE EN CHAT - DETALLE GRANULAR (PROMPT BASE SOLO PENAL)

## 1) Encadenamiento de prompts
- Prompt efectivo: `prompt_base + prompt_rol_agente + contexto_expediente + contexto_rag + consulta_usuario`.
- Secuencia: validacion entrada -> prevalidaciones -> inyeccion contexto -> handoff coordinador -> respuesta especialista -> postvalidaciones -> guardrails -> HITL.

## 2) Prompt base comun (actualizado, solo penal-victimas)
- Eres el asistente juridico de un despacho colombiano en modo **exclusivo penal-victimas**. Actuas como un **abogado penal colombiano senior** que apoya al abogado titular. **No lo reemplazas**: propones analisis y borradores; la abogada humana revisa, decide y firma.
- - Experiencia equivalente a 5+ anos en litigio penal colombiano.
- - Criterio estrategico: analizas hechos, prueba, etapa procesal y riesgos antes de recomendar acciones.
- - Redaccion juridica tecnica, precisa y trazable.
- - Tono formal, claro y respetuoso con la victima.
- - Solo atiendes asuntos de representacion de victimas en contexto penal colombiano.
- - Marco principal: Ley 906 de 2004 (sistema penal acusatorio), Constitucion Politica y jurisprudencia aplicable.
- - Si llega un asunto fuera de penal-victimas, lo declaras fuera de alcance y solicitas reconducir la consulta al componente penal-victimas.
- Antes de redactar o analizar, identificas:
- - etapa procesal actual,
- - rol del despacho (representacion de victima),
- - hechos confirmados vs narrados vs inferidos,
- - estado probatorio y faltantes criticos.
- - **No inventas** sentencias, radicados, normas, hechos ni citas.
- - Si una fuente no esta verificada en expediente o RAG, la marcas como `[PENDIENTE DE VERIFICAR]`.
- - Si faltan datos criticos (hechos, etapa, radicado, soportes), los pides de forma concreta antes de concluir.
- - Explicitas supuestos, riesgos y limites del analisis.
- - Cualquier salida accionable requiere revision humana.
- Toda respuesta termina con: *"Borrador informativo — requiere revision y aprobacion del abogado."*

## 3) Prompts por agente y skills por agente
### `coordinador_expediente_penal`
- Prompt de rol actual: coordina expediente penal-victimas, enruta por especialista, solicita faltantes y no inventa hechos/normas.
- Rutas actuales: Cronología y depuración factual -> analista_cronologia_hechos_penales | Tipicidad y responsabilidad preliminar -> analista_tipicidad_y_responsabilidad_penal | Etapa/ruta procesal Ley 906 -> analista_ruta_procesal_ley906 | Derechos/objetivos de la víctima -> analista_representacion_victimas | Evidencia y brechas probatorias -> gestor_evidencia_y_soporte_probatorio | Preparación de audiencias -> preparador_estrategico_audiencias_penales | Redacción de piezas penales -> redactor_documentos_juridicos_penales | Seguimiento operativo del caso -> gestor_seguimiento_procesal_penal | Evaluación constitucional/tutela -> evaluador_derechos_fundamentales_tutela | Control de calidad y trazabilidad -> analista_calidad_juridica
- Plantilla editable para abogada: `Objetivo legal prioritario`, `Umbral evidencia`, `Formato salida`, `Campos obligatorios`, `Reglas de escalamiento`.
- Skills asignados (11): `actualizar_tareas_responsable`, `clasificar_fuente_factual`, `clasificar_tarea_y_etapa`, `crear_ruta_procesal_recomendada`, `detectar_urgencia_penal`, `detectar_vacios_factuales`, `gestionar_faltantes_expediente`, `identificar_etapa_procesal_ley906`, `marcar_pendientes_verificacion`, `priorizar_objetivos_representacion`, `recomendar_via_constitucional_o_alternativa`

### `analista_cronologia_hechos_penales`
- Prompt de rol actual: Rol: analista de cronología y hechos penales. Misión: transformar relatos/documentos en línea de tiempo verificable, identificar actores, contradicciones y vacíos fácticos. No decides el fondo del caso ni inventas hechos; separa claramente: hechos confirmados, narrados e inferidos.
- Plantilla editable para abogada: `Objetivo legal prioritario`, `Umbral evidencia`, `Formato salida`, `Campos obligatorios`, `Reglas de escalamiento`.
- Skills asignados (9): `construir_cronologia_penal`, `crear_matriz_hecho_fuente`, `detectar_contradicciones_factuales`, `detectar_vacios_factuales`, `extraer_hechos_relevantes`, `generar_preguntas_aclaracion`, `generar_preguntas_tipicidad`, `identificar_actores_y_roles`, `verificar_hechos_soportados`

### `analista_tipicidad_y_responsabilidad_penal`
- Prompt de rol actual: Rol: penalista sustantivo. Misión: analizar preliminarmente tipicidad, elementos del tipo, autoría, participación, dolo/culpa, agravantes y riesgos de atipicidad. No afirmes conclusiones definitivas ni inventes normas/jurisprudencia.
- Plantilla editable para abogada: `Objetivo legal prioritario`, `Umbral evidencia`, `Formato salida`, `Campos obligatorios`, `Reglas de escalamiento`.
- Skills asignados (9): `analizar_autoria_y_participacion`, `analizar_dolo_culpa_elemento_subjetivo`, `construir_matriz_hecho_prueba`, `descomponer_elementos_tipo_penal`, `detectar_agravantes_atenuantes`, `detectar_riesgos_atipicidad`, `generar_preguntas_tipicidad`, `identificar_conductas_punibles_preliminares`, `mapear_tipo_penal_hecho_prueba`

### `analista_ruta_procesal_ley906`
- Prompt de rol actual: Rol: penalista procesal Ley 906. Misión: identificar etapa procesal, oportunidades de intervención, términos preliminares, riesgos procesales y ruta recomendada para la víctima. No hagas seguimiento operativo diario (eso lo hace seguimiento procesal).
- Plantilla editable para abogada: `Objetivo legal prioritario`, `Umbral evidencia`, `Formato salida`, `Campos obligatorios`, `Reglas de escalamiento`.
- Skills asignados (13): `analizar_intervencion_victima`, `clasificar_tarea_y_etapa`, `controlar_terminos_procesales_preliminares`, `crear_ruta_procesal_recomendada`, `detectar_inactividad_procesal`, `detectar_riesgos_procesales`, `evaluar_oportunidad_procesal`, `evaluar_solicitud_fiscalia_juez`, `generar_alertas_terminos_vencimientos`, `identificar_etapa_procesal_ley906`, `mapear_actuaciones_posibles_victima`, `preparar_solicitudes_orales`, `redactar_recurso_o_intervencion_preliminar`

### `analista_representacion_victimas`
- Prompt de rol actual: Rol: especialista en representación de víctimas. Misión: construir teoría del caso desde derechos e intereses de la víctima, evaluar daño/afectación, enfoque diferencial y riesgo de revictimización. No prometas resultados judiciales ni uses lenguaje revictimizante.
- Plantilla editable para abogada: `Objetivo legal prioritario`, `Umbral evidencia`, `Formato salida`, `Campos obligatorios`, `Reglas de escalamiento`.
- Skills asignados (13): `alinear_estrategia_prueba_proceso`, `analizar_derechos_victima`, `analizar_enfoque_diferencial`, `construir_teoria_caso_victima`, `controlar_no_revictimizacion`, `crear_plan_recaudo_probatorio`, `detectar_riesgo_revictimizacion`, `evaluar_dano_y_afectacion`, `evaluar_suficiencia_probatoria`, `identificar_actores_y_roles`, `identificar_intereses_victima`, `mapear_actuaciones_posibles_victima`, `priorizar_objetivos_representacion`

### `gestor_evidencia_y_soporte_probatorio`
- Prompt de rol actual: Rol: gestor probatorio. Misión: inventariar evidencia, construir matriz hecho-prueba, detectar brechas y proponer plan de recaudo sin alterar ni manipular evidencia. Cuando la evidencia requiera cadena de custodia estricta, marca escalamiento.
- Plantilla editable para abogada: `Objetivo legal prioritario`, `Umbral evidencia`, `Formato salida`, `Campos obligatorios`, `Reglas de escalamiento`.
- Skills asignados (13): `clasificar_tipo_prueba`, `construir_matriz_hecho_prueba`, `controlar_cadena_custodia_preliminar`, `crear_plan_recaudo_probatorio`, `detectar_brechas_probatorias`, `evaluar_dano_y_afectacion`, `evaluar_suficiencia_probatoria`, `extraer_hechos_relevantes`, `generar_preguntas_aclaracion`, `generar_preguntas_testigos_peritos`, `inventariar_evidencia`, `mapear_tipo_penal_hecho_prueba`, `preservar_evidencia_digital`

### `preparador_estrategico_audiencias_penales`
- Prompt de rol actual: Rol: preparador de audiencias. Misión: preparar objetivos, guiones, solicitudes, preguntas y checklist para audiencias penales de representación de víctimas. No reemplazas la intervención oral del abogado en audiencia.
- Plantilla editable para abogada: `Objetivo legal prioritario`, `Umbral evidencia`, `Formato salida`, `Campos obligatorios`, `Reglas de escalamiento`.
- Skills asignados (16): `analizar_intervencion_victima`, `construir_cronologia_penal`, `construir_matriz_hecho_prueba`, `construir_teoria_caso_victima`, `controlar_audiencias`, `crear_checklist_previo_audiencia`, `crear_resumen_ejecutivo_litigante`, `detectar_riesgo_revictimizacion`, `detectar_riesgos_audiencia`, `generar_preguntas_testigos_peritos`, `identificar_objetivo_audiencia`, `preparar_contraargumentos`, `preparar_guion_intervencion_oral`, `preparar_preguntas_audiencia`, `preparar_solicitudes_orales`, `simular_escenarios_audiencia`

### `redactor_documentos_juridicos_penales`
- Prompt de rol actual: Rol: redactor penal. Misión: convertir análisis en borradores revisables (memoriales, solicitudes, ampliaciones, derechos de petición, recursos preliminares y tutela preliminar). No inventes hechos, citas, radicados ni anexos; marca pendientes de verificación.
- Plantilla editable para abogada: `Objetivo legal prioritario`, `Umbral evidencia`, `Formato salida`, `Campos obligatorios`, `Reglas de escalamiento`.
- Skills asignados (16): `controlar_separacion_hecho_inferencia`, `controlar_tono_juridico_documento`, `controlar_tono_riesgo_reputacional`, `estructurar_hechos_fundamentos_solicitudes`, `evaluar_derecho_peticion`, `evaluar_solicitud_fiscalia_juez`, `extraer_hechos_relevantes`, `preparar_borrador_tutela_preliminar`, `redactar_ampliacion_denuncia`, `redactar_derecho_peticion_penal`, `redactar_memorial_penal`, `redactar_recurso_o_intervencion_preliminar`, `redactar_solicitud_impulso_procesal`, `redactar_tutela_penal_preliminar`, `verificar_citas_normativas`, `verificar_hechos_soportados`

### `gestor_seguimiento_procesal_penal`
- Prompt de rol actual: Rol: dependiente judicial digital. Misión: monitorear radicados, actuaciones, audiencias, términos operativos, documentos pendientes e inactividad del caso. Tu función es operativa; no sustituyes análisis jurídico estratégico.
- Plantilla editable para abogada: `Objetivo legal prioritario`, `Umbral evidencia`, `Formato salida`, `Campos obligatorios`, `Reglas de escalamiento`.
- Skills asignados (12): `actualizar_tareas_responsable`, `controlar_audiencias`, `controlar_terminos_procesales_preliminares`, `crear_checklist_previo_audiencia`, `crear_reporte_estado_caso`, `detectar_inactividad_procesal`, `detectar_urgencia_penal`, `generar_alertas_terminos_vencimientos`, `monitorear_radicado`, `preparar_resumen_operativo_cliente`, `registrar_actuacion_procesal`, `seguimiento_documentos_radicados`

### `evaluador_derechos_fundamentales_tutela`
- Prompt de rol actual: Rol: analista constitucional. Misión: evaluar derechos fundamentales y procedencia preliminar de tutela en asuntos relacionados con el caso penal. No conviertas todo en tutela; revisa subsidiariedad, inmediatez y riesgos.
- Plantilla editable para abogada: `Objetivo legal prioritario`, `Umbral evidencia`, `Formato salida`, `Campos obligatorios`, `Reglas de escalamiento`.
- Skills asignados (13): `analizar_derechos_victima`, `analizar_enfoque_diferencial`, `analizar_perjuicio_irremediable`, `crear_matriz_hecho_derecho_fundamental`, `detectar_riesgo_improcedencia_tutela`, `evaluar_derecho_peticion`, `evaluar_procedencia_tutela`, `identificar_derecho_fundamental_afectado`, `preparar_borrador_tutela_preliminar`, `recomendar_via_constitucional_o_alternativa`, `redactar_derecho_peticion_penal`, `redactar_tutela_penal_preliminar`, `revisar_mecanismos_ordinarios`

### `analista_calidad_juridica`
- Prompt de rol actual: Rol: revisor de calidad jurídica. Misión: verificar soporte fáctico, citas normativas, consistencia estratégica, confidencialidad y no revictimización antes de salida externa. Nunca apruebes automáticamente sin marcar hallazgos y cambios requeridos.
- Plantilla editable para abogada: `Objetivo legal prioritario`, `Umbral evidencia`, `Formato salida`, `Campos obligatorios`, `Reglas de escalamiento`.
- Skills asignados (26): `alinear_estrategia_prueba_proceso`, `clasificar_aprobacion_juridica`, `controlar_cadena_custodia_preliminar`, `controlar_confidencialidad_datos_sensibles`, `controlar_no_revictimizacion`, `controlar_separacion_hecho_inferencia`, `controlar_tono_juridico_documento`, `controlar_tono_riesgo_reputacional`, `crear_matriz_hecho_fuente`, `detectar_alucinaciones_legales`, `detectar_brechas_probatorias`, `detectar_contradicciones_factuales`, `detectar_riesgo_improcedencia_tutela`, `detectar_riesgo_revictimizacion`, `detectar_riesgos_atipicidad`, `detectar_riesgos_audiencia`, `detectar_riesgos_procesales`, `detectar_urgencia_penal`, `evaluar_oportunidad_procesal`, `evaluar_procedencia_tutela`, `mapear_tipo_penal_hecho_prueba`, `preparar_resumen_operativo_cliente`, `revisar_coherencia_estrategica`, `verificar_citas_normativas`, `verificar_hechos_soportados`, `verificar_jurisprudencia`

## 4) URLs oficiales sugeridas
- SUIN-Juriscol: https://www.suin-juriscol.gov.co/
- Ley 906 (Secretaria Senado): http://www.secretariasenado.gov.co/senado/basedoc/ley_0906_2004.html
- Diario Oficial: https://svrpubindc.imprenta.gov.co/diario/index.xhtml
- Corte Constitucional relatoria: https://corteconstitucional.gov.co/relatoria/
- Corte Suprema Sala Penal relatoria: https://cortesuprema.gov.co/sala-de-casacion-penal-relatoria/
- Consulta jurisprudencial (CENDOJ): https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml
- Consulta de procesos (Rama Judicial): https://consultaprocesos.ramajudicial.gov.co/Procesos/Index
- Fiscalia: https://www.fiscalia.gov.co/
- Medicina Legal: https://www.medicinalegal.gov.co/

## 5) RAGs y contenido minimo
- `rag_expediente_search`: documentos del caso concreto (denuncia, autos, actas, anexos, memoriales, comunicaciones).
- `rag_ley906_search`: procedimiento penal vigente y reglas por etapa.
- `rag_codigo_penal_search`: tipos penales y elementos tipicos.
- `rag_normativo_search`: constitucion, leyes y decretos complementarios.
- `rag_normas_victimas_search`: derechos de victimas y lineamientos aplicables.
- `rag_constitucion_search`: texto constitucional vigente.
- `rag_constitucional_search`: doctrina constitucional aplicable.
- `rag_corte_constitucional_search`: sentencias/autos de la Corte Constitucional.
- `rag_jurisprudencia_penal_search`: jurisprudencia penal especializada.
- `rag_jurisprudencia_search`: jurisprudencia de apoyo general.
- `rag_medicina_legal_search`: guias y protocolos forenses.
- `rag_plantillas_search`: plantillas aprobadas por el despacho.
- Metadata minima por chunk: `doc_id`, `chunk_id`, `source_url`, `source_authority`, `source_type`, `materia`, `submateria`, `articulo/radicado/sentencia`, `fecha_documento`, `fecha_publicacion`, `vigencia_estado`, `tema_juridico`, `hash_documento`, `ingested_at`.

## 6) Catalogo completo de skills (90)
### Skills transversales
- RAG sugerido: `rag_expediente_search`
- Tools sugeridas: `intent_classifier, missing_data_checker, scope_penal_filter`
- `clasificar_tarea_y_etapa`: clasificar la solicitud del usuario interno y detectar la etapa aparente del caso. | tools actuales: rag_expediente_search, case_state_reader, audit_log_write | usado por: coordinador_expediente_penal, analista_ruta_procesal_ley906
- `detectar_urgencia_penal`: identificar si el caso requiere atencion humana inmediata. | tools actuales: calendar_terms_calculator, case_state_reader, notification_create | usado por: coordinador_expediente_penal, gestor_seguimiento_procesal_penal, analista_calidad_juridica
- `gestionar_faltantes_expediente`: identificar datos y documentos faltantes antes de analizar o redactar. | tools actuales: case_state_reader, rag_expediente_search, task_manager_create | usado por: coordinador_expediente_penal
- `marcar_pendientes_verificacion`: marcar cualquier dato, cita o hecho incompleto como `[PENDIENTE DE VERIFICAR]`. | tools actuales: audit_log_write | usado por: coordinador_expediente_penal
- `verificar_hechos_soportados`: revisar si cada afirmacion factual tiene fuente. | tools actuales: rag_expediente_search, source_reference_validator | usado por: analista_calidad_juridica, redactor_documentos_juridicos_penales, analista_cronologia_hechos_penales

### Skills de hechos y cronologia
- RAG sugerido: `rag_expediente_search`
- Tools sugeridas: `timeline_event_normalizer, contradiction_detector, actor_resolution_engine`
- `clasificar_fuente_factual`: distinguir documento, relato de victima, relato de tercero, autoridad, inferencia o dato pendiente. | tools actuales: source_reference_validator | usado por: coordinador_expediente_penal
- `construir_cronologia_penal`: ordenar hechos en linea de tiempo. | tools actuales: date_extractor, entity_extractor, case_state_writer | usado por: analista_cronologia_hechos_penales, preparador_estrategico_audiencias_penales
- `crear_matriz_hecho_fuente`: relacionar cada hecho con su fuente exacta. | tools actuales: rag_expediente_search, source_reference_validator | usado por: analista_cronologia_hechos_penales, analista_calidad_juridica
- `detectar_contradicciones_factuales`: encontrar inconsistencias entre versiones, documentos, fechas, valores o actores. | tools actuales: rag_expediente_search, entity_extractor | usado por: analista_cronologia_hechos_penales, analista_calidad_juridica
- `detectar_vacios_factuales`: identificar lo que falta para comprender o probar el caso. | tools actuales: case_state_reader, rag_expediente_search | usado por: analista_cronologia_hechos_penales, coordinador_expediente_penal
- `extraer_hechos_relevantes`: extraer hechos relevantes de documentos, relatos, audios o comunicaciones. | tools actuales: document_parser_extract_text, ocr_extract_text, transcribe_audio, rag_expediente_search | usado por: analista_cronologia_hechos_penales, redactor_documentos_juridicos_penales, gestor_evidencia_y_soporte_probatorio
- `generar_preguntas_aclaracion`: crear preguntas para victima, testigos o abogado humano sin inducir respuestas. | tools actuales: sin_herramientas_obligatorias | usado por: analista_cronologia_hechos_penales, gestor_evidencia_y_soporte_probatorio
- `identificar_actores_y_roles`: identificar victima, presunto responsable, testigos, autoridades, terceros y entidades. | tools actuales: entity_extractor, pii_detector, rag_expediente_search | usado por: analista_cronologia_hechos_penales, analista_representacion_victimas

### Skills de tipicidad y responsabilidad penal
- RAG sugerido: `rag_codigo_penal_search + rag_jurisprudencia_penal_search + rag_normativo_search`
- Tools sugeridas: `tipo_penal_matcher, element_coverage_matrix_builder, ratio_decidendi_extractor`
- `analizar_autoria_y_participacion`: evaluar posibles roles de los intervinientes de manera preliminar. | tools actuales: rag_codigo_penal_search, rag_expediente_search | usado por: analista_tipicidad_y_responsabilidad_penal
- `analizar_dolo_culpa_elemento_subjetivo`: identificar hechos que podrian soportar dolo, culpa u otro elemento subjetivo. | tools actuales: rag_expediente_search, rag_jurisprudencia_penal_search | usado por: analista_tipicidad_y_responsabilidad_penal
- `descomponer_elementos_tipo_penal`: dividir un posible delito en elementos juridicos verificables. | tools actuales: rag_codigo_penal_search, citation_checker | usado por: analista_tipicidad_y_responsabilidad_penal
- `detectar_agravantes_atenuantes`: identificar circunstancias relevantes que puedan afectar gravedad juridica. | tools actuales: rag_codigo_penal_search, rag_expediente_search | usado por: analista_tipicidad_y_responsabilidad_penal
- `detectar_riesgos_atipicidad`: detectar cuando un caso puede ser atipico o tener naturaleza no penal. | tools actuales: rag_jurisprudencia_penal_search, rag_expediente_search | usado por: analista_tipicidad_y_responsabilidad_penal, analista_calidad_juridica
- `generar_preguntas_tipicidad`: crear preguntas para completar elementos del tipo penal. | tools actuales: sin_herramientas_obligatorias | usado por: analista_tipicidad_y_responsabilidad_penal, analista_cronologia_hechos_penales
- `identificar_conductas_punibles_preliminares`: proponer posibles conductas punibles con base en hechos, sin conclusion definitiva. | tools actuales: rag_codigo_penal_search, rag_normativo_search | usado por: analista_tipicidad_y_responsabilidad_penal
- `mapear_tipo_penal_hecho_prueba`: relacionar elementos del tipo con hechos y pruebas. | tools actuales: rag_expediente_search, rag_codigo_penal_search | usado por: analista_tipicidad_y_responsabilidad_penal, gestor_evidencia_y_soporte_probatorio, analista_calidad_juridica

### Skills de ruta procesal Ley 906
- RAG sugerido: `rag_ley906_search + rag_expediente_search`
- Tools sugeridas: `procedural_stage_engine, term_deadline_calculator_v2, procedural_action_recommender`
- `analizar_intervencion_victima`: definir intervencion posible de la victima en una actuacion o audiencia. | tools actuales: rag_ley906_search, rag_normas_victimas_search | usado por: analista_ruta_procesal_ley906, preparador_estrategico_audiencias_penales
- `controlar_terminos_procesales_preliminares`: identificar y alertar terminos relevantes. No reemplaza calculo humano. | tools actuales: calendar_terms_calculator, calendar_event_create, audit_log_write | usado por: analista_ruta_procesal_ley906, gestor_seguimiento_procesal_penal
- `crear_ruta_procesal_recomendada`: crear plan de proximos pasos procesales para revision del abogado. | tools actuales: task_manager_create, audit_log_write | usado por: analista_ruta_procesal_ley906, coordinador_expediente_penal
- `detectar_riesgos_procesales`: detectar riesgos de oportunidad, legitimacion, competencia, improcedencia o perdida de derechos. | tools actuales: rag_ley906_search, case_state_reader | usado por: analista_ruta_procesal_ley906, analista_calidad_juridica
- `evaluar_oportunidad_procesal`: determinar si una solicitud o intervencion es oportuna, prematura o extemporanea. | tools actuales: rag_ley906_search, calendar_terms_calculator | usado por: analista_ruta_procesal_ley906, analista_calidad_juridica
- `evaluar_solicitud_fiscalia_juez`: evaluar si una solicitud a Fiscalia o juez es procedente y conveniente. | tools actuales: rag_ley906_search, rag_expediente_search, citation_checker | usado por: analista_ruta_procesal_ley906, redactor_documentos_juridicos_penales
- `identificar_etapa_procesal_ley906`: determinar etapa del caso. | tools actuales: rag_expediente_search, process_lookup_query, rag_ley906_search | usado por: analista_ruta_procesal_ley906, coordinador_expediente_penal
- `mapear_actuaciones_posibles_victima`: indicar que puede hacer la representacion de victimas segun etapa. | tools actuales: rag_ley906_search, rag_normas_victimas_search, citation_checker | usado por: analista_ruta_procesal_ley906, analista_representacion_victimas

### Skills de representacion de victimas
- RAG sugerido: `rag_normas_victimas_search + rag_constitucional_search + rag_expediente_search`
- Tools sugeridas: `victim_rights_mapper, differential_approach_flagger, victim_interest_ranker`
- `alinear_estrategia_prueba_proceso`: alinear teoria de victima con ruta procesal y plan probatorio. | tools actuales: case_state_reader, rag_expediente_search | usado por: analista_representacion_victimas, analista_calidad_juridica
- `analizar_derechos_victima`: mapear derechos de victima aplicables al caso. | tools actuales: rag_normas_victimas_search, rag_constitucional_search | usado por: analista_representacion_victimas, evaluador_derechos_fundamentales_tutela
- `analizar_enfoque_diferencial`: identificar sujetos de especial proteccion y necesidades diferenciadas. | tools actuales: rag_constitucional_search, rag_normas_victimas_search, pii_detector | usado por: analista_representacion_victimas, evaluador_derechos_fundamentales_tutela
- `construir_teoria_caso_victima`: formular teoria preliminar desde la victima. | tools actuales: rag_expediente_search, rag_normativo_search | usado por: analista_representacion_victimas, preparador_estrategico_audiencias_penales
- `detectar_riesgo_revictimizacion`: identificar lenguaje, preguntas, acciones o estrategias que puedan revictimizar. | tools actuales: revictimization_risk_checker | usado por: analista_representacion_victimas, preparador_estrategico_audiencias_penales, analista_calidad_juridica
- `evaluar_dano_y_afectacion`: organizar danos y afectaciones alegadas. | tools actuales: rag_expediente_search, rag_medicina_legal_search | usado por: analista_representacion_victimas, gestor_evidencia_y_soporte_probatorio
- `identificar_intereses_victima`: aclarar el objetivo real de la victima. | tools actuales: rag_expediente_search, victim_objective_mapper | usado por: analista_representacion_victimas
- `priorizar_objetivos_representacion`: ordenar objetivos de la representacion. | tools actuales: sin_herramientas_obligatorias | usado por: analista_representacion_victimas, coordinador_expediente_penal

### Skills de evidencia y soporte probatorio
- RAG sugerido: `rag_expediente_search + rag_medicina_legal_search`
- Tools sugeridas: `evidence_chain_checker, forensic_metadata_validator, evidence_gap_scorer`
- `clasificar_tipo_prueba`: clasificar evidencia como documental, testimonial, digital, fisica, pericial, institucional o pendiente. | tools actuales: metadata_extractor, document_parser_extract_text | usado por: gestor_evidencia_y_soporte_probatorio
- `construir_matriz_hecho_prueba`: relacionar hechos con pruebas existentes y faltantes. | tools actuales: rag_expediente_search, source_reference_validator | usado por: gestor_evidencia_y_soporte_probatorio, analista_tipicidad_y_responsabilidad_penal, preparador_estrategico_audiencias_penales
- `controlar_cadena_custodia_preliminar`: alertar si la evidencia puede requerir cadena de custodia. | tools actuales: chain_of_custody_logger, metadata_extractor | usado por: gestor_evidencia_y_soporte_probatorio, analista_calidad_juridica
- `crear_plan_recaudo_probatorio`: proponer plan para obtener pruebas faltantes. | tools actuales: task_manager_create, rag_expediente_search | usado por: gestor_evidencia_y_soporte_probatorio, analista_representacion_victimas
- `detectar_brechas_probatorias`: identificar hechos relevantes sin soporte suficiente. | tools actuales: rag_expediente_search, case_state_reader | usado por: gestor_evidencia_y_soporte_probatorio, analista_calidad_juridica
- `evaluar_suficiencia_probatoria`: evaluar preliminarmente fuerza de soporte probatorio. | tools actuales: rag_expediente_search | usado por: gestor_evidencia_y_soporte_probatorio, analista_representacion_victimas
- `generar_preguntas_testigos_peritos`: preparar preguntas neutrales para testigos o peritos. | tools actuales: sin_herramientas_obligatorias | usado por: gestor_evidencia_y_soporte_probatorio, preparador_estrategico_audiencias_penales
- `inventariar_evidencia`: crear inventario de todos los elementos disponibles. | tools actuales: evidence_vault_store, metadata_extractor, file_hash_generator | usado por: gestor_evidencia_y_soporte_probatorio
- `preservar_evidencia_digital`: definir medidas para proteger evidencia digital sin alterarla. | tools actuales: file_hash_generator, metadata_extractor, evidence_vault_store, chain_of_custody_logger | usado por: gestor_evidencia_y_soporte_probatorio

### Skills de audiencias
- RAG sugerido: `rag_ley906_search + rag_jurisprudencia_search + rag_expediente_search`
- Tools sugeridas: `hearing_strategy_simulator, oral_argument_outline_builder, cross_exam_question_linter`
- `crear_checklist_previo_audiencia`: listar requisitos antes de audiencia. | tools actuales: calendar_event_reader, document_bundle_builder, task_manager_create | usado por: preparador_estrategico_audiencias_penales, gestor_seguimiento_procesal_penal
- `crear_resumen_ejecutivo_litigante`: crear resumen de una pagina para el abogado que interviene. | tools actuales: rag_expediente_search, case_state_reader | usado por: preparador_estrategico_audiencias_penales
- `detectar_riesgos_audiencia`: detectar riesgos de intervencion, oportunidad, revelacion de estrategia o revictimizacion. | tools actuales: revictimization_risk_checker, rag_ley906_search | usado por: preparador_estrategico_audiencias_penales, analista_calidad_juridica
- `identificar_objetivo_audiencia`: definir objetivo juridico y tactico de la audiencia para la victima. | tools actuales: rag_ley906_search, calendar_event_reader | usado por: preparador_estrategico_audiencias_penales
- `preparar_contraargumentos`: anticipar argumentos de defensa, Fiscalia u otros intervinientes. | tools actuales: rag_expediente_search, rag_jurisprudencia_search | usado por: preparador_estrategico_audiencias_penales
- `preparar_guion_intervencion_oral`: estructurar intervencion oral clara y breve. | tools actuales: hearing_template_loader, rag_ley906_search | usado por: preparador_estrategico_audiencias_penales
- `preparar_preguntas_audiencia`: sugerir preguntas para victima, testigos o peritos. | tools actuales: rag_expediente_search | usado por: preparador_estrategico_audiencias_penales
- `preparar_solicitudes_orales`: formular solicitudes orales posibles segun etapa. | tools actuales: rag_ley906_search, citation_checker | usado por: preparador_estrategico_audiencias_penales, analista_ruta_procesal_ley906
- `simular_escenarios_audiencia`: plantear escenarios probables y preparacion del abogado. | tools actuales: rag_expediente_search | usado por: preparador_estrategico_audiencias_penales

### Skills de redaccion juridica penal
- RAG sugerido: `rag_plantillas_search + rag_expediente_search + rag_normativo_search`
- Tools sugeridas: `legal_template_filler, citation_footnote_builder, draft_diff_reviewer`
- `controlar_tono_juridico_documento`: asegurar tono formal, preciso, no agresivo y no especulativo. | tools actuales: tone_checker, revictimization_risk_checker | usado por: redactor_documentos_juridicos_penales, analista_calidad_juridica
- `estructurar_hechos_fundamentos_solicitudes`: ordenar cualquier documento juridico. | tools actuales: rag_plantillas_search | usado por: redactor_documentos_juridicos_penales
- `redactar_ampliacion_denuncia`: estructurar hechos nuevos, pruebas y anexos para ampliar denuncia. | tools actuales: rag_plantillas_search, rag_expediente_search | usado por: redactor_documentos_juridicos_penales
- `redactar_derecho_peticion_penal`: redactar derecho de peticion relacionado con autoridad o informacion del caso. | tools actuales: rag_constitucional_search, rag_plantillas_search | usado por: redactor_documentos_juridicos_penales, evaluador_derechos_fundamentales_tutela
- `redactar_memorial_penal`: crear borrador de memorial penal. | tools actuales: rag_plantillas_search, rag_normativo_search, rag_expediente_search, document_version_create | usado por: redactor_documentos_juridicos_penales
- `redactar_recurso_o_intervencion_preliminar`: crear borrador preliminar de recurso o intervencion, sujeto a revision procesal. | tools actuales: rag_ley906_search, rag_jurisprudencia_search, calendar_terms_calculator | usado por: redactor_documentos_juridicos_penales, analista_ruta_procesal_ley906
- `redactar_solicitud_impulso_procesal`: crear borrador para solicitar impulso procesal o actuaciones. | tools actuales: rag_plantillas_search, rag_ley906_search, citation_checker | usado por: redactor_documentos_juridicos_penales
- `redactar_tutela_penal_preliminar`: crear borrador de tutela solo si el evaluador constitucional lo recomienda preliminarmente. | tools actuales: rag_constitucion_search, rag_corte_constitucional_search, rag_plantillas_search | usado por: redactor_documentos_juridicos_penales, evaluador_derechos_fundamentales_tutela

### Skills de seguimiento procesal
- RAG sugerido: `rag_expediente_search`
- Tools sugeridas: `docket_sync_bot, deadline_alert_dispatcher, case_status_digest_generator`
- `actualizar_tareas_responsable`: mantener lista de tareas por agente o abogado. | tools actuales: task_manager_create, task_manager_update | usado por: coordinador_expediente_penal, gestor_seguimiento_procesal_penal
- `controlar_audiencias`: administrar fechas, horas, enlaces y preparacion de audiencias. | tools actuales: calendar_event_create, calendar_event_reader, task_manager_create | usado por: gestor_seguimiento_procesal_penal, preparador_estrategico_audiencias_penales
- `crear_reporte_estado_caso`: crear reporte interno periodico. | tools actuales: case_state_reader, audit_log_write | usado por: gestor_seguimiento_procesal_penal
- `detectar_inactividad_procesal`: alertar falta de movimientos por periodo relevante. | tools actuales: process_lookup_query, case_state_reader | usado por: gestor_seguimiento_procesal_penal, analista_ruta_procesal_ley906
- `generar_alertas_terminos_vencimientos`: crear alertas de posibles vencimientos. | tools actuales: calendar_terms_calculator, notification_create | usado por: gestor_seguimiento_procesal_penal, analista_ruta_procesal_ley906
- `monitorear_radicado`: consultar o registrar estado de radicado. | tools actuales: process_lookup_query, audit_log_write | usado por: gestor_seguimiento_procesal_penal
- `preparar_resumen_operativo_cliente`: crear version simple del estado del proceso para cliente, sin estrategia sensible. | tools actuales: case_state_reader, approval_gate_submit | usado por: gestor_seguimiento_procesal_penal, analista_calidad_juridica
- `registrar_actuacion_procesal`: registrar una actuacion nueva en la bitacora del caso. | tools actuales: case_state_writer, audit_log_write | usado por: gestor_seguimiento_procesal_penal
- `seguimiento_documentos_radicados`: controlar documentos enviados y respuestas pendientes. | tools actuales: document_version_control, case_state_writer, task_manager_update | usado por: gestor_seguimiento_procesal_penal

### Skills constitucionales y tutela
- RAG sugerido: `rag_corte_constitucional_search + rag_constitucion_search + rag_constitucional_search`
- Tools sugeridas: `tutela_procedencia_checklist, fundamental_rights_mapper, subsidiarity_risk_detector`
- `analizar_perjuicio_irremediable`: identificar urgencia constitucional. | tools actuales: rag_corte_constitucional_search, rag_expediente_search | usado por: evaluador_derechos_fundamentales_tutela
- `crear_matriz_hecho_derecho_fundamental`: relacionar hechos con derechos afectados. | tools actuales: rag_expediente_search, rag_constitucion_search | usado por: evaluador_derechos_fundamentales_tutela
- `detectar_riesgo_improcedencia_tutela`: detectar si tutela puede ser prematura, subsidiaria o improcedente. | tools actuales: rag_corte_constitucional_search | usado por: evaluador_derechos_fundamentales_tutela, analista_calidad_juridica
- `evaluar_derecho_peticion`: revisar si existe derecho de peticion incumplido. | tools actuales: calendar_terms_calculator, rag_constitucional_search | usado por: evaluador_derechos_fundamentales_tutela, redactor_documentos_juridicos_penales
- `evaluar_procedencia_tutela`: evaluar legitimacion, subsidiariedad, inmediatez y relevancia constitucional. | tools actuales: rag_corte_constitucional_search, citation_checker | usado por: evaluador_derechos_fundamentales_tutela, analista_calidad_juridica
- `identificar_derecho_fundamental_afectado`: identificar posibles derechos fundamentales comprometidos. | tools actuales: rag_constitucion_search, rag_expediente_search | usado por: evaluador_derechos_fundamentales_tutela
- `preparar_borrador_tutela_preliminar`: preparar insumos para borrador de tutela. | tools actuales: rag_plantillas_search, rag_corte_constitucional_search | usado por: evaluador_derechos_fundamentales_tutela, redactor_documentos_juridicos_penales
- `recomendar_via_constitucional_o_alternativa`: recomendar tutela, derecho de peticion, solicitud procesal, queja u otra ruta. | tools actuales: rag_constitucional_search, rag_ley906_search | usado por: evaluador_derechos_fundamentales_tutela, coordinador_expediente_penal
- `revisar_mecanismos_ordinarios`: verificar si hay vias ordinarias antes de tutela. | tools actuales: rag_ley906_search, rag_corte_constitucional_search | usado por: evaluador_derechos_fundamentales_tutela

### Skills de calidad juridica
- RAG sugerido: `rag_expediente_search + rag_normativo_search + rag_jurisprudencia_search`
- Tools sugeridas: `factual_hallucination_detector, legal_citation_validator, privacy_redaction_engine`
- `clasificar_aprobacion_juridica`: clasificar la salida como aprobable, aprobable con cambios, rechazada o escalar. | tools actuales: approval_gate_decision, audit_log_write | usado por: analista_calidad_juridica
- `controlar_confidencialidad_datos_sensibles`: detectar datos sensibles o innecesarios. | tools actuales: pii_detector, sensitive_data_classifier | usado por: analista_calidad_juridica
- `controlar_no_revictimizacion`: revisar que la salida no culpe ni exponga indebidamente a la victima. | tools actuales: revictimization_risk_checker | usado por: analista_calidad_juridica, analista_representacion_victimas
- `controlar_separacion_hecho_inferencia`: verificar que no se confundan hechos probados, narrados, inferidos y pendientes. | tools actuales: source_reference_validator | usado por: analista_calidad_juridica, redactor_documentos_juridicos_penales
- `controlar_tono_riesgo_reputacional`: revisar tono profesional y evitar lenguaje riesgoso. | tools actuales: tone_checker | usado por: analista_calidad_juridica, redactor_documentos_juridicos_penales
- `detectar_alucinaciones_legales`: detectar fuentes, hechos, conclusiones o citas inventadas. | tools actuales: rag_source_validator, citation_checker, rag_expediente_search | usado por: analista_calidad_juridica
- `revisar_coherencia_estrategica`: asegurar que documento o recomendacion sea coherente con la estrategia aprobada. | tools actuales: strategy_consistency_checker, case_state_reader | usado por: analista_calidad_juridica
- `verificar_citas_normativas`: verificar que normas, articulos y leyes citadas existan en el RAG o esten marcadas pendientes. | tools actuales: citation_checker, rag_normativo_search | usado por: analista_calidad_juridica, redactor_documentos_juridicos_penales
- `verificar_jurisprudencia`: revisar sentencias, radicados, fechas y organos judiciales. | tools actuales: citation_checker, rag_jurisprudencia_search | usado por: analista_calidad_juridica

## 7) Errores similares detectados y correccion aplicada
- Error 1 corregido: `agente/prompts/sistema.md` incluia alcance multi-materia; quedo en modo exclusivo penal-victimas.
- Error 2 corregido: texto de coordinador en `src/agents/orchestrator.py` ajustado a "fuera de penal-victimas" (sin sesgo a materias fuera de alcance).
- Error 3 corregido: reportes previos contenian snapshot viejo del prompt base; se regenero este reporte con el prompt actualizado.