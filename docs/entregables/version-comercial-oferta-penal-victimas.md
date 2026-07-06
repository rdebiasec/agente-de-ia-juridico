# Version comercial para presentacion a firmas

![DBX Solutions](../assets/dbx-logo.png)

**Oferta:** Firma virtual penal-victimas con control humano  
**Dirigido a:** Socias/os de firma, direccion juridica y desarrollo de negocio  
**Fecha:** 2026-07-01

---

## 1) Propuesta comercial en una frase

DBX no vende un chatbot generico: vende una **capacidad operativa de litigio penal-victimas** que reduce tiempo de produccion juridica, mantiene control profesional y deja trazabilidad auditable.

---

## 2) Problema de negocio que resuelve

En firmas que representan victimas, la presion operativa suele concentrarse en:

- organizacion de hechos y pruebas bajo tiempos cortos,
- redaccion repetitiva de piezas procesales,
- preparacion de audiencia con informacion fragmentada,
- seguimiento de actuaciones y terminos,
- riesgo reputacional por respuestas IA sin control juridico.

Resultado de esa friccion: retrabajo, variabilidad de calidad y menor velocidad de respuesta al cliente.

---

## 3) Arquitectura comercializable (que compra la firma)

La oferta se estructura como una celula legal digital con 11 agentes especializados y revisiones humanas obligatorias:

1. Coordinacion del expediente.
2. Analisis factual, sustantivo y procesal.
3. Evidencia, audiencias y redaccion.
4. Seguimiento, constitucional y control de calidad.
5. Aprobacion final por abogado responsable.

---

## 4) Roles de agente y capacidades (skills) por valor comercial

## 4.1 Coordinacion y direccion del caso

### `coordinador_expediente_penal`
- **Valor para firma:** triage rapido y enrutamiento correcto desde la primera consulta.
- **Skills clave:** `clasificar_tarea_y_etapa`, `detectar_urgencia_penal`, `gestionar_faltantes_expediente`, `crear_ruta_procesal_recomendada`.

### `analista_calidad_juridica`
- **Valor para firma:** control de riesgo legal y reputacional antes de salida externa.
- **Skills clave:** `verificar_hechos_soportados`, `verificar_citas_normativas`, `detectar_alucinaciones_legales`, `clasificar_aprobacion_juridica`.

## 4.2 Eje analitico penal

### `analista_cronologia_hechos_penales`
- **Valor para firma:** hechos estructurados y verificables desde etapas tempranas.
- **Skills clave:** `extraer_hechos_relevantes`, `construir_cronologia_penal`, `detectar_contradicciones_factuales`.

### `analista_tipicidad_y_responsabilidad_penal`
- **Valor para firma:** preanalisis tecnico de hipotesis penales y riesgos.
- **Skills clave:** `identificar_conductas_punibles_preliminares`, `descomponer_elementos_tipo_penal`, `mapear_tipo_penal_hecho_prueba`.

### `analista_ruta_procesal_ley906`
- **Valor para firma:** decisiones procesales mas oportunas por etapa.
- **Skills clave:** `identificar_etapa_procesal_ley906`, `evaluar_oportunidad_procesal`, `detectar_riesgos_procesales`.

### `analista_representacion_victimas`
- **Valor para firma:** estrategia juridica centrada en derechos, reparacion y no revictimizacion.
- **Skills clave:** `identificar_intereses_victima`, `construir_teoria_caso_victima`, `detectar_riesgo_revictimizacion`.

## 4.3 Eje probatorio, audiencia y redaccion

### `gestor_evidencia_y_soporte_probatorio`
- **Valor para firma:** mejora del soporte probatorio y deteccion temprana de brechas.
- **Skills clave:** `inventariar_evidencia`, `detectar_brechas_probatorias`, `preservar_evidencia_digital`.

### `preparador_estrategico_audiencias_penales`
- **Valor para firma:** litigio oral mejor preparado y menos improvisacion.
- **Skills clave:** `identificar_objetivo_audiencia`, `preparar_guion_intervencion_oral`, `preparar_contraargumentos`.

