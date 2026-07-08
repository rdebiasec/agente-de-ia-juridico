---
name: analizar-perjuicio-irremediable
description: Skill estrategico penal-victimas: identificar urgencia constitucional. Use when the workflow requires `analizar_perjuicio_irremediable`.
disable-model-invocation: true
---

# analizar_perjuicio_irremediable

## Scope
- Category: `Skills constitucionales y tutela`
- Skill ID: `analizar_perjuicio_irremediable`
- Tier: `estrategico`

## Used By Agents
- `evaluador_derechos_fundamentales_tutela`

## Purpose
Evaluar si el perjuicio alegado es actual, grave y de difícil reparación para sustentar inmediatez constitucional.

## Rol en evaluador_derechos_fundamentales_tutela
Insumo para `evaluar_procedencia_tutela` (requisito de inmediatez); no dictamina procedencia sola.

## Inputs
- Hechos del perjuicio alegado (integridad, salud, vida, libertad, participación, etc.).
- Plazos de mecanismos ordinarios disponibles.
- Medidas de protección ya ordenadas o pendientes (si constan).

## Outputs
- `perjuicio_actual_o_inminente`: sí | no | `[PENDIENTE DE VERIFICAR]`.
- `gravedad`: alta | media | baja.
- `dificultad_reparacion`: alta | media | baja.
- `necesidad_medida_urgente`: sí | no | dudosa.
- `grado_inmediatez_preliminar`: alta | media | baja | no_evaluable.
- Etiqueta: `INSUMO INMEDIATEZ — NO SUSTITUYE evaluar_procedencia_tutela`.

## Steps
1. Identificar el perjuicio alegado y su carácter actual o inminente.
2. Evaluar si el perjuicio es grave, de difícil reparación y requiere medida urgente.
3. Contrastar con mecanismos ordinarios y plazos procesales vigentes.
4. Documentar conclusión preliminar de perjuicio irremediable con grado de certeza.
5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_corte_constitucional_search`
- `rag_expediente_search`

## Guardrails (g1–g10)
- **g1:** No inventar perjuicios ni estados de salud/riesgo.
- **g3:** Urgencia emocional ≠ perjuicio irremediable constitucional sin análisis.
- **g4:** HITL obligatorio; insumo de inmediatez — no autoriza tutela ni redacción sin abogado.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No dictaminar procedencia (`evaluar_procedencia_tutela`).
- No revisar vías ordinarias (`revisar_mecanismos_ordinarios`).

## Riesgo si se omite
Tutela sin sustento de inmediatez (rechazo) o demora en caso que sí requiere medida urgente.
