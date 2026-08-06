<!-- config-version: 4; checksum: 5e4addcbb219de52 -->
# Guardrails de tools — analista_calidad_juridica

## desk_policies
Políticas del despacho aplicables (ver `_shared/desk_policies.md`):
- `no_inventar` · `pedir_faltantes` · `hecho_vs_inferencia` · `hitl`
- `no_revictimizar` · `confidencialidad` · `fuera_de_alcance` · `aviso_borrador`
- `terminos_906` · `integridad_probatoria` (según dominio del agente)
Alias legacy `g1`…`g10` deprecados; no usarlos en texto nuevo.

## allowed_tools_policy
Tools reales permitidas para verificar citas/hechos:
`buscar_en_expediente`, `buscar_en_conocimiento`, `leer_playbook_proceso`,
`leer_normas_clave`, `leer_area_derecho`, `listar_areas_derecho`.
No reescribir memoriales vía otras tools.
No invocar capacidades planeadas (`citation_checker`, `rag_jurisprudencia_search`,
`rag_source_validator`, `approval_gate_decision`) como function_tools.

## tripwire_message
"Tool de calidad bloqueada por política."

## enforcement
Desde Gerente: `poc_tool_*`.
