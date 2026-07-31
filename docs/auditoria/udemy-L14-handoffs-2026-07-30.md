# Udemy L14 — Handoffs and Multi-Agentic Orchestration — 2026-07-30 (clase formal adaptada)

**Fase:** HECHO_CLASE  
**Orden pedagógico:** #12  
**Decisión global:** DEJAR QUIETO / **adaptar** — sin handoffs peer; orquestación = as_tool + planes  
**Batch:** no Must nuevo; Won’t peer confirmado  
**Fuente:** `txt/14_handoffs_and_multi_agentic_orchestration.txt` (ok)  
**Previo conjunto L14/L16:** [`udemy-L14-L16-handoffs-adaptado-2026-07-27.md`](./udemy-L14-L16-handoffs-adaptado-2026-07-27.md)

---

## 0. Veredicto

L14 enseña **cuándo partir agents**, el patrón **handoff** (el micrófono pasa) vs **as_tool** (el manager sintetiza), y 4 topologías (manager, sequential, parallel, conditional).  
En firma virtual: **as_tool + planes HITL** = vuestra orquestación. Handoffs peer = **Won’t** (rompe una voz, más hops/tokens, cara de especialista al abogado).

---

## 1. Qué enseña el curso (sin omitir)

### Por qué partir agents
Un monolito con demasiadas tools/prompt: más lento, más caro, más errores, contaminación de info (p.ej. lógica de refund en pregunta de envío). Especialistas de scope estrecho. Regla empírica curso: ~10+ tools → pensar en split.

### Handoff vs as_tool
| | Handoff | as_tool |
|---|---|---|
| Micrófono | Pasa al especialista | Queda en el manager |
| Uso curso | Domain shift fuerte; especialista cierra con el usuario | Una respuesta unificada; manager observa end-to-end; parallel tools |

Handoff API: campo `handoffs`, overrides (`handoff()`): description, input_filter, `on_handoff` callback, tool name, input pydantic.

### 4 topologías
1. **Manager / triage** — router a especialistas (handoff o tools).  
2. **Sequential** — pipeline A→B→C (handoffs encadenados o varios `Runner.run`).  
3. **Parallel** — fan-out (as_tool parallel o asyncio gather).  
4. **Conditional** — classifier → agent según flag/tier.

### Cuándo NO partir
Solapamiento ~80% tools → merge; demasiados handoffs → lento (doble reasoning); 2 especialistas no justifican triage agent; 5–10 sí.

---

## 2. Traducción firma virtual

### Negocio
El abogado siempre habla con el **despacho (Gerente)**. No debe “pasar” a Tipicidad o Redactor como si fueran colegas de chat. Eso diluye responsabilidad y HITL.

**Ejemplo:** “Prepare tipicidad y luego memorial”  
- Curso handoff: triage → tipicidad habla → redactor habla.  
- Firma: Gerente consulta tipicidad (as_tool) y/o propone **plan** secuencial aprobado; voz siempre Gerente.

### Mapa topologías → producto

| Topología curso | Aquí |
|---|---|
| Manager | POC + triage código + `as_tool` (no `handoffs=`) |
| Sequential | `plan_templates` + `plan_executor` (depends_on) tras HITL |
| Parallel | Posible en tools; no fan-out libre de memoriales |
| Conditional | Triage keywords + gates alto riesgo → plan |
| `on_handoff` callback | Traza/hooks; Slack HITL vía plan, no handoff peer |
| Defensa residual | `_ensure_poc_voice` si filtrara voz especialista |

Evidencia: POC sin handoffs terminales (`orchestrator.py`); eval `no_terminal_handoff`.

---

## 3. High-level

> **DEJAR QUIETO / adaptar.** Aprende el concepto; no portes el lab de handoffs.  
> Orquestación productizable = una voz + as_tool + planes.  
> Batch Must sigue B01–B05. L14 no añade Must.

| Ítem | Acción | Backlog |
|---|---|---|
| `handoffs=` peer en POC | No | Won’t |
| as_tool + planes | Mantener | — |
| `_ensure_poc_voice` | Mantener | — |
| Portar lab L14 | No | Won’t |

---

## 4. Costos / productizar

- Handoffs peer: más reasoning hops → **más tokens** y latencia.  
- Manager as_tool + plan solo cuando hace falta high-risk → **mejor $/valor**.  
- Productizar = ownership claro (Gerente) + HITL en planes, no “ping-pong” de caras.

---

## 5. Qué NO hacer

- No `handoffs=` entre especialistas en prod.  
- No exponer especialistas como caras web/Slack.  
- No copiar lab “para completar el curso”.  
- No triage agent LLM redundante si el triage de código + focus ya enruta.

---

## Cierre

Siguiente: **L16 — Lab: Multi-Agents Handoffs and As Tools** (adaptado; no portar lab).
