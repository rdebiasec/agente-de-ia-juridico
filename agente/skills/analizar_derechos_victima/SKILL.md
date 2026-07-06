---
name: analizar-derechos-victima
description: Skill atomico penal-victimas: mapear derechos de victima aplicables al caso. Use when the workflow requires `analizar_derechos_victima`.
disable-model-invocation: true
---

# analizar_derechos_victima

## Scope
- Category: `Skills de representacion de victimas`
- Skill ID: `analizar_derechos_victima`

## Used By Agents
- `analista_representacion_victimas`
- `evaluador_derechos_fundamentales_tutela`

## Purpose
mapear derechos de victima aplicables al caso.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
derecho, hecho relacionado, oportunidad procesal, fuente.

## Tools
- `rag_normas_victimas_search`
- `rag_constitucional_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
