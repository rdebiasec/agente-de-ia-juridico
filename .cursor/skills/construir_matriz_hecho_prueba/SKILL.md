---
name: construir-matriz-hecho-prueba
description: Skill operativo penal-victimas: relacionar hechos con pruebas existentes y faltantes. Use when the workflow requires `construir_matriz_hecho_prueba`.
disable-model-invocation: true
---

# construir_matriz_hecho_prueba

## Scope
- Category: `Skills de evidencia y soporte probatorio`
- Skill ID: `construir_matriz_hecho_prueba`
- Tier: `operativo`

## Used By Agents
- `gestor_evidencia_y_soporte_probatorio` (uso principal operativo)
- `analista_tipicidad_y_responsabilidad_penal` (vista factual para tipicidad)
- `preparador_estrategico_audiencias_penales`

## Purpose
Vincular hechos relevantes con prueba existente, faltante o en trámite, priorizando brechas críticas.

## Rol en analista_tipicidad
Vista **factual** de soporte probatorio antes o en paralelo con `mapear_tipo_penal_hecho_prueba`. No sustituye la matriz por elemento del tipo.

## Inputs
- Hechos relevantes de la teoría del caso (cronología verificada).
- Inventario probatorio disponible.
- Objetivo: tipicidad | audiencia | memorial.

## Outputs
- Matriz: `hecho`, `prueba_existente`, `prueba_faltante`, `en_tramite`, `fortaleza`, `brecha`, `accion_sugerida`.
- Brechas priorizadas que afectan tipicidad o audiencia.

## Steps
1. Listar hechos relevantes para la teoría del caso.
2. Vincular cada hecho con prueba existente, faltante o en trámite.
3. Priorizar brechas que afecten tipicidad o audiencia.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_expediente_search`
- `source_reference_validator`

## Guardrails (g1–g10)
- **g1:** No inventar pruebas ni estados “en trámite” sin constancia.
- **g3:** Hecho sin prueba = brecha, no hecho probado.
- **g4:** Matriz para memorial requiere revisión humana.
- **g9:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **g8:** Aviso de revisión profesional.

## No duplicar
- **vs `mapear_tipo_penal_hecho_prueba`:** esta matriz es hecho→prueba; la otra es elemento del tipo→hecho→prueba.
- No inventariar evidencia (`inventariar_evidencia`).
- No plan de recaudo (`crear_plan_recaudo_probatorio`).

## Riesgo si se omite
Brechas probatorias no detectadas hasta audiencia o formulación de cargos.
