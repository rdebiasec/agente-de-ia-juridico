# Version ejecutiva para aprobacion juridica

![DBX Solutions](../assets/dbx-logo.png)

**Documento:** Aprobacion de arquitectura y operacion multiagente penal-victimas  
**Dirigido a:** Abogada lider  
**Fecha:** 2026-08-04  
**Ambito:** Representacion de victimas en materia penal colombiana (Ley 906)  
**Producto:** LexiaTek — firma virtual (tutela / via constitucional **fuera del producto**)

---

## 1) Objeto de aprobacion

Este documento presenta, en formato ejecutivo, el modelo operativo de la firma virtual penal-victimas para validar:

1. pertinencia juridica de los roles agenticos (**10**: Coordinador + 9 especialistas),
2. suficiencia tecnica del **pack de uso diario** para litigio,
3. robustez de controles HITL (human-in-the-loop),
4. consistencia de los flujos conversacionales para uso real del despacho.

---

## 2) Regla profesional y limites

- La IA **no reemplaza** criterio, direccion ni firma profesional.
- La IA **no inventa** normas, sentencias, radicados, hechos ni soportes.
- Toda salida con destino externo (cliente, autoridad, tercero) exige aprobacion humana.
- El despacho conserva control sobre estrategia, tono juridico y decision de radicacion.
- Valor: **acelerar actividades cognitivas repetitivas** (orden factual, tipicidad preliminar, inventario probatorio, estructura de piezas, alertas); el abogado decide y firma.

---

## 3) Arquitectura funcional (resumen)

El sistema opera por orquestacion y especializacion:

1. `coordinador_caso` recibe la solicitud (unica voz al abogado) y clasifica objetivo/etapa/urgencia.
2. Enruta al especialista por dominio (hechos, tipicidad, ruta 906, victimas, evidencia, audiencia, seguimiento, calidad). Redaccion solo via **plan aprobado**.
3. `analista_calidad_juridica` realiza control previo de riesgos y consistencia.
4. La abogada revisa y aprueba antes de cualquier uso externo.

Onboarding corto: `docs/formacion/GUIA_1_PAGINA_ABOGADO.md` · pack diario: `docs/formacion/PACK_USO_DIARIO_ABOGADOS.md`.

---

## 4) Roles de agente y skills nucleares

> Catalogo amplio ~81 skills atomicos. Aqui: skills troncales del pack diario.

### 4.1 `coordinador_caso`
- **Funcion:** triage legal-operativo y unica voz de despacho.
- **Skills clave:** `clasificar_tarea_y_etapa`, `detectar_urgencia_penal`, `gestionar_faltantes_expediente`, `marcar_pendientes_verificacion`, `actualizar_tareas_responsable`.

### 4.2 `analista_cronologia_hechos`
- **Funcion:** depuracion factual y linea de tiempo verificable.
- **Skills clave:** `extraer_hechos_relevantes`, `construir_cronologia_penal`, `detectar_contradicciones_factuales`, `detectar_vacios_factuales`, `crear_matriz_hecho_fuente`.

### 4.3 `analista_responsabilidad_tipicidad`
- **Funcion:** analisis preliminar de tipicidad y responsabilidad.
- **Skills clave:** `identificar_conductas_punibles_preliminares`, `descomponer_elementos_tipo_penal`, `mapear_tipo_penal_hecho_prueba`, `detectar_riesgos_atipicidad`, `detectar_agravantes_atenuantes`.

### 4.4 `analista_ruta_procesal`
- **Funcion:** lectura procesal por etapa y oportunidad.
- **Skills clave:** `identificar_etapa_procesal_ley906`, `mapear_actuaciones_posibles_victima`, `evaluar_oportunidad_procesal`, `crear_ruta_procesal_recomendada`, `detectar_riesgos_procesales`.

