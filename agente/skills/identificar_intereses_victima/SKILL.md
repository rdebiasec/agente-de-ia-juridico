---
name: identificar-intereses-victima
description: Skill atomico penal-victimas: aclarar el objetivo real de la victima. Use when the workflow requires `identificar_intereses_victima`.
disable-model-invocation: true
---

# identificar_intereses_victima

## Scope
- Category: `Skills de representacion de victimas`
- Skill ID: `identificar_intereses_victima`

## Used By Agents
- `analista_representacion_victimas`

## Purpose
aclarar el objetivo real de la victima.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
objetivos principales, secundarios, tensiones, decisiones humanas necesarias.

## Tools
- `rag_expediente_search`
- `victim_objective_mapper`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
