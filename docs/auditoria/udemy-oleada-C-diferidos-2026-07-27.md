# Udemy Oleada C — Diferidos documentales — 2026-07-27

**Fase:** AUDITORIA_DESPUES (cierre documental; sin implementación)  
**Prioridad:** Diferido  
**Tablero:** [`plan-udemy-agents-sdk-aplicacion.md`](../canon/plan-udemy-agents-sdk-aplicacion.md)

Cierre de L01–L02, L06, L18–L28. No se portan labs. Cada fila queda `Diferido` con razón breve.

---

## Checklist Antes / Después / Decisión

| Lección | Antes (producto) | Después | Decisión / por qué |
|---|---|---|---|
| L01 Overview | Arquitectura Agents SDK en prod; caption Udemy inválida | Sin código | Overview ya vivido en el producto; fuente transcript rota |
| L02 Setup Codex + API Key | Local + Render con API key | Sin código | Setup operativo; no rehacer lab |
| L06 Lab Basic Agents | Sin caption URL | Sin código | Gap de fuente; cubrir vía L03+L05+código actual |
| L18 Realtime Voice | Sin canal voz | Sin código | Voz/WhatsApp bloqueados sin evaluación 1581/2300 |
| L19 Chained Voice | N/A | Sin código | Idem L18 |
| L20 Lab Voice | N/A | Sin código | Idem L18 |
| L21 Sandbox Agents | Runtime Render | Sin código | Sandbox OpenAI no es el hosting |
| L22 SandboxRunConfig / Manifest | Gobernanza vía G1–G10 + tool guardrails | Solo mapeo conceptual | Capabilities ≈ guardrails/tools existentes |
| L23 Provider / Mount Credentials | Secrets en env Render | Sin código | Modelo de secretos ya definido |
| L24 AGENTS.md / Skills / Sandbox Memory | `agente/skills` + prompts versionados en `/auditoria` | Sin portar AGENTS.md sandbox | Equivalente de producto ya existe |
| L25 Sandbox State / Composition | Ledger expediente + planes Postgres | Sin código | Estado vive en DB, no en sandbox |
| L26 Lab SandboxAgents | N/A | Sin código | Runtime distinto |
| L27 Lab SQL Analyzer | N/A | Sin código | Sin caso de uso abogado inmediato |
| L28 AWS Bedrock AgentCore | Deploy Render | Sin código | Bedrock no es target de deploy |

---

## Relevancia al producto abogado

Diferir estas lecciones **protege** el producto: evita canales no evaluados (voz), runtime ajeno (sandbox/Bedrock) y labs que no mejoran el despacho penal-víctimas.

## Qué NO hacer

- No implementar voz/WhatsApp “para completar el curso”.
- No migrar a Bedrock/Sandbox por el bonus L28.
- No publicar transcripts Udemy.

## PASS / FAIL

| Verificación | PASS | FAIL | Resultado |
|---|---|---|---|
| Filas L01–L02, L06, L18–L28 en tablero | Estado `Diferido` + razón | Pendiente o P0 erróneo | PASS |
| Código de voz/sandbox/Bedrock añadido por este cierre | Ausente | Presente | PASS |

## Pendiente humano

- Si cambia la premisa de canal (evaluación 1581/2300 aprobada) o de hosting, reabrir solo las filas afectadas.

## Estado tras esta pasada

Oleada C **cerrada documentalmente**. Tablero maestro actualizado en la misma fecha.
