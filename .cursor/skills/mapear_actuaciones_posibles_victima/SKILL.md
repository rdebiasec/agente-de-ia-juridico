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
- `analista_ruta_procesal_ley906`
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
- `rag_ley906_search`
- `rag_normas_victimas_search`
- `citation_checker`

## Guardrails (g1–g10)
- **g1:** Normas solo desde RAG verificado.
- **g2:** Sin etapa, listar solo categorías genéricas marcadas pendientes.
- **g4:** HITL antes de radicar cualquier actuación.
- **g5:** Actuaciones que expongan a la víctima señalar riesgo revictimización.
- **g9:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No evaluar oportunidad concreta (`evaluar_oportunidad_procesal`).
- No redactar memorial (`redactor_documentos_juridicos_penales`).
- No teoría del caso (`construir_teoria_caso_victima`).

## Riesgo si se omite
Opciones procesales válidas no identificadas o actuaciones improcedentes en la etapa.
