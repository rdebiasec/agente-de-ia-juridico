# Udemy L04 — Model Settings — 2026-07-27

**Fase:** AUDITORIA_ANTES  
**Prioridad:** P0 · Oleada A

---

## 1. Checklist Antes / Después

| Ítem | Antes | Después propuesto | Decisión / por qué | Evidencia |
|---|---|---|---|---|
| Selección de modelo | `_model_for_agent`: high-risk → `openai_model_high_risk`, resto `openai_model` | Mantener estratificación; documentar en Settings | Ya alinea costo a riesgo | `orchestrator.py`, `config.py` |
| ModelSettings | Ausente en `Agent(...)` | Añadir temp baja / límites por rol (gerente, redactor, calidad) | Determinismo jurídico; lección del curso | — |
| Temperature prod | Solo en validation/evals | Temp baja explícita en redacción/calidad | Menos creatividad en textos legales | `validation/report.py`, `probes.py` |
| Presupuesto | Tokens/turns/timeouts en settings + hooks | Mantener watchdog; complementar con ModelSettings | Costo no solo por modelo | `runner.py` `_TraceRunHooks` |

---

## 2. Relevancia al producto abogado

- Redacciones más estables y revisables.
- Costo predecible por tipo de actuación.

## 3. Qué NO hacer

- No subir temperatura “para respuestas más naturales” en redactor/tutela.
- No usar WebSocket solo porque el curso lo menciona (chat HTTPS basta).

## 4. PASS / FAIL

| Verificación | PASS | FAIL | Resultado |
|---|---|---|---|
| High-risk usa modelo fuerte | `gpt-4o` (o setting) | Mini en tutela/redactor | Revalidar |
| Temp redactor | ≤ valor acordado | Default creativo | Pendiente impl |

## 5. Pendiente humano

- Acordar valores (temp / reasoning_effort) por rol.
- «aprobado, ejecuta» L04.

## 6. Estado tras esta pasada

**Sin cambio de código.** Hueco más claro de Oleada A vs currículo.
