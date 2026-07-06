---
name: clasificar-tipo-prueba
description: Skill atomico penal-victimas: clasificar evidencia como documental, testimonial, digital, fisica, pericial, institucional o pendiente. Use when the workflow requires `clasificar_tipo_prueba`.
disable-model-invocation: true
---

# clasificar_tipo_prueba

## Scope
- Category: `Skills de evidencia y soporte probatorio`
- Skill ID: `clasificar_tipo_prueba`

## Used By Agents
- `gestor_evidencia_y_soporte_probatorio`

## Purpose
clasificar evidencia como documental, testimonial, digital, fisica, pericial, institucional o pendiente.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
item, tipo, justificacion, riesgo.

## Tools
- `metadata_extractor`
- `document_parser_extract_text`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
