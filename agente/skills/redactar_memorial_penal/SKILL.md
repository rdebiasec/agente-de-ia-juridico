---
name: redactar-memorial-penal
description: Skill atomico penal-victimas: crear borrador de memorial penal. Use when the workflow requires `redactar_memorial_penal`.
disable-model-invocation: true
---

# redactar_memorial_penal

## Scope
- Category: `Skills de redaccion juridica penal`
- Skill ID: `redactar_memorial_penal`

## Used By Agents
- `redactor_documentos_juridicos_penales`

## Purpose
crear borrador de memorial penal.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
documento borrador, fuentes, anexos, pendientes.

## Tools
- `rag_plantillas_search`
- `rag_normativo_search`
- `rag_expediente_search`
- `document_version_create`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
