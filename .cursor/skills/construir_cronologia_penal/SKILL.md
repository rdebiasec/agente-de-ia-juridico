---
name: construir-cronologia-penal
description: Skill estrategico penal-victimas: ordenar hechos en linea de tiempo. Use when the workflow requires `construir_cronologia_penal`.
disable-model-invocation: true
---

# construir_cronologia_penal

## Scope
- Category: `Skills de hechos y cronologia`
- Skill ID: `construir_cronologia_penal`
- Tier: `estrategico`

## Used By Agents
- `analista_cronologia_hechos_penales` (skill primario del agente)
- `preparador_estrategico_audiencias_penales`

## Purpose
Construir línea de tiempo penal con hechos fechados, actores y nivel de soporte, separando confirmados, narrados e inferidos.

## Rol en analista_cronologia
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
1. Extraer hechos con fecha, hora y actores de fuentes verificadas.
2. Ordenar línea de tiempo y señalar eventos sin fecha exacta.
3. Marcar inconsistencias entre versiones.
4. Validar coherencia temporal con matriz hecho-fuente y marcar huecos.
5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `date_extractor`
- `entity_extractor`
- `case_state_writer`

## Guardrails (g1–g10)
- **g1:** No inventar fechas, horas ni eventos para completar la línea de tiempo.
- **g2:** Sin fuentes con fecha, dejar evento en cola sin fecha; no inferir secuencia cerrada.
- **g3:** Obligatorio: tres bloques (confirmado / narrado / inferido) en la salida final.
- **g4:** Cronología para memorial o audiencia requiere revisión del abogado antes de uso externo.
- **g5:** No ordenar relatos de víctima de forma que implique incredibilidad o culpa.
- **g6:** Minimizar datos sensibles; referir a fuente documental cuando baste.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No extraer hechos crudos (`extraer_hechos_relevantes`).
- No análisis exhaustivo de contradicciones (`detectar_contradicciones_factuales` — solo señalar en paso 3).
- No vincular hecho-prueba (`construir_matriz_hecho_prueba`).

## Riesgo si se omite
Memoriales con línea de tiempo inconsistente que defensa o Fiscalía explotan en audiencia.
