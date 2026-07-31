# Udemy L16 — Lab: Multi-Agents Handoffs and As Tools — 2026-07-30 (clase formal adaptada)

**Fase:** HECHO_CLASE  
**Orden pedagógico:** #13  
**Decisión global:** DEJAR QUIETO / **no portar lab** — quedarse con el patrón as_tool (+ planes)  
**Batch:** sin Must nuevo  
**Fuente:** `txt/16_lab_multi_agents_handoffs_and_as_tools.txt` (ok)  
**Previo:** [`udemy-L14-L16-handoffs-adaptado-2026-07-27.md`](./udemy-L14-L16-handoffs-adaptado-2026-07-27.md)

---

## 0. Veredicto

L16 es el **lab práctico** de L14: construir triage + billing/tech primero con **handoffs**, luego con **as_tool**, y verificar con `last_agent` + dashboard (handoff count vs tool calls).  
En la firma: **ya vivís el segundo patrón** (Gerente + especialistas as_tool). No rehacer el lab Codex ni adoptar el primer patrón (handoff) en prod.

---

## 1. Qué hace el lab del curso

### Parte A — Handoffs
- Triage + billing specialist + tech specialist.  
- Usuario → triage → handoff → **especialista habla al usuario**.  
- Verificación: `result.last_agent` = billing/tech; dashboard columna handoff > 0.

### Parte B — As tools
- Mismos especialistas expuestos con `as_tool` + descriptions.  
- Usuario → manager → tool call especialista → **manager siempre last_agent**.  
- Verificación: `last_agent` = support manager en todos los escenarios; `new_items` ToolCall/ToolOutput; dashboard handoff = 0, tools > 0.

### Takeaway del lab
Ownership de la respuesta + trazabilidad (quién habló / qué tool). Observability vía RunResult + OpenAI traces.

---

## 2. Traducción firma virtual

### Negocio
El lab “customer support” del curso = vuestro **despacho**: el abogado no debe ver “last agent = redactor”. Debe ver siempre el Gerente; el backoffice queda en traza/plan.

**Ejemplo lab → firma**

| Lab | Firma |
|---|---|
| Billing question → handoff billing | Tipicidad → as_tool tipicidad; voz Gerente |
| Tech question → as_tool tech; manager responde | Audiencia → as_tool preparador; voz Gerente |
| General FAQ → triage solo | Pregunta general → POC sin tool |
| Pipeline multi-paso handoff | **Plan HITL** sequential (`plan_templates` / `depends_on`) |

### Ya implementado (no portar)
- `build_orchestrator` + as_tool + descriptions Usar/No usar (L10).  
- Planes sequential condicionales (L14).  
- Traza + `last_agent` / backoffice + `_ensure_poc_voice` (L08).  
- Eval `no_terminal_handoff`.

---

## 3. High-level

> **No portes el lab.** No clones triage/billing/tech ni actives handoffs “para completar L16”.  
> Lo productizable del lab ya está: **ownership (Gerente) + tools + traza**.  
> Batch Must sigue B01–B05.

| Ítem | Acción | Backlog |
|---|---|---|
| Lab Codex L16 | No | Won’t |
| Handoff demo en prod | No | Won’t (L14) |
| as_tool manager | Mantener | — |
| Planes multi-paso | Mantener | — |

---

## 4. Costos / productizar

- Lab handoff: 2× LLM (triage + especialista) y cara inconsistente → peor UX jurídica y a menudo más $.  
- as_tool + plan solo cuando high-risk: mismo aprendizaje del lab **Parte B**, alineado a productizar.  
- Dashboard OpenAI del lab ≈ Workflow Trace / desk soporte (B04/B08 refuerzan visibilidad, no hacen falta para “pasar” L16).

---

## 5. Qué NO hacer

- No rehacer el proyecto support del curso en este repo.  
- No medir “éxito” por haber corrido Codex lab.  
- No usar `last_agent` especialista como voz del chat.

---

## Cierre

Siguiente pedagógica: **L11 — Guardrails and Human Review** (reabrir formal; hubo parcial fuera de orden).