### 4.5 `analista_representacion_victimas`
- **Funcion:** estrategia centrada en derechos/intereses de la victima.
- **Skills clave:** `identificar_intereses_victima`, `construir_teoria_caso_victima`, `analizar_derechos_victima`, `detectar_riesgo_revictimizacion`, `priorizar_objetivos_representacion`.

### 4.6 `analista_evidencia`
- **Funcion:** gestion probatoria y brechas de soporte.
- **Skills clave:** `inventariar_evidencia`, `construir_matriz_hecho_prueba`, `detectar_brechas_probatorias`, `evaluar_suficiencia_probatoria`, `crear_plan_recaudo_probatorio`.

### 4.7 `analista_audiencias`
- **Funcion:** preparacion tactica de audiencias.
- **Skills clave:** `preparar_preguntas_audiencia`, `preparar_guion_intervencion_oral`, `preparar_solicitudes_orales`, `crear_checklist_previo_audiencia`, `detectar_riesgos_audiencia`.

### 4.8 `redactor_documentos_juridicos`
- **Funcion:** redaccion tecnica de piezas revisables (solo plan HITL).
- **Skills clave:** `redactar_memorial_penal`, `redactar_solicitud_impulso_procesal`, `redactar_derecho_peticion_penal`, `estructurar_hechos_fundamentos_solicitudes`, `verificar_citas_normativas`.
- **Fuera de producto:** tutela / piezas constitucionales.

### 4.9 `analista_seguimiento_procesal`
- **Funcion:** continuidad operativa y trazabilidad de radicado/actuaciones.
- **Skills clave:** `monitorear_radicado`, `registrar_actuacion_procesal`, `generar_alertas_terminos_vencimientos`, `crear_reporte_estado_caso`, `preparar_resumen_operativo_cliente`.

### 4.10 `analista_calidad_juridica`
- **Funcion:** control previo de calidad juridica y riesgo.
- **Skills clave:** `revisar_coherencia_estrategica`, `verificar_hechos_soportados`, `verificar_citas_normativas`, `detectar_alucinaciones_legales`, `clasificar_aprobacion_juridica`.

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

**Ruta:** coordinador -> ruta 906 -> audiencias -> calidad -> revision abogada.

**Resultado esperado:** guion tactico, checklist previo, riesgos de audiencia.

## Flujo D - Mora / inactividad (sin tutela)
**Solicitud:** "No hay respuesta a la peticion; prepare impulso y seguimiento."

**Ruta:** coordinador -> seguimiento -> redactor (plan HITL) -> calidad -> revision abogada.

**Resultado esperado:** borrador de impulso o peticion + alertas; **sin** ruta constitucional.

---

## 6) Matriz HITL para aprobacion

| Salida | Uso interno inmediato | Requiere control de calidad | Requiere aprobacion abogada |
|---|---|---|---|
| Cronologia preliminar | Si | Recomendado | Si, antes de uso estrategico |
| Analisis tipicidad preliminar | Si | Si | Si |
| Guion de audiencia | No | Si | Si |
| Memorial/recurso/solicitud | No | Si | Si (obligatorio) |
| Impulso por mora/inactividad | No | Si | Si (obligatorio) |
| Reporte a cliente | No | Si | Si |

---

## 7) Criterios de aprobacion sugeridos

- [ ] Los **10** roles representan funciones reales del despacho (sin evaluador de tutela).
- [ ] El pack de uso diario es suficiente para carga operativa semanal.
- [ ] Los flujos respetan practica procesal Ley 906.
- [ ] El esquema HITL preserva responsabilidad profesional.
- [ ] No hay riesgo de salida externa automatica sin revision humana.

---

## 8) Recomendacion

Se recomienda aprobar bajo modalidad **"piloto controlado con gobernanza juridica estricta"**:

1. revision semanal de calidad de salidas,
2. seguimiento de incidentes de alucinacion (meta tendencia a 0),
3. validacion humana obligatoria para toda salida externa.
