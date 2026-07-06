---
name: redactar-ampliacion-denuncia
description: Skill atomico penal-victimas: estructurar hechos nuevos, pruebas y anexos para ampliar denuncia. Use when the workflow requires `redactar_ampliacion_denuncia`.
disable-model-invocation: true
---

# redactar_ampliacion_denuncia

## Scope
- Category: `Skills de redaccion juridica penal`
- Skill ID: `redactar_ampliacion_denuncia`

## Used By Agents
- `redactor_documentos_juridicos_penales`

## Purpose
estructurar hechos nuevos, pruebas y anexos para ampliar denuncia.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
borrador, hechos nuevos, pruebas, anexos, pendientes.

## Tools
- `rag_plantillas_search`
- `rag_expediente_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
