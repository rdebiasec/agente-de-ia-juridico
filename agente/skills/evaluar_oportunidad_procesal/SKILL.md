---
name: evaluar-oportunidad-procesal
description: Skill atomico penal-victimas: determinar si una solicitud o intervencion es oportuna, prematura o extemporanea. Use when the workflow requires `evaluar_oportunidad_procesal`.
disable-model-invocation: true
---

# evaluar_oportunidad_procesal

## Scope
- Category: `Skills de ruta procesal Ley 906`
- Skill ID: `evaluar_oportunidad_procesal`

## Used By Agents
- `analista_ruta_procesal_ley906`
- `analista_calidad_juridica`

## Purpose
determinar si una solicitud o intervencion es oportuna, prematura o extemporanea.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
decision preliminar, razon, datos faltantes, riesgo.

## Tools
- `rag_ley906_search`
- `calendar_terms_calculator`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
