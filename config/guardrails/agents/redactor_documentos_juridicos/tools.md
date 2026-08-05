<!-- config-version: 3; checksum: 043d13c41f51c13b -->
# Guardrails de tools — redactor_documentos_juridicos

## desk_policies
Políticas del despacho aplicables (ver `_shared/desk_policies.md`):
- `no_inventar` · `pedir_faltantes` · `hecho_vs_inferencia` · `hitl`
- `no_revictimizar` · `confidencialidad` · `fuera_de_alcance` · `aviso_borrador`
- `terminos_906` · `integridad_probatoria` (según dominio del agente)
Alias legacy `g1`…`g10` deprecados; no usarlos en texto nuevo.

## allowed_tools_policy
Knowledge tools para anclar hechos/normas. No invocar otros especialistas.

## args_sensitivity_policy
Minimizar PII en args (`confidencialidad`).

## tripwire_message

## enforcement
Desde Gerente: `poc_tool_*`. En plan: input/output del propio agente.
