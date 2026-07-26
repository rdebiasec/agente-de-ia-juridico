<!-- config-version: 2; checksum: 60ac8fb70bc57b36 -->
---
name: mapear-tipo-penal-hecho-prueba
description: Skill estrategico penal-victimas: relacionar elementos del tipo con hechos y pruebas. Use when the workflow requires `mapear_tipo_penal_hecho_prueba`.
disable-model-invocation: true
---

# mapear_tipo_penal_hecho_prueba

## Scope
- Category: `Skills de tipicidad y responsabilidad penal`
- Skill ID: `mapear_tipo_penal_hecho_prueba`
- Tier: `estrategico`

## Used By Agents
- `analista_tipicidad_y_responsabilidad_penal`
- `gestor_evidencia_y_soporte_probatorio`
- `analista_calidad_juridica`

## Purpose
Relacionar cada elemento del tipo penal con hechos y pruebas, visualizando fortalezas, debilidades y recaudo necesario.

## Rol en analista_tipicidad
Producto integrador del agente. Ejecutar tras descomposición, autoría y dolo/culpa. Alimenta plan probatorio (`crear_plan_recaudo_probatorio` → gestor evidencia).

## Inputs
- Elementos del tipo descompuestos.
- Matriz hecho-fuente y hecho-prueba (si existen).
- Inventario probatorio del expediente.

## Outputs
- Matriz: `elemento_tipo`, `hecho`, `prueba_existente`, `prueba_faltante`, `fortaleza` (alta | media | baja), `riesgo`.
- Prioridad de recaudo por elemento débil.
- Etiqueta: `INSUMO ESTRATÉGICO — REVISIÓN ABOGADO`.

## Steps
1. Relacionar cada elemento del tipo con hechos y pruebas.
2. Visualizar fortalezas y debilidades por elemento.
3. Proponer recaudo orientado a elementos débiles.
4. Entregar matriz tabular por elemento del tipo con fortalezas y debilidades.
5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

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

## Guardrails (g1–g10)
- **g1:** No inventar pruebas ni elementos cubiertos artificialmente.
- **g3:** Elemento “cubierto” requiere prueba identificada o hecho confirmado.
- **g4:** HITL obligatorio antes de audiencia o memorial.
- **g8:** Aviso de revisión profesional.

## No duplicar
- **vs `construir_matriz_hecho_prueba`:** esta matriz es por **elemento del tipo penal**; la otra es hecho→prueba genérica.
- No plan de recaudo operativo (`crear_plan_recaudo_probatorio`).
- No suficiencia global (`evaluar_suficiencia_probatoria`).

## Riesgo si se omite
Audiencia o memorial con elementos del tipo sin prueba identificada → fracaso probatorio.
