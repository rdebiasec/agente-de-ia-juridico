---
name: verificar-jurisprudencia
description: Skill atomico penal-victimas: revisar sentencias, radicados, fechas y organos judiciales. Use when the workflow requires `verificar_jurisprudencia`.
disable-model-invocation: true
---

# verificar_jurisprudencia

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `verificar_jurisprudencia`
- Tier: `operativo`

## Used By Agents
- `analista_calidad_juridica`
- `redactor_documentos_juridicos_penales`

## Purpose
Verificar que sentencias citadas existan en RAG y sean pertinentes al argumento.

## Rol en redactor_documentos_juridicos_penales
Control en borrador antes de calidad.

## Rol en analista_calidad_juridica
Verificación final.

## Inputs
- Citas jurisprudenciales en el documento.
- Tema jurídico del argumento donde se citan.

## Outputs
- Por sentencia: `referencia`, `localizada` (sí | no | pendiente), `pertinencia`, `extracto_relevante` (si aplica).
- Etiqueta: `VERIFICACIÓN JURISPRUDENCIAL`.

## Steps
1. Buscar cada sentencia citada en RAG jurisprudencial.
2. Evaluar pertinencia al argumento del caso.
3. Marcar citas no localizadas o irrelevantes.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_jurisprudencia_search`
- `citation_checker`

## Guardrails (g1–g10)
- **g1:** No inventar sentencias ni extractos.
- **g4:** HITL obligatorio antes de usar la salida en memorial, estrategia o comunicación con cliente.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No citas normativas (`verificar_citas_normativas`).
- No alucinaciones globales (`detectar_alucinaciones_legales`).

## Riesgo si se omite
Argumento sustentado en jurisprudencia inventada o mal aplicada.
