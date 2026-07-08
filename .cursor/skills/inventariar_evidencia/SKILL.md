---
name: inventariar-evidencia
description: Skill operativo penal-victimas: crear inventario numerado de evidencia del caso. Use when the workflow requires `inventariar_evidencia`.
disable-model-invocation: true
---

# inventariar_evidencia

## Scope
- Category: `Skills de evidencia y soporte probatorio`
- Skill ID: `inventariar_evidencia`
- Tier: `operativo`

## Used By Agents
- `gestor_evidencia_y_soporte_probatorio` (skill primario del agente)

## Purpose
Recopilar y numerar todos los elementos probatorios con metadatos y custodia preliminar.


## Rol en gestor_evidencia
Base del inventario probatorio; antecede clasificación, matrices y brechas.
## Inputs
- Documentos, audios, mensajes, objetos aportados o en expediente.
- Metadatos disponibles (fecha, origen, formato).

## Outputs
- Inventario numerado: `id`, `tipo`, `descripción`, `origen`, `fecha`, `ubicación_custodia`, `hash` (si aplica).
- Elementos sin clasificar marcados `[PENDIENTE DE VERIFICAR]`.

## Steps
1. Recopilar todos los elementos disponibles (documentos, audios, mensajes, objetos).
2. Registrar metadatos, hash y ubicación de custodia preliminar.
3. Emitir inventario numerado para el expediente.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `evidence_vault_store`
- `metadata_extractor`
- `file_hash_generator`

## Guardrails (g1–g10)
- **g1:** No inventar elementos ni hashes.
- **g6:** Minimizar exposición de datos sensibles en descripciones.
- **g9:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **g4:** HITL obligatorio antes de usar la salida en memorial, estrategia o comunicación con cliente.
- **g8:** Aviso de revisión profesional.

## Handoff
- Alimenta `clasificar_tipo_prueba`, `construir_matriz_hecho_prueba`, `preservar_evidencia_digital`.

## Riesgo si se omite
Pérdida de trazabilidad probatoria y debilidad en audiencia.
