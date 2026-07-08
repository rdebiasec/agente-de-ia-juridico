---
name: redactar-memorial-penal
description: Skill critico penal-victimas: crear borrador de memorial penal para firma humana. Use when the workflow requires `redactar_memorial_penal`.
disable-model-invocation: true
---

# redactar_memorial_penal

## Scope
- Category: `Skills de redaccion juridica penal`
- Skill ID: `redactar_memorial_penal`
- Tier: `critico`

## Used By Agents
- `redactor_documentos_juridicos_penales` (skill primario del agente)

## Purpose
Redactar borrador de memorial penal con hechos soportados, fundamentos y peticiones.

## Rol en redactor_documentos_juridicos_penales
Skill primario del agente; ejecutar antes de pasar a calidad jurídica.

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
1. Recopilar hechos soportados y pretensiones de la víctima.
2. Verificar citas normativas aplicables al memorial.
3. Revisar estructura hechos-fundamentos-peticiones según plantilla del despacho.
4. Redactar memorial integrando hechos, fundamentos y peticiones.
5. Marcar pendientes de verificación antes de firma humana.
6. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_plantillas_search`
- `rag_normativo_search`
- `rag_expediente_search`
- `document_version_create`

## Guardrails (g1–g10)
- **g1:** No inventar hechos, citas ni anexos.
- **g3:** Hechos separados de argumentación y peticiones.
- **g4:** HITL y firma humana obligatorias.
- **g5:** Lenguaje respetuoso con la víctima.
- **g8:** Aviso de borrador.

## Handoff
- Pasar a `analista_calidad_juridica` (`clasificar_aprobacion_juridica`) antes de uso externo.

## Riesgo si se omite
Memorial con hechos no soportados o improcedente en la etapa.
