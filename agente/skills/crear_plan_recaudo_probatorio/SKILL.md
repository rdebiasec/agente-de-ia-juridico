<!-- config-version: 2; checksum: 4577d9bd56357daa -->
---
name: crear-plan-recaudo-probatorio
description: Skill estrategico penal-victimas: proponer plan para obtener pruebas faltantes. Use when the workflow requires `crear_plan_recaudo_probatorio`.
disable-model-invocation: true
---

# crear_plan_recaudo_probatorio

## Scope
- Category: `Skills de evidencia y soporte probatorio`
- Skill ID: `crear_plan_recaudo_probatorio`
- Tier: `estrategico`

## Used By Agents
- `gestor_evidencia_y_soporte_probatorio`
- `analista_representacion_victimas`

## Purpose
Planificar obtención de pruebas faltantes críticas según matriz hecho-prueba y etapa procesal.

## Rol en gestor_evidencia_y_soporte_probatorio
Ejecutar tras `detectar_brechas_probatorias` o matriz hecho-prueba.

## Rol en analista_representacion_victimas
Alinear recaudo con objetivos de la víctima y teoría del caso.

## Inputs
- Brechas probatorias (`detectar_brechas_probatorias`) o matriz hecho-prueba.
- Etapa procesal y plazos de recaudo disponibles.
- Recursos del despacho y acceso a víctima/testigos.

## Outputs
- Plan por ítem: `prueba_faltante`, `hecho_que_sostiene`, `via_obtencion` (oficio | solicitud | peritaje | declaración), `responsable`, `plazo`, `urgencia`.
- Orden por impacto procesal (alto → bajo).
- Etiqueta: `PLAN RECAUDO — EJECUCIÓN CON APROBACIÓN ABOGADO`.

## Steps
1. Listar pruebas faltantes críticas según matriz hecho-prueba.
2. Asignar responsable, plazo y vía de obtención (oficio, solicitud, peritaje).
3. Ordenar por impacto procesal y urgencia.
4. Señalar dependencias (ej. custodia antes de peritaje).
5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `crear_plan_recaudo_probatorio`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `task_manager_create` — no implementada
- `rag_expediente_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto

## Guardrails (g1–g10)
- **g1:** No inventar pruebas ya existentes en expediente.
- **g4:** HITL antes de oficios o contacto con víctima para recaudo.
- **g5:** Minimizar exposición de la víctima en vías de obtención innecesarias.
- **g9:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No inventariar evidencia existente (`inventariar_evidencia`).
- No evaluar suficiencia global (`evaluar_suficiencia_probatoria`).

## Riesgo si se omite
Audiencia o memorial sin prueba clave que ya se podía recaudar con tiempo.
