---
name: redactar-recurso-o-intervencion-preliminar
description: Skill operativo penal-victimas: evaluar y preparar insumos para recurso o intervencion; redaccion final en redactor. Use when the workflow requires `redactar_recurso_o_intervencion_preliminar`.
disable-model-invocation: true
---

# redactar_recurso_o_intervencion_preliminar

## Scope
- Category: `Skills de redaccion juridica penal`
- Skill ID: `redactar_recurso_o_intervencion_preliminar`
- Tier: `operativo`

## Used By Agents
- `redactor_documentos_juridicos_penales` (redacción del borrador)
- `analista_ruta_procesal_ley906` (solo evaluación e insumos — **no redacta texto final**)

## Purpose
Confirmar oportunidad y preparar insumos para recurso o intervención; el borrador lo redacta el agente redactor.

## Rol en analista_ruta_procesal
**Solo pasos 1 y 3:** confirmar oportunidad/tipo de recurso y alertar términos. **No ejecutar paso 2 (redactar)** — derivar a `redactor_documentos_juridicos_penales`.

## Rol en redactor
Ejecutar los 4 pasos completos incluyendo borrador.

## Inputs
- Acto a impugnar o intervención objetivo.
- `evaluar_oportunidad_procesal` y términos (`controlar_terminos_procesales_preliminares`).
- Hechos soportados y fundamentos normativos (RAG).

## Outputs (ruta 906)
- `tipo_recurso_intervencion`, `oportunidad`, `agravios_preliminares`, `terminos_pendientes_verificar`.
- `derivar_a`: `redactor_documentos_juridicos_penales`.
- Etiqueta: `NO ES BORRADOR — SOLO INSUMOS PROCESALES`.

## Outputs (redactor)
- Borrador completo + pendientes + términos.

## Steps
1. Confirmar oportunidad procesal y tipo de recurso/intervención.
2. Redactar borrador con argumentos y peticiones procedentes. *(Solo redactor)*
3. Alertar términos y requisitos de forma pendientes de verificación.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_ley906_search`
- `rag_jurisprudencia_search`
- `calendar_terms_calculator`

## Guardrails (g1–g10)
- **g1:** No inventar actos procesales ni plazos.
- **g4:** HITL y firma humana antes de radicar.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No oportunidad sin recurso concreto (`evaluar_oportunidad_procesal`).
- No memorial ordinario (`redactar_memorial_penal`).

## Riesgo si se omite
Recurso extemporáneo o borrador sin evaluación procesal previa.
