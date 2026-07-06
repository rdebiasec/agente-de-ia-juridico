---
name: evaluar-procedencia-tutela
description: Skill atomico penal-victimas: evaluar legitimacion, subsidiariedad, inmediatez y relevancia constitucional. Use when the workflow requires `evaluar_procedencia_tutela`.
disable-model-invocation: true
---

# evaluar_procedencia_tutela

## Scope
- Category: `Skills constitucionales y tutela`
- Skill ID: `evaluar_procedencia_tutela`

## Used By Agents
- `evaluador_derechos_fundamentales_tutela`
- `analista_calidad_juridica`

## Purpose
evaluar legitimacion, subsidiariedad, inmediatez y relevancia constitucional.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
procedencia preliminar, riesgos, datos faltantes.

## Tools
- `rag_corte_constitucional_search`
- `citation_checker`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
