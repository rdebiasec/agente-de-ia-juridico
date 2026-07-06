---
name: controlar-separacion-hecho-inferencia
description: Skill atomico penal-victimas: verificar que no se confundan hechos probados, narrados, inferidos y pendientes. Use when the workflow requires `controlar_separacion_hecho_inferencia`.
disable-model-invocation: true
---

# controlar_separacion_hecho_inferencia

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `controlar_separacion_hecho_inferencia`

## Used By Agents
- `analista_calidad_juridica`
- `redactor_documentos_juridicos_penales`

## Purpose
verificar que no se confundan hechos probados, narrados, inferidos y pendientes.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
problema, fragmento, correccion sugerida.

## Tools
- `source_reference_validator`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
