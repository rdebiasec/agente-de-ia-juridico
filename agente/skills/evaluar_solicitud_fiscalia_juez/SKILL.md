---
name: evaluar-solicitud-fiscalia-juez
description: Skill atomico penal-victimas: evaluar si una solicitud a Fiscalia o juez es procedente y conveniente. Use when the workflow requires `evaluar_solicitud_fiscalia_juez`.
disable-model-invocation: true
---

# evaluar_solicitud_fiscalia_juez

## Scope
- Category: `Skills de ruta procesal Ley 906`
- Skill ID: `evaluar_solicitud_fiscalia_juez`

## Used By Agents
- `analista_ruta_procesal_ley906`
- `redactor_documentos_juridicos_penales`

## Purpose
evaluar si una solicitud a Fiscalia o juez es procedente y conveniente.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
solicitud, autoridad, fundamento, oportunidad, riesgos, documento sugerido.

## Tools
- `rag_ley906_search`
- `rag_expediente_search`
- `citation_checker`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
