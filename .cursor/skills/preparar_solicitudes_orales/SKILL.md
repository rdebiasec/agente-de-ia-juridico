---
name: preparar-solicitudes-orales
description: Skill operativo penal-victimas: formular solicitudes orales posibles segun etapa. Use when the workflow requires `preparar_solicitudes_orales`.
disable-model-invocation: true
---

# preparar_solicitudes_orales

## Scope
- Category: `Skills de audiencias`
- Skill ID: `preparar_solicitudes_orales`
- Tier: `operativo`

## Used By Agents
- `preparador_estrategico_audiencias_penales` (uso principal)
- `analista_ruta_procesal_ley906` (catálogo procedimental preliminar)

## Purpose
Identificar y formular solicitudes orales procedentes según etapa y tipo de audiencia.

## Rol en analista_ruta_procesal
**Solo catálogo preliminar:** qué solicitudes orales son procedentes en la etapa (sin guion ni táctica de audiencia). Derivar detalle a preparador de audiencias.

## Rol en preparador_audiencias
Formulación completa con fundamento, prioridad y dependencias probatorias para estrados.

## Inputs
- Etapa procesal y tipo de audiencia.
- Objetivo de intervención (`analizar_intervencion_victima`).
- Hechos y prueba disponibles.

## Outputs
- Lista: `solicitud`, `fundamento_normativo`, `hecho_soporte`, `prioridad`, `riesgo`.
- Etiqueta en ruta 906: `PRELIMINAR — DETALLE EN PREPARADOR AUDIENCIAS`.

## Steps
1. Identificar solicitudes orales procedentes según etapa y tipo de audiencia.
2. Formular peticiones con fundamento normativo preliminar.
3. Ordenar por prioridad y dependencias probatorias.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_ley906_search`
- `citation_checker`

## Guardrails (g1–g10)
- **g1:** Fundamentos desde RAG.
- **g4:** HITL antes de audiencia.
- **g5:** Solicitudes que expongan víctima: señalar riesgo.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No guion completo (`preparar_guion_intervencion_oral`).
- No marco de intervención (`analizar_intervencion_victima`).

## Riesgo si se omite
Oportunidades orales perdidas en audiencia por falta de peticiones preparadas.
