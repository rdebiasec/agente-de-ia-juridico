---
name: clasificar-aprobacion-juridica
description: Skill atomico penal-victimas: clasificar la salida como aprobable, aprobable con cambios, rechazada o escalar. Use when the workflow requires `clasificar_aprobacion_juridica`.
disable-model-invocation: true
---

# clasificar_aprobacion_juridica

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `clasificar_aprobacion_juridica`
- Tier: `operativo`

## Used By Agents
- `analista_calidad_juridica`

## Purpose
Emitir dictamen final de aprobación sobre salidas destinadas a uso externo o comunicación con cliente.

## Rol en analista_calidad_juridica
Último filtro antes de salida externa; integra hallazgos de skills de calidad previos.

## Inputs
- Salida a evaluar (documento, análisis, recomendación).
- Hallazgos de: `detectar_alucinaciones_legales`, `verificar_hechos_soportados`, `controlar_no_revictimizacion`, `controlar_confidencialidad_datos_sensibles`, tono.
- Contexto del caso y tier del skill origen.

## Outputs
- `dictamen`: aprobable | con_cambios | rechazar | escalar.
- `hallazgos_por_categoria`: factual | normativo | tono | confidencialidad | revictimización | estrategia.
- `cambios_requeridos` (lista priorizada si aplica).
- Etiqueta: `ULTIMO_FILTRO_SALIDA_EXTERNA`.

## Steps
1. Revisar soporte fáctico, normativo y jurisprudencial de la salida.
2. Aplicar checklist de riesgos (alucinación, confidencialidad, tono, revictimización).
3. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `approval_gate_decision`
- `audit_log_write`

## Guardrails (g1–g10)
- **g4:** Nunca aprobar automáticamente con hallazgos críticos sin marcar `con_cambios` o `rechazar`.
- **g8:** Aviso de revisión profesional; dictamen preliminar de la IA.

## No duplicar
- No detectar alucinaciones (`detectar_alucinaciones_legales`).
- No revisar coherencia estratégica en detalle (`revisar_coherencia_estrategica`).

## Riesgo si se omite
Salida no revisada llega al cliente, a la víctima o al juzgado con errores graves.
