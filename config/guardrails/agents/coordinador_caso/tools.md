<!-- config-version: 1; checksum: 86590f4e3ff90f9b -->
# Guardrails de tools — coordinador_caso

## allowed_tools_policy
Solo invocar tools del **canal chat**: `buscar_en_expediente` (+ KB search si no hubo prefetch) y especialistas as-tool de bajo riesgo listados en la sección chat de `tool_routing`.
No invocar herramientas ajenas al pedido ni “por curiosidad”.
`listar_areas_derecho` y lecturas MD completas no están en el chat del Gerente.

## routing_constraints
- Completitud: gate en código antes del Runner; no re-inventar faltantes si el turno ya pasó.
- Tutela / redacción: **no disponibles como tools en chat**; solo vía plan aprobado (HITL).
- En plan: la acción de tutela está fuera del producto; no invocar especialista constitucional.
- Calidad → `analista_calidad_juridica` cuando la salida vaya a uso externo.
- Una voz: los especialistas son backoffice; el POC sintetiza.

## needs_approval_tools
Tools / vías que requieren plan aprobado (HITL) — fuera del orquestador de chat:
- `redactor_documentos_juridicos`

## approval_prompt
"El coordinador solicita usar el equipo de [redacción|audiencias|seguimiento] para: {resumen_pedido}. ¿Aprueba ejecutar este paso del plan? (web: aprobar plan · Slack: EJECUTAR)"

## args_sensitivity_policy
No pasar en argumentos de tools: cédulas completas, datos de contacto, ubicaciones exactas u otros PII no necesarios para la consulta interna (g6).
Minimizar el payload al especialista.

## ask_before_invoke_policy
Si falta contexto mínimo (hechos, radicado, etapa o tipo de pieza), pedir aclaración al abogado **antes** de invocar especialistas costosos (redactor, audiencias, seguimiento).

## tripwire_message
"No se invocó la tool porque viola la política de enrutamiento, faltan insumos, o requiere aprobación humana pendiente."

## output_info_fields
Registrar: `tool_name`, `reason` (`ok` | `needs_approval` | `blocked_routing` | `missing_context` | `pii_stripped`), `approved` (true/false/null).
