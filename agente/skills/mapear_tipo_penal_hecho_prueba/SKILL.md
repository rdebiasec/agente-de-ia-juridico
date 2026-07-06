---
name: mapear-tipo-penal-hecho-prueba
description: Skill atomico penal-victimas: relacionar elementos del tipo con hechos y pruebas. Use when the workflow requires `mapear_tipo_penal_hecho_prueba`.
disable-model-invocation: true
---

# mapear_tipo_penal_hecho_prueba

## Scope
- Category: `Skills de tipicidad y responsabilidad penal`
- Skill ID: `mapear_tipo_penal_hecho_prueba`

## Used By Agents
- `analista_tipicidad_y_responsabilidad_penal`
- `gestor_evidencia_y_soporte_probatorio`
- `analista_calidad_juridica`

## Purpose
relacionar elementos del tipo con hechos y pruebas.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
matriz tipo/elemento/hecho/prueba/vacio/riesgo.

## Tools
- `rag_expediente_search`
- `rag_codigo_penal_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
