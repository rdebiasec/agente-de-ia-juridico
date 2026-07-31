# Udemy L17 — Monitoring — 2026-07-31 (clase formal)

**Fase:** HECHO_CLASE  
**Orden pedagógico:** #17  
**Decisión global:** DEJAR QUIETO base (trazas propias + OpenAI) · backlog **B04 · B07 · B15** (costos/ops/Sentry scrub) en batch final  
**Fuente:** `txt/17_monitoring.txt` (ok)  
**Previo:** [`udemy-L17-monitoring-2026-07-27.md`](./udemy-L17-monitoring-2026-07-27.md)

---

## 0. Veredicto

L17 = **observabilidad**: no bastan logs; hace falta jerarquía session → trace → spans (tools, LLM, handoffs, guardrails).  
Firma: doble capa — (1) traces OpenAI (`RunConfig workflow_name=firma-juridica`) (2) traza propia (Workflow Trace, desk soporte, `/debug/trace`, tokens en hooks).  
Productizar costos = convertir tokens de traza en **$/turno** (B04). Sin Datadog/Langfuse obligatorio.

---

## 1. Qué enseña el curso

- Logs solos no explican fallo en loop async/parallel.  
- Tracing **on by default** → OpenAI Traces dashboard.  
- Jerarquía: **session** (conversación) → **trace** (un run) → **spans** (subpasos).  
- Agrupar runs: `trace()` + `workflow_name` + `group_id`.  
- Spans custom: decorator.  
- Third-party: processors nativos (Datadog, Langfuse…) o custom.  
- `draw_graph` para dibujar topología multi-agent.  
- Apagar: `set_tracing_disabled` / env.

---

## 2. Traducción firma virtual

### Negocio
Soporte debe responder: ¿qué tool falló?, ¿cuántos tokens?, ¿se disparó guardrail?, ¿hay draft HITL? — **sin** reabrir el expediente completo ni filtrar PII a Sentry.

### Mapa

| Curso | Aquí |
|---|---|
| OpenAI Traces | `RunConfig(workflow_name="firma-juridica", group_id=session_id)` · plan steps `firma-plan-step` |
| Session → traces | `chat_sessions` + `SessionTrace` / list traces |
| Spans / actions | `trace.spans`, `trace.actions`, hooks LLM/tool |
| Usage / costo | `trace.completion` (hooks) — base de **B04** |
| Local “REPL” prod | Workflow Trace UI + desk soporte + `GET /debug/trace/{session_id}` |
| Third-party | Sentry opcional (`SENTRY_DSN`, sample 0.05) — **falta scrub 1581** → **B15** |
| draw_graph | No crítico; organigrama en docs/código |

---

## 3. High-level

> **DEJAR QUIETO** la doble traza (OpenAI + propia). Ya productiza ops básica.  
> Batch: **B04** $/turno en soporte/export · **B07** budget visible · **B15** Sentry `before_send` scrub PII.  
> No Datadog “porque el curso”. No subir sample Sentry sin scrub. No mandar cuerpos de expediente a terceros.

| Ítem | Acción | Backlog |
|---|---|---|
| RunConfig + traza propia | Mantener | — |
| Desk / debug trace | Mantener | — |
| $/turno desde completion | UI/export | **B04** |
| Budget excedido visible | Desk | **B07** |
| Sentry scrub 1581 | `main.py` before_send | **B15** |
| Langfuse/Datadog | Solo si ya hay licencia | Could |

---

## 4. Costos / productizar

L17 cierra el circuito de forecast:

```text
tokens en trace.completion × precio modelo → $/turno → B06 doc comercial
```

Sin esto, B01/B13 se tunan a ciegas. Observabilidad = palanca de **margen** y de **confianza** en demos.

---

## 5. Qué NO hacer

- Expediente crudo a Sentry.  
- Sample rate alto sin scrub.  
- Apagar tracing OpenAI sin capa propia equivalente.  
- Sustituir desk propio solo por dashboard OpenAI (PII/casos).

---

## Cierre

Siguiente pedagógica: **L18–L20 Voice** (esperado **DIFERIR** 1581/2300). Luego sandbox L21–L27 y Bedrock L28 (diferir).
