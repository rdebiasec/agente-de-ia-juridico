---
name: detectar-inactividad-procesal
description: Skill atomico penal-victimas: alertar falta de movimientos por periodo relevante. Use when the workflow requires `detectar_inactividad_procesal`.
disable-model-invocation: true
---

# detectar_inactividad_procesal

## Scope
- Category: `Skills de seguimiento procesal`
- Skill ID: `detectar_inactividad_procesal`

## Used By Agents
- `gestor_seguimiento_procesal_penal`
- `analista_ruta_procesal_ley906`

## Purpose
alertar falta de movimientos por periodo relevante.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
periodo, ultima actuacion, riesgo, accion sugerida.

## Tools
- `process_lookup_query`
- `case_state_reader`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
