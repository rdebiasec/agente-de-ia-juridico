<!-- config-version: 4; checksum: 609b82866cb97b48 -->
---
name: clasificar-tipo-prueba
description: Contrato penal-víctimas: Clasificar cada elemento probatorio según tipo procesal (documental, testimonial, pericial, etc.). Activar cuando el plan/HITL o el especialista requiera `clasificar_tipo_prueba`. No sustituye a `inventariar_evidencia`.
disable-model-invocation: true
---

# clasificar_tipo_prueba

## Scope
- Category: `Skills de evidencia y soporte probatorio`
- Skill ID: `clasificar_tipo_prueba`
- Tier: `operativo`

## Used By Agents
- `analista_evidencia`

## Purpose
Clasificar cada elemento probatorio según tipo procesal (documental, testimonial, pericial, etc.).

## Rol en analista_evidencia
Tipificación que alimenta matriz hecho-prueba y evaluación de fuerza probatoria.
## Fuentes KB
- Inventario del caso (`inventariar_evidencia`); no inventar tipología sin descripción.
- `agente/conocimiento/proceso-penal-906.md` — contexto de descubrimiento/admisión (etapas 6–7) solo si consta actuación.
- `agente/conocimiento/normas-clave.md` — clasificación preliminar; no afirmar admisibilidad judicial.
- Tools reales: `buscar_en_expediente`, `buscar_en_conocimiento` (+ lecturas KB si hace falta anclar etapa).

## Inputs
- Inventario de evidencia (`inventariar_evidencia`).
- Descripción y origen de cada elemento.

## Outputs
- Por ítem: `id`, `tipo_prueba`, `fuerza_preliminar`, `observaciones`.
- Etiqueta: `CLASIFICACIÓN PROBATORIA PRELIMINAR`.

## Steps
1. Revisar cada elemento del inventario probatorio.
2. Asignar tipo de prueba según naturaleza y origen.
3. Señalar elementos no clasificables como pendientes.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `clasificar_tipo_prueba`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_expediente_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto

## Guardrails
- **No inventar:** No inventar tipo ni origen.
- **Oportunidad y terminos Ley 906:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **Revision humana obligatoria:** HITL obligatorio antes de usar la salida en memorial, estrategia o comunicación con cliente.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No inventariar el universo probatorio (`inventariar_evidencia`).
- No mapear hecho↔prueba (`construir_matriz_hecho_prueba`).

## Riesgo si se omite
Matriz hecho-prueba y estrategia con prueba mal categorizada o inadmisible.
