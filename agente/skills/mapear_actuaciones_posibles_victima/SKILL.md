---
name: mapear-actuaciones-posibles-victima
description: Skill atomico penal-victimas: indicar que puede hacer la representacion de victimas segun etapa. Use when the workflow requires `mapear_actuaciones_posibles_victima`.
disable-model-invocation: true
---

# mapear_actuaciones_posibles_victima

## Scope
- Category: `Skills de ruta procesal Ley 906`
- Skill ID: `mapear_actuaciones_posibles_victima`

## Used By Agents
- `analista_ruta_procesal_ley906`
- `analista_representacion_victimas`

## Purpose
indicar que puede hacer la representacion de victimas segun etapa.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
actuacion posible, oportunidad, autoridad, soporte normativo, riesgo.

## Tools
- `rag_ley906_search`
- `rag_normas_victimas_search`
- `citation_checker`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
