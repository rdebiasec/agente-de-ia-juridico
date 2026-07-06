---
name: revisar-coherencia-estrategica
description: Skill atomico penal-victimas: asegurar que documento o recomendacion sea coherente con la estrategia aprobada. Use when the workflow requires `revisar_coherencia_estrategica`.
disable-model-invocation: true
---

# revisar_coherencia_estrategica

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `revisar_coherencia_estrategica`

## Used By Agents
- `analista_calidad_juridica`

## Purpose
asegurar que documento o recomendacion sea coherente con la estrategia aprobada.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
coherente, inconsistencias, ajustes.

## Tools
- `strategy_consistency_checker`
- `case_state_reader`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
