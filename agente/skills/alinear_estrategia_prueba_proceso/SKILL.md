---
name: alinear-estrategia-prueba-proceso
description: Skill atomico penal-victimas: alinear teoria de victima con ruta procesal y plan probatorio. Use when the workflow requires `alinear_estrategia_prueba_proceso`.
disable-model-invocation: true
---

# alinear_estrategia_prueba_proceso

## Scope
- Category: `Skills de representacion de victimas`
- Skill ID: `alinear_estrategia_prueba_proceso`

## Used By Agents
- `analista_representacion_victimas`
- `analista_calidad_juridica`

## Purpose
alinear teoria de victima con ruta procesal y plan probatorio.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
alineacion, contradicciones, ajustes, tareas.

## Tools
- `case_state_reader`
- `rag_expediente_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
