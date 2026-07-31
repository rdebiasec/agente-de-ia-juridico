# Plan Udemy → Agente jurídico (tablero maestro)

**Fecha apertura:** 2026-07-27  
**Reorden pedagógico:** 2026-07-27 — propósito primero (L01), no L11  
**Curso:** Mastering Agents with OpenAI Agents SDK & OpenAI Codex (28 lecciones)  
**Fuente transcripts (gitignored):** `documentos/udemy_transcripts/mastering_agents_openai_sdk_codex/`  
**Producto:** firma virtual — [`ESTADO_PROYECTO.md`](../../agente/fases/ESTADO_PROYECTO.md), [`plan-rediseno-firma.md`](./plan-rediseno-firma.md)

## Premisas aprobadas

| Premisa | Valor |
|---|---|
| Curso | Solo este (Agents SDK + Codex) |
| Orden | Pedagógico L01→…→L28 (propósito → diseño → run → tools → orquestación → safety → sesiones → obs → avanzado) |
| Modo | Una lección a la vez; código solo tras «aprobado, ejecuta» |
| Arquitectura fija | `coordinador_expediente_penal` = única voz; especialistas = `Agent.as_tool`; sin handoffs peer |
| HITL | La IA propone; el abogado aprueba |
| Material Udemy | No se publica ni se commitea |
| L18–L20 | Voice **aparcada** hasta implementar canal voz |
| L21–L28 | Clase + mapa; código DIFERIR (sandbox/Bedrock ≠ Render) |

## Documentos hermanos

| Doc | Rol |
|---|---|
| [`PLAN_UDEMY_CORTO.md`](./PLAN_UDEMY_CORTO.md) | Orden corto + «Ahora» |
| [`PROMPT_CLASE_UDEMY.md`](./PROMPT_CLASE_UDEMY.md) | Prompt educativo reutilizable |
| [`../auditoria/UDEMY_LISTA_CAMBIOS.md`](../auditoria/UDEMY_LISTA_CAMBIOS.md) | Lista única: qué cambiar / por qué (L01–L28) |
| [`CHECKLIST_UDEMY_CIERRE_LECCION.md`](./CHECKLIST_UDEMY_CIERRE_LECCION.md) | Casillas de cierre |
| [`REGISTRO_UDEMY_REVISIONES.md`](./REGISTRO_UDEMY_REVISIONES.md) | Bitácora |
| [`udemy-plan-dashboard.html`](./udemy-plan-dashboard.html) | Vista visual |
| [`../auditoria/PLANTILLA_udemy-leccion.md`](../auditoria/PLANTILLA_udemy-leccion.md) | Plantilla auditoría |

## Flujo

1. Abrir siguiente lección del **camino pedagógico**.  
2. Pegar [`PROMPT_CLASE_UDEMY.md`](./PROMPT_CLASE_UDEMY.md) con `{NN}` y título.  
3. Leer veredicto high-level → `cerrar Lxx, dejar quieto` o `aprobado, ejecuta Lxx`.  
4. Actualizar **todas** las listas canónicas en el mismo turno.  
5. Avanzar solo a la siguiente.

Leyenda estado: `PENDIENTE` · `EN_CLASE` · `HECHO_CLASE` · `HECHO_AJUSTE` · `DIFERIR_OK` · `PARCIAL_FUERA_ORDEN`

---

## Camino pedagógico — las 28

