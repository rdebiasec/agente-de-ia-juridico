---
name: crear-checklist-previo-audiencia
description: Skill atomico penal-victimas: listar requisitos antes de audiencia. Use when the workflow requires `crear_checklist_previo_audiencia`.
disable-model-invocation: true
---

# crear_checklist_previo_audiencia

## Scope
- Category: `Skills de audiencias`
- Skill ID: `crear_checklist_previo_audiencia`
- Tier: `operativo`

## Used By Agents
- `preparador_estrategico_audiencias_penales`
- `analista_calidad_juridica`

## Purpose
Generar lista verificable de tareas y documentos antes de una audiencia penal.

## Rol en preparador_estrategico_audiencias_penales
Checklist operativo tras definir objetivo de audiencia.

## Rol en analista_calidad_juridica
Verificar completitud del paquete de audiencia.

## Inputs
- Tipo de audiencia y fecha.
- Objetivo de audiencia (`identificar_objetivo_audiencia`).
- Materiales preparados (guion, preguntas, pruebas).

## Outputs
- Checklist: `ítem`, `responsable`, `estado` (listo | pendiente | no_aplica).
- `documentos_requeridos` y plazos internos.
- Etiqueta: `CHECKLIST PRE-AUDIENCIA`.

## Steps
1. Listar requisitos formales y materiales según tipo de audiencia.
2. Cruzar con objetivo táctico y prueba disponible.
3. Asignar responsable y estado por ítem.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `hearing_template_loader`
- `calendar_event_reader`

## Guardrails (g1–g10)
- **g4:** HITL antes de audiencia.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No definir objetivo (`identificar_objetivo_audiencia`).
- No control formal Ley 906 (`controlar_audiencias`).

## Riesgo si se omite
Olvido de prueba, memorial o requisito clave el día de la audiencia.
