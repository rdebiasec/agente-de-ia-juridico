<!-- config-version: 3; checksum: df4e59040dcbf9e5 -->
---
name: redactar-recurso-o-intervencion-preliminar
description: Contrato penal-víctimas: Confirmar oportunidad y preparar insumos para recurso o intervención; el borrador lo redacta el agente redactor. Activar cuando el plan/HITL o el especialista requiera `redactar_recurso_o_intervencion_preliminar`. No sustituye a `evaluar_oportunidad_pr...
disable-model-invocation: true
---

# redactar_recurso_o_intervencion_preliminar

## Scope
- Category: `Skills de redaccion juridica penal`
- Skill ID: `redactar_recurso_o_intervencion_preliminar`
- Tier: `operativo`

## Used By Agents
- `redactor_documentos_juridicos` (redacción del borrador)
- `analista_ruta_procesal` (solo evaluación e insumos — **no redacta texto final**)

## Purpose
Confirmar oportunidad y preparar insumos para recurso o intervención; el borrador lo redacta el agente redactor.

## Rol en analista_ruta_procesal
**Solo pasos 1 y 3:** confirmar oportunidad/tipo de recurso y alertar términos. **No ejecutar paso 2 (redactar)** — derivar a `redactor_documentos_juridicos`.

## Rol en redactor_documentos_juridicos
Ejecutar los 4 pasos completos incluyendo borrador.

## Fuentes KB
- `agente/conocimiento/proceso-penal-906.md` — etapas, enum `etapa_ley906`, términos (días hábiles).
- `agente/conocimiento/normas-clave.md` — criterio operativo y derechos de víctima.
- Herramientas: `leer_playbook_proceso(penal)`, `leer_normas_clave`, `buscar_en_conocimiento` antes de afirmar etapa/plazos.
## Inputs
- Acto a impugnar o intervención objetivo.
- `evaluar_oportunidad_procesal` y términos (`controlar_terminos_procesales_preliminares`).
- Hechos soportados y fundamentos normativos (RAG).

## Outputs (ruta 906)
- `tipo_recurso_intervencion`, `oportunidad`, `agravios_preliminares`, `terminos_pendientes_verificar`.
- `derivar_a`: `redactor_documentos_juridicos`.
- Etiqueta: `NO ES BORRADOR — SOLO INSUMOS PROCESALES`.

## Outputs (redactor)
- Borrador completo + pendientes + términos.

## Steps
0. Anclar etapa/ruta a `proceso-penal-906.md` (enum `etapa_ley906`); términos en días hábiles; sin `fecha_base` no certificar plazos.
1. Confirmar oportunidad procesal y tipo de recurso/intervención.
2. Redactar borrador con argumentos y peticiones procedentes. *(Solo redactor)*
3. Alertar términos y requisitos de forma pendientes de verificación.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `redactar_recurso_o_intervencion_preliminar`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_ley906_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `rag_jurisprudencia_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `calendar_terms_calculator` — no implementada

## Guardrails
- **No inventar:** No inventar actos procesales ni plazos.
- **Revision humana obligatoria:** HITL y firma humana antes de radicar.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No oportunidad sin recurso concreto (`evaluar_oportunidad_procesal`).
- No memorial ordinario (`redactar_memorial_penal`).

## Riesgo si se omite
Recurso extemporáneo o borrador sin evaluación procesal previa.
