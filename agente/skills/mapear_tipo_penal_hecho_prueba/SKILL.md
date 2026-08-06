<!-- config-version: 3; checksum: cbe5f8425977cef0 -->
---
name: mapear-tipo-penal-hecho-prueba
description: Contrato penal-víctimas: Relacionar cada elemento del tipo penal con hechos y pruebas, visualizando fortalezas, debilidades y recaudo necesario. Activar cuando el plan/HITL o el especialista requiera `mapear_tipo_penal_hecho_prueba`. No sustituye a `construir_matriz_hecho_prue...
disable-model-invocation: true
---

# mapear_tipo_penal_hecho_prueba

## Scope
- Category: `Skills de tipicidad y responsabilidad penal`
- Skill ID: `mapear_tipo_penal_hecho_prueba`
- Tier: `estrategico`

## Used By Agents
- `analista_responsabilidad_tipicidad`
- `analista_evidencia`
- `analista_calidad_juridica`

## Purpose
Relacionar cada elemento del tipo penal con hechos y pruebas, visualizando fortalezas, debilidades y recaudo necesario.

## Rol en analista_responsabilidad_tipicidad
Producto integrador del agente. Ejecutar tras descomposición, autoría y dolo/culpa. Alimenta plan probatorio (`crear_plan_recaudo_probatorio` → `analista_evidencia`).

## Inputs
- Elementos del tipo descompuestos.
- Matriz hecho-fuente y hecho-prueba (si existen).
- Inventario probatorio del expediente.

## Outputs
- Matriz: `elemento_tipo`, `hecho`, `prueba_existente`, `prueba_faltante`, `fortaleza` (alta | media | baja), `riesgo`.
- Prioridad de recaudo por elemento débil.
- Etiqueta: `INSUMO ESTRATÉGICO — REVISIÓN ABOGADO`.

## Steps
1. Tomar hipótesis tipica y elementos descompuestos (`penal.md` paso 6).
2. Por cada `elemento_tipo`: hecho, prueba_existente, prueba_faltante, fortaleza, riesgo.
3. Celdas vacías = brecha de recaudo; priorizar elementos débiles; no inventar prueba.
4. No sustituir `inventariar_evidencia` ni `construir_matriz_hecho_prueba` (matriz genérica hecho→prueba).
5. Etiqueta `INSUMO ESTRATÉGICO — REVISIÓN ABOGADO`; HITL antes de audiencia/memorial.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `mapear_tipo_penal_hecho_prueba`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_expediente_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `rag_codigo_penal_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto

## Guardrails
- **No inventar:** No inventar pruebas ni elementos cubiertos artificialmente.
- **Separar hecho de inferencia:** Elemento “cubierto” requiere prueba identificada o hecho confirmado.
- **Revision humana obligatoria:** HITL obligatorio antes de audiencia o memorial.
- **Aviso de borrador:** Aviso de revisión profesional.


## Fuentes KB (obligatorio consultar antes de citar norma)
- `agente/conocimiento/penal.md` — marco tipico, dolo/culpa, autoría, agravantes.
- `agente/conocimiento/normas-clave.md` — marco Ley 599/906 + checklist de citación.
- Tools: `leer_area_derecho` (penal), `leer_normas_clave`, `buscar_en_conocimiento`.
- Artículo concreto no verificado → `[PENDIENTE DE VERIFICAR]`. No inventar normas.

## No duplicar
- **vs `construir_matriz_hecho_prueba`:** esta matriz es por **elemento del tipo penal**; la otra es hecho→prueba genérica.
- No plan de recaudo operativo (`crear_plan_recaudo_probatorio`).
- No suficiencia global (`evaluar_suficiencia_probatoria`).

## Riesgo si se omite
Audiencia o memorial con elementos del tipo sin prueba identificada → fracaso probatorio.
