---
name: detectar-riesgos-procesales
description: Skill atomico penal-victimas: detectar riesgos de oportunidad, legitimacion, competencia, improcedencia o perdida de derechos. Use when the workflow requires `detectar_riesgos_procesales`.
disable-model-invocation: true
---

# detectar_riesgos_procesales

## Scope
- Category: `Skills de ruta procesal Ley 906`
- Skill ID: `detectar_riesgos_procesales`

## Used By Agents
- `analista_ruta_procesal_ley906`
- `analista_calidad_juridica`

## Purpose
detectar riesgos de oportunidad, legitimacion, competencia, improcedencia o perdida de derechos.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
riesgo, severidad, accion preventiva, responsable.

## Tools
- `rag_ley906_search`
- `case_state_reader`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
