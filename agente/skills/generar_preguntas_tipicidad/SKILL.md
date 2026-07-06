---
name: generar-preguntas-tipicidad
description: Skill atomico penal-victimas: crear preguntas para completar elementos del tipo penal. Use when the workflow requires `generar_preguntas_tipicidad`.
disable-model-invocation: true
---

# generar_preguntas_tipicidad

## Scope
- Category: `Skills de tipicidad y responsabilidad penal`
- Skill ID: `generar_preguntas_tipicidad`

## Used By Agents
- `analista_tipicidad_y_responsabilidad_penal`
- `analista_cronologia_hechos_penales`

## Purpose
crear preguntas para completar elementos del tipo penal.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
pregunta, elemento que busca aclarar, riesgo de induccion.

## Tools
- `sin_herramientas_obligatorias`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
