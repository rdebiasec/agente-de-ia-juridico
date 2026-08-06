<!-- config-version: 3; checksum: 614e8faeb355ae01 -->
---
name: crear-checklist-previo-audiencia
description: Contrato penal-víctimas: Generar lista verificable de tareas y documentos antes de una audiencia penal. Activar cuando el plan/HITL o el especialista requiera `crear_checklist_previo_audiencia`. No sustituye a `identificar_objetivo_audiencia`.
disable-model-invocation: true
---

# crear_checklist_previo_audiencia

## Scope
- Category: `Skills de audiencias`
- Skill ID: `crear_checklist_previo_audiencia`
- Tier: `operativo`

## Used By Agents
- `analista_audiencias`
- `analista_calidad_juridica`

## Purpose
Generar lista verificable de tareas y documentos antes de una audiencia penal.

## Rol en analista_audiencias
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
Skills = contratos (no function_tools invocables). No existe tool LLM `crear_checklist_previo_audiencia`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `hearing_template_loader` — no implementada
- `calendar_event_reader` — no implementada

## Guardrails
- **Revision humana obligatoria:** HITL antes de audiencia.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No definir objetivo (`identificar_objetivo_audiencia`).
- No control formal Ley 906 (`controlar_audiencias`).

## Riesgo si se omite
Olvido de prueba, memorial o requisito clave el día de la audiencia.
