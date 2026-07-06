---
name: analizar-perjuicio-irremediable
description: Skill atomico penal-victimas: identificar urgencia constitucional. Use when the workflow requires `analizar_perjuicio_irremediable`.
disable-model-invocation: true
---

# analizar_perjuicio_irremediable

## Scope
- Category: `Skills constitucionales y tutela`
- Skill ID: `analizar_perjuicio_irremediable`

## Used By Agents
- `evaluador_derechos_fundamentales_tutela`

## Purpose
identificar urgencia constitucional.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
gravedad, urgencia, impostergabilidad, prueba, riesgo.

## Tools
- `rag_corte_constitucional_search`
- `rag_expediente_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
