---
name: controlar-audiencias
description: Skill atomico penal-victimas: administrar fechas, horas, enlaces y preparacion de audiencias. Use when the workflow requires `controlar_audiencias`.
disable-model-invocation: true
---

# controlar_audiencias

## Scope
- Category: `Skills de audiencias`
- Skill ID: `controlar_audiencias`
- Tier: `operativo`

## Used By Agents
- `preparador_estrategico_audiencias_penales`
- `analista_calidad_juridica`

## Purpose
Controlar que la preparación de audiencia cumpla requisitos formales y sustantivos Ley 906 antes de la intervención.

## Rol en preparador_estrategico_audiencias_penales
Checklist de control previo a audiencia.

## Rol en analista_calidad_juridica
Segunda revisión si el paquete de audiencia va a uso externo.

## Inputs
- Tipo de audiencia, fecha y etapa procesal.
- Objetivo, guion, preguntas y solicitudes orales preparadas.
- Plazos y requisitos de intervención de la víctima.

## Outputs
- `checklist`: ítem | cumple | no_cumple | pendiente.
- `bloqueantes` que impiden intervenir sin corrección.
- Etiqueta: `CONTROL AUDIENCIA — REVISAR CON ABOGADO`.

## Steps
1. Verificar tipo de audiencia y competencia del despacho/juez.
2. Contrastar preparación con requisitos Ley 906 de intervención de la víctima.
3. Señalar omisiones formales o sustantivas antes de la audiencia.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `controlar_audiencias`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_ley906_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `calendar_event_reader` — no implementada

## Guardrails (g1–g10)
- **g4:** HITL obligatorio antes de audiencia.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No redactar preguntas (`preparar_preguntas_audiencia`).
- No checklist operativo (`crear_checklist_previo_audiencia` — lista táctica).

## Riesgo si se omite
Intervención extemporánea, improcedente o sin cumplir requisitos de la audiencia.
