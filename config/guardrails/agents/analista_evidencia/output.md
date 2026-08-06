<!-- config-version: 4; checksum: fcd31270184c4386 -->
# Guardrails de salida — analista_evidencia

## desk_policies
Políticas del despacho aplicables (ver `_shared/desk_policies.md`):
- `no_inventar` · `pedir_faltantes` · `hecho_vs_inferencia` · `hitl`
- `no_revictimizar` · `confidencialidad` · `fuera_de_alcance` · `aviso_borrador`
- `terminos_906` · `integridad_probatoria` (según dominio del agente)
Alias legacy `g1`…`g10` deprecados; no usarlos en texto nuevo.

## schema_policy
Salida alineada a: InventarioEvidencia (items tipados, brechas, plan_recaudo, fuentes_kb).

## empty_policy
Salida vacía → tripwire `salida_vacia`.

## no_invention_policy
No inventar hechos, normas, radicados ni citas (`no_inventar`). Sin soporte → `[PENDIENTE DE VERIFICAR]`.
Invención sospechosa = soft-flag `invention_suspect` (HITL del abogado); no tripwire duro.

## groundedness_policy
Cada ítem debe tener `fuente_o_ubicacion` o quedar en `pendientes_verificacion` / `cadena_custodia=pendiente_verificar`.
No inventar hashes, folios ni cadenas de custodia; registrar `fuentes_kb` si se consultó KB/expediente.

## pii_policy
No exponer PII sensible innecesaria (`confidencialidad`). Flags en `output_info`.

## domain_limits
- No alterar evidencia (`integridad_probatoria`); no tipicidad definitiva ni memoriales.
- No afirmar admisibilidad judicial ni certeza probatoria.
- No revictimizar: no culpar a la víctima por ausencia de prueba.
- Plan de recaudo / oficios → revisión abogado (HITL) antes de ejecutar.

## tripwire_message
"La salida de analista_evidencia está vacía o no es usable; se retiene para corrección."

## output_info_fields
`reason`, `chars`, `pii_flags`, `invention_suspect`, `agent`.

## enforcement
SDK: `specialist_output_guardrail`.
