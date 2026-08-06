<!-- config-version: 2; checksum: 85a737ce3364d496 -->
# Guardrails de tools — analista_seguimiento_procesal

## desk_policies
Políticas del despacho aplicables (ver `_shared/desk_policies.md`):
- `no_inventar` · `pedir_faltantes` · `hecho_vs_inferencia` · `hitl`
- `no_revictimizar` · `confidencialidad` · `fuera_de_alcance` · `aviso_borrador`
- `terminos_906` · `integridad_probatoria` (según dominio del agente)
Alias legacy `g1`…`g10` deprecados; no usarlos en texto nuevo.

## allowed_tools_policy
Solo tools de conocimiento del especialista: `buscar_en_expediente`, `buscar_en_conocimiento`,
lecturas MD de área/playbook/normas según cableado del builder.
No invocar redacción ni otros especialistas (eso lo hace el Gerente vía `as_tool`).

## args_sensitivity_policy
Minimizar PII en argumentos (`confidencialidad`).

## tripwire_message
"Tool bloqueada por política de especialista (routing, PII o fuera de producto)."

## output_info_fields
`tool_name`, `reason` (`ok` | `blocked` | `pii_in_args`).

## enforcement
Las invocaciones desde el Gerente pasan por `poc_tool_input_guardrail` / `poc_tool_output_guardrail`.
