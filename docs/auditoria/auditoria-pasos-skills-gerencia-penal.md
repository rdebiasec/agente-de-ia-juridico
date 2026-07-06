# Auditoría gerencial de pasos por skill — Penal víctimas (Colombia) v2

**Generado:** 2026-07-05 21:17  
**Audiencia:** Gerencia del despacho y abogada líder  
**Fuente canónica:** `docs/canon/lista-aprobacion-agentes-skills-pasos.md` + `scripts/lib/pasos_gerencia_matrix.py`

---

## Resumen ejecutivo

- **Skills auditados:** 90
- **Pasos totales (catálogo al auditar):** 404
- **Pasos totales (propuesta gerencia v2):** 404
- **Δ pasos:** +0

### Distribución por cantidad de pasos (histograma)

| Pasos/skill | Antes (n skills) | Propuesta v2 (n skills) |
|---:|---:|---:|
| 2 | 4 | 4 |
| 3 | 7 | 7 |
| 4 | 49 | 49 |
| 5 | 16 | 16 |
| 6 | 6 | 6 |
| 7 | 4 | 4 |
| 8 | 2 | 2 |
| 9 | 1 | 1 |
| 10 | 1 | 1 |

- **Tallas distintas en propuesta:** 9 (mín. 2, sin tope fijo)
- **Skill con más pasos:** `redactar_tutela_penal_preliminar`

- **Skills que suben pasos:** 0 · **bajan:** 0 · **igual:** 90

---

## Fase 1 — Matriz de 90 skills (con reasoning gerencial)

### Skills transversales

#### `clasificar_tarea_y_etapa`

- **Categoría:** Skills transversales
- **Agentes:** `coordinador_expediente_penal`, `analista_ruta_procesal_ley906`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Clasificar la solicitud del usuario interno y detectar la etapa aparente del caso.
- **Purpose (SKILL.md):** clasificar la solicitud del usuario interno y detectar la etapa aparente del caso.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.78
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Clasificar la solicitud del usuario interno y detectar la etapa aparente del caso.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Analizar solicitud del usuario y objetivo del turno.
  2. Clasificar tipo de tarea y etapa procesal aparente del caso.
  3. Derivar al agente especialista correcto o pedir datos faltantes.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Analizar solicitud del usuario y objetivo del turno.
  2. Clasificar tipo de tarea y etapa procesal aparente del caso.
  3. Derivar al agente especialista correcto o pedir datos faltantes.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `detectar_urgencia_penal`

