---
name: preparar-solicitudes-orales
description: Skill atomico penal-victimas: formular solicitudes orales posibles segun etapa. Use when the workflow requires `preparar_solicitudes_orales`.
disable-model-invocation: true
---

# preparar_solicitudes_orales

## Scope
- Category: `Skills de audiencias`
- Skill ID: `preparar_solicitudes_orales`

## Used By Agents
- `preparador_estrategico_audiencias_penales`
- `analista_ruta_procesal_ley906`

## Purpose
formular solicitudes orales posibles segun etapa.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
solicitud, fundamento, hecho soporte, prueba, riesgo.

## Tools
- `rag_ley906_search`
- `citation_checker`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
