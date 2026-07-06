---
name: detectar-riesgos-audiencia
description: Skill atomico penal-victimas: detectar riesgos de intervencion, oportunidad, revelacion de estrategia o revictimizacion. Use when the workflow requires `detectar_riesgos_audiencia`.
disable-model-invocation: true
---

# detectar_riesgos_audiencia

## Scope
- Category: `Skills de audiencias`
- Skill ID: `detectar_riesgos_audiencia`

## Used By Agents
- `preparador_estrategico_audiencias_penales`
- `analista_calidad_juridica`

## Purpose
detectar riesgos de intervencion, oportunidad, revelacion de estrategia o revictimizacion.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
riesgo, severidad, mitigacion.

## Tools
- `revictimization_risk_checker`
- `rag_ley906_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
