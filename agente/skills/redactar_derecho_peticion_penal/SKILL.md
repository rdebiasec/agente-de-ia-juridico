---
name: redactar-derecho-peticion-penal
description: Skill atomico penal-victimas: redactar derecho de peticion relacionado con autoridad o informacion del caso. Use when the workflow requires `redactar_derecho_peticion_penal`.
disable-model-invocation: true
---

# redactar_derecho_peticion_penal

## Scope
- Category: `Skills de redaccion juridica penal`
- Skill ID: `redactar_derecho_peticion_penal`

## Used By Agents
- `redactor_documentos_juridicos_penales`
- `evaluador_derechos_fundamentales_tutela`

## Purpose
redactar derecho de peticion relacionado con autoridad o informacion del caso.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
borrador, autoridad, peticiones, anexos, terminos, pendientes.

## Tools
- `rag_constitucional_search`
- `rag_plantillas_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
