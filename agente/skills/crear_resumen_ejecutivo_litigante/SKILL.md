---
name: crear-resumen-ejecutivo-litigante
description: Skill atomico penal-victimas: crear resumen de una pagina para el abogado que interviene. Use when the workflow requires `crear_resumen_ejecutivo_litigante`.
disable-model-invocation: true
---

# crear_resumen_ejecutivo_litigante

## Scope
- Category: `Skills de audiencias`
- Skill ID: `crear_resumen_ejecutivo_litigante`

## Used By Agents
- `preparador_estrategico_audiencias_penales`

## Purpose
crear resumen de una pagina para el abogado que interviene.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
resumen, hechos clave, pruebas clave, solicitudes, alertas.

## Tools
- `rag_expediente_search`
- `case_state_reader`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
