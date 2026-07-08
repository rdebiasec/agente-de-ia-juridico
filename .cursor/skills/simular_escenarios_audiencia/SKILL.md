---
name: simular-escenarios-audiencia
description: Skill estrategico penal-victimas: plantear escenarios probables y preparacion del abogado. Use when the workflow requires `simular_escenarios_audiencia`.
disable-model-invocation: true
---

# simular_escenarios_audiencia

## Scope
- Category: `Skills de audiencias`
- Skill ID: `simular_escenarios_audiencia`
- Tier: `estrategico`

## Used By Agents
- `preparador_estrategico_audiencias_penales`

## Purpose
Anticipar escenarios favorable, intermedio y adverso en audiencia y preparar respuesta táctica del abogado.

## Rol en preparador_estrategico_audiencias_penales
Ejecutar tras `identificar_objetivo_audiencia` y antes o junto al guion oral.

## Inputs
- Objetivo de audiencia y teoría del caso.
- Contraargumentos anticipados (`preparar_contraargumentos`, si existe).
- Fortalezas y debilidades probatorias preliminares.
- Postura probable de Fiscalía y defensa (hipótesis, no certezas).

## Outputs
- Tres escenarios: `favorable`, `intermedio`, `adverso` con descripción breve.
- `respuesta_tactica` por escenario (qué decir, qué pedir, qué evitar).
- `senales_cambio_escenario` durante la audiencia.
- Etiqueta: `SIMULACIÓN PRELIMINAR — NO PREDICE DECISIÓN DEL JUEZ`.

## Steps
1. Plantear escenarios favorable, intermedio y adverso probables.
2. Definir respuesta táctica para cada escenario.
3. Listar señales en audiencia que indiquen cambio de escenario.
4. Cruzar escenarios adverso con plan de contingencia (aplazamiento, solicitud oral, etc.).
5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_expediente_search`

## Guardrails (g1–g10)
- **g1:** No predecir decisiones del juez ni declaraciones de testigos no documentadas.
- **g3:** Escenarios son hipótesis tácticas, no hechos.
- **g4:** HITL; simulación para preparación del abogado, no para la víctima sin filtro.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No guion literal (`preparar_guion_intervencion_oral`).
- No contraargumentos detallados (`preparar_contraargumentos`).

## Riesgo si se omite
Improvisación ante imprevistos de Fiscalía o defensa; pérdida de oportunidad procesal en audiencia.
