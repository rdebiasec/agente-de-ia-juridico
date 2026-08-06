<!-- config-version: 3; checksum: ab40b6337fca7493 -->
---
name: revisar-coherencia-estrategica
description: Contrato penal-víctimas: Contrastar salidas (documentos, recomendaciones) con teoría del caso y objetivos aprobados de la víctima. Activar cuando el plan/HITL o el especialista requiera `revisar_coherencia_estrategica`. No sustituye a `clasificar_aprobacion_juridica`.
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
1. Cruzar teoría del caso, ruta y prueba propuesta.
2. Señalar inconsistencias estratégicas y riesgos.
3. No dictaminar aprobación final ni solo cazar citas falsas.

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

## Guardrails
- **Revision humana obligatoria:** No aprobar salida desalineada para uso externo.
- **Aviso de borrador:** Aviso de revisión profesional.

## Handoff
- Complementar con `clasificar_aprobacion_juridica` antes de entrega final.

## No duplicar
- No clasificar aprobación final (`clasificar_aprobacion_juridica`).
- No detectar solo alucinaciones (`detectar_alucinaciones_legales`).
- No reescribir el memorial completo (`redactar_memorial_penal`).

## Riesgo si se omite
Memoriales o rutas que contradicen la estrategia aprobada del caso.
