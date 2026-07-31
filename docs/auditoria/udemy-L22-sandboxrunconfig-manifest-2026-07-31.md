# Udemy L22 — SandboxRunConfig, Manifest and Capabilities — 2026-07-31

**Fase:** HECHO_CLASE  
**Orden pedagógico:** #22  
**Decisión global:** **DIFERIR** · no código · usar solo como analogía de gobernanza  
**Fuente:** `txt/22_sandboxrunconfig_manifest_and_capabilities.txt` (ok)  
**Siguiente:** L23 — Sandbox Provider and Mount Credentials

---

## 0. Veredicto

L22 enseña **cómo se hace deployable** un Sandbox Agent: workspace (manifest), allowlist de poderes (capabilities) y `SandboxRunConfig` (client + session + override).  
En el repo: no hay sandbox; el equivalente mental es G1/tools slim + `RunConfig` + expediente inyectado.  
¿Tocar config? No. **DIFERIR** implementación; **aprender** el mapa.

---

## 1. Clase del concepto

### Problema
Sin workspace el sandbox es “sala vacía”. Hay que decidir qué entra al boot, qué puede hacer el agente, y con qué client/session se corre.

### Concepto
1. **Manifest** — entradas al `workspace/` (provider-agnostic):  
   - file / directory (dentro del sandbox)  
   - local file / local directory (copiar desde fuera)  
   - git repo  
   - cloud mounts (S3, etc.)  
   Común: `path` relativo a `workspace`. Opcional: env del container, POSIX users/groups.
2. **Capabilities** (5): default = shell + file system + auto-compaction; opcionales = skills + memory.
3. **SandboxRunConfig** — extensión de RunConfig: `client` (p.ej. unix local) + `session` (live/resume) + `manifest_override` opcional + max_turns / model_settings / workflow_name.  
   `Runner.run` + `RunResult` igual que agent normal.

### Lab del curso
Finance agent: monta `data/` (CSV trimestrales) → shell+FS → limpia con pandas → escribe `out/`. No portar.

### Traducción firma
| Curso | Firma |
|---|---|
| Manifest “qué entra” | Qué KB/expediente/fragmentos inyectáis (G1, RAG slim) |
| Capabilities allowlist | Superficie tools del Gerente (`REAL_FUNCTION_TOOL_NAMES`, high-risk off) |
| SandboxRunConfig | `RunConfig(workflow_name=…)` + settings (`agent_max_turns`) |
| out/ artefactos FS | Drafts/planes en DB + HITL |

### Anti-mitos
| Mito | Realidad |
|---|---|
| “Hay que montar S3/git al Gerente” | El despacho lee expediente vía tools, no mounts |
| “Capabilities default = prod segura” | Default incluye **shell** — peligroso con casos |
| “SandboxRunConfig reemplaza RunConfig” | Es extensión para otro runtime |

---

## 2. Mapa en ESTE proyecto

| Idea curso | Ruta/símbolo | Práctica |
|---|---|---|
| Manifest entries | Inyección contexto / RAG | G1; no full dump |
| Capabilities | `get_knowledge_tools` · allowlist | Slim en chat |
| SandboxRunConfig.client | — | Ausente |
| RunConfig | `runner.py` · `plan_executor.py` | `firma-juridica` / `firma-plan-step` |
| max_turns | `settings.agent_max_turns` | Ya acotado |
| Artefacto out/ | planes / drafts DB | HITL abogado |

---

## 3. High-level

> **Para L22: DIFERIR.** No portar Manifest/Capabilities/SandboxRunConfig.  
> Usar como analogía: “qué entra / qué puede / cómo se corre” → G1 + tools slim + RunConfig propio.

| Ítem | Hoy | Recomendación | Prioridad |
|---|---|---|---|
| SandboxRunConfig | Ausente | No | Won’t |
| Manifest mounts | Ausente | No | Won’t |
| Allowlist tools | Ya | Mantener | — |
| RunConfig propio | Ya | Mantener | — |

---

## 4. Desempeño

| Eje | Efecto si se portara |
|---|---|
| Calidad jurídica | No mejora tipicidad; mounts mal hechos = fuga de hechos |
| Costo/ruido | Shell+pandas en sandbox = $ y ruido |
| Confianza | Baja si el abogado no ve el allowlist |
| Latencia | Peor |

---

## 5. Mini-laboratorio

| Entrada | Debería | Hoy | |
|---|---|---|---|
| Chat con expediente | Solo fragmentos autorizados | RAG/tools slim | PASS |
| Tool high-risk en chat | Off / plan | High-risk off | PASS |
| “Montá el repo del cliente” | No | No sandbox | PASS |
| Override de “qué entra” por turno | RunConfig/context, no manifest | context session | PASS patrón |
| max_turns | Acotado | settings | PASS |

---

## 6. Qué NO hacer

- No activar capabilities.default (trae shell) sobre datos de casos.  
- No montar directorios locales del abogado al agente.  
- No confundir compactación de sandbox con compactación de session chat (L12).

---

## 7. Cierre

`cerrar L22, diferir` → siguiente `siguiente L23`
