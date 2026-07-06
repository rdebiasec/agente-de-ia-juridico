---
name: detectar-contradicciones-factuales
description: Skill atomico penal-victimas: encontrar inconsistencias entre versiones, documentos, fechas, valores o actores. Use when the workflow requires `detectar_contradicciones_factuales`.
disable-model-invocation: true
---

# detectar_contradicciones_factuales

## Scope
- Category: `Skills de hechos y cronologia`
- Skill ID: `detectar_contradicciones_factuales`

## Used By Agents
- `analista_cronologia_hechos_penales`
- `analista_calidad_juridica`

## Purpose
encontrar inconsistencias entre versiones, documentos, fechas, valores o actores.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
contradiccion, fuentes en tension, impacto, pregunta de aclaracion.

## Tools
- `rag_expediente_search`
- `entity_extractor`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
