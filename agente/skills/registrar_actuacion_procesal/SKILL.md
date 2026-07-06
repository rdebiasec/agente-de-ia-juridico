---
name: registrar-actuacion-procesal
description: Skill atomico penal-victimas: registrar una actuacion nueva en la bitacora del caso. Use when the workflow requires `registrar_actuacion_procesal`.
disable-model-invocation: true
---

# registrar_actuacion_procesal

## Scope
- Category: `Skills de seguimiento procesal`
- Skill ID: `registrar_actuacion_procesal`

## Used By Agents
- `gestor_seguimiento_procesal_penal`

## Purpose
registrar una actuacion nueva en la bitacora del caso.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
actuacion, fecha, fuente, impacto operativo, tareas.

## Tools
- `case_state_writer`
- `audit_log_write`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
