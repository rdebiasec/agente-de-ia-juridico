---
name: construir-teoria-caso-victima
description: Skill atomico penal-victimas: formular teoria preliminar desde la victima. Use when the workflow requires `construir_teoria_caso_victima`.
disable-model-invocation: true
---

# construir_teoria_caso_victima

## Scope
- Category: `Skills de representacion de victimas`
- Skill ID: `construir_teoria_caso_victima`

## Used By Agents
- `analista_representacion_victimas`
- `preparador_estrategico_audiencias_penales`

## Purpose
formular teoria preliminar desde la victima.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
teoria del caso, hechos clave, pruebas clave, riesgos, narrativa juridica.

## Tools
- `rag_expediente_search`
- `rag_normativo_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
