# Udemy L07 — Run Loop — 2026-07-28 (clase formal, profundidad producto)

**Fase:** HECHO_CLASE  
**Orden pedagógico:** #7  
**Decisión global:** DEJAR QUIETO (chat completo async; SSE solo en planes)  
**Comando código:** no hace falta salvo que producto pida streaming de chat

---

## 0. Veredicto

L07 es el **ciclo de vida** de una corrida: razonar → tools → respuesta (y a veces otra vuelta).  
En tu firma hay **dos run loops de producto**, no uno:

1. **Chat del Gerente** — `Runner.run` async, respuesta **completa** (no stream de tokens).  
2. **Plan aprobado** — varios pasos, cada uno con su run, progreso por **SSE**.

Eso no es casualidad: el abogado revisa mejor un bloque cerrado; los planes largos sí necesitan “sigue vivo” en la UI.

---

## 1. Qué enseña el curso (L07)

Del KB Udemy:

- El run loop es el corazón: razonamiento, tool calls, respuesta.  
- Modos: sync / async / streaming — eliges por UX y costo.  
- Cada iteración es un “round” con estado (tools, a veces handoffs).  
- La continuidad conversacional depende de **cómo persistís** entre llamadas.  
- El modo de run define latencia y complejidad de integración.

**Traducción despacho:** no es “hacer streaming porque queda cool”; es decidir si el litigante espera un memo cerrado o un ticker de pasos.

---

## 2. Anatomía del loop en ESTE producto

### 2.1 Antes del LLM (código — ya lo viste con triage)

Orden fijo en `run_agent`:

1. Validación de entrada  
2. Sync expediente / historial  
3. Triage determinista  
4. Pre-validaciones  
5. Gate alto riesgo → plan (a veces **sin** entrar al loop LLM)  
6. Armado de `context_block` (triage + expediente + RAG)  
7. `build_orchestrator` (superficie de tools)  
8. **Recién ahí** `Runner.run(...)`

Eso significa: el “run loop” del SDK es solo el núcleo caro; el producto lo envuelve con gates de bufete.

### 2.2 Dentro del SDK (`Runner.run`)

En chat (`runner.py`):

```text
bind_active_session(session_id)
  → run_with_retries(
       Runner.run(
         orchestrator,          # POC + tools
         agent_input,           # triage + expediente + mensaje
         session=agent_session, # multi-turno Postgres
         max_turns=…,           # tope de vueltas internas
         hooks=…,               # traza / usage / budget
         run_config=…,          # workflow_name firma-juridica
       ),
       timeout + retries + fallback_model opcional
     )
```

Cada “turno interno” del SDK puede:

- generar texto,  
- llamar un `as_tool` (especialista),  
- volver a razonar,  
- hasta `agent_max_turns` (default 10) o tripwire/budget.

**No** usáis handoffs peer: el “cambio de agente” es tool call anidado, y la cara al abogado sigue siendo el POC (`_ensure_poc_voice`).

### 2.3 Después del LLM

- Interruptions (si hubiera needs_approval — en chat high-risk tools están off)  
- `final_output` → post-validaciones / PII / disclaimer  
- HITL draft si `needs_human_review`  
- Persistencia mensajes + traza  

### 2.4 Loop de plan (segundo producto)

Tras aprobar plan:

- `plan_executor` ejecuta pasos en serie (depends_on),  
- cada paso = otro `Runner.run` (a menudo especialista o POC),  
- UI escucha **SSE** (`PlanEventBroker`, `text/event-stream`) con eventos de paso.

Ahí sí hay “streaming de producto”: no tokens del modelo, sino **progreso de workflow**.

---

## 3. Modos de ejecución — decisión de firma virtual

| Modo curso | ¿Lo usáis? | Dónde | Por qué |
|---|---|---|---|
| Sync bloqueante | No en web | — | FastAPI es async |
| Async `Runner.run` completo | **Sí** | `/chat` | Respuesta revisable de una pieza; debug/HITL más simple |
| `run_streamed` tokens | **No** (hoy) | — | Cancelación + HITL parcial + “medio memorial en pantalla” = riesgo UX/jurídico |
| Stream de eventos de plan | **Sí** | execute plan SSE | Planes largos sin “pantalla congelada” |

