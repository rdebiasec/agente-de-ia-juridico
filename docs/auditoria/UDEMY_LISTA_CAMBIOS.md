# Udemy → producto — lista de mejoras (productizar + costos)

**Producto:** firma virtual · asistente de abogados (penal-víctimas)  
**Orden de clases:** pedagógico ([`PLAN_UDEMY_CORTO.md`](../canon/PLAN_UDEMY_CORTO.md))  
**Ejecución de código:** **batch al final** de la serie (no `aprobado, ejecuta` por lección).  
**No** crear un archivo por lección.

Leyenda estado: `pendiente` · `hecho` · `N/A` · `diferir` · `clase pendiente`

---

## Cómo leer este documento

1. **Backlog de productización** (arriba) — lo que importa para vender/operar/costear; se implementa al final.  
2. **Progreso de clases** — qué lecciones ya cerramos.  
3. **Por lección** (abajo) — detalle Cambiar / No cambiar / por qué (auditoría).

Criterios de priorización del backlog:

| Criterio | Pregunta |
|---|---|
| Productizar | ¿Reduce riesgo jurídico, fricción del abogado o trabajo de ops? |
| Costo | ¿Baja tokens/errores caros, o solo añade gasto? |
| Esfuerzo | S ≤ 0.5 d · M 0.5–2 d · L > 2 d (1 dev familiarizado) |
| $/mes | Estimación **orientativa** tras medir tokens (L17); hoy = orden de magnitud |

---

## BACKLOG FINAL — productizar + estimar costos

> Implementar **solo** cuando digas que cerramos el batch (tras terminar las clases que falten, o cuando lo indiques).  
> Las clases siguen; este backlog se **enriquece** al cerrar cada lección.

### A) Must — productización (hacer en el batch)

| ID | Mejora | Lección | Dónde | Productiza | Efecto costo | Esf. | Est. costo* | Estado |
|---|---|---|---|---|---|---|---|---|
| B01 | `ModelSettings` temp baja en redactor / tutela / calidad | L04 | `orchestrator.py` | Memoriales/tutelas más estables; menos re-trabajo HITL | **Baja** retries y reescrituras (tokens high-risk ~`gpt-4o`) | S | Ahorro neto si baja 10–20% re-runs high-risk | pendiente |
| B02 | Dataclass RunContext + `Runner.run(..., context=)` | L05 | `runner.py`, `plan_executor.py`, tipo nuevo | Anti-IDOR tipado; tools/guardrails listos para prod multi-tenant | Neutro tokens; evita incidente de fuga (costo reputacional) | M | Costo eng. único; riesgo $ incidente >> eng. | pendiente |
| B03 | Enlazar `resolve_expediente_id` al context tipado | L05 | `session_context.py` + tools | Misma defensa IDOR, idiomática SDK | Neutro tokens | S–M | Incluido en B02 | pendiente |
| B04 | Panel/ops: costo por turno (tokens in/out × precio modelo) | L08→L17 | hooks → `trace.completion` + UI soporte o export | **Estimar costos** reales por consulta/plan | Neutro (solo lectura); habilita control de gasto | M | Sin él no hay forecast serio | pendiente (parcial hoy: tokens en traza) |
| B05 | Smoke productización: chat tipicidad + plan HITL + traza tokens | L08 | checklist ops / tests | Confianza pre-demo / pre-cliente | Evita demos rotas (costo comercial) | S | — | pendiente |

\*Est. costo = orden de magnitud hasta fijar precios OpenAI vigentes × mediana de tokens por turno (medir en desk).

### B) Should — ops / forecast (batch o justo después)

