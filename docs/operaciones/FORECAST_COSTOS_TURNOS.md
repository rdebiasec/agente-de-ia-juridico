# Forecast costos internos — chat vs plan (B06)

**Producto:** firma virtual penal-víctimas  
**Modelos (Opción A):** `OPENAI_MODEL=gpt-4.1-mini` · `OPENAI_MODEL_HIGH_RISK=gpt-4.1`  
**Temp:** `0.2` general · `0.1` high-risk (redactor / tutela)  
**Fuente de medición:** `trace.completion` (hooks) + `estimated_cost_usd` en summary/calls  
**Tabla de precios:** `src/agents/pricing.py` (actualizar si cambia OpenAI)

## Fórmula

```text
$/turno ≈ Σ calls (input_tokens × $/1M_in + output_tokens × $/1M_out) / 1e6
         + (si plan: sumar cada paso)
```

No adivinar: leer mediana desde desk soporte / Workflow Trace.

## Precios orientativos (USD / 1M tokens, ~2026-07)

| Modelo | Input | Output | Uso |
|---|---:|---:|---|
| gpt-4.1-mini | 0.40 | 1.60 | POC + laborers |
| gpt-4.1 | 2.00 | 8.00 | Redactor / tutela |
| gpt-4o-mini (legacy) | 0.15 | 0.60 | — |
| gpt-4o (legacy) | 2.50 | 10.00 | — |

## Escenarios de ejemplo (orden de magnitud)

| Escenario | Shape típica | Estimación |
|---|---|---|
| Chat tipicidad (1 laborer) | ~4k in / 1.2k out mini | ~USD 0.0035 |
| Chat multi-tool | ~8k in / 2k out mini | ~USD 0.006 |
| Plan 3 pasos (sin high-risk) | 3× chat | ~USD 0.01–0.02 |
| Plan con redactor (1 paso 4.1) | ~6k in / 2k out 4.1 | ~USD 0.028 + pasos previos |

## Controles de costo ya en producto

| Driver | Default | Rol |
|---|---|---|
| `agent_max_turns` | 10 | Tope vueltas chat |
| `agent_max_turns_plan_step` | 6 | Tope por paso |
| `agent_max_total_tokens` | 30000 | Budget por run (alerta en desk) |
| Nested specialist ceiling | 8 | Evita loops as_tool |
| Chat sin high-risk tools | on | Evita $ 4.1 sin plan HITL |

## B13 — compactación de sesión

Tras medir mediana de tokens en desk (2 semanas):

- Tunear `SESSION_RECENT_MESSAGES` (hoy 16) y `SESSION_SUMMARY_MAX_CHARS` (hoy 1200).
- No bajar agresivo sin evidencia: corta contexto jurídico útil.

## Cómo cotizar

1. Medir mediana `$/turno` chat y `$/paso` plan en soporte.  
2. Multiplicar por volumen mensual esperado del cliente.  
3. Añadir margen ops + HITL (tiempo abogado), no solo tokens.
