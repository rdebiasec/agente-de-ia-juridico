<!-- config-version: 2; checksum: 2e432b7a8b54a55e -->
---
name: crear-resumen-ejecutivo-litigante
description: Skill atomico penal-victimas: crear resumen de una pagina para el abogado que interviene. Use when the workflow requires `crear_resumen_ejecutivo_litigante`.
disable-model-invocation: true
---

# crear_resumen_ejecutivo_litigante

## Scope
- Category: `Skills de representacion de victimas`
- Skill ID: `crear_resumen_ejecutivo_litigante`
- Tier: `operativo`

## Used By Agents
- `analista_audiencias`
- `analista_representacion_victimas`

## Purpose
Síntesis ejecutiva del caso para el abogado litigante (estrategia y estado, no para cliente).

## Inputs
- Teoría del caso, etapa procesal, prueba clave.
- Objetivos de representación y próximas audiencias.

## Outputs
- Resumen: situación | fortalezas | debilidades | próximos pasos | decisiones pendientes.
- Etiqueta: `RESUMEN ABOGADO — CONFIDENCIAL`.

## Steps
1. Sintetizar estado factual y procesal del caso.
2. Destacar fortalezas, debilidades y decisiones pendientes.
3. Proponer próximos pasos prioritarios para el litigante.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `crear_resumen_ejecutivo_litigante`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `case_state_reader` — no implementada
- `rag_expediente_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto

## Guardrails (g1–g10)
- **g4:** HITL obligatorio; uso interno del abogado — no envío a cliente ni terceros.
- **g6:** Confidencial; no formato cliente.
- **g5:** Lenguaje respetuoso con la víctima; sin juicios de credibilidad ni exposición innecesaria.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No resumen cliente (`preparar_resumen_operativo_cliente`).

## Riesgo si se omite
Abogado litigante sin panorama rápido antes de audiencia o reunión estratégica.