| ID | Mejora | Productiza | Efecto costo | Esf. | Estado |
|---|---|---|---|---|---|
| B06 | Documento de precios internos: $/turno chat vs $/paso plan (mini vs high-risk) | Cotizar clientes / límites de uso | Base del forecast | S (docs + medir) | pendiente |
| B07 | Alertas budget ya existentes visibles en desk soporte (si faltan) | Ops no adivina | Evita runs que estallan en 30k tokens | S | revisar en L17 |
| B08 | Detalle `new_items` (tool name + args redactados) en traza | Debug más barato (menos re-runs a ciegas) | Baja re-trabajo | S | pendiente (L08 opc.) |
| B12 | Slack HITL en Render (`SLACK_APP_TOKEN` / approvers) verificado | Cola humana en canal Slack además de web | Neutro tokens; productiza aprobación | S (ops) | pendiente ops (L11) |
| B13 | Tunear `session_recent_messages` / `session_summary_max_chars` tras medir tokens | Controlar $/turno cuando el chat crece | Baja input tokens largos | S | pendiente medir (L12→L17) |
| B14 | Documentar/ops: idle UI (60m) ≠ retención 5y ≠ borrar con HITL pendiente; smoke `purge_retention --dry-run` | Evita pérdida de trabajo y cumple narrativa 1581 | Neutro tokens; baja riesgo ops | S | pendiente (L13) |
| B15 | Sentry `before_send` scrub PII/caso + tags release; no subir sample sin scrub | Incidentes sin filtrar 1581 | Neutro tokens | S | pendiente (L17) |

### C) Could — solo si producto duele

| ID | Mejora | Nota | Estado |
|---|---|---|---|
| B09 | `run_streamed` en chat | Solo con cancelación + HITL parcial; no por el curso | diferir demanda |
| B10 | Campos nuevos en schemas | Solo demanda abogado real | diferir demanda |
| B11 | Renombrar `src/mcp/` → `src/knowledge_tools/` (o similar) | Evita confusión con MCP real (L15); cosmético | diferir batch si sobra tiempo |

### D) Won’t — no productiza / sube riesgo o costo

| Tema | Por qué no |
|---|---|
| Web search / FileSearch hosted (L09) | Citas no auditables + storage terceros + $/calls |
| MCP Hosted / connectors Google·Drive·Notion con datos de casos (L15) | 1581/DPA; exfiltración; OAuth/ops sin valor litigante core |
| Montar MCP server “porque el curso” (L15) | Grounding ya es function tools; N×M no duele con superficie slim |
| Handoffs peer (L14 esperado) | Rompe una voz; más hops = más tokens |
| Sandbox / Bedrock (L21–L28) | Runtime distinto; no core firma web (clase hecha · Won’t) |
| Voice (L18–L20) | Aparcada hasta implementar voz + 1581/2300 |
| Resume-by-state mid-chat del lab L11 (en lugar de plan/draft) | Ambiguo para abogado; chat ya cierra respuesta |
| Conversation ID OpenAI como store primario de historial de casos (L12/L13) | Menos control 1581/ARCO; Postgres propio ya productiza |
| SQLite lab como DB de prod | Ops frágil vs Postgres |
| Purge por idle 60 min del chat | Anti-productizar; idle ≠ retención |
| Subir temperatura “naturalidad” | Empeora memoriales → más HITL → más $ |
| REPL con datos reales | Compliance |

### E) Drivers de costo ya en el producto (no tocar en batch salvo medir)

| Driver | Valor típico hoy | Rol |
|---|---|---|
| Modelo default | `gpt-4o-mini` | Chat / especialistas baratos |
| Modelo high-risk | `gpt-4o` | Redacción / tutela (vía plan) |
| `agent_max_turns` | 10 | Tope vueltas chat |
| `agent_max_turns_plan_step` | 6 | Tope por paso plan |
| `agent_max_total_tokens` | 30000 | Budget por run |
| Nested specialist ceiling | 8 | Evita loops as_tool |
| Chat sin high-risk tools | on | Evita $ high-risk sin plan |

**Fórmula forecast (usar en B04/B06):**

```text
$/turno ≈ (input_tokens × $/1k_in + output_tokens × $/1k_out) × modelo_usado
         + (si plan: sumar cada paso)
```

