<!-- config-version: 3; checksum: 5a61418ba1630320 -->
# Guardrails de salida — analista_audiencias

## desk_policies
Políticas del despacho aplicables (ver `_shared/desk_policies.md`):
- `no_inventar` · `pedir_faltantes` · `hecho_vs_inferencia` · `hitl`
- `no_revictimizar` · `confidencialidad` · `fuera_de_alcance` · `aviso_borrador`
- `terminos_906` · `integridad_probatoria` (según dominio del agente)
Alias legacy `g1`…`g10` deprecados; no usarlos en texto nuevo.

## schema_policy
Salida alineada a: PreparacionAudiencia (objetivo, guion, solicitudes, preguntas,
riesgos, checklist, fuentes_kb).

## empty_policy
Salida vacía → tripwire `salida_vacia`.

## no_invention_policy
No inventar hechos, normas, radicados, fechas de audiencia ni citas (`no_inventar`).
Sin soporte → `[PENDIENTE DE VERIFICAR]`.
Invención sospechosa = soft-flag `invention_suspect` (HITL del abogado); no tripwire duro.

## groundedness_policy
Objetivo, guion, solicitudes y preguntas deben anclarse a expediente/KB o quedar
en `pendientes_verificacion`. Registrar `fuentes_kb` si se consultó KB/expediente.
No inventar tipo de audiencia, facultades de intervención ni decisiones judiciales previas.

## pii_policy
No exponer PII sensible innecesaria (`confidencialidad`). Flags en `output_info`.
Minimizar detalle gráfico del relato (menor / violencia sexual) en preguntas y guion.

## domain_limits
- No revictimizar en preguntas ni guion (`no_revictimizar`).
- No sustituir al abogado en sala; producto = preparación interna (HITL antes de estrados).
- No tipicidad definitiva ni memorial escrito (otros agentes / plan).
- Sin fecha/notificación fundante → no certificar oportunidad ni términos.

## tripwire_message
"La salida de analista_audiencias está vacía o no es usable; se retiene para corrección."

## output_info_fields
`reason`, `chars`, `pii_flags`, `invention_suspect`, `agent`.

## enforcement
SDK: `specialist_output_guardrail`.
