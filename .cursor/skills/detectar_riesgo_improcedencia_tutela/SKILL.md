---
name: detectar-riesgo-improcedencia-tutela
description: Skill critico penal-victimas: detectar si tutela puede ser prematura, subsidiaria o improcedente. Use when the workflow requires `detectar_riesgo_improcedencia_tutela`.
disable-model-invocation: true
---

# detectar_riesgo_improcedencia_tutela

## Scope
- Category: `Skills constitucionales y tutela`
- Skill ID: `detectar_riesgo_improcedencia_tutela`
- Tier: `critico`

## Used By Agents
- `evaluador_derechos_fundamentales_tutela`
- `analista_calidad_juridica`

## Purpose
Alertar temprano si la tutela parece prematura, subsidiaria o improcedente antes del dictamen formal.

## Rol en evaluador_derechos_fundamentales_tutela
Triaje de riesgo antes o en paralelo a `evaluar_procedencia_tutela`; no sustituye el dictamen.

## Rol en analista_calidad_juridica
Segunda revisión si un borrador de tutela llegó al pipeline de calidad.

## Inputs
- Etapa procesal penal y actuaciones ordinarias pendientes o agotadas.
- Derecho invocado y hechos que motivan la acción.
- Recursos o solicitudes Ley 906 no interpuestos (si constan).
- Salida de `revisar_mecanismos_ordinarios` (si existe).

## Outputs
- `causales_riesgo`: subsidiariedad | falta_agotamiento | incompetencia | cosa_juzgada | daño_remediable | inmediatez_dudosa.
- `probabilidad_rechazo_preliminar`: alta | media | baja | `[PENDIENTE DE VERIFICAR]`.
- `via_alternativa_recomendada`: petición | solicitud_906 | recurso | aguardar_ordinario.
- `actuacion_ordinaria_pendiente` antes de tutela (si aplica).
- Etiqueta: `ALERTA IMPROCEDENCIA — NO SUSTITUYE evaluar_procedencia_tutela`.

## Steps
1. Inventariar vías ordinarias disponibles en la etapa penal actual.
2. Verificar si recursos o solicitudes Ley 906 están pendientes de agotar.
3. Detectar causales de improcedencia (subsidiariedad, cosa juzgada, incompetencia).
4. Evaluar si el daño es actual o remediabile por vía ordinaria.
5. Documentar probabilidad de rechazo y costo de tutela prematura.
6. Recomendar vía alternativa preferente si la tutela es improcedente.
7. Señalar plazo y actuación ordinaria recomendada antes de tutela.
8. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `detectar_riesgo_improcedencia_tutela`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_corte_constitucional_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto

## Guardrails (g1–g10)
- **g1:** No citar sentencias de tutela sin verificar en RAG.
- **g3:** Alerta de riesgo ≠ dictamen de improcedencia definitivo.
- **g4:** HITL obligatorio; no desaconsejar tutela sin revisión del abogado en casos de urgencia extrema.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No dictaminar procedencia (`evaluar_procedencia_tutela`).
- No redactar tutela ni insumos (`preparar_borrador_tutela_preliminar`, `redactar_tutela_penal_preliminar`).

## Riesgo si se omite
Radicar tutela rechazada por subsidiariedad, debilitando la vía ordinaria penal y generando costos a la víctima.
