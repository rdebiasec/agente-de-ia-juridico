<!-- config-version: 1; checksum: f404a2805cf6fb5b -->
# Guardrails de tools — coordinador_expediente_penal

## allowed_tools_policy
Solo invocar tools pertinentes al triage y a la consulta del turno: knowledge tools + especialistas as-tool listados en `tool_routing` del prompt.
No invocar herramientas ajenas al pedido ni “por curiosidad”.

## routing_constraints
- Tutela / derechos fundamentales → primero `evaluador_derechos_fundamentales_tutela`; **nunca** `redactor_documentos_juridicos_penales` de forma directa para tutela.
- Redacción de memoriales → `redactor_documentos_juridicos_penales` solo con faltantes no bloqueantes y tras triage.
- Calidad / citas / no revictimización → `analista_calidad_juridica` cuando la salida vaya a uso externo.
- Una voz: los especialistas son backoffice; el POC sintetiza.

## needs_approval_tools
Tools que requieren aprobación humana (HITL / plan aprobado) antes o al invocarse:
- `redactor_documentos_juridicos_penales`
- `evaluador_derechos_fundamentales_tutela`
- Cualquier salida accionable de audiencia con impacto estratégico (`preparador_estrategico_audiencias_penales`) cuando el canal exija revisión.

## approval_prompt
"El coordinador solicita usar el equipo de [redacción|tutela|audiencias] para: {resumen_pedido}. ¿Aprueba ejecutar este paso del plan? (web: aprobar plan · Slack: EJECUTAR)"

## args_sensitivity_policy
No pasar en argumentos de tools: cédulas completas, datos de contacto, ubicaciones exactas u otros PII no necesarios para la consulta interna (g6).
Minimizar el payload al especialista.

## ask_before_invoke_policy
Si falta contexto mínimo (hechos, radicado, etapa o tipo de pieza), pedir aclaración al abogado **antes** de invocar especialistas costosos (redactor, tutela, audiencias).

## tripwire_message
"No se invocó la tool porque viola la política de enrutamiento, faltan insumos, o requiere aprobación humana pendiente."

## output_info_fields
Registrar: `tool_name`, `reason` (`ok` | `needs_approval` | `blocked_routing` | `missing_context` | `pii_stripped`), `approved` (true/false/null).
