<!-- config-version: 2; checksum: cf314adbe7ba9671 -->
---
name: redactar-solicitud-impulso-procesal
description: Skill atomico penal-victimas: crear borrador para solicitar impulso procesal o actuaciones. Use when the workflow requires `redactar_solicitud_impulso_procesal`.
disable-model-invocation: true
---

# redactar_solicitud_impulso_procesal

## Scope
- Category: `Skills de redaccion juridica penal`
- Skill ID: `redactar_solicitud_impulso_procesal`
- Tier: `operativo`

## Used By Agents
- `redactor_documentos_juridicos_penales`
- `gestor_seguimiento_procesal_penal`

## Purpose
Redactar solicitud de impulso procesal ante inactividad de Fiscalía o juez.

## Rol en redactor_documentos_juridicos_penales
Redacta borrador formal.

## Rol en gestor_seguimiento_procesal_penal
Aporta hechos de inactividad (`detectar_inactividad_procesal`); no redacta texto final.

## Inputs
- Registro de inactividad y última actuación.
- Etapa procesal y actuación solicitada.
- Norma Ley 906 que fundamente el impulso.

## Outputs
- Borrador: hechos de parálisis, fundamentos, petición concreta de actuación.
- Etiqueta: `BORRADOR — NO RADICAR SIN FIRMA`.

## Steps
1. Documentar inactividad procesal con fechas y actuaciones omitidas.
2. Fundamentar solicitud en Ley 906 y derechos de la víctima.
3. Formular petición concreta de actuación al Fiscal o juez.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `redactar_solicitud_impulso_procesal`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_ley906_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `rag_plantillas_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `case_state_reader` — no implementada

## Guardrails (g1–g10)
- **g1:** No inventar actuaciones ni fechas.
- **g4:** HITL antes de radicar.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No detectar inactividad (`detectar_inactividad_procesal` — seguimiento).

## Riesgo si se omite
Proceso paralizado sin presión formal y pérdida de oportunidades probatorias.
