---
name: monitorear-radicado
description: Skill atomico penal-victimas: consultar o registrar estado de radicado. Use when the workflow requires `monitorear_radicado`.
disable-model-invocation: true
---

# monitorear_radicado

## Scope
- Category: `Skills de seguimiento procesal`
- Skill ID: `monitorear_radicado`

## Used By Agents
- `gestor_seguimiento_procesal_penal`

## Purpose
consultar o registrar estado de radicado.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
estado, ultima actuacion, fuente, fecha consulta, incertidumbres.

## Tools
- `process_lookup_query`
- `audit_log_write`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
