<!-- config-version: 4; checksum: 44d5afb1d6d7a6a1 -->
---
name: identificar-objetivo-audiencia
description: Contrato penal-víctimas: Definir qué debe lograr la víctima en la audiencia: objetivo jurídico (Ley 906) y táctico (postura procesal). Activar cuando el plan/HITL o el especialista requiera `identificar_objetivo_audiencia`. No sustituye a `preparar_guion_intervencion_oral`.
disable-model-invocation: true
---

# identificar_objetivo_audiencia

## Scope
- Category: `Skills de audiencias`
- Skill ID: `identificar_objetivo_audiencia`
- Tier: `estrategico`

## Used By Agents
- `analista_audiencias` (primer skill del flujo de audiencia)

## Purpose
Definir qué debe lograr la víctima en la audiencia: objetivo jurídico (Ley 906) y táctico (postura procesal).

## Rol en analista_audiencias
Antecede guion, preguntas, solicitudes orales y simulación de escenarios.

## Fuentes KB
- `agente/conocimiento/proceso-penal-906.md` — etapas, tipos de audiencia, checklist preparación O6.
- `agente/conocimiento/normas-clave.md` — participación/protección víctima; sin inventar facultades.
- Tools reales: `leer_playbook_proceso`, `leer_normas_clave`, `buscar_en_conocimiento`, `buscar_en_expediente`.

## Inputs
- Tipo de audiencia programada (legalización, formulación, juicio, etc.).
- Etapa procesal y actuación que se discute.
- Teoría del caso y matriz hecho-prueba (preliminar).
- Peticiones o pretensiones ya planteadas en expediente.

## Outputs
- `tipo_audiencia` y norma Ley 906 habilitante.
- `objetivo_juridico`: qué se pide al juez/Fiscalía según la ley.
- `objetivo_tactico`: postura procesal (presionar recaudo, oponerse, participar, etc.).
- `peticiones_orientativas` alineadas al objetivo.
- `coherencia_teoria_caso`: alineado | parcial | `[PENDIENTE DE VERIFICAR]`.
- Etiqueta: `OBJETIVO AUDIENCIA — VALIDAR CON ABOGADO`.

## Steps
0. Anclar tipo de audiencia/etapa/objetivo a Fuentes KB; sin soporte → `[PENDIENTE DE VERIFICAR]`.
1. Identificar tipo de audiencia y pretensión de la víctima.
2. Listar 1–5 objetivos medibles para la intervención.
3. No redactar guion ni checklist completo aquí.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `identificar_objetivo_audiencia`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_ley906_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `calendar_event_reader` — no implementada

## Guardrails
- **No inventar:** No inventar tipo de audiencia ni competencias.
- **Separar hecho de inferencia:** Objetivo táctico separado de hechos probados.
- **Revision humana obligatoria:** HITL antes de audiencia.
- **Aviso de borrador:** Aviso de revisión profesional.

## Handoff
- Siguiente: `preparar_preguntas_audiencia`, `preparar_guion_intervencion_oral`, `preparar_solicitudes_orales`.

## No duplicar
- No redactar guion oral completo (`preparar_guion_intervencion_oral`).
- No listar preguntas detalladas (`preparar_preguntas_audiencia`).
- No simular escenarios (`simular_escenarios_audiencia`).

## Riesgo si se omite
Audiencia sin norte: intervenciones dispersas que no protegen los intereses de la víctima.
