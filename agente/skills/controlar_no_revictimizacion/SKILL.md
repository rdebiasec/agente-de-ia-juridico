---
name: controlar-no-revictimizacion
description: Skill atomico penal-victimas: revisar que la salida no culpe ni exponga indebidamente a la victima. Use when the workflow requires `controlar_no_revictimizacion`.
disable-model-invocation: true
---

# controlar_no_revictimizacion

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `controlar_no_revictimizacion`

## Used By Agents
- `analista_calidad_juridica`
- `analista_representacion_victimas`

## Purpose
revisar que la salida no culpe ni exponga indebidamente a la victima.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
fragmento, riesgo, alternativa.

## Tools
- `revictimization_risk_checker`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
