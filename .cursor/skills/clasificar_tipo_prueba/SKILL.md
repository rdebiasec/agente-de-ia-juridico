---
name: clasificar-tipo-prueba
description: Skill atomico penal-victimas: clasificar evidencia como documental, testimonial, digital, fisica, pericial, institucional o pendiente. Use when the workflow requires `clasificar_tipo_prueba`.
disable-model-invocation: true
---

# clasificar_tipo_prueba

## Scope
- Category: `Skills de evidencia y soporte probatorio`
- Skill ID: `clasificar_tipo_prueba`
- Tier: `operativo`

## Used By Agents
- `gestor_evidencia_y_soporte_probatorio`

## Purpose
Clasificar cada elemento probatorio según tipo procesal (documental, testimonial, pericial, etc.).


## Rol en gestor_evidencia
Tipificación que alimenta matriz hecho-prueba y evaluación de fuerza probatoria.
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
- `rag_expediente_search`

## Guardrails (g1–g10)
- **g1:** No inventar tipo ni origen.
- **g9:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **g4:** HITL obligatorio antes de usar la salida en memorial, estrategia o comunicación con cliente.
- **g8:** Aviso de revisión profesional.

## Riesgo si se omite
Matriz hecho-prueba y estrategia con prueba mal categorizada o inadmisible.
