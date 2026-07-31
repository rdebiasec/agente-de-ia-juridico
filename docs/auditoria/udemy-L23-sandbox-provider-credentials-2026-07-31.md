# Udemy L23 — Sandbox Provider and Mount Credentials — 2026-07-31

**Fase:** HECHO_CLASE  
**Orden pedagógico:** #23  
**Decisión global:** **DIFERIR** · no código · secrets = env Render  
**Fuente:** `txt/23_sandbox_provider_and_mount_credentials.txt` (ok)  
**Siguiente:** L24 — AGENTS.md, Skills and Sandbox Memory

---

## 0. Veredicto

L23 = **dónde corre** el sandbox (9 providers) y **cómo montar credenciales** sin que el LLM las vea.  
Repo: deploy = **Render + Postgres**; secrets en env (`Settings` / pydantic). Sin sandbox client.  
**DIFERIR** providers E2B/Vercel/etc. Mantener modelo de secretos actual.

---

## 1. Clase del concepto

### Problema
El mismo Sandbox Agent debe poder pasar de laptop → Docker → SaaS sin reescribir lógica. Credenciales mal puestas = fuga.

### Concepto
**9 clients:** unix local · Docker · 7 SaaS nativos (E2B, Modal, Daytona, Runloop, Cloudflare, Vercel, Blackcell/Plexel — nombres del curso).

| Enfoque | Aislamiento multi-usuario | Escala |
|---|---|---|
| Unix local | Custom a tu cargo | Solo dev |
| Docker | Medio | Mejor |
| Micro-VM (E2B, Runloop…) | Dedicado por usuario | Prod-grade curso |

**Credenciales en 2 capas (curso):**
1. **Harness (ocultas al LLM):** provider API keys + mount storage creds (en client / manifest).  
2. **Runtime secrets:** vía `RunContext` (p.ej. DB) — el patrón L05 que ya conocéis.

**Preview URL:** muchos providers exponen puerto ~8000 → hostname para ver frontend generado + HITL humano (merge).

### Lab
Swap de `client` en SandboxRunConfig; no hay lab de firmas.

### Traducción firma
| Curso | Firma |
|---|---|
| Provider sandbox | **Render** (web app), no E2B |
| Provider secrets | Env Render / `.env` → `src/config.py` Settings |
| Mount storage creds | No mounts; no S3 de casos al modelo |
| Runtime secrets (RunContext) | Contexto de sesión/expediente; no meter API keys en prompt |
| Preview URL | Desk `static/` propio |
| Aislamiento multi-usuario | Session + anti-IDOR expediente (no micro-VM) |

### Anti-mitos
| Mito | Realidad |
|---|---|
| “Hay que probar los 7 SaaS” | No aportan al flujo abogado→Gerente |
| “Si el LLM no ve la key, ya es 1581-ok” | El **dato de caso** en el sandbox sigue siendo tratamiento |
| “Preview = desk” | Preview es UI efímera del sandbox; desk es producto |

---

## 2. Mapa en ESTE proyecto

| Idea curso | Ruta/símbolo | Práctica |
|---|---|---|
| Client / provider | Render deploy | `deploy/docker-compose.yml` · Render |
| Secrets env | `src/config.py` Settings | OPENAI, DATABASE_URL, Slack, SESSION_SECRET… |
| RunContext secrets | L05 / runner context | Expediente/session; no keys en chat |
| Preview | `static/desk/` | UI firmada |
| Multi-tenant | subject_id + resolve_expediente | Anti-IDOR |

---

## 3. High-level

> **Para L23: DIFERIR.** No adoptar providers sandbox.  
> Secrets = env Render. No montar storages de casos al compute del modelo.  
> Preview SaaS ≠ desk del abogado.

| Ítem | Hoy | Recomendación | Prioridad |
|---|---|---|---|
| E2B/Vercel/Daytona… | Ausente | No | Won’t |
| Secrets en env | Ya | Mantener + rotación ops | — |
| Mount S3 casos | No | Mantener no | — |
| Keys en prompt/tools result | Evitar | Seguir evitando | — |

---

## 4. Desempeño

| Eje | Si se portara |
|---|---|
| Calidad jurídica | No sube |
| Costo | + SaaS sandbox por sesión |
| Confianza | Baja si casos viven en micro-VM de tercero sin DPA |
| Latencia | Spin provider |

---

## 5. Mini-laboratorio

| Entrada | Debería | Hoy | |
|---|---|---|---|
| API keys solo en env | Sí | Settings | PASS |
| LLM no imprime DATABASE_URL | Sí | No inyectar keys en tools | PASS (disciplina) |
| Caso A no ve caso B | Anti-IDOR | resolve_expediente | PASS |
| “Abrí preview E2B del expediente” | No | Sin sandbox | PASS |
| Desk abogado | UI propia | static/desk | PASS |

---

## 6. Qué NO hacer

- No montar bucket/carpeta de expedientes en sandbox SaaS.  
- No poner secrets en instructions ni en respuestas de tools.  
- No confundir “LLM no ve la key” con cumplimiento 1581 del **contenido**.

---

## 7. Cierre

`cerrar L23, diferir` → `siguiente L24`
