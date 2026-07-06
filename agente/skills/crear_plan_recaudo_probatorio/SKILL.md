---
name: crear-plan-recaudo-probatorio
description: Skill atomico penal-victimas: proponer plan para obtener pruebas faltantes. Use when the workflow requires `crear_plan_recaudo_probatorio`.
disable-model-invocation: true
---

# crear_plan_recaudo_probatorio

## Scope
- Category: `Skills de evidencia y soporte probatorio`
- Skill ID: `crear_plan_recaudo_probatorio`

## Used By Agents
- `gestor_evidencia_y_soporte_probatorio`
- `analista_representacion_victimas`

## Purpose
proponer plan para obtener pruebas faltantes.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
prueba requerida, fuente, medio, prioridad, responsable, riesgo.

## Tools
- `task_manager_create`
- `rag_expediente_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
