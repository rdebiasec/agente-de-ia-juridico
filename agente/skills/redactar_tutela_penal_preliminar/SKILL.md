---
name: redactar-tutela-penal-preliminar
description: Skill atomico penal-victimas: crear borrador de tutela solo si el evaluador constitucional lo recomienda preliminarmente. Use when the workflow requires `redactar_tutela_penal_preliminar`.
disable-model-invocation: true
---

# redactar_tutela_penal_preliminar

## Scope
- Category: `Skills de redaccion juridica penal`
- Skill ID: `redactar_tutela_penal_preliminar`

## Used By Agents
- `redactor_documentos_juridicos_penales`
- `evaluador_derechos_fundamentales_tutela`

## Purpose
crear borrador de tutela solo si el evaluador constitucional lo recomienda preliminarmente.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
borrador, derechos, hechos, accionado, pruebas, pretensiones, pendientes.

## Tools
- `rag_constitucion_search`
- `rag_corte_constitucional_search`
- `rag_plantillas_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
