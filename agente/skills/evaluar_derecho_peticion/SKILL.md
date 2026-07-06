---
name: evaluar-derecho-peticion
description: Skill atomico penal-victimas: revisar si existe derecho de peticion incumplido. Use when the workflow requires `evaluar_derecho_peticion`.
disable-model-invocation: true
---

# evaluar_derecho_peticion

## Scope
- Category: `Skills constitucionales y tutela`
- Skill ID: `evaluar_derecho_peticion`

## Used By Agents
- `evaluador_derechos_fundamentales_tutela`
- `redactor_documentos_juridicos_penales`

## Purpose
revisar si existe derecho de peticion incumplido.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
solicitud, fecha, autoridad, termino, respuesta, riesgo.

## Tools
- `calendar_terms_calculator`
- `rag_constitucional_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
