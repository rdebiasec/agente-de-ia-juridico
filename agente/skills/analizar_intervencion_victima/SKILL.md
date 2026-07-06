---
name: analizar-intervencion-victima
description: Skill atomico penal-victimas: definir intervencion posible de la victima en una actuacion o audiencia. Use when the workflow requires `analizar_intervencion_victima`.
disable-model-invocation: true
---

# analizar_intervencion_victima

## Scope
- Category: `Skills de ruta procesal Ley 906`
- Skill ID: `analizar_intervencion_victima`

## Used By Agents
- `analista_ruta_procesal_ley906`
- `preparador_estrategico_audiencias_penales`

## Purpose
definir intervencion posible de la victima en una actuacion o audiencia.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
objetivo, limite de intervencion, solicitudes posibles, riesgos.

## Tools
- `rag_ley906_search`
- `rag_normas_victimas_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
