# Udemy L10 — Function Tools and Agent as Tools — 2026-07-30 (clase formal)

**Fase:** HECHO_CLASE  
**Orden pedagógico:** #10  
**Decisión global:** DEJAR QUIETO (patrón canónico ya endurecido; no código nuevo ahora)  
**Batch final:** L10 no añade ítem obligatorio (hardening anticipado ya hecho)  
**Fuente curso:** `txt/10_function_tools_and_agent_as_tools.txt` (ok)  
**Código previo:** [`udemy-L10-as-tool-2026-07-27.md`](./udemy-L10-as-tool-2026-07-27.md) · `tests/test_l10_as_tool.py`

---

## 0. Veredicto

L10 = dos puentes del SDK hacia **tu** sistema:

1. **Function tools** — tu código/APIs como tool (`@function_tool` / schema).  
2. **Agent as tool** — un agente especialista invocable por otro; el “micrófono” queda en el manager.

En la firma virtual esto **ya es la arquitectura**: Gerente = única voz; 10 especialistas = `Agent.as_tool`; KB = function tools; **no** handoffs peer. Hardening L10 (descriptions, failures tipados, nested turns, needs_approval) ya aplicado fuera de orden; esta pasada cierra la **clase** sin tocar runtime (batch de cambios al final de la serie).

---

## 1. Qué enseña el curso (sin omitir)

### Function tools
- Conectan DB, APIs internas/terceros, reglas de dominio, preferencias de usuario.  
- Descripción → JSON schema que ve el modelo: **nombre + description + parameters**.  
- Buena description: verbo + objeto + cuándo usar; hablarle al agente; qué pasa si falla; diferenciar tools similares; corto, concreto, sin marketing.  
- Errores: **return** string útil al modelo (caso de negocio) vs **raise** (fallo técnico → app).  
- Parallel vs sequential tool execution (solo parallel si no hay orden/pago/efectos).  
- Tools pueden devolver Pydantic estructurado (contrato).  
- `tool_choice` en ModelSettings: auto / none / required / specific.

### Agent as tools vs handoffs
| Patrón | Micrófono | Cuándo |
|---|---|---|
| **as_tool** | Queda en el manager | Un dueño de comunicación; manager sintetiza |
| **handoff** | Pasa al especialista | Routing flexible; el último agente habla al usuario |

Curso: en el mundo real a menudo se combinan. **En este producto: solo as_tool** (una voz).

---

## 2. Traducción firma virtual

### Negocio
El abogado no debe “cambiar de interlocutor” cada vez que hace falta tipicidad o cronología. Habla con el **Gerente**; el Gerente consulta al equipo interno y responde con una sola voz.

**Ejemplo:** “Analice tipicidad del hurto” → Gerente invoca tool `analista_tipicidad_…` → recibe salida (prosa/schema renderizado) → sintetiza al abogado. El tipicidad **no** habla directo.

**Ejemplo alto riesgo:** “Redacte memorial” → en chat las tools de redacción/tutela están **fuera** o van por **plan HITL** (no `as_tool` libre mid-chat).

### Mapa curso → repo

| Idea curso | Aquí |
|---|---|
| Function tool | Tools KB / conocimiento (`get_knowledge_tools`) |
| Agent as tool | 10 especialistas en `build_orchestrator` → `agent.as_tool(...)` |
| Tool descriptions | `_SPECIALIST_TOOL_DESCRIPTIONS` (skill + Usar/No usar) |
| Failure handling | `_as_tool_failure_error` (códigos tipados, sin stack/PII) |
| Nested agent turns | `nested_max_turns_for` + techo `_NESTED_MAX_TURNS_CEILING` |
| needs_approval | redactor + tutela cuando `require_tool_approval` |
| Micrófono = manager | POC + `_ensure_poc_voice`; sin `handoffs=` en POC |
| Superficie de tools | Focus + vecinos (`enabled_specialists_for_focus`); chat sin high-risk |
| Structured via tools | `output_type` en especialistas + `custom_output_extractor` / render |

Ruta central: `src/agents/orchestrator.py` (`build_orchestrator`).  
Input tipado a especialistas: `SpecialistConsultInput` / `specialist_input_builder`.

---

## 3. High-level

> **DEJAR QUIETO.** El patrón L10 ya es la firma: function tools (KB) + Agent as tools (especialistas), micrófono en el Gerente, sin handoffs peer.  
> Hardening ya hecho (descriptions, failures, nested turns, approval).  
> No implementar ahora: batch de código al final (L04/L05/L08). L10 no suma ítem obligatorio.

| Ítem | Hoy | Acción |
|---|---|---|
| Manager-specialist as_tool | Operativo | Mantener |
| Descriptions Usar/No usar | Hecho | Mantener |
| Failures tipados | Hecho | Mantener |
| Nested max turns + techo | Hecho | Mantener |
| High-risk off en chat | Hecho | Mantener (planes HITL) |
| Handoffs peer | Prohibidos | No introducir |

---

## 4. Qué NO hacer

- No cambiar a handoffs peer “porque el curso combina ambos”.  
- No dejar que el especialista hable al abogado.  
- No subir `max_turns` anidados sin techo.  
- No exponer stack traces / PII en fallos de tool.  
- No reabrir redacción/tutela como tools libres en chat sin plan.

---

## 5. Mini-laboratorio

| Caso | Debería | Hoy |
|---|---|---|
| Tipicidad en chat | as_tool tipicidad; voz Gerente | PASS |
| Especialista falla | Mensaje código tipado, sin Traceback | PASS (tests L10) |
| Redactor en chat libre | No / plan HITL | PASS (high-risk off) |
| POC con handoffs= | No | PASS |

---

## Cierre

Siguiente pedagógica: **L15 — MCP** (MCP real vs `src/mcp/tools.py`).
