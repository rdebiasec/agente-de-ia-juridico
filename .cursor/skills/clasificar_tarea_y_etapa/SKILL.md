---
name: clasificar-tarea-y-etapa
description: Skill operativo penal-victimas: clasificar la solicitud del usuario interno y detectar la etapa aparente del caso. Use when the workflow requires `clasificar_tarea_y_etapa`.
disable-model-invocation: true
---

# clasificar_tarea_y_etapa

## Scope
- Category: `Skills transversales`
- Skill ID: `clasificar_tarea_y_etapa`
- Tier: `operativo`

## Used By Agents
- `coordinador_expediente_penal` (skill primario del agente)
- `analista_ruta_procesal_ley906`

## Purpose
Entender qué pide el despacho en el turno, clasificar el tipo de tarea y ubicar la etapa procesal aparente para derivar al especialista correcto o pedir datos faltantes.

## Rol en coordinador
Primer skill en cada consulta nueva. No resuelve el fondo del caso; enruta o solicita insumos mínimos.

## Inputs
- Solicitud textual del abogado o usuario interno.
- Resumen de caso y radicado (si existe).
- Documentos disponibles en el turno o expediente.
- Estado procesal conocido (última actuación, audiencia programada, etapa declarada).

## Outputs
- `tipo_tarea`: redacción | análisis factual | tipicidad | ruta 906 | representación víctima | evidencia | audiencia | tutela/constitucional | seguimiento | fuera_de_alcance.
- `etapa_aparente`: indagación | investigación | imputación | juicio | ejecución | desconocida | `[PENDIENTE DE VERIFICAR]`.
- `agente_destino` recomendado (uno o secuencia).
- `datos_faltantes_bloqueantes` (lista corta) o confirmación de derivación.
- `urgencia_preliminar`: sí/no (disparar `detectar_urgencia_penal` si sí).

## Steps
1. Analizar solicitud del usuario y objetivo del turno.
2. Clasificar tipo de tarea y etapa procesal aparente del caso.
3. Derivar al agente especialista correcto o pedir datos faltantes.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_expediente_search`
- `case_state_reader`
- `audit_log_write`

## Guardrails (g1–g10)
- **g1:** No inventar etapa, radicado ni actuaciones para justificar derivación.
- **g2:** Sin radicado ni actuaciones mínimas, no concluir etapa; marcar `desconocida` y pedir datos.
- **g3:** Etapa aparente es hipótesis de enrutamiento, no conclusión procesal definitiva.
- **g4:** Derivación con implicación estratégica (tutela, memorial, audiencia) requiere revisión del abogado.
- **g7:** Consultas no penales o ajenas a representación de víctimas en Colombia → declarar fuera de alcance y no derivar a redactor.
- **g8:** Cerrar con aviso de revisión profesional.

## Rol en analista_ruta_procesal
Clasificación de tarea cuando la consulta es procesal (etapa, oportunidad, actuación). Comparte skill con coordinador; aquí profundiza etapa aparente.

## Handoff (derivación típica)
- Análisis factual → `analista_cronologia_hechos_penales` (`extraer_hechos_relevantes`).
- Tipicidad / calificación → `analista_tipicidad_y_responsabilidad_penal` (solo con hechos mínimos).
- Ruta Ley 906 → `analista_ruta_procesal_ley906`.
- Tutela → `evaluador_derechos_fundamentales_tutela` (nunca redactor directo).
- Urgencia detectada → `detectar_urgencia_penal` antes de derivar.

## No duplicar
- No determinar etapa con rigor procesal (`identificar_etapa_procesal_ley906` → especialista ruta 906).
- No inventariar faltantes documentales (`gestionar_faltantes_expediente`).
- No evaluar urgencia en detalle (`detectar_urgencia_penal`).

## Riesgo si se omite
Derivación errónea retrasa actuaciones, mezcla competencias y puede hacer perder términos en Ley 906.
