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
- `strategy_consistency_checker`
- `case_state_reader`

## Guardrails (g1–g10)
- **g4:** No aprobar salida desalineada para uso externo.
- **g8:** Aviso de revisión profesional.

## Handoff
- Complementar con `clasificar_aprobacion_juridica` antes de entrega final.

## Riesgo si se omite
Memoriales o rutas que contradicen la estrategia aprobada del caso.
