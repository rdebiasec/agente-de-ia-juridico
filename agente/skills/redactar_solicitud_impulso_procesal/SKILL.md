---
name: redactar-solicitud-impulso-procesal
description: Skill atomico penal-victimas: crear borrador para solicitar impulso procesal o actuaciones. Use when the workflow requires `redactar_solicitud_impulso_procesal`.
disable-model-invocation: true
---

# redactar_solicitud_impulso_procesal

## Scope
- Category: `Skills de redaccion juridica penal`
- Skill ID: `redactar_solicitud_impulso_procesal`

## Used By Agents
- `redactor_documentos_juridicos_penales`

## Purpose
crear borrador para solicitar impulso procesal o actuaciones.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
solicitud, hechos, fundamento, peticiones, anexos, pendientes.

## Tools
- `rag_plantillas_search`
- `rag_ley906_search`
- `citation_checker`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
