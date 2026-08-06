<!-- config-version: 4; checksum: aca411d8957c8516 -->
# Guardrails de salida — analista_ruta_procesal

## desk_policies
Políticas del despacho aplicables (ver `_shared/desk_policies.md`):
- `no_inventar` · `pedir_faltantes` · `hecho_vs_inferencia` · `hitl`
- `no_revictimizar` · `confidencialidad` · `fuera_de_alcance` · `aviso_borrador`
- `terminos_906` · `integridad_probatoria` (según dominio del agente)
Alias legacy `g1`…`g10` deprecados; no usarlos en texto nuevo.

## schema_policy
Salida alineada a: `etapa_ley906` canónica, `evidencia_etapa`, oportunidades, riesgos, ruta numerada y pendientes.

## empty_policy
Salida vacía → tripwire `salida_vacia`.

## no_invention_policy
No inventar hechos, normas, radicados ni citas (`no_inventar`). Sin soporte → `[PENDIENTE DE VERIFICAR]`.
Invención sospechosa = soft-flag `invention_suspect` (HITL del abogado); no tripwire duro.

## pii_policy
No exponer PII sensible innecesaria (`confidencialidad`). Flags en `output_info`.

## domain_limits
- Etapa procesal solo desde el enum canónico de `agente/conocimiento/proceso-penal-906.md`.
- Sin actuación y fecha fuente, la etapa es inferida o `pendiente_verificar`, nunca acreditada.
- Sin fecha base no certificar vencimiento. Toda estimación usa días hábiles y la etiqueta `ESTIMACIÓN IA — VERIFICAR CON ABOGADO`.
- Memorial, impulso u otra pieza accionable → redactor + plan HITL; este agente no redacta ni ejecuta.

## groundedness_policy
- Consultar `proceso-penal-906.md` vía `leer_playbook_proceso`.
- Artículo, actuación, notificación o fecha sin soporte → `[PENDIENTE DE VERIFICAR]`.
- Cada paso de ruta debe declarar soporte normativo verificado o pendiente.

## tripwire_message
"La salida de analista_ruta_procesal está vacía o no es usable; se retiene para corrección."

## output_info_fields
`reason`, `chars`, `pii_flags`, `invention_suspect`, `agent`.

## enforcement
SDK: `specialist_output_guardrail`.
