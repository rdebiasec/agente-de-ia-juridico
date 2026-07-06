---
name: crear-matriz-hecho-derecho-fundamental
description: Skill atomico penal-victimas: relacionar hechos con derechos afectados. Use when the workflow requires `crear_matriz_hecho_derecho_fundamental`.
disable-model-invocation: true
---

# crear_matriz_hecho_derecho_fundamental

## Scope
- Category: `Skills constitucionales y tutela`
- Skill ID: `crear_matriz_hecho_derecho_fundamental`

## Used By Agents
- `evaluador_derechos_fundamentales_tutela`

## Purpose
relacionar hechos con derechos afectados.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
hecho, derecho, prueba, autoridad, solicitud.

## Tools
- `rag_expediente_search`
- `rag_constitucion_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
