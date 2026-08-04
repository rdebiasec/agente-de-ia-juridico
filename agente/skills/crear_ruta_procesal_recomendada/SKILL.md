<!-- config-version: 2; checksum: ebf44a0af3487133 -->
---
name: crear-ruta-procesal-recomendada
description: Skill estrategico penal-victimas: crear plan de proximos pasos procesales para revision del abogado. Use when the workflow requires `crear_ruta_procesal_recomendada`.
disable-model-invocation: true
---

# crear_ruta_procesal_recomendada

## Scope
- Category: `Skills de ruta procesal Ley 906`
- Skill ID: `crear_ruta_procesal_recomendada`
- Tier: `estrategico`

## Used By Agents
- `analista_ruta_procesal` (uso principal)

## Purpose
Proponer secuencia de próximos pasos procesales para la representación de la víctima, con responsables y plazos, para revisión del abogado.

## Rol en analista_ruta_procesal
Producto integrador del agente. Ejecutar tras etapa, actuaciones mapeadas, oportunidad y riesgos procesales.

## Rol en coordinador
**MOVE:** este skill ya no es ownership del POC. El coordinador solo lo dispara vía tool del especialista dueño.


## Inputs
- Etapa procesal actual (confirmada o `[PENDIENTE DE VERIFICAR]`).
- Actuaciones pendientes y últimas actuaciones del radicado.
- Objetivos preliminares de la víctima (si constan).
- Términos o audiencias próximas conocidas.
- Riesgos procesales (`detectar_riesgos_procesales`).

## Outputs
- Ruta numerada: paso, actuación, responsable, plazo estimado, dependencia.
- Riesgos procesales de la ruta (oportunidad, improcedencia, extemporaneidad).
- Agentes IA o abogados sugeridos por paso.
- Etiqueta: `BORRADOR PARA REVISIÓN — NO EJECUTAR SIN APROBACIÓN`.

## Steps
1. Sintetizar etapa actual y actuaciones pendientes.
2. Proponer secuencia de próximos pasos con responsables y plazos.
3. Incluir riesgos procesales de la ruta propuesta.
4. Entregar ruta numerada con responsable y plazo por paso.
5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `crear_ruta_procesal_recomendada`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `task_manager_create` — no implementada
- `audit_log_write` — no implementada

## Guardrails (g1–g10)
- **g1:** No citar artículos Ley 906 sin verificar en RAG.
- **g2:** Sin etapa ni radicado, no proponer ruta cerrada.
- **g3:** Distinguir hechos del expediente de supuestos para planificar.
- **g4:** HITL obligatorio: estrategia procesal no se ejecuta sin firma.
- **g5:** Ruta centrada en derechos de la víctima.
- **g9:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **g8:** Aviso de borrador y revisión profesional.

## No duplicar
- No evaluar oportunidad de cada actuación (`evaluar_oportunidad_procesal`).
- No redactar memoriales (`redactor_documentos_juridicos`).

## Riesgo si se omite
Actuaciones desordenadas o extemporáneas en representación de víctimas bajo Ley 906.
