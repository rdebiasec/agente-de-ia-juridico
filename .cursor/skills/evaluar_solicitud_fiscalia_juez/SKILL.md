---
name: evaluar-solicitud-fiscalia-juez
description: Skill operativo penal-victimas: evaluar si una solicitud a Fiscalia o juez es procedente y conveniente. Use when the workflow requires `evaluar_solicitud_fiscalia_juez`.
disable-model-invocation: true
---

# evaluar_solicitud_fiscalia_juez

## Scope
- Category: `Skills de ruta procesal Ley 906`
- Skill ID: `evaluar_solicitud_fiscalia_juez`
- Tier: `operativo`

## Used By Agents
- `analista_ruta_procesal_ley906`
- `redactor_documentos_juridicos_penales`

## Purpose
Evaluar procedencia formal y conveniencia estratégica de una solicitud a Fiscalía o juez de control de garantías / conocimiento.

## Rol en analista_ruta_procesal
Dictamen preliminar antes de derivar a redactor. Incluye oportunidad, requisitos y anexos.

## Rol en redactor
Validar que la solicitud a redactar tuvo evaluación procesal previa.

## Inputs
- Tipo de solicitud propuesta (oficio, memorial, incidente, etc.).
- Autoridad destino (Fiscalía, Juez PGA/JUEZ).
- Etapa procesal y hechos soportados.
- Objetivo de la víctima.

## Outputs
- `procedencia_preliminar`: procedente | improcedente | `[PENDIENTE DE VERIFICAR]`.
- `conveniencia_estrategica` para la víctima.
- `requisitos_y_anexos` necesarios.
- `documento_sugerido` y agente (`redactor_documentos_juridicos_penales` si procede).
- `riesgos` (improcedencia, rechazo, efecto adverso).

## Steps
1. Verificar procedencia formal de la solicitud a Fiscalía o juez.
2. Evaluar conveniencia estratégica para la víctima.
3. Listar requisitos y anexos necesarios.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_ley906_search`
- `rag_expediente_search`
- `citation_checker`

## Guardrails (g1–g10)
- **g1:** Fundamentos normativos verificados en RAG.
- **g3:** Conveniencia estratégica ≠ predicción de resultado favorable.
- **g4:** HITL antes de radicación.
- **g5:** Solicitudes que expongan innecesariamente a la víctima señalar riesgo.
- **g9:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No redactar memorial (`redactar_memorial_penal`).
- No oportunidad genérica (`evaluar_oportunidad_procesal` — usar junto, no duplicar).

## Riesgo si se omite
Solicitud improcedente o inconveniente que perjudica la posición de la víctima.
