---
name: extraer-hechos-relevantes
description: Skill operativo penal-victimas: extraer hechos relevantes de documentos, relatos, audios o comunicaciones. Use when the workflow requires `extraer_hechos_relevantes`.
disable-model-invocation: true
---

# extraer_hechos_relevantes

## Scope
- Category: `Skills de hechos y cronologia`
- Skill ID: `extraer_hechos_relevantes`
- Tier: `operativo`

## Used By Agents
- `analista_cronologia_hechos_penales` (primer skill del pipeline factual)
- `redactor_documentos_juridicos_penales`
- `gestor_evidencia_y_soporte_probatorio`

## Purpose
Extraer hechos materiales de documentos, relatos, audios o mensajes, con referencia de fuente, filtrando opiniones e inferencias.

## Rol en analista_cronologia
Punto de entrada del agente tras triage del coordinador. Alimenta matriz hecho-fuente, actores y cronología.

## Inputs
- Documentos PDF/imagen, textos, transcripciones de audio o mensajes del turno/expediente.
- Objetivo del análisis (comprensión del caso, memorial, audiencia).
- Tipos de hecho relevantes según consulta (conducta, lugar, fecha, daño, participantes).

## Outputs
- Lista de hechos: `descripción`, `fuente`, `fecha_si_consta`, `actor_si_consta`, `tipo_fuente`, `nivel_soporte`.
- Opiniones e inferencias filtradas (listadas aparte, no como hechos).
- Elementos no legibles o no procesables marcados `[PENDIENTE DE VERIFICAR]`.

## Steps
1. Procesar documentos, relatos, audios o mensajes del expediente.
2. Extraer hechos materiales con referencia de fuente.
3. Filtrar opiniones e inferencias no soportadas.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `document_parser_extract_text`
- `ocr_extract_text`
- `transcribe_audio`
- `rag_expediente_search`

## Guardrails (g1–g10)
- **g1:** No completar lagunas del relato con hechos inventados.
- **g2:** Audio/documento ilegible → pedir nueva copia o transcripción humana.
- **g3:** Separar hecho material de opinión del declarante o de la IA.
- **g5:** En relatos de víctima, extraer sin juicio de credibilidad.
- **g6:** No reproducir datos sensibles innecesarios en la lista de hechos.
- **g4:** HITL obligatorio antes de usar la salida en memorial, estrategia o comunicación con cliente.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No clasificar nivel de soporte en profundidad (`crear_matriz_hecho_fuente`).
- No ordenar cronología (`construir_cronologia_penal`).
- No inventariar evidencia física/digital (`inventariar_evidencia`).

## Riesgo si se omite
Todo el análisis posterior se construye sobre relato no depurado o con inferencias disfrazadas de hechos.
