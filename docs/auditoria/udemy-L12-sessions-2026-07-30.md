# Udemy L12 — Session Management — 2026-07-30 (clase formal)

**Fase:** HECHO_CLASE  
**Orden pedagógico:** #15  
**Decisión global:** DEJAR QUIETO (base prod ya propia) · opcional tunear compactación (**B13**)  
**Batch:** Must sin cambio; **B13** Should = revisar umbrales compactación (costo)  
**Fuente:** `txt/12_session_management.txt` (ok)  
**Previo:** [`udemy-L12-sessions-2026-07-27.md`](./udemy-L12-sessions-2026-07-27.md)

---

## 0. Veredicto

L12 = el runner **no recuerda** solo; hay que elegir estrategia de historial.  
Curso: 4 estrategias (replay local, SQLite, Conversation ID OpenAI, previous response ID) + session vs context.  
Firma: **SessionABC propia** (`RepositoryAgentSession`) sobre Postgres/`chat_sessions` + compactación + reset — no SQLite del lab ni Conversation ID de OpenAI como store primario (datos de casos / control).

---

## 1. Qué enseña el curso

### Por qué olvida
Cada `Runner.run` sin session = amnesia (turno 1 “soy Alex”; turno 2 “¿cómo me llamo?” → no sabe).

### 4 estrategias
| Estrategia | Idea | Curso recomienda |
|---|---|---|
| Local replay | JSON de mensajes en el input | Solo debug / Redis-like casero |
| SQLite session | DB local + key | Dev; ops pesada en prod |
| Conversation ID | Historial hosted OpenAI | Default curso prod |
| Previous response ID | Encadenar Responses API | Ephemeral / corto |

Claves SQLite: tenant + user + thread. Historial largo → overflow context, peor accuracy, **más $** → nuevas conversaciones / keys frescas.

### Session vs context (crítico)
- **Session** = memoria que el **modelo debe ver** (chat history).  
- **Context** (`RunContext`) = DI para tools (ids, flags) — **no** secrets al modelo.  
No mezclar.

También menciona workspace/sandbox memory (archivos) → más L24/L25.

---

## 2. Traducción firma virtual

### Negocio
El abogado sigue el **mismo expediente** en varios mensajes sin repetir hechos. Si cambia de caso, **reset**. No mezclar radicados. El resumen compactado **no** es hecho probado.

**Ejemplo:** Turno 1 aporta hechos del hurto → turno 2 “ahora tipicidad” usa historial + bloque expediente, no amnesia.

### Mapa

| Curso | Aquí |
|---|---|
| Session en Runner | `RepositoryAgentSession` → `Runner.run(session=…)` |
| Store | Postgres `chat_sessions` (no SQLite lab; no Conversation ID OpenAI como primary) |
| Key | `session_id` (+ canal/user); atado a expediente vía bind (L05/L13) |
| Compactación | `compact_session_items` — últimos N + resumen sintético **no persistido** |
| Clear / new thread | `POST /chat/reset` |
| Session vs context | Historial session ≠ context_block expediente/RAG ≠ RunContext tipado (B02) |
| Inspect items | Repo + Workflow Trace |

Defaults: `session_recent_messages=16`, `session_max_messages`, `session_summary_max_chars` en `config.py`.

---

## 3. High-level

> **DEJAR QUIETO** la arquitectura de sesión. Ya es productizable (Postgres + SessionABC + compact + reset).  
> No migrar a Conversation ID OpenAI para historial de casos (control/1581).  
> Opcional batch: tunear umbrales de compactación si el $/turno de historial duele (**B13**).  
> Idle/retención/prod → **L13**.

| Ítem | Acción | Backlog |
|---|---|---|
| RepositoryAgentSession | Mantener | — |
| Compactación + no persistir resumen | Mantener | — |
| `/chat/reset` | Mantener | — |
| Tunear N mensajes / chars resumen | Medir tokens | **B13** Should |
| Conversation ID OpenAI como store | No | Won’t (casos) |

---

## 4. Costos / productizar

- Sin compactación: historial infinito → tokens ↑ cada turno.  
- Compactación: baja input tokens; resumen no es prueba jurídica.  
- Reset al cambiar caso: evita contaminación (riesgo + tokens basura).  
- Productizar memoria = continuidad **por expediente**, no “un chat eterno”.

---

## 5. Qué NO hacer

- Mezclar dos radicados en una session.  
- Tratar el resumen sintético como hecho probado.  
- Meter API keys en session (van a context, y ni ahí en claro — L05).  
- Portar SQLite lab a Render como store primario.

---

## Cierre

Siguiente: **L13 — Session Management on Production** (idle, retención, 1581).
