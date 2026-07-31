# Registro de revisiones Udemy → producto

**Propósito:** bitácora viva — **una lección a la vez**, orden pedagógico.  
**Orden oficial:** [`PLAN_UDEMY_CORTO.md`](./PLAN_UDEMY_CORTO.md) (L01 primero, no L11).  
**Checklist:** [`CHECKLIST_UDEMY_CIERRE_LECCION.md`](./CHECKLIST_UDEMY_CIERRE_LECCION.md)  
**Tablero:** [`plan-udemy-agents-sdk-aplicacion.md`](./plan-udemy-agents-sdk-aplicacion.md)  
**Prompt:** [`PROMPT_CLASE_UDEMY.md`](./PROMPT_CLASE_UDEMY.md)  
**Cambios (todas las lecciones, un doc):** [`../auditoria/UDEMY_LISTA_CAMBIOS.md`](../auditoria/UDEMY_LISTA_CAMBIOS.md)

---

## Estado actual

| Campo | Valor |
|---|---|
| Serie formal | **Reabierta** — orden pedagógico 2026-07-27 |
| Lección en foco | **BATCH CÓDIGO** (L28 cerrada) · Voice aparcada |
| Estado | L01–L17 + L21–L28 HECHO_CLASE; L18–L20 aparcadas |
| Siguiente | `aprobado, ejecuta batch udemy` |
| Nota | L11 tuvo revisión parcial **fuera de orden**; se reabre en puesto #14 |

---

## Bitácora (revisiones formales en orden)

