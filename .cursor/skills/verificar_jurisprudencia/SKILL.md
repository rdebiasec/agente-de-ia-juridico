<!-- config-version: 4; checksum: e8df58dfca68a942 -->
---
name: verificar-jurisprudencia
description: Contrato penal-víctimas: Verificar que sentencias citadas existan en RAG y sean pertinentes al argumento. Activar cuando el plan/HITL o el especialista requiera `verificar_jurisprudencia`. No sustituye a `verificar_citas_normativas`.
disable-model-invocation: true
---

# verificar_jurisprudencia

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `verificar_jurisprudencia`
- Tier: `operativo`

## Used By Agents
- `analista_calidad_juridica`
- `redactor_documentos_juridicos`

## Purpose
Verificar que sentencias citadas existan en RAG y sean pertinentes al argumento.

## Rol en redactor_documentos_juridicos
Control en borrador antes de calidad.

## Rol en analista_calidad_juridica
Verificación final.

## Fuentes KB
- `agente/conocimiento/normas-clave.md` — no inventar sentencias ni extractos; checklist citas.
- `agente/conocimiento/proceso-penal-906.md` — checklist calidad; pertinencia al argumento.
- Tools reales: `buscar_en_conocimiento`, `buscar_en_expediente` (no hay `rag_jurisprudencia_search` invocable).
- Sentencia no localizada → `localizada=pendiente` / `[PENDIENTE DE VERIFICAR]`.

## Inputs
- Citas jurisprudenciales en el documento.
- Tema jurídico del argumento donde se citan.

## Outputs
- Por sentencia: `referencia`, `localizada` (sí | no | pendiente), `pertinencia`, `extracto_relevante` (si aplica).
- Etiqueta: `VERIFICACIÓN JURISPRUDENCIAL`.

## Steps
0. Anclar cada sentencia a Fuentes KB/RAG; no inventar extractos ni existencia.
1. Buscar cada sentencia citada en RAG jurisprudencial.
2. Evaluar pertinencia al argumento del caso.
3. Marcar citas no localizadas o irrelevantes.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `verificar_jurisprudencia`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_jurisprudencia_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `citation_checker` — no implementada

## Guardrails
- **No inventar:** No inventar sentencias ni extractos.
- **Revision humana obligatoria:** HITL obligatorio antes de usar la salida en memorial, estrategia o comunicación con cliente.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No citas normativas (`verificar_citas_normativas`).
- No alucinaciones globales (`detectar_alucinaciones_legales`).

## Riesgo si se omite
Argumento sustentado en jurisprudencia inventada o mal aplicada.
