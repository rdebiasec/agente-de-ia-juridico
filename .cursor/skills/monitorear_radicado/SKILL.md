---
name: monitorear-radicado
description: Skill atomico penal-victimas: consultar o registrar estado de radicado. Use when the workflow requires `monitorear_radicado`.
disable-model-invocation: true
---

# monitorear_radicado

## Scope
- Category: `Skills de seguimiento procesal`
- Skill ID: `monitorear_radicado`
- Tier: `atomico`

## Used By Agents
- `gestor_seguimiento_procesal_penal` (skill primario del agente)

## Purpose
Consultar o registrar estado del radicado con fuente y timestamp.


## Rol en gestor_seguimiento
Consulta puntual de estado; alimenta alertas y reportes de seguimiento.
## Inputs
- Número de radicado (si consta).
- Última consulta registrada (si existe).

## Outputs
- Estado del radicado, fuente, `timestamp_consulta`.
- Cambios respecto a consulta anterior (si aplica).

## Steps
1. Consultar o registrar estado del radicado con fuente y timestamp de la consulta.
2. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `process_lookup_query`
- `audit_log_write`

## Guardrails (g1–g10)
- **g1:** No inventar actuaciones ni estados.
- **g9:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **g4:** HITL obligatorio antes de usar la salida en memorial, estrategia o comunicación con cliente.
- **g8:** Aviso de revisión profesional.

## Handoff
- Cambios relevantes → `registrar_actuacion_procesal`, `detectar_inactividad_procesal`.

## Riesgo si se omite
Desfase entre estado real del proceso y estrategia del despacho.
