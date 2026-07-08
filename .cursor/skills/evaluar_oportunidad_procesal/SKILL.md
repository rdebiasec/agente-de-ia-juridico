---
name: evaluar-oportunidad-procesal
description: Skill operativo penal-victimas: determinar si una solicitud o intervencion es oportuna, prematura o extemporanea. Use when the workflow requires `evaluar_oportunidad_procesal`.
disable-model-invocation: true
---

# evaluar_oportunidad_procesal

## Scope
- Category: `Skills de ruta procesal Ley 906`
- Skill ID: `evaluar_oportunidad_procesal`
- Tier: `operativo`

## Used By Agents
- `analista_ruta_procesal_ley906`
- `analista_calidad_juridica`

## Purpose
Determinar si una actuación propuesta es oportuna, prematura o extemporánea para la víctima en la etapa actual.

## Rol en analista_ruta_procesal
Decisión clave antes de cualquier solicitud, recurso o intervención. Requiere etapa y términos preliminares.

## Inputs
- Actuación o solicitud propuesta (tipo, destinatario, objeto).
- Etapa procesal y actuaciones previas del radicado.
- Fechas límite estimadas (`controlar_terminos_procesales_preliminares`).
- Estado probatorio relevante (si aplica).

## Outputs
- `dictamen_preliminar`: oportuna | prematura | extemporánea | `[PENDIENTE DE VERIFICAR]`.
- `razon`, `consecuencias_de_actuar_o_no`, `fecha_alternativa_sugerida`.
- `datos_faltantes` para cerrar dictamen.
- Advertencia: cálculo de términos requiere verificación humana.

## Steps
1. Ubicar la actuación propuesta en la etapa exacta del proceso penal.
2. Verificar plazos y términos aplicables con advertencia de cálculo humano.
3. Contrastar con actuaciones previas y estado del radicado.
4. Determinar si es oportuna, prematura o extemporánea para la víctima.
5. Evaluar consecuencias de actuar o no actuar en este momento.
6. Sugerir fecha o actuación alternativa si no es oportuna.
7. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_ley906_search`
- `calendar_terms_calculator`

## Guardrails (g1–g10)
- **g1:** No inventar plazos ni actuaciones previas.
- **g2:** Sin fecha de notificación de acto a impugnar, dictamen extemporaneidad = pendiente.
- **g3:** Oportunidad es dictamen preliminar, no certeza judicial.
- **g4:** HITL obligatorio antes de interponer recurso o solicitud.
- **g9:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **g8:** Aviso: términos deben verificarse por abogado.

## No duplicar
- No calcular todos los términos (`controlar_terminos_procesales_preliminares`).
- No redactar recurso (`redactar_recurso_o_intervencion_preliminar` → redactor).
- No mapear catálogo de actuaciones (`mapear_actuaciones_posibles_victima`).

## Riesgo si se omite
Pérdida de recursos, preclusión o solicitud rechazada por extemporaneidad.
