<!-- config-version: 4; checksum: 251a068991614c79 -->
# Guardrails de salida — analista_responsabilidad_tipicidad

## desk_policies
Políticas del despacho aplicables (ver `_shared/desk_policies.md`):
- `no_inventar` · `pedir_faltantes` · `hecho_vs_inferencia` · `hitl`
- `no_revictimizar` · `confidencialidad` · `fuera_de_alcance` · `aviso_borrador`
- `terminos_906` · `integridad_probatoria` (según dominio del agente)
Alias legacy `g1`…`g10` deprecados; no usarlos en texto nuevo.

## schema_policy
Salida alineada a `MatrizTipicidad`: hipótesis preliminar, fuentes KB, elementos con hecho/prueba/estado, autoría, dolo/culpa, agravantes, riesgos y pendientes.

## empty_policy
Salida vacía → tripwire `salida_vacia`.

## no_invention_policy
No inventar hechos, normas, radicados ni citas (`no_inventar`). Sin soporte → `[PENDIENTE DE VERIFICAR]`.
Invención sospechosa = soft-flag `invention_suspect` (HITL del abogado); no tripwire duro.

## pii_policy
No exponer PII sensible innecesaria (`confidencialidad`). Flags en `output_info`.

## domain_limits
No afirmar tipicidad definitiva ni imputación formal.
Resultado dañoso por sí solo no acredita dolo, autoría ni elemento del tipo.

## groundedness_policy
- Consultar `agente/conocimiento/penal.md` y `normas-clave.md` vía tools antes de citar.
- Artículo, inciso, sentencia o radicado sin soporte RAG → `[PENDIENTE DE VERIFICAR]`.
- Separar siempre `hecho_soporte` de inferencia y de conclusión jurídica.
- Etiqueta obligatoria: `HIPÓTESIS PRELIMINAR — NO IMPUTACIÓN`.

## tripwire_message
"La salida de analista_responsabilidad_tipicidad está vacía o no es usable; se retiene para corrección."

## output_info_fields
`reason`, `chars`, `pii_flags`, `invention_suspect`, `agent`.

## enforcement
SDK: `specialist_output_guardrail`.
