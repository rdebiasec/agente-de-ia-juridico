---
name: detectar-riesgos-audiencia
description: Skill atomico penal-victimas: detectar riesgos de intervencion, oportunidad, revelacion de estrategia o revictimizacion. Use when the workflow requires `detectar_riesgos_audiencia`.
disable-model-invocation: true
---

# detectar_riesgos_audiencia

## Scope
- Category: `Skills de audiencias`
- Skill ID: `detectar_riesgos_audiencia`
- Tier: `operativo`

## Used By Agents
- `preparador_estrategico_audiencias_penales`
- `analista_calidad_juridica`

## Purpose
Identificar riesgos tácticos y procesales específicos de una audiencia programada.

## Rol en preparador_estrategico_audiencias_penales
Antecede simulación y guion oral.

## Rol en analista_calidad_juridica
Segunda opinión en audiencias de alto riesgo.

## Inputs
- Tipo de audiencia, postura de Fiscalía/defensa (hipótesis).
- Debilidades probatorias y objetivo de audiencia.
- Antecedentes de audiencias previas en el caso.

## Outputs
- `riesgos`: descripción | probabilidad | impacto | mitigación sugerida.
- `riesgo_global`: alto | medio | bajo.
- Etiqueta: `RIESGOS AUDIENCIA PRELIMINARES`.

## Steps
1. Listar riesgos procesales y tácticos de la audiencia concreta.
2. Evaluar probabilidad e impacto en objetivos de la víctima.
3. Proponer mitigaciones (aplazamiento, solicitud oral, prueba).
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `detectar_riesgos_audiencia`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_expediente_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `rag_ley906_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto

## Guardrails (g1–g10)
- **g3:** Riesgos son hipótesis, no predicciones certas.
- **g4:** HITL obligatorio antes de usar en audiencia o comunicar a terceros.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No simular escenarios (`simular_escenarios_audiencia`).
- No contraargumentos detallados (`preparar_contraargumentos`).

## Riesgo si se omite
Audiencia sin preparación para imprevistos que perjudican a la víctima.
