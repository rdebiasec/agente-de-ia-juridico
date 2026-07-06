---
name: detectar-brechas-probatorias
description: Skill atomico penal-victimas: identificar hechos relevantes sin soporte suficiente. Use when the workflow requires `detectar_brechas_probatorias`.
disable-model-invocation: true
---

# detectar_brechas_probatorias

## Scope
- Category: `Skills de evidencia y soporte probatorio`
- Skill ID: `detectar_brechas_probatorias`

## Used By Agents
- `gestor_evidencia_y_soporte_probatorio`
- `analista_calidad_juridica`

## Purpose
identificar hechos relevantes sin soporte suficiente.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
brecha, impacto, prueba sugerida, prioridad.

## Tools
- `rag_expediente_search`
- `case_state_reader`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
