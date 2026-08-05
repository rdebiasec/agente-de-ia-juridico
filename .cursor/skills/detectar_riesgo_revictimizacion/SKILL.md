<!-- config-version: 2; checksum: a595263c93bfa277 -->
---
name: detectar-riesgo-revictimizacion
description: Contrato penal-víctimas: Alertar tempranamente sobre riesgo de revictimización en materiales o estrategia propuesta. Activar cuando el plan/HITL o el especialista requiera `detectar_riesgo_revictimizacion`. No sustituye a `controlar_no_revictimizacion`.
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
1. Identificar actos/lenguaje/prácticas que puedan revictimizar.
2. Clasificar riesgo y proponer mitigaciones al Gerente.
3. No culpabilizar a la víctima; proteger datos sensibles (/).

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `detectar_riesgo_revictimizacion`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `revictimization_risk_checker` — no implementada

## Guardrails
- **No revictimizar:** Priorizar dignidad y derechos de la víctima.
- **Revision humana obligatoria:** HITL obligatorio antes de incorporar hallazgos a escritos o comunicación externa.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No revisión exhaustiva (`controlar_no_revictimizacion`).
- No enfoque diferencial (`analizar_enfoque_diferencial`).

## Riesgo si se omite
Material dañino llega a la víctima o a audiencia sin filtro previo.
