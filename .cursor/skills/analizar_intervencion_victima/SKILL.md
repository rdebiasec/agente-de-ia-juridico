---
name: analizar-intervencion-victima
description: Skill estrategico penal-victimas: definir intervencion posible de la victima en una actuacion o audiencia. Use when the workflow requires `analizar_intervencion_victima`.
disable-model-invocation: true
---

# analizar_intervencion_victima

## Scope
- Category: `Skills de ruta procesal Ley 906`
- Skill ID: `analizar_intervencion_victima`
- Tier: `estrategico`

## Used By Agents
- `analista_ruta_procesal_ley906`
- `preparador_estrategico_audiencias_penales`

## Purpose
Definir formas de intervención procedentes de la víctima en una actuación o audiencia específica bajo Ley 906.

## Rol en analista_ruta_procesal
Marco procesal de intervención (qué puede pedir la víctima y cuándo). La preparación táctica oral la hace `preparador_estrategico_audiencias_penales`.

## Rol en preparador_audiencias
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
- `rag_ley906_search`
- `rag_normas_victimas_search`

## Guardrails (g1–g10)
- **g1:** No inventar facultades de intervención no previstas en norma verificada.
- **g4:** HITL antes de que la víctima intervenga en audiencia.
- **g5:** Minimizar exposición innecesaria de la víctima.
- **g9:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No guion oral (`preparar_guion_intervencion_oral`).
- No solicitudes orales detalladas (`preparar_solicitudes_orales` en preparador).

## Riesgo si se omite
Intervención extemporánea o improcedente de la víctima en audiencia.
