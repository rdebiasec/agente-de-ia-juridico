# Udemy L13 — Session Management on Production — 2026-07-31 (clase formal)

**Fase:** HECHO_CLASE  
**Orden pedagógico:** #16  
**Decisión global:** DEJAR QUIETO (Postgres BYOS ya prod) · **B14** Should = clarificar idle vs retención/HITL  
**Batch:** Must sin cambio; B14 ops/política (no reescribir store)  
**Fuente:** `txt/13_session_management_on_production.txt` (ok)  
**Previo:** [`udemy-L13-sessions-prod-2026-07-27.md`](./udemy-L13-sessions-prod-2026-07-27.md)

---

## 0. Veredicto

L13 = pasar de SQLite / Conversation ID a **tu motor durable** (SQLAlchemy → Postgres/MySQL), con residencia, retención, cifrado y escala horizontal.  
Firma: **ya está en el destino del curso** — `RepositoryAgentSession` + Postgres en Render; retención 1581 + ARCO.  
No migrar “hacia atrás” a Conversation ID. Gap menor: **idle UI (60 min)** vs **retención años** vs **no borrar drafts HITL** — documentar/endurecer política (**B14**).

---

## 1. Qué enseña el curso

### Problemas de SQLite en prod
Replicación multi-server, multi-región, cifrado, retention policies → ops pesada.

### Camino típico del curso
1. Empezar SQLite o Conversations API.  
2. Migrar conexión del agent (fácil) — migración de datos fuera de scope.  
3. SQLAlchemy session → endpoint Postgres/MySQL en tu VPC.  
4. Opcional: encrypted session + rotación de keys.  
5. Custom SessionABC (get/add/clear) solo si NoSQL y vale la pena.

### Cuándo Conversations API no basta
Data residency / VPC / flota DB propia / retention nativa del engine.  
Retention OpenAI: response chaining ~30 días; Conversations API = vos borrás.

Default curso: Conversations API → BYO SQLAlchemy si compliance lo exige → custom solo si hace falta.

---

## 2. Traducción firma virtual

### Negocio
Tras deploy/reinicio, el chat del expediente **sigue**. Retención y ARCO alineados a Ley 1581. Idle de pantalla ≠ “borrar el caso”. Planes huérfanos se recuperan; no confundir con idle de chat.

### Mapa

| Curso | Aquí |
|---|---|
| SQLAlchemy / BYO Postgres | `storage/sql.py` + `RepositoryAgentSession` (custom SessionABC — ya “paso 5” con Postgres) |
| Multi-instance / Render | Postgres managed; no SQLite file |
| Retention policies | `compliance/policy.py` chat 5y / audit 3y; `purge_expired_data` + `scripts/purge_retention.py` |
| ARCO delete | `POST /api/compliance/arco-erase` · runbook 1581 |
| Idle | `session_idle_minutes=60` → UI/auth; **no** es purge de historial |
| Stale recovery planes | `plan_stale_after_seconds=300` · `recover_stale_executions` |
| Encrypted session SDK | TLS a Postgres + controles hosting; no wrapper encrypted-session del lab |
| Conversations API OpenAI | No como store primario de casos |

Runbook: [`docs/operaciones/RUNBOOK_CUMPLIMIENTO_1581.md`](../operaciones/RUNBOOK_CUMPLIMIENTO_1581.md).

---

## 3. Tres relojes (no confundir)

| Reloj | Valor típico | Efecto |
|---|---|---|
| Idle UI/auth | 60 min | Aviso / sesión web; **no** borra chat del expediente |
| Plan stale | 300 s | Reclaim ejecución huérfana |
| Retención 1581 | 5y chat / 3y audit | Job purge + ARCO |

**Regla producto:** no purge automático de sesión con borrador HITL pendiente sin política explícita (hoy retención es por antigüedad larga + ARCO).

---

## 4. High-level

> **DEJAR QUIETO** el store (Postgres + SessionABC). Ya cumplís el “prod” del curso mejor que SQLite/Conversations para datos de casos.  
> **B14** Should: documentar en ops/UI que idle ≠ borrado; checklist “no borrar con HITL pendiente”; opcional smoke del job `purge_retention` dry-run.  
> No Conversation ID OpenAI como primary. No SQLite lab en Render.

| Ítem | Acción | Backlog |
|---|---|---|
| Postgres sessions | Mantener | — |
| Retención + ARCO + runbook | Mantener | — |
| Clarificar idle vs retención / HITL | Ops + copy UI | **B14** |
| EncryptedSession wrapper curso | No obligatorio | — |

---

## 5. Costos / productizar

- BYO Postgres: control + compliance = **productizable** frente a Conversations API con casos.  
- Retención finita: menos storage a largo plazo; ARCO = requisito comercial Colombia.  
- Idle corto que **borrara** chat = pérdida de trabajo abogado (anti-productizar).  
- Plan stale recovery: evita planes colgados sin re-gastar runs a ciegas.

---

## 6. Qué NO hacer

- SQLiteSession en prod.  
- Borrar sesiones con drafts pendientes “porque idle=60”.  
- Meter historial de casos solo en OpenAI Conversations.  
- Confundir reclaim de plan con idle de chat.

---

## Cierre

Siguiente: **L17 — Monitoring**.
