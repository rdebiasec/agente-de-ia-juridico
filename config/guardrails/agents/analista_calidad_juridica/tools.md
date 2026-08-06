<!-- config-version: 2; checksum: 603cac65bf26b886 -->
# Guardrails de tools — analista_calidad_juridica

## desk_policies
Políticas del despacho aplicables (ver `_shared/desk_policies.md`):
- `no_inventar` · `pedir_faltantes` · `hecho_vs_inferencia` · `hitl`
- `no_revictimizar` · `confidencialidad` · `fuera_de_alcance` · `aviso_borrador`
- `terminos_906` · `integridad_probatoria` (según dominio del agente)
Alias legacy `g1`…`g10` deprecados; no usarlos en texto nuevo.

## allowed_tools_policy
Knowledge/expediente para verificar citas. No reescribir memoriales vía otras tools.

## tripwire_message
"Tool de calidad bloqueada por política."

## enforcement
Desde Gerente: `poc_tool_*`.
