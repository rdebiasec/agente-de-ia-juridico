# Plan Udemy → producto (corto)

**Dashboard:** [udemy-plan-dashboard.html](./udemy-plan-dashboard.html)  
**Checklist de cierre:** [CHECKLIST_UDEMY_CIERRE_LECCION.md](./CHECKLIST_UDEMY_CIERRE_LECCION.md)  
**Registro vivo:** [REGISTRO_UDEMY_REVISIONES.md](./REGISTRO_UDEMY_REVISIONES.md)  
**Prompt de clase:** [PROMPT_CLASE_UDEMY.md](./PROMPT_CLASE_UDEMY.md)  
**Listas de cambios (qué / por qué) — un solo doc:** [../auditoria/UDEMY_LISTA_CAMBIOS.md](../auditoria/UDEMY_LISTA_CAMBIOS.md)  
**Tablero maestro:** [plan-udemy-agents-sdk-aplicacion.md](./plan-udemy-agents-sdk-aplicacion.md)

Curso: OpenAI Agents SDK (28 lecciones).  
Orden: **pedagógico — propósito primero** (no empezar por guardrails).  
Regla: **una lección a la vez**. Código solo con `aprobado, ejecuta Lxx`.

## Orden oficial (28)

| # | Lección | Modo |
|---|---|---|
| 1 | L01 Overview | CLASE + mapa |
| 2 | L02 Setup | CLASE + mapa |
| 3 | L06 Basic Agents (POC) | CLASE + mapa |
| 4 | L03 Prompts / Structured Output | CLASE → AJUSTE |
| 5 | L04 Model Settings | CLASE → AJUSTE |
| 6 | L05 RunContext | CLASE → AJUSTE |
| 7 | L07 Run Loop | CLASE + decisión |
| 8 | L08 RunResult | CLASE → AJUSTE |
| 9 | L09 Hosted Tools | CLASE + no aplicar |
| 10 | L10 as_tool | CLASE → AJUSTE |
| 11 | L15 MCP | CLASE + decisión |
| 12 | L14 Handoffs (adaptado) | CLASE + adaptación |
| 13 | L16 Lab multi-agents (adaptado) | CLASE + adaptación |
| 14 | L11 Guardrails + HITL | CLASE → AJUSTE |
| 15 | L12 Sessions | CLASE → AJUSTE |
| 16 | L13 Sessions prod | CLASE → AJUSTE |
| 17 | L17 Monitoring | CLASE → AJUSTE |
| 18 | L18 Realtime Voice | APARCADA (hasta voz) |
| 19 | L19 Chained Voice | APARCADA (hasta voz) |
| 20 | L20 Lab Voice | APARCADA (hasta voz) |
| 21 | L21 Sandbox Agents | CLASE + diferir |
| 22 | L22 SandboxRunConfig | CLASE + diferir |
| 23 | L23 Sandbox credentials | CLASE + diferir |
| 24 | L24 AGENTS.md / Skills sandbox | CLASE + diferir |
| 25 | L25 Sandbox state | CLASE + diferir |
| 26 | L26 Lab Sandbox | CLASE + diferir |
| 27 | L27 Lab SQL Analyzer | CLASE + diferir |
| 28 | L28 Bedrock AgentCore | CLASE + diferir |

## Ritual

1. Prompt de clase (`PROMPT_CLASE_UDEMY.md`)  
2. Veredicto: DEJAR QUIETO / AJUSTAR / DIFERIR  
3. Solo si aplica: `aprobado, ejecuta Lxx`  
4. Actualizar **siempre** registro + checklist + este archivo + tablero + dashboard  
5. Actualizar `docs/auditoria/UDEMY_LISTA_CAMBIOS.md` (sección de esa lección)  

## Ahora

**Batch Udemy Must+Should ejecutado (2026-07-31):** Opción A modelos (`gpt-4.1-mini` / `gpt-4.1`) + temp baja; RunContext tipado; costo en traza; forecast; Sentry scrub; docs Slack/idle.  
**Pendiente ops:** secretos Slack en Render (B12) · medir tokens y tunear compactación (B13).  
**Aparcadas:** L18–L20 Voice.  
**Pedagógicas sandbox:** L21–L28 cerradas.
