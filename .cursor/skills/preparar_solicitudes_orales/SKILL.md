<!-- config-version: 2; checksum: 3c5ced4bcf34026b -->
---
name: preparar-solicitudes-orales
description: Contrato penal-víctimas: Identificar y formular solicitudes orales procedentes según etapa y tipo de audiencia. Activar cuando el plan/HITL o el especialista requiera `preparar_solicitudes_orales`. No sustituye a `preparar_guion_intervencion_oral`.
disable-model-invocation: true
---

# preparar_solicitudes_orales

## Scope
- Category: `Skills de audiencias`
- Skill ID: `preparar_solicitudes_orales`
- Tier: `operativo`

## Used By Agents
- `analista_audiencias` (uso principal)
- `analista_ruta_procesal` (catálogo procedimental preliminar)

## Purpose
Identificar y formular solicitudes orales procedentes según etapa y tipo de audiencia.

## Rol en analista_ruta_procesal
**Solo catálogo preliminar:** qué solicitudes orales son procedentes en la etapa (sin guion ni táctica de audiencia). Derivar detalle a preparador de audiencias.

## Rol en analista_audiencias
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
Skills = contratos (no function_tools invocables). No existe tool LLM `preparar_solicitudes_orales`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_ley906_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `citation_checker` — no implementada

## Guardrails
- **No inventar:** Fundamentos desde RAG.
- **Revision humana obligatoria:** HITL antes de audiencia.
- **No revictimizar:** Solicitudes que expongan víctima: señalar riesgo.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No guion completo (`preparar_guion_intervencion_oral`).
- No marco de intervención (`analizar_intervencion_victima`).

## Riesgo si se omite
Oportunidades orales perdidas en audiencia por falta de peticiones preparadas.
