<!-- config-version: 4; checksum: 6215004ad7c8323c -->
---
name: detectar-alucinaciones-legales
description: Contrato penal-víctimas: Detectar citas normativas, sentencias, radicados o hechos inventados o no localizables en fuentes verificables. Activar cuando el plan/HITL o el especialista requiera `detectar_alucinaciones_legales`. No sustituye a `clasificar_aprobacion_juridica`.
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

## Fuentes KB
- `agente/conocimiento/normas-clave.md` — checklist calidad/citas; regla de no invención.
- `agente/conocimiento/proceso-penal-906.md` — checklist control de calidad (gate duro).
- Tools reales: `buscar_en_conocimiento`, `buscar_en_expediente`, `leer_normas_clave`, `leer_playbook_proceso`.
- Sin soporte → estado `no_localizada` o `pendiente`; no inventar que una cita “existe”.

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
0. Extraer citas/hechos y cruzar con Fuentes KB/expediente; sin soporte → no_localizada/pendiente. No inventar verificaciones.
1. Extraer citas de normas, sentencias, radicados y hechos afirmados.
2. Cruzar con expediente/KB; clasificar verificada | no_localizada | inventada | pendiente.
3. Entregar conteo y recomendación de escalamiento; no dictaminar aprobación final.

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

## Guardrails
- **No inventar:** No inventar verificaciones; si RAG no resuelve, marcar `no_localizada`.
- **Separar hecho de inferencia:** Distinguir cita incorrecta de hecho no soportado.
- **Revision humana obligatoria:** HITL antes de marcar referencia como inventada en salida externa.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No clasificar aprobación (`clasificar_aprobacion_juridica`).
- No verificar solo normas (`verificar_citas_normativas` — foco normativo).

## Riesgo si se omite
Memorial o informe con citas falsas radicado ante juez o entregado al cliente.
