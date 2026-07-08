---
name: generar-alertas-terminos-vencimientos
description: Skill operativo penal-victimas: crear alertas de posibles vencimientos. Use when the workflow requires `generar_alertas_terminos_vencimientos`.
disable-model-invocation: true
---

# generar_alertas_terminos_vencimientos

## Scope
- Category: `Skills de seguimiento procesal`
- Skill ID: `generar_alertas_terminos_vencimientos`
- Tier: `operativo`

## Used By Agents
- `analista_ruta_procesal_ley906`
- `gestor_seguimiento_procesal_penal`

## Purpose
Generar alertas de vencimientos próximos clasificadas por criticidad.

## Rol en analista_ruta_procesal
Alertas ligadas a actuación estratégica inminente (recurso, audiencia). Complementa `controlar_terminos_procesales_preliminares`.

## Rol en gestor_seguimiento
Calendario operativo del caso.

## Inputs
- Términos identificados (`controlar_terminos_procesales_preliminares`).
- Calendario de audiencias y actuaciones.
- Responsable asignado por alerta.

## Outputs
- Alertas: `id`, `descripcion`, `fecha_objetivo`, `criticidad` (crítica | alta | media), `responsable`, `nivel_confianza`.
- Notificación sugerida (sí/no).

## Steps
1. Identificar vencimientos próximos en calendario procesal.
2. Clasificar alertas por criticidad.
3. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `calendar_terms_calculator`
- `notification_create`

## Guardrails (g1–g10)
- **g1:** Fechas estimadas etiquetadas como tales.
- **g4:** Alerta crítica dispara revisión humana, no actuación automática.
- **g9:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **g8:** Verificación humana de términos.

## No duplicar
- No identificar términos desde cero (`controlar_terminos_procesales_preliminares`).
- No urgencia global del caso (`detectar_urgencia_penal`).

## Riesgo si se omite
Vencimientos no visibles hasta que ya es tarde para recurrir.