**Visión de experto:** en despacho, el chat es una **consulta con respuesta**. El plan es un **workflow**. Mezclar streaming de tokens del chat con aprobación humana a medias suele generar:

- el abogado lee un borrador a medias y cree que ya “salió”,  
- o cancela a mitad y el estado queda ambiguo.

Por eso L07 en este producto = **mantener la dualidad actual**.

---

## 4. Continuidad entre turns (memoria del loop)

El loop no es solo una llamada:

| Capa | Mecanismo | Rol |
|---|---|---|
| Sesión SDK | `RepositoryAgentSession` | Historial para el modelo |
| DB | `chat_sessions` | Sobrevive deploy |
| Expediente | sync + resumen | Grounding del caso |
| Triage por turno | `build_triage` cada mensaje | Re-etiqueta sin LLM |
| Traza | spans + actions | Ops / soporte |

L07 conecta con L12/L13 (sesiones) y L05 (context tipado): el loop **consume** esa continuidad.

---

## 5. Resiliencia del loop (lo que el curso a veces resume)

En vuestro runner no es un `try/except` pobre:

- **Timeout** por corrida (`agent_run_timeout_seconds`)  
- **Retries** (`agent_max_retries`) con span en traza  
- **Fallback model** opcional en reintento (sin contaminar cache del Agent)  
- **Non-retryable:** tripwires de guardrail y budget  
- **Sin API key:** loop ni empieza; fallback determinista  

Eso es run-loop de **producción jurídica**, no de notebook.

---

## 6. Relación con hops de “denuncia de robo”

Recordatorio alineado a L07:

1. Código pre-loop (triage, gates).  
2. Si “redacte denuncia” → **no hay run loop LLM** en ese turno; mensaje de plan.  
3. Si “ordenar hechos / tipicidad” → entra el loop: POC ↔ tools hasta `final_output`.  
4. Si luego aprueba plan → **varios** loops (uno por paso) + SSE.

El “run loop” no es un solo círculo: es **familia de corridas** gobernada por el producto.

---

## 7. Qué cambiar / no cambiar

Ver también [`UDEMY_LISTA_CAMBIOS.md`](./UDEMY_LISTA_CAMBIOS.md) sección L07.

### Cambiar

| Qué | Por qué | Estado |
|---|---|---|
| — obligatorio | Chat no-streamed + SSE planes ya es la decisión correcta de firma | N/A |
| (Opcional) streaming de chat | Solo si latencia percibida duele **y** hay diseño de cancelación/HITL parcial | pendiente demanda producto |

### No cambiar

| Qué | Por qué |
|---|---|
| `Runner.run` completo en `/chat` | Respuesta cerrada = mejor para revisión |
| SSE en execute plan | Feedback de pasos largos |
| Retries / timeout / fallback | Resiliencia |
| Activar `run_streamed` “porque L07” | Complejidad y riesgo HITL |
| Handoffs dentro del loop | Rompe una voz |

---

## 8. High-level config

> **Para L07: DEJAR QUIETO.**  
> El despacho ya tiene el run loop correcto: chat async de respuesta completa; planes con SSE de progreso; retries y topes.  
> No actives streaming de tokens en chat sin un diseño explícito de cancelación y de “qué ve el abogado a medias”.  
> Si algún día el desk se siente “colgado” en consultas largas no-plan, entonces evaluamos streaming — como decisión de producto, no como deber del curso.

---

## 9. Criterio PASS (smoke mental)

| Caso | PASS |
|---|---|
| `/chat` consulta tipicidad | Respuesta completa; traza con spans runner |
| `/chat` “redacte memorial” | Sin loop LLM de redacción; pide plan |
| Execute plan | Eventos SSE de pasos |
| Sin API key | Fallback, no 500 eterno |
| Tripwire input | No reintenta en loop infinito |

---

## 10. Encaje en el camino pedagógico

| Lección | Aporta al loop |
|---|---|
| L01–L06 | Qué Agent corre |
| L03 | Forma de salidas de tools dentro del loop |
| L04 | Costo/calidad del modelo en cada vuelta |
| L05 | Carpeta tipada durante el run |
| **L07** | **Cómo se ejecuta y se percibe el turno** |
| L08 (siguiente) | Cómo inspeccionar el `RunResult` del loop |

---

## Cierre

Siguiente: **L08 RunResult** (más que el texto final: tools, interruptions, last_agent).
