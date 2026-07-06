---
name: clasificar-fuente-factual
description: Skill atomico penal-victimas: distinguir documento, relato de victima, relato de tercero, autoridad, inferencia o dato pendiente. Use when the workflow requires `clasificar_fuente_factual`.
disable-model-invocation: true
---

# clasificar_fuente_factual

## Scope
- Category: `Skills de hechos y cronologia`
- Skill ID: `clasificar_fuente_factual`

## Used By Agents
- `coordinador_expediente_penal`

## Purpose
distinguir documento, relato de victima, relato de tercero, autoridad, inferencia o dato pendiente.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
clasificacion por hecho y nivel de soporte.

## Tools
- `source_reference_validator`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
