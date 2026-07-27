# Udemy L12 — Session Management — 2026-07-27

**Fase:** AUDITORIA_ANTES  
**Prioridad:** P1 · Oleada B

---

## 1. Checklist Antes / Después

| Ítem | Antes | Después propuesto | Decisión / por qué | Evidencia |
|---|---|---|---|---|
| Session SDK | `RepositoryAgentSession(SessionABC)` pasada a `Runner.run` | Mantener | Continuidad multi-turno idiomática | `gateway/agent_session.py` |
| Compactación | Resume turnos viejos en item sintético no persistido | Revisar umbrales `session_recent_messages` | Evita contaminación y costo | mismo |
| Límites de tarea | Sesión atada a expediente vía bind | Reforzar reset chat al cambiar caso | Evita cruzar contextos | `POST /chat/reset` |
| Memoria vs prompt | Historial en session store + bloque expediente | No duplicar hechos sensibles innecesariamente | Curso: boundaries explícitos | `runner.py` context_block |

---

## 2. Relevancia al producto abogado

- Conversación coherente sobre el mismo expediente.
- Menos repetición de hechos ya aportados.

## 3. Qué NO hacer

- No mezclar sesiones de dos radicados distintos.
- No persistir el resumen sintético como “hecho probado”.

## 4. PASS / FAIL

| Verificación | PASS | FAIL | Resultado |
|---|---|---|---|
| Multi-turno | Recuerda datos del turno previo | Amnesia | Revalidar |
| Reset | Limpia sesión | Arrastra historial | Revalidar |

## 5. Pendiente humano

- «aprobado, ejecuta» L12 si se ajustan umbrales de compactación.

## 6. Estado tras esta pasada

**Sin cambio de código.** Base alineada con la lección.
