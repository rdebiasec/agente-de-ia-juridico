---
name: detectar-riesgos-procesales
description: Skill estrategico penal-victimas: detectar riesgos de oportunidad, legitimacion, competencia, improcedencia o perdida de derechos. Use when the workflow requires `detectar_riesgos_procesales`.
disable-model-invocation: true
---

# detectar_riesgos_procesales

## Scope
- Category: `Skills de ruta procesal Ley 906`
- Skill ID: `detectar_riesgos_procesales`
- Tier: `estrategico`

## Used By Agents
- `analista_ruta_procesal_ley906`
- `analista_calidad_juridica`

## Purpose
Identificar y priorizar riesgos procesales que puedan causar improcedencia, pérdida de derechos o extemporaneidad.

## Rol en analista_ruta_procesal
Ejecutar tras identificar etapa y antes de `crear_ruta_procesal_recomendada`. Complementa `evaluar_oportunidad_procesal` (caso por caso).

## Inputs
- Etapa procesal y actuaciones del expediente.
- Legitimación de la víctima/apoderado (poder, calidad).
- Actuaciones propuestas o pendientes.
- Términos próximos.

## Outputs
- Registro: `riesgo`, `tipo` (oportunidad | legitimación | competencia | improcedencia | preclusión), `severidad`, `accion_preventiva`, `responsable`, `plazo`.
- Riesgos críticos destacados para decisión inmediata.

## Steps
1. Revisar oportunidad, legitimación, competencia e improcedencia.
2. Documentar riesgos de pérdida de derechos o extemporaneidad.
3. Priorizar riesgos críticos para decisión inmediata.
4. Recomendar actuación inmediata para riesgos críticos extemporáneos.
5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_ley906_search`
- `case_state_reader`

## Guardrails (g1–g10)
- **g1:** No inventar vicios procesales sin actuación de soporte.
- **g4:** Riesgos críticos requieren escalamiento al abogado titular.
- **g9:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No evaluar una sola actuación (`evaluar_oportunidad_procesal`).
- No atipicidad penal (`detectar_riesgos_atipicidad`).
- No tutela (`detectar_riesgo_improcedencia_tutela`).

## Riesgo si se omite
Pérdida silenciosa de recursos o derechos de la víctima en el proceso.
