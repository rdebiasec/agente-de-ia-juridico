<!-- config-version: 3; checksum: 182d9c17c8812a24 -->
---
name: crear-matriz-hecho-fuente
description: Contrato penal-víctimas: Relacionar cada hecho relevante con su fuente exacta (documento, folio, timestamp) y nivel de soporte. Activar cuando el plan/HITL o el especialista requiera `crear_matriz_hecho_fuente`. No sustituye a `clasificar_fuente_factual`.
disable-model-invocation: true
---

# crear_matriz_hecho_fuente

## Scope
- Category: `Skills de hechos y cronologia`
- Skill ID: `crear_matriz_hecho_fuente`
- Tier: `operativo`

## Used By Agents
- `analista_cronologia_hechos`
- `analista_calidad_juridica`

## Purpose
Relacionar cada hecho relevante con su fuente exacta (documento, folio, timestamp) y nivel de soporte.

## Rol en analista_cronologia_hechos
Puente entre extracción y cronología. Profundiza la matriz preliminar del coordinador (`clasificar_fuente_factual`) con referencias verificables.

## Inputs
- Lista de hechos extraídos (`extraer_hechos_relevantes`).
- Expediente y documentos disponibles.
- Clasificación preliminar de fuentes (si viene del coordinador).

## Outputs
- Tabla: `hecho`, `fuente_exacta`, `tipo_fuente`, `nivel_soporte`, `pendiente` (sí/no).
- Conteo de hechos sin fuente.
- Lista de fuentes a solicitar al abogado.

## Steps
1. Listar hechos relevantes uno a uno.
2. Vincular cada hecho con fuente exacta (documento, folio, timestamp).
3. Señalar hechos sin fuente como pendientes.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `crear_matriz_hecho_fuente`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_expediente_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `source_reference_validator` — no implementada

## Guardrails
- **No inventar:** No inventar folios, timestamps ni documentos.
- **Pedir datos faltantes:** Sin acceso al documento citado, marcar fuente `[PENDIENTE DE VERIFICAR]`.
- **Separar hecho de inferencia:** Un hecho por fila; no mezclar inferencias con hechos documentados.
- **Revision humana obligatoria:** Matriz usada en escrito requiere revisión humana.
- **Confidencialidad:** No exponer PII innecesaria en la columna hecho.
- **No revictimizar:** Lenguaje respetuoso con la víctima; sin juicios de credibilidad ni exposición innecesaria.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- **vs `clasificar_fuente_factual`:** esta matriz exige referencia exacta (folio/timestamp); la del coordinador es preliminar.
- No construir cronología (`construir_cronologia_penal`).
- No verificar soporte de texto ya redactado (`verificar_hechos_soportados`).

## Riesgo si se omite
Hechos citados en memorial sin trazabilidad → rechazo probatorio.
