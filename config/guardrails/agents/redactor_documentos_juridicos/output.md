<!-- config-version: 1; checksum: 849c9b773d5c7844 -->
# Output guardrails — redactor_documentos_juridicos

- Salida debe ser `BorradorDocumentoPenal` con `cuerpo` no vacío.
- No inventar normas, sentencias, radicados ni anexos (g1).
- Citas o radicados sin soporte → `[PENDIENTE DE VERIFICAR]` (g1/g8).
- Escritos requieren revisión humana antes de uso externo (g4).
- Enforcement SDK: `redactor_output_guardrail` (vacío = tripwire; citas sin pendiente = flag).
