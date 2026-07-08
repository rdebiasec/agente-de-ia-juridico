---
name: alinear-estrategia-prueba-proceso
description: Skill estrategico penal-victimas: alinear teoria de victima con ruta procesal y plan probatorio. Use when the workflow requires `alinear_estrategia_prueba_proceso`.
disable-model-invocation: true
---

# alinear_estrategia_prueba_proceso

## Scope
- Category: `Skills de representacion de victimas`
- Skill ID: `alinear_estrategia_prueba_proceso`
- Tier: `estrategico`

## Used By Agents
- `analista_representacion_victimas`
- `analista_calidad_juridica`

## Purpose
Detectar desalineación entre teoría del caso, ruta Ley 906 y plan probatorio; proponer ajustes coordinados.

## Rol en analista_representacion_victimas
Ejecutar tras `construir_teoria_caso_victima` y `crear_ruta_procesal_recomendada`.

## Rol en analista_calidad_juridica
Verificar coherencia estratégica antes de aprobar memorial o plan de actuación.

## Inputs
- Teoría del caso de la víctima (`construir_teoria_caso_victima`).
- Ruta procesal recomendada y etapa Ley 906.
- Matriz hecho-prueba y plan de recaudo (`crear_plan_recaudo_probatorio`, si existe).
- Objetivos priorizados de la víctima.

## Outputs
- `desalineaciones`: lista con `area` (teoria | ruta | prueba), `descripcion`, `impacto` (alto | medio | bajo).
- `ajustes_recomendados` priorizados por urgencia procesal.
- `coherencia_global`: alineado | parcial | desalineado.
- Etiqueta: `ESTRATEGIA PRELIMINAR — APROBACIÓN ABOGADO`.

## Steps
1. Contrastar teoría del caso con etapa procesal y prueba disponible.
2. Detectar desalineaciones entre ruta 906 y plan probatorio.
3. Proponer ajustes coordinados para representación de la víctima.
4. Priorizar ajustes por plazos procesales y objetivos de la víctima.
5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `case_state_reader`
- `rag_expediente_search`

## Guardrails (g1–g10)
- **g3:** Ajustes basados en hechos y etapa, no en deseos sin soporte probatorio.
- **g4:** HITL obligatorio antes de cambiar teoría o ruta aprobada.
- **g5:** Lenguaje respetuoso con la víctima; sin juicios de credibilidad ni exposición innecesaria.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No construir teoría (`construir_teoria_caso_victima`).
- No crear ruta procesal (`crear_ruta_procesal_recomendada`).
- No revisión final de coherencia (`revisar_coherencia_estrategica` — calidad).

## Riesgo si se omite
Memoriales y audiencias que persiguen objetivos inalcanzables en la etapa o sin prueba para sostenerlos.
