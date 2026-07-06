---
name: identificar-conductas-punibles-preliminares
description: Skill atomico penal-victimas: proponer posibles conductas punibles con base en hechos, sin conclusion definitiva. Use when the workflow requires `identificar_conductas_punibles_preliminares`.
disable-model-invocation: true
---

# identificar_conductas_punibles_preliminares

## Scope
- Category: `Skills de tipicidad y responsabilidad penal`
- Skill ID: `identificar_conductas_punibles_preliminares`

## Used By Agents
- `analista_tipicidad_y_responsabilidad_penal`

## Purpose
proponer posibles conductas punibles con base en hechos, sin conclusion definitiva.

## Inputs
cronologia, hechos soportados, objetivo de victima.

## Outputs
posibles delitos, razon preliminar, fuentes normativas, nivel de confianza.

## Tools
- `rag_codigo_penal_search`
- `rag_normativo_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
