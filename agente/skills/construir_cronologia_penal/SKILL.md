<!-- config-version: 3; checksum: 111430392bc5f502 -->
---
name: construir-cronologia-penal
description: Contrato penal-víctimas: Construir línea de tiempo penal con hechos fechados, actores y nivel de soporte, separando confirmados, narrados e inferidos. Activar cuando el plan/HITL o el especialista requiera `construir_cronologia_penal`. No sustituye a `extraer_hechos_relevantes`.
disable-model-invocation: true
---

# construir_cronologia_penal

## Scope
- Category: `Skills de hechos y cronologia`
- Skill ID: `construir_cronologia_penal`
- Tier: `estrategico`

## Used By Agents
- `analista_cronologia_hechos` (skill primario del agente)
- `analista_audiencias`

## Purpose
Construir línea de tiempo penal con hechos fechados, actores y nivel de soporte, separando confirmados, narrados e inferidos.

## Rol en analista_cronologia_hechos
Producto central del agente. Ejecutar tras `extraer_hechos_relevantes` y `crear_matriz_hecho_fuente`. Las contradicciones profundas van a `detectar_contradicciones_factuales`.

## Inputs
- Hechos extraídos con referencia de fuente (`extraer_hechos_relevantes`).
- Matriz hecho-fuente (si existe).
- Mapa de actores (`identificar_actores_y_roles`).
- Fechas/horas explícitas o aproximadas en documentos y relatos.

## Outputs
- Cronología ordenada: `fecha_hora`, `evento`, `actores`, `nivel_soporte`, `fuente`.
- Eventos sin fecha exacta (cola o rango estimado marcado `[PENDIENTE DE VERIFICAR]`).
- Inconsistencias temporales señaladas (no resueltas).
- Tres bloques separados: hechos confirmados | narrados | inferidos.

## Steps
1. Ordenar hechos/eventos por fecha u orden relativo cuando falte fecha exacta.
2. Etiquetar cada evento: confirmado | narrado | inferido | pendiente_verificar.
3. Registrar actores y fuente por evento; no inventar fechas.
4. Señalar huecos temporales evidentes sin rellenarlos; derivar vacíos a `detectar_vacios_factuales` si aplica.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `construir_cronologia_penal`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `date_extractor` — no implementada
- `entity_extractor` — no implementada
- `case_state_writer` — no implementada

## Guardrails
- **No inventar:** No inventar fechas, horas ni eventos para completar la línea de tiempo.
- **Pedir datos faltantes:** Sin fuentes con fecha, dejar evento en cola sin fecha; no inferir secuencia cerrada.
- **Separar hecho de inferencia:** Obligatorio: tres bloques (confirmado / narrado / inferido) en la salida final.
- **Revision humana obligatoria:** Cronología para memorial o audiencia requiere revisión del abogado antes de uso externo.
- **No revictimizar:** No ordenar relatos de víctima de forma que implique incredibilidad o culpa.
- **Confidencialidad:** Minimizar datos sensibles; referir a fuente documental cuando baste.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No extraer hechos crudos (`extraer_hechos_relevantes`).
- No análisis exhaustivo de contradicciones (`detectar_contradicciones_factuales` — solo señalar en paso 3).
- No vincular hecho-prueba (`construir_matriz_hecho_prueba`).

## Riesgo si se omite
Memoriales con línea de tiempo inconsistente que defensa o Fiscalía explotan en audiencia.
