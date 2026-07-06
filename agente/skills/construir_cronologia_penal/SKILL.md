---
name: construir-cronologia-penal
description: Skill atomico penal-victimas: ordenar hechos en linea de tiempo. Use when the workflow requires `construir_cronologia_penal`.
disable-model-invocation: true
---

# construir_cronologia_penal

## Scope
- Category: `Skills de hechos y cronologia`
- Skill ID: `construir_cronologia_penal`

## Used By Agents
- `analista_cronologia_hechos_penales`
- `preparador_estrategico_audiencias_penales`

## Purpose
ordenar hechos en linea de tiempo.

## Inputs
hechos extraidos, documentos, fechas, actores.

## Outputs
cronologia ordenada, hechos sin fecha, contradicciones temporales.

## Tools
- `date_extractor`
- `entity_extractor`
- `case_state_writer`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
