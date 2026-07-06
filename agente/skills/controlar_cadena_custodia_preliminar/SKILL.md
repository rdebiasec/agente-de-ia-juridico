---
name: controlar-cadena-custodia-preliminar
description: Skill atomico penal-victimas: alertar si la evidencia puede requerir cadena de custodia. Use when the workflow requires `controlar_cadena_custodia_preliminar`.
disable-model-invocation: true
---

# controlar_cadena_custodia_preliminar

## Scope
- Category: `Skills de evidencia y soporte probatorio`
- Skill ID: `controlar_cadena_custodia_preliminar`

## Used By Agents
- `gestor_evidencia_y_soporte_probatorio`
- `analista_calidad_juridica`

## Purpose
alertar si la evidencia puede requerir cadena de custodia.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
evidencia, riesgo, accion sugerida, necesidad de experto.

## Tools
- `chain_of_custody_logger`
- `metadata_extractor`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
