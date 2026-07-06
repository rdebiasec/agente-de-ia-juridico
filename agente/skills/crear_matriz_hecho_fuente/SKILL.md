---
name: crear-matriz-hecho-fuente
description: Skill atomico penal-victimas: relacionar cada hecho con su fuente exacta. Use when the workflow requires `crear_matriz_hecho_fuente`.
disable-model-invocation: true
---

# crear_matriz_hecho_fuente

## Scope
- Category: `Skills de hechos y cronologia`
- Skill ID: `crear_matriz_hecho_fuente`

## Used By Agents
- `analista_cronologia_hechos_penales`
- `analista_calidad_juridica`

## Purpose
relacionar cada hecho con su fuente exacta.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
tabla hecho/fuente/tipo/nivel de soporte/pendientes.

## Tools
- `rag_expediente_search`
- `source_reference_validator`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
