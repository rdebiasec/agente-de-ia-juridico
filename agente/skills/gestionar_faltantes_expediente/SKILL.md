---
name: gestionar-faltantes-expediente
description: Skill atomico penal-victimas: identificar datos y documentos faltantes antes de analizar o redactar. Use when the workflow requires `gestionar_faltantes_expediente`.
disable-model-invocation: true
---

# gestionar_faltantes_expediente

## Scope
- Category: `Skills transversales`
- Skill ID: `gestionar_faltantes_expediente`

## Used By Agents
- `coordinador_expediente_penal`

## Purpose
identificar datos y documentos faltantes antes de analizar o redactar.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
lista de faltantes, prioridad, responsable sugerido, dependencia con otros analisis.

## Tools
- `case_state_reader`
- `rag_expediente_search`
- `task_manager_create`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
