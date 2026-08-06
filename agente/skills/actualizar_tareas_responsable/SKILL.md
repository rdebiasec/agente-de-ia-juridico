<!-- config-version: 3; checksum: 21da80ef276bc781 -->
---
name: actualizar-tareas-responsable
description: Contrato penal-víctimas: Mantener actualizada la lista de tareas del caso con estado, plazo y responsable, para que el despacho no pierda actuaciones por falta de seguimiento. Activar cuando el plan/HITL o el especialista requiera `actualizar_tareas_responsable`. No sustituye ...
disable-model-invocation: true
---

# actualizar_tareas_responsable

## Scope
- Category: `Skills de seguimiento procesal`
- Skill ID: `actualizar_tareas_responsable`
- Tier: `atomico`

## Index Blurb
Registra tareas del triage (faltantes, urgencias, derivaciones) con responsable y plazo.

## Used By Agents
- `coordinador_caso`
- `analista_seguimiento_procesal`

## Purpose
Mantener actualizada la lista de tareas del caso con estado, plazo y responsable, para que el despacho no pierda actuaciones por falta de seguimiento.

## Rol en coordinador_caso
Registrar o actualizar tareas surgidas del triage inicial (derivación, faltantes, urgencias). Runtime: `tareas_gerencia` en `completeness.py` (no CRUD LLM).

## Inputs
- Lista de tareas abiertas del caso (id, descripción, estado actual).
- Cambios reportados en el turno (nueva tarea, cierre, replazo de responsable, nuevo plazo).
- Radicado o identificador interno del caso.
- Responsable asignado: abogado de planta, agente IA o pendiente de asignación.

## Outputs
Alineados al ledger real (`src/agents/completeness.py`):
- Tabla de tareas: `id`, `titulo`/`descripción`, `responsable`, `tipo` (`faltante` | `verificacion_especialista` | …), `estado` (`pendiente` | `cerrada`).
- Campos opcionales: `prioridad`, `motivo`, `pendiente_tipo`, `impacto_juridico`, `origen`, `creada_en`/`cerrada_en`.
- Tareas nuevas o modificadas marcadas para revisión humana.
- Alertas de tareas vencidas o sin responsable (cuando el turno las reporte).

Nota: estados ricos (`abierta`/`en_curso`/`bloqueada`) no viven en el ledger del POC; el código usa solo `pendiente`|`cerrada` para menos churn.

## Steps
1. Actualizar estado, plazo y responsable de cada tarea pendiente del caso.
2. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM de CRUD de tareas.

### Function tools (LLM)
- (ninguna; el ledger no se muta por tool del modelo)

### Side-effects de código (no son function_tools)
- `gerencia_ledger` — `tareas_gerencia` en expediente (`completeness.py`: estados `pendiente`|`cerrada`)
- `audit_trace` — spans de verificación/delegación

## Guardrails
- **No inventar:** No inventar tareas, plazos ni actuaciones no reportadas en el expediente o el turno.
- **Pedir datos faltantes:** Si falta responsable en tarea crítica, dejar `pendiente` y solicitar dato al abogado (no inventar cierre).
- **Separar hecho de inferencia:** Distinguir tarea confirmada de tarea sugerida por la IA (etiquetar sugeridas como preliminares).
- **Revision humana obligatoria:** Cambios de plazo en actuaciones procesales requieren validación del abogado responsable.
- **Confidencialidad:** No incluir datos sensibles de la víctima en descripciones de tarea si no son necesarios.
- **Oportunidad y terminos Ley 906:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **Aviso de borrador:** Cerrar con aviso de que la asignación y plazos requieren revisión profesional.

## Handoff
- Seguimiento continuo de radicado/términos → `analista_seguimiento_procesal`.
- Tareas de recolección documental → permanecen visibles para el abogado vía POC.

## No duplicar
- No calcular términos procesales (`controlar_terminos_procesales_preliminares`, `generar_alertas_terminos_vencimientos`).
- No definir la ruta estratégica del caso (`crear_ruta_procesal_recomendada`).

## Best Practices
- Toda tarea crítica sin responsable queda `pendiente` con solicitud explícita al abogado.
- Descripciones cortas y sin PII innecesaria.

## Riesgo si se omite
Tareas sin dueño ni plazo generan extemporaneidad y pérdida de oportunidad procesal en Ley 906.
