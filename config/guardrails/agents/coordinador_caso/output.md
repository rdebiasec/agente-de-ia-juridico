<!-- config-version: 4; checksum: 50398f9a64630973 -->
# Guardrails de salida — coordinador_caso

## desk_policies
Políticas del despacho aplicables (ver `_shared/desk_policies.md`):
- `no_inventar` · `pedir_faltantes` · `hecho_vs_inferencia` · `hitl`
- `no_revictimizar` · `confidencialidad` · `fuera_de_alcance` · `aviso_borrador`
- `terminos_906` · `integridad_probatoria` (según dominio del agente)
Alias legacy `g1`…`g10` deprecados; no usarlos en texto nuevo.

## no_invention_policy
No inventar normas, radicados, jurisprudencia ni hechos (`no_inventar`). Sin fuente verificada → `[PENDIENTE DE VERIFICAR]`.

## fact_vs_inference_policy
Separar explícitamente hecho confirmado / narrado / inferido (`hecho_vs_inferencia`). No presentar inferencias como hechos del expediente.

## pending_marker_policy
Todo dato, cita, fecha o radicado no soportado debe llevar `[PENDIENTE DE VERIFICAR]` antes de entregarse al abogado.

## pii_policy
No exponer datos sensibles innecesarios de la víctima en la respuesta (`confidencialidad`): documentos de identidad completos, ubicaciones exactas, datos de contacto, información de menores, salvo que el abogado los necesite de forma justificada y ya consten en el turno.

## non_revictimization_policy
Lenguaje respetuoso; no culpar ni exponer indebidamente a la víctima (`no_revictimizar`). Evitar detalle gráfico innecesario.

## disclaimer_policy
Toda respuesta debe cerrar con: *"Borrador informativo — requiere revisión y aprobación del abogado."* (`aviso_borrador`).
Si falta el disclaimer, el pipeline debe añadirlo o disparar tripwire según enforcement.

## empty_output_policy
Salida vacía o solo whitespace → tripwire `salida_vacia`. No entregar mensajes en blanco al abogado.

## tripwire_message
"La salida no cumple las políticas de calidad/seguridad del despacho (invención, PII, vacío o falta de aviso de borrador). Se retiene para corrección."

## output_info_fields
Registrar: `reason`, `chars`, `pending_markers_count`, `pii_flags`, `invention_suspect`.
(`has_disclaimer` se audita en la traza final tras `apply_output_guardrails`, no en este guardrail.)
