<!-- config-version: 3; checksum: d30420f51c9c5c65 -->
---
name: generar-alertas-terminos-vencimientos
description: Contrato penal-víctimas: Generar alertas de vencimientos próximos clasificadas por criticidad. Activar cuando el plan/HITL o el especialista requiera `generar_alertas_terminos_vencimientos`. No sustituye a `controlar_terminos_procesales_preliminares`.
disable-model-invocation: true
---

# generar_alertas_terminos_vencimientos

## Scope
- Category: `Skills de seguimiento procesal`
- Skill ID: `generar_alertas_terminos_vencimientos`
- Tier: `operativo`

## Used By Agents
- `analista_ruta_procesal`
- `analista_seguimiento_procesal`

## Purpose
Generar alertas de vencimientos próximos clasificadas por criticidad.

## Rol en analista_ruta_procesal
Alertas ligadas a actuación estratégica inminente (recurso, audiencia). Complementa `controlar_terminos_procesales_preliminares`.

## Rol en analista_seguimiento_procesal
Calendario operativo del caso.

## Inputs
- Términos identificados (`controlar_terminos_procesales_preliminares`).
- Calendario de audiencias y actuaciones.
- Responsable asignado por alerta.

## Outputs
- Alertas: `id`, `descripcion`, `fecha_objetivo`, `criticidad` (crítica | alta | media), `responsable`, `nivel_confianza`.
- Notificación sugerida (sí/no).

## Steps
1. Identificar términos/plazos con fuente y fecha de cómputo si consta.
2. Clasificar alerta: informativa | próxima | vencida | incierta.
3. No inventar dies a quo; marcar incertidumbre.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `generar_alertas_terminos_vencimientos`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `calendar_terms_calculator` — no implementada
- `notification_create` — no implementada

## Guardrails
- **No inventar:** Fechas estimadas etiquetadas como tales.
- **Revision humana obligatoria:** Alerta crítica dispara revisión humana, no actuación automática.
- **Oportunidad y terminos Ley 906:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **Aviso de borrador:** Verificación humana de términos.

## No duplicar
- No identificar términos desde cero (`controlar_terminos_procesales_preliminares`).
- No urgencia global del caso (`detectar_urgencia_penal`).

## Riesgo si se omite
Vencimientos no visibles hasta que ya es tarde para recurrir.
