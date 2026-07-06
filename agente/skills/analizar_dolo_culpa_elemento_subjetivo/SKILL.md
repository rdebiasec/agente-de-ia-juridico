---
name: analizar-dolo-culpa-elemento-subjetivo
description: Skill atomico penal-victimas: identificar hechos que podrian soportar dolo, culpa u otro elemento subjetivo. Use when the workflow requires `analizar_dolo_culpa_elemento_subjetivo`.
disable-model-invocation: true
---

# analizar_dolo_culpa_elemento_subjetivo

## Scope
- Category: `Skills de tipicidad y responsabilidad penal`
- Skill ID: `analizar_dolo_culpa_elemento_subjetivo`

## Used By Agents
- `analista_tipicidad_y_responsabilidad_penal`

## Purpose
identificar hechos que podrian soportar dolo, culpa u otro elemento subjetivo.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
indicios, hechos soporte, pruebas, debilidades.

## Tools
- `rag_expediente_search`
- `rag_jurisprudencia_penal_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
