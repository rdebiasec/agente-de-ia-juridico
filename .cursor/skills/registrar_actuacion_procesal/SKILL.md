<!-- config-version: 4; checksum: f0a5ae5f6f113b06 -->
---
name: registrar-actuacion-procesal
description: Contrato penal-víctimas: Registrar en el sistema una actuación procesal nueva con fuente y fecha. Activar cuando el plan/HITL o el especialista requiera `registrar_actuacion_procesal`. No sustituye a `monitorear_radicado`.
disable-model-invocation: true
---

# registrar_actuacion_procesal

## Scope
- Category: `Skills de seguimiento procesal`
- Skill ID: `registrar_actuacion_procesal`
- Tier: `atomico`

## Used By Agents
- `analista_seguimiento_procesal`

## Purpose
Registrar en el sistema una actuación procesal nueva con fuente y fecha.

## Rol en analista_seguimiento_procesal
Bitácora operativa del expediente para cronología y reportes.
## Fuentes KB
- `agente/conocimiento/proceso-penal-906.md` — etapas Ley 906, términos (días hábiles), checklist seguimiento operativo.
- `agente/conocimiento/normas-clave.md` — criterio operativo; no inventar radicados ni actuaciones.
- Herramientas: `leer_playbook_proceso(penal)`, `leer_normas_clave`, `buscar_en_conocimiento` / `buscar_en_expediente` antes de afirmar estado, plazos o movimientos.

## Inputs
- Descripción de la actuación, fecha, documento fuente.
- Radicado del caso.

## Outputs
- Registro: `actuacion`, `fecha`, `fuente`, `timestamp_registro`.
- Confirmación de actualización de estado del caso.

## Steps
0. Anclar estado/términos a Fuentes KB/expediente; sin radicado/actuación verificada → `[PENDIENTE DE VERIFICAR]`. No inventar radicados ni movimientos judiciales.
1. Registrar actuación con descripción, fecha y fuente documental.
2. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `registrar_actuacion_procesal`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `case_state_writer` — no implementada
- `audit_log_write` — no implementada

## Guardrails
- **No inventar:** No inventar actuaciones.
- **Oportunidad y terminos Ley 906:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **Revision humana obligatoria:** HITL obligatorio antes de usar la salida en memorial, estrategia o comunicación con cliente.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No monitoreo continuo del radicado (`monitorear_radicado`).
- No gestión de backlog de tareas (`actualizar_tareas_responsable`).

## Riesgo si se omite
Expediente interno desactualizado y errores en alertas de términos.
