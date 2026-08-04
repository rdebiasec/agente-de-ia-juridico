# Checklist Udemy — cierre por lección (orden pedagógico)

**Fecha reorden:** 2026-07-27  
**Curso:** Mastering Agents with OpenAI Agents SDK & OpenAI Codex (L01–L28)  
**Arranque oficial:** **L01** (propósito), no L11  

| Doc | Rol |
|---|---|
| [`REGISTRO_UDEMY_REVISIONES.md`](./REGISTRO_UDEMY_REVISIONES.md) | Bitácora |
| [`PLAN_UDEMY_CORTO.md`](./PLAN_UDEMY_CORTO.md) | Orden + Ahora |
| [`PROMPT_CLASE_UDEMY.md`](./PROMPT_CLASE_UDEMY.md) | Prompt de clase |
| [`plan-udemy-agents-sdk-aplicacion.md`](./plan-udemy-agents-sdk-aplicacion.md) | Tablero 28 |
| [`udemy-plan-dashboard.html`](./udemy-plan-dashboard.html) | Vista visual |

---

## Cómo usar

1. Tomar la siguiente lección del **orden oficial** (abajo).  
2. Correr clase con [`PROMPT_CLASE_UDEMY.md`](./PROMPT_CLASE_UDEMY.md).  
3. Decidir: DEJAR QUIETO / AJUSTAR / DIFERIR.  
4. Si AJUSTAR: solo tras `aprobado, ejecuta Lxx`.  
5. Actualizar sección Lxx en `docs/auditoria/UDEMY_LISTA_CAMBIOS.md`  
6. Actualizar **todas** las listas canónicas.

### Ritual de cierre

- [ ] Clase entregada (veredicto high-level)
- [ ] Auditoría `docs/auditoria/udemy-Lxx-*.md` creada/actualizada
- [ ] REGISTRO + PLAN_CORTO + tablero + dashboard sincronizados
- [ ] Premisas: única voz POC, sin handoffs peer, HITL, sin voz/WhatsApp sin 1581

---

## Orden oficial y progreso

| # | Lección | Modo | Cerrada |
|---|---|---|---|
| 1 | L01 Overview | CLASE + mapa | [x] |
| 2 | L02 Setup | CLASE + mapa | [x] |
| 3 | L06 Basic Agents (POC) | CLASE + mapa | [x] |
| 4 | L03 Structured output | CLASE → AJUSTE | [x] |
| 5 | L04 Model Settings | CLASE → AJUSTE | [x] |
| 6 | L05 RunContext | CLASE → AJUSTE | [x] |
| 7 | L07 Run Loop | CLASE + decisión | [x] |
| 8 | L08 RunResult | CLASE → AJUSTE | [x] |
| 9 | L09 Hosted Tools | CLASE + no aplicar | [x] |
| 10 | L10 as_tool | CLASE → AJUSTE | [x] |
| 11 | L15 MCP | CLASE + decisión | [x] |
| 12 | L14 Handoffs (adaptado) | CLASE + adaptación | [x] |
| 13 | L16 Lab multi-agents | CLASE + adaptación | [x] |
| 14 | L11 Guardrails + HITL | CLASE → AJUSTE | [x] |
| 15 | L12 Sessions | CLASE → AJUSTE | [x] |
| 16 | L13 Sessions prod | CLASE → AJUSTE | [x] |
| 17 | L17 Monitoring | CLASE → AJUSTE | [x] |
| 18–20 | L18–L20 Voice | Aparcada hasta voz | [ ] |
| 18–20 | L18–L20 Voice | Aparcada hasta voz | [ ] |
| 21–28 | L21–L28 Sandbox→Bedrock | Hilo explicativo + DIFERIR | [x] |

**Ahora:** L21–L28 hechas (diferir). L18–L20 aparcadas. Código: `aprobado, ejecuta batch udemy`.

---

## Por lección — casillas mínimas

Para cada Lxx, al cerrar:

### Plantilla

- [ ] Antes: leí KB/transcript o anoté gap de fuente
- [ ] Mapa: equivalente en este repo (o AUSENTE)
- [ ] Mensaje high-level escrito (DEJAR / AJUSTAR / DIFERIR)
- [ ] Si AJUSTE: PASS/FAIL + tests
- [ ] Listas canónicas actualizadas

### L01 — Overview

