<!-- config-version: 2; checksum: 4e16cd7e83c1b264 -->
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
Skills = contratos (no function_tools invocables). No existe tool LLM `clasificar_aprobacion_juridica`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `approval_gate_decision` — no implementada
- `audit_log_write` — no implementada

## Guardrails (g1–g10)
- **g4:** Nunca aprobar automáticamente con hallazgos críticos sin marcar `con_cambios` o `rechazar`.
- **g8:** Aviso de revisión profesional; dictamen preliminar de la IA.

## No duplicar
- No detectar alucinaciones (`detectar_alucinaciones_legales`).
- No revisar coherencia estratégica en detalle (`revisar_coherencia_estrategica`).

## Riesgo si se omite
Salida no revisada llega al cliente, a la víctima o al juzgado con errores graves.
