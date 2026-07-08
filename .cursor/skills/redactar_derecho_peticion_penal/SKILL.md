---
name: redactar-derecho-peticion-penal
description: Skill atomico penal-victimas: redactar derecho de peticion relacionado con autoridad o informacion del caso. Use when the workflow requires `redactar_derecho_peticion_penal`.
disable-model-invocation: true
---

# redactar_derecho_peticion_penal

## Scope
- Category: `Skills de redaccion juridica penal`
- Skill ID: `redactar_derecho_peticion_penal`
- Tier: `operativo`

## Used By Agents
- `redactor_documentos_juridicos_penales` (único ejecutor de redacción)

## Purpose
Redactar borrador de derecho de petición relacionado con el caso penal cuando `evaluar_derecho_peticion` indica procedencia.

## Rol en redactor_documentos_juridicos_penales
Ejecutar redacción solo con evaluación favorable preliminar de petición.

## Inputs
- Salida de `evaluar_derecho_peticion` (procedencia preliminar).
- Destinatario, objeto, hechos y anexos disponibles.
- Plantilla y norma aplicable (RAG).

## Outputs
- Borrador: hechos, fundamentos, peticiones, anexos referenciados.
- `plazo_respuesta_esperado`.
- Etiqueta: `BORRADOR — NO RADICAR SIN FIRMA`.

## Steps
1. Precisar destinatario, objeto y hechos que motivan la petición.
2. Redactar peticiones claras con fundamento constitucional/legal.
3. Incluir anexos y plazo de respuesta esperado.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_constitucional_search`
- `rag_plantillas_search`

## Guardrails (g1–g10)
- **g4:** HITL y firma humana antes de radicar.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No evaluar procedencia de petición (`evaluar_derecho_peticion` — evaluador).

## Riesgo si se omite
Petición mal dirigida, extemporánea o sin fundamento que retrasa la vía útil.
