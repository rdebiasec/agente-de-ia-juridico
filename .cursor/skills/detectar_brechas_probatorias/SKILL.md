---
name: detectar-brechas-probatorias
description: Skill atomico penal-victimas: identificar hechos relevantes sin soporte suficiente. Use when the workflow requires `detectar_brechas_probatorias`.
disable-model-invocation: true
---

# detectar_brechas_probatorias

## Scope
- Category: `Skills de evidencia y soporte probatorio`
- Skill ID: `detectar_brechas_probatorias`
- Tier: `operativo`

## Used By Agents
- `gestor_evidencia_y_soporte_probatorio`
- `analista_representacion_victimas`

## Purpose
Identificar hechos relevantes sin prueba suficiente en el expediente.

## Rol en gestor_evidencia_y_soporte_probatorio
Antecede plan de recaudo.

## Rol en analista_representacion_victimas
Informa debilidades para teoría del caso.

## Inputs
- Matriz hecho-prueba (`construir_matriz_hecho_prueba`).
- Inventario de evidencia (`inventariar_evidencia`).

## Outputs
- `brechas`: hecho | prueba_ausente_o_débil | impacto (alto | medio | bajo).
- `prioridad_recaudo` ordenada.
- Etiqueta: `BRECHAS PROBATORIAS PRELIMINARES`.

## Steps
1. Contrastar hechos relevantes con prueba disponible en expediente.
2. Clasificar brechas por impacto procesal.
3. Priorizar recaudo urgente según etapa y audiencias próximas.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_expediente_search`

## Guardrails (g1–g10)
- **g1:** No asumir prueba existente sin constar en inventario.
- **g9:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **g4:** HITL obligatorio antes de usar la salida en memorial, estrategia o comunicación con cliente.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No plan de recaudo (`crear_plan_recaudo_probatorio`).
- No suficiencia global (`evaluar_suficiencia_probatoria`).

## Riesgo si se omite
Estrategia o memorial que depende de prueba que no existe ni está en camino.
