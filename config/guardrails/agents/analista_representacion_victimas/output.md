<!-- config-version: 4; checksum: bd0bbfe3078e345b -->
# Guardrails de salida — analista_representacion_victimas

## desk_policies
Políticas del despacho aplicables (ver `_shared/desk_policies.md`):
- `no_inventar` · `pedir_faltantes` · `hecho_vs_inferencia` · `hitl`
- `no_revictimizar` · `confidencialidad` · `fuera_de_alcance` · `aviso_borrador`
- `terminos_906` · `integridad_probatoria` (según dominio del agente)
Alias legacy `g1`…`g10` deprecados; no usarlos en texto nuevo.

## schema_policy
Salida alineada a: RepresentacionVictimas (teoría, derechos, daño, diferencial,
riesgos, objetivos, fuentes_kb).

## empty_policy
Salida vacía → tripwire `salida_vacia`.

## no_invention_policy
No inventar hechos, normas, radicados ni citas (`no_inventar`). Sin soporte → `[PENDIENTE DE VERIFICAR]`.
Invención sospechosa = soft-flag `invention_suspect` (HITL del abogado); no tripwire duro.

## groundedness_policy
Derechos, daño, enfoque diferencial e intereses deben anclarse a expediente/KB o quedar
en `pendientes_verificacion`. Registrar `fuentes_kb` si se consultó KB/expediente.
No inventar vulneraciones, diagnósticos médicos ni facultades de intervención.

## pii_policy
No exponer PII sensible innecesaria (`confidencialidad`). Flags en `output_info`.
Minimizar detalle gráfico del relato (menor / violencia sexual).

## domain_limits
- No culpar a la víctima (`no_revictimizar`); no prometer resultados judiciales.
- No comunicar teoría del caso al cliente sin abogado (HITL).
- No tipicidad definitiva, memoriales ni guion oral (otros agentes / plan).
- Enfoque diferencial: solo factores documentados; no estigmatizar.

## tripwire_message
"La salida de analista_representacion_victimas está vacía o no es usable; se retiene para corrección."

## output_info_fields
`reason`, `chars`, `pii_flags`, `invention_suspect`, `agent`.

## enforcement
SDK: `specialist_output_guardrail`.