| # | Fecha | Lección | Qué se revisó | Resultado | Evidencia |
|---|---|---|---|---|---|
| 1 | 2026-07-27 | **L01** Overview | Propósito Agents SDK → firma virtual (POC + as_tool + HITL); caption L01 inválida → KB + ESTADO + plan-rediseno | **HECHO_CLASE** · DEJAR QUIETO | [`../auditoria/udemy-L01-overview-2026-07-27.md`](../auditoria/udemy-L01-overview-2026-07-27.md) |
| 2 | 2026-07-28 | **L02** Setup | API key + local/Render; no rehacer lab Codex; fallback sin key en runner | **HECHO_CLASE** · DEJAR QUIETO | [`../auditoria/udemy-L02-setup-2026-07-28.md`](../auditoria/udemy-L02-setup-2026-07-28.md) |
| 3 | 2026-07-28 | **L06** Basic Agents | Agent = POC `coordinador_expediente_penal`; caption ausente → `orchestrator.py` | **HECHO_CLASE** · DEJAR QUIETO | [`../auditoria/udemy-L06-basic-agents-2026-07-28.md`](../auditoria/udemy-L06-basic-agents-2026-07-28.md) |
| 4 | 2026-07-28 | **L03** Structured Output | Prompts = contrato; 10/10 schemas backoffice; POC prosa; render HITL | **HECHO_CLASE** · DEJAR QUIETO | [`../auditoria/udemy-L03-structured-output-2026-07-28.md`](../auditoria/udemy-L03-structured-output-2026-07-28.md) |
| 5 | 2026-07-28 | **L04** Model Settings | Modelo high-risk sí; `ModelSettings` ausente → gap documentado | **HECHO_CLASE** · AJUSTE pendiente | [`../auditoria/udemy-L04-model-settings-2026-07-28.md`](../auditoria/udemy-L04-model-settings-2026-07-28.md) |
| 6 | 2026-07-28 | **L05** RunContext | ContextVar anti-IDOR sí; falta `context=` tipado | **HECHO_CLASE** · AJUSTE pendiente | [`../auditoria/udemy-L05-runcontext-2026-07-28.md`](../auditoria/udemy-L05-runcontext-2026-07-28.md) |
| 7 | 2026-07-28 | **L07** Run Loop | Chat async completo; SSE planes; retries; no run_streamed | **HECHO_CLASE** · DEJAR QUIETO | [`../auditoria/udemy-L07-run-loop-2026-07-28.md`](../auditoria/udemy-L07-run-loop-2026-07-28.md) |
| 8 | 2026-07-29 | **L08** RunResult | 7 campos + new_items; traza/desk = REPL; chat HITL≠interruptions | **HECHO_CLASE** · AJUSTE opcional | [`../auditoria/udemy-L08-runresult-2026-07-29.md`](../auditoria/udemy-L08-runresult-2026-07-29.md) |
| 9 | 2026-07-30 | **L09** Hosted Tools | 6 hosted; no web/file hosted; RAG propio | **HECHO_CLASE** · DEJAR QUIETO / no aplicar | [`../auditoria/udemy-L09-hosted-tools-2026-07-30.md`](../auditoria/udemy-L09-hosted-tools-2026-07-30.md) |
| 10 | 2026-07-30 | **L10** Function + as_tool | Gerente+especialistas; hardening previo; sin handoffs | **HECHO_CLASE** · DEJAR QUIETO | [`../auditoria/udemy-L10-as-tool-2026-07-30.md`](../auditoria/udemy-L10-as-tool-2026-07-30.md) |
| 11 | 2026-07-30 | **L15** MCP | MCP curso ≠ src/mcp function tools; no Hosted/connectors casos | **HECHO_CLASE** · no MCP real | [`../auditoria/udemy-L15-mcp-2026-07-30.md`](../auditoria/udemy-L15-mcp-2026-07-30.md) |
| 12 | 2026-07-30 | **L14** Handoffs | Concepto + 4 topologías; adaptar a as_tool+planes; Won’t peer | **HECHO_CLASE** · adaptar | [`../auditoria/udemy-L14-handoffs-2026-07-30.md`](../auditoria/udemy-L14-handoffs-2026-07-30.md) |
| 13 | 2026-07-30 | **L16** Lab multi-agents | Lab handoff vs as_tool; no portar; ownership=Gerente | **HECHO_CLASE** · no portar | [`../auditoria/udemy-L16-lab-multi-agents-2026-07-30.md`](../auditoria/udemy-L16-lab-multi-agents-2026-07-30.md) |
| 14 | 2026-07-30 | **L11** Guardrails + HITL | 3 superficies + plan/draft HITL; código previo; B12 Slack ops | **HECHO_CLASE** · DEJAR QUIETO | [`../auditoria/udemy-L11-guardrails-hitl-2026-07-30.md`](../auditoria/udemy-L11-guardrails-hitl-2026-07-30.md) |
| 15 | 2026-07-30 | **L12** Sessions | SessionABC+Postgres+compact; no Conversation ID OpenAI; B13 | **HECHO_CLASE** · DEJAR QUIETO | [`../auditoria/udemy-L12-sessions-2026-07-30.md`](../auditoria/udemy-L12-sessions-2026-07-30.md) |
| 16 | 2026-07-31 | **L13** Sessions prod | BYO Postgres ya prod; retención/ARCO; B14 idle≠purge | **HECHO_CLASE** · DEJAR QUIETO | [`../auditoria/udemy-L13-sessions-prod-2026-07-31.md`](../auditoria/udemy-L13-sessions-prod-2026-07-31.md) |
| 17 | 2026-07-31 | **L17** Monitoring | OpenAI traces + traza propia; B04/B07/B15 costos/Sentry | **HECHO_CLASE** · DEJAR QUIETO base | [`../auditoria/udemy-L17-monitoring-2026-07-31.md`](../auditoria/udemy-L17-monitoring-2026-07-31.md) |
| — | 2026-07-31 | **L18–L20** Voice | Aparcada hasta implementar voz (1581/2300) | **APARCADA** | [`../auditoria/udemy-L18-L20-voice-aparcada-2026-07-31.md`](../auditoria/udemy-L18-L20-voice-aparcada-2026-07-31.md) |
| 18 | 2026-07-31 | **L21** Sandbox Agents | Playground ≠ firma; DIFERIR | **HECHO_CLASE** · DIFERIR | [`../auditoria/udemy-L21-sandbox-agents-2026-07-31.md`](../auditoria/udemy-L21-sandbox-agents-2026-07-31.md) |
| 19 | 2026-07-31 | **L22** SandboxRunConfig / Manifest | Analogía G1/tools/RunConfig; DIFERIR | **HECHO_CLASE** · DIFERIR | [`../auditoria/udemy-L22-sandboxrunconfig-manifest-2026-07-31.md`](../auditoria/udemy-L22-sandboxrunconfig-manifest-2026-07-31.md) |
| 20 | 2026-07-31 | **L23** Provider + credentials | Secrets = env Render; DIFERIR SaaS sandbox | **HECHO_CLASE** · DIFERIR | [`../auditoria/udemy-L23-sandbox-provider-credentials-2026-07-31.md`](../auditoria/udemy-L23-sandbox-provider-credentials-2026-07-31.md) |
| 21 | 2026-07-31 | **L24** AGENTS.md / Skills / Memory | Reexplicada; skills propias; DIFERIR memory sandbox | **HECHO_CLASE** · DIFERIR | [`../auditoria/udemy-L24-agents-md-skills-memory-2026-07-31.md`](../auditoria/udemy-L24-agents-md-skills-memory-2026-07-31.md) |
| 22 | 2026-07-31 | **L25–L27** | State · labs (una a una) | **HECHO_CLASE** · DIFERIR | audits L25–L27 |
| 23 | 2026-07-31 | **L28** Bedrock AgentCore | A–Z + mapa competitivo; no migrar | **HECHO_CLASE** · DIFERIR | [`../auditoria/udemy-L28-bedrock-agentcore-2026-07-31.md`](../auditoria/udemy-L28-bedrock-agentcore-2026-07-31.md) |

