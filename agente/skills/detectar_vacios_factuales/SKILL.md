---
name: detectar-vacios-factuales
description: Skill atomico penal-victimas: identificar lo que falta para comprender o probar el caso. Use when the workflow requires `detectar_vacios_factuales`.
disable-model-invocation: true
---

# detectar_vacios_factuales

## Scope
- Category: `Skills de hechos y cronologia`
- Skill ID: `detectar_vacios_factuales`

## Used By Agents
- `analista_cronologia_hechos_penales`
- `coordinador_expediente_penal`

## Purpose
identificar lo que falta para comprender o probar el caso.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
vacios, prioridad, agente responsable, pregunta sugerida.

## Tools
- `case_state_reader`
- `rag_expediente_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
