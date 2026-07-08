---
name: verificar-citas-normativas
description: Skill atomico penal-victimas: verificar que normas, articulos y leyes citadas existan en el RAG o esten marcadas pendientes. Use when the workflow requires `verificar_citas_normativas`.
disable-model-invocation: true
---

# verificar_citas_normativas

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `verificar_citas_normativas`
- Tier: `operativo`

## Used By Agents
- `redactor_documentos_juridicos_penales`
- `analista_calidad_juridica`

## Purpose
Verificar que leyes, artículos y decretos citados existan, estén vigentes y sean pertinentes al caso.

## Rol en redactor_documentos_juridicos_penales
Control en borrador antes de calidad.

## Rol en analista_calidad_juridica
Verificación en salida final.

## Inputs
- Lista de citas normativas en el documento.
- Contexto del caso (penal-víctimas Colombia).

## Outputs
- Por cita: `referencia`, `existe_en_rag` (sí | no | pendiente), `vigente` (sí | no | pendiente), `pertinencia` (alta | media | baja).
- `citas_a_corregir` priorizadas.
- Etiqueta: `VERIFICACIÓN NORMATIVA — NO ES APROBACIÓN FINAL`.

## Steps
1. Validar existencia de leyes, artículos y decretos citados.
2. Verificar vigencia y pertinencia al caso penal-víctimas.
3. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `citation_checker`
- `rag_normativo_search`

## Guardrails (g1–g10)
- **g1:** No afirmar vigencia sin verificar en RAG.
- **g4:** HITL obligatorio antes de usar la salida en memorial, estrategia o comunicación con cliente.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No detectar alucinaciones globales (`detectar_alucinaciones_legales`).
- No jurisprudencia (`verificar_jurisprudencia`).

## Riesgo si se omite
Memorial con artículos derogados, inexistentes o irrelevantes citados como fundamento.
