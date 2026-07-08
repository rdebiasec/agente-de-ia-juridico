---
name: identificar-etapa-procesal-ley906
description: Skill estrategico penal-victimas: determinar etapa del caso segun Ley 906. Use when the workflow requires `identificar_etapa_procesal_ley906`.
disable-model-invocation: true
---

# identificar_etapa_procesal_ley906

## Scope
- Category: `Skills de ruta procesal Ley 906`
- Skill ID: `identificar_etapa_procesal_ley906`
- Tier: `estrategico`

## Used By Agents
- `analista_ruta_procesal_ley906` (skill primario del agente)
- `coordinador_expediente_penal`

## Purpose
Determinar la etapa procesal del caso penal bajo Ley 906 de 2004 con base en actuaciones verificables, señalando incertidumbres.

## Rol en analista_ruta_procesal
Primer paso del agente tras recibir caso del coordinador. Toda actuación posterior depende de etapa confirmada o `[PENDIENTE DE VERIFICAR]`.

## Rol en coordinador
Hipótesis de etapa para enrutamiento cuando el abogado no la indica. Derivar al analista ruta 906 para determinación definitiva.

## Inputs
- Radicado y últimas actuaciones procesales (auto, informe, audiencia, imputación).
- Consulta a estado del proceso (`process_lookup_query`) si está disponible.
- Fechas y tipos de actuación en expediente.
- Declaración de etapa por el abogado (si existe) para contrastar.

## Outputs
- `etapa_ley906`: indagación | investigación | etapa_intermedia | juicio | ejecución_penal | archivo | `[PENDIENTE DE VERIFICAR]`.
- `evidencia_etapa`: actuación + fecha + fuente.
- `incertidumbres` y `siguiente_dato_a_verificar`.
- Nota: conclusión preliminar, no dictamen procesal vinculante.

## Steps
1. Revisar actuaciones y estado del radicado.
2. Determinar etapa procesal según Ley 906 (indagación, investigación, juicio, etc.).
3. Señalar incertidumbres si el expediente es incompleto.
4. Señalar actuaciones habilitadas en la etapa identificada.
5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_expediente_search`
- `process_lookup_query`
- `rag_ley906_search`

## Guardrails (g1–g10)
- **g1:** No inventar actuaciones ni fechas para ubicar etapa.
- **g2:** Expediente incompleto → etapa `[PENDIENTE DE VERIFICAR]` y pedir actuación fundante.
- **g3:** Distinguir etapa inferida de etapa acreditada en auto o estado del radicado.
- **g4:** Etapa incorrecta invalida oportunidad de solicitudes; HITL obligatorio.
- **g7:** Solo aplica a proceso penal Ley 906 en Colombia.
- **g9:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **g8:** Aviso de revisión profesional.

## Handoff
- Salida alimenta: `mapear_actuaciones_posibles_victima`, `evaluar_oportunidad_procesal`, `controlar_terminos_procesales_preliminares`.

## No duplicar
- No evaluar oportunidad de actuaciones (`evaluar_oportunidad_procesal`).
- No clasificar tarea del turno (`clasificar_tarea_y_etapa`).

## Riesgo si se omite
Solicitudes extemporáneas o improcedentes por error en etapa.
