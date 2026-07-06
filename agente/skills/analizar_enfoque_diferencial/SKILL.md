---
name: analizar-enfoque-diferencial
description: Skill atomico penal-victimas: identificar sujetos de especial proteccion y necesidades diferenciadas. Use when the workflow requires `analizar_enfoque_diferencial`.
disable-model-invocation: true
---

# analizar_enfoque_diferencial

## Scope
- Category: `Skills de representacion de victimas`
- Skill ID: `analizar_enfoque_diferencial`

## Used By Agents
- `analista_representacion_victimas`
- `evaluador_derechos_fundamentales_tutela`

## Purpose
identificar sujetos de especial proteccion y necesidades diferenciadas.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
condicion relevante, implicacion juridica, medida sugerida, fuente.

## Tools
- `rag_constitucional_search`
- `rag_normas_victimas_search`
- `pii_detector`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
