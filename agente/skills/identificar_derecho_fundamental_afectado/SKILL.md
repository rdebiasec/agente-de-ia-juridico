---
name: identificar-derecho-fundamental-afectado
description: Skill atomico penal-victimas: identificar posibles derechos fundamentales comprometidos. Use when the workflow requires `identificar_derecho_fundamental_afectado`.
disable-model-invocation: true
---

# identificar_derecho_fundamental_afectado

## Scope
- Category: `Skills constitucionales y tutela`
- Skill ID: `identificar_derecho_fundamental_afectado`

## Used By Agents
- `evaluador_derechos_fundamentales_tutela`

## Purpose
identificar posibles derechos fundamentales comprometidos.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
derecho, hecho vulnerador, soporte, accionado potencial.

## Tools
- `rag_constitucion_search`
- `rag_expediente_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
