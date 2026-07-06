---
name: identificar-actores-y-roles
description: Skill atomico penal-victimas: identificar victima, presunto responsable, testigos, autoridades, terceros y entidades. Use when the workflow requires `identificar_actores_y_roles`.
disable-model-invocation: true
---

# identificar_actores_y_roles

## Scope
- Category: `Skills de hechos y cronologia`
- Skill ID: `identificar_actores_y_roles`

## Used By Agents
- `analista_cronologia_hechos_penales`
- `analista_representacion_victimas`

## Purpose
identificar victima, presunto responsable, testigos, autoridades, terceros y entidades.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
mapa de actores, rol, fuente, relevancia, datos sensibles.

## Tools
- `entity_extractor`
- `pii_detector`
- `rag_expediente_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
