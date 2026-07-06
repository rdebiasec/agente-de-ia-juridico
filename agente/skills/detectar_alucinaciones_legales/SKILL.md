---
name: detectar-alucinaciones-legales
description: Skill atomico penal-victimas: detectar fuentes, hechos, conclusiones o citas inventadas. Use when the workflow requires `detectar_alucinaciones_legales`.
disable-model-invocation: true
---

# detectar_alucinaciones_legales

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `detectar_alucinaciones_legales`

## Used By Agents
- `analista_calidad_juridica`

## Purpose
detectar fuentes, hechos, conclusiones o citas inventadas.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
item sospechoso, razon, severidad, accion.

## Tools
- `rag_source_validator`
- `citation_checker`
- `rag_expediente_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
