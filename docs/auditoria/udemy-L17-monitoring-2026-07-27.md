# Udemy L17 — Monitoring — 2026-07-27

**Fase:** AUDITORIA_ANTES  
**Prioridad:** P0 · Oleada A

---

## 1. Checklist Antes / Después

| Ítem | Antes | Después propuesto | Decisión / por qué | Evidencia |
|---|---|---|---|---|
| Traces OpenAI | `RunConfig(workflow_name="firma-juridica", group_id=session_id, …)` | Mantener | Debugging en platform.openai.com | `runner.py` |
| Traza propia | Spans agent/tool/llm + usage; `SessionTrace` | Ampliar tasa tripwire / costo por sesión | Ops sin adivinar | `runner.py`, `gateway/trace.py` |
| Support API | `/support/operations`, sessions | Mantener + scrubbing PII en resúmenes | Consola despacho | `support_api.py`, `desk-soporte.js` |
| Sentry | Opcional `SENTRY_DSN`, sample 0.05, sin scrub 1581 | `before_send` scrub + release tags | Cumplimiento + incidentes | `main.py`, `config.py` |
| Alerting / métricas | Ausente (p95, fallos tool) | Mínimo: log estructurado o Sentry issues de tripwire | Lección: observability obligatoria en prod | — |

---

## 2. Relevancia al producto abogado

- Incidentes de producción no pueden filtrar datos de casos.
- Soporte puede ver qué tool falló sin reabrir el chat completo.

## 3. Qué NO hacer

- No enviar cuerpos de expediente crudos a Sentry.
- No subir `traces_sample_rate` sin scrubbing.

## 4. PASS / FAIL

| Verificación | PASS | FAIL | Resultado |
|---|---|---|---|
| Traza sesión | Spans + usage visibles | Vacío | Ya parcial PASS |
| Sentry PII | Scrubbed | PII en event | Pendiente impl |

## 5. Pendiente humano

- Set `SENTRY_DSN` en Render si se quiere observability externa.
- «aprobado, ejecuta» L17.

## 6. Estado tras esta pasada

**Sin cambio de código.** Base de trazas sólida; falta scrubbing/métricas/alerting.
