<!-- config-version: 2; checksum: 0b2841aa091a644d -->
---
name: alinear-estrategia-prueba-proceso
description: Contrato penal-víctimas: Detectar desalineación entre teoría del caso, ruta Ley 906 y plan probatorio; proponer ajustes coordinados. Activar cuando el plan/HITL o el especialista requiera `alinear_estrategia_prueba_proceso`. No sustituye a `construir_teoria_caso_victima`.
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
Skills = contratos (no function_tools invocables). No existe tool LLM `alinear_estrategia_prueba_proceso`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `case_state_reader` — no implementada
- `rag_expediente_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto

## Guardrails
- **Separar hecho de inferencia:** Ajustes basados en hechos y etapa, no en deseos sin soporte probatorio.
- **Revision humana obligatoria:** HITL obligatorio antes de cambiar teoría o ruta aprobada.
- **No revictimizar:** Lenguaje respetuoso con la víctima; sin juicios de credibilidad ni exposición innecesaria.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No construir teoría (`construir_teoria_caso_victima`).
- No crear ruta procesal (`crear_ruta_procesal_recomendada`).
- No revisión final de coherencia (`revisar_coherencia_estrategica` — calidad).

## Riesgo si se omite
Memoriales y audiencias que persiguen objetivos inalcanzables en la etapa o sin prueba para sostenerlos.
