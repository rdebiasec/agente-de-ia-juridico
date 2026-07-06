---
name: detectar-riesgos-atipicidad
description: Skill atomico penal-victimas: detectar cuando un caso puede ser atipico o tener naturaleza no penal. Use when the workflow requires `detectar_riesgos_atipicidad`.
disable-model-invocation: true
---

# detectar_riesgos_atipicidad

## Scope
- Category: `Skills de tipicidad y responsabilidad penal`
- Skill ID: `detectar_riesgos_atipicidad`

## Used By Agents
- `analista_tipicidad_y_responsabilidad_penal`
- `analista_calidad_juridica`

## Purpose
detectar cuando un caso puede ser atipico o tener naturaleza no penal.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
riesgo, razon, hecho faltante, prueba faltante, recomendacion interna.

## Tools
- `rag_jurisprudencia_penal_search`
- `rag_expediente_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
