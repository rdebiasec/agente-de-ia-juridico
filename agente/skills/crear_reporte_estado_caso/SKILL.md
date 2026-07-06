---
name: crear-reporte-estado-caso
description: Skill atomico penal-victimas: crear reporte interno periodico. Use when the workflow requires `crear_reporte_estado_caso`.
disable-model-invocation: true
---

# crear_reporte_estado_caso

## Scope
- Category: `Skills de seguimiento procesal`
- Skill ID: `crear_reporte_estado_caso`

## Used By Agents
- `gestor_seguimiento_procesal_penal`

## Purpose
crear reporte interno periodico.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
estado, ultimas actuaciones, proximos hitos, tareas, riesgos.

## Tools
- `case_state_reader`
- `audit_log_write`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
