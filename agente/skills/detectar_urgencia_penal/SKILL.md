---
name: detectar-urgencia-penal
description: Skill atomico penal-victimas: identificar si el caso requiere atencion humana inmediata. Use when the workflow requires `detectar_urgencia_penal`.
disable-model-invocation: true
---

# detectar_urgencia_penal

## Scope
- Category: `Skills transversales`
- Skill ID: `detectar_urgencia_penal`

## Used By Agents
- `coordinador_expediente_penal`
- `gestor_seguimiento_procesal_penal`
- `analista_calidad_juridica`

## Purpose
identificar si el caso requiere atencion humana inmediata.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
urgencias, nivel de severidad, accion inmediata, agente/humano responsable.

## Tools
- `calendar_terms_calculator`
- `case_state_reader`
- `notification_create`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
