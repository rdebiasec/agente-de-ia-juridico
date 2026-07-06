---
name: descomponer-elementos-tipo-penal
description: Skill atomico penal-victimas: dividir un posible delito en elementos juridicos verificables. Use when the workflow requires `descomponer_elementos_tipo_penal`.
disable-model-invocation: true
---

# descomponer_elementos_tipo_penal

## Scope
- Category: `Skills de tipicidad y responsabilidad penal`
- Skill ID: `descomponer_elementos_tipo_penal`

## Used By Agents
- `analista_tipicidad_y_responsabilidad_penal`

## Purpose
dividir un posible delito en elementos juridicos verificables.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
elementos objetivos, subjetivos, sujetos, conducta, resultado, nexo, agravantes posibles.

## Tools
- `rag_codigo_penal_search`
- `citation_checker`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
