---
name: marcar-pendientes-verificacion
description: Skill atomico penal-victimas: marcar cualquier dato, cita o hecho incompleto como `[PENDIENTE DE VERIFICAR]`. Use when the workflow requires `marcar_pendientes_verificacion`.
disable-model-invocation: true
---

# marcar_pendientes_verificacion

## Scope
- Category: `Skills transversales`
- Skill ID: `marcar_pendientes_verificacion`

## Used By Agents
- `coordinador_expediente_penal`

## Purpose
marcar cualquier dato, cita o hecho incompleto como `[PENDIENTE DE VERIFICAR]`.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
texto marcado, lista de pendientes, impacto juridico.

## Tools
- `audit_log_write`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
