---
name: recomendar-via-constitucional-o-alternativa
description: Skill atomico penal-victimas: recomendar tutela, derecho de peticion, solicitud procesal, queja u otra ruta. Use when the workflow requires `recomendar_via_constitucional_o_alternativa`.
disable-model-invocation: true
---

# recomendar_via_constitucional_o_alternativa

## Scope
- Category: `Skills constitucionales y tutela`
- Skill ID: `recomendar_via_constitucional_o_alternativa`

## Used By Agents
- `evaluador_derechos_fundamentales_tutela`
- `coordinador_expediente_penal`

## Purpose
recomendar tutela, derecho de peticion, solicitud procesal, queja u otra ruta.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
via, razon, riesgos, siguiente accion.

## Tools
- `rag_constitucional_search`
- `rag_ley906_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
