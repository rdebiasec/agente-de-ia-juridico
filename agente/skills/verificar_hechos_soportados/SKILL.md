---
name: verificar-hechos-soportados
description: Skill atomico penal-victimas: revisar si cada afirmacion factual tiene fuente. Use when the workflow requires `verificar_hechos_soportados`.
disable-model-invocation: true
---

# verificar_hechos_soportados

## Scope
- Category: `Skills transversales`
- Skill ID: `verificar_hechos_soportados`

## Used By Agents
- `analista_calidad_juridica`
- `redactor_documentos_juridicos_penales`
- `analista_cronologia_hechos_penales`

## Purpose
revisar si cada afirmacion factual tiene fuente.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
hechos soportados, hechos no soportados, tipo de fuente, nivel de confianza.

## Tools
- `rag_expediente_search`
- `source_reference_validator`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
