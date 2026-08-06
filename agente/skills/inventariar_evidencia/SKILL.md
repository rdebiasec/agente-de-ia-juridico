<!-- config-version: 4; checksum: 4ffd5d70c26a88ed -->
---
name: inventariar-evidencia
description: Contrato penal-víctimas: Recopilar y numerar todos los elementos probatorios con metadatos y custodia preliminar. Activar cuando el plan/HITL o el especialista requiera `inventariar_evidencia`. No sustituye a `clasificar_tipo_prueba`.
disable-model-invocation: true
---

# inventariar_evidencia

## Scope
- Category: `Skills de evidencia y soporte probatorio`
- Skill ID: `inventariar_evidencia`
- Tier: `operativo`

## Used By Agents
- `analista_evidencia` (skill primario del agente)

## Purpose
Recopilar y numerar todos los elementos probatorios con metadatos y custodia preliminar.

## Rol en analista_evidencia
Base del inventario probatorio; antecede clasificación, matrices y brechas.
## Fuentes KB
- Expediente/relato del caso (existencia y descripción de soportes); no inventar folios ni hashes.
- `agente/conocimiento/proceso-penal-906.md` — momento procesal del recaudo/descubrimiento (etapas 5–7) sin certificar admisibilidad.
- `agente/conocimiento/normas-clave.md` — integridad, no revictimización y HITL antes de uso externo.
- Tools reales: `buscar_en_expediente`, `buscar_en_conocimiento`, lecturas KB (`leer_area_derecho` / `leer_playbook_proceso` / `leer_normas_clave`).

## Inputs
- Documentos, audios, mensajes, objetos aportados o en expediente.
- Metadatos disponibles (fecha, origen, formato).

## Outputs
- Inventario numerado: `id`, `tipo`, `descripción`, `origen`, `fecha`, `ubicación_custodia`, `hash` (si aplica).
- Elementos sin clasificar marcados `[PENDIENTE DE VERIFICAR]`.

## Steps
1. Listar cada medio de prueba mencionado o allegado con identificador provisional.
2. Anotar metadatos mínimos: tipo, fuente, fecha_si_consta, custodia_preliminar, legibilidad.
3. Separar evidencia existente de la solo narrada; marcar narrada como pendiente de recaudo.
4. Entregar inventario numerado; no clasificar tipología profunda ni matriz hecho-prueba aquí.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `inventariar_evidencia`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `evidence_vault_store` — no implementada
- `metadata_extractor` — no implementada
- `file_hash_generator` — no implementada

## Guardrails
- **Integridad probatoria:** Inventariar sin alterar originales; registrar estado y ubicación.
- **No inventar:** No inventar elementos ni hashes.
- **Confidencialidad:** Minimizar exposición de datos sensibles en descripciones.
- **Oportunidad y terminos Ley 906:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **Revision humana obligatoria:** HITL obligatorio antes de usar la salida en memorial, estrategia o comunicación con cliente.
- **Aviso de borrador:** Aviso de revisión profesional.

## Handoff
- Alimenta `clasificar_tipo_prueba`, `construir_matriz_hecho_prueba`, `preservar_evidencia_digital`.

## No duplicar
- No clasificar tipología probatoria en profundidad (`clasificar_tipo_prueba`).
- No construir matriz hecho-prueba (`construir_matriz_hecho_prueba`).
- No diseñar plan de recaudo (`crear_plan_recaudo_probatorio`).

## Riesgo si se omite
Pérdida de trazabilidad probatoria y debilidad en audiencia.
