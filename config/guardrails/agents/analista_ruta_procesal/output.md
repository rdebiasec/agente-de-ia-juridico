<!-- config-version: 3; checksum: d098f3ef5df0e8ec -->
# Guardrails de salida — analista_ruta_procesal

## desk_policies
Políticas del despacho aplicables (ver `_shared/desk_policies.md`):
- `no_inventar` · `pedir_faltantes` · `hecho_vs_inferencia` · `hitl`
- `no_revictimizar` · `confidencialidad` · `fuera_de_alcance` · `aviso_borrador`
- `terminos_906` · `integridad_probatoria` (según dominio del agente)
Alias legacy `g1`…`g10` deprecados; no usarlos en texto nuevo.

## schema_policy
Salida alineada a: RutaProcesalLey906 (etapa_ley906, evidencia_etapa, ruta, fuentes_kb).

## empty_policy
Salida vacía → tripwire `salida_vacia`.

## no_invention_policy
No inventar hechos, normas, radicados ni citas (`no_inventar`). Sin soporte → `[PENDIENTE DE VERIFICAR]`.
Invención sospechosa = soft-flag `invention_suspect` (HITL del abogado); no tripwire duro.

## groundedness_policy
Anclar etapa a `agente/conocimiento/proceso-penal-906.md`; términos en días hábiles con `fecha_base`.

## pii_policy
No exponer PII sensible innecesaria (`confidencialidad`). Flags en `output_info`.

## domain_limits
- No inventar etapas ni notificaciones.
- Sin fecha_base no certificar plazos ni extemporaneidad.
- Piezas accionables requieren HITL / abogado.

## tripwire_message
"La salida de analista_ruta_procesal está vacía o no es usable; se retiene para corrección."

## output_info_fields
`reason`, `chars`, `pii_flags`, `invention_suspect`, `agent`.

## enforcement
SDK: `specialist_output_guardrail`.
