# Udemy L28 — Bonus AWS Bedrock AgentCore (clase A–Z) — 2026-07-31

**Fase:** HECHO_CLASE  
**Decisión firma:** DIFERIR / no migrar · target = Render + Postgres  
**Fuente curso:** `txt/28_bonus_aws_bedrock_agentcore.txt`  
**Complemento:** mapa competitivo 2026 (hyperscalers + sandboxes + frameworks)

---

## 0. Nombre correcto

- Producto AWS: **Amazon Bedrock AgentCore** (a veces “Agent Core”).  
- No es lo mismo que solo “Bedrock” (modelos): AgentCore es la **plataforma de runtime/prod** para agents.  
- Relacionado pero distinto: **Amazon Bedrock Agents** (agente nativo AWS) vs AgentCore (hospeda tu framework: OpenAI Agents SDK, LangGraph, CrewAI, etc.).

---

## 1. Problema que resuelve (gaps laptop → prod)

| Gap | Por qué duele | Qué ofrece AgentCore |
|---|---|---|
| Aislamiento multi-usuario | Usuario A y B comparten compute → fuga | Micro-VM por sesión |
| Corridas largas | Serverless clásico ~15 min | Runtime hasta ~8 h |
| OAuth tools / “en nombre del usuario” | Calendar, Slack, etc. | Identity (2LO / 3LO) |
| Catálogo de tools | N×M wrappers | Gateway → MCP |
| Memoria corta/larga | Solo chat history | Memory service |
| Observar / evaluar | DIY | CloudWatch + Evaluations |
| Políticas finas | “¿puede pagar >$2000?” | Policy (lenguaje natural → reglas) |
| Compartir agents en la empresa | Wiki informal | Registry |

Principios: **framework-agnostic · model-agnostic · modular** (puzzle: usás lo que necesitás).

---

## 2. Los ~10 servicios (catálogo)

| # | Servicio | Para qué |
|---|---|---|
| 1 | **Runtime** | Hospedar agent (y MCP servers); micro-VM/sesión |
| 2 | **Memory** | Short-term (eventos) + long-term (semantic, summary, preferences, episodic, custom) |
| 3 | **Gateway** | APIs → MCP; OpenAPI/Smithy/Lambda; search de tools |
| 4 | **Identity** | OAuth/API keys; 2LO (máquina-máquina) vs 3LO (consentimiento usuario) |
| 5 | **Code Interpreter** | VM para correr código (Py/JS/TS); VPC opcional |
| 6 | **Browser** | Automatización web (Playwright managed); replay/auditoría |
| 7 | **Observability** | Logs/traces/metrics CloudWatch; OTEL |
| 8 | **Evaluations** | Offline (dataset) / online (live); ~13 evaluators |
| 9 | **Policy** | Permisos finos sobre gateway (CEDAR-like / NL policies) |
| 10 | **Registry** | Publicar/descubrir agents y tools en la org (+ approval) |

(El curso nota que el número creció 7→9→10.)

---

## 3. Runtime en detalle

- Micro-VM dedicada por `session_id` (CPU/RAM/FS separados; destruida al fin).  
- Cold start sub-segundo (claim AWS).  
- Cobro por segundo de CPU útil; **no cobrás** mientras el LLM espera tools (según curso).  
- Payload grande hasta ~100 MB; multimodal.  
- Puertos: 8000 invocations/MCP, health, 8080 WebSocket, 9000 A2A.  
- Imágenes en **ECR**.  
- Wrapper OpenAI Agents: `BedrockAgentCoreApp` + `@app.entrypoint` → `Runner.run`.  
- Deploy: CLI AgentCore o CDK.

Vs Lambda: Lambda = aislamiento a nivel proceso + límites de duración/payload; AgentCore = micro-VM + largas corridas.

---

## 4. Memory / Gateway / Identity (resumen útil)

**Memory namespaces:** agent id · actor (user) · session.  
Estrategias long-term: semantic · summary · user preference · episodic · custom.

**Gateway:** inbound OAuth/IAM · outbound API key/OAuth/IAM; connectors one-click (Slack, Salesforce, Jira…).

**Identity:** vault de tokens; refresh; 3LO = consentimiento humano (ej. Google Calendar).

---

## 5. Mapa competitivo A–Z (no solo Bedrock)

### Capa A — Runtimes managed de hyperscaler (competidores directos)

| Nombre | Quién | Enfoque típico |
|---|---|---|
| **Amazon Bedrock AgentCore** | AWS | Isolation-first, framework-agnostic, puzzle modular |
| **Google Vertex AI Agent Engine** | Google | Runtime + **Memory Bank**; ecosistema Gemini / ADK |
| **Azure AI Foundry Agent Service** (Hosted Agents) | Microsoft | PaaS: identity Entra, scale-to-zero, M365/Teams |

### Capa B — Plataformas / frameworks de agents (orquestación, no siempre el mismo “hotel”)

| Nombre | Nota |
|---|---|
| **OpenAI Agents SDK** (+ AgentKit / platform traces) | Lo que ustedes ya usan en código |
| **LangGraph Platform** / LangSmith | Runtime + obs del ecosistema LangChain |
| **CrewAI** | Multi-agent crews |
| **Microsoft AutoGen / Agent Framework** | Stack MS |
| **Google ADK** | Agents en Vertex |
| **Amazon Bedrock Agents** | Agente “nativo” AWS (distinto de AgentCore hospedando tu SDK) |
| **Databricks Agent Bricks** | Agents anclados a datos / Unity Catalog |

### Capa C — Sandbox / compute para el “PC del agent” (L21–L23)

| Nombre | Nota |
|---|---|
| **E2B**, **Modal**, **Daytona**, **Runloop**, **Blackcell** | microVM / sandbox agentic |
| **Vercel Sandbox**, **Cloudflare Agents / Workers** | edge + preview |
| **Fly.io Machines** | VMs ligeras |

### Capa D — “Hacer prod sin AgentCore” (lo de ustedes)

| Nombre | Nota |
|---|---|
| **Render** (+ Postgres) | App web + DB; HITL; session propia |
| **Railway / Fly / Cloud Run / ECS** | App containers genéricos |
| **Self-host K8s** | Máximo control, máximo ops |

**Importante:** competir con AgentCore ≠ cambiar de modelo LLM. Pueden seguir con OpenAI y hospedar en Render, o en AgentCore, o en Foundry.

---

## 6. Traducción a la firma virtual

| Necesidad AgentCore | Ustedes hoy |
|---|---|
| Runtime aislado | Proceso Render + session/expediente anti-IDOR (no micro-VM/usuario) |
| Memory | Chat Postgres + expediente (HITL); no Memory Bank AWS |
| Gateway MCP | Function tools KB/expediente |
| Identity OAuth tools | Login cookie + consent 1581; Slack HITL; no 3LO Calendar |
| Observability | Traces propias + OpenAI + desk soporte (L17) |
| Policy | G1–G10 + guardrails + planes HITL |
| Registry | Skills/prompts en git |

---

## 7. Veredicto

> **DIFERIR / no migrar a Bedrock AgentCore.**  
> Target de producto = **Render + Postgres + Gerente + as_tool + HITL**.  
> Si un día hay requisito enterprise AWS (o Azure/GCP), reabrir con evaluación 1581/DPA/costo — no “porque L28”.

### Cuándo sí tendría sentido AgentCore (hipotético)
- Obligación de quedarse en AWS.  
- Necesidad real de micro-VM por sesión + corridas de horas.  
- Catálogo enterprise de tools MCP + OAuth 3LO a escala.  

Hoy el despacho litigante web **no** lo pide.
