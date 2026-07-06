---
name: preservar-evidencia-digital
description: Skill atomico penal-victimas: definir medidas para proteger evidencia digital sin alterarla. Use when the workflow requires `preservar_evidencia_digital`.
disable-model-invocation: true
---

# preservar_evidencia_digital

## Scope
- Category: `Skills de evidencia y soporte probatorio`
- Skill ID: `preservar_evidencia_digital`

## Used By Agents
- `gestor_evidencia_y_soporte_probatorio`

## Purpose
definir medidas para proteger evidencia digital sin alterarla.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
item, accion preservacion, riesgo, responsable.

## Tools
- `file_hash_generator`
- `metadata_extractor`
- `evidence_vault_store`
- `chain_of_custody_logger`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
