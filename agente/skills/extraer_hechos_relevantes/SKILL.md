---
name: extraer-hechos-relevantes
description: Skill atomico penal-victimas: extraer hechos relevantes de documentos, relatos, audios o comunicaciones. Use when the workflow requires `extraer_hechos_relevantes`.
disable-model-invocation: true
---

# extraer_hechos_relevantes

## Scope
- Category: `Skills de hechos y cronologia`
- Skill ID: `extraer_hechos_relevantes`

## Used By Agents
- `analista_cronologia_hechos_penales`
- `redactor_documentos_juridicos_penales`
- `gestor_evidencia_y_soporte_probatorio`

## Purpose
extraer hechos relevantes de documentos, relatos, audios o comunicaciones.

## Inputs
documentos, texto, transcripcion, objetivo del analisis.

## Outputs
lista de hechos con fuente, fecha, actor, tipo de fuente y soporte.

## Tools
- `document_parser_extract_text`
- `ocr_extract_text`
- `transcribe_audio`
- `rag_expediente_search`

## Guardrails
- No inventar hechos ni fuentes. Requiere revision humana.
- Do not invent norms, rulings, case numbers, or facts.
- Keep facts, inferences, and pending verification clearly separated.
- Any external output requires explicit human legal review.
