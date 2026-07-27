# Udemy L11 — Guardrails and Human Review — 2026-07-27

**Fase:** AUDITORIA_DESPUES  
**Prioridad:** P0 · Oleada A  
**Estado:** HECHO (código)

---

## 1. Checklist Antes / Después

| Ítem | Antes | Después | Decisión / por qué |
|---|---|---|---|
| Fallo al crear borrador HITL | `except` → `None` en silencio; traza decía `pending` igual | Traza `draft_created`/`human_review` = `blocked` si no hay draft | El abogado no debe creer que hay cola si no hay |
| Citas sin `[PENDIENTE]` en chat POC | No se reportaban en `poc_output_guardrail` | Soft flag `invention_suspect` + `pending_markers_count` | Auditable; no tripwire (HITL revisa) |
| `has_disclaimer` en guardrail | Siempre False (se mide antes del disclaimer) | Quitado del output_info; se mide en traza final | Evita telemetría mentirosa |
| `require_tool_approval` en chat | `True` pero sin tools de alto riesgo | `False` + comentario | HITL de alto riesgo = plan, no interruptions |
| Prueba del loop | Solo piezas sueltas | `tests/test_l11_hitl.py` | Demuestra borrador real en repo |

## 2. PASS / FAIL

| Verificación | Resultado |
|---|---|
| `tests/test_l11_hitl.py` (3) | PASS |
| Redacción web → `draft_id` + estado propuesto/en_revision | PASS |
| Consulta fuera de alcance → sin draft | PASS |
| Cita sin pendiente → `invention_suspect` | PASS |

## 3. Pendiente humano

- Slack HITL en Render (`SLACK_APP_TOKEN` / approvers) — ops, no código.

## 4. Archivos tocados

- `src/agents/runner.py`
- `src/agents/sdk_guardrails.py`
- `config/guardrails/agents/coordinador_expediente_penal/output.md`
- `tests/test_l11_hitl.py` (nuevo)
