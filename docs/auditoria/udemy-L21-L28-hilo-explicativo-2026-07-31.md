# Udemy — Hilo L21→L28 explicado (Sandbox → Bedrock) — 2026-07-31

**Para qué sirve este doc:** leer en orden. Cada lección es un capítulo; al final queda claro qué ya tenéis en la firma y qué **no** vamos a montar.

**Decisión de producto (todas):** DIFERIR código sandbox/Bedrock. Deploy = Render + Postgres + Gerente + as_tool + HITL.

---

## El hilo en una página

Imagina un **pasante con un computador propio** (no solo un chat):

| Paso | Lección | Pregunta que responde |
|---|---|---|
| 1 | L21 | ¿Qué es ese “pasante con PC”? |
| 2 | L22 | ¿Qué carpetas ve y qué le dejamos hacer? |
| 3 | L23 | ¿En qué máquina corre y dónde van las contraseñas? |
| 4 | L24 | ¿Cómo le enseñamos el oficio sin reescribir el system prompt? |
| 5 | L25 | Si se pausa (HITL / se cae el container), ¿cómo se reanuda? |
| 6 | L26 | Lab: arreglar un bug con shell/archivos |
| 7 | L27 | Lab: agente que consulta SQL |
| 8 | L28 | Bonus: llevar agents a AWS Bedrock AgentCore |

**En la firma virtual el “pasante” no tiene PC propio.** Tiene chat + tools + especialistas + planes que el abogado aprueba. Por eso estas lecciones se **entienden** y se **diferirán**.

---

## Recuerdo rápido L21–L23 (puente)

### L21 — Sandbox Agents
Agent normal = habla y usa tools.  
Sandbox Agent = eso **más un playground** (archivos, terminal, instalar librerías, a veces un link de preview).  
OpenAI separa **harness** (orquestación) y **compute** (donde trabaja).

### L22 — Manifest + Capabilities + SandboxRunConfig
- **Manifest** = qué entra al escritorio al arrancar (CSV, git, S3…).  
- **Capabilities** = poderes: shell, archivos, compactación; opcionales skills/memory.  
- **SandboxRunConfig** = con qué client/session se corre.

Analogía firma: qué inyectáis (G1/RAG) · qué tools puede (allowlist) · `RunConfig` propio.

### L23 — Providers + credentials
9 sitios donde corre el playground (local, Docker, E2B, Vercel…).  
Secrets en dos capas: (1) del provider/mount ocultas al LLM; (2) runtime vía RunContext.  
Firma: secrets en **env Render**; no mounts de expedientes a SaaS.

---

## L24 — AGENTS.md, Skills y Sandbox Memory *(reexplicada)*

### Analogía de despacho
Tenés tres cosas distintas en un estudio jurídico:

1. **Quién es el abogado asociado** (rol, tono, límites) → eso es el **system prompt / instructions**.  
2. **Cómo funciona *este* expediente o carpeta del caso** (dónde está la denuncia, qué no tocar) → eso sería **AGENTS.md** en el curso (reglas del *workspace*).  
3. **Manuales de práctica** (“cómo se arma una tipicidad”, “cómo se inventaría un memorial”) → **Skills**.  
4. **Cuaderno de lecciones del pasante** (“la semana pasada me equivoqué con pandas”) → **Sandbox memory** (el modelo se escribe a sí mismo archivos de memoria).

### Por qué el curso los separa
- Las **instructions** viven en el código del agent (identidad). No deberían describir “la carpeta billing de Acme”, porque otro agent en otro workspace no las comparte igual.  
- **AGENTS.md** vive *dentro del escritorio* del sandbox: cualquier agent que entre a ese workspace lee las mismas reglas de proyecto.  
- **Skills** = playbooks en markdown (con índice corto para no gastar tokens). El agent lee el índice y solo carga el skill completo si lo necesita.  
- **Sandbox memory** ≠ historial de chat:  
  - **Session** = “qué nos dijimos hoy” (hace falta para conversar).  
  - **Memory** = “qué aprendí del mundo/tareas a lo largo del tiempo”.

### Qué tenéis YA en la firma (esto es lo importante)

| Idea del curso | En vuestro producto |
|---|---|
| Instructions (identidad) | `agente/prompts/agents/*.md` (Gerente = única voz) |
| Reglas de “proyecto” | G1–G10, guía, guardrails — no un AGENTS.md de sandbox |
| Skills / playbooks | `agente/skills/**/SKILL.md` (~90), versionados en git |
| Historial de chat | Session Postgres (L12/L13) |
| “Memoria larga” útil | Expediente + planes + drafts en DB, con abogado |

