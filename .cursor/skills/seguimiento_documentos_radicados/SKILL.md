<!-- config-version: 2; checksum: 832d683f212ba195 -->
---
name: seguimiento-documentos-radicados
description: Skill atomico penal-victimas: controlar documentos enviados y respuestas pendientes. Use when the workflow requires `seguimiento_documentos_radicados`.
disable-model-invocation: true
---

# seguimiento_documentos_radicados

## Scope
- Category: `Skills de seguimiento procesal`
- Skill ID: `seguimiento_documentos_radicados`
- Tier: `operativo`

## Used By Agents
- `analista_seguimiento_procesal`

## Purpose
Hacer seguimiento a documentos enviados o radicados y su estado de respuesta.


## Rol en gestor_seguimiento
Seguimiento de peticiones y respuestas; alerta vencimientos y faltantes.
## Inputs
- Lista de documentos radicados (fecha, destinatario, radicado interno).
- Plazos de respuesta esperados.

## Outputs
- Por documento: `estado` (pendiente | respondido | vencido | desconocido), `días_transcurridos`, `acción_sugerida`.
- Alertas de vencimiento.

## Steps
1. Cruzar documentos radicados con plazos y respuestas recibidas.
2. Marcar vencidos y próximos a vencer.
3. Sugerir acción de seguimiento (llamado, memorial, petición).
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `seguimiento_documentos_radicados`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `case_state_reader` — no implementada
- `calendar_terms_calculator` — no implementada

## Guardrails (g1–g10)
- **g1:** No inventar respuestas de autoridad.
- **g9:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **g4:** HITL obligatorio antes de usar la salida en memorial, estrategia o comunicación con cliente.
- **g8:** Aviso de revisión profesional.

## Riesgo si se omite
Silencios administrativos no detectados y pérdida de términos útiles.
