---
name: evaluar-dano-y-afectacion
description: Skill atomico penal-victimas: organizar danos y afectaciones alegadas. Use when the workflow requires `evaluar_dano_y_afectacion`.
disable-model-invocation: true
---

# evaluar_dano_y_afectacion

## Scope
- Category: `Skills de representacion de victimas`
- Skill ID: `evaluar_dano_y_afectacion`

## Used By Agents
- `analista_representacion_victimas`
- `gestor_evidencia_y_soporte_probatorio`

## Purpose
organizar danos y afectaciones alegadas.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
tipo de dano, hecho origen, prueba, necesidad pericial, pendiente.

## Tools
- `rag_expediente_search`
- `rag_medicina_legal_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
