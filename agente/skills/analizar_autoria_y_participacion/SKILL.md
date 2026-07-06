---
name: analizar-autoria-y-participacion
description: Skill atomico penal-victimas: evaluar posibles roles de los intervinientes de manera preliminar. Use when the workflow requires `analizar_autoria_y_participacion`.
disable-model-invocation: true
---

# analizar_autoria_y_participacion

## Scope
- Category: `Skills de tipicidad y responsabilidad penal`
- Skill ID: `analizar_autoria_y_participacion`

## Used By Agents
- `analista_tipicidad_y_responsabilidad_penal`

## Purpose
evaluar posibles roles de los intervinientes de manera preliminar.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
actor, posible rol, hechos soporte, riesgos, pendientes.

## Tools
- `rag_codigo_penal_search`
- `rag_expediente_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
