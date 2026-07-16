# Baseline — Validación 7 expertos (2026-07-16 00:34)

## Métricas automáticas

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

## Skills por bloque

### Bloque A (11 skills)

- `analizar_perjuicio_irremediable`
- `crear_matriz_hecho_derecho_fundamental`
- `detectar_riesgo_improcedencia_tutela`
- `evaluar_derecho_peticion`
- `evaluar_procedencia_tutela`
- `identificar_derecho_fundamental_afectado`
- `preparar_borrador_tutela_preliminar`
- `recomendar_via_constitucional_o_alternativa`
- `redactar_derecho_peticion_penal`
- `redactar_tutela_penal_preliminar`
- `revisar_mecanismos_ordinarios`

### Bloque B (16 skills)

- `clasificar_aprobacion_juridica`
- `controlar_confidencialidad_datos_sensibles`
- `controlar_no_revictimizacion`
- `controlar_separacion_hecho_inferencia`
- `controlar_tono_juridico_documento`
- `controlar_tono_riesgo_reputacional`
- `detectar_alucinaciones_legales`
- `detectar_riesgo_revictimizacion`
- `estructurar_hechos_fundamentos_solicitudes`
- `redactar_ampliacion_denuncia`
- `redactar_memorial_penal`
- `redactar_recurso_o_intervencion_preliminar`
- `redactar_solicitud_impulso_procesal`
- `revisar_coherencia_estrategica`
- `verificar_citas_normativas`
- `verificar_jurisprudencia`

### Bloque C (13 skills)

- `analizar_intervencion_victima`
- `clasificar_tarea_y_etapa`
- `controlar_terminos_procesales_preliminares`
- `crear_ruta_procesal_recomendada`
- `detectar_riesgos_procesales`
- `detectar_urgencia_penal`
- `evaluar_oportunidad_procesal`
- `evaluar_solicitud_fiscalia_juez`
- `gestionar_faltantes_expediente`
- `identificar_etapa_procesal_ley906`
- `mapear_actuaciones_posibles_victima`
- `marcar_pendientes_verificacion`
- `verificar_hechos_soportados`

### Bloque D (24 skills)

- `analizar_autoria_y_participacion`
- `analizar_dolo_culpa_elemento_subjetivo`
- `clasificar_fuente_factual`
- `clasificar_tipo_prueba`
- `construir_cronologia_penal`
- `construir_matriz_hecho_prueba`
- `controlar_cadena_custodia_preliminar`
- `crear_matriz_hecho_fuente`
- `crear_plan_recaudo_probatorio`
- `descomponer_elementos_tipo_penal`
- `detectar_agravantes_atenuantes`
- `detectar_brechas_probatorias`
- `detectar_contradicciones_factuales`
- `detectar_riesgos_atipicidad`
- `detectar_vacios_factuales`
- `evaluar_suficiencia_probatoria`
- `extraer_hechos_relevantes`
- `generar_preguntas_aclaracion`
- `generar_preguntas_tipicidad`
- `identificar_actores_y_roles`
- `identificar_conductas_punibles_preliminares`
- `inventariar_evidencia`
- `mapear_tipo_penal_hecho_prueba`
- `preservar_evidencia_digital`

### Bloque E (18 skills)

- `alinear_estrategia_prueba_proceso`
- `analizar_derechos_victima`
- `analizar_enfoque_diferencial`
- `construir_teoria_caso_victima`
- `controlar_audiencias`
- `crear_checklist_previo_audiencia`
- `crear_resumen_ejecutivo_litigante`
- `detectar_riesgos_audiencia`
- `evaluar_dano_y_afectacion`
- `generar_preguntas_testigos_peritos`
- `identificar_intereses_victima`
- `identificar_objetivo_audiencia`
- `preparar_contraargumentos`
- `preparar_guion_intervencion_oral`
- `preparar_preguntas_audiencia`
- `preparar_solicitudes_orales`
- `priorizar_objetivos_representacion`
- `simular_escenarios_audiencia`

### Bloque F (8 skills)

- `actualizar_tareas_responsable`
- `crear_reporte_estado_caso`
- `detectar_inactividad_procesal`
- `generar_alertas_terminos_vencimientos`
- `monitorear_radicado`
- `preparar_resumen_operativo_cliente`
- `registrar_actuacion_procesal`
- `seguimiento_documentos_radicados`

## Lista canónica

```
CHECK OK: 90 skills + matriz variable validada
```

## Pytest

```
.........                                                                [100%]
=============================== warnings summary ===============================
tests/test_compliance.py::test_audit_progress_history_and_isolation
  /Users/ricardodebiase/Documents/agente de IA juridico/.venv/lib/python3.13/site-packages/httpx/_client.py:1896: DeprecationWarning: Setting per-request cookies=<...> is being deprecated, because the expected behaviour on cookie persistence is ambiguous. Set cookies directly on the client instance instead.
    return await self.request(

tests/test_compliance.py::test_audit_progress_history_and_isolation
  /Users/ricardodebiase/Documents/agente de IA juridico/.venv/lib/python3.13/site-packages/httpx/_client.py:1768: DeprecationWarning: Setting per-request cookies=<...> is being deprecated, because the expected behaviour on cookie persistence is ambiguous. Set cookies directly on the client instance instead.
    return await self.request(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
9 passed, 2 warnings in 1.39s
```
