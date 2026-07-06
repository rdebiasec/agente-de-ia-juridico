---
name: detectar-agravantes-atenuantes
description: Skill atomico penal-victimas: identificar circunstancias relevantes que puedan afectar gravedad juridica. Use when the workflow requires `detectar_agravantes_atenuantes`.
disable-model-invocation: true
---

# detectar_agravantes_atenuantes

## Scope
- Category: `Skills de tipicidad y responsabilidad penal`
- Skill ID: `detectar_agravantes_atenuantes`

## Used By Agents
- `analista_tipicidad_y_responsabilidad_penal`

## Purpose
identificar circunstancias relevantes que puedan afectar gravedad juridica.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
circunstancia, fuente normativa, hecho soporte, prueba, riesgo.

## Tools
- `rag_codigo_penal_search`
- `rag_expediente_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