### Qué NO vamos a hacer
- Montar **sandbox memory** para que el modelo escriba “hechos del caso” en un `memory.md`. En penal-víctimas eso puede **contaminar** el expediente sin HITL.  
- Tirar las skills propias para “usar AGENTS.md OpenAI”.

**Veredicto L24:** DIFERIR portar sandbox. Mantener skills + prompts.

---

## L25 — State and Composition

### Problema humano
El sandbox puede tardar **minutos**; el abogado puede tardar **horas** en aprobar. O se cae el container. Hay que poder **pausar y reanudar** sin perder el trabajo.

### Tres capas de estado (curso)

1. **Run state** — el loop del agent (harness): “iba a llamar tal tool”. Igual que HITL en agents normales.  
2. **Session state** — el container vivo (procesos, env, playground encendido).  
3. **Snapshots** — solo los **archivos** del workspace (lo más fácil de entender: copiar carpetas / sync a S3).

Orden mental al reanudar: si el client sigue vivo → reusar session; si solo pausaste el harness → resume run state; si murió el container → resume session state o, en frío, solo snapshots.

### Composition
Podés mezclar agent normal + sandbox (handoff o as_tool). El curso avisa: **quién tiene el micrófono**.  
En la firma: ya resolvisteis eso con **as_tool** (Gerente habla; especialistas trabajan y devuelven). No handoffs peer.

### En la firma
| Capa curso | Equivalente |
|---|---|
| Run state | Plan executor + pause HITL (planes/drafts) |
| Session state container | No aplica (no hay playground) |
| Snapshots FS | Drafts/planes/expediente en **Postgres** |

**Veredicto L25:** DIFERIR. Estado productizable = DB + planes, no freeze de container.

---

## L26 — Lab: SandboxAgents

### Qué hace el lab
Montan un repo de calculadora con bug → el sandbox agent usa **archivos + shell + tests** → encuentra el bug → lo arregla → tests verdes. También juega con skills/memory/AGENTS.md.

### Qué aprendés (sin portar)
Confirmar el mental model L21–L25 con las manos.

### Firma
No portar. No dar shell al Gerente sobre expedientes.

**Veredicto L26:** DIFERIR / no portar lab.

---

## L27 — Lab: SQL Analyzer Agent

### Qué hace el lab
Agente que responde preguntas de negocio sobre una DB e-commerce (SQLite). Tools + **RunContext** con la conexión. Safety: solo SELECT / read-only.

### Qué aprendés
- RunContext para secretos/conexión (eco de L05/L23).  
- Guardrails sobre SQL (no dejar que el modelo haga DROP).

### Firma
Ya tenéis tools de KB/expediente con anti-IDOR. **No** conectar un agent con SQL libre a Postgres de prod. Consultas a DB = código/ops controlado.

**Veredicto L27:** DIFERIR / no portar.

---

## L28 — Bonus AWS Bedrock AgentCore

### Qué es
Servicio AWS para **hospedar** agents en producción “enterprise”: aislamiento por sesión (micro-VM), corridas largas, memoria, eval, identity/OAuth, gateway MCP, etc. Framework/model agnostic; podés envolver un OpenAI agent.

### Qué gaps dice resolver
Laptop ≠ prod: isolation multi-usuario, seguridad OAuth, long-running, observability, tools gateway…

### Firma
Deploy elegido = **Render + Postgres**. Bedrock = **otro cloud, otra factura, otro compliance**. No migrar “porque L28”.

**Veredicto L28:** DIFERIR / no migrar. Si un día hay requisito AWS enterprise, reabrir con evaluación (no por el curso).

---

## Cierre del bloque — una sola tabla

| L | Título | En la firma | Decisión |
|---|---|---|---|
| L21 | Sandbox Agents | No hay playground | DIFERIR |
| L22 | Manifest / Caps / RunConfig | G1 + tools + RunConfig | DIFERIR (analogía sí) |
| L23 | Providers / creds | Env Render | DIFERIR |
| L24 | AGENTS.md / Skills / Memory | Skills+prompts sí; memory sandbox no | DIFERIR portar |
| L25 | State / composition | Planes + Postgres; as_tool | DIFERIR |
| L26 | Lab Sandbox | — | No portar |
| L27 | Lab SQL | — | No portar |
| L28 | Bedrock | Render | No migrar |

**Productizar ahora** = batch `aprobado, ejecuta batch udemy` (B01–B05…), no este bloque.

**Voice L18–L20** sigue aparcada hasta que implementéis voz.
