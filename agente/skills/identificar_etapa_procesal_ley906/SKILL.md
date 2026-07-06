---
name: identificar-etapa-procesal-ley906
description: Skill atomico penal-victimas: determinar etapa del caso. Use when the workflow requires `identificar_etapa_procesal_ley906`.
disable-model-invocation: true
---

# identificar_etapa_procesal_ley906

## Scope
- Category: `Skills de ruta procesal Ley 906`
- Skill ID: `identificar_etapa_procesal_ley906`

## Used By Agents
- `analista_ruta_procesal_ley906`
- `coordinador_expediente_penal`

## Purpose
determinar etapa del caso.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
etapa, evidencia de la etapa, incertidumbres, siguiente dato a verificar.

## Tools
- `rag_expediente_search`
- `process_lookup_query`
- `rag_ley906_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
