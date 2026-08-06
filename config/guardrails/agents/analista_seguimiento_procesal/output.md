<!-- config-version: 3; checksum: 00e31ee8404ddbc4 -->
# Guardrails de salida — analista_seguimiento_procesal

## desk_policies
Políticas del despacho aplicables (ver `_shared/desk_policies.md`):
- `no_inventar` · `pedir_faltantes` · `hecho_vs_inferencia` · `hitl`
- `no_revictimizar` · `confidencialidad` · `fuera_de_alcance` · `aviso_borrador`
- `terminos_906` · `integridad_probatoria` (según dominio del agente)
Alias legacy `g1`…`g10` deprecados; no usarlos en texto nuevo.

## schema_policy
Salida alineada a `SeguimientoProcesal` (radicado, alertas, inactividad, `fuentes_kb`).

## empty_policy
Salida vacía → tripwire `salida_vacia`.

## no_invention_policy
No inventar hechos, normas, radicados ni actuaciones (`no_inventar`). Sin soporte → `[PENDIENTE DE VERIFICAR]`.
Invención sospechosa = soft-flag `invention_suspect` (HITL del abogado); no tripwire duro.

## groundedness_policy
Estado de radicado, actuaciones, términos e inactividad deben anclarse a expediente/KB
o quedar en `pendientes_verificacion`. Registrar `fuentes_kb` si se consultó KB/expediente.
Sin `fecha_base` no certificar vencimientos; estimaciones = `ESTIMACIÓN IA — VERIFICAR CON ABOGADO`.

## pii_policy
No exponer PII sensible innecesaria (`confidencialidad`). Flags en `output_info`.

## domain_limits
- Solo seguimiento procesal operativo (radicado, actuaciones, términos, inactividad, reporte).
- No tipicidad ni redacción de piezas; impulso escrito → redactor vía Gerente.
- Salida accionable → HITL (`HITL_OUTPUT_AGENTS`).

## tripwire_message
"La salida de analista_seguimiento_procesal está vacía o no es usable; se retiene para corrección."

## output_info_fields
`reason`, `chars`, `pii_flags`, `invention_suspect`, `agent`.

## enforcement
SDK: `specialist_output_guardrail`.
