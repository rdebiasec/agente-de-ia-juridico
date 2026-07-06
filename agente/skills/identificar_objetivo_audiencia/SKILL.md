---
name: identificar-objetivo-audiencia
description: Skill atomico penal-victimas: definir objetivo juridico y tactico de la audiencia para la victima. Use when the workflow requires `identificar_objetivo_audiencia`.
disable-model-invocation: true
---

# identificar_objetivo_audiencia

## Scope
- Category: `Skills de audiencias`
- Skill ID: `identificar_objetivo_audiencia`

## Used By Agents
- `preparador_estrategico_audiencias_penales`

## Purpose
definir objetivo juridico y tactico de la audiencia para la victima.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
objetivo, limites, solicitudes posibles, riesgos.

## Tools
- `rag_ley906_search`
- `calendar_event_reader`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
