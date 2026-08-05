<!-- config-version: 2; checksum: 521472bc509898e5 -->
---
name: detectar-inactividad-procesal
description: Contrato penal-víctimas: Detectar periodos sin movimiento procesal relevante y sugerir impulso si corresponde. Activar cuando el plan/HITL o el especialista requiera `detectar_inactividad_procesal`. No sustituye a `redactar_solicitud_impulso_procesal`.
disable-model-invocation: true
---

# detectar_inactividad_procesal

## Scope
- Category: `Skills de seguimiento procesal`
- Skill ID: `detectar_inactividad_procesal`
- Tier: `operativo`

## Used By Agents
- `analista_ruta_procesal`
- `analista_seguimiento_procesal`

## Purpose
Detectar periodos sin movimiento procesal relevante y sugerir impulso si corresponde.

## Rol en analista_ruta_procesal
Evaluación estratégica de silencio fiscal/judicial para recomendar solicitud de impulso. El monitoreo diario es del gestor de seguimiento.

## Rol en analista_seguimiento_procesal
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
1. Comparar última actuación conocida vs tiempo transcurrido.
2. Señalar inactividad material y posibles impulsos.
3. No inventar actuaciones; no sustituir monitoreo de radicado.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `detectar_inactividad_procesal`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `process_lookup_query` — no implementada
- `case_state_reader` — no implementada

## Guardrails
- **No inventar:** Última actuación con fuente y timestamp de consulta.
- **Separar hecho de inferencia:** Inactividad inferida sin consulta radicado = pendiente.
- **Oportunidad y terminos Ley 906:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **Revision humana obligatoria:** HITL obligatorio antes de usar la salida en memorial, estrategia o comunicación con cliente.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No redactar impulso (`redactar_solicitud_impulso_procesal` → redactor).
- No monitoreo continuo (`monitorear_radicado` → gestor).

## Riesgo si se omite
Archivo o abandono del caso por inactividad institucional no impugnada.
