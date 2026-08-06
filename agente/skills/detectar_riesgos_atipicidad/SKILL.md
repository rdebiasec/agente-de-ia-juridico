<!-- config-version: 3; checksum: 0fac7d931e44cd27 -->
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
1. Contrastar elementos del tipo (descompuestos o hipótesis) vs hechos/prueba (`penal.md` pasos 5–6).
2. Calificar `riesgo_atipicidad` alto|medio|bajo por elementos faltantes objetivos/subjetivos.
3. Si indicios de vía no penal, anotar `conducta_alternativa` como preliminar (civil/disciplinaria/administrativa).
4. No afirmar inocencia ni tipicidad definitiva; no inventar jurisprudencia.
5. Recomendación interna + preguntas de aclaración; riesgo alto → alertar Gerente/abogado antes de radicar.

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


## Fuentes KB (obligatorio consultar antes de citar norma)
- `agente/conocimiento/penal.md` — marco tipico, dolo/culpa, autoría, agravantes.
- `agente/conocimiento/normas-clave.md` — marco Ley 599/906 + checklist de citación.
- Tools: `leer_area_derecho` (penal), `leer_normas_clave`, `buscar_en_conocimiento`.
- Artículo concreto no verificado → `[PENDIENTE DE VERIFICAR]`. No inventar normas.

## No duplicar
- No descomponer elementos (`descomponer_elementos_tipo_penal`).
- No calidad final (`clasificar_aprobacion_juridica` → `analista_calidad_juridica`).

## Riesgo si se omite
Denuncia o memorial por delito inexistente → archivo, costos y daño a la víctima.