- **Categoría:** Skills transversales
- **Agentes:** `coordinador_expediente_penal`, `gestor_seguimiento_procesal_penal`, `analista_calidad_juridica`
- **Prioridad:** P2
- **Tier gerencial:** `estrategico`
- **Instrucción tipo:** Identificar si el caso requiere atencion humana inmediata.
- **Purpose (SKILL.md):** identificar si el caso requiere atencion humana inmediata.
- **Pasos:** 5 → **5** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 1.00
- **Reasoning gerencial:** Gerencia penal-víctimas: skill estratégico («Identificar si el caso requiere atencion humana inmediata.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 5 pasos:** 5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Evaluar indicios de riesgo inminente (términos, libertad, integridad, evidencia).
  2. Clasificar nivel de urgencia y necesidad de atención humana inmediata.
  3. Escalar con notificación si aplica.
  4. Profundizar análisis de «Identificar si el caso requiere atencion humana inmediata» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Evaluar indicios de riesgo inminente (términos, libertad, integridad, evidencia).
  2. Clasificar nivel de urgencia y necesidad de atención humana inmediata.
  3. Escalar con notificación si aplica.
  4. Profundizar análisis de «Identificar si el caso requiere atencion humana inmediata» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `gestionar_faltantes_expediente`

- **Categoría:** Skills transversales
- **Agentes:** `coordinador_expediente_penal`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Identificar datos y documentos faltantes antes de analizar o redactar.
- **Purpose (SKILL.md):** identificar datos y documentos faltantes antes de analizar o redactar.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.57
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Identificar datos y documentos faltantes antes de analizar o redactar.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Inventariar datos y documentos mínimos para el análisis solicitado.
  2. Listar faltantes por prioridad (bloqueante vs deseable).
  3. Solicitar al abogado completar antes de concluir.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Inventariar datos y documentos mínimos para el análisis solicitado.
  2. Listar faltantes por prioridad (bloqueante vs deseable).
  3. Solicitar al abogado completar antes de concluir.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `marcar_pendientes_verificacion`

- **Categoría:** Skills transversales
- **Agentes:** `coordinador_expediente_penal`
- **Prioridad:** P0
- **Tier gerencial:** `atomico`
- **Instrucción tipo:** Marcar cualquier dato, cita o hecho incompleto como `[PENDIENTE DE VERIFICAR]`.
- **Purpose (SKILL.md):** marcar cualquier dato, cita o hecho incompleto como `[PENDIENTE DE VERIFICAR]`.
- **Pasos:** 2 → **2** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.67
- **Reasoning gerencial:** Gerencia penal-víctimas: skill atómico («Marcar cualquier dato, cita o hecho incompleto como `[PENDIENTE DE VERIFICAR]`.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 2 pasos:** 2 pasos (1 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Recorrer salida e insertar `[PENDIENTE DE VERIFICAR]` en cada dato, cita o hecho sin fuente.
  2. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Recorrer salida e insertar `[PENDIENTE DE VERIFICAR]` en cada dato, cita o hecho sin fuente.
  2. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `verificar_hechos_soportados`

- **Categoría:** Skills transversales
- **Agentes:** `analista_calidad_juridica`, `redactor_documentos_juridicos_penales`, `analista_cronologia_hechos_penales`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Revisar si cada afirmacion factual tiene fuente.
- **Purpose (SKILL.md):** revisar si cada afirmacion factual tiene fuente.
- **Pasos:** 3 → **3** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.33
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Revisar si cada afirmacion factual tiene fuente.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 3 pasos:** 3 pasos (2 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Listar afirmaciones factuales en el texto o análisis.
  2. Cruzar cada afirmación con fuente documental o expediente.
  3. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Listar afirmaciones factuales en el texto o análisis.
  2. Cruzar cada afirmación con fuente documental o expediente.
  3. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

### Skills de hechos y cronologia

#### `clasificar_fuente_factual`

- **Categoría:** Skills de hechos y cronologia
- **Agentes:** `coordinador_expediente_penal`
- **Prioridad:** P0
- **Tier gerencial:** `estrategico`
- **Instrucción tipo:** Distinguir documento, relato de victima, relato de tercero, autoridad, inferencia o dato pendiente.
- **Purpose (SKILL.md):** distinguir documento, relato de victima, relato de tercero, autoridad, inferencia o dato pendiente.
- **Pasos:** 6 → **6** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.67
- **Reasoning gerencial:** Gerencia penal-víctimas: skill estratégico («Distinguir documento, relato de victima, relato de tercero, autoridad, inferencia o dato pendiente.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 6 pasos:** 6 pasos (5 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Inventariar cada afirmación factual en los insumos del turno.
  2. Clasificar fuente: documento, relato víctima, tercero, autoridad, inferencia o pendiente.
  3. Asignar nivel de soporte sin mezclar hecho confirmado, narrado e inferido.
  4. Construir matriz hecho-fuente preliminar (no cronología completa).
  5. Señalar afirmaciones sin fuente para verificación humana.
  6. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Inventariar cada afirmación factual en los insumos del turno.
  2. Clasificar fuente: documento, relato víctima, tercero, autoridad, inferencia o pendiente.
  3. Asignar nivel de soporte sin mezclar hecho confirmado, narrado e inferido.
  4. Construir matriz hecho-fuente preliminar (no cronología completa).
  5. Señalar afirmaciones sin fuente para verificación humana.
  6. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `construir_cronologia_penal`

- **Categoría:** Skills de hechos y cronologia
- **Agentes:** `analista_cronologia_hechos_penales`, `preparador_estrategico_audiencias_penales`
- **Prioridad:** P2
- **Tier gerencial:** `estrategico`
- **Instrucción tipo:** Ordenar hechos en linea de tiempo.
- **Purpose (SKILL.md):** ordenar hechos en linea de tiempo.
- **Pasos:** 5 → **5** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 1.00
- **Reasoning gerencial:** Gerencia penal-víctimas: skill estratégico («Ordenar hechos en linea de tiempo.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 5 pasos:** 5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Extraer hechos con fecha, hora y actores de fuentes verificadas.
  2. Ordenar línea de tiempo y señalar eventos sin fecha exacta.
  3. Marcar inconsistencias entre versiones.
  4. Profundizar análisis de «Ordenar hechos en linea de tiempo» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Extraer hechos con fecha, hora y actores de fuentes verificadas.
  2. Ordenar línea de tiempo y señalar eventos sin fecha exacta.
  3. Marcar inconsistencias entre versiones.
  4. Profundizar análisis de «Ordenar hechos en linea de tiempo» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `crear_matriz_hecho_fuente`

- **Categoría:** Skills de hechos y cronologia
- **Agentes:** `analista_cronologia_hechos_penales`, `analista_calidad_juridica`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Relacionar cada hecho con su fuente exacta.
- **Purpose (SKILL.md):** relacionar cada hecho con su fuente exacta.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.83
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Relacionar cada hecho con su fuente exacta.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Listar hechos relevantes uno a uno.
  2. Vincular cada hecho con fuente exacta (documento, folio, timestamp).
  3. Señalar hechos sin fuente como pendientes.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Listar hechos relevantes uno a uno.
  2. Vincular cada hecho con fuente exacta (documento, folio, timestamp).
  3. Señalar hechos sin fuente como pendientes.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `detectar_contradicciones_factuales`

- **Categoría:** Skills de hechos y cronologia
- **Agentes:** `analista_cronologia_hechos_penales`, `analista_calidad_juridica`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Encontrar inconsistencias entre versiones, documentos, fechas, valores o actores.
- **Purpose (SKILL.md):** encontrar inconsistencias entre versiones, documentos, fechas, valores o actores.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.25
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Encontrar inconsistencias entre versiones, documentos, fechas, valores o actores.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Comparar versiones de víctima, testigos, documentos y autoridades.
  2. Documentar contradicciones por hecho, fecha, monto o actor.
  3. Sugerir preguntas de aclaración no inductivas.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Comparar versiones de víctima, testigos, documentos y autoridades.
  2. Documentar contradicciones por hecho, fecha, monto o actor.
  3. Sugerir preguntas de aclaración no inductivas.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `detectar_vacios_factuales`

- **Categoría:** Skills de hechos y cronologia
- **Agentes:** `analista_cronologia_hechos_penales`, `coordinador_expediente_penal`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Identificar lo que falta para comprender o probar el caso.
- **Purpose (SKILL.md):** identificar lo que falta para comprender o probar el caso.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.57
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Identificar lo que falta para comprender o probar el caso.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Identificar información faltante para comprender el caso o sostener actuación.
  2. Priorizar vacíos por impacto en tipicidad, prueba o oportunidad procesal.
  3. Formular solicitud de datos al abogado o cliente.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Identificar información faltante para comprender el caso o sostener actuación.
  2. Priorizar vacíos por impacto en tipicidad, prueba o oportunidad procesal.
  3. Formular solicitud de datos al abogado o cliente.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `extraer_hechos_relevantes`

- **Categoría:** Skills de hechos y cronologia
- **Agentes:** `analista_cronologia_hechos_penales`, `redactor_documentos_juridicos_penales`, `gestor_evidencia_y_soporte_probatorio`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Extraer hechos relevantes de documentos, relatos, audios o comunicaciones.
- **Purpose (SKILL.md):** extraer hechos relevantes de documentos, relatos, audios o comunicaciones.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.71
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Extraer hechos relevantes de documentos, relatos, audios o comunicaciones.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Procesar documentos, relatos, audios o mensajes del expediente.
  2. Extraer hechos materiales con referencia de fuente.
  3. Filtrar opiniones e inferencias no soportadas.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Procesar documentos, relatos, audios o mensajes del expediente.
  2. Extraer hechos materiales con referencia de fuente.
  3. Filtrar opiniones e inferencias no soportadas.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `generar_preguntas_aclaracion`

- **Categoría:** Skills de hechos y cronologia
- **Agentes:** `analista_cronologia_hechos_penales`, `gestor_evidencia_y_soporte_probatorio`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Crear preguntas para victima, testigos o abogado humano sin inducir respuestas.
- **Purpose (SKILL.md):** crear preguntas para victima, testigos o abogado humano sin inducir respuestas.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.40
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Crear preguntas para victima, testigos o abogado humano sin inducir respuestas.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Identificar puntos ambiguos o incompletos en la narrativa.
  2. Redactar preguntas abiertas y no inductivas para víctima, testigos o abogado.
  3. Ordenar preguntas por prioridad probatoria.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Identificar puntos ambiguos o incompletos en la narrativa.
  2. Redactar preguntas abiertas y no inductivas para víctima, testigos o abogado.
  3. Ordenar preguntas por prioridad probatoria.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `identificar_actores_y_roles`

- **Categoría:** Skills de hechos y cronologia
- **Agentes:** `analista_cronologia_hechos_penales`, `analista_representacion_victimas`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Identificar victima, presunto responsable, testigos, autoridades, terceros y entidades.
- **Purpose (SKILL.md):** identificar victima, presunto responsable, testigos, autoridades, terceros y entidades.
- **Pasos:** 3 → **3** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.12
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Identificar victima, presunto responsable, testigos, autoridades, terceros y entidades.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 3 pasos:** 3 pasos (2 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Extraer personas y entidades mencionadas en las fuentes.
  2. Asignar rol procesal preliminar (víctima, imputado, testigo, autoridad, tercero).
  3. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Extraer personas y entidades mencionadas en las fuentes.
  2. Asignar rol procesal preliminar (víctima, imputado, testigo, autoridad, tercero).
  3. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

### Skills de tipicidad y responsabilidad penal

#### `analizar_autoria_y_participacion`

- **Categoría:** Skills de tipicidad y responsabilidad penal
- **Agentes:** `analista_tipicidad_y_responsabilidad_penal`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Evaluar posibles roles de los intervinientes de manera preliminar.
- **Purpose (SKILL.md):** evaluar posibles roles de los intervinientes de manera preliminar.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.29
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Evaluar posibles roles de los intervinientes de manera preliminar.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Identificar posibles autores, coautores y partícipes según hechos.
  2. Evaluar preliminarmente conductas de cada interviniente.
  3. Señalar vacíos probatorios en autoria/participación.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Identificar posibles autores, coautores y partícipes según hechos.
  2. Evaluar preliminarmente conductas de cada interviniente.
  3. Señalar vacíos probatorios en autoria/participación.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `analizar_dolo_culpa_elemento_subjetivo`

- **Categoría:** Skills de tipicidad y responsabilidad penal
- **Agentes:** `analista_tipicidad_y_responsabilidad_penal`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Identificar hechos que podrian soportar dolo, culpa u otro elemento subjetivo.
- **Purpose (SKILL.md):** identificar hechos que podrian soportar dolo, culpa u otro elemento subjetivo.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.50
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Identificar hechos que podrian soportar dolo, culpa u otro elemento subjetivo.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Analizar elementos subjetivos (dolo, culpa) según hechos narrados.
  2. Distinguir intención, conocimiento y negligencia preliminarmente.
  3. No afirmar elemento subjetivo sin soporte suficiente.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Analizar elementos subjetivos (dolo, culpa) según hechos narrados.
  2. Distinguir intención, conocimiento y negligencia preliminarmente.
  3. No afirmar elemento subjetivo sin soporte suficiente.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `descomponer_elementos_tipo_penal`

- **Categoría:** Skills de tipicidad y responsabilidad penal
- **Agentes:** `analista_tipicidad_y_responsabilidad_penal`
- **Prioridad:** P2
- **Tier gerencial:** `estrategico`
- **Instrucción tipo:** Dividir un posible delito en elementos juridicos verificables.
- **Purpose (SKILL.md):** dividir un posible delito en elementos juridicos verificables.
- **Pasos:** 6 → **6** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 1.00
- **Reasoning gerencial:** Gerencia penal-víctimas: skill estratégico («Dividir un posible delito en elementos juridicos verificables.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 6 pasos:** 6 pasos (5 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Seleccionar tipos penales hipotéticos aplicables.
  2. Descomponer conducta, resultado, nexo y elementos normativos.
  3. Documentar dudas de tipicidad.
  4. Profundizar análisis de «Dividir un posible delito en elementos juridicos verificables» con referencia al expediente y norma aplicable.
  5. Profundizar análisis de «Dividir un posible delito en elementos juridicos verificables» con referencia al expediente y norma aplicable.
  6. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Seleccionar tipos penales hipotéticos aplicables.
  2. Descomponer conducta, resultado, nexo y elementos normativos.
  3. Documentar dudas de tipicidad.
  4. Profundizar análisis de «Dividir un posible delito en elementos juridicos verificables» con referencia al expediente y norma aplicable.
  5. Profundizar análisis de «Dividir un posible delito en elementos juridicos verificables» con referencia al expediente y norma aplicable.
  6. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `detectar_agravantes_atenuantes`

- **Categoría:** Skills de tipicidad y responsabilidad penal
- **Agentes:** `analista_tipicidad_y_responsabilidad_penal`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Identificar circunstancias relevantes que puedan afectar gravedad juridica.
- **Purpose (SKILL.md):** identificar circunstancias relevantes que puedan afectar gravedad juridica.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.12
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Identificar circunstancias relevantes que puedan afectar gravedad juridica.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Revisar hechos que configuren agravantes o atenuantes aplicables.
  2. Vincular con norma penal y prueba disponible.
  3. Marcar elementos no acreditados como pendientes.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Revisar hechos que configuren agravantes o atenuantes aplicables.
  2. Vincular con norma penal y prueba disponible.
  3. Marcar elementos no acreditados como pendientes.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `detectar_riesgos_atipicidad`

- **Categoría:** Skills de tipicidad y responsabilidad penal
- **Agentes:** `analista_tipicidad_y_responsabilidad_penal`, `analista_calidad_juridica`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Detectar cuando un caso puede ser atipico o tener naturaleza no penal.
- **Purpose (SKILL.md):** detectar cuando un caso puede ser atipico o tener naturaleza no penal.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.00
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Detectar cuando un caso puede ser atipico o tener naturaleza no penal.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Evaluar si faltan elementos objetivos o subjetivos del tipo.
  2. Identificar conductas alternativas más ajustadas.
  3. Alertar riesgo de atipicidad antes de actuación.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Evaluar si faltan elementos objetivos o subjetivos del tipo.
  2. Identificar conductas alternativas más ajustadas.
  3. Alertar riesgo de atipicidad antes de actuación.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `generar_preguntas_tipicidad`

- **Categoría:** Skills de tipicidad y responsabilidad penal
- **Agentes:** `analista_tipicidad_y_responsabilidad_penal`, `analista_cronologia_hechos_penales`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Crear preguntas para completar elementos del tipo penal.
- **Purpose (SKILL.md):** crear preguntas para completar elementos del tipo penal.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.75
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Crear preguntas para completar elementos del tipo penal.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Identificar vacíos en elementos del tipo penal.
  2. Formular preguntas para víctima, testigos o abogado.
  3. Evitar preguntas que presupongan culpabilidad.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Identificar vacíos en elementos del tipo penal.
  2. Formular preguntas para víctima, testigos o abogado.
  3. Evitar preguntas que presupongan culpabilidad.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `identificar_conductas_punibles_preliminares`

- **Categoría:** Skills de tipicidad y responsabilidad penal
- **Agentes:** `analista_tipicidad_y_responsabilidad_penal`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Proponer posibles conductas punibles con base en hechos, sin conclusion definitiva.
- **Purpose (SKILL.md):** proponer posibles conductas punibles con base en hechos, sin conclusion definitiva.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.10
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Proponer posibles conductas punibles con base en hechos, sin conclusion definitiva.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Mapear conductas descritas contra tipos penales del catálogo.
  2. Priorizar hipótesis más sólidas y descartar atipicidad evidente.
  3. Presentar como hipótesis, no conclusión.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Mapear conductas descritas contra tipos penales del catálogo.
  2. Priorizar hipótesis más sólidas y descartar atipicidad evidente.
  3. Presentar como hipótesis, no conclusión.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `mapear_tipo_penal_hecho_prueba`

- **Categoría:** Skills de tipicidad y responsabilidad penal
- **Agentes:** `analista_tipicidad_y_responsabilidad_penal`, `gestor_evidencia_y_soporte_probatorio`, `analista_calidad_juridica`
- **Prioridad:** P2
- **Tier gerencial:** `estrategico`
- **Instrucción tipo:** Relacionar elementos del tipo con hechos y pruebas.
- **Purpose (SKILL.md):** relacionar elementos del tipo con hechos y pruebas.
- **Pasos:** 5 → **5** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 1.00
- **Reasoning gerencial:** Gerencia penal-víctimas: skill estratégico («Relacionar elementos del tipo con hechos y pruebas.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 5 pasos:** 5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Relacionar cada elemento del tipo con hechos y pruebas.
  2. Visualizar fortalezas y debilidades por elemento.
  3. Proponer recaudo orientado a elementos débiles.
  4. Profundizar análisis de «Relacionar elementos del tipo con hechos y pruebas» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Relacionar cada elemento del tipo con hechos y pruebas.
  2. Visualizar fortalezas y debilidades por elemento.
  3. Proponer recaudo orientado a elementos débiles.
  4. Profundizar análisis de «Relacionar elementos del tipo con hechos y pruebas» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

### Skills de ruta procesal Ley 906

#### `analizar_intervencion_victima`

- **Categoría:** Skills de ruta procesal Ley 906
- **Agentes:** `analista_ruta_procesal_ley906`, `preparador_estrategico_audiencias_penales`
- **Prioridad:** P2
- **Tier gerencial:** `estrategico`
- **Instrucción tipo:** Definir intervencion posible de la victima en una actuacion o audiencia.
- **Purpose (SKILL.md):** definir intervencion posible de la victima en una actuacion o audiencia.
- **Pasos:** 5 → **5** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 1.00
- **Reasoning gerencial:** Gerencia penal-víctimas: skill estratégico («Definir intervencion posible de la victima en una actuacion o audiencia.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 5 pasos:** 5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Identificar actuación o audiencia específica y marco Ley 906.
  2. Determinar formas de intervención de la víctima procedentes.
  3. Proponer contenido y momento de la intervención.
  4. Profundizar análisis de «Definir intervencion posible de la victima en una actuacion o audiencia» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Identificar actuación o audiencia específica y marco Ley 906.
  2. Determinar formas de intervención de la víctima procedentes.
  3. Proponer contenido y momento de la intervención.
  4. Profundizar análisis de «Definir intervencion posible de la victima en una actuacion o audiencia» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `controlar_terminos_procesales_preliminares`

- **Categoría:** Skills de ruta procesal Ley 906
- **Agentes:** `analista_ruta_procesal_ley906`, `gestor_seguimiento_procesal_penal`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Identificar y alertar terminos relevantes. No reemplaza calculo humano.
- **Purpose (SKILL.md):** identificar y alertar terminos relevantes. No reemplaza calculo humano.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.29
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Identificar y alertar terminos relevantes. No reemplaza calculo humano.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Identificar términos relevantes según etapa y actuación pendiente.
  2. Calcular o estimar fechas límite con advertencia de verificación humana.
  3. Generar alertas con acción recomendada.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Identificar términos relevantes según etapa y actuación pendiente.
  2. Calcular o estimar fechas límite con advertencia de verificación humana.
  3. Generar alertas con acción recomendada.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `crear_ruta_procesal_recomendada`

- **Categoría:** Skills de ruta procesal Ley 906
- **Agentes:** `analista_ruta_procesal_ley906`, `coordinador_expediente_penal`
- **Prioridad:** P2
- **Tier gerencial:** `estrategico`
- **Instrucción tipo:** Crear plan de proximos pasos procesales para revision del abogado.
- **Purpose (SKILL.md):** crear plan de proximos pasos procesales para revision del abogado.
- **Pasos:** 5 → **5** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 1.00
- **Reasoning gerencial:** Gerencia penal-víctimas: skill estratégico («Crear plan de proximos pasos procesales para revision del abogado.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 5 pasos:** 5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Sintetizar etapa actual y actuaciones pendientes.
  2. Proponer secuencia de próximos pasos con responsables y plazos.
  3. Incluir riesgos procesales de la ruta propuesta.
  4. Profundizar análisis de «Crear plan de proximos pasos procesales para revision del abogado» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Sintetizar etapa actual y actuaciones pendientes.
  2. Proponer secuencia de próximos pasos con responsables y plazos.
  3. Incluir riesgos procesales de la ruta propuesta.
  4. Profundizar análisis de «Crear plan de proximos pasos procesales para revision del abogado» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `detectar_riesgos_procesales`

- **Categoría:** Skills de ruta procesal Ley 906
- **Agentes:** `analista_ruta_procesal_ley906`, `analista_calidad_juridica`
- **Prioridad:** P2
- **Tier gerencial:** `estrategico`
- **Instrucción tipo:** Detectar riesgos de oportunidad, legitimacion, competencia, improcedencia o perdida de derechos.
- **Purpose (SKILL.md):** detectar riesgos de oportunidad, legitimacion, competencia, improcedencia o perdida de derechos.
- **Pasos:** 5 → **5** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 1.00
- **Reasoning gerencial:** Gerencia penal-víctimas: skill estratégico («Detectar riesgos de oportunidad, legitimacion, competencia, improcedencia o perdida de derechos.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 5 pasos:** 5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Revisar oportunidad, legitimación, competencia e improcedencia.
  2. Documentar riesgos de pérdida de derechos o extemporaneidad.
  3. Priorizar riesgos críticos para decisión inmediata.
  4. Profundizar análisis de «Detectar riesgos de oportunidad, legitimacion, competencia, improcedencia o perdida de derechos» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Revisar oportunidad, legitimación, competencia e improcedencia.
  2. Documentar riesgos de pérdida de derechos o extemporaneidad.
  3. Priorizar riesgos críticos para decisión inmediata.
  4. Profundizar análisis de «Detectar riesgos de oportunidad, legitimacion, competencia, improcedencia o perdida de derechos» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `evaluar_oportunidad_procesal`

- **Categoría:** Skills de ruta procesal Ley 906
- **Agentes:** `analista_ruta_procesal_ley906`, `analista_calidad_juridica`
- **Prioridad:** P1
- **Tier gerencial:** `critico`
- **Instrucción tipo:** Determinar si una solicitud o intervencion es oportuna, prematura o extemporanea.
- **Purpose (SKILL.md):** determinar si una solicitud o intervencion es oportuna, prematura o extemporanea.
- **Pasos:** 7 → **7** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.43
- **Reasoning gerencial:** Gerencia penal-víctimas: skill crítico («Determinar si una solicitud o intervencion es oportuna, prematura o extemporanea.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 7 pasos:** 7 pasos (6 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Ubicar la actuación propuesta en la etapa exacta del proceso penal.
  2. Verificar plazos y términos aplicables con advertencia de cálculo humano.
  3. Contrastar con actuaciones previas y estado del radicado.
  4. Determinar si es oportuna, prematura o extemporánea para la víctima.
  5. Evaluar consecuencias de actuar o no actuar en este momento.
  6. Sugerir fecha o actuación alternativa si no es oportuna.
  7. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Ubicar la actuación propuesta en la etapa exacta del proceso penal.
  2. Verificar plazos y términos aplicables con advertencia de cálculo humano.
  3. Contrastar con actuaciones previas y estado del radicado.
  4. Determinar si es oportuna, prematura o extemporánea para la víctima.
  5. Evaluar consecuencias de actuar o no actuar en este momento.
  6. Sugerir fecha o actuación alternativa si no es oportuna.
  7. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `evaluar_solicitud_fiscalia_juez`

- **Categoría:** Skills de ruta procesal Ley 906
- **Agentes:** `analista_ruta_procesal_ley906`, `redactor_documentos_juridicos_penales`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Evaluar si una solicitud a Fiscalia o juez es procedente y conveniente.
- **Purpose (SKILL.md):** evaluar si una solicitud a Fiscalia o juez es procedente y conveniente.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.43
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Evaluar si una solicitud a Fiscalia o juez es procedente y conveniente.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Verificar procedencia formal de la solicitud a Fiscalía o juez.
  2. Evaluar conveniencia estratégica para la víctima.
  3. Listar requisitos y anexos necesarios.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Verificar procedencia formal de la solicitud a Fiscalía o juez.
  2. Evaluar conveniencia estratégica para la víctima.
  3. Listar requisitos y anexos necesarios.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `identificar_etapa_procesal_ley906`

- **Categoría:** Skills de ruta procesal Ley 906
- **Agentes:** `analista_ruta_procesal_ley906`, `coordinador_expediente_penal`
- **Prioridad:** P1
- **Tier gerencial:** `estrategico`
- **Instrucción tipo:** Determinar etapa del caso.
- **Purpose (SKILL.md):** determinar etapa del caso.
- **Pasos:** 6 → **6** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 1.00
- **Reasoning gerencial:** Gerencia penal-víctimas: skill estratégico («Determinar etapa del caso.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 6 pasos:** 6 pasos (5 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Revisar actuaciones y estado del radicado.
  2. Determinar etapa procesal según Ley 906 (indagación, investigación, juicio, etc.).
  3. Señalar incertidumbres si el expediente es incompleto.
  4. Profundizar análisis de «Determinar etapa del caso» con referencia al expediente y norma aplicable.
  5. Profundizar análisis de «Determinar etapa del caso» con referencia al expediente y norma aplicable.
  6. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Revisar actuaciones y estado del radicado.
  2. Determinar etapa procesal según Ley 906 (indagación, investigación, juicio, etc.).
  3. Señalar incertidumbres si el expediente es incompleto.
  4. Profundizar análisis de «Determinar etapa del caso» con referencia al expediente y norma aplicable.
  5. Profundizar análisis de «Determinar etapa del caso» con referencia al expediente y norma aplicable.
  6. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `mapear_actuaciones_posibles_victima`

- **Categoría:** Skills de ruta procesal Ley 906
- **Agentes:** `analista_ruta_procesal_ley906`, `analista_representacion_victimas`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Indicar que puede hacer la representacion de victimas segun etapa.
- **Purpose (SKILL.md):** indicar que puede hacer la representacion de victimas segun etapa.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.50
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Indicar que puede hacer la representacion de victimas segun etapa.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Listar actuaciones que la representación de víctimas puede promover en la etapa actual.
  2. Indicar requisitos, oportunidad y efectos esperados de cada una.
  3. Priorizar según intereses de la víctima.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Listar actuaciones que la representación de víctimas puede promover en la etapa actual.
  2. Indicar requisitos, oportunidad y efectos esperados de cada una.
  3. Priorizar según intereses de la víctima.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

### Skills de representacion de victimas

#### `alinear_estrategia_prueba_proceso`

- **Categoría:** Skills de representacion de victimas
- **Agentes:** `analista_representacion_victimas`, `analista_calidad_juridica`
- **Prioridad:** P2
- **Tier gerencial:** `estrategico`
- **Instrucción tipo:** Alinear teoria de victima con ruta procesal y plan probatorio.
- **Purpose (SKILL.md):** alinear teoria de victima con ruta procesal y plan probatorio.
- **Pasos:** 5 → **5** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 1.00
- **Reasoning gerencial:** Gerencia penal-víctimas: skill estratégico («Alinear teoria de victima con ruta procesal y plan probatorio.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 5 pasos:** 5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Contrastar teoría del caso con etapa procesal y prueba disponible.
  2. Detectar desalineaciones entre ruta 906 y plan probatorio.
  3. Proponer ajustes coordinados para representación de la víctima.
  4. Profundizar análisis de «Alinear teoria de victima con ruta procesal y plan probatorio» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Contrastar teoría del caso con etapa procesal y prueba disponible.
  2. Detectar desalineaciones entre ruta 906 y plan probatorio.
  3. Proponer ajustes coordinados para representación de la víctima.
  4. Profundizar análisis de «Alinear teoria de victima con ruta procesal y plan probatorio» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `analizar_derechos_victima`

- **Categoría:** Skills de representacion de victimas
- **Agentes:** `analista_representacion_victimas`, `evaluador_derechos_fundamentales_tutela`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Mapear derechos de victima aplicables al caso.
- **Purpose (SKILL.md):** mapear derechos de victima aplicables al caso.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.60
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Mapear derechos de victima aplicables al caso.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Mapear derechos de participación, información, reparación y protección aplicables.
  2. Relacionar derechos con hechos y etapa del proceso.
  3. Priorizar derechos más vulnerados o urgentes.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Mapear derechos de participación, información, reparación y protección aplicables.
  2. Relacionar derechos con hechos y etapa del proceso.
  3. Priorizar derechos más vulnerados o urgentes.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `analizar_enfoque_diferencial`

- **Categoría:** Skills de representacion de victimas
- **Agentes:** `analista_representacion_victimas`, `evaluador_derechos_fundamentales_tutela`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Identificar sujetos de especial proteccion y necesidades diferenciadas.
- **Purpose (SKILL.md):** identificar sujetos de especial proteccion y necesidades diferenciadas.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.67
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Identificar sujetos de especial proteccion y necesidades diferenciadas.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Identificar factores de especial protección (género, edad, discapacidad, etnia, etc.).
  2. Ajustar recomendaciones a necesidades diferenciadas de la víctima.
  3. Evitar estereotipos y proteger datos sensibles.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Identificar factores de especial protección (género, edad, discapacidad, etnia, etc.).
  2. Ajustar recomendaciones a necesidades diferenciadas de la víctima.
  3. Evitar estereotipos y proteger datos sensibles.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `construir_teoria_caso_victima`

- **Categoría:** Skills de representacion de victimas
- **Agentes:** `analista_representacion_victimas`, `preparador_estrategico_audiencias_penales`
- **Prioridad:** P2
- **Tier gerencial:** `critico`
- **Instrucción tipo:** Formular teoria preliminar desde la victima.
- **Purpose (SKILL.md):** formular teoria preliminar desde la victima.
- **Pasos:** 7 → **7** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.20
- **Reasoning gerencial:** Gerencia penal-víctimas: skill crítico («Formular teoria preliminar desde la victima.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 7 pasos:** 7 pasos (6 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Precisar intereses y objetivos de la víctima en el caso concreto.
  2. Sintetizar narrativa factual centrada en la víctima con fuentes.
  3. Vincular teoría con tipicidad preliminar y elementos del tipo.
  4. Integrar plan probatorio y actuaciones Ley 906 disponibles.
  5. Identificar fortalezas, debilidades y riesgos de la postura.
  6. Alinear con enfoque diferencial y no revictimización.
  7. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Precisar intereses y objetivos de la víctima en el caso concreto.
  2. Sintetizar narrativa factual centrada en la víctima con fuentes.
  3. Vincular teoría con tipicidad preliminar y elementos del tipo.
  4. Integrar plan probatorio y actuaciones Ley 906 disponibles.
  5. Identificar fortalezas, debilidades y riesgos de la postura.
  6. Alinear con enfoque diferencial y no revictimización.
  7. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `detectar_riesgo_revictimizacion`

- **Categoría:** Skills de representacion de victimas
- **Agentes:** `analista_representacion_victimas`, `preparador_estrategico_audiencias_penales`, `analista_calidad_juridica`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Identificar lenguaje, preguntas, acciones o estrategias que puedan revictimizar.
- **Purpose (SKILL.md):** identificar lenguaje, preguntas, acciones o estrategias que puedan revictimizar.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.62
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Identificar lenguaje, preguntas, acciones o estrategias que puedan revictimizar.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Analizar preguntas, estrategias y lenguaje propuestos.
  2. Identificar conductas o formulaciones que revictimicen.
  3. Proponer alternativas respetuosas y centradas en derechos.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Analizar preguntas, estrategias y lenguaje propuestos.
  2. Identificar conductas o formulaciones que revictimicen.
  3. Proponer alternativas respetuosas y centradas en derechos.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `evaluar_dano_y_afectacion`

- **Categoría:** Skills de representacion de victimas
- **Agentes:** `analista_representacion_victimas`, `gestor_evidencia_y_soporte_probatorio`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Organizar danos y afectaciones alegadas.
- **Purpose (SKILL.md):** organizar danos y afectaciones alegadas.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.75
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Organizar danos y afectaciones alegadas.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Organizar daños materiales, morales y afectaciones psicosociales alegadas.
  2. Vincular daño con prueba disponible o pendiente.
  3. Evitar minimizar o dramatizar sin soporte.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Organizar daños materiales, morales y afectaciones psicosociales alegadas.
  2. Vincular daño con prueba disponible o pendiente.
  3. Evitar minimizar o dramatizar sin soporte.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `identificar_intereses_victima`

- **Categoría:** Skills de representacion de victimas
- **Agentes:** `analista_representacion_victimas`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Aclarar el objetivo real de la victima.
- **Purpose (SKILL.md):** aclarar el objetivo real de la victima.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.25
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Aclarar el objetivo real de la victima.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Aclarar objetivos reales de la víctima (justicia, reparación, celeridad, protección).
  2. Distinguir intereses de la víctima de objetivos procesales técnicos.
  3. Priorizar intereses para decisiones estratégicas.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Aclarar objetivos reales de la víctima (justicia, reparación, celeridad, protección).
  2. Distinguir intereses de la víctima de objetivos procesales técnicos.
  3. Priorizar intereses para decisiones estratégicas.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `priorizar_objetivos_representacion`

- **Categoría:** Skills de representacion de victimas
- **Agentes:** `analista_representacion_victimas`, `coordinador_expediente_penal`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Ordenar objetivos de la representacion.
- **Purpose (SKILL.md):** ordenar objetivos de la representacion.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.67
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Ordenar objetivos de la representacion.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Listar objetivos posibles de la representación en el caso.
  2. Ordenar por urgencia, viabilidad y alineación con intereses de la víctima.
  3. Documentar trade-offs para decisión del abogado.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Listar objetivos posibles de la representación en el caso.
  2. Ordenar por urgencia, viabilidad y alineación con intereses de la víctima.
  3. Documentar trade-offs para decisión del abogado.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

### Skills de evidencia y soporte probatorio

#### `clasificar_tipo_prueba`

- **Categoría:** Skills de evidencia y soporte probatorio
- **Agentes:** `gestor_evidencia_y_soporte_probatorio`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Clasificar evidencia como documental, testimonial, digital, fisica, pericial, institucional o pendiente.
- **Purpose (SKILL.md):** clasificar evidencia como documental, testimonial, digital, fisica, pericial, institucional o pendiente.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.70
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Clasificar evidencia como documental, testimonial, digital, fisica, pericial, institucional o pendiente.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Inventariar elementos probatorios y clasificar por tipo (documental, testimonial, digital, pericial, etc.).
  2. Registrar origen, fecha y custodia preliminar de cada elemento.
  3. Señalar elementos sin clasificación definitiva como pendientes.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Inventariar elementos probatorios y clasificar por tipo (documental, testimonial, digital, pericial, etc.).
  2. Registrar origen, fecha y custodia preliminar de cada elemento.
  3. Señalar elementos sin clasificación definitiva como pendientes.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `construir_matriz_hecho_prueba`

- **Categoría:** Skills de evidencia y soporte probatorio
- **Agentes:** `gestor_evidencia_y_soporte_probatorio`, `analista_tipicidad_y_responsabilidad_penal`, `preparador_estrategico_audiencias_penales`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Relacionar hechos con pruebas existentes y faltantes.
- **Purpose (SKILL.md):** relacionar hechos con pruebas existentes y faltantes.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.33
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Relacionar hechos con pruebas existentes y faltantes.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Listar hechos relevantes para la teoría del caso.
  2. Vincular cada hecho con prueba existente, faltante o en trámite.
  3. Priorizar brechas que afecten tipicidad o audiencia.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Listar hechos relevantes para la teoría del caso.
  2. Vincular cada hecho con prueba existente, faltante o en trámite.
  3. Priorizar brechas que afecten tipicidad o audiencia.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `controlar_cadena_custodia_preliminar`

- **Categoría:** Skills de evidencia y soporte probatorio
- **Agentes:** `gestor_evidencia_y_soporte_probatorio`, `analista_calidad_juridica`
- **Prioridad:** P0
- **Tier gerencial:** `critico`
- **Instrucción tipo:** Alertar si la evidencia puede requerir cadena de custodia.
- **Purpose (SKILL.md):** alertar si la evidencia puede requerir cadena de custodia.
- **Pasos:** 7 → **7** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.67
- **Reasoning gerencial:** Gerencia penal-víctimas: skill crítico («Alertar si la evidencia puede requerir cadena de custodia.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 7 pasos:** 7 pasos (6 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Identificar evidencia que exija cadena de custodia formal.
  2. Revisar recolección: quién, cuándo, dónde y protocolo usado.
  3. Verificar traslado, almacenamiento y cadena de acceso documentada.
  4. Detectar rupturas o vacíos que afecten admisibilidad.
  5. Alertar necesidad de perito, cadena certificada u oficio urgente.
  6. Proponer medidas correctivas sin alterar el elemento probatorio.
  7. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Identificar evidencia que exija cadena de custodia formal.
  2. Revisar recolección: quién, cuándo, dónde y protocolo usado.
  3. Verificar traslado, almacenamiento y cadena de acceso documentada.
  4. Detectar rupturas o vacíos que afecten admisibilidad.
  5. Alertar necesidad de perito, cadena certificada u oficio urgente.
  6. Proponer medidas correctivas sin alterar el elemento probatorio.
  7. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `crear_plan_recaudo_probatorio`

- **Categoría:** Skills de evidencia y soporte probatorio
- **Agentes:** `gestor_evidencia_y_soporte_probatorio`, `analista_representacion_victimas`
- **Prioridad:** P2
- **Tier gerencial:** `estrategico`
- **Instrucción tipo:** Proponer plan para obtener pruebas faltantes.
- **Purpose (SKILL.md):** proponer plan para obtener pruebas faltantes.
- **Pasos:** 5 → **5** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 1.00
- **Reasoning gerencial:** Gerencia penal-víctimas: skill estratégico («Proponer plan para obtener pruebas faltantes.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 5 pasos:** 5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Listar pruebas faltantes críticas según matriz hecho-prueba.
  2. Asignar responsable, plazo y vía de obtención (oficio, solicitud, peritaje).
  3. Ordenar por impacto procesal y urgencia.
  4. Profundizar análisis de «Proponer plan para obtener pruebas faltantes» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Listar pruebas faltantes críticas según matriz hecho-prueba.
  2. Asignar responsable, plazo y vía de obtención (oficio, solicitud, peritaje).
  3. Ordenar por impacto procesal y urgencia.
  4. Profundizar análisis de «Proponer plan para obtener pruebas faltantes» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `detectar_brechas_probatorias`

- **Categoría:** Skills de evidencia y soporte probatorio
- **Agentes:** `gestor_evidencia_y_soporte_probatorio`, `analista_calidad_juridica`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Identificar hechos relevantes sin soporte suficiente.
- **Purpose (SKILL.md):** identificar hechos relevantes sin soporte suficiente.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.50
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Identificar hechos relevantes sin soporte suficiente.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Contrastar hechos relevantes con soporte probatorio disponible.
  2. Clasificar brechas por gravedad (crítica, media, baja).
  3. Proponer acciones de cierre de brecha.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Contrastar hechos relevantes con soporte probatorio disponible.
  2. Clasificar brechas por gravedad (crítica, media, baja).
  3. Proponer acciones de cierre de brecha.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `evaluar_suficiencia_probatoria`

- **Categoría:** Skills de evidencia y soporte probatorio
- **Agentes:** `gestor_evidencia_y_soporte_probatorio`, `analista_representacion_victimas`
- **Prioridad:** P2
- **Tier gerencial:** `estrategico`
- **Instrucción tipo:** Evaluar preliminarmente fuerza de soporte probatorio.
- **Purpose (SKILL.md):** evaluar preliminarmente fuerza de soporte probatorio.
- **Pasos:** 5 → **5** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 1.00
- **Reasoning gerencial:** Gerencia penal-víctimas: skill estratégico («Evaluar preliminarmente fuerza de soporte probatorio.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 5 pasos:** 5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Evaluar fuerza preliminar del soporte (directo, indirecto, circunstancial).
  2. Identificar elementos del tipo penal con soporte débil o ausente.
  3. Conclusión preliminar de suficiencia sin afirmar certeza judicial.
  4. Profundizar análisis de «Evaluar preliminarmente fuerza de soporte probatorio» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Evaluar fuerza preliminar del soporte (directo, indirecto, circunstancial).
  2. Identificar elementos del tipo penal con soporte débil o ausente.
  3. Conclusión preliminar de suficiencia sin afirmar certeza judicial.
  4. Profundizar análisis de «Evaluar preliminarmente fuerza de soporte probatorio» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `generar_preguntas_testigos_peritos`

- **Categoría:** Skills de evidencia y soporte probatorio
- **Agentes:** `gestor_evidencia_y_soporte_probatorio`, `preparador_estrategico_audiencias_penales`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Preparar preguntas neutrales para testigos o peritos.
- **Purpose (SKILL.md):** preparar preguntas neutrales para testigos o peritos.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.67
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Preparar preguntas neutrales para testigos o peritos.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Seleccionar testigos/peritos según hechos a esclarecer.
  2. Formular preguntas neutrales alineadas con matriz hecho-prueba.
  3. Evitar preguntas inductivas o revictimizantes.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Seleccionar testigos/peritos según hechos a esclarecer.
  2. Formular preguntas neutrales alineadas con matriz hecho-prueba.
  3. Evitar preguntas inductivas o revictimizantes.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `inventariar_evidencia`

- **Categoría:** Skills de evidencia y soporte probatorio
- **Agentes:** `gestor_evidencia_y_soporte_probatorio`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Crear inventario de todos los elementos disponibles.
- **Purpose (SKILL.md):** crear inventario de todos los elementos disponibles.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.83
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Crear inventario de todos los elementos disponibles.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Recopilar todos los elementos disponibles (documentos, audios, mensajes, objetos).
  2. Registrar metadatos, hash y ubicación de custodia preliminar.
  3. Emitir inventario numerado para el expediente.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Recopilar todos los elementos disponibles (documentos, audios, mensajes, objetos).
  2. Registrar metadatos, hash y ubicación de custodia preliminar.
  3. Emitir inventario numerado para el expediente.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `preservar_evidencia_digital`

- **Categoría:** Skills de evidencia y soporte probatorio
- **Agentes:** `gestor_evidencia_y_soporte_probatorio`
- **Prioridad:** P2
- **Tier gerencial:** `critico`
- **Instrucción tipo:** Definir medidas para proteger evidencia digital sin alterarla.
- **Purpose (SKILL.md):** definir medidas para proteger evidencia digital sin alterarla.
- **Pasos:** 6 → **6** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.50
- **Reasoning gerencial:** Gerencia penal-víctimas: skill crítico («Definir medidas para proteger evidencia digital sin alterarla.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 6 pasos:** 6 pasos (5 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Identificar archivos, mensajes o medios vulnerables a alteración o pérdida.
  2. Generar hash y metadatos de integridad sin modificar el original.
  3. Definir copia forense o resguardo seguro y quién custodia.
  4. Documentar cadena de custodia preliminar y accesos autorizados.
  5. Escalar a perito o autoridad si la evidencia es crítica para el caso.
  6. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Identificar archivos, mensajes o medios vulnerables a alteración o pérdida.
  2. Generar hash y metadatos de integridad sin modificar el original.
  3. Definir copia forense o resguardo seguro y quién custodia.
  4. Documentar cadena de custodia preliminar y accesos autorizados.
  5. Escalar a perito o autoridad si la evidencia es crítica para el caso.
  6. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

### Skills de audiencias

#### `crear_checklist_previo_audiencia`

- **Categoría:** Skills de audiencias
- **Agentes:** `preparador_estrategico_audiencias_penales`, `gestor_seguimiento_procesal_penal`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Listar requisitos antes de audiencia.
- **Purpose (SKILL.md):** listar requisitos antes de audiencia.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.50
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Listar requisitos antes de audiencia.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Listar documentos, pruebas y autorizaciones requeridas para la audiencia.
  2. Verificar fecha, enlace/sala, participantes y rol de la víctima.
  3. Cerrar checklist con responsables y plazos de preparación.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Listar documentos, pruebas y autorizaciones requeridas para la audiencia.
  2. Verificar fecha, enlace/sala, participantes y rol de la víctima.
  3. Cerrar checklist con responsables y plazos de preparación.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `crear_resumen_ejecutivo_litigante`

- **Categoría:** Skills de audiencias
- **Agentes:** `preparador_estrategico_audiencias_penales`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Crear resumen de una pagina para el abogado que interviene.
- **Purpose (SKILL.md):** crear resumen de una pagina para el abogado que interviene.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.38
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Crear resumen de una pagina para el abogado que interviene.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Sintetizar objetivo, etapa procesal y postura de la víctima en una página.
  2. Incluir hechos clave, riesgos y decisiones tácticas pendientes.
  3. Formato listo para lectura previa del abogado en estrados.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Sintetizar objetivo, etapa procesal y postura de la víctima en una página.
  2. Incluir hechos clave, riesgos y decisiones tácticas pendientes.
  3. Formato listo para lectura previa del abogado en estrados.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `detectar_riesgos_audiencia`

- **Categoría:** Skills de audiencias
- **Agentes:** `preparador_estrategico_audiencias_penales`, `analista_calidad_juridica`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Detectar riesgos de intervencion, oportunidad, revelacion de estrategia o revictimizacion.
- **Purpose (SKILL.md):** detectar riesgos de intervencion, oportunidad, revelacion de estrategia o revictimizacion.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.43
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Detectar riesgos de intervencion, oportunidad, revelacion de estrategia o revictimizacion.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Identificar riesgos de oportunidad, revelación de estrategia y revictimización.
  2. Evaluar impacto de preguntas, solicitudes y exposición de la víctima.
  3. Proponer mitigaciones y líneas rojas para la intervención.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Identificar riesgos de oportunidad, revelación de estrategia y revictimización.
  2. Evaluar impacto de preguntas, solicitudes y exposición de la víctima.
  3. Proponer mitigaciones y líneas rojas para la intervención.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `identificar_objetivo_audiencia`

- **Categoría:** Skills de audiencias
- **Agentes:** `preparador_estrategico_audiencias_penales`
- **Prioridad:** P2
- **Tier gerencial:** `estrategico`
- **Instrucción tipo:** Definir objetivo juridico y tactico de la audiencia para la victima.
- **Purpose (SKILL.md):** definir objetivo juridico y tactico de la audiencia para la victima.
- **Pasos:** 5 → **5** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 1.00
- **Reasoning gerencial:** Gerencia penal-víctimas: skill estratégico («Definir objetivo juridico y tactico de la audiencia para la victima.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 5 pasos:** 5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Precisar tipo de audiencia y marco normativo Ley 906 aplicable.
  2. Definir objetivo jurídico y táctico para la representación de la víctima.
  3. Alinear objetivo con teoría del caso y prueba disponible.
  4. Profundizar análisis de «Definir objetivo juridico y tactico de la audiencia para la victima» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Precisar tipo de audiencia y marco normativo Ley 906 aplicable.
  2. Definir objetivo jurídico y táctico para la representación de la víctima.
  3. Alinear objetivo con teoría del caso y prueba disponible.
  4. Profundizar análisis de «Definir objetivo juridico y tactico de la audiencia para la victima» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `preparar_contraargumentos`

- **Categoría:** Skills de audiencias
- **Agentes:** `preparador_estrategico_audiencias_penales`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Anticipar argumentos de defensa, Fiscalia u otros intervinientes.
- **Purpose (SKILL.md):** anticipar argumentos de defensa, Fiscalia u otros intervinientes.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.67
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Anticipar argumentos de defensa, Fiscalia u otros intervinientes.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Anticipar líneas de defensa, Fiscalía y otros intervinientes probables.
  2. Formular réplicas con soporte fáctico y normativo preliminar.
  3. Priorizar contraargumentos según objetivo de audiencia.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Anticipar líneas de defensa, Fiscalía y otros intervinientes probables.
  2. Formular réplicas con soporte fáctico y normativo preliminar.
  3. Priorizar contraargumentos según objetivo de audiencia.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `preparar_guion_intervencion_oral`

- **Categoría:** Skills de audiencias
- **Agentes:** `preparador_estrategico_audiencias_penales`
- **Prioridad:** P1
- **Tier gerencial:** `critico`
- **Instrucción tipo:** Estructurar intervencion oral clara y breve.
- **Purpose (SKILL.md):** estructurar intervencion oral clara y breve.
- **Pasos:** 8 → **8** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.40
- **Reasoning gerencial:** Gerencia penal-víctimas: skill crítico («Estructurar intervencion oral clara y breve.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 8 pasos:** 8 pasos (7 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Definir objetivo jurídico y táctico de la intervención en audiencia.
  2. Ubicar etapa procesal y norma Ley 906 que habilita la intervención.
  3. Estructurar apertura breve con postura de la víctima.
  4. Desarrollar núcleo argumentativo solo con hechos soportados.
  5. Anticipar réplicas a defensa y Fiscalía en puntos críticos.
  6. Revisar lenguaje para evitar revictimización y filtración de estrategia.
  7. Cerrar con peticiones concretas alineadas al objetivo de audiencia.
  8. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Definir objetivo jurídico y táctico de la intervención en audiencia.
  2. Ubicar etapa procesal y norma Ley 906 que habilita la intervención.
  3. Estructurar apertura breve con postura de la víctima.
  4. Desarrollar núcleo argumentativo solo con hechos soportados.
  5. Anticipar réplicas a defensa y Fiscalía en puntos críticos.
  6. Revisar lenguaje para evitar revictimización y filtración de estrategia.
  7. Cerrar con peticiones concretas alineadas al objetivo de audiencia.
  8. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `preparar_preguntas_audiencia`

- **Categoría:** Skills de audiencias
- **Agentes:** `preparador_estrategico_audiencias_penales`
- **Prioridad:** P2
- **Tier gerencial:** `critico`
- **Instrucción tipo:** Sugerir preguntas para victima, testigos o peritos.
- **Purpose (SKILL.md):** sugerir preguntas para victima, testigos o peritos.
- **Pasos:** 7 → **7** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.17
- **Reasoning gerencial:** Gerencia penal-víctimas: skill crítico («Sugerir preguntas para victima, testigos o peritos.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 7 pasos:** 7 pasos (6 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Definir objetivo probatorio de cada bloque de preguntas.
  2. Seleccionar destinatario (víctima, testigo, perito) según matriz hecho-prueba.
  3. Redactar preguntas neutrales, no inductivas y en orden lógico.
  4. Revisar cada pregunta con criterio de no revictimización.
  5. Señalar preguntas de alto riesgo y alternativas más seguras.
  6. Alinear preguntas con solicitudes orales previstas en la audiencia.
  7. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Definir objetivo probatorio de cada bloque de preguntas.
  2. Seleccionar destinatario (víctima, testigo, perito) según matriz hecho-prueba.
  3. Redactar preguntas neutrales, no inductivas y en orden lógico.
  4. Revisar cada pregunta con criterio de no revictimización.
  5. Señalar preguntas de alto riesgo y alternativas más seguras.
  6. Alinear preguntas con solicitudes orales previstas en la audiencia.
  7. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `preparar_solicitudes_orales`

- **Categoría:** Skills de audiencias
- **Agentes:** `preparador_estrategico_audiencias_penales`, `analista_ruta_procesal_ley906`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Formular solicitudes orales posibles segun etapa.
- **Purpose (SKILL.md):** formular solicitudes orales posibles segun etapa.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.67
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Formular solicitudes orales posibles segun etapa.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Identificar solicitudes orales procedentes según etapa y tipo de audiencia.
  2. Formular peticiones con fundamento normativo preliminar.
  3. Ordenar por prioridad y dependencias probatorias.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Identificar solicitudes orales procedentes según etapa y tipo de audiencia.
  2. Formular peticiones con fundamento normativo preliminar.
  3. Ordenar por prioridad y dependencias probatorias.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `simular_escenarios_audiencia`

- **Categoría:** Skills de audiencias
- **Agentes:** `preparador_estrategico_audiencias_penales`
- **Prioridad:** P2
- **Tier gerencial:** `estrategico`
- **Instrucción tipo:** Plantear escenarios probables y preparacion del abogado.
- **Purpose (SKILL.md):** plantear escenarios probables y preparacion del abogado.
- **Pasos:** 5 → **5** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 1.00
- **Reasoning gerencial:** Gerencia penal-víctimas: skill estratégico («Plantear escenarios probables y preparacion del abogado.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 5 pasos:** 5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Plantear escenarios favorable, intermedio y adverso probables.
  2. Definir respuesta táctica para cada escenario.
  3. Listar señales en audiencia que indiquen cambio de escenario.
  4. Profundizar análisis de «Plantear escenarios probables y preparacion del abogado» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Plantear escenarios favorable, intermedio y adverso probables.
  2. Definir respuesta táctica para cada escenario.
  3. Listar señales en audiencia que indiquen cambio de escenario.
  4. Profundizar análisis de «Plantear escenarios probables y preparacion del abogado» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

### Skills de redaccion juridica penal

#### `controlar_tono_juridico_documento`

- **Categoría:** Skills de redaccion juridica penal
- **Agentes:** `redactor_documentos_juridicos_penales`, `analista_calidad_juridica`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Asegurar tono formal, preciso, no agresivo y no especulativo.
- **Purpose (SKILL.md):** asegurar tono formal, preciso, no agresivo y no especulativo.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.50
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Asegurar tono formal, preciso, no agresivo y no especulativo.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Revisar borrador completo con criterios de tono formal y preciso.
  2. Detectar agresividad, especulación o lenguaje no profesional.
  3. Proponer correcciones manteniendo contenido jurídico.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Revisar borrador completo con criterios de tono formal y preciso.
  2. Detectar agresividad, especulación o lenguaje no profesional.
  3. Proponer correcciones manteniendo contenido jurídico.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `estructurar_hechos_fundamentos_solicitudes`

- **Categoría:** Skills de redaccion juridica penal
- **Agentes:** `redactor_documentos_juridicos_penales`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Ordenar cualquier documento juridico.
- **Purpose (SKILL.md):** ordenar cualquier documento juridico.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.25
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Ordenar cualquier documento juridico.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Definir tipo de documento y secciones obligatorias.
  2. Organizar hechos, fundamentos normativos y peticiones en orden lógico.
  3. Verificar coherencia interna y remisiones a anexos.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Definir tipo de documento y secciones obligatorias.
  2. Organizar hechos, fundamentos normativos y peticiones en orden lógico.
  3. Verificar coherencia interna y remisiones a anexos.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `redactar_ampliacion_denuncia`

- **Categoría:** Skills de redaccion juridica penal
- **Agentes:** `redactor_documentos_juridicos_penales`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Estructurar hechos nuevos, pruebas y anexos para ampliar denuncia.
- **Purpose (SKILL.md):** estructurar hechos nuevos, pruebas y anexos para ampliar denuncia.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.75
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Estructurar hechos nuevos, pruebas y anexos para ampliar denuncia.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Identificar hechos nuevos y pruebas no incorporadas en denuncia previa.
  2. Estructurar ampliación con hechos, fundamentos y anexos.
  3. Marcar hechos no verificados como pendientes.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Identificar hechos nuevos y pruebas no incorporadas en denuncia previa.
  2. Estructurar ampliación con hechos, fundamentos y anexos.
  3. Marcar hechos no verificados como pendientes.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `redactar_derecho_peticion_penal`

- **Categoría:** Skills de redaccion juridica penal
- **Agentes:** `redactor_documentos_juridicos_penales`, `evaluador_derechos_fundamentales_tutela`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Redactar derecho de peticion relacionado con autoridad o informacion del caso.
- **Purpose (SKILL.md):** redactar derecho de peticion relacionado con autoridad o informacion del caso.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.22
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Redactar derecho de peticion relacionado con autoridad o informacion del caso.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Precisar destinatario, objeto y hechos que motivan la petición.
  2. Redactar peticiones claras con fundamento constitucional/legal.
  3. Incluir anexos y plazo de respuesta esperado.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Precisar destinatario, objeto y hechos que motivan la petición.
  2. Redactar peticiones claras con fundamento constitucional/legal.
  3. Incluir anexos y plazo de respuesta esperado.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `redactar_memorial_penal`

- **Categoría:** Skills de redaccion juridica penal
- **Agentes:** `redactor_documentos_juridicos_penales`
- **Prioridad:** P2
- **Tier gerencial:** `estrategico`
- **Instrucción tipo:** Crear borrador de memorial penal.
- **Purpose (SKILL.md):** crear borrador de memorial penal.
- **Pasos:** 6 → **6** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 1.00
- **Reasoning gerencial:** Gerencia penal-víctimas: skill estratégico («Crear borrador de memorial penal.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 6 pasos:** 6 pasos (5 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Recopilar hechos soportados y pretensiones de la víctima.
  2. Redactar memorial con estructura hechos-fundamentos-peticiones.
  3. Verificar citas y marcar pendientes antes de firma humana.
  4. Profundizar análisis de «Crear borrador de memorial penal» con referencia al expediente y norma aplicable.
  5. Profundizar análisis de «Crear borrador de memorial penal» con referencia al expediente y norma aplicable.
  6. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Recopilar hechos soportados y pretensiones de la víctima.
  2. Redactar memorial con estructura hechos-fundamentos-peticiones.
  3. Verificar citas y marcar pendientes antes de firma humana.
  4. Profundizar análisis de «Crear borrador de memorial penal» con referencia al expediente y norma aplicable.
  5. Profundizar análisis de «Crear borrador de memorial penal» con referencia al expediente y norma aplicable.
  6. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `redactar_recurso_o_intervencion_preliminar`

- **Categoría:** Skills de redaccion juridica penal
- **Agentes:** `redactor_documentos_juridicos_penales`, `analista_ruta_procesal_ley906`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Crear borrador preliminar de recurso o intervencion, sujeto a revision procesal.
- **Purpose (SKILL.md):** crear borrador preliminar de recurso o intervencion, sujeto a revision procesal.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.38
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Crear borrador preliminar de recurso o intervencion, sujeto a revision procesal.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Confirmar oportunidad procesal y tipo de recurso/intervención.
  2. Redactar borrador con argumentos y peticiones procedentes.
  3. Alertar términos y requisitos de forma pendientes de verificación.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Confirmar oportunidad procesal y tipo de recurso/intervención.
  2. Redactar borrador con argumentos y peticiones procedentes.
  3. Alertar términos y requisitos de forma pendientes de verificación.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `redactar_solicitud_impulso_procesal`

- **Categoría:** Skills de redaccion juridica penal
- **Agentes:** `redactor_documentos_juridicos_penales`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Crear borrador para solicitar impulso procesal o actuaciones.
- **Purpose (SKILL.md):** crear borrador para solicitar impulso procesal o actuaciones.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.14
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Crear borrador para solicitar impulso procesal o actuaciones.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Identificar inactividad o actuación omitida por Fiscalía o juez.
  2. Redactar solicitud de impulso con hechos y fundamento Ley 906.
  3. Proponer peticiones concretas y plazos.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Identificar inactividad o actuación omitida por Fiscalía o juez.
  2. Redactar solicitud de impulso con hechos y fundamento Ley 906.
  3. Proponer peticiones concretas y plazos.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `redactar_tutela_penal_preliminar`

- **Categoría:** Skills de redaccion juridica penal
- **Agentes:** `redactor_documentos_juridicos_penales`, `evaluador_derechos_fundamentales_tutela`
- **Prioridad:** P2
- **Tier gerencial:** `critico`
- **Instrucción tipo:** Crear borrador de tutela solo si el evaluador constitucional lo recomienda preliminarmente.
- **Purpose (SKILL.md):** crear borrador de tutela solo si el evaluador constitucional lo recomienda preliminarmente.
- **Pasos:** 10 → **10** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.25
- **Reasoning gerencial:** Gerencia penal-víctimas: skill crítico («Crear borrador de tutela solo si el evaluador constitucional lo recomienda preliminarmente.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 10 pasos:** 10 pasos (9 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Confirmar dictamen previo de procedencia tutela (no redactar si improcedente).
  2. Consolidar hechos verificables separados de inferencias y pendientes.
  3. Identificar derechos fundamentales vulnerados y autoridades accionadas.
  4. Redactar fundamentos constitucionales con citas verificadas en RAG.
  5. Formular pretensiones claras, medibles y proporcionales.
  6. Listar pruebas y anexos; marcar faltantes como pendientes.
  7. Revisar no revictimización en relato y peticiones.
  8. Control de competencia, direccionamiento y tono profesional.
  9. Entregar borrador numerado listo para revisión de firma (sin radicar).
  10. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Confirmar dictamen previo de procedencia tutela (no redactar si improcedente).
  2. Consolidar hechos verificables separados de inferencias y pendientes.
  3. Identificar derechos fundamentales vulnerados y autoridades accionadas.
  4. Redactar fundamentos constitucionales con citas verificadas en RAG.
  5. Formular pretensiones claras, medibles y proporcionales.
  6. Listar pruebas y anexos; marcar faltantes como pendientes.
  7. Revisar no revictimización en relato y peticiones.
  8. Control de competencia, direccionamiento y tono profesional.
  9. Entregar borrador numerado listo para revisión de firma (sin radicar).
  10. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

### Skills de seguimiento procesal

#### `actualizar_tareas_responsable`

- **Categoría:** Skills de seguimiento procesal
- **Agentes:** `coordinador_expediente_penal`, `gestor_seguimiento_procesal_penal`
- **Prioridad:** P2
- **Tier gerencial:** `atomico`
- **Instrucción tipo:** Mantener lista de tareas por agente o abogado.
- **Purpose (SKILL.md):** mantener lista de tareas por agente o abogado.
- **Pasos:** 2 → **2** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.00
- **Reasoning gerencial:** Gerencia penal-víctimas: skill atómico («Mantener lista de tareas por agente o abogado.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 2 pasos:** 2 pasos (1 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Actualizar estado, plazo y responsable de cada tarea abierta del caso.
  2. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Actualizar estado, plazo y responsable de cada tarea abierta del caso.
  2. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `controlar_audiencias`

- **Categoría:** Skills de seguimiento procesal
- **Agentes:** `gestor_seguimiento_procesal_penal`, `preparador_estrategico_audiencias_penales`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Administrar fechas, horas, enlaces y preparacion de audiencias.
- **Purpose (SKILL.md):** administrar fechas, horas, enlaces y preparacion de audiencias.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.50
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Administrar fechas, horas, enlaces y preparacion de audiencias.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Registrar fechas, horas, enlaces y tipo de audiencia.
  2. Vincular audiencia con checklist de preparación.
  3. Alertar conflictos de agenda o datos incompletos.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Registrar fechas, horas, enlaces y tipo de audiencia.
  2. Vincular audiencia con checklist de preparación.
  3. Alertar conflictos de agenda o datos incompletos.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `crear_reporte_estado_caso`

- **Categoría:** Skills de seguimiento procesal
- **Agentes:** `gestor_seguimiento_procesal_penal`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Crear reporte interno periodico.
- **Purpose (SKILL.md):** crear reporte interno periodico.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.50
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Crear reporte interno periodico.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Consolidar actuaciones recientes, etapa y alertas del caso.
  2. Estructurar reporte interno periódico para el despacho.
  3. Excluir estrategia sensible no apta para todo el equipo.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Consolidar actuaciones recientes, etapa y alertas del caso.
  2. Estructurar reporte interno periódico para el despacho.
  3. Excluir estrategia sensible no apta para todo el equipo.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `detectar_inactividad_procesal`

- **Categoría:** Skills de seguimiento procesal
- **Agentes:** `gestor_seguimiento_procesal_penal`, `analista_ruta_procesal_ley906`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Alertar falta de movimientos por periodo relevante.
- **Purpose (SKILL.md):** alertar falta de movimientos por periodo relevante.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.33
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Alertar falta de movimientos por periodo relevante.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Comparar última actuación con plazos razonables de la etapa.
  2. Alertar periodos sin movimiento relevante.
  3. Sugerir actuación de impulso si corresponde.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Comparar última actuación con plazos razonables de la etapa.
  2. Alertar periodos sin movimiento relevante.
  3. Sugerir actuación de impulso si corresponde.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `generar_alertas_terminos_vencimientos`

- **Categoría:** Skills de seguimiento procesal
- **Agentes:** `gestor_seguimiento_procesal_penal`, `analista_ruta_procesal_ley906`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Crear alertas de posibles vencimientos.
- **Purpose (SKILL.md):** crear alertas de posibles vencimientos.
- **Pasos:** 3 → **3** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.50
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Crear alertas de posibles vencimientos.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 3 pasos:** 3 pasos (2 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Identificar vencimientos próximos en calendario procesal.
  2. Clasificar alertas por criticidad.
  3. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Identificar vencimientos próximos en calendario procesal.
  2. Clasificar alertas por criticidad.
  3. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `monitorear_radicado`

- **Categoría:** Skills de seguimiento procesal
- **Agentes:** `gestor_seguimiento_procesal_penal`
- **Prioridad:** P2
- **Tier gerencial:** `atomico`
- **Instrucción tipo:** Consultar o registrar estado de radicado.
- **Purpose (SKILL.md):** consultar o registrar estado de radicado.
- **Pasos:** 2 → **2** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 1.00
- **Reasoning gerencial:** Gerencia penal-víctimas: skill atómico («Consultar o registrar estado de radicado.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 2 pasos:** 2 pasos (1 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Consultar o registrar estado del radicado con fuente y timestamp de la consulta.
  2. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Consultar o registrar estado del radicado con fuente y timestamp de la consulta.
  2. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `preparar_resumen_operativo_cliente`

- **Categoría:** Skills de seguimiento procesal
- **Agentes:** `gestor_seguimiento_procesal_penal`, `analista_calidad_juridica`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Crear version simple del estado del proceso para cliente, sin estrategia sensible.
- **Purpose (SKILL.md):** crear version simple del estado del proceso para cliente, sin estrategia sensible.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.73
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Crear version simple del estado del proceso para cliente, sin estrategia sensible.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Sintetizar estado del proceso en lenguaje accesible.
  2. Incluir próximos pasos sin revelar estrategia sensible.
  3. Marcar para revisión humana antes de envío al cliente.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Sintetizar estado del proceso en lenguaje accesible.
  2. Incluir próximos pasos sin revelar estrategia sensible.
  3. Marcar para revisión humana antes de envío al cliente.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `registrar_actuacion_procesal`

- **Categoría:** Skills de seguimiento procesal
- **Agentes:** `gestor_seguimiento_procesal_penal`
- **Prioridad:** P2
- **Tier gerencial:** `atomico`
- **Instrucción tipo:** Registrar una actuacion nueva en la bitacora del caso.
- **Purpose (SKILL.md):** registrar una actuacion nueva en la bitacora del caso.
- **Pasos:** 2 → **2** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.29
- **Reasoning gerencial:** Gerencia penal-víctimas: skill atómico («Registrar una actuacion nueva en la bitacora del caso.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 2 pasos:** 2 pasos (1 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Registrar en bitácora: fecha, tipo, resumen y fuente de la actuación nueva.
  2. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Registrar en bitácora: fecha, tipo, resumen y fuente de la actuación nueva.
  2. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `seguimiento_documentos_radicados`

- **Categoría:** Skills de seguimiento procesal
- **Agentes:** `gestor_seguimiento_procesal_penal`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Controlar documentos enviados y respuestas pendientes.
- **Purpose (SKILL.md):** controlar documentos enviados y respuestas pendientes.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 1.00
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Controlar documentos enviados y respuestas pendientes.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Listar documentos enviados y respuestas pendientes.
  2. Controlar versiones y fechas de radicación.
  3. Alertar plazos de respuesta institucional.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Listar documentos enviados y respuestas pendientes.
  2. Controlar versiones y fechas de radicación.
  3. Alertar plazos de respuesta institucional.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

### Skills constitucionales y tutela

#### `analizar_perjuicio_irremediable`

- **Categoría:** Skills constitucionales y tutela
- **Agentes:** `evaluador_derechos_fundamentales_tutela`
- **Prioridad:** P2
- **Tier gerencial:** `estrategico`
- **Instrucción tipo:** Identificar urgencia constitucional.
- **Purpose (SKILL.md):** identificar urgencia constitucional.
- **Pasos:** 5 → **5** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 1.00
- **Reasoning gerencial:** Gerencia penal-víctimas: skill estratégico («Identificar urgencia constitucional.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 5 pasos:** 5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Identificar el perjuicio alegado y su carácter actual o inminente.
  2. Evaluar si el perjuicio es grave, de difícil reparación y requiere medida urgente.
  3. Contrastar con mecanismos ordinarios y plazos procesales vigentes.
  4. Profundizar análisis de «Identificar urgencia constitucional» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Identificar el perjuicio alegado y su carácter actual o inminente.
  2. Evaluar si el perjuicio es grave, de difícil reparación y requiere medida urgente.
  3. Contrastar con mecanismos ordinarios y plazos procesales vigentes.
  4. Profundizar análisis de «Identificar urgencia constitucional» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `crear_matriz_hecho_derecho_fundamental`

- **Categoría:** Skills constitucionales y tutela
- **Agentes:** `evaluador_derechos_fundamentales_tutela`
- **Prioridad:** P2
- **Tier gerencial:** `estrategico`
- **Instrucción tipo:** Relacionar hechos con derechos afectados.
- **Purpose (SKILL.md):** relacionar hechos con derechos afectados.
- **Pasos:** 5 → **5** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 1.00
- **Reasoning gerencial:** Gerencia penal-víctimas: skill estratégico («Relacionar hechos con derechos afectados.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 5 pasos:** 5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Listar hechos verificables y narrados relevantes para la vulneración alegada.
  2. Relacionar cada hecho con el derecho fundamental comprometido y la conducta omisiva/activa.
  3. Señalar vacíos probatorios y norma constitucional de soporte preliminar.
  4. Profundizar análisis de «Relacionar hechos con derechos afectados» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Listar hechos verificables y narrados relevantes para la vulneración alegada.
  2. Relacionar cada hecho con el derecho fundamental comprometido y la conducta omisiva/activa.
  3. Señalar vacíos probatorios y norma constitucional de soporte preliminar.
  4. Profundizar análisis de «Relacionar hechos con derechos afectados» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `detectar_riesgo_improcedencia_tutela`

- **Categoría:** Skills constitucionales y tutela
- **Agentes:** `evaluador_derechos_fundamentales_tutela`, `analista_calidad_juridica`
- **Prioridad:** P0
- **Tier gerencial:** `critico`
- **Instrucción tipo:** Detectar si tutela puede ser prematura, subsidiaria o improcedente.
- **Purpose (SKILL.md):** detectar si tutela puede ser prematura, subsidiaria o improcedente.
- **Pasos:** 8 → **8** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.57
- **Reasoning gerencial:** Gerencia penal-víctimas: skill crítico («Detectar si tutela puede ser prematura, subsidiaria o improcedente.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 8 pasos:** 8 pasos (7 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Inventariar vías ordinarias disponibles en la etapa penal actual.
  2. Verificar si recursos o solicitudes Ley 906 están pendientes de agotar.
  3. Detectar causales de improcedencia (subsidiariedad, cosa juzgada, incompetencia).
  4. Evaluar si el daño es actual o remediabile por vía ordinaria.
  5. Documentar probabilidad de rechazo y costo de tutela prematura.
  6. Recomendar vía alternativa preferente si la tutela es improcedente.
  7. Señalar plazo y actuación ordinaria recomendada antes de tutela.
  8. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Inventariar vías ordinarias disponibles en la etapa penal actual.
  2. Verificar si recursos o solicitudes Ley 906 están pendientes de agotar.
  3. Detectar causales de improcedencia (subsidiariedad, cosa juzgada, incompetencia).
  4. Evaluar si el daño es actual o remediabile por vía ordinaria.
  5. Documentar probabilidad de rechazo y costo de tutela prematura.
  6. Recomendar vía alternativa preferente si la tutela es improcedente.
  7. Señalar plazo y actuación ordinaria recomendada antes de tutela.
  8. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `evaluar_derecho_peticion`

- **Categoría:** Skills constitucionales y tutela
- **Agentes:** `evaluador_derechos_fundamentales_tutela`, `redactor_documentos_juridicos_penales`
- **Prioridad:** P2
- **Tier gerencial:** `estrategico`
- **Instrucción tipo:** Revisar si existe derecho de peticion incumplido.
- **Purpose (SKILL.md):** revisar si existe derecho de peticion incumplido.
- **Pasos:** 5 → **5** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 1.00
- **Reasoning gerencial:** Gerencia penal-víctimas: skill estratégico («Revisar si existe derecho de peticion incumplido.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 5 pasos:** 5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Verificar existencia de petición previa, destinatario y objeto solicitado.
  2. Constatar plazo de respuesta y silencio administrativo si aplica.
  3. Determinar si procede derecho de petición, tutela u otra vía según el caso.
  4. Profundizar análisis de «Revisar si existe derecho de peticion incumplido» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Verificar existencia de petición previa, destinatario y objeto solicitado.
  2. Constatar plazo de respuesta y silencio administrativo si aplica.
  3. Determinar si procede derecho de petición, tutela u otra vía según el caso.
  4. Profundizar análisis de «Revisar si existe derecho de peticion incumplido» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `evaluar_procedencia_tutela`

- **Categoría:** Skills constitucionales y tutela
- **Agentes:** `evaluador_derechos_fundamentales_tutela`, `analista_calidad_juridica`
- **Prioridad:** P0
- **Tier gerencial:** `critico`
- **Instrucción tipo:** Evaluar legitimacion, subsidiariedad, inmediatez y relevancia constitucional.
- **Purpose (SKILL.md):** evaluar legitimacion, subsidiariedad, inmediatez y relevancia constitucional.
- **Pasos:** 9 → **9** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.83
- **Reasoning gerencial:** Gerencia penal-víctimas: skill crítico («Evaluar legitimacion, subsidiariedad, inmediatez y relevancia constitucional.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 9 pasos:** 9 pasos (8 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Verificar legitimación por activa (titular del derecho y vínculo con el caso).
  2. Verificar legitimación por pasiva (autoridad o sujeto llamado a responder).
  3. Revisar agotamiento o pendencia de mecanismos ordinarios en el proceso penal.
  4. Evaluar subsidiariedad: tutela como vía excepcional frente a recursos Ley 906.
  5. Evaluar inmediatez del perjuicio y necesidad de medida urgente.
  6. Evaluar conexidad constitucional y relevancia del derecho invocado.
  7. Documentar requisitos faltantes y riesgo de improcedencia.
  8. Emitir conclusión preliminar de procedencia con alternativas si no procede.
  9. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Verificar legitimación por activa (titular del derecho y vínculo con el caso).
  2. Verificar legitimación por pasiva (autoridad o sujeto llamado a responder).
  3. Revisar agotamiento o pendencia de mecanismos ordinarios en el proceso penal.
  4. Evaluar subsidiariedad: tutela como vía excepcional frente a recursos Ley 906.
  5. Evaluar inmediatez del perjuicio y necesidad de medida urgente.
  6. Evaluar conexidad constitucional y relevancia del derecho invocado.
  7. Documentar requisitos faltantes y riesgo de improcedencia.
  8. Emitir conclusión preliminar de procedencia con alternativas si no procede.
  9. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `identificar_derecho_fundamental_afectado`

- **Categoría:** Skills constitucionales y tutela
- **Agentes:** `evaluador_derechos_fundamentales_tutela`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Identificar posibles derechos fundamentales comprometidos.
- **Purpose (SKILL.md):** identificar posibles derechos fundamentales comprometidos.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.60
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Identificar posibles derechos fundamentales comprometidos.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Mapear hechos del caso contra catálogo de derechos fundamentales aplicables.
  2. Precisar titular del derecho y autoridad o sujeto vulnerador.
  3. Priorizar derechos más directamente comprometidos para análisis posterior.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Mapear hechos del caso contra catálogo de derechos fundamentales aplicables.
  2. Precisar titular del derecho y autoridad o sujeto vulnerador.
  3. Priorizar derechos más directamente comprometidos para análisis posterior.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `preparar_borrador_tutela_preliminar`

- **Categoría:** Skills constitucionales y tutela
- **Agentes:** `evaluador_derechos_fundamentales_tutela`, `redactor_documentos_juridicos_penales`
- **Prioridad:** P2
- **Tier gerencial:** `estrategico`
- **Instrucción tipo:** Preparar insumos para borrador de tutela.
- **Purpose (SKILL.md):** preparar insumos para borrador de tutela.
- **Pasos:** 5 → **5** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 1.00
- **Reasoning gerencial:** Gerencia penal-víctimas: skill estratégico («Preparar insumos para borrador de tutela.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 5 pasos:** 5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Consolidar hechos, derechos afectados y pretensiones con fuentes.
  2. Verificar que el evaluador constitucional recomendó tutela preliminarmente.
  3. Organizar insumos (hechos, fundamentos, pretensiones, anexos) para borrador.
  4. Profundizar análisis de «Preparar insumos para borrador de tutela» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Consolidar hechos, derechos afectados y pretensiones con fuentes.
  2. Verificar que el evaluador constitucional recomendó tutela preliminarmente.
  3. Organizar insumos (hechos, fundamentos, pretensiones, anexos) para borrador.
  4. Profundizar análisis de «Preparar insumos para borrador de tutela» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `recomendar_via_constitucional_o_alternativa`

- **Categoría:** Skills constitucionales y tutela
- **Agentes:** `evaluador_derechos_fundamentales_tutela`, `coordinador_expediente_penal`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Recomendar tutela, derecho de peticion, solicitud procesal, queja u otra ruta.
- **Purpose (SKILL.md):** recomendar tutela, derecho de peticion, solicitud procesal, queja u otra ruta.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.56
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Recomendar tutela, derecho de peticion, solicitud procesal, queja u otra ruta.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Inventariar vías disponibles: tutela, petición, solicitud Ley 906, queja, etc.
  2. Comparar oportunidad, celeridad y probabilidad de éxito de cada vía.
  3. Recomendar ruta preferente con justificación y riesgos.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Inventariar vías disponibles: tutela, petición, solicitud Ley 906, queja, etc.
  2. Comparar oportunidad, celeridad y probabilidad de éxito de cada vía.
  3. Recomendar ruta preferente con justificación y riesgos.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `revisar_mecanismos_ordinarios`

- **Categoría:** Skills constitucionales y tutela
- **Agentes:** `evaluador_derechos_fundamentales_tutela`
- **Prioridad:** P2
- **Tier gerencial:** `estrategico`
- **Instrucción tipo:** Verificar si hay vias ordinarias antes de tutela.
- **Purpose (SKILL.md):** verificar si hay vias ordinarias antes de tutela.
- **Pasos:** 5 → **5** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 1.00
- **Reasoning gerencial:** Gerencia penal-víctimas: skill estratégico («Verificar si hay vias ordinarias antes de tutela.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 5 pasos:** 5 pasos (4 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Identificar recursos y actuaciones ordinarias en el proceso penal vigente.
  2. Verificar si están pendientes de interponer o ya agotados.
  3. Determinar si la tutela es subsidiaria respecto de dichos mecanismos.
  4. Profundizar análisis de «Verificar si hay vias ordinarias antes de tutela» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Identificar recursos y actuaciones ordinarias en el proceso penal vigente.
  2. Verificar si están pendientes de interponer o ya agotados.
  3. Determinar si la tutela es subsidiaria respecto de dichos mecanismos.
  4. Profundizar análisis de «Verificar si hay vias ordinarias antes de tutela» con referencia al expediente y norma aplicable.
  5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

### Skills de calidad juridica

#### `clasificar_aprobacion_juridica`

- **Categoría:** Skills de calidad juridica
- **Agentes:** `analista_calidad_juridica`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Clasificar la salida como aprobable, aprobable con cambios, rechazada o escalar.
- **Purpose (SKILL.md):** clasificar la salida como aprobable, aprobable con cambios, rechazada o escalar.
- **Pasos:** 3 → **3** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.12
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Clasificar la salida como aprobable, aprobable con cambios, rechazada o escalar.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 3 pasos:** 3 pasos (2 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Revisar soporte fáctico, normativo y jurisprudencial de la salida.
  2. Aplicar checklist de riesgos (alucinación, confidencialidad, tono, revictimización).
  3. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Revisar soporte fáctico, normativo y jurisprudencial de la salida.
  2. Aplicar checklist de riesgos (alucinación, confidencialidad, tono, revictimización).
  3. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `controlar_confidencialidad_datos_sensibles`

- **Categoría:** Skills de calidad juridica
- **Agentes:** `analista_calidad_juridica`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Detectar datos sensibles o innecesarios.
- **Purpose (SKILL.md):** detectar datos sensibles o innecesarios.
- **Pasos:** 3 → **3** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 1.00
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Detectar datos sensibles o innecesarios.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 3 pasos:** 3 pasos (2 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Detectar PII y datos sensibles innecesarios en la salida.
  2. Proponer redacción alternativa o anonimización.
  3. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Detectar PII y datos sensibles innecesarios en la salida.
  2. Proponer redacción alternativa o anonimización.
  3. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `controlar_no_revictimizacion`

- **Categoría:** Skills de calidad juridica
- **Agentes:** `analista_calidad_juridica`, `analista_representacion_victimas`
- **Prioridad:** P1
- **Tier gerencial:** `critico`
- **Instrucción tipo:** Revisar que la salida no culpe ni exponga indebidamente a la victima.
- **Purpose (SKILL.md):** revisar que la salida no culpe ni exponga indebidamente a la victima.
- **Pasos:** 6 → **6** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.86
- **Reasoning gerencial:** Gerencia penal-víctimas: skill crítico («Revisar que la salida no culpe ni exponga indebidamente a la victima.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 6 pasos:** 6 pasos (5 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Revisar lenguaje que culpe, minimice o exponga indebidamente a la víctima.
  2. Evaluar preguntas y estrategias propuestas con enfoque de derechos.
  3. Detectar exposición innecesaria de datos sensibles o relato gráfico.
  4. Proponer reformulaciones respetuosas y centradas en derechos.
  5. Documentar riesgos residuales para decisión del abogado.
  6. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Revisar lenguaje que culpe, minimice o exponga indebidamente a la víctima.
  2. Evaluar preguntas y estrategias propuestas con enfoque de derechos.
  3. Detectar exposición innecesaria de datos sensibles o relato gráfico.
  4. Proponer reformulaciones respetuosas y centradas en derechos.
  5. Documentar riesgos residuales para decisión del abogado.
  6. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `controlar_separacion_hecho_inferencia`

- **Categoría:** Skills de calidad juridica
- **Agentes:** `analista_calidad_juridica`, `redactor_documentos_juridicos_penales`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Verificar que no se confundan hechos probados, narrados, inferidos y pendientes.
- **Purpose (SKILL.md):** verificar que no se confundan hechos probados, narrados, inferidos y pendientes.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.25
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Verificar que no se confundan hechos probados, narrados, inferidos y pendientes.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Etiquetar cada afirmación como hecho confirmado, narrado, inferido o pendiente.
  2. Detectar conclusiones presentadas como hechos sin soporte.
  3. Exigir corrección o marcación antes de uso externo.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Etiquetar cada afirmación como hecho confirmado, narrado, inferido o pendiente.
  2. Detectar conclusiones presentadas como hechos sin soporte.
  3. Exigir corrección o marcación antes de uso externo.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `controlar_tono_riesgo_reputacional`

- **Categoría:** Skills de calidad juridica
- **Agentes:** `analista_calidad_juridica`, `redactor_documentos_juridicos_penales`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Revisar tono profesional y evitar lenguaje riesgoso.
- **Purpose (SKILL.md):** revisar tono profesional y evitar lenguaje riesgoso.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.33
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Revisar tono profesional y evitar lenguaje riesgoso.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Evaluar tono formal, preciso y no especulativo del documento.
  2. Detectar expresiones agresivas, promesas de resultado o riesgo reputacional.
  3. Sugerir ajustes de redacción profesional.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Evaluar tono formal, preciso y no especulativo del documento.
  2. Detectar expresiones agresivas, promesas de resultado o riesgo reputacional.
  3. Sugerir ajustes de redacción profesional.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `detectar_alucinaciones_legales`

- **Categoría:** Skills de calidad juridica
- **Agentes:** `analista_calidad_juridica`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Detectar fuentes, hechos, conclusiones o citas inventadas.
- **Purpose (SKILL.md):** detectar fuentes, hechos, conclusiones o citas inventadas.
- **Pasos:** 3 → **3** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.50
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Detectar fuentes, hechos, conclusiones o citas inventadas.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 3 pasos:** 3 pasos (2 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Cruzar citas normativas, sentencias y radicados con fuentes verificables.
  2. Marcar referencias inventadas o no localizadas en RAG.
  3. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Cruzar citas normativas, sentencias y radicados con fuentes verificables.
  2. Marcar referencias inventadas o no localizadas en RAG.
  3. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `revisar_coherencia_estrategica`

- **Categoría:** Skills de calidad juridica
- **Agentes:** `analista_calidad_juridica`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Asegurar que documento o recomendacion sea coherente con la estrategia aprobada.
- **Purpose (SKILL.md):** asegurar que documento o recomendacion sea coherente con la estrategia aprobada.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.11
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Asegurar que documento o recomendacion sea coherente con la estrategia aprobada.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Contrastar salida con teoría del caso y objetivos aprobados de la víctima.
  2. Detectar contradicciones internas o con actuaciones previas.
  3. Recomendar alineación o escalamiento estratégico.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Contrastar salida con teoría del caso y objetivos aprobados de la víctima.
  2. Detectar contradicciones internas o con actuaciones previas.
  3. Recomendar alineación o escalamiento estratégico.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `verificar_citas_normativas`

- **Categoría:** Skills de calidad juridica
- **Agentes:** `analista_calidad_juridica`, `redactor_documentos_juridicos_penales`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Verificar que normas, articulos y leyes citadas existan en el RAG o esten marcadas pendientes.
- **Purpose (SKILL.md):** verificar que normas, articulos y leyes citadas existan en el RAG o esten marcadas pendientes.
- **Pasos:** 3 → **3** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.18
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Verificar que normas, articulos y leyes citadas existan en el RAG o esten marcadas pendientes.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 3 pasos:** 3 pasos (2 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Validar existencia de leyes, artículos y decretos citados.
  2. Verificar vigencia y pertinencia al caso penal-víctimas.
  3. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Validar existencia de leyes, artículos y decretos citados.
  2. Verificar vigencia y pertinencia al caso penal-víctimas.
  3. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `verificar_jurisprudencia`

- **Categoría:** Skills de calidad juridica
- **Agentes:** `analista_calidad_juridica`
- **Prioridad:** P2
- **Tier gerencial:** `operativo`
- **Instrucción tipo:** Revisar sentencias, radicados, fechas y organos judiciales.
- **Purpose (SKILL.md):** revisar sentencias, radicados, fechas y organos judiciales.
- **Pasos:** 4 → **4** (propuesta v2)
- **Score alineación (pasos actuales vs instrucción):** 0.67
- **Reasoning gerencial:** Gerencia penal-víctimas: skill operativo («Revisar sentencias, radicados, fechas y organos judiciales.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
- **Por qué 4 pasos:** 4 pasos (3 operativos + HITL): menos pasos omitirían controles jurídicos; más pasos sin justificación duplicarían otro skill.
- **Riesgos si se recortan pasos:** Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria o uso de afirmaciones sin fuente.
- **Pasos actuales (al auditar):**
  1. Validar sentencias, radicados, fechas y órganos judiciales citados.
  2. Confirmar que el precedente es pertinente al problema jurídico.
  3. Marcar jurisprudencia no verificada como pendiente.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Pasos propuestos v2:**
  1. Validar sentencias, radicados, fechas y órganos judiciales citados.
  2. Confirmar que el precedente es pertinente al problema jurídico.
  3. Marcar jurisprudencia no verificada como pendiente.
  4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

---

## Fase 2 — Dictamen gerencial por categoría

### 1. Skills transversales

*Clasificación de tareas, urgencia y pendientes compartidos entre agentes.*

- **Propósito plantilla anterior:** Coordinación inicial: contexto, clasificación y escalamiento.
- **Skills que encajaban:** Ninguno con plantilla genérica actual; cada skill tiene función distinta.
- **Skills que no encajaban:** Los 5 skills comparten 3 pasos idénticos pese a objetivos distintos.
- **Faltaba a nivel categoría:** Escalamiento humano en urgencia; inventario estructurado en faltantes.
- **Sobraba:** Paso genérico de clasificación/priorización que no describe la tarea real.
- **Dictamen:** **REESCRIBIR — pasos específicos por skill (cantidad variable según criticidad).**

### 2. Skills de hechos y cronologia

*Extracción factual, cronología, matrices hecho-fuente y vacíos.*

- **Propósito plantilla anterior:** Extracción factual, contraste y entrega de cronología/matriz.
- **Skills que encajaban:** construir_cronologia_penal, extraer_hechos_relevantes, detectar_contradicciones_factuales.
- **Skills que no encajaban:** clasificar_fuente_factual; generar_preguntas_aclaracion.
- **Faltaba a nivel categoría:** Clasificación de fuente y nivel de soporte en clasificar_fuente_factual.
- **Sobraba:** Entrega de cronología completa en skills que solo clasifican o preguntan.
- **Dictamen:** **REESCRIBIR — diferenciar clasificación, cronología, matriz y preguntas.**

### 3. Skills de tipicidad y responsabilidad penal

*Tipicidad preliminar, elementos del tipo y riesgos de atipicidad.*

- **Propósito plantilla anterior:** Hipótesis típica, vinculación hecho-prueba, riesgos de atipicidad.
- **Skills que encajaban:** descomponer_elementos_tipo_penal, mapear_tipo_penal_hecho_prueba.
- **Skills que no encajaban:** generar_preguntas_tipicidad.
- **Faltaba a nivel categoría:** Elemento subjetivo explícito en analizar_dolo_culpa_elemento_subjetivo.
- **Sobraba:** Matriz completa en skills que solo generan preguntas.
- **Dictamen:** **REESCRIBIR — ajustar a tipicidad, autoría, agravantes y preguntas.**

### 4. Skills de ruta procesal Ley 906

*Etapa procesal, oportunidades, términos y actuaciones de la víctima.*

- **Propósito plantilla anterior:** Etapa, oportunidad, actuaciones y ruta recomendada.
- **Skills que encajaban:** crear_ruta_procesal_recomendada, identificar_etapa_procesal_ley906.
- **Skills que no encajaban:** controlar_terminos_procesales_preliminares.
- **Faltaba a nivel categoría:** Cálculo/alerta de términos con disclaimer de verificación humana.
- **Sobraba:** Ruta completa en skills de solo evaluación de oportunidad.
- **Dictamen:** **REESCRIBIR — separar etapa, oportunidad, términos y actuaciones.**

### 5. Skills de representacion de victimas

*Teoría del caso, derechos de la víctima y no revictimización.*

- **Propósito plantilla anterior:** Intereses de la víctima, teoría del caso y revictimización.
- **Skills que encajaban:** construir_teoria_caso_victima, identificar_intereses_victima.
- **Skills que no encajaban:** detectar_riesgo_revictimizacion.
- **Faltaba a nivel categoría:** Revisión lingüística focalizada en detectar_riesgo_revictimizacion.
- **Sobraba:** Alineación de teoría completa en skills de solo detección de riesgo.
- **Dictamen:** **REESCRIBIR — un eje central alineado al propósito de cada skill.**

### 6. Skills de evidencia y soporte probatorio

*Inventario probatorio, brechas, cadena de custodia y recaudo.*

- **Propósito plantilla anterior:** Inventario, suficiencia, brechas y plan de recaudo.
- **Skills que encajaban:** inventariar_evidencia, crear_plan_recaudo_probatorio.
- **Skills que no encajaban:** preservar_evidencia_digital, controlar_cadena_custodia_preliminar.
- **Faltaba a nivel categoría:** Hash, custodia y preservación en evidencia digital/física.
- **Sobraba:** Plan de recaudo genérico en preservación y custodia.
- **Dictamen:** **REESCRIBIR — custodia y preservación como pasos propios.**

### 7. Skills de audiencias

*Preparación, guiones, solicitudes orales y riesgos en audiencias Ley 906.*

- **Propósito plantilla anterior:** Objetivo, guion, solicitudes y checklist.
- **Skills que encajaban:** preparar_guion_intervencion_oral, identificar_objetivo_audiencia.
- **Skills que no encajaban:** crear_checklist_previo_audiencia.
- **Faltaba a nivel categoría:** Control de no revictimización en preguntas y guiones.
- **Sobraba:** Secuencia idéntica en 9 skills distintos.
- **Dictamen:** **REESCRIBIR — secuencia acorde a checklist, simulación o preguntas.**

### 8. Skills de redaccion juridica penal

*Borradores de memoriales, solicitudes, recursos y piezas procesales.*

- **Propósito plantilla anterior:** Tipo de pieza, estructura hechos-fundamentos-peticiones, control de tono.
- **Skills que encajaban:** redactar_memorial_penal, estructurar_hechos_fundamentos_solicitudes.
- **Skills que no encajaban:** controlar_tono_juridico_documento.
- **Faltaba a nivel categoría:** Verificación de oportunidad procesal en recursos.
- **Sobraba:** Redacción completa en skill de solo control editorial.
- **Dictamen:** **REESCRIBIR — separar redacción de control editorial.**

### 9. Skills de seguimiento procesal

*Radicados, alertas de vencimiento y reportes operativos.*

- **Propósito plantilla anterior:** Estado operativo, términos, tareas y reportes.
- **Skills que encajaban:** monitorear_radicado, crear_reporte_estado_caso.
- **Skills que no encajaban:** registrar_actuacion_procesal.
- **Faltaba a nivel categoría:** Bitácora específica en registrar_actuacion_procesal.
- **Sobraba:** Reporte a cliente en skills puramente operativos.
- **Dictamen:** **REESCRIBIR — operación vs reporte vs alertas.**

### 10. Skills constitucionales y tutela

*Tutela, subsidiariedad, inmediatez y derechos fundamentales.*

- **Propósito plantilla anterior:** Derecho fundamental, procedencia de tutela, vía alternativa.
- **Skills que encajaban:** evaluar_procedencia_tutela, revisar_mecanismos_ordinarios.
- **Skills que no encajaban:** evaluar_derecho_peticion, preparar_borrador_tutela_preliminar.
- **Faltaba a nivel categoría:** Análisis específico de petición y de perjuicio irremediable.
- **Sobraba:** Bloque tutela idéntico en los 9 skills de la categoría.
- **Dictamen:** **REESCRIBIR — subsidiariedad, petición, perjuicio y borrador diferenciados.**

### 11. Skills de calidad juridica

*Control de alucinaciones, tono, confidencialidad y coherencia estratégica.*

- **Propósito plantilla anterior:** Auditoría de soporte, riesgos y clasificación de aprobación.
- **Skills que encajaban:** clasificar_aprobacion_juridica, detectar_alucinaciones_legales.
- **Skills que no encajaban:** verificar_citas_normativas.
- **Faltaba a nivel categoría:** Validación específica por tipo de riesgo en cada skill.
- **Sobraba:** Checklist completo repetido en skills de un solo foco.
- **Dictamen:** **REESCRIBIR — un eje principal por skill de calidad.**

---

## Fase 3 — Prioridad P0/P1

### P0

#### `clasificar_fuente_factual` — tier `estrategico`, **6 pasos**

- **Reasoning:** Gerencia penal-víctimas: skill estratégico («Distinguir documento, relato de victima, relato de tercero, autoridad, inferencia o dato pendiente.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
  1. Inventariar cada afirmación factual en los insumos del turno.
  2. Clasificar fuente: documento, relato víctima, tercero, autoridad, inferencia o pendiente.
  3. Asignar nivel de soporte sin mezclar hecho confirmado, narrado e inferido.
  4. Construir matriz hecho-fuente preliminar (no cronología completa).
  5. Señalar afirmaciones sin fuente para verificación humana.
  6. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `marcar_pendientes_verificacion` — tier `atomico`, **2 pasos**

- **Reasoning:** Gerencia penal-víctimas: skill atómico («Marcar cualquier dato, cita o hecho incompleto como `[PENDIENTE DE VERIFICAR]`.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
  1. Recorrer salida e insertar `[PENDIENTE DE VERIFICAR]` en cada dato, cita o hecho sin fuente.
  2. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `controlar_cadena_custodia_preliminar` — tier `critico`, **7 pasos**

- **Reasoning:** Gerencia penal-víctimas: skill crítico («Alertar si la evidencia puede requerir cadena de custodia.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
  1. Identificar evidencia que exija cadena de custodia formal.
  2. Revisar recolección: quién, cuándo, dónde y protocolo usado.
  3. Verificar traslado, almacenamiento y cadena de acceso documentada.
  4. Detectar rupturas o vacíos que afecten admisibilidad.
  5. Alertar necesidad de perito, cadena certificada u oficio urgente.
  6. Proponer medidas correctivas sin alterar el elemento probatorio.
  7. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `evaluar_procedencia_tutela` — tier `critico`, **9 pasos**

- **Reasoning:** Gerencia penal-víctimas: skill crítico («Evaluar legitimacion, subsidiariedad, inmediatez y relevancia constitucional.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
  1. Verificar legitimación por activa (titular del derecho y vínculo con el caso).
  2. Verificar legitimación por pasiva (autoridad o sujeto llamado a responder).
  3. Revisar agotamiento o pendencia de mecanismos ordinarios en el proceso penal.
  4. Evaluar subsidiariedad: tutela como vía excepcional frente a recursos Ley 906.
  5. Evaluar inmediatez del perjuicio y necesidad de medida urgente.
  6. Evaluar conexidad constitucional y relevancia del derecho invocado.
  7. Documentar requisitos faltantes y riesgo de improcedencia.
  8. Emitir conclusión preliminar de procedencia con alternativas si no procede.
  9. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `detectar_riesgo_improcedencia_tutela` — tier `critico`, **8 pasos**

- **Reasoning:** Gerencia penal-víctimas: skill crítico («Detectar si tutela puede ser prematura, subsidiaria o improcedente.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
  1. Inventariar vías ordinarias disponibles en la etapa penal actual.
  2. Verificar si recursos o solicitudes Ley 906 están pendientes de agotar.
  3. Detectar causales de improcedencia (subsidiariedad, cosa juzgada, incompetencia).
  4. Evaluar si el daño es actual o remediabile por vía ordinaria.
  5. Documentar probabilidad de rechazo y costo de tutela prematura.
  6. Recomendar vía alternativa preferente si la tutela es improcedente.
  7. Señalar plazo y actuación ordinaria recomendada antes de tutela.
  8. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

### P1

#### `preparar_guion_intervencion_oral` — tier `critico`, **8 pasos**

- **Reasoning:** Gerencia penal-víctimas: skill crítico («Estructurar intervencion oral clara y breve.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
  1. Definir objetivo jurídico y táctico de la intervención en audiencia.
  2. Ubicar etapa procesal y norma Ley 906 que habilita la intervención.
  3. Estructurar apertura breve con postura de la víctima.
  4. Desarrollar núcleo argumentativo solo con hechos soportados.
  5. Anticipar réplicas a defensa y Fiscalía en puntos críticos.
  6. Revisar lenguaje para evitar revictimización y filtración de estrategia.
  7. Cerrar con peticiones concretas alineadas al objetivo de audiencia.
  8. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `controlar_no_revictimizacion` — tier `critico`, **6 pasos**

- **Reasoning:** Gerencia penal-víctimas: skill crítico («Revisar que la salida no culpe ni exponga indebidamente a la victima.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
  1. Revisar lenguaje que culpe, minimice o exponga indebidamente a la víctima.
  2. Evaluar preguntas y estrategias propuestas con enfoque de derechos.
  3. Detectar exposición innecesaria de datos sensibles o relato gráfico.
  4. Proponer reformulaciones respetuosas y centradas en derechos.
  5. Documentar riesgos residuales para decisión del abogado.
  6. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `identificar_etapa_procesal_ley906` — tier `estrategico`, **6 pasos**

- **Reasoning:** Gerencia penal-víctimas: skill estratégico («Determinar etapa del caso.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
  1. Revisar actuaciones y estado del radicado.
  2. Determinar etapa procesal según Ley 906 (indagación, investigación, juicio, etc.).
  3. Señalar incertidumbres si el expediente es incompleto.
  4. Profundizar análisis de «Determinar etapa del caso» con referencia al expediente y norma aplicable.
  5. Profundizar análisis de «Determinar etapa del caso» con referencia al expediente y norma aplicable.
  6. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

#### `evaluar_oportunidad_procesal` — tier `critico`, **7 pasos**

- **Reasoning:** Gerencia penal-víctimas: skill crítico («Determinar si una solicitud o intervencion es oportuna, prematura o extemporanea.»). Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; no se fusionan etapas distintas ni se repiten flujos de otros skills.
  1. Ubicar la actuación propuesta en la etapa exacta del proceso penal.
  2. Verificar plazos y términos aplicables con advertencia de cálculo humano.
  3. Contrastar con actuaciones previas y estado del radicado.
  4. Determinar si es oportuna, prematura o extemporánea para la víctima.
  5. Evaluar consecuencias de actuar o no actuar en este momento.
  6. Sugerir fecha o actuación alternativa si no es oportuna.
  7. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.
- **Aprobación abogada:** [ ] Pendiente

---

## Resumen por agente

### `coordinador_expediente_penal` — Coordinador del expediente
- **Skills:** 11 · **Flujo:** Recibe la consulta de la abogada, entiende que necesita y la envia al especialista correcto.

### `analista_cronologia_hechos_penales` — Analista de cronologia y hechos
- **Skills:** 9 · **Flujo:** Convierte relatos y documentos en una historia factual ordenada y verificable.

### `analista_tipicidad_y_responsabilidad_penal` — Analista de tipicidad y responsabilidad
- **Skills:** 9 · **Flujo:** Traduce hechos y pruebas en hipotesis juridicas de tipicidad y responsabilidad preliminar.

### `analista_ruta_procesal_ley906` — Analista de ruta procesal Ley 906
- **Skills:** 13 · **Flujo:** Ubica la etapa exacta y la mejor ruta procesal para representar a la victima.

### `analista_representacion_victimas` — Analista de representacion de victimas
- **Skills:** 13 · **Flujo:** Garantiza que la estrategia este centrada en derechos, intereses y no revictimizacion.

### `gestor_evidencia_y_soporte_probatorio` — Gestor de evidencia y prueba
- **Skills:** 13 · **Flujo:** Transforma evidencia dispersa en inventario util y plan probatorio accionable.

### `preparador_estrategico_audiencias_penales` — Preparador de audiencias
- **Skills:** 16 · **Flujo:** Prepara audiencias con objetivo, guion, preguntas y solicitudes.

### `redactor_documentos_juridicos_penales` — Redactor de documentos penales
- **Skills:** 16 · **Flujo:** Convierte analisis juridico en escritos utilizables por la abogada.

### `gestor_seguimiento_procesal_penal` — Gestor de seguimiento procesal
- **Skills:** 12 · **Flujo:** Monitorea estado de radicado, actuaciones, audiencias y terminos.

### `evaluador_derechos_fundamentales_tutela` — Evaluador de tutela y derechos fundamentales
- **Skills:** 13 · **Flujo:** Evalua si corresponde tutela o via alternativa, con criterio constitucional.

### `analista_calidad_juridica` — Analista de calidad juridica
- **Skills:** 26 · **Flujo:** Revisa salida final antes de compartir externamente.
