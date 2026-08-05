<!-- config-version: 2; checksum: a6246750767df617 -->
---
name: identificar-etapa-procesal-ley906
description: Contrato penal-víctimas: Determinar la etapa procesal del caso penal bajo Ley 906 de 2004 con base en actuaciones verificables, señalando incertidumbres. Activar cuando el plan/HITL o el especialista requiera `identificar_etapa_procesal_ley906`. No sustituye a `evaluar_oportun...
disable-model-invocation: true
---

# identificar_etapa_procesal_ley906

## Scope
- Category: `Skills de ruta procesal Ley 906`
- Skill ID: `identificar_etapa_procesal_ley906`
- Tier: `estrategico`

## Used By Agents
- `analista_ruta_procesal` (skill primario del agente)

## Purpose
Determinar la etapa procesal del caso penal bajo Ley 906 de 2004 con base en actuaciones verificables, señalando incertidumbres.

## Rol en analista_ruta_procesal
Primer paso del agente tras recibir caso del coordinador. Toda actuación posterior depende de etapa confirmada o `[PENDIENTE DE VERIFICAR]`.

## Rol en coordinador_caso
**MOVE:** este skill ya no es ownership del POC. El coordinador solo lo dispara vía tool del especialista dueño.

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
1. Identificar etapa aparente con base en actuaciones/radicado aportados.
2. Justificar con hechos procesales; marcar incertidumbre si faltan datos.
3. No inventar actuaciones ni fechas de audiencia.
4. Derivar ruta completa a `crear_ruta_procesal_recomendada` si se pide plan.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `identificar_etapa_procesal_ley906`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_expediente_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `process_lookup_query` — no implementada
- `rag_ley906_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto

## Guardrails
- **No inventar:** No inventar actuaciones ni fechas para ubicar etapa.
- **Pedir datos faltantes:** Expediente incompleto → etapa `[PENDIENTE DE VERIFICAR]` y pedir actuación fundante.
- **Separar hecho de inferencia:** Distinguir etapa inferida de etapa acreditada en auto o estado del radicado.
- **Revision humana obligatoria:** Etapa incorrecta invalida oportunidad de solicitudes; HITL obligatorio.
- **Fuera de alcance:** Solo aplica a proceso penal Ley 906 en Colombia.
- **Oportunidad y terminos Ley 906:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **Aviso de borrador:** Aviso de revisión profesional.

## Handoff
- Salida alimenta: `mapear_actuaciones_posibles_victima`, `evaluar_oportunidad_procesal`, `controlar_terminos_procesales_preliminares`.

## No duplicar
- No evaluar oportunidad de actuaciones (`evaluar_oportunidad_procesal`).
- No clasificar tarea del turno (`clasificar_tarea_y_etapa`).

## Riesgo si se omite
Solicitudes extemporáneas o improcedentes por error en etapa.