Medir mediana desde `trace.completion` (hooks), no adivinar.

### Orden sugerido del batch (cuando toque)

1. B02 + B03 (RunContext — seguridad/productización)  
2. B01 (ModelSettings — calidad + costo high-risk)  
3. B04 + B05 + B08 (visibilidad costo + smoke + traza)  
4. B06 (doc forecast para comercial/ops)  
5. B07 al cerrar L17 si falta

Comando único futuro (no usar aún): `aprobado, ejecuta batch udemy` (o listar B01–B05).

---

## Progreso de clases

| # | Lección | Decisión clase | ¿En backlog batch? |
|---|---|---|---|
| 1 | L01 Overview | DEJAR QUIETO | No |
| 2 | L02 Setup | DEJAR QUIETO | No |
| 3 | L06 Basic Agents | DEJAR QUIETO | No |
| 4 | L03 Structured Output | DEJAR QUIETO | No (schemas hechos) |
| 5 | L04 Model Settings | AJUSTAR | **B01** |
| 6 | L05 RunContext | AJUSTAR | **B02 · B03** |
| 7 | L07 Run Loop | DEJAR QUIETO | No (B09 diferido) |
| 8 | L08 RunResult | AJUSTAR | **B04 · B05 · B08** |
| 9 | L09 Hosted Tools | no aplicar | Won’t |
| 10 | L10 as_tool | DEJAR QUIETO | No (hecho) |
| 11 | L15 MCP | DEJAR QUIETO / no MCP real | Won’t MCP; Could **B11** rename |
| 12 | L14 Handoffs | DEJAR QUIETO / adaptar | Won’t peer (confirmado) |
| 13 | L16 Lab multi-agents | DEJAR QUIETO / no portar | Won’t lab; patrón as_tool ya vivo |
| 14 | L11 Guardrails + HITL | DEJAR QUIETO (código hecho) | **B12** Slack ops; no Must código |
| 15 | L12 Sessions | DEJAR QUIETO | **B13** tunear compactación |
| 16 | L13 Sessions prod | DEJAR QUIETO | **B14** idle vs retención |
| 17 | L17 Monitoring | DEJAR QUIETO base | **B04 · B07 · B15** |
| 18–20 | L18–L20 Voice | **APARCADA** hasta implementar voz | Reabrir con 1581/2300 |
| 21 | L21 Sandbox Agents | DIFERIR | Won’t |
| 22 | L22 Manifest / Caps | DIFERIR | Won’t |
| 23 | L23 Provider + creds | DIFERIR | Won’t |
| 24 | L24 Skills / Memory | DIFERIR portar · skills OK | Won’t sandbox |
| 25 | L25 State / composition | DIFERIR | Won’t |
| 26–27 | L26–L27 Labs | No portar | Won’t |
| 28 | L28 Bedrock | No migrar | Won’t |

---


## L01 — Overview

**Decisión global:** DEJAR QUIETO  
**Clase:** [`udemy-L01-overview-2026-07-27.md`](./udemy-L01-overview-2026-07-27.md)

### Cambiar

| Qué | Dónde | Por qué | Estado |
|---|---|---|---|
| — | — | El overview ya es la firma virtual (POC + as_tool + HITL) | N/A |

### No cambiar

| Qué | Por qué |
|---|---|
| Organigrama POC + especialistas | Es el propósito de L01 aplicado |
| Empezar por L11 guardrails | Primero propósito |
| Portar lab/demo del curso | No aporta al producto |

---

## L02 — Setup

**Decisión global:** DEJAR QUIETO  
**Clase:** [`udemy-L02-setup-2026-07-28.md`](./udemy-L02-setup-2026-07-28.md)

### Cambiar

| Qué | Dónde | Por qué | Estado |
|---|---|---|---|
| — | — | Local + Render ya operan | N/A |

### No cambiar

| Qué | Por qué |
|---|---|
| Lab Codex del curso | Setup del producto ya existe |
| Fallback sin API key | Resiliencia del desk |
| Commit de secrets | Seguridad |

