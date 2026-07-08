---
name: estructurar-hechos-fundamentos-solicitudes
description: Skill atomico penal-victimas: ordenar cualquier documento juridico. Use when the workflow requires `estructurar_hechos_fundamentos_solicitudes`.
disable-model-invocation: true
---

# estructurar_hechos_fundamentos_solicitudes

## Scope
- Category: `Skills de redaccion juridica penal`
- Skill ID: `estructurar_hechos_fundamentos_solicitudes`
- Tier: `operativo`

## Used By Agents
- `redactor_documentos_juridicos_penales`

## Purpose
Organizar esquema hechos-fundamentos-peticiones antes de redactar memorial o escrito.


## Rol en redactor
Esquema previo a redacción de escritos; insumo del redactor, no pieza final.
## Inputs
- Hechos soportados y pretensiones.
- Norma y plantilla aplicable.
- Tipo de escrito (memorial, solicitud, recurso).

## Outputs
- Esquema numerado: bloque hechos | fundamentos | peticiones con referencias cruzadas.
- Pendientes `[PENDIENTE DE VERIFICAR]` por bloque.
- Etiqueta: `ESQUEMA — NO ES BORRADOR FINAL`.

## Steps
1. Agrupar hechos verificados por tema o cronología.
2. Vincular fundamentos normativos a cada bloque fáctico.
3. Formular peticiones derivadas de cada fundamento.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_plantillas_search`
- `rag_normativo_search`

## Guardrails (g1–g10)
- **g3:** Esquema separa hecho de argumento.
- **g4:** HITL obligatorio antes de usar la salida en memorial, estrategia o comunicación con cliente.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No redactar memorial completo (`redactar_memorial_penal`).

## Riesgo si se omite
Borrador desordenado con peticiones desconectadas de los hechos probados.
