<!-- config-version: 2; checksum: 81029d074ff6580f -->
---
name: seguimiento-documentos-radicados
description: Contrato penal-víctimas: Hacer seguimiento a documentos enviados o radicados y su estado de respuesta. Activar cuando el plan/HITL o el especialista requiera `seguimiento_documentos_radicados`. No sustituye a `monitorear_radicado`.
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

## Rol en analista_seguimiento_procesal
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

## Guardrails
- **No inventar:** No inventar respuestas de autoridad.
- **Oportunidad y terminos Ley 906:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **Revision humana obligatoria:** HITL obligatorio antes de usar la salida en memorial, estrategia o comunicación con cliente.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No solo estado del radicado (`monitorear_radicado`).
- No inventario de evidencia física/digital (`inventariar_evidencia`).

## Riesgo si se omite
Silencios administrativos no detectados y pérdida de términos útiles.