### Ops

| Qué | Por qué |
|---|---|
| Verificar `OPENAI_API_KEY` en local y Render | Sin key → fallback |

---

## L06 — Basic Agents (POC)

**Decisión global:** DEJAR QUIETO  
**Clase:** [`udemy-L06-basic-agents-2026-07-28.md`](./udemy-L06-basic-agents-2026-07-28.md)

### Cambiar

| Qué | Dónde | Por qué | Estado |
|---|---|---|---|
| (Opcional) tono del Gerente | `agente/prompts/`, `/auditoria/` | Ajuste de producto sin romper organigrama | solo si se pide |

### No cambiar

| Qué | Por qué |
|---|---|
| `name` del POC | Rompe IDs / trazas / skills |
| Lab “hello agent” | Firma completa ya existe |
| Especialistas como caras de chat | Rompe una sola voz |

---

## L03 — Prompts & Structured Output

**Decisión global:** DEJAR QUIETO  
**Clase:** [`udemy-L03-structured-output-2026-07-28.md`](./udemy-L03-structured-output-2026-07-28.md)

### Cambiar

| Qué | Dónde | Por qué | Estado |
|---|---|---|---|
| (Opcional) campo nuevo en schema | `schemas.py` + render | Solo demanda real del abogado | pendiente demanda |
| (Opcional) pulir prompt especialista | `agente/prompts/` | Si hay alucinación de forma/tono | pendiente demanda |

### No cambiar

| Qué | Por qué |
|---|---|
| `output_type` en el chat POC | Gerente habla prosa |
| Inventar campos para llenar schema | Alucinación por formulario |
| Triage como `output_type` del chat | Triage es código (`triage.py`) |

---

## L04 — Model Settings

**Decisión global:** AJUSTAR → backlog **B01** (batch final)  
**Clase:** [`udemy-L04-model-settings-2026-07-28.md`](./udemy-L04-model-settings-2026-07-28.md)

### Cambiar

| Qué | Dónde | Por qué | Estado |
|---|---|---|---|
| Añadir `ModelSettings` (temp baja) en redactor, tutela, calidad | `orchestrator.py` | Menos creatividad; menos re-HITL/$ high-risk | **B01 pendiente** |
| Documentar valores modelo/temp en config o runbook | `config.py` / ops | Transparencia costo/calidad (B06) | con batch |

### No cambiar

| Qué | Por qué |
|---|---|
| `_model_for_agent` (mini vs high-risk) | Ya alinea costo a riesgo |
| Subir temperatura “por naturalidad” | Empeora memoriales |
| WebSocket en chat | HTTPS basta |

---

## L05 — RunContext

**Decisión global:** AJUSTAR → backlog **B02 · B03** (batch final) · anti-IDOR ContextVar se mantiene hasta cablear  
**Clase:** [`udemy-L05-runcontext-2026-07-28.md`](./udemy-L05-runcontext-2026-07-28.md)

### Cambiar

| Qué | Dónde | Por qué | Estado |
|---|---|---|---|
| Dataclass tipada (session, expediente, channel, user, flags 1581) | nuevo tipo + `runner.py` / plan_executor | Productizar multi-sesión segura | **B02 pendiente** |
| Pasar `context=` a `Runner.run` | `runner.py`, `plan_executor.py` | Idioma Agents SDK; `ctx.context` usable | **B02 pendiente** |
| Enlazar `resolve_expediente_id` al context tipado | `session_context.py` + tools | Misma defensa anti-IDOR, tipada | **B03 pendiente** |

### No cambiar

| Qué | Por qué |
|---|---|
| Anti-IDOR actual (`bind_active_session`) | Ya evita leer otro expediente; no romper hasta cablear |
| Meter API keys / tokens Slack / PII cruda en context | Fuga / 1581 |
| Consentimiento en RunContext del modelo | Consentimiento es gate de canal (`compliance/consent.py`) |

