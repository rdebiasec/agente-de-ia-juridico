---
name: generar-alertas-terminos-vencimientos
description: Skill atomico penal-victimas: crear alertas de posibles vencimientos. Use when the workflow requires `generar_alertas_terminos_vencimientos`.
disable-model-invocation: true
---

# generar_alertas_terminos_vencimientos

## Scope
- Category: `Skills de seguimiento procesal`
- Skill ID: `generar_alertas_terminos_vencimientos`

## Used By Agents
- `gestor_seguimiento_procesal_penal`
- `analista_ruta_procesal_ley906`

## Purpose
crear alertas de posibles vencimientos.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
alerta, fecha base, fecha objetivo, responsable, nivel de confianza.

## Tools
- `calendar_terms_calculator`
- `notification_create`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
