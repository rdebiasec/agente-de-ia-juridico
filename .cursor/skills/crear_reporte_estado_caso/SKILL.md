<!-- config-version: 4; checksum: 23a79d75cca81ca5 -->
---
name: crear-reporte-estado-caso
description: Contrato penal-víctimas: Generar reporte interno del estado del caso para el despacho (no para cliente). Activar cuando el plan/HITL o el especialista requiera `crear_reporte_estado_caso`. No sustituye a `preparar_resumen_operativo_cliente`.
disable-model-invocation: true
---

# crear_reporte_estado_caso

## Scope
- Category: `Skills de seguimiento procesal`
- Skill ID: `crear_reporte_estado_caso`
- Tier: `operativo`

## Used By Agents
- `analista_seguimiento_procesal`

## Purpose
Generar reporte interno del estado del caso para el despacho (no para cliente).

## Rol en analista_seguimiento_procesal
Panorama operativo interno para el despacho; no sustituye memorial ni comunicación con cliente.
## Fuentes KB
- `agente/conocimiento/proceso-penal-906.md` — etapas Ley 906, términos (días hábiles), checklist seguimiento operativo.
- `agente/conocimiento/normas-clave.md` — criterio operativo; no inventar radicados ni actuaciones.
- Herramientas: `leer_playbook_proceso(penal)`, `leer_normas_clave`, `buscar_en_conocimiento` / `buscar_en_expediente` antes de afirmar estado, plazos o movimientos.

## Inputs
- Radicado, actuaciones recientes, tareas pendientes.
- Alertas de términos y seguimiento documental.

## Outputs
- Reporte: etapa, últimas actuaciones, pendientes, riesgos procesales, próximos pasos.
- Etiqueta: `REPORTE INTERNO DESPACHO`.

## Steps
0. Anclar estado/términos a Fuentes KB/expediente; sin radicado/actuación verificada → `[PENDIENTE DE VERIFICAR]`. No inventar radicados ni movimientos judiciales.
1. Consolidar estado procesal y actuaciones recientes.
2. Listar pendientes, responsables y plazos.
3. Incluir alertas de términos relevantes.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `crear_reporte_estado_caso`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `case_state_reader` — no implementada
- `audit_log_write` — no implementada

## Guardrails
- **Confidencialidad:** Reporte interno; no incluir datos innecesarios.
- **Oportunidad y terminos Ley 906:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **Revision humana obligatoria:** HITL obligatorio antes de compartir reporte con cliente o terceros; uso interno despacho con revisión.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No resumen operativo al cliente (`preparar_resumen_operativo_cliente`).
- No resumen ejecutivo litigante (`crear_resumen_ejecutivo_litigante`).
- No bitácora de una sola actuación (`registrar_actuacion_procesal`).

## Riesgo si se omite
Despacho opera sin panorama actualizado del caso y pierde plazos.
