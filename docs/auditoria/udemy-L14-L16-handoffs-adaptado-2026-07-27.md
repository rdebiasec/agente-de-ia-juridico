# Udemy L14 + L16 — Handoffs / Lab multi-agents (adaptado) — 2026-07-27

**Fase:** AUDITORIA_ANTES  
**Prioridad:** P1 · Oleada B  
**Tipo:** adaptación documental (no portar labs)

---

## 1. Checklist Antes / Después

| Ítem | Antes | Después propuesto | Decisión / por qué | Evidencia |
|---|---|---|---|---|
| Handoffs peer | No hay `handoffs=` en el Agent del coordinador | **No implementar handoffs peer** | Una sola voz de despacho; decisión de producto | `orchestrator.py`, `ESTADO_PROYECTO.md` |
| Orquestación | `plan_templates.py` + `as_tool` + depends_on | Mantener cadenas por plantilla | Equivalente seguro al “triage-orchestrator” del curso | `plan_templates.py` |
| Lab L16 | Curso combina handoffs + as_tool | Solo tomar: ownership de respuesta + trazabilidad de pasos | Portar el lab rompería firma virtual | transcripts L16 (gitignored) |
| Defensa residual | `_ensure_poc_voice` por si filtra voz de especialista | Mantener | Cinturón y tirantes | `runner.py` |

---

## 2. Relevancia al producto abogado

- El litigante siempre habla con el “despacho”, no con 10 agentes.
- Planes aprobables paso a paso = HITL claro.

## 3. Qué NO hacer

- No copiar el lab de handoffs “para completar el curso”.
- No exponer especialistas como caras en Slack/web.

## 4. PASS / FAIL

| Verificación | PASS | FAIL | Resultado |
|---|---|---|---|
| Payload chat | `agent` = POC | Cara de especialista | Ya diseño PASS |
| Plan incompleto | Sin especialistas | Especialista invocado | Ya PASS gerente |

## 5. Pendiente humano

- Ninguno de código. Confirmar que la decisión “sin handoffs peer” permanece.

## 6. Estado tras esta pasada

**Sin cambio de código.** L14/L16 cerradas como **adaptación**: concepto del curso → planes + as_tool.
