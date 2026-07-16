# Reporte — Validación absoluta 7 expertos (2026-07-15 23:54)

## Resumen ejecutivo

Se validaron **90 skills** con 7 perspectivas expertas (rúbrica automatizada + revisión de cadenas).
- **APROBADO:** 90
- **APROBADO_CON_OBSERVACIONES:** 0
- **RECHAZADO:** 0

### Métricas automáticas

| Métrica | Valor |
|---------|------:|
| generic_io | 0 |
| generic_risk | 0 |
| missing_g10 | 0 |
| missing_g9 | 0 |
| mono_sin_rol | 0 |
| multi_no_boundary | 0 |
| profundizar | 0 |
| total | 90 |
| with_boundary | 84 |
| with_guardrails | 90 |
| with_rol | 89 |
| with_steps | 90 |

## Consenso fuerte (7 expertos)

- Cadena tutela con gates explícitos (evaluador → insumos → redactor).
- Ruta Ley 906 no redacta recursos finales sin pasar por redactor.
- Calidad: detectar alucinaciones separado de clasificar aprobación.
- HITL y etiquetas en comunicación con cliente.
- 90/90 skills con Steps, Guardrails y sin plantillas genéricas I/O/riesgo.
- Lista canónica y matriz alineadas (CHECK OK).
- Multi-agente con No duplicar o Handoff en todos los skills compartidos.
- 10 reglas globales g1–g10 (plazos Ley 906 y custodia probatoria).

## Cadenas críticas (5)

| Cadena | Estado | Observaciones |
|--------|--------|---------------|
| tutela | OK | Sin contradicciones |
| recursos_906 | OK | Sin contradicciones |
| calidad_salida | OK | Sin contradicciones |
| cliente | OK | Sin contradicciones |
| evidencia_digital | OK | Sin contradicciones |

## Reglas de negocio

| Regla | Estado |
|-------|--------|
| Tutela solo tras evaluador | OK |
| Ruta 906 no redacta recursos | OK |
| Preguntas víctima HITL | OK |
| IA propone; abogado aprueba | OK |
| Guardrails globales g1–g10 | OK |

## Remediación aplicada (Fase V3)

- `analizar_perjuicio_irremediable` — Añadido g4 HITL en cadena tutela.
- `revisar_mecanismos_ordinarios` — Añadido g4 HITL subsidiariedad.
- `crear_matriz_hecho_derecho_fundamental` — Añadido g4 HITL matriz preliminar.
- `identificar_derecho_fundamental_afectado` — Añadidos g3 separación hecho/inferencia y g4 HITL.
- `crear_resumen_ejecutivo_litigante` — Añadido g4 HITL uso interno abogado.
- `detectar_riesgos_audiencia` — Añadido g4 HITL antes de audiencia.
- `preparar_contraargumentos` — Añadido g4 HITL antes de memorial/audiencia.

Tras remediación: **90/90 APROBADO**, 0 RECHAZADO, 5/5 cadenas OK.

## Tabla completa (90 skills)

