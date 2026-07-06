---
name: verificar-citas-normativas
description: Skill atomico penal-victimas: verificar que normas, articulos y leyes citadas existan en el RAG o esten marcadas pendientes. Use when the workflow requires `verificar_citas_normativas`.
disable-model-invocation: true
---

# verificar_citas_normativas

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `verificar_citas_normativas`

## Used By Agents
- `analista_calidad_juridica`
- `redactor_documentos_juridicos_penales`

## Purpose
verificar que normas, articulos y leyes citadas existan en el RAG o esten marcadas pendientes.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
cita, estado, fuente, error, correccion sugerida.

## Tools
- `citation_checker`
- `rag_normativo_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
