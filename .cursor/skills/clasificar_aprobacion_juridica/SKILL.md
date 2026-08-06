<!-- config-version: 3; checksum: a7a9833f08e8c9fa -->
---
name: clasificar-aprobacion-juridica
description: Contrato penal-víctimas: Emitir dictamen final de aprobación sobre salidas destinadas a uso externo o comunicación con cliente. Activar cuando el plan/HITL o el especialista requiera `clasificar_aprobacion_juridica`. No sustituye a `detectar_alucinaciones_legales`.
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

## Fuentes KB
- `agente/conocimiento/proceso-penal-906.md` — checklist control de calidad; veredicto y gate duro.
- `agente/conocimiento/normas-clave.md` — checklist calidad/citas; HITL antes de uso externo.
- Tools reales: `buscar_en_conocimiento`, `buscar_en_expediente`, lecturas KB si hace falta anclar.
- Dictamen alineado a schema `DictamenCalidad` (`aprobable`|`con_cambios`|`rechazado`|`escalar`).

## Inputs
- Salida a evaluar (documento, análisis, recomendación).
- Hallazgos de: `detectar_alucinaciones_legales`, `verificar_hechos_soportados`, `controlar_no_revictimizacion`, `controlar_confidencialidad_datos_sensibles`, tono.
- Contexto del caso y tier del skill origen.

## Outputs
- `dictamen`: aprobable | con_cambios | rechazado | escalar.
- `hallazgos_por_categoria`: factual | normativo | tono | confidencialidad | revictimización | estrategia.
- `cambios_requeridos` (lista priorizada si aplica).
- Etiqueta: `ULTIMO_FILTRO_SALIDA_EXTERNA`.

## Steps
0. Integrar hallazgos previos; veredicto en {aprobable, con_cambios, rechazado, escalar} segun schema DictamenCalidad.
1. Clasificar: aprobable | con_cambios | rechazado | escalar.
2. Listar hallazgos y cambios requeridos concretos.
3. No reescribir el memorial completo; gate duro si rechazado/escalar.

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

## Guardrails
- **Revision humana obligatoria:** Nunca aprobar automáticamente con hallazgos críticos sin marcar `con_cambios` o `rechazado`.
- **Aviso de borrador:** Aviso de revisión profesional; dictamen preliminar de la IA.

## No duplicar
- No detectar alucinaciones (`detectar_alucinaciones_legales`).
- No revisar coherencia estratégica en detalle (`revisar_coherencia_estrategica`).

## Riesgo si se omite
Salida no revisada llega al cliente, a la víctima o al juzgado con errores graves.
