<!-- config-version: 2; checksum: a58113eba6d1c1a6 -->
---
name: preparar-resumen-operativo-cliente
description: Contrato penal-víctimas: Redactar resumen simple del estado del proceso para la víctima o cliente, sin estrategia sensible. Activar cuando el plan/HITL o el especialista requiera `preparar_resumen_operativo_cliente`. No sustituye a `crear_resumen_ejecutivo_litigante`.
disable-model-invocation: true
---

# preparar_resumen_operativo_cliente

## Scope
- Category: `Skills de seguimiento procesal`
- Skill ID: `preparar_resumen_operativo_cliente`
- Tier: `operativo`

## Used By Agents
- `analista_seguimiento_procesal`
- `analista_calidad_juridica`

## Purpose
Redactar resumen simple del estado del proceso para la víctima o cliente, sin estrategia sensible.

## Rol en analista_seguimiento_procesal
Comunicación periódica de avance procesal.

## Rol en analista_calidad_juridica
Aprobar tono y confidencialidad antes de envío.

## Inputs
- Estado del radicado y últimas actuaciones.
- Próximos pasos procesales públicos (no estrategia interna).
- Aprobación previa del abogado (si aplica).

## Outputs
- Resumen en lenguaje accesible: qué pasó, qué sigue, qué necesita el cliente.
- `excluido_estrategia_sensible`: confirmación explícita.
- Etiqueta: `SOLO_TRAS_APROBACION_ABOGADO — NO ENVIAR DIRECTO`.

## Steps
1. Sintetizar estado del proceso en lenguaje accesible.
2. Incluir próximos pasos sin revelar estrategia sensible.
3. Marcar para revisión humana antes de envío al cliente.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `preparar_resumen_operativo_cliente`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `case_state_reader` — no implementada
- `approval_gate_submit` — no implementada

## Guardrails
- **Revision humana obligatoria:** HITL obligatorio; nunca envío automático al cliente.
- **Confidencialidad:** No incluir datos de terceros ni detalles gráficos innecesarios.
- **Oportunidad y terminos Ley 906:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No resumen ejecutivo litigante (`crear_resumen_ejecutivo_litigante` — abogado).
- No reporte técnico (`crear_reporte_estado_caso`).

## Riesgo si se omite
Cliente desinformado o, peor, informado con datos estratégicos que no debía conocer.
