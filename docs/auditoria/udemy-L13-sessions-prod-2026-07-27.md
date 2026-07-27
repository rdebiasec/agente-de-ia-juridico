# Udemy L13 — Session Management on Production — 2026-07-27

**Fase:** AUDITORIA_ANTES  
**Prioridad:** P1 · Oleada B

---

## 1. Checklist Antes / Después

| Ítem | Antes | Después propuesto | Decisión / por qué | Evidencia |
|---|---|---|---|---|
| Persistencia | Postgres `chat_sessions` (dev==prod) | Mantener | Lección: storage durable | `storage/sql.py`, `render.yaml` |
| Idle | `session_idle_minutes=60` expuesto a UI; sin borrado server-side | Definir política: warning UI vs purge/retención 1581 | Gap vs “production session design” del curso | `config.py`, `main.py` |
| Stale recovery | Planes `executing` huérfanos reclaim 300s | Mantener; no confundir con idle de chat | Recuperación operativa distinta de chat idle | `plan_executor.py` |
| Observabilidad sesión | Traces por `session_id` | Enlazar métricas idle/stale | Recovery y forensics | `SessionTrace` |

---

## 2. Relevancia al producto abogado

- Sesiones no se “pierden” entre deploys.
- Retención alineable a ARCO/1581.

## 3. Qué NO hacer

- No borrar sesiones con borradores HITL pendientes sin aviso.
- No usar SQLiteSession local en producción.

## 4. PASS / FAIL

| Verificación | PASS | FAIL | Resultado |
|---|---|---|---|
| Persistencia prod | `persistencia: postgres` | memory | Ya PASS en cierre gerente |
| Idle policy | Documentada + aplicada | Solo UI | Gap documentado |

## 5. Pendiente humano

- Definir retención/ARCO vs idle purge.
- «aprobado, ejecuta» L13 para idle server-side si se aprueba política.

## 6. Estado tras esta pasada

**Sin cambio de código.** Durabilidad OK; lifecycle idle incompleto.