---

## L07 — Run Loop

**Decisión global:** DEJAR QUIETO  
**Clase:** [`udemy-L07-run-loop-2026-07-28.md`](./udemy-L07-run-loop-2026-07-28.md)

### Cambiar

| Qué | Dónde | Por qué | Estado |
|---|---|---|---|
| — obligatorio | — | Chat async completo + SSE en planes ya correcto para firma/HITL | N/A |
| (Opcional) `run_streamed` en chat | `runner.py` / UI | Solo si latencia percibida duele y hay cancelación + HITL parcial diseñado | pendiente demanda |

### No cambiar

| Qué | Por qué |
|---|---|
| `Runner.run` (no stream) en `/chat` | Respuesta cerrada = revisable |
| SSE `PlanEventBroker` en execute plan | Feedback de workflows largos |
| `run_with_retries` + timeout + fallback model | Resiliencia sin 500 eterno |
| Activar streaming “porque el curso” | Riesgo de borrador a medias / estado ambiguo |
| Handoffs peer dentro del loop | Rompe una voz de despacho |

---

## L08 — RunResult

**Decisión global:** AJUSTAR → backlog **B04 · B05 · B08** (batch final; base traza ya existe)  
**Clase:** [`udemy-L08-runresult-2026-07-29.md`](./udemy-L08-runresult-2026-07-29.md)

### Cambiar

| Qué | Dónde | Por qué | Estado |
|---|---|---|---|
| Detalle tool name/args redactados desde `new_items` | `runner.py` → traza / UI soporte | Menos re-runs a ciegas | **B08 pendiente** |
| Smoke formal RunResult (chat + plan + tokens) | checklist ops / tests | Productizar demos | **B05 pendiente** |
| Costo por turno desde hooks (`trace.completion`) | soporte / export | Estimar $/consulta | **B04 pendiente** |
| Documentar: usage vía hooks, no `result.usage` | ops | Evitar “arreglar” mal | con B04/B06 |

### No cambiar

| Qué | Por qué |
|---|---|
| Consumo de `final_output` + `_ensure_poc_voice` | Cara al abogado = Gerente; last_agent = auditoría |
| HITL alto riesgo por **plan**, no por interruptions en chat | Diseño L07/L11; chat sin high-risk tools |
| Workflow Trace + desk soporte + `/debug/trace` como “REPL” | Debug autenticado; sin CLI sobre expedientes |
| Exponer `raw_responses` en UI/logs públicos | Riesgo PII / forensics sin control |
| Portar REPL del curso a producción | 1581 / datos de casos |
| Reintroducir handoffs peer por `last_agent` | Rompe una sola voz |

---


## L09 — Hosted Tools

**Decisión global:** DEJAR QUIETO / no aplicar  
**Clase:** [`udemy-L09-hosted-tools-2026-07-30.md`](./udemy-L09-hosted-tools-2026-07-30.md)

### Cambiar

| Qué | Dónde | Por qué | Estado |
|---|---|---|---|
| — | — | Hosted tools del curso no caben en prod jurídica; RAG propio ya cubre grounding | N/A |

### No cambiar

| Qué | Por qué |
|---|---|
| Cero `WebSearch` / `FileSearch` / code / image / computer / shell hosted | Evita citas web y fuga de casos a terceros |
| RAG propio (`rag.py`) + prefetch + tool KB | Corpus auditable del despacho |
| Activar hosted “para bajar TCO” | En penal el riesgo jurídico > ahorro ops |
| Meter L09 en el batch final de código | No hay ítem de implementación; batch sigue siendo L04/L05/(L08) |

---


## L10 — Function Tools and Agent as Tools

**Decisión global:** DEJAR QUIETO  
**Clase:** [`udemy-L10-as-tool-2026-07-30.md`](./udemy-L10-as-tool-2026-07-30.md)  
**Código previo:** [`udemy-L10-as-tool-2026-07-27.md`](./udemy-L10-as-tool-2026-07-27.md)

