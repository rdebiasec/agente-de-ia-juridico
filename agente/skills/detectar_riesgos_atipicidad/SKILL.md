<!-- config-version: 2; checksum: 5c1b57f7dcc68555 -->
---
name: detectar-riesgos-atipicidad
description: Skill operativo penal-victimas: detectar cuando un caso puede ser atipico o tener naturaleza no penal. Use when the workflow requires `detectar_riesgos_atipicidad`.
disable-model-invocation: true
---

# detectar_riesgos_atipicidad

## Scope
- Category: `Skills de tipicidad y responsabilidad penal`
- Skill ID: `detectar_riesgos_atipicidad`
- Tier: `operativo`

## Used By Agents
- `analista_tipicidad_y_responsabilidad_penal`
- `analista_calidad_juridica`

## Purpose
Detectar riesgo de atipicidad o naturaleza no penal antes de actuaciones que presupongan delito.

## Rol en analista_tipicidad
Gate temprano: ejecutar en paralelo con o justo después de `identificar_conductas_punibles_preliminares`. Si riesgo alto, alertar antes de ruta procesal penal.

## Inputs
- Hipótesis de tipos penales.
- Descomposición de elementos (si existe).
- Hechos soportados y vacíos documentados.

## Outputs
- `riesgo_atipicidad`: alto | medio | bajo.
- `elementos_faltantes` (objetivos y subjetivos).
- `conducta_alternativa` (civil, disciplinaria, administrativa — solo si hay indicios, marcados preliminares).
- `recomendacion_interna`: continuar análisis penal | explorar vía no penal | pedir hechos adicionales.

## Steps
1. Evaluar si faltan elementos objetivos o subjetivos del tipo.
2. Identificar conductas alternativas más ajustadas.
3. Alertar riesgo de atipicidad antes de actuación.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `detectar_riesgos_atipicidad`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_jurisprudencia_penal_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `rag_expediente_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto

## Guardrails (g1–g10)
- **g1:** No citar jurisprudencia no verificada en RAG.
- **g3:** Atipicidad es hipótesis; no afirmar que “no es delito”.
- **g4:** Alerta de atipicidad alta debe llegar al abogado antes de radicar denuncia o memorial.
- **g7:** Si el caso es claramente no penal, declararlo y no forzar tipicidad.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No descomponer elementos (`descomponer_elementos_tipo_penal`).
- No evaluar procedencia tutela (`evaluar_procedencia_tutela`).
- No calidad final (`clasificar_aprobacion_juridica` en calidad).

## Riesgo si se omite
Denuncia o memorial por delito inexistente → archivo, costos y daño a la víctima.
