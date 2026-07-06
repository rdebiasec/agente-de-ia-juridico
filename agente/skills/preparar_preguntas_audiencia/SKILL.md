---
name: preparar-preguntas-audiencia
description: Skill atomico penal-victimas: sugerir preguntas para victima, testigos o peritos. Use when the workflow requires `preparar_preguntas_audiencia`.
disable-model-invocation: true
---

# preparar_preguntas_audiencia

## Scope
- Category: `Skills de audiencias`
- Skill ID: `preparar_preguntas_audiencia`

## Used By Agents
- `preparador_estrategico_audiencias_penales`

## Purpose
sugerir preguntas para victima, testigos o peritos.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
pregunta, objetivo, tipo, riesgo, fundamento.

## Tools
- `rag_expediente_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
