---
name: crear-matriz-hecho-fuente
description: Skill operativo penal-victimas: relacionar cada hecho con su fuente exacta. Use when the workflow requires `crear_matriz_hecho_fuente`.
disable-model-invocation: true
---

# crear_matriz_hecho_fuente

## Scope
- Category: `Skills de hechos y cronologia`
- Skill ID: `crear_matriz_hecho_fuente`
- Tier: `operativo`

## Used By Agents
- `analista_cronologia_hechos_penales`
- `analista_calidad_juridica`

## Purpose
Relacionar cada hecho relevante con su fuente exacta (documento, folio, timestamp) y nivel de soporte.

## Rol en analista_cronologia
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
- `rag_expediente_search`
- `source_reference_validator`

## Guardrails (g1–g10)
- **g1:** No inventar folios, timestamps ni documentos.
- **g2:** Sin acceso al documento citado, marcar fuente `[PENDIENTE DE VERIFICAR]`.
- **g3:** Un hecho por fila; no mezclar inferencias con hechos documentados.
- **g4:** Matriz usada en escrito requiere revisión humana.
- **g6:** No exponer PII innecesaria en la columna hecho.
- **g5:** Lenguaje respetuoso con la víctima; sin juicios de credibilidad ni exposición innecesaria.
- **g8:** Aviso de revisión profesional.

## No duplicar
- **vs `clasificar_fuente_factual`:** esta matriz exige referencia exacta (folio/timestamp); la del coordinador es preliminar.
- No construir cronología (`construir_cronologia_penal`).
- No verificar soporte de texto ya redactado (`verificar_hechos_soportados`).

## Riesgo si se omite
Hechos citados en memorial sin trazabilidad → rechazo probatorio.
