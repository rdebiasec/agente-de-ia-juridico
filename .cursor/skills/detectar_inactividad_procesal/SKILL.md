---
name: detectar-inactividad-procesal
description: Skill operativo penal-victimas: alertar falta de movimientos por periodo relevante. Use when the workflow requires `detectar_inactividad_procesal`.
disable-model-invocation: true
---

# detectar_inactividad_procesal

## Scope
- Category: `Skills de seguimiento procesal`
- Skill ID: `detectar_inactividad_procesal`
- Tier: `operativo`

## Used By Agents
- `analista_ruta_procesal_ley906`
- `gestor_seguimiento_procesal_penal`

## Purpose
Detectar periodos sin movimiento procesal relevante y sugerir impulso si corresponde.

## Rol en analista_ruta_procesal
Evaluación estratégica de silencio fiscal/judicial para recomendar solicitud de impulso. El monitoreo diario es del gestor de seguimiento.

## Rol en gestor_seguimiento
Alerta operativa periódica sobre radicado.

## Inputs
- Última actuación registrada (fecha, tipo, fuente).
- Etapa procesal y plazos razonables de la etapa.
- Consulta estado radicado (`process_lookup_query`).

## Outputs
- `periodo_inactividad` (días/meses).
- `ultima_actuacion` con fuente.
- `riesgo` (pérdida prueba, archivo, olvido víctima).
- `accion_sugerida` (solicitud impulso, derecho petición, seguimiento).
- Derivar a `evaluar_solicitud_fiscalia_juez` si procede impulso.

## Steps
1. Comparar última actuación con plazos razonables de la etapa.
2. Alertar periodos sin movimiento relevante.
3. Sugerir actuación de impulso si corresponde.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `process_lookup_query`
- `case_state_reader`

## Guardrails (g1–g10)
- **g1:** Última actuación con fuente y timestamp de consulta.
- **g3:** Inactividad inferida sin consulta radicado = pendiente.
- **g9:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **g4:** HITL obligatorio antes de usar la salida en memorial, estrategia o comunicación con cliente.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No redactar impulso (`redactar_solicitud_impulso_procesal` → redactor).
- No monitoreo continuo (`monitorear_radicado` → gestor).

## Riesgo si se omite
Archivo o abandono del caso por inactividad institucional no impugnada.
