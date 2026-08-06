<!-- config-version: 3; checksum: 0ed0e1c5498a2f8f -->
---
name: evaluar-solicitud-fiscalia-juez
description: Contrato penal-víctimas: Evaluar procedencia formal y conveniencia estratégica de una solicitud a Fiscalía o juez de control de garantías / conocimiento. Activar cuando el plan/HITL o el especialista requiera `evaluar_solicitud_fiscalia_juez`. No sustituye a `redactar_memorial...
disable-model-invocation: true
---

# evaluar_solicitud_fiscalia_juez

## Scope
- Category: `Skills de ruta procesal Ley 906`
- Skill ID: `evaluar_solicitud_fiscalia_juez`
- Tier: `operativo`

## Used By Agents
- `analista_ruta_procesal`
- `redactor_documentos_juridicos`

## Purpose
Evaluar procedencia formal y conveniencia estratégica de una solicitud a Fiscalía o juez de control de garantías / conocimiento.

## Rol en analista_ruta_procesal
Dictamen preliminar antes de derivar a redactor. Incluye oportunidad, requisitos y anexos.

## Rol en redactor_documentos_juridicos
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
- `documento_sugerido` y agente (`redactor_documentos_juridicos` si procede).
- `riesgos` (improcedencia, rechazo, efecto adverso).

## Steps
1. Verificar procedencia formal de la solicitud a Fiscalía o juez.
2. Evaluar conveniencia estratégica para la víctima.
3. Listar requisitos y anexos necesarios.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `evaluar_solicitud_fiscalia_juez`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_ley906_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `rag_expediente_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `citation_checker` — no implementada

## Guardrails
- **No inventar:** Fundamentos normativos verificados en RAG.
- **Separar hecho de inferencia:** Conveniencia estratégica ≠ predicción de resultado favorable.
- **Revision humana obligatoria:** HITL antes de radicación.
- **No revictimizar:** Solicitudes que expongan innecesariamente a la víctima señalar riesgo.
- **Oportunidad y terminos Ley 906:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **Aviso de borrador:** Aviso de revisión profesional.


## Fuentes KB (obligatorio consultar antes de citar norma)
- `agente/conocimiento/proceso-penal-906.md` — etapas canónicas y términos (días hábiles).
- `agente/conocimiento/normas-clave.md` — criterio operativo + citación.
- Tools: `leer_playbook_proceso`, `leer_normas_clave`, `buscar_en_conocimiento`.
- Actuación/fecha/artículo no verificado → `[PENDIENTE DE VERIFICAR]`.

## No duplicar
- No redactar memorial (`redactar_memorial_penal`).
- No oportunidad genérica (`evaluar_oportunidad_procesal` — usar junto, no duplicar).

## Riesgo si se omite
Solicitud improcedente o inconveniente que perjudica la posición de la víctima.
