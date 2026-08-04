<!-- config-version: 2; checksum: 388fef5b6b3e4763 -->
---
name: mapear-actuaciones-posibles-victima
description: Skill operativo penal-victimas: indicar que puede hacer la representacion de victimas segun etapa Ley 906. Use when the workflow requires `mapear_actuaciones_posibles_victima`.
disable-model-invocation: true
---

# mapear_actuaciones_posibles_victima

## Scope
- Category: `Skills de ruta procesal Ley 906`
- Skill ID: `mapear_actuaciones_posibles_victima`
- Tier: `operativo`

## Used By Agents
- `analista_ruta_procesal`
- `analista_representacion_victimas`

## Purpose
Listar actuaciones que la representación de víctimas puede promover en la etapa actual, con requisitos y efectos esperados.

## Rol en analista_ruta_procesal
Ejecutar inmediatamente tras `identificar_etapa_procesal_ley906`. Catálogo de opciones procesales antes de evaluar oportunidad de cada una.

## Rol en analista_representacion_victimas
Alinear actuaciones con intereses y teoría del caso de la víctima.

## Inputs
- Etapa Ley 906 confirmada o `[PENDIENTE DE VERIFICAR]`.
- Objetivos preliminares de la víctima.
- Actuaciones ya realizadas en el expediente.
- Norma Ley 906 y derechos de víctimas (RAG).

## Outputs
- Lista: `actuacion`, `autoridad_destino`, `requisitos`, `oportunidad_preliminar`, `efecto_esperado`, `riesgo`, `norma_soporte`.
- Priorización según intereses de la víctima.
- Actuaciones no procedentes en etapa marcadas con motivo.

## Steps
1. Listar actuaciones que la representación de víctimas puede promover en la etapa actual.
2. Indicar requisitos, oportunidad y efectos esperados de cada una.
3. Priorizar según intereses de la víctima.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `mapear_actuaciones_posibles_victima`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_ley906_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `rag_normas_victimas_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `citation_checker` — no implementada

## Guardrails (g1–g10)
- **g1:** Normas solo desde RAG verificado.
- **g2:** Sin etapa, listar solo categorías genéricas marcadas pendientes.
- **g4:** HITL antes de radicar cualquier actuación.
- **g5:** Actuaciones que expongan a la víctima señalar riesgo revictimización.
- **g9:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No evaluar oportunidad concreta (`evaluar_oportunidad_procesal`).
- No redactar memorial (`redactor_documentos_juridicos`).
- No teoría del caso (`construir_teoria_caso_victima`).

## Riesgo si se omite
Opciones procesales válidas no identificadas o actuaciones improcedentes en la etapa.
