<!-- config-version: 2; checksum: e262fe9710a1a847 -->
---
name: detectar-contradicciones-factuales
description: Contrato penal-víctimas: Detectar y documentar inconsistencias entre versiones (víctima, testigos, documentos, autoridades) sin resolverlas ni concluir culpabilidad. Activar cuando el plan/HITL o el especialista requiera `detectar_contradicciones_factuales`. No sustituye a `co...
disable-model-invocation: true
---

# detectar_contradicciones_factuales

## Scope
- Category: `Skills de hechos y cronologia`
- Skill ID: `detectar_contradicciones_factuales`
- Tier: `operativo`

## Used By Agents
- `analista_cronologia_hechos`
- `analista_calidad_juridica`

## Purpose
Detectar y documentar inconsistencias entre versiones (víctima, testigos, documentos, autoridades) sin resolverlas ni concluir culpabilidad.

## Rol en analista_cronologia_hechos
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
1. Comparar relatos/fuentes sobre el mismo evento (quién, qué, cuándo, dónde).
2. Listar contradicciones con fragmentos enfrentados y fuentes.
3. Clasificar severidad (menor|material) sin resolver el fondo del caso.
4. No inventar versión conciliadora; pedir aclaración vía Gerente si aplica.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `detectar_contradicciones_factuales`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_expediente_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `entity_extractor` — no implementada

## Guardrails
- **No inventar:** No inventar versiones ni citar documentos no aportados.
- **Separar hecho de inferencia:** Contradicción es tensión entre fuentes, no conclusión de falsedad.
- **Revision humana obligatoria:** No comunicar contradicciones a contraparte sin revisión del abogado.
- **No revictimizar:** No formular contradicciones en lenguaje que culpe a la víctima (ej. “la víctima miente”).
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No señalar solo inconsistencias temporales en línea de tiempo (`construir_cronologia_penal` paso 3).
- No generar batería completa de preguntas (`generar_preguntas_aclaracion`).
- No evaluar tipicidad por contradicción (`analista_responsabilidad_tipicidad`).

## Riesgo si se omite
Estrategia basada en versión única que colapsa ante informe de policía o declaración de testigo.