### Fuera de orden (histórico)

| Fecha | Lección | Nota |
|---|---|---|
| 2026-07-27 | L11 (parcial) | Código/tests antes del puesto #14; **formalizado** el 2026-07-30 |
| 2026-07-27 | L10 / L03 (anticipado) | Código existía antes; L03 y L10 ya cerrados en serie formal |

---

## Progreso 1–28

| # | Lección | Estado |
|---|---|---|
| 1 | L01 | [x] HECHO_CLASE |
| 2 | L02 | [x] HECHO_CLASE |
| 3 | L06 | [x] HECHO_CLASE |
| 4 | L03 | [x] HECHO_CLASE |
| 5 | L04 | [x] HECHO_CLASE (AJUSTE pend.) |
| 6 | L05 | [x] HECHO_CLASE (AJUSTE pend.) |
| 7 | L07 | [x] HECHO_CLASE |
| 8 | L08 | [x] HECHO_CLASE (AJUSTE opcional) |
| 9 | L09 | [x] HECHO_CLASE (no aplicar) |
| 10 | L10 | [x] HECHO_CLASE |
| 11 | L15 | [x] HECHO_CLASE (no MCP real) |
| 12 | L14 | [x] HECHO_CLASE (adaptar) |
| 13 | L16 | [x] HECHO_CLASE (no portar) |
| 14 | L11 | [x] HECHO_CLASE |
| 15 | L12 | [x] HECHO_CLASE |
| 16 | L13 | [x] HECHO_CLASE |
| 17 | L17 | [x] HECHO_CLASE |
| 18–20 | L18–L20 Voice | [ ] APARCADA (hasta voz) |
| 21 | L21 Sandbox Agents | [x] HECHO_CLASE · DIFERIR |
| 22 | L22 SandboxRunConfig… | [x] HECHO_CLASE · DIFERIR |
| 23 | L23 Provider + credentials | [x] HECHO_CLASE · DIFERIR |
| 24 | L24 AGENTS.md / Skills / Memory | [x] HECHO_CLASE · DIFERIR |
| 25 | L25 State and Composition | [x] HECHO_CLASE · DIFERIR |
| 26 | L26 Lab SandboxAgents | [x] HECHO_CLASE · no portar |
| 27 | L27 Lab SQL Analyzer | [x] HECHO_CLASE · no portar |
| 28 | L28 Bedrock AgentCore | [x] HECHO_CLASE · no migrar |

---

## Cómo actualizar

1. Solo tras clase / `aprobado, ejecuta Lxx` / `cerrar Lxx, dejar quieto`.  
2. Nueva fila en Bitácora + casilla en Progreso.  
3. Sincronizar PLAN_CORTO, tablero, checklist, dashboard.  
4. Actualizar sección Lxx en `docs/auditoria/UDEMY_LISTA_CAMBIOS.md`.  
5. No adelantar lecciones.
