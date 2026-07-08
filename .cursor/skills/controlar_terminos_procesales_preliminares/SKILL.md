---
name: controlar-terminos-procesales-preliminares
description: Skill operativo penal-victimas: identificar y alertar terminos relevantes. No reemplaza calculo humano. Use when the workflow requires `controlar_terminos_procesales_preliminares`.
disable-model-invocation: true
---

# controlar_terminos_procesales_preliminares

## Scope
- Category: `Skills de ruta procesal Ley 906`
- Skill ID: `controlar_terminos_procesales_preliminares`
- Tier: `operativo`

## Used By Agents
- `analista_ruta_procesal_ley906`
- `gestor_seguimiento_procesal_penal`

## Purpose
Identificar términos procesales relevantes y estimar fechas límite, con advertencia explícita de verificación humana.

## Rol en analista_ruta_procesal
Soporte a `evaluar_oportunidad_procesal` y recursos. **No sustituye** el cálculo del abogado.

## Rol en gestor_seguimiento
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
1. Identificar términos relevantes según etapa y actuación pendiente.
2. Calcular o estimar fechas límite con advertencia de verificación humana.
3. Generar alertas con acción recomendada.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `calendar_terms_calculator`
- `calendar_event_create`
- `audit_log_write`

## Guardrails (g1–g10)
- **g1:** No inventar fechas de notificación.
- **g2:** Sin fecha base, no cerrar fecha límite; marcar pendiente.
- **g4:** Nunca radicar recurso solo por alerta IA.
- **g9:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **g8:** Aviso de verificación humana obligatoria en cada salida.

## No duplicar
- No alertas de calendario operativo (`generar_alertas_terminos_vencimientos` → gestor).
- No oportunidad global (`evaluar_oportunidad_procesal`).

## Riesgo si se omite
Recursos extemporáneos por error en cómputo de términos.
