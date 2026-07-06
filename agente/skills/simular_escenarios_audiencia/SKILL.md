---
name: simular-escenarios-audiencia
description: Skill atomico penal-victimas: plantear escenarios probables y preparacion del abogado. Use when the workflow requires `simular_escenarios_audiencia`.
disable-model-invocation: true
---

# simular_escenarios_audiencia

## Scope
- Category: `Skills de audiencias`
- Skill ID: `simular_escenarios_audiencia`

## Used By Agents
- `preparador_estrategico_audiencias_penales`

## Purpose
plantear escenarios probables y preparacion del abogado.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
escenario, probabilidad preliminar, impacto, respuesta sugerida.

## Tools
- `rag_expediente_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
