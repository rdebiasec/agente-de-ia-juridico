---
name: estructurar-hechos-fundamentos-solicitudes
description: Skill atomico penal-victimas: ordenar cualquier documento juridico. Use when the workflow requires `estructurar_hechos_fundamentos_solicitudes`.
disable-model-invocation: true
---

# estructurar_hechos_fundamentos_solicitudes

## Scope
- Category: `Skills de redaccion juridica penal`
- Skill ID: `estructurar_hechos_fundamentos_solicitudes`

## Used By Agents
- `redactor_documentos_juridicos_penales`

## Purpose
ordenar cualquier documento juridico.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
secciones de hechos, fundamentos, pruebas, solicitudes y anexos.

## Tools
- `rag_plantillas_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
