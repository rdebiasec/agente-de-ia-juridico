---
name: construir-matriz-hecho-prueba
description: Skill atomico penal-victimas: relacionar hechos con pruebas existentes y faltantes. Use when the workflow requires `construir_matriz_hecho_prueba`.
disable-model-invocation: true
---

# construir_matriz_hecho_prueba

## Scope
- Category: `Skills de evidencia y soporte probatorio`
- Skill ID: `construir_matriz_hecho_prueba`

## Used By Agents
- `gestor_evidencia_y_soporte_probatorio`
- `analista_tipicidad_y_responsabilidad_penal`
- `preparador_estrategico_audiencias_penales`

## Purpose
relacionar hechos con pruebas existentes y faltantes.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
matriz hecho/prueba/fuente/fortaleza/brecha/riesgo/accion.

## Tools
- `rag_expediente_search`
- `source_reference_validator`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
