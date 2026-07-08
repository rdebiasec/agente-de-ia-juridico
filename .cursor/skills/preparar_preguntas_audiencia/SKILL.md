---
name: preparar-preguntas-audiencia
description: Skill operativo penal-victimas: sugerir preguntas para victima, testigos o peritos en audiencia. Use when the workflow requires `preparar_preguntas_audiencia`.
disable-model-invocation: true
---

# preparar_preguntas_audiencia

## Scope
- Category: `Skills de audiencias`
- Skill ID: `preparar_preguntas_audiencia`
- Tier: `operativo`

## Used By Agents
- `preparador_estrategico_audiencias_penales` (skill primario del agente)

## Purpose
Redactar preguntas neutrales y no inductivas para víctima, testigos o peritos, alineadas a matriz hecho-prueba y objetivo de audiencia.


## Rol en preparador_audiencias
Guion probatorio oral alineado con hechos y teoría del caso.
## Inputs
- Objetivo de audiencia (`identificar_objetivo_audiencia`).
- Matriz hecho-prueba y cronología verificada.
- Tipo de audiencia y etapa Ley 906.

## Outputs
- Preguntas por bloque: `destinatario`, `objetivo_probatorio`, `pregunta`, `riesgo`, `alternativa_segura`.
- Orden lógico; preguntas de alto riesgo señaladas.
- Etiqueta: `REVISAR CON ABOGADO — ESPECIALMENTE PREGUNTAS A VÍCTIMA`.

## Steps
1. Definir objetivo probatorio de cada bloque de preguntas.
2. Seleccionar destinatario (víctima, testigo, perito) según matriz hecho-prueba.
3. Redactar preguntas neutrales, no inductivas y en orden lógico.
4. Revisar cada pregunta con criterio de no revictimización.
5. Señalar preguntas de alto riesgo y alternativas más seguras.
6. Alinear preguntas con solicitudes orales previstas en la audiencia.
7. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_expediente_search`

## Guardrails (g1–g10)
- **g4:** HITL obligatorio antes de audiencia.
- **g5:** No revictimizar; evitar preguntas sobre vida íntima no pertinente.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No guion completo (`preparar_guion_intervencion_oral`).
- No preguntas genéricas de aclaración (`generar_preguntas_aclaracion`).

## Riesgo si se omite
Audiencia improvisada con preguntas inductivas o revictimizantes.
