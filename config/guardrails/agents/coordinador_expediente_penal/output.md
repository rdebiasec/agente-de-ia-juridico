<!-- config-version: 1; checksum: fff4d998a6bb2f9f -->
# Guardrails de salida — coordinador_expediente_penal

## no_invention_policy
No inventar normas, radicados, jurisprudencia ni hechos (g1). Sin fuente verificada → `[PENDIENTE DE VERIFICAR]`.

## fact_vs_inference_policy
Separar explícitamente hecho confirmado / narrado / inferido (g3). No presentar inferencias como hechos del expediente.

## pending_marker_policy
Todo dato, cita, fecha o radicado no soportado debe llevar `[PENDIENTE DE VERIFICAR]` antes de entregarse al abogado.

## pii_policy
No exponer datos sensibles innecesarios de la víctima en la respuesta (g6): documentos de identidad completos, ubicaciones exactas, datos de contacto, información de menores, salvo que el abogado los necesite de forma justificada y ya consten en el turno.

## non_revictimization_policy
Lenguaje respetuoso; no culpar ni exponer indebidamente a la víctima (g5). Evitar detalle gráfico innecesario.

## disclaimer_policy
Toda respuesta debe cerrar con: *"Borrador informativo — requiere revisión y aprobación del abogado."* (g8).
Si falta el disclaimer, el pipeline debe añadirlo o disparar tripwire según enforcement.

## empty_output_policy
Salida vacía o solo whitespace → tripwire `salida_vacia`. No entregar mensajes en blanco al abogado.

## tripwire_message
"La salida no cumple las políticas de calidad/seguridad del despacho (invención, PII, vacío o falta de aviso de borrador). Se retiene para corrección."

## output_info_fields
Registrar: `reason`, `chars`, `has_disclaimer`, `pending_markers_count`, `pii_flags`, `invention_suspect`.
