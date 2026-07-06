---
name: evaluar-suficiencia-probatoria
description: Skill atomico penal-victimas: evaluar preliminarmente fuerza de soporte probatorio. Use when the workflow requires `evaluar_suficiencia_probatoria`.
disable-model-invocation: true
---

# evaluar_suficiencia_probatoria

## Scope
- Category: `Skills de evidencia y soporte probatorio`
- Skill ID: `evaluar_suficiencia_probatoria`

## Used By Agents
- `gestor_evidencia_y_soporte_probatorio`
- `analista_representacion_victimas`

## Purpose
evaluar preliminarmente fuerza de soporte probatorio.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
hecho, fortaleza, debilidad, contradiccion, necesidad adicional.

## Tools
- `rag_expediente_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
