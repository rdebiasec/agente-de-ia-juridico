<!-- config-version: 6; checksum: 28c265295e06a315 -->
# Guardrails de tools — coordinador_caso

## desk_policies
Políticas del despacho aplicables (ver `_shared/desk_policies.md`):
- `no_inventar` · `pedir_faltantes` · `hecho_vs_inferencia` · `hitl`
- `no_revictimizar` · `confidencialidad` · `fuera_de_alcance` · `aviso_borrador`
- `terminos_906` · `integridad_probatoria` (según dominio del agente)
Alias legacy `g1`…`g10` deprecados; no usarlos en texto nuevo.

## allowed_tools_policy
Solo invocar tools del **canal chat**: `buscar_en_expediente` (+ KB search si no hubo prefetch) y especialistas as-tool de bajo riesgo listados en la sección chat de `tool_routing`.
No invocar herramientas ajenas al pedido ni “por curiosidad”.
`listar_areas_derecho` y lecturas MD completas no están en el chat del Gerente.

## routing_constraints
- Completitud: gate en código antes del Runner; no re-inventar faltantes si el turno ya pasó.
- Calidad → `analista_calidad_juridica` cuando la salida vaya a uso externo.
- Una voz: los especialistas son backoffice; el POC sintetiza.

## needs_approval_tools
Tools / vías que requieren plan aprobado (HITL) — fuera del orquestador de chat:
- `redactor_documentos_juridicos`

## approval_prompt
"El coordinador solicita usar el equipo de [redacción|audiencias|seguimiento] para: {resumen_pedido}. ¿Aprueba ejecutar este paso del plan? (web: aprobar plan · Slack: EJECUTAR)"

## args_sensitivity_policy
No pasar en argumentos de tools: cédulas completas, datos de contacto, ubicaciones exactas u otros PII no necesarios para la consulta interna (`confidencialidad`).
Minimizar el payload al especialista.

## ask_before_invoke_policy
Si falta contexto mínimo (hechos, radicado, etapa o tipo de pieza), pedir aclaración al abogado **antes** de invocar especialistas costosos (redactor, audiencias, seguimiento).

## tripwire_message
"No se invocó la tool porque viola la política de enrutamiento, faltan insumos, o requiere aprobación humana pendiente."

## output_info_fields
Registrar: `tool_name`, `reason` (`ok` | `needs_approval` | `blocked_routing` | `missing_context` | `pii_stripped`), `approved` (true/false/null).
