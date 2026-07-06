---
name: revisar-mecanismos-ordinarios
description: Skill atomico penal-victimas: verificar si hay vias ordinarias antes de tutela. Use when the workflow requires `revisar_mecanismos_ordinarios`.
disable-model-invocation: true
---

# revisar_mecanismos_ordinarios

## Scope
- Category: `Skills constitucionales y tutela`
- Skill ID: `revisar_mecanismos_ordinarios`

## Used By Agents
- `evaluador_derechos_fundamentales_tutela`

## Purpose
verificar si hay vias ordinarias antes de tutela.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
mecanismos existentes, idoneidad, eficacia, riesgo de improcedencia.

## Tools
- `rag_ley906_search`
- `rag_corte_constitucional_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
