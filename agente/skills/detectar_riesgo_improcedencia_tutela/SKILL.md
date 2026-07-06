---
name: detectar-riesgo-improcedencia-tutela
description: Skill atomico penal-victimas: detectar si tutela puede ser prematura, subsidiaria o improcedente. Use when the workflow requires `detectar_riesgo_improcedencia_tutela`.
disable-model-invocation: true
---

# detectar_riesgo_improcedencia_tutela

## Scope
- Category: `Skills constitucionales y tutela`
- Skill ID: `detectar_riesgo_improcedencia_tutela`

## Used By Agents
- `evaluador_derechos_fundamentales_tutela`
- `analista_calidad_juridica`

## Purpose
detectar si tutela puede ser prematura, subsidiaria o improcedente.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
riesgo, razon, alternativa sugerida.

## Tools
- `rag_corte_constitucional_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
