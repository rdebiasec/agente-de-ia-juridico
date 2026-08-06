<!-- config-version: 4; checksum: aa0e975d53b00be6 -->
---
name: detectar-riesgos-procesales
description: Contrato penal-víctimas: Identificar y priorizar riesgos procesales que puedan causar improcedencia, pérdida de derechos o extemporaneidad. Activar cuando el plan/HITL o el especialista requiera `detectar_riesgos_procesales`. No sustituye a `evaluar_oportunidad_procesal`.
disable-model-invocation: true
---

# detectar_riesgos_procesales

## Scope
- Category: `Skills de ruta procesal Ley 906`
- Skill ID: `detectar_riesgos_procesales`
- Tier: `estrategico`

## Used By Agents
- `analista_ruta_procesal`
- `analista_calidad_juridica`

## Purpose
Identificar y priorizar riesgos procesales que puedan causar improcedencia, pérdida de derechos o extemporaneidad.

## Rol en analista_ruta_procesal
Ejecutar tras identificar etapa y antes de `crear_ruta_procesal_recomendada`. Complementa `evaluar_oportunidad_procesal` (caso por caso).

## Fuentes KB
- `agente/conocimiento/proceso-penal-906.md` — etapas, enum `etapa_ley906`, términos (días hábiles).
- `agente/conocimiento/normas-clave.md` — criterio operativo y derechos de víctima.
- Herramientas: `leer_playbook_proceso(penal)`, `leer_normas_clave`, `buscar_en_conocimiento` antes de afirmar etapa/plazos.
## Inputs
- Etapa procesal y actuaciones del expediente.
- Legitimación de la víctima/apoderado (poder, calidad).
- Actuaciones propuestas o pendientes.
- Términos próximos.

## Outputs
- Registro: `riesgo`, `tipo` (oportunidad | legitimación | competencia | improcedencia | preclusión), `severidad`, `accion_preventiva`, `responsable`, `plazo`.
- Riesgos críticos destacados para decisión inmediata.

## Steps
0. Anclar etapa/ruta a `proceso-penal-906.md` (enum `etapa_ley906`); términos en días hábiles; sin `fecha_base` no certificar plazos.
1. Revisar oportunidad, legitimación, competencia e improcedencia.
2. Documentar riesgos de pérdida de derechos o extemporaneidad.
3. Priorizar riesgos críticos para decisión inmediata.
4. Recomendar actuación inmediata para riesgos críticos extemporáneos.
5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `detectar_riesgos_procesales`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_ley906_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `case_state_reader` — no implementada

## Guardrails
- **No inventar:** No inventar vicios procesales sin actuación de soporte.
- **Revision humana obligatoria:** Riesgos críticos requieren escalamiento al abogado titular.
- **Oportunidad y terminos Ley 906:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No evaluar una sola actuación (`evaluar_oportunidad_procesal`).
- No atipicidad penal (`detectar_riesgos_atipicidad`).

## Riesgo si se omite
Pérdida silenciosa de recursos o derechos de la víctima en el proceso.
