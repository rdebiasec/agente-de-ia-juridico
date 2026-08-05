<!-- config-version: 3; checksum: 1800dfd79181ba19 -->
# Guardrails de salida — analista_representacion_victimas

## desk_policies
Políticas del despacho aplicables (ver `_shared/desk_policies.md`):
- `no_inventar` · `pedir_faltantes` · `hecho_vs_inferencia` · `hitl`
- `no_revictimizar` · `confidencialidad` · `fuera_de_alcance` · `aviso_borrador`
- `terminos_906` · `integridad_probatoria` (según dominio del agente)
Alias legacy `g1`…`g10` deprecados; no usarlos en texto nuevo.

## schema_policy
Salida alineada a: teoría del caso, derechos, riesgos de revictimización.

## empty_policy
Salida vacía → tripwire `salida_vacia`.

## no_invention_policy
No inventar hechos, normas, radicados ni citas (`no_inventar`). Sin soporte → `[PENDIENTE DE VERIFICAR]`.
Invención sospechosa = soft-flag `invention_suspect` (HITL del abogado); no tripwire duro.

## pii_policy
No exponer PII sensible innecesaria (`confidencialidad`). Flags en `output_info`.

## domain_limits
No culpar a la víctima (`no_revictimizar`); no prometer resultados.

## tripwire_message
"La salida de analista_representacion_victimas está vacía o no es usable; se retiene para corrección."

## output_info_fields
`reason`, `chars`, `pii_flags`, `invention_suspect`, `agent`.

## enforcement
SDK: `specialist_output_guardrail`.