### Cambiar

| Qué | Dónde | Por qué | Estado |
|---|---|---|---|
| — obligatorio | — | Patrón + hardening (descriptions, failures, nested turns, needs_approval) ya aplicados | N/A |

### No cambiar

| Qué | Por qué |
|---|---|
| Especialistas = `Agent.as_tool` (micrófono en Gerente) | Una sola voz al abogado |
| Function tools KB (`get_knowledge_tools`) | Dominio propio sin hosted L09 |
| `_SPECIALIST_TOOL_DESCRIPTIONS` (Usar/No usar) | Routing del Gerente |
| `_as_tool_failure_error` tipado | Sin stack/PII al abogado |
| Techo nested max turns | Evita loops caros |
| High-risk off en chat + plan HITL | Memorial/tutela no libres mid-chat |
| Handoffs peer | Rompe ownership de comunicación (L14) |
| Meter L10 en batch final | No hay gap de código pendiente |

---


## L15 — MCP

**Decisión global:** DEJAR QUIETO / no montar MCP real  
**Clase:** [`udemy-L15-mcp-2026-07-30.md`](./udemy-L15-mcp-2026-07-30.md)

### Cambiar

| Qué | Dónde | Por qué | Estado |
|---|---|---|---|
| (Opcional) rename `src/mcp/` → knowledge_tools | imports + docs | Naming ≠ protocolo MCP | **B11** Could |
| — obligatorio | — | Function tools KB bastan | N/A |

### No cambiar

| Qué | Por qué |
|---|---|
| `get_knowledge_tools` / allowlist / chat slim | Grounding controlado |
| Anti-IDOR expediente | Seguridad casos |
| Hosted MCP / native connectors con casos | 1581 / fuga |
| Servidor MCP genérico “por el curso” | Complejidad sin productizar |

---


## L14 — Handoffs (adaptado)

**Decisión global:** DEJAR QUIETO / adaptar — sin handoffs peer  
**Clase:** [`udemy-L14-handoffs-2026-07-30.md`](./udemy-L14-handoffs-2026-07-30.md)

### Cambiar

| Qué | Dónde | Por qué | Estado |
|---|---|---|---|
| — | — | Orquestación ya = as_tool + planes; no gap de código | N/A |

### No cambiar

| Qué | Por qué |
|---|---|
| Sin `handoffs=` en POC | Una voz; menos hops/$ |
| Especialistas vía `as_tool` | Manager sintetiza (L10) |
| Sequential vía plan HITL | Equivalente seguro al pipeline del curso |
| Conditional vía triage + gates | Sin classifier LLM extra |
| `_ensure_poc_voice` | Defensa residual |
| Portar lab handoffs | Rompe firma virtual |

---


## L16 — Lab multi-agents (adaptado)

**Decisión global:** DEJAR QUIETO / no portar lab  
**Clase:** [`udemy-L16-lab-multi-agents-2026-07-30.md`](./udemy-L16-lab-multi-agents-2026-07-30.md)

### Cambiar

| Qué | Dónde | Por qué | Estado |
|---|---|---|---|
| — | — | Ownership + as_tool + planes ya cubren el lab Parte B | N/A |

### No cambiar

| Qué | Por qué |
|---|---|
| Portar lab Codex triage/billing/tech | No es el producto firma |
| Patrón handoff del lab Parte A | Rompe una voz (L14 Won’t) |
| as_tool + last_agent = Gerente | Es el PASS del lab Parte B |
| Planes sequential HITL | Multi-paso productizable |
| Traza / desk como “dashboard del lab” | Ops sin CLI sobre casos |

---


## L11 — Guardrails + HITL

**Decisión global:** DEJAR QUIETO (runtime) · clase formal cerrada en #14  
**Clase:** [`udemy-L11-guardrails-hitl-2026-07-30.md`](./udemy-L11-guardrails-hitl-2026-07-30.md)  
**Código previo:** [`udemy-L11-guardrails-hitl-2026-07-27.md`](./udemy-L11-guardrails-hitl-2026-07-27.md)

