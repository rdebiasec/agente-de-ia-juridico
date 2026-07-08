---
name: detectar-urgencia-penal
description: Skill estrategico penal-victimas: identificar si el caso requiere atencion humana inmediata. Use when the workflow requires `detectar_urgencia_penal`.
disable-model-invocation: true
---

# detectar_urgencia_penal

## Scope
- Category: `Skills transversales`
- Skill ID: `detectar_urgencia_penal`
- Tier: `estrategico`

## Used By Agents
- `coordinador_expediente_penal`
- `gestor_seguimiento_procesal_penal`
- `analista_calidad_juridica`

## Purpose
Detectar si el caso o el turno exigen atención humana inmediata por riesgo a derechos, términos, integridad o pérdida probatoria.

## Rol en coordinador
Ejecutar en triage inicial y cuando el abogado reporte hechos nuevos de riesgo. Prioriza escalamiento antes de análisis de fondo.

## Inputs
- Solicitud del turno y hechos reportados.
- Fechas de audiencias, términos o vencimientos mencionados o en expediente.
- Indicios de riesgo a integridad de la víctima, libertad, destrucción de evidencia o silencio procesal prolongado.
- Estado del radicado y última actuación (si existe).

## Outputs
- `nivel_urgencia`: crítica | alta | media | baja.
- `motivos` (lista verificable o `[PENDIENTE DE VERIFICAR]`).
- `accion_inmediata_sugerida` (ej. contactar abogado titular, preservar evidencia, verificar término).
- `escalamiento`: sí/no y destino (humano responsable / agente especialista).
- Timestamp de la evaluación preliminar.

## Steps
1. Evaluar indicios de riesgo inminente (términos, libertad, integridad, evidencia).
2. Clasificar nivel de urgencia y necesidad de atención humana inmediata.
3. Escalar con notificación si aplica.
4. Documentar motivo de escalamiento y agente destino.
5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `calendar_terms_calculator`
- `case_state_reader`
- `notification_create`

## Guardrails (g1–g10)
- **g1:** No inventar vencimientos ni amenazas no reportadas.
- **g2:** Si falta fecha de audiencia o término crítico, marcar urgencia `[PENDIENTE DE VERIFICAR]` y pedir dato.
- **g3:** Distinguir riesgo reportado de inferencia de la IA.
- **g4:** Nivel crítica/alta siempre requiere confirmación humana antes de actuar.
- **g5:** En riesgo a integridad, no exponer datos sensibles de la víctima en la notificación de escalamiento.
- **g8:** Aviso de que la urgencia es preliminar y debe confirmar el abogado.

## No duplicar
- No calcular todos los términos del caso (`generar_alertas_terminos_vencimientos`).
- No evaluar procedencia de tutela (`evaluar_procedencia_tutela`).
- No preservar evidencia digital (`preservar_evidencia_digital`).

## Riesgo si se omite
Pérdida de términos, deterioro probatorio o falta de protección oportuna a la víctima.