### `redactor_documentos_juridicos_penales`
- **Valor para firma:** primera version de piezas procesales en menor tiempo.
- **Skills clave:** `redactar_memorial_penal`, `redactar_solicitud_impulso_procesal`, `estructurar_hechos_fundamentos_solicitudes`.

## 4.4 Eje de continuidad y constitucional

### `gestor_seguimiento_procesal_penal`
- **Valor para firma:** continuidad operativa de radicados, actuaciones y alertas.
- **Skills clave:** `monitorear_radicado`, `generar_alertas_terminos_vencimientos`, `crear_reporte_estado_caso`.

### `evaluador_derechos_fundamentales_tutela`
- **Valor para firma:** mejor filtro de procedencia y menor riesgo de improcedencia.
- **Skills clave:** `evaluar_procedencia_tutela`, `detectar_riesgo_improcedencia_tutela`, `recomendar_via_constitucional_o_alternativa`.

---

## 5) Guiones de conversacion para demo comercial

## Demo 1 - Intake a estrategia en menos de una reunion
**Prompt de demo:** "Organiza hechos de victima, identifica riesgos y propon ruta procesal inicial."

**Flujo visible al cliente:**
- coordinador clasifica,
- cronologia ordena hechos,
- ruta 906 define etapa,
- representacion de victimas propone objetivos,
- calidad marca riesgos y pendientes.

**Mensaje comercial:** "La firma pasa de relato disperso a hoja de ruta legal accionable en un solo flujo supervisado."

## Demo 2 - Audiencia preparada con checklist
**Prompt de demo:** "Tenemos audiencia preliminar; prepara guion y solicitudes."

**Flujo visible al cliente:**
- ruta 906 valida oportunidad,
- audiencias prepara intervencion,
- evidencia valida soporte,
- calidad revisa riesgos.

**Mensaje comercial:** "Menos improvisacion, mas consistencia de intervencion y mejor control de riesgo."

## Demo 3 - Memorial listo para revision
**Prompt de demo:** "Redacta memorial de impulso procesal con hechos, fundamentos y peticiones."

**Flujo visible al cliente:**
- redactor genera borrador,
- calidad verifica citas/hechos,
- abogada aprueba y ajusta.

**Mensaje comercial:** "La firma reduce tiempo de primera version sin ceder control profesional."

## Demo 4 - Filtro de tutela con alternativa
**Prompt de demo:** "Evalua procedencia de tutela por afectacion de debido proceso."

**Flujo visible al cliente:**
- evaluador tutela aplica test de procedencia,
- redactor prepara borrador si aplica,
- calidad clasifica aprobacion.

**Mensaje comercial:** "No se fuerza tutela; se recomienda la via juridicamente mas defendible."

---

## 6) ROI esperado para conversacion comercial

### KPIs sugeridos a 90 dias

- Tiempo a primera version juridicamente util: objetivo **-30% a -50%**.
- Tasa de retrabajo mayor: objetivo **<= 25%**.
- Incidentes por alucinacion legal: objetivo **tendencia a 0**.
- Adopcion interna semanal: objetivo **>= 70%**.

### Lectura comercial del ROI

- Si baja tiempo de produccion y retrabajo, mejora margen por asunto.
- Si sube adopcion y baja error factual, mejora estandar de calidad del despacho.
- Si hay trazabilidad y HITL robusto, disminuye objecion de riesgo en comites de compra.

---

## 7) Modelo de gobierno y cumplimiento (mensaje clave para cierre)

DBX se implementa bajo tres capas de control:

1. **Guardrails tecnicos:** no invencion de fuentes, separacion hecho/inferencia, control de datos sensibles.
2. **Guardrails operativos:** trazabilidad por turno y registro de decisiones.
3. **Guardrails profesionales:** aprobacion humana obligatoria antes de salida externa.

Este marco habilita una adopcion segura: productividad con control juridico, no automatizacion ciega.

---

## 8) Cierre comercial recomendado

Propuesta de siguiente paso:

- iniciar piloto controlado con casos reales acotados,
- medir KPIs de productividad/calidad/riesgo desde semana 1,
- presentar resultado ejecutivo de 30-60-90 para decision de escalamiento.

**Tesis final de venta:** capacidad operativa penal-victimas + control humano + evidencia de ROI.
