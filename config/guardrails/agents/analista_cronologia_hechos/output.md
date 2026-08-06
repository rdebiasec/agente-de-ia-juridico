<!-- config-version: 3; checksum: a5be7a39fabb447b -->
# Guardrails de salida — analista_cronologia_hechos

## desk_policies
Políticas del despacho aplicables (ver `_shared/desk_policies.md`):
- `no_inventar` · `pedir_faltantes` · `hecho_vs_inferencia` · `hitl`
- `no_revictimizar` · `confidencialidad` · `fuera_de_alcance` · `aviso_borrador`
- `terminos_906` · `integridad_probatoria` (según dominio del agente)
Alias legacy `g1`…`g10` deprecados; no usarlos en texto nuevo.

## schema_policy
Salida alineada a: CronologiaPenal (eventos clasificados, contradicciones, vacíos, fuentes_kb).

## empty_policy
Salida vacía → tripwire `salida_vacia`.

## no_invention_policy
No inventar hechos, normas, radicados ni citas (`no_inventar`). Sin soporte → `[PENDIENTE DE VERIFICAR]`.
Invención sospechosa = soft-flag `invention_suspect` (HITL del abogado); no tripwire duro.

## groundedness_policy
Cada evento debe tener fuente o quedar en `pendiente_verificar`; separar hecho de inferencia.

## pii_policy
No exponer PII sensible innecesaria (`confidencialidad`). Flags en `output_info`.

## domain_limits
- No calificar tipicidad ni redactar memoriales.
- No inventar fechas/horas/actuaciones.
- No revictimizar al contrastar relatos.

## tripwire_message
"La salida de analista_cronologia_hechos está vacía o no es usable; se retiene para corrección."

## output_info_fields
`reason`, `chars`, `pii_flags`, `invention_suspect`, `agent`.

## enforcement
SDK: `specialist_output_guardrail`.
