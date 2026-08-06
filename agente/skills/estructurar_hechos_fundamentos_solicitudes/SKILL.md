<!-- config-version: 3; checksum: 6dfbce8de435dae9 -->
---
name: estructurar-hechos-fundamentos-solicitudes
description: Contrato penal-víctimas: Organizar esquema hechos-fundamentos-peticiones antes de redactar memorial o escrito. Activar cuando el plan/HITL o el especialista requiera `estructurar_hechos_fundamentos_solicitudes`. No sustituye a `redactar_memorial_penal`.
disable-model-invocation: true
---

# estructurar_hechos_fundamentos_solicitudes

## Scope
- Category: `Skills de redaccion juridica penal`
- Skill ID: `estructurar_hechos_fundamentos_solicitudes`
- Tier: `operativo`

## Used By Agents
- `redactor_documentos_juridicos`

## Purpose
Organizar esquema hechos-fundamentos-peticiones antes de redactar memorial o escrito.

## Rol en redactor_documentos_juridicos
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
1. Organizar esquema hechos → fundamentos → peticiones sin prosa final.
2. Anclar cada bloque a fuente; marcar pendientes.
3. No redactar el memorial completo (`redactar_memorial_penal`).

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `estructurar_hechos_fundamentos_solicitudes`.

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

## Guardrails
- **Separar hecho de inferencia:** Esquema separa hecho de argumento.
- **Revision humana obligatoria:** HITL obligatorio antes de usar la salida en memorial, estrategia o comunicación con cliente.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No redactar memorial completo (`redactar_memorial_penal`).

## Riesgo si se omite
Borrador desordenado con peticiones desconectadas de los hechos probados.
