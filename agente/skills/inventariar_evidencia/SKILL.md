---
name: inventariar-evidencia
description: Skill atomico penal-victimas: crear inventario de todos los elementos disponibles. Use when the workflow requires `inventariar_evidencia`.
disable-model-invocation: true
---

# inventariar_evidencia

## Scope
- Category: `Skills de evidencia y soporte probatorio`
- Skill ID: `inventariar_evidencia`

## Used By Agents
- `gestor_evidencia_y_soporte_probatorio`

## Purpose
crear inventario de todos los elementos disponibles.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
evidencia, tipo, origen, fecha, custodia, estado, ubicacion.

## Tools
- `evidence_vault_store`
- `metadata_extractor`
- `file_hash_generator`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
