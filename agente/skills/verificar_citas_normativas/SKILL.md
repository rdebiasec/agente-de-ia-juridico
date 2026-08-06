<!-- config-version: 3; checksum: 8ea5409c983d6dae -->
---
name: verificar-citas-normativas
description: Contrato penal-víctimas: Verificar que leyes, artículos y decretos citados existan, estén vigentes y sean pertinentes al caso. Activar cuando el plan/HITL o el especialista requiera `verificar_citas_normativas`. No sustituye a `detectar_alucinaciones_legales`.
disable-model-invocation: true
---

# verificar_citas_normativas

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `verificar_citas_normativas`
- Tier: `operativo`

## Used By Agents
- `redactor_documentos_juridicos`
- `analista_calidad_juridica`

## Purpose
Verificar que leyes, artículos y decretos citados existan, estén vigentes y sean pertinentes al caso.

## Rol en redactor_documentos_juridicos
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
Skills = contratos (no function_tools invocables). No existe tool LLM `verificar_citas_normativas`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `citation_checker` — no implementada
- `rag_normativo_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto

## Guardrails
- **No inventar:** No afirmar vigencia sin verificar en RAG.
- **Revision humana obligatoria:** HITL obligatorio antes de usar la salida en memorial, estrategia o comunicación con cliente.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No detectar alucinaciones globales (`detectar_alucinaciones_legales`).
- No jurisprudencia (`verificar_jurisprudencia`).

## Riesgo si se omite
Memorial con artículos derogados, inexistentes o irrelevantes citados como fundamento.
