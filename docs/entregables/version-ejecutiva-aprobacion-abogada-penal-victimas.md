# Version ejecutiva para aprobacion juridica

![DBX Solutions](../assets/dbx-logo.png)

**Documento:** Aprobacion de arquitectura y operacion multiagente penal-victimas  
**Dirigido a:** Abogada lider  
**Fecha:** 2026-07-01  
**Ambito:** Representacion de victimas en materia penal colombiana (Ley 906)

---

## 1) Objeto de aprobacion

Este documento presenta, en formato ejecutivo, el modelo operativo de la firma virtual penal-victimas para validar:

1. pertinencia juridica de los roles agenticos,
2. suficiencia tecnica de skills para trabajo diario de litigio,
3. robustez de controles HITL (human-in-the-loop),
4. consistencia de los flujos conversacionales para uso real del despacho.

---

## 2) Regla profesional y limites

- La IA **no reemplaza** criterio, direccion ni firma profesional.
- La IA **no inventa** normas, sentencias, radicados, hechos ni soportes.
- Toda salida con destino externo (cliente, autoridad, tercero) exige aprobacion humana.
- El despacho conserva control sobre estrategia, tono juridico y decision de radicacion.

---

## 3) Arquitectura funcional (resumen)

El sistema opera por orquestacion y especializacion:

1. `coordinador_expediente_penal` recibe la solicitud y clasifica objetivo/etapa.
2. Enruta al especialista por dominio (hechos, tipicidad, ruta 906, evidencia, audiencia, redaccion, seguimiento, tutela).
3. `analista_calidad_juridica` realiza control previo de riesgos y consistencia.
4. La abogada revisa y aprueba antes de cualquier uso externo.

---

## 4) Roles de agente y skills nucleares

> Nota: el catalogo completo activo contiene 90 skills atomicos. Aqui se listan los skills troncales para decision ejecutiva.

### 4.1 `coordinador_expediente_penal`
- **Funcion:** triage legal-operativo y direccion del flujo.
- **Skills clave:** `clasificar_tarea_y_etapa`, `detectar_urgencia_penal`, `gestionar_faltantes_expediente`, `crear_ruta_procesal_recomendada`, `recomendar_via_constitucional_o_alternativa`.

### 4.2 `analista_cronologia_hechos_penales`
- **Funcion:** depuracion factual y linea de tiempo verificable.
- **Skills clave:** `extraer_hechos_relevantes`, `construir_cronologia_penal`, `identificar_actores_y_roles`, `detectar_contradicciones_factuales`, `crear_matriz_hecho_fuente`.

### 4.3 `analista_tipicidad_y_responsabilidad_penal`
- **Funcion:** analisis preliminar de tipicidad y responsabilidad.
- **Skills clave:** `identificar_conductas_punibles_preliminares`, `descomponer_elementos_tipo_penal`, `mapear_tipo_penal_hecho_prueba`, `detectar_riesgos_atipicidad`, `detectar_agravantes_atenuantes`.

### 4.4 `analista_ruta_procesal_ley906`
- **Funcion:** lectura procesal por etapa y oportunidad.
- **Skills clave:** `identificar_etapa_procesal_ley906`, `mapear_actuaciones_posibles_victima`, `evaluar_oportunidad_procesal`, `controlar_terminos_procesales_preliminares`, `detectar_riesgos_procesales`.

### 4.5 `analista_representacion_victimas`
- **Funcion:** estrategia centrada en derechos/intereses de la victima.
- **Skills clave:** `identificar_intereses_victima`, `construir_teoria_caso_victima`, `analizar_derechos_victima`, `detectar_riesgo_revictimizacion`, `priorizar_objetivos_representacion`.

### 4.6 `gestor_evidencia_y_soporte_probatorio`
- **Funcion:** gestion probatoria y brechas de soporte.
- **Skills clave:** `inventariar_evidencia`, `construir_matriz_hecho_prueba`, `detectar_brechas_probatorias`, `preservar_evidencia_digital`, `controlar_cadena_custodia_preliminar`.

### 4.7 `preparador_estrategico_audiencias_penales`
- **Funcion:** preparacion tactica de audiencias.
- **Skills clave:** `identificar_objetivo_audiencia`, `preparar_guion_intervencion_oral`, `preparar_solicitudes_orales`, `preparar_contraargumentos`, `crear_checklist_previo_audiencia`.

