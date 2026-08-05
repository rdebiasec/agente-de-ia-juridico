<!-- config-version: 2; checksum: 9def3638a96efeba -->
---
name: analizar-intervencion-victima
description: Contrato penal-víctimas: Definir formas de intervención procedentes de la víctima en una actuación o audiencia específica bajo Ley 906. Activar cuando el plan/HITL o el especialista requiera `analizar_intervencion_victima`. No sustituye a `preparar_guion_intervencion_oral`.
disable-model-invocation: true
---

# analizar_intervencion_victima

## Scope
- Category: `Skills de ruta procesal Ley 906`
- Skill ID: `analizar_intervencion_victima`
- Tier: `estrategico`

## Used By Agents
- `analista_ruta_procesal`
- `analista_audiencias`

## Purpose
Definir formas de intervención procedentes de la víctima en una actuación o audiencia específica bajo Ley 906.

## Rol en analista_ruta_procesal
Marco procesal de intervención (qué puede pedir la víctima y cuándo). La preparación táctica oral la hace `analista_audiencias`.

## Rol en analista_audiencias
Usar este marco como base para guion, preguntas y solicitudes orales.

## Inputs
- Tipo de audiencia o actuación (fecha si consta).
- Etapa procesal.
- Objetivos de la víctima.
- Norma Ley 906 y derechos de víctimas.

## Outputs
- `formas_intervencion_procedentes` (oral, escrita, solicitudes, etc.).
- `contenido_sugerido` y `momento_procesal`.
- `limites` de intervención.
- `riesgos` (revictimización, revelación de estrategia).
- Etiqueta: `MARCO PROCESAL — PREPARACIÓN TÁCTICA EN OTRO AGENTE`.

## Steps
1. Identificar actuación o audiencia específica y marco Ley 906.
2. Determinar formas de intervención de la víctima procedentes.
3. Proponer contenido y momento de la intervención.
4. Documentar riesgos procesales si la intervención no es oportuna.
5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `analizar_intervencion_victima`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_ley906_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `rag_normas_victimas_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto

## Guardrails
- **No inventar:** No inventar facultades de intervención no previstas en norma verificada.
- **Revision humana obligatoria:** HITL antes de que la víctima intervenga en audiencia.
- **No revictimizar:** Minimizar exposición innecesaria de la víctima.
- **Oportunidad y terminos Ley 906:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No guion oral (`preparar_guion_intervencion_oral`).
- No solicitudes orales detalladas (`preparar_solicitudes_orales` en preparador).

## Riesgo si se omite
Intervención extemporánea o improcedente de la víctima en audiencia.
