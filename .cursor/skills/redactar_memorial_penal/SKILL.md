<!-- config-version: 4; checksum: 64af5b00c57de6b9 -->
---
name: redactar-memorial-penal
description: Contrato penal-víctimas: Redactar borrador de memorial penal con hechos soportados, fundamentos y peticiones. Activar cuando el plan/HITL o el especialista requiera `redactar_memorial_penal`. No sustituye a `estructurar_hechos_fundamentos_solicitudes`.
disable-model-invocation: true
---

# redactar_memorial_penal

## Scope
- Category: `Skills de redaccion juridica penal`
- Skill ID: `redactar_memorial_penal`
- Tier: `critico`

## Used By Agents
- `redactor_documentos_juridicos` (skill primario del agente)

## Purpose
Redactar borrador de memorial penal con hechos soportados, fundamentos y peticiones.

## Rol en redactor_documentos_juridicos
Skill primario del agente; ejecutar antes de pasar a calidad jurídica.

## Fuentes KB
- `agente/conocimiento/proceso-penal-906.md` — checklist redacción O7; etapas; no inventar arts CPP.
- `agente/conocimiento/normas-clave.md` — checklist redacción; derechos víctima; HITL antes de radicar.
- Tools reales: `leer_playbook_proceso`, `leer_normas_clave`, `buscar_en_conocimiento`, `buscar_en_expediente`.

## Inputs
- Hechos verificados y cronología (`verificar_hechos_soportados`).
- Evaluación de solicitud si aplica (`evaluar_solicitud_fiscalia_juez`).
- Plantilla del despacho y norma Ley 906 (RAG).
- Tipicidad y matriz hecho-prueba (preliminar).

## Outputs
- Memorial: hechos, fundamentos, peticiones, anexos referenciados.
- Pendientes `[PENDIENTE DE VERIFICAR]` antes de firma.
- Etiqueta: `BORRADOR — NO RADICAR SIN FIRMA`.

## Steps
0. Anclar hechos/etapa/norma a Fuentes KB; sin soporte → `[PENDIENTE DE VERIFICAR]`. No inventar radicados ni arts.
1. Identificar destinatario, pretensión y hechos soportados del expediente.
2. Estructurar hechos → fundamentos → peticiones sin inventar citas ni radicados.
3. Insertar `[PENDIENTE DE VERIFICAR]` en cada dato no anclado.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `redactar_memorial_penal`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_plantillas_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `rag_normativo_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `rag_expediente_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `document_version_create` — no implementada

## Guardrails
- **No inventar:** No inventar hechos, citas ni anexos.
- **Separar hecho de inferencia:** Hechos separados de argumentación y peticiones.
- **Revision humana obligatoria:** HITL y firma humana obligatorias.
- **No revictimizar:** Lenguaje respetuoso con la víctima.
- **Aviso de borrador:** Aviso de borrador.

## Handoff
- Pasar a `analista_calidad_juridica` (`clasificar_aprobacion_juridica`) antes de uso externo.

## No duplicar
- No solo estructurar secciones sin redactar (`estructurar_hechos_fundamentos_solicitudes`).
- No derecho de petición (`redactar_derecho_peticion_penal`).

## Riesgo si se omite
Memorial con hechos no soportados o improcedente en la etapa.
