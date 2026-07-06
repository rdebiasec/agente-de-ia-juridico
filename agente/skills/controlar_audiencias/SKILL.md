---
name: controlar-audiencias
description: Skill atomico penal-victimas: administrar fechas, horas, enlaces y preparacion de audiencias. Use when the workflow requires `controlar_audiencias`.
disable-model-invocation: true
---

# controlar_audiencias

## Scope
- Category: `Skills de seguimiento procesal`
- Skill ID: `controlar_audiencias`

## Used By Agents
- `gestor_seguimiento_procesal_penal`
- `preparador_estrategico_audiencias_penales`

## Purpose
administrar fechas, horas, enlaces y preparacion de audiencias.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
audiencia, fecha, tipo, documentos requeridos, responsable.

## Tools
- `calendar_event_create`
- `calendar_event_reader`
- `task_manager_create`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
