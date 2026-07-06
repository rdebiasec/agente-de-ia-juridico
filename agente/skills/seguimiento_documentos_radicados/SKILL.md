---
name: seguimiento-documentos-radicados
description: Skill atomico penal-victimas: controlar documentos enviados y respuestas pendientes. Use when the workflow requires `seguimiento_documentos_radicados`.
disable-model-invocation: true
---

# seguimiento_documentos_radicados

## Scope
- Category: `Skills de seguimiento procesal`
- Skill ID: `seguimiento_documentos_radicados`

## Used By Agents
- `gestor_seguimiento_procesal_penal`

## Purpose
controlar documentos enviados y respuestas pendientes.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
documento, fecha radicacion, autoridad, respuesta esperada, alerta.

## Tools
- `document_version_control`
- `case_state_writer`
- `task_manager_update`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
