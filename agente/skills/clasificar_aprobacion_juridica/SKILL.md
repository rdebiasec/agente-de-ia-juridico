---
name: clasificar-aprobacion-juridica
description: Skill atomico penal-victimas: clasificar la salida como aprobable, aprobable con cambios, rechazada o escalar. Use when the workflow requires `clasificar_aprobacion_juridica`.
disable-model-invocation: true
---

# clasificar_aprobacion_juridica

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `clasificar_aprobacion_juridica`

## Used By Agents
- `analista_calidad_juridica`

## Purpose
clasificar la salida como aprobable, aprobable con cambios, rechazada o escalar.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
decision, razones, cambios, aprobador humano requerido.

## Tools
- `approval_gate_decision`
- `audit_log_write`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
