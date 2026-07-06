---
name: detectar-riesgo-revictimizacion
description: Skill atomico penal-victimas: identificar lenguaje, preguntas, acciones o estrategias que puedan revictimizar. Use when the workflow requires `detectar_riesgo_revictimizacion`.
disable-model-invocation: true
---

# detectar_riesgo_revictimizacion

## Scope
- Category: `Skills de representacion de victimas`
- Skill ID: `detectar_riesgo_revictimizacion`

## Used By Agents
- `analista_representacion_victimas`
- `preparador_estrategico_audiencias_penales`
- `analista_calidad_juridica`

## Purpose
identificar lenguaje, preguntas, acciones o estrategias que puedan revictimizar.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
riesgo, ubicacion, recomendacion, severidad.

## Tools
- `revictimization_risk_checker`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
