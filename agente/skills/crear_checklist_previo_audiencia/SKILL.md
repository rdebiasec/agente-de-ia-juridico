---
name: crear-checklist-previo-audiencia
description: Skill atomico penal-victimas: listar requisitos antes de audiencia. Use when the workflow requires `crear_checklist_previo_audiencia`.
disable-model-invocation: true
---

# crear_checklist_previo_audiencia

## Scope
- Category: `Skills de audiencias`
- Skill ID: `crear_checklist_previo_audiencia`

## Used By Agents
- `preparador_estrategico_audiencias_penales`
- `gestor_seguimiento_procesal_penal`

## Purpose
listar requisitos antes de audiencia.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
poder, radicado, enlace, hora, documentos, anexos, identificacion, estrategia, responsables.

## Tools
- `calendar_event_reader`
- `document_bundle_builder`
- `task_manager_create`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
