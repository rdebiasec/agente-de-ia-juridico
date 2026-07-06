---
name: preparar-contraargumentos
description: Skill atomico penal-victimas: anticipar argumentos de defensa, Fiscalia u otros intervinientes. Use when the workflow requires `preparar_contraargumentos`.
disable-model-invocation: true
---

# preparar_contraargumentos

## Scope
- Category: `Skills de audiencias`
- Skill ID: `preparar_contraargumentos`

## Used By Agents
- `preparador_estrategico_audiencias_penales`

## Purpose
anticipar argumentos de defensa, Fiscalia u otros intervinientes.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
argumento esperado, respuesta posible, fuente, riesgo.

## Tools
- `rag_expediente_search`
- `rag_jurisprudencia_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
