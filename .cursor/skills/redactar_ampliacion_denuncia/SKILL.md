---
name: redactar-ampliacion-denuncia
description: Skill atomico penal-victimas: estructurar hechos nuevos, pruebas y anexos para ampliar denuncia. Use when the workflow requires `redactar_ampliacion_denuncia`.
disable-model-invocation: true
---

# redactar_ampliacion_denuncia

## Scope
- Category: `Skills de redaccion juridica penal`
- Skill ID: `redactar_ampliacion_denuncia`
- Tier: `operativo`

## Used By Agents
- `redactor_documentos_juridicos_penales`

## Purpose
Redactar borrador de ampliación de denuncia con nuevos hechos o elementos.


## Rol en redactor
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
- `rag_expediente_search`
- `rag_plantillas_search`

## Guardrails (g1–g10)
- **g1:** No inventar radicados ni hechos.
- **g4:** HITL y firma humana.
- **g8:** Aviso de revisión profesional.

## Riesgo si se omite
Hechos nuevos no incorporados formalmente al expediente penal.
