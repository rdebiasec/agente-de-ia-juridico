---
name: verificar-jurisprudencia
description: Skill atomico penal-victimas: revisar sentencias, radicados, fechas y organos judiciales. Use when the workflow requires `verificar_jurisprudencia`.
disable-model-invocation: true
---

# verificar_jurisprudencia

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `verificar_jurisprudencia`

## Used By Agents
- `analista_calidad_juridica`

## Purpose
revisar sentencias, radicados, fechas y organos judiciales.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
jurisprudencia, estado verificacion, fuente, riesgo.

## Tools
- `citation_checker`
- `rag_jurisprudencia_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
