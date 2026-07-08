---
name: identificar-objetivo-audiencia
description: Skill estrategico penal-victimas: definir objetivo juridico y tactico de la audiencia para la victima. Use when the workflow requires `identificar_objetivo_audiencia`.
disable-model-invocation: true
---

# identificar_objetivo_audiencia

## Scope
- Category: `Skills de audiencias`
- Skill ID: `identificar_objetivo_audiencia`
- Tier: `estrategico`

## Used By Agents
- `preparador_estrategico_audiencias_penales` (primer skill del flujo de audiencia)

## Purpose
Definir qué debe lograr la víctima en la audiencia: objetivo jurídico (Ley 906) y táctico (postura procesal).

## Rol en preparador_estrategico_audiencias_penales
Antecede guion, preguntas, solicitudes orales y simulación de escenarios.

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
1. Precisar tipo de audiencia y marco normativo Ley 906 aplicable.
2. Definir objetivo jurídico y táctico para la representación de la víctima.
3. Alinear objetivo con teoría del caso y prueba disponible.
4. Documentar peticiones orientativas y riesgos si no se logra el objetivo.
5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_ley906_search`
- `calendar_event_reader`

## Guardrails (g1–g10)
- **g1:** No inventar tipo de audiencia ni competencias.
- **g3:** Objetivo táctico separado de hechos probados.
- **g4:** HITL antes de audiencia.
- **g8:** Aviso de revisión profesional.

## Handoff
- Siguiente: `preparar_preguntas_audiencia`, `preparar_guion_intervencion_oral`, `preparar_solicitudes_orales`.

## Riesgo si se omite
Audiencia sin norte: intervenciones dispersas que no protegen los intereses de la víctima.
