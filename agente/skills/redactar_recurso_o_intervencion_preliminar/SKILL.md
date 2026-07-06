---
name: redactar-recurso-o-intervencion-preliminar
description: Skill atomico penal-victimas: crear borrador preliminar de recurso o intervencion, sujeto a revision procesal. Use when the workflow requires `redactar_recurso_o_intervencion_preliminar`.
disable-model-invocation: true
---

# redactar_recurso_o_intervencion_preliminar

## Scope
- Category: `Skills de redaccion juridica penal`
- Skill ID: `redactar_recurso_o_intervencion_preliminar`

## Used By Agents
- `redactor_documentos_juridicos_penales`
- `analista_ruta_procesal_ley906`

## Purpose
crear borrador preliminar de recurso o intervencion, sujeto a revision procesal.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
borrador, decision atacada, agravios, fundamento, termino, pendientes.

## Tools
- `rag_ley906_search`
- `rag_jurisprudencia_search`
- `calendar_terms_calculator`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
