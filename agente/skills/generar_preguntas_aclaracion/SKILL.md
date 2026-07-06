---
name: generar-preguntas-aclaracion
description: Skill atomico penal-victimas: crear preguntas para victima, testigos o abogado humano sin inducir respuestas. Use when the workflow requires `generar_preguntas_aclaracion`.
disable-model-invocation: true
---

# generar_preguntas_aclaracion

## Scope
- Category: `Skills de hechos y cronologia`
- Skill ID: `generar_preguntas_aclaracion`

## Used By Agents
- `analista_cronologia_hechos_penales`
- `gestor_evidencia_y_soporte_probatorio`

## Purpose
crear preguntas para victima, testigos o abogado humano sin inducir respuestas.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
preguntas neutrales, objetivo de cada pregunta, riesgo asociado.

## Tools
- `sin_herramientas_obligatorias`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
