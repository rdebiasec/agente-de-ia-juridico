---
name: marcar-pendientes-verificacion
description: Skill atomico penal-victimas: marcar cualquier dato, cita o hecho incompleto como `[PENDIENTE DE VERIFICAR]`. Use when the workflow requires `marcar_pendientes_verificacion`.
disable-model-invocation: true
---

# marcar_pendientes_verificacion

## Scope
- Category: `Skills transversales`
- Skill ID: `marcar_pendientes_verificacion`
- Tier: `atomico`

## Used By Agents
- `coordinador_expediente_penal`

## Purpose
Recorrer la salida del turno e insertar `[PENDIENTE DE VERIFICAR]` en todo dato, cita normativa, hecho o radicado sin fuente verificable.

## Rol en coordinador
Control de calidad transversal antes de entregar cualquier salida del coordinador o de ensamblar respuestas de subagentes.

## Inputs
- Texto o estructura de salida a revisar (del turno actual o borrador consolidado).
- Fuentes disponibles en expediente o RAG para contrastar.
- Lista opcional de elementos ya marcados por otros skills.

## Outputs
- Texto con marcadores `[PENDIENTE DE VERIFICAR]` insertados.
- Registro de pendientes: `elemento`, `tipo` (hecho | cita | radicado | fecha | otro), `impacto_juridico` (alto | medio | bajo).
- Conteo de pendientes y recomendación de no uso externo si hay impacto alto.

## Steps
1. Recorrer salida e insertar `[PENDIENTE DE VERIFICAR]` en cada dato, cita o hecho sin fuente.
2. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `audit_log_write`

## Guardrails (g1–g10)
- **g1:** Implementación directa de g1 — todo sin fuente queda marcado, nunca inventado.
- **g3:** No eliminar la distinción hecho/inferencia al marcar; solo etiquetar.
- **g4:** Si impacto alto (etapa, tutela, término), bloquear uso externo hasta revisión humana.
- **g8:** Incluir aviso estándar de revisión profesional al final.

## No duplicar
- No validar existencia de normas (`verificar_citas_normativas` → calidad/redactor).
- No cruzar hechos con expediente en profundidad (`verificar_hechos_soportados`).
- No clasificar tipo de fuente (`clasificar_fuente_factual`).

## Riesgo si se omite
Uso de afirmaciones sin soporte en comunicaciones del despacho → responsabilidad profesional y daño al caso.
