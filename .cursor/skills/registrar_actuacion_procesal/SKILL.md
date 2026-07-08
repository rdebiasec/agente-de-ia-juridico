---
name: registrar-actuacion-procesal
description: Skill atomico penal-victimas: registrar una actuacion nueva en la bitacora del caso. Use when the workflow requires `registrar_actuacion_procesal`.
disable-model-invocation: true
---

# registrar_actuacion_procesal

## Scope
- Category: `Skills de seguimiento procesal`
- Skill ID: `registrar_actuacion_procesal`
- Tier: `atomico`

## Used By Agents
- `gestor_seguimiento_procesal_penal`

## Purpose
Registrar en el sistema una actuación procesal nueva con fuente y fecha.


## Rol en gestor_seguimiento
Bitácora operativa del expediente para cronología y reportes.
## Inputs
- Descripción de la actuación, fecha, documento fuente.
- Radicado del caso.

## Outputs
- Registro: `actuacion`, `fecha`, `fuente`, `timestamp_registro`.
- Confirmación de actualización de estado del caso.

## Steps
1. Registrar actuación con descripción, fecha y fuente documental.
2. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `case_state_writer`
- `audit_log_write`

## Guardrails (g1–g10)
- **g1:** No inventar actuaciones.
- **g9:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **g4:** HITL obligatorio antes de usar la salida en memorial, estrategia o comunicación con cliente.
- **g8:** Aviso de revisión profesional.

## Riesgo si se omite
Expediente interno desactualizado y errores en alertas de términos.
