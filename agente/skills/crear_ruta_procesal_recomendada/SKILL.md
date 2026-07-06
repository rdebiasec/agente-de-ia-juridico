---
name: crear-ruta-procesal-recomendada
description: Skill atomico penal-victimas: crear plan de proximos pasos procesales para revision del abogado. Use when the workflow requires `crear_ruta_procesal_recomendada`.
disable-model-invocation: true
---

# crear_ruta_procesal_recomendada

## Scope
- Category: `Skills de ruta procesal Ley 906`
- Skill ID: `crear_ruta_procesal_recomendada`

## Used By Agents
- `analista_ruta_procesal_ley906`
- `coordinador_expediente_penal`

## Purpose
crear plan de proximos pasos procesales para revision del abogado.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
ruta, pasos, prioridad, dependencias, agentes involucrados.

## Tools
- `task_manager_create`
- `audit_log_write`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
