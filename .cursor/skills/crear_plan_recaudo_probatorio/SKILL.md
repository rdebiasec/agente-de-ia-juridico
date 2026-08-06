<!-- config-version: 4; checksum: 4309be4259555b1f -->
---
name: crear-plan-recaudo-probatorio
description: Contrato penal-víctimas: Planificar obtención de pruebas faltantes críticas según matriz hecho-prueba y etapa procesal. Activar cuando el plan/HITL o el especialista requiera `crear_plan_recaudo_probatorio`. No sustituye a `inventariar_evidencia`.
disable-model-invocation: true
---

# crear_plan_recaudo_probatorio

## Scope
- Category: `Skills de evidencia y soporte probatorio`
- Skill ID: `crear_plan_recaudo_probatorio`
- Tier: `estrategico`

## Used By Agents
- `analista_evidencia`
- `analista_representacion_victimas`

## Purpose
Planificar obtención de pruebas faltantes críticas según matriz hecho-prueba y etapa procesal.

## Rol en analista_evidencia
Ejecutar tras `detectar_brechas_probatorias` o matriz hecho-prueba.

## Rol en analista_representacion_victimas
Alinear recaudo con objetivos de la víctima y teoría del caso.

## Fuentes KB
- Brechas/matriz del expediente; etapa aparente si consta (no inventar plazos).
- `agente/conocimiento/proceso-penal-906.md` — vías de obtención según etapa; días hábiles solo con `fecha_base`.
- `agente/conocimiento/normas-clave.md` — no revictimizar en vías de obtención; HITL antes de oficios/contactos.
- Tools reales: `buscar_en_expediente`, `buscar_en_conocimiento`, `leer_playbook_proceso` si ancla etapa.

## Inputs
- Brechas probatorias (`detectar_brechas_probatorias`) o matriz hecho-prueba.
- Etapa procesal y plazos de recaudo disponibles.
- Recursos del despacho y acceso a víctima/testigos.

## Outputs
- Plan por ítem: `prueba_faltante`, `hecho_que_sostiene`, `via_obtencion` (oficio | solicitud | peritaje | declaración), `responsable`, `plazo`, `urgencia`.
- Orden por impacto procesal (alto → bajo).
- Etiqueta: `PLAN RECAUDO — EJECUCIÓN CON APROBACIÓN ABOGADO`.

## Steps
1. Priorizar brechas materiales.
2. Proponer diligencias/recaudos con responsable sugerido y urgencia.
3. No alterar evidencia; preservar integridad.
4. HITL antes de contactar terceros o radicar solicitudes.

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

## Guardrails
- **No inventar:** No inventar pruebas ya existentes en expediente.
- **Revision humana obligatoria:** HITL antes de oficios o contacto con víctima para recaudo.
- **No revictimizar:** Minimizar exposición de la víctima en vías de obtención innecesarias.
- **Oportunidad y terminos Ley 906:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No inventariar evidencia existente (`inventariar_evidencia`).
- No evaluar suficiencia global (`evaluar_suficiencia_probatoria`).

## Riesgo si se omite
Audiencia o memorial sin prueba clave que ya se podía recaudar con tiempo.
