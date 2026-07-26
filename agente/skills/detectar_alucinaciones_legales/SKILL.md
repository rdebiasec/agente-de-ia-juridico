<!-- config-version: 2; checksum: 1d1b772ebaccba72 -->
---
name: detectar-alucinaciones-legales
description: Skill operativo penal-victimas: detectar fuentes, hechos, conclusiones o citas inventadas. Use when the workflow requires `detectar_alucinaciones_legales`.
disable-model-invocation: true
---

# detectar_alucinaciones_legales

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `detectar_alucinaciones_legales`
- Tier: `operativo`

## Used By Agents
- `analista_calidad_juridica`

## Purpose
Detectar citas normativas, sentencias, radicados o hechos inventados o no localizables en fuentes verificables.

## Rol en analista_calidad_juridica
Primer filtro de detección; **no** clasifica aprobación final — derivar a `clasificar_aprobacion_juridica`.

## Inputs
- Documento, análisis o recomendación a revisar.
- Referencias citadas (artículos, sentencias, radicados, folios).
- Acceso RAG: normativo, jurisprudencia, expediente.

## Outputs
- `referencias_sospechosas`: lista con `tipo` (norma | sentencia | radicado | hecho), `fragmento`, `estado` (inventada | no_localizada | verificada | pendiente).
- `conteo`: verificadas / sospechosas / pendientes.
- `recomendacion`: `escalar_revision` | `corregir_antes_aprobacion` | `sin_hallazgos`.
- Etiqueta: `DETECCIÓN ALUCINACIONES — NO ES DICTAMEN DE APROBACIÓN`.

## Steps
1. Cruzar citas normativas, sentencias y radicados con fuentes verificables.
2. Marcar referencias inventadas o no localizadas en RAG.
3. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `detectar_alucinaciones_legales`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_source_validator` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `citation_checker` — no implementada
- `rag_expediente_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto

## Guardrails (g1–g10)
- **g1:** No inventar verificaciones; si RAG no resuelve, marcar `no_localizada`.
- **g3:** Distinguir cita incorrecta de hecho no soportado.
- **g4:** HITL antes de marcar referencia como inventada en salida externa.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No clasificar aprobación (`clasificar_aprobacion_juridica`).
- No verificar solo normas (`verificar_citas_normativas` — foco normativo).

## Riesgo si se omite
Memorial o informe con citas falsas radicado ante juez o entregado al cliente.
