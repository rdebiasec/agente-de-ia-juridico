# Udemy L08 — RunResult and REPL — 2026-07-27

**Fase:** AUDITORIA_ANTES  
**Prioridad:** P0 · Oleada A

---

## 1. Checklist Antes / Después

| Ítem | Antes | Después propuesto | Decisión / por qué | Evidencia |
|---|---|---|---|---|
| Inspección RunResult | `final_output`, `last_agent`, `interruptions`, `new_items` (tools/handoffs) | Checklist smoke formal + más detalle en soporte | Curso: RunResult > texto final | `runner.py` |
| Usage | Vía hooks `on_llm_end`, no `result.context_wrapper.usage` | Documentar; opcional alinear a API SDK | Consistencia debug | `_TraceRunHooks` |
| UI Workflow Trace | `static/chat.js` spans + response/request ids | Exponer árbol de tool items si falta | Abogado/ops ve el camino | `chat.js`, `desk-soporte.js` |
| Debug API | `GET /debug/trace/{session_id}` (web) | Mantener auth; no filtrar PII extra | REPL mental del curso = estas APIs | `main.py` |
| raw_responses | No expuesto en UI | Solo si hace falta forensics; default no | Evitar dump masivo sensible | — |

---

## 2. Relevancia al producto abogado

- Explica *por qué* el gerente pidió un dato o invocó un especialista.
- Facilita QA de HITL (interruptions visibles).

## 3. Qué NO hacer

- No volcar `raw_responses` completos a logs públicos.
- No construir un REPL local que use datos reales de clientes.

## 4. PASS / FAIL

| Verificación | PASS | FAIL | Resultado |
|---|---|---|---|
| Workflow Trace en chat | Spans visibles post-turno | Sin traza | Revalidar smoke |
| Interruption HITL | Aparece en traza | Invisible | Pendiente checklist |

## 5. Pendiente humano

- «aprobado, ejecuta» L08 para mejoras de exposición UI/API.

## 6. Estado tras esta pasada

**Sin cambio de código.** Capacidad base presente; falta formalizar smoke RunResult.