| # | Lección | Propósito aquí | Modo | Estado | Evidencia |
|---|---|---|---|---|---|
| 1 | L01 Overview | Qué es Agents SDK y para qué existe esta firma | CLASE + mapa | HECHO_CLASE | [`udemy-L01-overview-2026-07-27.md`](../auditoria/udemy-L01-overview-2026-07-27.md) |
| 2 | L02 Setup | Cómo corre este repo (local/Render/API key) | CLASE + mapa | HECHO_CLASE | [`udemy-L02-setup-2026-07-28.md`](../auditoria/udemy-L02-setup-2026-07-28.md) |
| 3 | L06 Basic Agents | Qué es un Agent: el POC | CLASE + mapa | HECHO_CLASE | [`udemy-L06-basic-agents-2026-07-28.md`](../auditoria/udemy-L06-basic-agents-2026-07-28.md) |
| 4 | L03 Prompts / Structured Output | Contratos de salida | CLASE → AJUSTE | HECHO_CLASE | [`udemy-L03-structured-output-2026-07-28.md`](../auditoria/udemy-L03-structured-output-2026-07-28.md) · código [`…-07-27.md`](../auditoria/udemy-L03-structured-output-2026-07-27.md) |
| 5 | L04 Model Settings | Costo/calidad por rol | CLASE → AJUSTE | HECHO_CLASE | [`udemy-L04-model-settings-2026-07-28.md`](../auditoria/udemy-L04-model-settings-2026-07-28.md) · gap ModelSettings |
| 6 | L05 RunContext | Expediente/canal tipados | CLASE → AJUSTE | HECHO_CLASE | [`udemy-L05-runcontext-2026-07-28.md`](../auditoria/udemy-L05-runcontext-2026-07-28.md) · AJUSTE pend. |
| 7 | L07 Run Loop | Cómo vive un turno | CLASE + decisión | HECHO_CLASE | [`udemy-L07-run-loop-2026-07-28.md`](../auditoria/udemy-L07-run-loop-2026-07-28.md) |
| 8 | L08 RunResult | Inspeccionar el run | CLASE → AJUSTE | HECHO_CLASE | [`udemy-L08-runresult-2026-07-29.md`](../auditoria/udemy-L08-runresult-2026-07-29.md) · previo [`…-07-27.md`](../auditoria/udemy-L08-runresult-2026-07-27.md) |
| 9 | L09 Hosted Tools | Por qué NO web_search hosted | CLASE + no aplicar | HECHO_CLASE | [`udemy-L09-hosted-tools-2026-07-30.md`](../auditoria/udemy-L09-hosted-tools-2026-07-30.md) · previo [`…-07-27.md`](../auditoria/udemy-L09-hosted-tools-2026-07-27.md) |
| 10 | L10 as_tool | Especialistas = backoffice | CLASE → AJUSTE | HECHO_CLASE | [`udemy-L10-as-tool-2026-07-30.md`](../auditoria/udemy-L10-as-tool-2026-07-30.md) · código [`…-07-27.md`](../auditoria/udemy-L10-as-tool-2026-07-27.md) |
| 11 | L15 MCP | MCP real vs `src/mcp/tools.py` | CLASE + decisión | HECHO_CLASE | [`udemy-L15-mcp-2026-07-30.md`](../auditoria/udemy-L15-mcp-2026-07-30.md) · previo [`…-07-27.md`](../auditoria/udemy-L15-mcp-2026-07-27.md) |
| 12 | L14 Handoffs | Por qué NO handoffs peer | CLASE + adaptación | HECHO_CLASE | [`udemy-L14-handoffs-2026-07-30.md`](../auditoria/udemy-L14-handoffs-2026-07-30.md) · previo [`…-07-27.md`](../auditoria/udemy-L14-L16-handoffs-adaptado-2026-07-27.md) |
| 13 | L16 Lab multi-agents | Ownership; no portar lab | CLASE + adaptación | HECHO_CLASE | [`udemy-L16-lab-multi-agents-2026-07-30.md`](../auditoria/udemy-L16-lab-multi-agents-2026-07-30.md) · previo [`…-07-27.md`](../auditoria/udemy-L14-L16-handoffs-adaptado-2026-07-27.md) |
| 14 | L11 Guardrails + HITL | Freno + abogado aprueba | CLASE → AJUSTE | HECHO_CLASE | [`udemy-L11-guardrails-hitl-2026-07-30.md`](../auditoria/udemy-L11-guardrails-hitl-2026-07-30.md) · código [`…-07-27.md`](../auditoria/udemy-L11-guardrails-hitl-2026-07-27.md) |
| 15 | L12 Sessions | Memoria multi-turno | CLASE → AJUSTE | HECHO_CLASE | [`udemy-L12-sessions-2026-07-30.md`](../auditoria/udemy-L12-sessions-2026-07-30.md) · previo [`…-07-27.md`](../auditoria/udemy-L12-sessions-2026-07-27.md) |
| 16 | L13 Sessions prod | Postgres / idle / 1581 | CLASE → AJUSTE | HECHO_CLASE | [`udemy-L13-sessions-prod-2026-07-31.md`](../auditoria/udemy-L13-sessions-prod-2026-07-31.md) · previo [`…-07-27.md`](../auditoria/udemy-L13-sessions-prod-2026-07-27.md) |
| 17 | L17 Monitoring | Ops sin adivinar | CLASE → AJUSTE | HECHO_CLASE | [`udemy-L17-monitoring-2026-07-31.md`](../auditoria/udemy-L17-monitoring-2026-07-31.md) · previo [`…-07-27.md`](../auditoria/udemy-L17-monitoring-2026-07-27.md) |
| 18–20 | L18–L20 Voice | Aparcada hasta voz | CLASE al implementar | APARCADA | [`udemy-L18-L20-voice-aparcada-2026-07-31.md`](../auditoria/udemy-L18-L20-voice-aparcada-2026-07-31.md) |
| 21 | L21 Sandbox Agents | DIFERIR | CLASE | HECHO_CLASE · DIFERIR | [`udemy-L21-sandbox-agents-2026-07-31.md`](../auditoria/udemy-L21-sandbox-agents-2026-07-31.md) |
| 22 | L22 Manifest / Caps | DIFERIR | CLASE | HECHO_CLASE · DIFERIR | [`udemy-L22-sandboxrunconfig-manifest-2026-07-31.md`](../auditoria/udemy-L22-sandboxrunconfig-manifest-2026-07-31.md) |
| 23 | L23 Provider + creds | DIFERIR | CLASE | HECHO_CLASE · DIFERIR | [`udemy-L23-sandbox-provider-credentials-2026-07-31.md`](../auditoria/udemy-L23-sandbox-provider-credentials-2026-07-31.md) |
| 24 | L24 Skills / Memory | DIFERIR portar | CLASE reexplicada | HECHO_CLASE · DIFERIR | [`udemy-L24-agents-md-skills-memory-2026-07-31.md`](../auditoria/udemy-L24-agents-md-skills-memory-2026-07-31.md) |
| 25 | L25 State / composition | DIFERIR | CLASE | HECHO_CLASE · DIFERIR | [`udemy-L25-sandbox-state-composition-2026-07-31.md`](../auditoria/udemy-L25-sandbox-state-composition-2026-07-31.md) |
| 26 | L26 Lab Sandbox | No portar | CLASE | HECHO_CLASE | [`udemy-L26-lab-sandboxagents-2026-07-31.md`](../auditoria/udemy-L26-lab-sandboxagents-2026-07-31.md) |
| 27 | L27 Lab SQL | No portar | CLASE | HECHO_CLASE | [`udemy-L27-lab-sql-analyzer-2026-07-31.md`](../auditoria/udemy-L27-lab-sql-analyzer-2026-07-31.md) |
| 28 | L28 Bedrock | No migrar | CLASE | HECHO_CLASE · DIFERIR | [`udemy-L28-bedrock-agentcore-2026-07-31.md`](../auditoria/udemy-L28-bedrock-agentcore-2026-07-31.md) |

**Hilo L21–L28:** [`udemy-L21-L28-hilo-explicativo-2026-07-31.md`](../auditoria/udemy-L21-L28-hilo-explicativo-2026-07-31.md)

## Criterio de éxito

Fila viva por lección. **Hechas:** L01–L17 + L21–L28. **Aparcadas:** L18–L20.  
Siguiente código: `aprobado, ejecuta batch udemy`.
