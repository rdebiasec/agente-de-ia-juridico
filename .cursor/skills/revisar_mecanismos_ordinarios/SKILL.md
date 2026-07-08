---
name: revisar-mecanismos-ordinarios
description: Skill estrategico penal-victimas: verificar si hay vias ordinarias antes de tutela. Use when the workflow requires `revisar_mecanismos_ordinarios`.
disable-model-invocation: true
---

# revisar_mecanismos_ordinarios

## Scope
- Category: `Skills constitucionales y tutela`
- Skill ID: `revisar_mecanismos_ordinarios`
- Tier: `estrategico`

## Used By Agents
- `evaluador_derechos_fundamentales_tutela`

## Purpose
Inventariar recursos y actuaciones ordinarias Ley 906 pendientes o agotadas para análisis de subsidiariedad.

## Rol en evaluador_derechos_fundamentales_tutela
Insumo obligatorio antes de `evaluar_procedencia_tutela`.

## Inputs
- Etapa procesal penal y últimas actuaciones.
- Recursos o solicitudes interpuestos o disponibles (apelación, reposición, incidente, etc.).
- Plazos vigentes para actuar en vía ordinaria.

## Outputs
- `mecanismos_disponibles`: lista con `tipo`, `estado` (pendiente | agotado | no_interpuesto | no_aplica).
- `agotamiento_ordinario`: sí | no | parcial | `[PENDIENTE DE VERIFICAR]`.
- `actuacion_ordinaria_recomendada_antes_tutela` (si aplica).
- Etiqueta: `SUBSIDIARIEDAD — INSUMO PARA PROCEDENCIA`.

## Steps
1. Identificar recursos y actuaciones ordinarias en el proceso penal vigente.
2. Verificar si están pendientes de interponer o ya agotados.
3. Determinar si la tutela es subsidiaria respecto de dichos mecanismos.
4. Señalar plazo y actuación ordinaria concreta pendiente antes de tutela.
5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_ley906_search`
- `rag_corte_constitucional_search`

## Guardrails (g1–g10)
- **g1:** No inventar recursos interpuestos ni plazos.
- **g3:** Mecanismo “disponible” solo si es jurídicamente procedente en la etapa.
- **g4:** HITL obligatorio; insumo de subsidiariedad — no autoriza tutela sin abogado.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No evaluar procedencia global (`evaluar_procedencia_tutela`).
- No recomendar vía desde coordinador (`recomendar_via_constitucional_o_alternativa`).

## Riesgo si se omite
Tutela rechazada por no agotar recurso o solicitud ordinaria que sí estaba abierta en Ley 906.
