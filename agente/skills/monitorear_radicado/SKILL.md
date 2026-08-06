<!-- config-version: 3; checksum: 6478e8939e885d1a -->
---
name: monitorear-radicado
description: Contrato penal-víctimas: Consultar o registrar estado del radicado con fuente y timestamp. Activar cuando el plan/HITL o el especialista requiera `monitorear_radicado`. No sustituye a `seguimiento_documentos_radicados`.
disable-model-invocation: true
---

# monitorear_radicado

## Scope
- Category: `Skills de seguimiento procesal`
- Skill ID: `monitorear_radicado`
- Tier: `atomico`

## Used By Agents
- `analista_seguimiento_procesal` (skill primario del agente)

## Purpose
Consultar o registrar estado del radicado con fuente y timestamp.

## Rol en analista_seguimiento_procesal
Consulta puntual de estado; alimenta alertas y reportes de seguimiento.
## Inputs
- Número de radicado (si consta).
- Última consulta registrada (si existe).

## Outputs
- Estado del radicado, fuente, `timestamp_consulta`.
- Cambios respecto a consulta anterior (si aplica).

## Steps
1. Registrar o consultar estado del radicado con fuente y timestamp.
2. Listar última actuación conocida sin inventar movimientos.
3. Marcar inconsistencias de número/estado como pendientes.
4. No sustituir seguimiento documental profundo ni alertas de términos.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `monitorear_radicado`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `process_lookup_query` — no implementada
- `audit_log_write` — no implementada

## Guardrails
- **No inventar:** No inventar actuaciones ni estados.
- **Oportunidad y terminos Ley 906:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **Revision humana obligatoria:** HITL obligatorio antes de usar la salida en memorial, estrategia o comunicación con cliente.
- **Aviso de borrador:** Aviso de revisión profesional.

## Handoff
- Cambios relevantes → `registrar_actuacion_procesal`, `detectar_inactividad_procesal`.

## No duplicar
- No inventario documental profundo (`seguimiento_documentos_radicados`).
- No análisis de inactividad estratégica (`detectar_inactividad_procesal`).
- No alertas de términos (`generar_alertas_terminos_vencimientos`).

## Riesgo si se omite
Desfase entre estado real del proceso y estrategia del despacho.