### Cambiar

| Qué | Dónde | Por qué | Estado |
|---|---|---|---|
| Verificar Slack HITL en Render | ops env | Productizar aprobación fuera de web | **B12** Should |
| — código guardrails/HITL chat | — | Ya endurecido + tests L11 | hecho |

### No cambiar

| Qué | Por qué |
|---|---|
| Input/output/tool guardrails SDK | 3 superficies del curso |
| Alto riesgo vía **plan** (no tools libres en chat) | HITL honesto + control $ |
| Soft `invention_suspect` (no tripwire duro en citas) | Auditable sin matar el turno |
| Traza draft blocked si no hay draft | No mentir al abogado |
| Resume-by-state mid-chat del lab | Plan/draft es el ciclo de producto |

---


## L12 — Sessions

**Decisión global:** DEJAR QUIETO · opcional **B13**  
**Clase:** [`udemy-L12-sessions-2026-07-30.md`](./udemy-L12-sessions-2026-07-30.md)

### Cambiar

| Qué | Dónde | Por qué | Estado |
|---|---|---|---|
| Revisar umbrales compactación tras medir tokens | `config.py` (`session_recent_messages`, summary chars) | $/turno y context window | **B13** Should |
| — arquitectura SessionABC + Postgres | `gateway/agent_session.py` | Ya idiomática y productizable | N/A |

### No cambiar

| Qué | Por qué |
|---|---|
| `RepositoryAgentSession` en `Runner.run` | Continuidad multi-turno |
| Compactación + no persistir resumen sintético | Costo + no inventar “hechos” |
| `/chat/reset` al cambiar caso | Evita cruzar radicados |
| Conversation ID OpenAI / SQLite lab como primary | Control casos + Postgres |
| Meter secrets en session | Session ≠ RunContext |

---


## L13 — Sessions prod

**Decisión global:** DEJAR QUIETO (Postgres BYOS) · **B14** Should  
**Clase:** [`udemy-L13-sessions-prod-2026-07-31.md`](./udemy-L13-sessions-prod-2026-07-31.md)

### Cambiar

| Qué | Dónde | Por qué | Estado |
|---|---|---|---|
| Clarificar idle UI vs retención 5y vs HITL | runbook / copy UI + smoke purge dry-run | Productizar sin borrar trabajo | **B14** pendiente |
| — store Postgres + SessionABC | ya prod | Cumple L13 del curso | N/A |

### No cambiar

| Qué | Por qué |
|---|---|
| Postgres + `RepositoryAgentSession` | BYO durable / multi-instance |
| Retención policy + `purge_expired_data` + ARCO | 1581 |
| Plan stale reclaim 300s | Ops distinta del idle chat |
| Conversation ID / SQLite como primary | Control casos |
| Borrar chat por idle 60 min | Anti-productizar |

---


## L17 — Monitoring

**Decisión global:** DEJAR QUIETO base · backlog **B04 · B07 · B15**  
**Clase:** [`udemy-L17-monitoring-2026-07-31.md`](./udemy-L17-monitoring-2026-07-31.md)

### Cambiar

| Qué | Dónde | Por qué | Estado |
|---|---|---|---|
| $/turno desde `trace.completion` | desk soporte / export | Forecast y control gasto | **B04** |
| Budget excedido visible en desk | UI soporte | Ops no adivina | **B07** |
| Sentry scrub PII (`before_send`) | `main.py` | 1581 en incidentes | **B15** |

### No cambiar

| Qué | Por qué |
|---|---|
| RunConfig OpenAI + traza propia | Doble capa ops |
| Desk / `/debug/trace` | REPL autenticado |
| Datadog/Langfuse obligatorio | Sin licencia; desk basta |
| Subir sample Sentry sin scrub | Fuga |

---


## L18–L20 — Voice (APARCADA)

