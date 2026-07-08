---
name: preparar-resumen-operativo-cliente
description: Skill atomico penal-victimas: crear version simple del estado del proceso para cliente, sin estrategia sensible. Use when the workflow requires `preparar_resumen_operativo_cliente`.
disable-model-invocation: true
---

# preparar_resumen_operativo_cliente

## Scope
- Category: `Skills de seguimiento procesal`
- Skill ID: `preparar_resumen_operativo_cliente`
- Tier: `operativo`

## Used By Agents
- `gestor_seguimiento_procesal_penal`
- `analista_calidad_juridica`

## Purpose
Redactar resumen simple del estado del proceso para la víctima o cliente, sin estrategia sensible.

## Rol en gestor_seguimiento_procesal_penal
Comunicación periódica de avance procesal.

## Rol en analista_calidad_juridica
Aprobar tono y confidencialidad antes de envío.

## Inputs
- Estado del radicado y últimas actuaciones.
- Próximos pasos procesales públicos (no estrategia interna).
- Aprobación previa del abogado (si aplica).

## Outputs
- Resumen en lenguaje accesible: qué pasó, qué sigue, qué necesita el cliente.
- `excluido_estrategia_sensible`: confirmación explícita.
- Etiqueta: `SOLO_TRAS_APROBACION_ABOGADO — NO ENVIAR DIRECTO`.

## Steps
1. Sintetizar estado del proceso en lenguaje accesible.
2. Incluir próximos pasos sin revelar estrategia sensible.
3. Marcar para revisión humana antes de envío al cliente.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `case_state_reader`
- `approval_gate_submit`

## Guardrails (g1–g10)
- **g4:** HITL obligatorio; nunca envío automático al cliente.
- **g6:** No incluir datos de terceros ni detalles gráficos innecesarios.
- **g9:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No resumen ejecutivo litigante (`crear_resumen_ejecutivo_litigante` — abogado).
- No reporte técnico (`crear_reporte_estado_caso`).

## Riesgo si se omite
Cliente desinformado o, peor, informado con datos estratégicos que no debía conocer.
