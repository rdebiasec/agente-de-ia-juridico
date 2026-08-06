<!-- config-version: 3; checksum: 73e805c135d78d70 -->
---
name: detectar-riesgos-atipicidad
description: Contrato penal-víctimas: Detectar riesgo de atipicidad o naturaleza no penal antes de actuaciones que presupongan delito. Activar cuando el plan/HITL o el especialista requiera `detectar_riesgos_atipicidad`. No sustituye a `descomponer_elementos_tipo_penal`.
disable-model-invocation: true
---

# detectar_riesgos_atipicidad

## Scope
- Category: `Skills de tipicidad y responsabilidad penal`
- Skill ID: `detectar_riesgos_atipicidad`
- Tier: `operativo`

## Used By Agents
- `analista_responsabilidad_tipicidad`
- `analista_calidad_juridica`

## Purpose
Detectar riesgo de atipicidad o naturaleza no penal antes de actuaciones que presupongan delito.

## Rol en analista_responsabilidad_tipicidad
Gate temprano: ejecutar en paralelo con o justo después de `identificar_conductas_punibles_preliminares`. Si riesgo alto, alertar antes de ruta procesal penal.

## Fuentes KB
- `agente/conocimiento/penal.md` — marco tipico preliminar (no imputación).
- `agente/conocimiento/normas-clave.md` — criterio operativo y regla de citación.
- Herramientas: `leer_area_derecho(penal)`, `leer_normas_clave`, `buscar_en_conocimiento` antes de citar CP.
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
0. Antes de citar normas o cerrar hipótesis: leer Fuentes KB (`penal.md` / `normas-clave.md`) vía tools de grounding; sin soporte → `[PENDIENTE DE VERIFICAR]`.
1. Revisar elementos del tipo vs hechos/prueba disponibles.
2. Señalar riesgos de atipicidad o insuficiencia probatoria por elemento.
3. No afirmar inocencia ni tipicidad definitiva.
4. Proponer preguntas de aclaración, no conclusiones cerradas.

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

## Guardrails
- **No inventar:** No citar jurisprudencia no verificada en RAG.
- **Separar hecho de inferencia:** Atipicidad es hipótesis; no afirmar que “no es delito”.
- **Revision humana obligatoria:** Alerta de atipicidad alta debe llegar al abogado antes de radicar denuncia o memorial.
- **Fuera de alcance:** Si el caso es claramente no penal, declararlo y no forzar tipicidad.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No descomponer elementos (`descomponer_elementos_tipo_penal`).
- No calidad final (`clasificar_aprobacion_juridica` en calidad).

## Riesgo si se omite
Denuncia o memorial por delito inexistente → archivo, costos y daño a la víctima.
