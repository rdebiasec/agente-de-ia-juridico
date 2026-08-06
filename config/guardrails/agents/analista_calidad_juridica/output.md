<!-- config-version: 4; checksum: a6f8f149fcb91225 -->
# Output guardrails — analista_calidad_juridica

## desk_policies
Políticas del despacho aplicables (ver `_shared/desk_policies.md`):
- `no_inventar` · `pedir_faltantes` · `hecho_vs_inferencia` · `hitl`
- `no_revictimizar` · `confidencialidad` · `fuera_de_alcance` · `aviso_borrador`
- `terminos_906` · `integridad_probatoria` (según dominio del agente)
Alias legacy `g1`…`g10` deprecados; no usarlos en texto nuevo.

## schema_policy
Salida obligatoria `DictamenCalidad` con veredicto ∈ {aprobable, con_cambios, rechazado, escalar}
y `fuentes_kb` cuando se consultó KB/expediente.

## gate_policy
`rechazado` / `escalar` = gate duro en plan_executor: no entrega accionable.

## silent_approval_policy
Nunca aprobar en silencio sin hallazgos o confirmación explícita de ausencia de hallazgos.

## no_invention_policy
No inventar normas, sentencias ni radicados (`no_inventar`).
Citas no localizadas → pendiente / no_localizada / `[PENDIENTE DE VERIFICAR]`.

## groundedness_policy
Hallazgos de citas/hechos deben anclarse a expediente/KB o quedar en
`pendientes_verificacion`. Registrar `fuentes_kb` si se consultó KB/expediente.
No afirmar vigencia ni existencia de jurisprudencia sin soporte.

## pii_policy
No exponer PII sensible innecesaria (`confidencialidad`). Minimizar datos de menor/salud.

## domain_limits
- Solo dictamen de calidad sobre piezas/análisis penales-víctimas.
- No reescribir memoriales ni tipificar (otros agentes).
- Dictamen preliminar de la IA; abogado decide uso externo.

## tripwire_message
"Dictamen sin veredicto válido; se retiene."

## output_info_fields
`reason`, `veredicto`, `chars`, `agent`.

## enforcement
SDK: `calidad_output_guardrail`.
