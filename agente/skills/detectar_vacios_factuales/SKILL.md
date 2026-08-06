<!-- config-version: 3; checksum: 040b46e25b701cc4 -->
---
name: detectar-vacios-factuales
description: Contrato penal-víctimas: Identificar información factual ausente que impide comprender el caso o sostener una actuación, y priorizar qué aclarar primero. Activar cuando el plan/HITL o el especialista requiera `detectar_vacios_factuales`. No sustituye a `gestionar_faltantes_exp...
disable-model-invocation: true
---

# detectar_vacios_factuales

## Scope
- Category: `Skills de hechos y cronologia`
- Skill ID: `detectar_vacios_factuales`
- Tier: `operativo`

## Used By Agents
- `analista_cronologia_hechos`

## Purpose
Identificar información factual ausente que impide comprender el caso o sostener una actuación, y priorizar qué aclarar primero.

## Rol en analista_cronologia_hechos
Análisis profundo de lagunas tras extracción y matriz hecho-fuente. Alimenta `generar_preguntas_aclaracion`. Prioriza vacíos que afectan cronología y teoría factual.

## Rol en coordinador_caso
**MOVE:** este skill ya no es ownership del POC. El coordinador solo lo dispara vía tool del especialista dueño.

## Fuentes KB
- Relato/expediente del caso (hechos); no inventar fechas ni actuaciones.
- `agente/conocimiento/proceso-penal-906.md` — solo si un evento es actuación procesal (etiquetar etapa con evidencia).
- `agente/conocimiento/normas-clave.md` — no revictimización al ordenar relatos.
- Herramientas: `buscar_en_expediente`, `buscar_en_conocimiento` para anclar; no calificar tipicidad aquí.
## Inputs
- Relato disponible (víctima, abogado, documentos).
- Matriz hecho-fuente preliminar (si existe).
- Tipo de actuación pretendida (denuncia, memorial, audiencia, petición).
- Etapa procesal aparente.

## Outputs
- Lista de vacíos: `descripción`, `impacto` (tipicidad | prueba | oportunidad_procesal | comprensión_caso), `prioridad` (crítica | media | baja).
- Preguntas sugeridas al abogado o víctima (no inductivas).
- Agente sugerido para profundizar (cronología, tipicidad, evidencia).

## Steps
0. Separar confirmado|narrado|inferido|pendiente_verificar; no inventar fechas; no tipificar (otro especialista).
1. Partir de hechos/cronología ya extraídos.
2. Listar huecos críticos (fecha, lugar, actor, medio, daño) para la pretensión.
3. Priorizar vacíos que bloquean tipicidad, prueba o actuación procesal.
4. No rellenar con inferencias presentadas como hechos.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `detectar_vacios_factuales`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `case_state_reader` — no implementada
- `rag_expediente_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto

## Guardrails
- **No inventar:** No suponer hechos para “cerrar” vacíos.
- **Pedir datos faltantes:** Pedir aclaración antes de recomendar actuación que dependa del dato faltante.
- **Separar hecho de inferencia:** Vacíos son lagunas de información, no inferencias presentadas como hechos.
- **Revision humana obligatoria:** Preguntas a víctima requieren revisión del abogado (riesgo revictimización).
- **No revictimizar:** Formular preguntas abiertas; no insinuar culpa o incredibilidad.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- **vs `gestionar_faltantes_expediente`:** este skill cubre vacíos **narrativos o probatorios** (qué pasó, quién, cuándo); `gestionar_faltantes_expediente` cubre **documentos/datos mínimos** para iniciar análisis o redacción.
- No construir cronología (`construir_cronologia_penal`).
- No generar batería completa de preguntas de tipicidad (`generar_preguntas_tipicidad`).

## Riesgo si se omite
Actuaciones o escritos con lagunas fácticas que la Fiscalía o el juez rechazan por falta de soporte.
