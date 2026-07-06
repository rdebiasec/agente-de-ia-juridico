---
name: preparar-resumen-operativo-cliente
description: Skill atomico penal-victimas: crear version simple del estado del proceso para cliente, sin estrategia sensible. Use when the workflow requires `preparar_resumen_operativo_cliente`.
disable-model-invocation: true
---

# preparar_resumen_operativo_cliente

## Scope
- Category: `Skills de seguimiento procesal`
- Skill ID: `preparar_resumen_operativo_cliente`

## Used By Agents
- `gestor_seguimiento_procesal_penal`
- `analista_calidad_juridica`

## Purpose
crear version simple del estado del proceso para cliente, sin estrategia sensible.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
resumen claro, proximos pasos, pendientes, advertencias.

## Tools
- `case_state_reader`
- `approval_gate_submit`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
