<!-- config-version: 2; checksum: 4b6241ebc4beba61 -->
---
name: redactar-ampliacion-denuncia
description: Contrato penal-víctimas: Redactar borrador de ampliación de denuncia con nuevos hechos o elementos. Activar cuando el plan/HITL o el especialista requiera `redactar_ampliacion_denuncia`. No sustituye a `redactar_memorial_penal`.
disable-model-invocation: true
---

# redactar_ampliacion_denuncia

## Scope
- Category: `Skills de redaccion juridica penal`
- Skill ID: `redactar_ampliacion_denuncia`
- Tier: `operativo`

## Used By Agents
- `redactor_documentos_juridicos`

## Purpose
Redactar borrador de ampliación de denuncia con nuevos hechos o elementos.

## Rol en redactor_documentos_juridicos
Borrador de ampliación; HITL y radicación son del despacho.
## Inputs
- Denuncia o informe previo (si consta).
- Nuevos hechos verificados o narrados con fuente.
- Radicado o número de noticia criminal (si existe).

## Outputs
- Borrador de ampliación: hechos nuevos, relación con denuncia previa, peticiones.
- Etiqueta: `BORRADOR — NO RADICAR SIN FIRMA`.

## Steps
1. Identificar hechos nuevos no incluidos en denuncia anterior.
2. Redactar ampliación vinculando con radicado o noticia existente.
3. Marcar hechos sin fuente como pendientes.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `redactar_ampliacion_denuncia`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_expediente_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `rag_plantillas_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto

## Guardrails
- **No inventar:** No inventar radicados ni hechos.
- **Revision humana obligatoria:** HITL y firma humana.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No memorial de impulso genérico (`redactar_memorial_penal` / `redactar_solicitud_impulso_procesal`).
- No derecho de petición (`redactar_derecho_peticion_penal`).

## Riesgo si se omite
Hechos nuevos no incorporados formalmente al expediente penal.
