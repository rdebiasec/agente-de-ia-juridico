---
name: crear-reporte-estado-caso
description: Skill atomico penal-victimas: crear reporte interno periodico. Use when the workflow requires `crear_reporte_estado_caso`.
disable-model-invocation: true
---

# crear_reporte_estado_caso

## Scope
- Category: `Skills de seguimiento procesal`
- Skill ID: `crear_reporte_estado_caso`
- Tier: `operativo`

## Used By Agents
- `gestor_seguimiento_procesal_penal`

## Purpose
Generar reporte interno del estado del caso para el despacho (no para cliente).


## Rol en gestor_seguimiento
Panorama operativo interno para el despacho; no sustituye memorial ni comunicación con cliente.
## Inputs
- Radicado, actuaciones recientes, tareas pendientes.
- Alertas de términos y seguimiento documental.

## Outputs
- Reporte: etapa, últimas actuaciones, pendientes, riesgos procesales, próximos pasos.
- Etiqueta: `REPORTE INTERNO DESPACHO`.

## Steps
1. Consolidar estado procesal y actuaciones recientes.
2. Listar pendientes, responsables y plazos.
3. Incluir alertas de términos relevantes.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `case_state_reader`
- `audit_log_write`

## Guardrails (g1–g10)
- **g6:** Reporte interno; no incluir datos innecesarios.
- **g9:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **g4:** HITL obligatorio antes de compartir reporte con cliente o terceros; uso interno despacho con revisión.
- **g8:** Aviso de revisión profesional.

## Riesgo si se omite
Despacho opera sin panorama actualizado del caso y pierde plazos.
