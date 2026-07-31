# Udemy L21–L28 — Índice Sandbox + Bedrock — 2026-07-31

**Estado:** índice / borrador de bloque. **Clases formales = una a una** (L21 hecha; L22–L28 en cola).  
**Decisión esperada por lección:** DIFERIR · cero código  
**Fuentes:** `txt/21_…` … `txt/28_…`  
**L18–L20 Voice:** aparcadas.  
**Individuales:** [L21](./udemy-L21-sandbox-agents-2026-07-31.md) · [L22](./udemy-L22-sandboxrunconfig-manifest-2026-07-31.md) · [L23](./udemy-L23-sandbox-provider-credentials-2026-07-31.md) · [L24](./udemy-L24-agents-md-skills-memory-2026-07-31.md)

---

## 0. Veredicto del bloque

Sandbox Agents y Bedrock AgentCore son el “modo avanzado” del curso: agentes con **playground** (shell, archivos, deps, UI) o hosting **AWS**.  
La firma virtual productizable hoy es **Gerente + as_tool + HITL + Postgres en Render**.  
Este bloque se estudia completo para **mapear equivalencias** y dejar explícito el Won’t — no para portar labs.

| L | Título | Decisión |
|---|---|---|
| L21 | Sandbox Agents | DIFERIR |
| L22 | SandboxRunConfig / Manifest / Capabilities | DIFERIR (+ mapa G1–G10) |
| L23 | Provider + Mount Credentials | DIFERIR |
| L24 | AGENTS.md / Skills / Sandbox Memory | DIFERIR portar · mantener skills propias |
| L25 | State and Composition | DIFERIR |
| L26 | Lab SandboxAgents | DIFERIR / no portar |
| L27 | Lab SQL Analyzer | DIFERIR / no portar |
| L28 | AWS Bedrock AgentCore | DIFERIR / no migrar |

---

## L21 — Sandbox Agents

### En el despacho (negocio)
Imagina un pasante que no solo redacta: abre terminal, crea carpetas, instala librerías, genera un mini-frontend y te manda un link. Eso es sandbox. En penal-víctimas, ese playground **sobre datos de casos** es riesgo (fuga, shell, dependencias) sin diseño de aislamiento + HITL + 1581.

### Qué enseña el curso
- Sandbox Agent ≠ Agent de texto: tiene **workspace** (playground).  
- Separación: **harness** (orquestación) vs **compute sandbox** (donde vive/trabaja).  
- **Siete componentes/primitivos** (definición del agent + manifest, capabilities, etc.).  
- Más allá de code interpreter: git, pip, artefactos reutilizables, frontends.  
- Skills + memory pueden vivir en el manifest.

### Cómo está en este producto
No hay Sandbox Agent. El “trabajo” del despacho es texto + tools + planes.  
Code interpreter hosted (L09) también Won’t.

### Decisión
**DIFERIR.** No activar sandbox OpenAI en el Gerente ni en especialistas de prod.

---

## L22 — SandboxRunConfig, Manifest and Capabilities

### En el despacho (negocio)
Manifest = qué archivos/carpetas/repos entran al “escritorio” del agente al arrancar. Capabilities = qué puede hacer (shell, files, memory…). Sin eso el sandbox es “sala vacía”.

### Qué enseña el curso
- Spec sandbox: `default` manifests + capabilities (+ tools/model/instructions).  
- Tipos de mount: file/dir, local file/dir (copiar desde fuera), git repo, cloud storage.  
- **SandboxRunConfig**: client, session, manifest override → artefacto deployable.  
- Capabilities: default típico **shell + file access + memory compaction**; opcionales **skills + memory**.  
- Ejemplo curso: limpiar CSVs con pandas y escribir summary.

### Mapa a firma (sin portar)
| Curso | Equivalente mental |
|---|---|
| Manifest “qué entra al workspace” | Qué KB/expediente/fragmentos inyectáis (RAG slim, G1) |
| Capabilities allowlist | Superficie tools del Gerente (sin high-risk en chat) |
| SandboxRunConfig | `RunConfig` + settings Render (otro runtime) |

### Decisión
**DIFERIR** implementación. Usar solo como **analogía** de gobernanza (G1–G10).

---

## L23 — Sandbox Provider and Mount Credentials

### En el despacho (negocio)
Quién alquila la máquina del pasante (local, Docker, SaaS) y cómo se meten contraseñas/API keys al workspace sin filtrarlas al chat.

### Qué enseña el curso
- Providers: unix local → Docker → **~7 SaaS nativos** OpenAI.  
- Mount credentials / params para storages y puertos (p.ej. frontend expuesto con URL del provider).  
- Credenciales mal montadas = fuga.

### Producto
Secrets = **env Render** (`OPENAI_API_KEY`, Slack, `DATABASE_URL`). No montar secretos de casos en sandbox de terceros.

