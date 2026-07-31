# Udemy L21 — Sandbox Agents — 2026-07-31 (clase formal)

**Fase:** HECHO_CLASE  
**Orden pedagógico:** #21  
**Decisión global:** **DIFERIR** · no código  
**Fuente:** `txt/21_sandbox_agents.txt` (ok)  
**Siguiente:** L22 — SandboxRunConfig, Manifest and Capabilities

---

## 0. Veredicto

Sandbox Agent = Agent de texto **+ playground** (workspace, shell, packages, mounts, preview URL, sesión resumible).  
En el repo: **ausente** (cero imports Sandbox*).  
Mejora desempeño litigante web: **no** (más superficie, $ y riesgo 1581).  
Config: no tocar; Won’t del batch.

---

## 1. Clase del concepto

### Problema
Code interpreter solo ejecuta código. Casos reales pedían “pasante con PC”: git, carpetas, pip, artefactos reutilizables, incluso un frontend con link.

### Concepto
- **Sandbox Agent** = superset del Agent (name, instructions, model, tools, handoffs, output_type) + `default_manifest` + `capabilities`.  
- **Harness vs compute:** harness = orquestación (`Runner`); compute = donde vive/trabaja (FS, shell, deps). Hay frontera de seguridad.  
- **7 piezas:** agent spec · manifest · capabilities · sandbox client · sandbox session · SandboxRunConfig · save state (workspace/deps).

### Capacidades nuevas (curso)
file storage · shell · packages · mounts (git/S3…) · preview URLs · session state resumible.

### Lab del curso
Intro conceptual (lab concreto en L26). Escenario: research → Excel → dashboard con preview.

### Traducción firma
El “trabajo” del despacho = texto + function tools + as_tool + planes HITL + Postgres.  
No hay shell ni workspace FS del modelo sobre expedientes.

### Anti-mitos
| Mito | Realidad |
|---|---|
| “Sandbox = code interpreter” | Va mucho más lejos (git, pip, UI) |
| “Hay que usarlo para productizar” | Productizar firma ≠ playground |
| “Más poder = mejor abogado” | Más poder sin HITL/aislamiento = más riesgo |

---

## 2. Mapa en ESTE proyecto

```
Curso Sandbox Agent          Firma virtual (hoy)
─────────────────────        ───────────────────
Agent + playground      →    Agent texto (Gerente)
manifest workspace      →    RAG/expediente inyectado (G1)
shell / packages        →    (no) · tools Python controladas
preview URL             →    desk web propio (static/)
sandbox session state   →    Postgres chat + planes
```

| Idea curso | Ruta/símbolo | Práctica |
|---|---|---|
| Agent de texto | `src/agents/runner.py` · Gerente | Única voz |
| Playground sandbox | — | Ausente |
| Code interpreter hosted | L09 Won’t | No |
| Skills propias | `agente/skills/**` | Ya (≠ sandbox skills) |
| Gobernanza superficie | G1–G10 · tools slim | Allowlist |

---

## 3. High-level

> **Para L21: DIFERIR.**  
> No activar Sandbox Agents en Gerente ni especialistas.  
> El producto productizable sigue siendo web + as_tool + HITL + Postgres en Render.

| Ítem | Hoy | Recomendación | Prioridad | Impacto agentes | Esfuerzo |
|---|---|---|---|---|---|
| Sandbox Agent SDK | Ausente | No añadir | Won’t | Alto riesgo | Alto |
| Shell sobre casos | No | Mantener no | — | — | — |
| Equivalente mental | skills + tools + DB | Usar en clase L22+ | — | Pedagógico | — |

---

## 4. Desempeño (4 ejes)

| Eje | Efecto si se portara |
|---|---|
| Calidad jurídica | No sube citas/hechos; puede inventar vía shell |
| Costo/ruido | Sube (compute + tokens + deps) |
| Confianza abogado | Baja si hay shell/FS opacos |
| Latencia/fricción | Peor (spin sandbox) |

---

## 5. Mini-laboratorio

| Entrada | Debería | Hoy | PASS/GAP |
|---|---|---|---|
| “Redactá memorial” | Gerente + tools + draft HITL | Así | PASS |
| “Instalá pandas y limpia CSV del caso” | Rechazar / no shell | No hay sandbox | PASS (por ausencia) |
| “Abrí terminal en el expediente” | Bloquear | No expuesto | PASS |
| “Generá un dashboard HTML del caso” | Desk propio / no preview sandbox | static desk | PASS · no sandbox |
| Multi-agente compartiendo carpeta FS | as_tool + DB, no FS compartido | as_tool | PASS patrón |

---

## 6. Qué NO hacer

- No montar sandbox con expedientes reales.  
- No confundir “productizar” con “tener playground OpenClaw-like”.  
- No activar sandbox “porque es lo último del SDK”.

---

## 7. Cierre

Texto: `cerrar L21, diferir`  
Siguiente clase: **L22 — SandboxRunConfig, Manifest and Capabilities**.
