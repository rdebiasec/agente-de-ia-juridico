---
name: detectar-contradicciones-factuales
description: Skill operativo penal-victimas: encontrar inconsistencias entre versiones, documentos, fechas, valores o actores. Use when the workflow requires `detectar_contradicciones_factuales`.
disable-model-invocation: true
---

# detectar_contradicciones_factuales

## Scope
- Category: `Skills de hechos y cronologia`
- Skill ID: `detectar_contradicciones_factuales`
- Tier: `operativo`

## Used By Agents
- `analista_cronologia_hechos_penales`
- `analista_calidad_juridica`

## Purpose
Detectar y documentar inconsistencias entre versiones (víctima, testigos, documentos, autoridades) sin resolverlas ni concluir culpabilidad.

## Rol en analista_cronologia
Ejecutar tras cronología o matriz hecho-fuente cuando hay múltiples fuentes. No sustituye preguntas de aclaración (`generar_preguntas_aclaracion`).

## Inputs
- Cronología o matriz hecho-fuente.
- Versiones de víctima, testigos, informes de autoridad, documentos.
- Mapa de actores.

## Outputs
- Registro por contradicción: `hecho_en_tension`, `fuente_A`, `fuente_B`, `tipo` (fecha | monto | actor | secuencia | otro), `impacto` (alto | medio | bajo).
- Preguntas de aclaración sugeridas (no inductivas).
- Nota: contradicción documentada ≠ hecho desmentido.

## Steps
1. Comparar versiones de víctima, testigos, documentos y autoridades.
2. Documentar contradicciones por hecho, fecha, monto o actor.
3. Sugerir preguntas de aclaración no inductivas.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_expediente_search`
- `entity_extractor`

## Guardrails (g1–g10)
- **g1:** No inventar versiones ni citar documentos no aportados.
- **g3:** Contradicción es tensión entre fuentes, no conclusión de falsedad.
- **g4:** No comunicar contradicciones a contraparte sin revisión del abogado.
- **g5:** No formular contradicciones en lenguaje que culpe a la víctima (ej. “la víctima miente”).
- **g8:** Aviso de revisión profesional.

## No duplicar
- No señalar solo inconsistencias temporales en línea de tiempo (`construir_cronologia_penal` paso 3).
- No generar batería completa de preguntas (`generar_preguntas_aclaracion`).
- No evaluar tipicidad por contradicción (`analista_tipicidad_y_responsabilidad_penal`).

## Riesgo si se omite
Estrategia basada en versión única que colapsa ante informe de policía o declaración de testigo.
