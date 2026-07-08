---
name: detectar-riesgo-revictimizacion
description: Skill atomico penal-victimas: identificar lenguaje, preguntas, acciones o estrategias que puedan revictimizar. Use when the workflow requires `detectar_riesgo_revictimizacion`.
disable-model-invocation: true
---

# detectar_riesgo_revictimizacion

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `detectar_riesgo_revictimizacion`
- Tier: `operativo`

## Used By Agents
- `analista_representacion_victimas`
- `analista_calidad_juridica`

## Purpose
Alertar tempranamente sobre riesgo de revictimización en materiales o estrategia propuesta.

## Rol en analista_representacion_victimas
Triaje rápido en teoría del caso y comunicación con víctima.

## Rol en analista_calidad_juridica
Alerta antes de revisión profunda (`controlar_no_revictimizacion`).

## Inputs
- Texto o estrategia a evaluar (preguntas, teoría, resumen).
- Tipo de delito y contexto (si consta).

## Outputs
- `nivel_riesgo`: alto | medio | bajo | no_detectado.
- `indicadores` detectados (breve lista).
- `derivar_a`: `controlar_no_revictimizacion` si riesgo medio/alto.

## Steps
1. Escanear lenguaje, preguntas y exposición de datos sensibles.
2. Clasificar nivel de riesgo de revictimización.
3. Recomendar revisión profunda o reformulación inmediata.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `revictimization_risk_checker`

## Guardrails (g1–g10)
- **g5:** Priorizar dignidad y derechos de la víctima.
- **g4:** HITL obligatorio antes de incorporar hallazgos a escritos o comunicación externa.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No revisión exhaustiva (`controlar_no_revictimizacion`).
- No enfoque diferencial (`analizar_enfoque_diferencial`).

## Riesgo si se omite
Material dañino llega a la víctima o a audiencia sin filtro previo.
