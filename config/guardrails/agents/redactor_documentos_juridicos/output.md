<!-- config-version: 3; checksum: 1860c445cefc9fdf -->
# Output guardrails — redactor_documentos_juridicos

## desk_policies
Políticas del despacho aplicables (ver `_shared/desk_policies.md`):
- `no_inventar` · `pedir_faltantes` · `hecho_vs_inferencia` · `hitl`
- `no_revictimizar` · `confidencialidad` · `fuera_de_alcance` · `aviso_borrador`
- `terminos_906` · `integridad_probatoria` (según dominio del agente)
Alias legacy `g1`…`g10` deprecados; no usarlos en texto nuevo.

## schema_policy
Salida `BorradorDocumentoPenal` con `cuerpo` no vacío.

## no_invention_policy
No inventar normas, sentencias, radicados ni anexos (`no_inventar`).
Citas/radicados sin soporte → `[PENDIENTE DE VERIFICAR]`.
`citation_without_pending` = flag (soft); vacío = tripwire.

## hitl_policy
Escritos requieren revisión humana antes de uso externo (`hitl`).

## tripwire_message
"Borrador vacío o no usable; se retiene para corrección."

## output_info_fields
`reason`, `chars`, `pii_flags`, `citation_without_pending`, `agent`.

## enforcement
SDK: `redactor_output_guardrail`.
