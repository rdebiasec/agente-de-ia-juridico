---
name: revisar-coherencia-estrategica
description: Skill estrategico penal-victimas: asegurar coherencia con teoria del caso aprobada. Use when the workflow requires `revisar_coherencia_estrategica`.
disable-model-invocation: true
---

# revisar_coherencia_estrategica

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `revisar_coherencia_estrategica`
- Tier: `estrategico`

## Used By Agents
- `analista_calidad_juridica` (skill primario del agente)

## Purpose
Contrastar salidas (documentos, recomendaciones) con teoría del caso y objetivos aprobados de la víctima.

## Rol en analista_calidad_juridica
Skill primario del agente; primer filtro de coherencia estratégica.

## Inputs
- Documento o recomendación a revisar.
- Teoría del caso y objetivos aprobados (si constan).
- Actuaciones previas del expediente.

## Outputs
- Coherencia: alineado | desalineado | `[PENDIENTE DE VERIFICAR]`.
- Contradicciones detectadas y recomendación de ajuste o escalamiento.

## Steps
1. Contrastar salida con teoría del caso y objetivos aprobados de la víctima.
2. Detectar contradicciones internas o con actuaciones previas.
3. Recomendar alineación o escalamiento estratégico.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `revisar_coherencia_estrategica`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `strategy_consistency_checker` — no implementada
- `case_state_reader` — no implementada

## Guardrails (g1–g10)
- **g4:** No aprobar salida desalineada para uso externo.
- **g8:** Aviso de revisión profesional.

## Handoff
- Complementar con `clasificar_aprobacion_juridica` antes de entrega final.

## Riesgo si se omite
Memoriales o rutas que contradicen la estrategia aprobada del caso.
