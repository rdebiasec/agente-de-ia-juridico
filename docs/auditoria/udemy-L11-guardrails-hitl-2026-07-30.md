# Udemy L11 — Guardrails and Human Review — 2026-07-30 (clase formal · reabertura)

**Fase:** HECHO_CLASE  
**Orden pedagógico:** #14  
**Decisión global:** DEJAR QUIETO en runtime (hardening ya hecho fuera de orden) · ops Slack en backlog  
**Batch:** sin Must nuevo de L11; **B12** Should = Slack HITL ops; Must sigue B01–B05  
**Fuente:** `txt/11_guardrails_and_human_review.txt` (ok)  
**Código previo:** [`udemy-L11-guardrails-hitl-2026-07-27.md`](./udemy-L11-guardrails-hitl-2026-07-27.md) · `tests/test_l11_hitl.py`

---

## 0. Veredicto

L11 = proteger **3 superficies** (input / tools / output) + ciclo **humano aprueba → agente continúa**.  
En la firma: guardrails SDK + PII + scope penal ya viven; HITL de alto riesgo = **plan / borrador** (no resume-by-state mid-chat del lab).  
Clase formal cierra el puesto #14; código L11 ya PASS — no reimplementar ahora.

---

## 1. Qué enseña el curso (sin omitir)

### Por qué importan
Prompt injection / reputación (chatbot que “vende” a $1), fuga PII/interna, decisiones de dinero fuera de política, off-topic caro, usuarios maliciosos.

### 3 superficies
1. **Input guardrails** — decorador; un guardrail por idea (topic, injection, policy); keywords / regex / LLM; acceso a context + agent + input; tripwire.  
2. **Output guardrails** — igual patrón; PII/regex; `GuardrailFunctionOutput` = output_info + tripwire_triggered.  
3. **Tool guardrails / needs_approval** — tool crítica → pause del loop → `interruptions` → humano → resume con `state` serializado (JSON/DB; puede tardar horas).

### Guardrails vs approvals
- Guardrails: injection, topic, PII, filtros.  
- Approvals: tools críticas (dinero, sistemas sensibles) — **approval stuck to tools, not the agent**.

### Best practices curso
Empezar tripwire=false → mirar logs → endurecer; muchos guardrails finos; output_info rico para audit; probar pause/serialize/resume.

---

## 2. Traducción firma virtual

### Negocio
La IA **propone**; el abogado **aprueba** memorial/tutela/plan. Guardrails evitan off-topic, injection y fugas; HITL evita que un borrador “salga” sin cola de revisión.

**Ejemplos**

| Entrada | Comportamiento deseado |
|---|---|
| Injection / “ignora instrucciones” | Input tripwire / bloqueo |
| “Divorcio / arrendamiento…” sin ancla penal | Fuera de alcance |
| Cita norma sin `[PENDIENTE_…]` | Soft flag `invention_suspect` (auditable; HITL revisa) |
| “Redacte memorial” | Plan HITL — no tool libre mid-chat |
| Borrador creado | `draft_id` + bandeja; si falla creación → traza `blocked` (no “pending” mentiroso) |

### Mapa curso → producto

| Curso | Aquí |
|---|---|
| Input guardrails | `sdk_guardrails.poc_input_guardrails` (+ injection, scope) |
| Output guardrails | POC/especialistas/redactor/tutela/calidad; PII mask |
| Tool guardrails | `poc_tool_input/output_guardrails` en as_tool |
| needs_approval + interruptions | Path existe; **chat** `require_tool_approval=False` + high-risk tools off |
| Pause / serialize state / resume | Equivalente producto = **plan aprobado** + drafts HITL (web/Slack), no freeze del mismo Runner en chat |
| Approvals “sobre tools” | Redactor/tutela solo vía plan; calidad puede bloquear entrega |

Config normativa: `config/guardrails/…`.

---

## 3. Dualidad HITL (importante)

```text
Curso lab:  tool needs_approval → interruptions → save state → human → resume Runner
Firma chat: high-risk tools OFF → "apruebe plan" → plan_executor (nuevos runs)
Firma draft: needs_human_review → crear_borrador → abogado / Slack
```

No es un bug: es productización jurídica (respuesta cerrada + workflow explícito).

---

## 4. High-level

> **DEJAR QUIETO el runtime.** Hardening L11 (draft honest, invention_suspect, require_tool_approval=False en chat, tests) ya hecho.  
> Batch Must no cambia por L11. Ops: Slack HITL en Render = **B12**.  
> No adoptar resume-by-state mid-chat “porque el curso”.

| Ítem | Acción | Backlog |
|---|---|---|
| Guardrails input/output/tool | Mantener | — |
| Plan HITL alto riesgo | Mantener | — |
| Draft traza honesta | Hecho | — |
| Slack approvers en Render | Ops | **B12** Should |
| Resume state SDK en chat | No | Won’t |

---

## 5. Costos / productizar

- Guardrails baratos (regex) evitan runs off-topic = **ahorro tokens**.  
- Tripwire duro de más → fricción abogado; soft flags (citas) = audit sin matar el turno.  
- HITL plan evita $ high-risk (`gpt-4o`) sin aprobación = **control de costo**.  
- Productizar = cola de revisión creíble (draft real o blocked), no “pending” fantasma.

---

## 6. Qué NO hacer

- No high-risk tools libres en chat.  
- No tripwirear cada cita (rompe flujo; usáis soft flag).  
- No mentir en traza si no hay draft.  
- No depender solo de interruptions SDK para memoriales.

---

## Cierre

Siguiente: **L12 — Session Management**.
