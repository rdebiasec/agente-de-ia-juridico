---
name: controlar-confidencialidad-datos-sensibles
description: Skill atomico penal-victimas: detectar datos sensibles o innecesarios. Use when the workflow requires `controlar_confidencialidad_datos_sensibles`.
disable-model-invocation: true
---

# controlar_confidencialidad_datos_sensibles

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `controlar_confidencialidad_datos_sensibles`

## Used By Agents
- `analista_calidad_juridica`

## Purpose
detectar datos sensibles o innecesarios.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
dato, riesgo, accion, anonimizar si aplica.

## Tools
- `pii_detector`
- `sensitive_data_classifier`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