### Decisión
**DIFERIR.** Mantener secrets en env; rotación vía ops (runbook).

---

## L24 — AGENTS.md, Skills and Sandbox Memory

### En el despacho (negocio)
- **AGENTS.md**: reglas del *proyecto/workspace* (cómo trabajar en esta carpeta).  
- **Skills**: playbooks en markdown (“cómo hacer X”).  
- **Sandbox memory**: el agente anota aprendizajes (p.ej. “necesito pandas”) — distinta del historial de chat.

### Qué enseña el curso
- Instructions del Agent ≠ AGENTS.md (este es del workspace, compartible entre agents).  
- Skills = automatizaciones/best practices en texto (+ estructura tags/código).  
- Memory larga vs **session** (chat): propósitos distintos; se combinan.  
- Persistencia de memory en files/folders del sandbox.

### Producto (ya existe el equivalente útil)
| Curso | Firma |
|---|---|
| Skills MD sandbox | `agente/skills/**/SKILL.md` |
| AGENTS.md workspace | Prompts/gobernanza en `agente/prompts` + G1–G10 |
| Session chat | Postgres `RepositoryAgentSession` (L12/L13) |
| Sandbox long-term memory files | **No** — estado = expediente/DB, no auto-escritura libre del modelo en FS |

### Decisión
**DIFERIR** portar sandbox memory/AGENTS.md de OpenAI.  
**Mantener y mejorar** skills/prompts propios (fuera de este bloque).

---

## L25 — Sandbox Agents State and Composition

### En el despacho (negocio)
Poder pausar/reanudar un “proyecto” del pasante: no solo el chat, sino archivos y estado de corrida.

### Qué enseña el curso
Tres capas de estado:
1. **Run state** (harness) — corrida en curso / resume.  
2. **Session state** — conversación.  
3. **Snapshots** — archivos del workspace (lo más simple de entender).  
Composición: mezclar agents normales + sandbox; patrones de handoff/as_tool en ese mundo.

### Producto
| Capa curso | Firma |
|---|---|
| Run state | Plan executor + reclaim stale (300s) |
| Session | Chat Postgres |
| Snapshots FS | No; artefactos = drafts/planes en DB |

### Decisión
**DIFERIR** sandbox state. Estado productizable = DB.

---

## L26 — Lab: SandboxAgents

### Curso
Lab: calculator / skills / memory / manifest; agent crea skills y memory summary; flush a artefacts.

### Producto
**No portar.** El valor pedagógico ya está en L21–L25.

### Decisión
**DIFERIR / no portar lab.**

---

## L27 — Lab: SQL Analyzer Agent

### Curso
Lab: agente con tools hacia DB, analizar SQL, etc. (sandbox + function tools).

### Producto
No es el caso litigante core. Conectar un agente con shell/SQL a datos reales de despacho sin diseño = riesgo alto.

### Decisión
**DIFERIR / no portar.** Consultas a Postgres propias = código/ops controlado, no lab sandbox.

---

## L28 — Bonus AWS Bedrock AgentCore

### En el despacho (negocio)
“Llevar el agente del laptop a AWS con isolation, memoria, eval, gateway MCP…”.

### Qué enseña el curso
- Gaps de producción más allá de “meter en un container”.  
- ~**10 primitives/services** AgentCore (runtime, memory short/long, eval online/offline, identity, gateway…).  
- Session isolation (CPU/memoria por sesión).  
- Wrapper Python para hostear OpenAI agents en AgentCore.

### Producto
Deploy = **Render + Postgres**. Bedrock = otro cloud, otra factura, otro modelo de ops/compliance.

### Decisión
**DIFERIR / no migrar.** Si algún día hay requisito enterprise AWS, reabrir con evaluación (no “porque L28”).

---

## High-level config

> **Para L21–L28: DIFERIR.**  
> No Sandbox Agents, no labs, no Bedrock.  
> Equivalencias: skills/prompts/G1/Postgres/trazas ya cubren lo útil del despacho.  
> L18–L20 se abren **cuando implementes voz** (con 1581/2300).

| Ítem | Acción | Backlog |
|---|---|---|
| Código sandbox/Bedrock | No | Won’t |
| Skills propias | Mantener | — |
| Voice L18–L20 | Aparcado | Reabrir con voz |

---

## Costos / productizar

Sandbox/Bedrock suben TCO (compute, storage, credenciales, superficie) sin mejorar el flujo abogado→Gerente→HITL en web.  
Productizar ahora = batch **B01–B05 + B12–B15**, no este bloque.

---

## Qué NO hacer

- No montar sandbox con expedientes reales.  
- No lab SQL analyzer sobre DB de prod.  
- No migrar a Bedrock “para completar el curso”.  
- No sustituir `agente/skills` por solo AGENTS.md sandbox.
