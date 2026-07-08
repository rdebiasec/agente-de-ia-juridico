---
name: detectar-vacios-factuales
description: Skill operativo penal-victimas: identificar lo que falta para comprender o probar el caso. Use when the workflow requires `detectar_vacios_factuales`.
disable-model-invocation: true
---

# detectar_vacios_factuales

## Scope
- Category: `Skills de hechos y cronologia`
- Skill ID: `detectar_vacios_factuales`
- Tier: `operativo`

## Used By Agents
- `analista_cronologia_hechos_penales`
- `coordinador_expediente_penal`

## Purpose
Identificar información factual ausente que impide comprender el caso o sostener una actuación, y priorizar qué aclarar primero.

## Rol en analista_cronologia
Análisis profundo de lagunas tras extracción y matriz hecho-fuente. Alimenta `generar_preguntas_aclaracion`. Prioriza vacíos que afectan cronología y teoría factual.

## Rol en coordinador
Detección rápida de vacíos en el relato o expediente al recibir el caso. No sustituye el análisis cronológico profundo de este agente.

## Inputs
- Relato disponible (víctima, abogado, documentos).
- Matriz hecho-fuente preliminar (si existe).
- Tipo de actuación pretendida (denuncia, memorial, audiencia, tutela preliminar).
- Etapa procesal aparente.

## Outputs
- Lista de vacíos: `descripción`, `impacto` (tipicidad | prueba | oportunidad_procesal | comprensión_caso), `prioridad` (crítica | media | baja).
- Preguntas sugeridas al abogado o víctima (no inductivas).
- Agente sugerido para profundizar (cronología, tipicidad, evidencia).

## Steps
1. Identificar información faltante para comprender el caso o sostener actuación.
2. Priorizar vacíos por impacto en tipicidad, prueba o oportunidad procesal.
3. Formular solicitud de datos al abogado o cliente.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `case_state_reader`
- `rag_expediente_search`

## Guardrails (g1–g10)
- **g1:** No suponer hechos para “cerrar” vacíos.
- **g2:** Pedir aclaración antes de recomendar actuación que dependa del dato faltante.
- **g3:** Vacíos son lagunas de información, no inferencias presentadas como hechos.
- **g4:** Preguntas a víctima requieren revisión del abogado (riesgo revictimización).
- **g5:** Formular preguntas abiertas; no insinuar culpa o incredibilidad.
- **g8:** Aviso de revisión profesional.

## No duplicar
- **vs `gestionar_faltantes_expediente`:** este skill cubre vacíos **narrativos o probatorios** (qué pasó, quién, cuándo); `gestionar_faltantes_expediente` cubre **documentos/datos mínimos** para iniciar análisis o redacción.
- No construir cronología (`construir_cronologia_penal`).
- No generar batería completa de preguntas de tipicidad (`generar_preguntas_tipicidad`).

## Riesgo si se omite
Actuaciones o escritos con lagunas fácticas que la Fiscalía o el juez rechazan por falta de soporte.
