<!-- config-version: 2; checksum: ba052db266bdb1e9 -->
# Output guardrails — analista_calidad_juridica

- Salida obligatoria `DictamenCalidad` con veredicto ∈ {aprobable, con_cambios, rechazado, escalar}.
- `rechazado` / `escalar` = gate duro en plan_executor: no entrega accionable.
- Nunca aprobar en silencio sin hallazgos o confirmación explícita de ausencia de hallazgos.
- Enforcement SDK: `calidad_output_guardrail` (veredicto inválido/vacío = tripwire).