**Decisión global:** APARCADA — clase formal cuando se implemente voz  
**Nota:** [`udemy-L18-L20-voice-aparcada-2026-07-31.md`](./udemy-L18-L20-voice-aparcada-2026-07-31.md)

| L | Título | Estado |
|---|---|---|
| L18 | Realtime Voice Agents | Aparcada |
| L19 | Chained Voice Workflows | Aparcada |
| L20 | Lab Voice Agents | Aparcada |

### Cambiar / No cambiar (hasta voz)

| Qué | Por qué |
|---|---|
| No activar Realtime/chained voice ahora | 1581/2300 + canal no autorizado |
| Reabrir L18–L20 al implementar voz | Clase completa + backlog entonces |

---

## L21–L28 — Sandbox → Bedrock (hilo explicativo)

**Guía de lectura (orden lógico):** [`udemy-L21-L28-hilo-explicativo-2026-07-31.md`](./udemy-L21-L28-hilo-explicativo-2026-07-31.md)

| L | Título | Decisión | Audit corto |
|---|---|---|---|
| L21 | Sandbox Agents | DIFERIR | [`udemy-L21-sandbox-agents-2026-07-31.md`](./udemy-L21-sandbox-agents-2026-07-31.md) |
| L22 | Manifest / Caps / RunConfig | DIFERIR (analogía G1) | [`udemy-L22-sandboxrunconfig-manifest-2026-07-31.md`](./udemy-L22-sandboxrunconfig-manifest-2026-07-31.md) |
| L23 | Provider + credentials | DIFERIR (env Render) | [`udemy-L23-sandbox-provider-credentials-2026-07-31.md`](./udemy-L23-sandbox-provider-credentials-2026-07-31.md) |
| L24 | AGENTS.md / Skills / Memory | DIFERIR portar · skills OK | [`udemy-L24-agents-md-skills-memory-2026-07-31.md`](./udemy-L24-agents-md-skills-memory-2026-07-31.md) |
| L25 | State and Composition | DIFERIR (DB + planes) | [`udemy-L25-sandbox-state-composition-2026-07-31.md`](./udemy-L25-sandbox-state-composition-2026-07-31.md) |
| L26 | Lab SandboxAgents | No portar | [`udemy-L26-lab-sandboxagents-2026-07-31.md`](./udemy-L26-lab-sandboxagents-2026-07-31.md) |
| L27 | Lab SQL Analyzer | No portar | [`udemy-L27-lab-sql-analyzer-2026-07-31.md`](./udemy-L27-lab-sql-analyzer-2026-07-31.md) |
| L28 | Bedrock AgentCore | No migrar (Render) | [`udemy-L28-bedrock-agentcore-2026-07-31.md`](./udemy-L28-bedrock-agentcore-2026-07-31.md) |

### No activar

| Qué | Por qué |
|---|---|
| Sandbox OpenAI en prod | Shell/FS sobre casos |
| Sandbox memory auto | Contamina hechos sin HITL |
| Labs L26/L27 | Pedagógicos, no core litigante |
| Migrar a Bedrock | Otro cloud; target = Render |

---

## Resumen gerencia — clases + batch

| Prioridad | IDs | Qué | Cuándo |
|---|---|---|---|
| Must | B01–B05 | ModelSettings · RunContext · costo/turno · smoke | `aprobado, ejecuta batch udemy` |
| Should | B06–B08 · B12–B15 | Forecast · budget · tools · Slack · compactación · idle · Sentry | Mismo batch / ops |
| Could | B09–B11 | Stream · schemas · rename mcp | Demanda |
| Won’t | L21–L28 sandbox/Bedrock · hosted · MCP terceros · handoffs peer | No productiza firma web | — |
| Aparcado | L18–L20 Voice | Cuando implementes voz + 1581/2300 | — |

**Clases hechas:** L01–L17 + L21–L28. **Aparcadas:** L18–L20.  
Comando código: `aprobado, ejecuta batch udemy`
