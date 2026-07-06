---
name: controlar-tono-riesgo-reputacional
description: Skill atomico penal-victimas: revisar tono profesional y evitar lenguaje riesgoso. Use when the workflow requires `controlar_tono_riesgo_reputacional`.
disable-model-invocation: true
---

# controlar_tono_riesgo_reputacional

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `controlar_tono_riesgo_reputacional`

## Used By Agents
- `analista_calidad_juridica`
- `redactor_documentos_juridicos_penales`

## Purpose
revisar tono profesional y evitar lenguaje riesgoso.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
fragmento, riesgo, sugerencia.

## Tools
- `tone_checker`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
