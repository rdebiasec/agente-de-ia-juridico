---
name: priorizar-objetivos-representacion
description: Skill atomico penal-victimas: ordenar objetivos de la representacion. Use when the workflow requires `priorizar_objetivos_representacion`.
disable-model-invocation: true
---

# priorizar_objetivos_representacion

## Scope
- Category: `Skills de representacion de victimas`
- Skill ID: `priorizar_objetivos_representacion`

## Used By Agents
- `analista_representacion_victimas`
- `coordinador_expediente_penal`

## Purpose
ordenar objetivos de la representacion.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
objetivo, prioridad, razon, dependencia, riesgo.

## Tools
- `sin_herramientas_obligatorias`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
