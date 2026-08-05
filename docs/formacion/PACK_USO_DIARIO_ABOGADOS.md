# Pack de uso diario — abogados (penal-víctimas)

Capa operativa sobre el catálogo amplio (~81 skills). **Use solo este set** en el día a día; el resto es profundidad para casos complejos o auditoría.

**Cómo pedirlo en chat:** hable en lenguaje natural al Coordinador. No necesita invocar skills por ID.

---

## Pack por área (prompt + 3–5 skills)

### Coordinador del Caso (voz única)
- **Pida:** clasificar urgencia, completar faltantes, siguiente paso del despacho.
- **Skills diarios:** `clasificar_tarea_y_etapa`, `detectar_urgencia_penal`, `gestionar_faltantes_expediente`, `marcar_pendientes_verificacion`, `actualizar_tareas_responsable`.

### Cronología y hechos
- **Pida:** “ordene la cronología con fuentes y vacíos”.
- **Skills diarios:** `construir_cronologia_penal`, `extraer_hechos_relevantes`, `detectar_vacios_factuales`, `detectar_contradicciones_factuales`, `crear_matriz_hecho_fuente`.

### Tipicidad y responsabilidad
- **Pida:** “hipótesis tipica preliminar, no definitiva”.
- **Skills diarios:** `descomponer_elementos_tipo_penal`, `identificar_conductas_punibles_preliminares`, `mapear_tipo_penal_hecho_prueba`, `detectar_riesgos_atipicidad`, `detectar_agravantes_atenuantes`.

### Ruta procesal Ley 906
- **Pida:** “etapa y actuaciones posibles para la víctima”.
- **Skills diarios:** `identificar_etapa_procesal_ley906`, `crear_ruta_procesal_recomendada`, `mapear_actuaciones_posibles_victima`, `evaluar_oportunidad_procesal`, `detectar_riesgos_procesales`.

### Representación de víctimas
- **Pida:** “teoría del caso centrada en la víctima, sin revictimizar”.
- **Skills diarios:** `construir_teoria_caso_victima`, `identificar_intereses_victima`, `analizar_derechos_victima`, `detectar_riesgo_revictimizacion`, `priorizar_objetivos_representacion`.

### Evidencia
- **Pida:** “inventario de prueba y brechas”.
- **Skills diarios:** `inventariar_evidencia`, `construir_matriz_hecho_prueba`, `detectar_brechas_probatorias`, `evaluar_suficiencia_probatoria`, `crear_plan_recaudo_probatorio`.

### Audiencias
- **Pida:** “guion, solicitudes y checklist para la audiencia”.
- **Skills diarios:** `preparar_preguntas_audiencia`, `preparar_guion_intervencion_oral`, `preparar_solicitudes_orales`, `crear_checklist_previo_audiencia`, `detectar_riesgos_audiencia`.

### Redacción (solo con plan aprobado)
- **Pida:** “borrador de memorial / impulso / derecho de petición” → apruebe el plan → firme.
- **Skills diarios:** `redactar_memorial_penal`, `redactar_solicitud_impulso_procesal`, `redactar_derecho_peticion_penal`, `estructurar_hechos_fundamentos_solicitudes`, `verificar_citas_normativas`.
- **Fuera de producto:** tutela / piezas constitucionales.

### Seguimiento procesal
- **Pida:** “estado del radicado, alertas y resumen para cliente (borrador)”.
- **Skills diarios:** `monitorear_radicado`, `generar_alertas_terminos_vencimientos`, `detectar_inactividad_procesal`, `crear_reporte_estado_caso`, `preparar_resumen_operativo_cliente`.

### Calidad jurídica
- **Pida:** “revise coherencia, alucinaciones y tono antes de firmar”.
- **Skills diarios:** `revisar_coherencia_estrategica`, `detectar_alucinaciones_legales`, `verificar_hechos_soportados`, `controlar_confidencialidad_datos_sensibles`, `clasificar_aprobacion_juridica`.

---

## Flujo típico de una mañana

1. Apertura / hechos → cronología + vacíos.  
2. Tipicidad preliminar + brechas de prueba.  
3. Ruta 906 + objetivo de víctima.  
4. Si hay audiencia: guion + checklist.  
5. Si hay pieza: plan → borrador → firma.  
6. Seguimiento: alertas y reporte interno.

## Relacionado

- Guía de 1 página: `docs/formacion/GUIA_1_PAGINA_ABOGADO.md`
- Prompt de valor: `docs/formacion/PROMPT_VALOR_AGENTES_COGNITIVO.md`
- Aprobación (canon): `docs/canon/guia-aprobacion-abogada-flujos-penal-victimas.md`
