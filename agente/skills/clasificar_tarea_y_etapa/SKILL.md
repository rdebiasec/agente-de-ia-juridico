---
name: clasificar-tarea-y-etapa
description: Skill atomico penal-victimas: clasificar la solicitud del usuario interno y detectar la etapa aparente del caso. Use when the workflow requires `clasificar_tarea_y_etapa`.
disable-model-invocation: true
---

# clasificar_tarea_y_etapa

## Scope
- Category: `Skills transversales`
- Skill ID: `clasificar_tarea_y_etapa`

## Used By Agents
- `coordinador_expediente_penal`
- `analista_ruta_procesal_ley906`

## Purpose
clasificar la solicitud del usuario interno y detectar la etapa aparente del caso.

## Inputs
solicitud, resumen de caso, documentos disponibles, estado procesal conocido.

## Outputs
clasificacion, etapa aparente, workflow recomendado, agentes requeridos.

## Tools
- `rag_expediente_search`
- `case_state_reader`
- `audit_log_write`

## Guardrails
- no concluir etapa si no hay datos suficientes; marcar como desconocida o pendiente.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
