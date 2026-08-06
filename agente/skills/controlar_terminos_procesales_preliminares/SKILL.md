<!-- config-version: 3; checksum: 8454f8307152ef9a -->
---
name: controlar-terminos-procesales-preliminares
description: Contrato penal-víctimas: Identificar términos procesales relevantes y estimar fechas límite, con advertencia explícita de verificación humana. Activar cuando el plan/HITL o el especialista requiera `controlar_terminos_procesales_preliminares`. No sustituye a `generar_alertas_t...
disable-model-invocation: true
---

# controlar_terminos_procesales_preliminares

## Scope
- Category: `Skills de ruta procesal Ley 906`
- Skill ID: `controlar_terminos_procesales_preliminares`
- Tier: `operativo`

## Used By Agents
- `analista_ruta_procesal`
- `analista_seguimiento_procesal`

## Purpose
Identificar términos procesales relevantes y estimar fechas límite, con advertencia explícita de verificación humana.

## Rol en analista_ruta_procesal
Soporte a `evaluar_oportunidad_procesal` y recursos. **No sustituye** el cálculo del abogado.

## Rol en analista_seguimiento_procesal
Monitoreo operativo continuo de vencimientos.

## Inputs
- Etapa procesal y tipo de actuación (recurso, solicitud, audiencia).
- Fecha de notificación o actuación fundante (si consta).
- Calendario procesal y reglas Ley 906 (RAG).

## Outputs
- Por término: `nombre`, `fecha_base`, `fecha_limite_estimada`, `nivel_confianza` (alto | medio | bajo), `accion_recomendada`.
- Etiqueta obligatoria: `ESTIMACIÓN IA — VERIFICAR CON ABOGADO`.
- Pendientes si falta fecha base.

## Steps
1. Identificar términos según etapa canónica 906 y actuación pendiente (`proceso-penal-906.md` §Términos).
2. Exigir `fecha_base` (notificación/actuación); si falta → no cerrar límite; pendiente.
3. Estimar en **días hábiles** con `nivel_confianza`; etiqueta `ESTIMACIÓN IA — VERIFICAR CON ABOGADO`.
4. Generar acción recomendada; nunca autorizar radicación solo por alerta IA.
5. Entregar salida estructurada + `[PENDIENTE DE VERIFICAR]` y revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `controlar_terminos_procesales_preliminares`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `calendar_terms_calculator` — no implementada
- `calendar_event_create` — no implementada
- `audit_log_write` — no implementada

## Guardrails
- **No inventar:** No inventar fechas de notificación.
- **Pedir datos faltantes:** Sin fecha base, no cerrar fecha límite; marcar pendiente.
- **Revision humana obligatoria:** Nunca radicar recurso solo por alerta IA.
- **Oportunidad y terminos Ley 906:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **Aviso de borrador:** Aviso de verificación humana obligatoria en cada salida.


## Fuentes KB (obligatorio consultar antes de citar norma)
- `agente/conocimiento/proceso-penal-906.md` — etapas canónicas y términos (días hábiles).
- `agente/conocimiento/normas-clave.md` — criterio operativo + citación.
- Tools: `leer_playbook_proceso`, `leer_normas_clave`, `buscar_en_conocimiento`.
- Actuación/fecha/artículo no verificado → `[PENDIENTE DE VERIFICAR]`.

## No duplicar
- No alertas de calendario operativo (`generar_alertas_terminos_vencimientos` → `analista_seguimiento_procesal`).
- No oportunidad global (`evaluar_oportunidad_procesal`).

## Riesgo si se omite
Recursos extemporáneos por error en cómputo de términos.
