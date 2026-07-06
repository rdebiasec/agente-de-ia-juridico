---
name: controlar-tono-juridico-documento
description: Skill atomico penal-victimas: asegurar tono formal, preciso, no agresivo y no especulativo. Use when the workflow requires `controlar_tono_juridico_documento`.
disable-model-invocation: true
---

# controlar_tono_juridico_documento

## Scope
- Category: `Skills de redaccion juridica penal`
- Skill ID: `controlar_tono_juridico_documento`

## Used By Agents
- `redactor_documentos_juridicos_penales`
- `analista_calidad_juridica`

## Purpose
asegurar tono formal, preciso, no agresivo y no especulativo.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
texto corregido, riesgos de tono, cambios sugeridos.

## Tools
- `tone_checker`
- `revictimization_risk_checker`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
