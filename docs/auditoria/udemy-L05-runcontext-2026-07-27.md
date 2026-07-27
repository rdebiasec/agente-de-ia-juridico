# Udemy L05 — RunContext and RunContextWrapper — 2026-07-27

**Fase:** AUDITORIA_ANTES  
**Prioridad:** P0 · Oleada A

---

## 1. Checklist Antes / Después

| Ítem | Antes | Después propuesto | Decisión / por qué | Evidencia |
|---|---|---|---|---|
| Context tipado SDK | No se pasa `context=` a `Runner.run`; wrapper suele envolver `None` | Introducir dataclass (`session_id`, `expediente_id`, `channel`, `user_id`, flags 1581) | DI tipada del curso; tools/guardrails dejan de depender solo de ContextVar | `runner.py`, `session_context.py` |
| Anti-IDOR | `resolve_expediente_id` + `bind_active_session` | Mantener y enlazar al nuevo context | Defensa ya correcta; hay que tiparla | `session_context.py` |
| Untrusted context | `wrap_untrusted_context` + flags en traza | Seguir; no meter secretos en prompt | Separar estado app vs texto modelo | `context_security.py` |
| Consentimiento 1581 | `compliance/consent.py` separado | No mezclar consentimiento en RunContext del modelo | Consentimiento es gate de canal, no tool state | `src/compliance/consent.py` |

---

## 2. Relevancia al producto abogado

- Evita lecturas cruzadas de expedientes.
- Grounding estable sin filtrar datos sensibles al modelo por accidente.

## 3. Qué NO hacer

- No poner API keys, tokens Slack ni PII cruda en el context visible al modelo.
- No romper ContextVar hasta que `context=` esté cableado en tools.

## 4. PASS / FAIL

| Verificación | PASS | FAIL | Resultado |
|---|---|---|---|
| Tool pide otro expediente | Se ignora; usa activo | Lee otro caso | Hoy PASS vía ContextVar; revalidar tras tipado |
| Guardrail ve canal/session | Tipado disponible | Sigue `None` | Pendiente impl |

## 5. Pendiente humano

- «aprobado, ejecuta» L05 para introducir dataclass + wiring.

## 6. Estado tras esta pasada

**Sin cambio de código.** Gap idiomático del SDK claramente identificado.
