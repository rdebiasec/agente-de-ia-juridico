---
name: preparar-guion-intervencion-oral
description: Skill atomico penal-victimas: estructurar intervencion oral clara y breve. Use when the workflow requires `preparar_guion_intervencion_oral`.
disable-model-invocation: true
---

# preparar_guion_intervencion_oral

## Scope
- Category: `Skills de audiencias`
- Skill ID: `preparar_guion_intervencion_oral`

## Used By Agents
- `preparador_estrategico_audiencias_penales`

## Purpose
estructurar intervencion oral clara y breve.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
apertura, puntos, solicitudes, cierre, advertencias.

## Tools
- `hearing_template_loader`
- `rag_ley906_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
