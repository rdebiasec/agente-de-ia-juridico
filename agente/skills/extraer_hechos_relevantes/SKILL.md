<!-- config-version: 3; checksum: 1235b1bd44352ea9 -->
---
name: extraer-hechos-relevantes
description: Contrato penal-víctimas: Extraer hechos materiales de documentos, relatos, audios o mensajes, con referencia de fuente, filtrando opiniones e inferencias. Activar cuando el plan/HITL o el especialista requiera `extraer_hechos_relevantes`. No sustituye a `crear_matriz_hecho_fue...
disable-model-invocation: true
---

# extraer_hechos_relevantes

## Scope
- Category: `Skills de hechos y cronologia`
- Skill ID: `extraer_hechos_relevantes`
- Tier: `operativo`

## Used By Agents
- `analista_cronologia_hechos` (primer skill del pipeline factual)
- `redactor_documentos_juridicos`
- `analista_evidencia`

## Purpose
Extraer hechos materiales de documentos, relatos, audios o mensajes, con referencia de fuente, filtrando opiniones e inferencias.

## Rol en analista_cronologia_hechos
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
1. Procesar documentos, relatos, audios o mensajes del expediente/turno.
2. Extraer hechos materiales con referencia de fuente (no opiniones).
3. Separar opiniones e inferencias en lista aparte.
4. Marcar ilegible/no procesable como `[PENDIENTE DE VERIFICAR]`; no inventar lagunas.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `extraer_hechos_relevantes`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `document_parser_extract_text` — no implementada
- `ocr_extract_text` — no implementada
- `transcribe_audio` — no implementada
- `rag_expediente_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto

## Guardrails
- **No inventar:** No completar lagunas del relato con hechos inventados.
- **Pedir datos faltantes:** Audio/documento ilegible → pedir nueva copia o transcripción humana.
- **Separar hecho de inferencia:** Separar hecho material de opinión del declarante o de la IA.
- **No revictimizar:** En relatos de víctima, extraer sin juicio de credibilidad.
- **Confidencialidad:** No reproducir datos sensibles innecesarios en la lista de hechos.
- **Revision humana obligatoria:** HITL obligatorio antes de usar la salida en memorial, estrategia o comunicación con cliente.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No clasificar nivel de soporte en profundidad (`crear_matriz_hecho_fuente`).
- No ordenar cronología (`construir_cronologia_penal`).
- No inventariar evidencia física/digital (`inventariar_evidencia`).

## Riesgo si se omite
Todo el análisis posterior se construye sobre relato no depurado o con inferencias disfrazadas de hechos.
