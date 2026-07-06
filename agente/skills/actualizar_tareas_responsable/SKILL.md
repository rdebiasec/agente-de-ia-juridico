---
name: actualizar-tareas-responsable
description: Skill atomico penal-victimas: mantener lista de tareas por agente o abogado. Use when the workflow requires `actualizar_tareas_responsable`.
disable-model-invocation: true
---

# actualizar_tareas_responsable

## Scope
- Category: `Skills de seguimiento procesal`
- Skill ID: `actualizar_tareas_responsable`

## Used By Agents
- `coordinador_expediente_penal`
- `gestor_seguimiento_procesal_penal`

## Purpose
mantener lista de tareas por agente o abogado.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
tarea, responsable, fecha limite, dependencia, estado.

## Tools
- `task_manager_create`
- `task_manager_update`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
