---
name: controlar-terminos-procesales-preliminares
description: Skill atomico penal-victimas: identificar y alertar terminos relevantes. No reemplaza calculo humano. Use when the workflow requires `controlar_terminos_procesales_preliminares`.
disable-model-invocation: true
---

# controlar_terminos_procesales_preliminares

## Scope
- Category: `Skills de ruta procesal Ley 906`
- Skill ID: `controlar_terminos_procesales_preliminares`

## Used By Agents
- `analista_ruta_procesal_ley906`
- `gestor_seguimiento_procesal_penal`

## Purpose
identificar y alertar terminos relevantes. No reemplaza calculo humano.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
termino, fecha base, fecha limite estimada, nivel de confianza, pendientes.

## Tools
- `calendar_terms_calculator`
- `calendar_event_create`
- `audit_log_write`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