| Skill | Tier | Bloque | Veredicto |
|-------|------|--------|-----------|
| `actualizar_tareas_responsable` | atomico | F | APROBADO |
| `alinear_estrategia_prueba_proceso` | estrategico | E | APROBADO |
| `analizar_autoria_y_participacion` | operativo | D | APROBADO |
| `analizar_derechos_victima` | operativo | E | APROBADO |
| `analizar_dolo_culpa_elemento_subjetivo` | operativo | D | APROBADO |
| `analizar_enfoque_diferencial` | operativo | E | APROBADO |
| `analizar_intervencion_victima` | estrategico | C | APROBADO |
| `analizar_perjuicio_irremediable` | estrategico | A | APROBADO |
| `clasificar_aprobacion_juridica` | operativo | B | APROBADO |
| `clasificar_fuente_factual` | estrategico | D | APROBADO |
| `clasificar_tarea_y_etapa` | operativo | C | APROBADO |
| `clasificar_tipo_prueba` | operativo | D | APROBADO |
| `construir_cronologia_penal` | estrategico | D | APROBADO |
| `construir_matriz_hecho_prueba` | operativo | D | APROBADO |
| `construir_teoria_caso_victima` | critico | E | APROBADO |
| `controlar_audiencias` | operativo | E | APROBADO |
| `controlar_cadena_custodia_preliminar` | critico | D | APROBADO |
| `controlar_confidencialidad_datos_sensibles` | operativo | B | APROBADO |
| `controlar_no_revictimizacion` | critico | B | APROBADO |
| `controlar_separacion_hecho_inferencia` | operativo | B | APROBADO |
| `controlar_terminos_procesales_preliminares` | operativo | C | APROBADO |
| `controlar_tono_juridico_documento` | operativo | B | APROBADO |
| `controlar_tono_riesgo_reputacional` | operativo | B | APROBADO |
| `crear_checklist_previo_audiencia` | operativo | E | APROBADO |
| `crear_matriz_hecho_derecho_fundamental` | estrategico | A | APROBADO |
| `crear_matriz_hecho_fuente` | operativo | D | APROBADO |
| `crear_plan_recaudo_probatorio` | estrategico | D | APROBADO |
| `crear_reporte_estado_caso` | operativo | F | APROBADO |
| `crear_resumen_ejecutivo_litigante` | operativo | E | APROBADO |
| `crear_ruta_procesal_recomendada` | estrategico | C | APROBADO |
| `descomponer_elementos_tipo_penal` | estrategico | D | APROBADO |
| `detectar_agravantes_atenuantes` | operativo | D | APROBADO |
| `detectar_alucinaciones_legales` | operativo | B | APROBADO |
| `detectar_brechas_probatorias` | operativo | D | APROBADO |
| `detectar_contradicciones_factuales` | operativo | D | APROBADO |
| `detectar_inactividad_procesal` | operativo | F | APROBADO |
| `detectar_riesgo_improcedencia_tutela` | critico | A | APROBADO |
| `detectar_riesgo_revictimizacion` | operativo | B | APROBADO |
| `detectar_riesgos_atipicidad` | operativo | D | APROBADO |
| `detectar_riesgos_audiencia` | operativo | E | APROBADO |
| `detectar_riesgos_procesales` | estrategico | C | APROBADO |
| `detectar_urgencia_penal` | estrategico | C | APROBADO |
| `detectar_vacios_factuales` | operativo | D | APROBADO |
| `estructurar_hechos_fundamentos_solicitudes` | operativo | B | APROBADO |
| `evaluar_dano_y_afectacion` | operativo | E | APROBADO |
| `evaluar_derecho_peticion` | estrategico | A | APROBADO |
| `evaluar_oportunidad_procesal` | operativo | C | APROBADO |
| `evaluar_procedencia_tutela` | critico | A | APROBADO |
| `evaluar_solicitud_fiscalia_juez` | operativo | C | APROBADO |
| `evaluar_suficiencia_probatoria` | estrategico | D | APROBADO |
| `extraer_hechos_relevantes` | operativo | D | APROBADO |
| `generar_alertas_terminos_vencimientos` | operativo | F | APROBADO |
| `generar_preguntas_aclaracion` | operativo | D | APROBADO |
| `generar_preguntas_testigos_peritos` | operativo | E | APROBADO |
| `generar_preguntas_tipicidad` | operativo | D | APROBADO |
| `gestionar_faltantes_expediente` | operativo | C | APROBADO |
| `identificar_actores_y_roles` | operativo | D | APROBADO |
| `identificar_conductas_punibles_preliminares` | operativo | D | APROBADO |
| `identificar_derecho_fundamental_afectado` | operativo | A | APROBADO |
| `identificar_etapa_procesal_ley906` | estrategico | C | APROBADO |
| `identificar_intereses_victima` | operativo | E | APROBADO |
| `identificar_objetivo_audiencia` | estrategico | E | APROBADO |
| `inventariar_evidencia` | operativo | D | APROBADO |
| `mapear_actuaciones_posibles_victima` | operativo | C | APROBADO |
| `mapear_tipo_penal_hecho_prueba` | estrategico | D | APROBADO |
| `marcar_pendientes_verificacion` | atomico | C | APROBADO |
| `monitorear_radicado` | atomico | F | APROBADO |
| `preparar_borrador_tutela_preliminar` | estrategico | A | APROBADO |
| `preparar_contraargumentos` | operativo | E | APROBADO |
| `preparar_guion_intervencion_oral` | critico | E | APROBADO |
| `preparar_preguntas_audiencia` | operativo | E | APROBADO |
| `preparar_resumen_operativo_cliente` | operativo | F | APROBADO |
| `preparar_solicitudes_orales` | operativo | E | APROBADO |
| `preservar_evidencia_digital` | critico | D | APROBADO |
| `priorizar_objetivos_representacion` | operativo | E | APROBADO |
| `recomendar_via_constitucional_o_alternativa` | operativo | A | APROBADO |
| `redactar_ampliacion_denuncia` | operativo | B | APROBADO |
| `redactar_derecho_peticion_penal` | operativo | A | APROBADO |
| `redactar_memorial_penal` | critico | B | APROBADO |
| `redactar_recurso_o_intervencion_preliminar` | operativo | B | APROBADO |
| `redactar_solicitud_impulso_procesal` | operativo | B | APROBADO |
| `redactar_tutela_penal_preliminar` | critico | A | APROBADO |
| `registrar_actuacion_procesal` | atomico | F | APROBADO |
| `revisar_coherencia_estrategica` | estrategico | B | APROBADO |
| `revisar_mecanismos_ordinarios` | estrategico | A | APROBADO |
| `seguimiento_documentos_radicados` | operativo | F | APROBADO |
| `simular_escenarios_audiencia` | estrategico | E | APROBADO |
| `verificar_citas_normativas` | operativo | B | APROBADO |
| `verificar_hechos_soportados` | operativo | C | APROBADO |
| `verificar_jurisprudencia` | operativo | B | APROBADO |

## Riesgos sistémicos residuales

1. 11 skills mono-agente sin sección Rol en (aceptable si atómicos; E1 condicional).
2. 6 skills mono-agente sin No duplicar (esperado; no aplica frontera multi-agente).
3. Coherencia semántica Steps vs matriz vs Purpose no verificada en runtime real.
4. Coherencia SKILL.md Steps vs lista: E7 puede marcar OBS en skills editados manualmente.
5. Runtime no invoca skills directamente; depende de orquestador/planner.
6. Aprobación humana de abogada sigue siendo gate de producto (no automatizable).
7. RAG y herramientas citadas no verificadas en esta auditoría estática.
8. Validación experta automatizada (rúbrica) no sustituye revisión humana de la abogada.
9. Skills atómicos de seguimiento (bloque F) con menor profundidad táctica penal.
10. Evolución normativa/jurisprudencial requiere re-validación periódica de skills constitucionales.