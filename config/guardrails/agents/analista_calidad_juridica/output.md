<!-- config-version: 3; checksum: 525608f9696fbb12 -->
# Output guardrails — analista_calidad_juridica

## desk_policies
Políticas del despacho aplicables (ver `_shared/desk_policies.md`):
- `no_inventar` · `pedir_faltantes` · `hecho_vs_inferencia` · `hitl`
- `no_revictimizar` · `confidencialidad` · `fuera_de_alcance` · `aviso_borrador`
- `terminos_906` · `integridad_probatoria` (según dominio del agente)
Alias legacy `g1`…`g10` deprecados; no usarlos en texto nuevo.

## schema_policy
Salida obligatoria `DictamenCalidad` con veredicto ∈ {aprobable, con_cambios, rechazado, escalar}.

## gate_policy
`rechazado` / `escalar` = gate duro en plan_executor: no entrega accionable.

## silent_approval_policy
Nunca aprobar en silencio sin hallazgos o confirmación explícita de ausencia de hallazgos.

## tripwire_message
"Dictamen sin veredicto válido; se retiene."

## output_info_fields
`reason`, `veredicto`, `chars`, `agent`.

## enforcement
SDK: `calidad_output_guardrail`.
