<!-- config-version: 2; checksum: 0468e938b87e4ffd -->
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

## Guardrails (g1–g10)
- **g1:** No inventar radicados ni hechos.
- **g4:** HITL y firma humana.
- **g8:** Aviso de revisión profesional.

## Riesgo si se omite
Hechos nuevos no incorporados formalmente al expediente penal.
