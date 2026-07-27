# Udemy L07 — Run Loop — 2026-07-27

**Fase:** AUDITORIA_ANTES  
**Prioridad:** P1 · Oleada B

---

## 1. Checklist Antes / Después

| Ítem | Antes | Después propuesto | Decisión / por qué | Evidencia |
|---|---|---|---|---|
| Chat web | `async` + `Runner.run` (no streamed); respuesta completa | Mantener por defecto; evaluar streaming solo si latencia percibida duele | Simplicidad HITL/debug | `runner.py`, `main.py` `/chat` |
| Planes aprobados | SSE `text/event-stream` + `PlanEventBroker` | Mantener | Ya da feedback de pasos largos | `plan_executor.py`, `/chat/plan/{id}/execute` |
| Retries / timeout | `run_with_retries`, fallback model, budget watchdog | Mantener | Resiliencia del loop | `runner.py` |
| Fallback sin API key | `_fallback_response` determinista | Mantener | Degrada en vez de 500 | mismo |

---

## 2. Relevancia al producto abogado

- Chat predecible para revisión humana.
- Planes largos ya streamean progreso.

## 3. Qué NO hacer

- No activar `run_streamed` en chat sin diseño de cancelación/HITL parcial.
- No mezclar streaming de chat con approval de plan a medias.

## 4. PASS / FAIL

| Verificación | PASS | FAIL | Resultado |
|---|---|---|---|
| `/chat` | Respuesta completa | Hang sin timeout | Revalidar |
| Execute plan SSE | Eventos step_* | Silencio | Revalidar |

## 5. Pendiente humano

- Decidir si se quiere streaming en chat (producto); si no, cerrar L07 como HECHO documental.
- «aprobado, ejecuta» solo si se pide streaming.

## 6. Estado tras esta pasada

**Sin cambio de código.** Decisión provisional: chat no-streamed es correcto para firma virtual.