- [x] Propósito Agents SDK explicado en lenguaje despacho
- [x] Mapa: POC + as_tool + HITL + Postgres (sin lab)
- [x] Caption inválida anotada; fuentes = KB + ESTADO + plan-rediseno
- [x] DEJAR QUIETO (sin código)
- [x] Auditoría L01 escrita
- [x] Listas actualizadas

### L02 — Setup

- [x] Mapa local/Render/API key
- [x] DEJAR QUIETO (no rehacer lab Codex)
- [x] Listas actualizadas

### L06 — Basic Agents (POC)

- [x] Definir Agent = coordinador_caso
- [x] Caption gap → código `orchestrator.py`
- [x] Listas actualizadas

### L03 … L10, L15, L14, L16, L11, L12, L13, L17

Usar plantilla + sección detallada en auditoría `docs/auditoria/udemy-Lxx-*.md`.  
Evidencias previas (L03/L10/L11/…) se **reabren** en su puesto del orden; no cuentan como cierre formal hasta entonces.

### L18–L20 — Voice (aparcada)

- [ ] Reabrir al implementar voz (+ 1581/2300)
- [ ] Clase formal L18→L20 + backlog entonces

### L21 — Sandbox Agents (hecho · diferir)

- [x] Concepto harness vs compute + 7 piezas
- [x] Mapa firma (ausente sandbox)
- [x] DIFERIR + listas

### L22 — SandboxRunConfig / Manifest (hecho · diferir)

- [x] Manifest / capabilities / SandboxRunConfig
- [x] Analogía G1 + tools + RunConfig
- [x] DIFERIR + listas

### L23 — Provider + credentials (hecho · diferir)

- [x] 9 providers + capas de secretos
- [x] Mapa env Render / no mounts casos
- [x] DIFERIR + listas

### L24–L28 — Hecho vía hilo explicativo

- [x] L24 reexplicada (skills vs memory)
- [x] L25 state/composition
- [x] L26–L27 labs no portar
- [x] L28 Bedrock no migrar
- [x] Guía: `udemy-L21-L28-hilo-explicativo-2026-07-31.md`

---

## Matriz rápida

| # | Lección | Clase | Ajuste/Diferir | Listas |
|---|---|---|---|---|
| 1 | L01 | [x] | DEJAR QUIETO | [x] |
| 2 | L02 | [x] | DEJAR QUIETO | [x] |
| 3 | L06 | [x] | DEJAR QUIETO | [x] |
| 4 | L03 | [x] | DEJAR QUIETO | [x] |
| 5 | L04 | [x] | AJUSTE pend. ModelSettings | [x] |
| 6 | L05 | [x] | AJUSTE pend. context= | [x] |
| 7 | L07 | [x] | DEJAR QUIETO | [x] |
| 8 | L08 | [x] | AJUSTE opcional new_items/smoke | [x] |
| 9 | L09 | [x] | DEJAR QUIETO / no aplicar | [x] |
| 10 | L10 | [x] | DEJAR QUIETO (hardening previo) | [x] |
| 11 | L15 | [x] | no MCP real; B11 rename opc. | [x] |
| 12 | L14 | [x] | adaptar · Won’t peer | [x] |
| 13 | L16 | [x] | no portar lab | [x] |
| 14 | L11 | [x] | DEJAR QUIETO · B12 Slack ops | [x] |
| 15 | L12 | [x] | B13 compactación | [x] |
| 16 | L13 | [x] | B14 idle≠retención | [x] |
| 17 | L17 | [x] | B04·B07·B15 | [x] |
| 18–20 | L18–L20 | [ ] | APARCADA hasta voz | [ ] |
| 21 | L21 | [x] | DIFERIR | [x] |
| 22 | L22 | [x] | DIFERIR | [x] |
| 23 | L23 | [x] | DIFERIR | [x] |
| 24 | L24 | [x] | DIFERIR portar · skills OK | [x] |
| 25 | L25 | [x] | DIFERIR | [x] |
| 26 | L26 | [x] | no portar | [x] |
| 27 | L27 | [x] | no portar | [x] |
| 28 | L28 | [x] | no migrar | [x] |

## Definición de lección terminada

1. Propósito de la lección quedó claro en el registro.  
2. Mapa en este repo (o diferido con razón).  
3. High-level DEJAR / AJUSTAR / DIFERIR ejecutado según acuerdo.  
4. Listas canónicas sincronizadas.  
5. Sin anti-patrón (handoffs peer, web_search libre, voz sin 1581, lab portado).
