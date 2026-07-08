---
name: actualizar-tareas-responsable
description: Skill atomico penal-victimas: mantener lista de tareas por agente o abogado. Use when the workflow requires `actualizar_tareas_responsable`.
disable-model-invocation: true
---

# actualizar_tareas_responsable

## Scope
- Category: `Skills de seguimiento procesal`
- Skill ID: `actualizar_tareas_responsable`
- Tier: `atomico`

## Used By Agents
- `coordinador_expediente_penal`
- `gestor_seguimiento_procesal_penal`

## Purpose
Mantener actualizada la lista de tareas del caso con estado, plazo y responsable, para que el despacho no pierda actuaciones por falta de seguimiento.

## Rol en coordinador
Registrar o actualizar tareas surgidas del triage inicial (derivación, faltantes, urgencias). El seguimiento operativo continuo corresponde a `gestor_seguimiento_procesal_penal`.

## Inputs
- Lista de tareas abiertas del caso (id, descripción, estado actual).
- Cambios reportados en el turno (nueva tarea, cierre, replazo de responsable, nuevo plazo).
- Radicado o identificador interno del caso.
- Responsable asignado: abogado de planta, agente IA o pendiente de asignación.

## Outputs
- Tabla de tareas actualizada: `id`, `descripción`, `responsable`, `fecha_límite`, `dependencia`, `estado` (`abierta` | `en_curso` | `bloqueada` | `cerrada`).
- Tareas nuevas o modificadas marcadas para revisión humana.
- Alertas de tareas vencidas o sin responsable.

## Steps
1. Actualizar estado, plazo y responsable de cada tarea abierta del caso.
2. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `task_manager_create`
- `task_manager_update`

## Guardrails (g1–g10)
- **g1:** No inventar tareas, plazos ni actuaciones no reportadas en el expediente o el turno.
- **g2:** Si falta responsable o fecha límite en tarea crítica, marcar `bloqueada` y solicitar dato al abogado.
- **g3:** Distinguir tarea confirmada de tarea sugerida por la IA (etiquetar sugeridas como preliminares).
- **g4:** Cambios de plazo en actuaciones procesales requieren validación del abogado responsable.
- **g6:** No incluir datos sensibles de la víctima en descripciones de tarea si no son necesarios.
- **g9:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **g8:** Cerrar con aviso de que la asignación y plazos requieren revisión profesional.

## No duplicar
- No calcular términos procesales (`controlar_terminos_procesales_preliminares`, `generar_alertas_terminos_vencimientos`).
- No definir la ruta estratégica del caso (`crear_ruta_procesal_recomendada`).

## Riesgo si se omite
Tareas sin dueño ni plazo generan extemporaneidad y pérdida de oportunidad procesal en Ley 906.
