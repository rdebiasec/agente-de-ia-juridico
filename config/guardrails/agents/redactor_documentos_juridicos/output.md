<!-- config-version: 4; checksum: 2ed8a1921eb78f23 -->
# Output guardrails — redactor_documentos_juridicos

## desk_policies
Políticas del despacho aplicables (ver `_shared/desk_policies.md`):
- `no_inventar` · `pedir_faltantes` · `hecho_vs_inferencia` · `hitl`
- `no_revictimizar` · `confidencialidad` · `fuera_de_alcance` · `aviso_borrador`
- `terminos_906` · `integridad_probatoria` (según dominio del agente)
Alias legacy `g1`…`g10` deprecados; no usarlos en texto nuevo.

## schema_policy
Salida `BorradorDocumentoPenal` con `cuerpo` no vacío (hechos→fundamentos→peticiones)
y `fuentes_kb` cuando se consultó KB/expediente.

## no_invention_policy
No inventar normas, sentencias, radicados ni anexos (`no_inventar`).
Citas/radicados sin soporte → `[PENDIENTE DE VERIFICAR]`.
`citation_without_pending` = flag (soft); vacío = tripwire.

## groundedness_policy
Hechos, fundamentos y peticiones deben anclarse a expediente/KB o quedar
en `pendientes_verificacion`. Registrar `fuentes_kb` si se consultó KB/expediente.
No inventar radicados, arts CPP ni anexos.

## pii_policy
No exponer PII sensible innecesaria (`confidencialidad`). Flags en `output_info`.
Minimizar detalle gráfico del relato (menor / violencia sexual) en el cuerpo.

## hitl_policy
Escritos accionables requieren revisión humana antes de uso externo (`hitl`).
Agente en `HIGH_RISK_AGENTS` / `HITL_OUTPUT_AGENTS`: plan aprobado; no radicar ni firmar.

## domain_limits
- Solo piezas penales-víctimas (memorial, impulso, petición, ampliación).
- No tipicidad definitiva ni dictamen de calidad (otros agentes).
- Sin fecha/notificación fundante → no certificar términos ni plazos.
- Etiqueta de borrador; no sustituir firma del abogado.

## tripwire_message
"Borrador vacío o no usable; se retiene para corrección."

## output_info_fields
`reason`, `chars`, `pii_flags`, `citation_without_pending`, `agent`.

## enforcement
SDK: `redactor_output_guardrail`.