### 4.8 `redactor_documentos_juridicos_penales`
- **Funcion:** redaccion tecnica de piezas revisables.
- **Skills clave:** `redactar_memorial_penal`, `redactar_solicitud_impulso_procesal`, `redactar_recurso_o_intervencion_preliminar`, `estructurar_hechos_fundamentos_solicitudes`, `verificar_citas_normativas`.

### 4.9 `gestor_seguimiento_procesal_penal`
- **Funcion:** continuidad operativa y trazabilidad de radicado/actuaciones.
- **Skills clave:** `monitorear_radicado`, `registrar_actuacion_procesal`, `generar_alertas_terminos_vencimientos`, `crear_reporte_estado_caso`, `preparar_resumen_operativo_cliente`.

### 4.10 `evaluador_derechos_fundamentales_tutela`
- **Funcion:** filtro constitucional de procedencia.
- **Skills clave:** `identificar_derecho_fundamental_afectado`, `evaluar_procedencia_tutela`, `revisar_mecanismos_ordinarios`, `detectar_riesgo_improcedencia_tutela`, `recomendar_via_constitucional_o_alternativa`.

### 4.11 `analista_calidad_juridica`
- **Funcion:** control previo de calidad juridica y riesgo.
- **Skills clave:** `verificar_hechos_soportados`, `verificar_citas_normativas`, `detectar_alucinaciones_legales`, `controlar_confidencialidad_datos_sensibles`, `clasificar_aprobacion_juridica`.

---

## 5) Flujos conversacionales de referencia

## Flujo A - Apertura de caso
**Solicitud:** "Necesito organizar hechos y definir ruta inicial para representacion de victima."

**Ruta:** coordinador -> cronologia -> representacion de victimas -> calidad -> revision abogada.

**Resultado esperado:** cronologia con fuentes, vacios factuales y plan de recaudo inicial.

## Flujo B - Tipicidad preliminar
**Solicitud:** "Valore posibles conductas punibles y riesgos de atipicidad."

**Ruta:** coordinador -> tipicidad -> evidencia -> calidad -> revision abogada.

**Resultado esperado:** matriz elemento-hecho-prueba, hipotesis preliminares y brechas.

## Flujo C - Preparacion de audiencia
**Solicitud:** "Prepare guion de intervencion y solicitudes para audiencia preliminar."

**Ruta:** coordinador -> ruta 906 -> preparador de audiencias -> calidad -> revision abogada.

**Resultado esperado:** guion tactico, checklist previo, riesgos de audiencia.

## Flujo D - Tutela vinculada a caso penal
**Solicitud:** "Evalua procedencia de tutela por afectacion de debido proceso."

**Ruta:** coordinador -> evaluador tutela -> redactor (si procede) -> calidad -> revision abogada.

**Resultado esperado:** concepto preliminar de procedencia + borrador condicionado.

---

## 6) Matriz HITL para aprobacion

| Salida | Uso interno inmediato | Requiere control de calidad | Requiere aprobacion abogada |
|---|---|---|---|
| Cronologia preliminar | Si | Recomendado | Si, antes de uso estrategico |
| Analisis tipicidad preliminar | Si | Si | Si |
| Guion de audiencia | No | Si | Si |
| Memorial/recurso/solicitud | No | Si | Si (obligatorio) |
| Tutela preliminar | No | Si | Si (obligatorio reforzado) |
| Reporte a cliente | No | Si | Si |

---

## 7) Criterios de aprobacion sugeridos

- [ ] Los 11 roles representan funciones reales del despacho.
- [ ] Los skills nucleares son suficientes para carga operativa semanal.
- [ ] Los flujos respetan practica procesal Ley 906.
- [ ] El esquema HITL preserva responsabilidad profesional.
- [ ] No hay riesgo de salida externa automatica sin revision humana.

---

## 8) Recomendacion

Se recomienda aprobar bajo modalidad **"piloto controlado con gobernanza juridica estricta"**:

1. revision semanal de calidad de salidas,
2. seguimiento de incidentes de alucinacion (meta tendencia a 0),
3. validacion humana obligatoria para toda salida externa.
