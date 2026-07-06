---
name: generar-preguntas-testigos-peritos
description: Skill atomico penal-victimas: preparar preguntas neutrales para testigos o peritos. Use when the workflow requires `generar_preguntas_testigos_peritos`.
disable-model-invocation: true
---

# generar_preguntas_testigos_peritos

## Scope
- Category: `Skills de evidencia y soporte probatorio`
- Skill ID: `generar_preguntas_testigos_peritos`

## Used By Agents
- `gestor_evidencia_y_soporte_probatorio`
- `preparador_estrategico_audiencias_penales`

## Purpose
preparar preguntas neutrales para testigos o peritos.

## Inputs
Depende del flujo. Solicitar datos faltantes antes de continuar.

## Outputs
pregunta, objetivo, hecho que busca probar, riesgo de induccion.

## Tools
- `sin_herramientas_obligatorias`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
