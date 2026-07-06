---
name: preparar-borrador-tutela-preliminar
description: Skill atomico penal-victimas: preparar insumos para borrador de tutela. Use when the workflow requires `preparar_borrador_tutela_preliminar`.
disable-model-invocation: true
---

# preparar_borrador_tutela_preliminar

## Scope
- Category: `Skills constitucionales y tutela`
- Skill ID: `preparar_borrador_tutela_preliminar`

## Used By Agents
- `evaluador_derechos_fundamentales_tutela`
- `redactor_documentos_juridicos_penales`

## Purpose
preparar insumos para borrador de tutela.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
hechos, derechos, pruebas, pretensiones, medidas provisionales si aplica.

## Tools
- `rag_plantillas_search`
- `rag_corte_constitucional_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
