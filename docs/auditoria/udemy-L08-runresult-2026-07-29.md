# Udemy L08 — RunResult and REPL — 2026-07-29 (clase formal, profundidad producto)

**Fase:** HECHO_CLASE  
**Orden pedagógico:** #8  
**Decisión global:** AJUSTAR (bajo esfuerzo; capacidad base ya existe)  
**Comando código:** `aprobado, ejecuta L08` (solo si queréis enriquecer traza/UI; no obligatorio para seguir)

**Fuente curso:** `documentos/udemy_transcripts/.../txt/08_runresult_and_repl.txt` (ok)  
**Auditoría previa (2026-07-27):** capa base mapeada; esta pasada cierra clase formal.

---

## 0. Veredicto

L08 = **qué sale del loop** (no solo el texto al abogado).  
El curso enseña 7 campos + taxonomía de `new_items` + REPL local.  
En la firma virtual ya consumís lo crítico: `final_output`, `last_agent`, `interruptions`, `new_items` → traza, más usage vía hooks.  
El “REPL” del despacho no es la terminal del curso: es **Workflow Trace + desk soporte + `/debug/trace`**.

---

## 1. Qué enseña el curso (sin omitir)

Tres takeaways oficiales:

1. **Siete componentes de RunResult** (más que el texto final).  
2. **Taxonomía de `new_items`** (subpasos del run).  
3. **REPL** para debug local de tools/args.

### 1.1 Los 7 campos (curso)

| Campo | Para qué sirve en el curso |
|---|---|
| `final_output` | Respuesta del agente (str o Pydantic) |
| `new_items` | Historial del run: mensajes, tools, handoffs, reasoning |
| `last_response_id` | Encadenar con Responses API (una de las estrategias de memoria) |
| `interruptions` | Pausa por aprobación humana (`needs_approval`) |
| `state` | Congelar el run para reanudar tras HITL |
| `usage` | Tokens → costo del run |
| `last_agent` | Quién habló al final (crítico con handoffs) |

### 1.2 Taxonomía `new_items` (4 tipos clave)

| Tipo | Señala |
|---|---|
| Message / message output | Texto / reasoning del LLM |
| ToolCallItem | Tool disparado + argumentos |
| ToolCallOutputItem | Salida del tool |
| Handoff* items | Cambio de agente (labs del curso) |

Patrón de debug del curso: tool mal elegido → mirar **name**; args mal → **arguments**; dato raro en la respuesta → **tool output**.

### 1.3 Interruptions + state (HITL del SDK)

Si una tool pide aprobación: el loop pausa → `interruptions` lleno → guardás `state` → humano aprueba → reanudás el mismo loop.

### 1.4 REPL

CLI del SDK: chat en terminal + ver `new_items`. Útil en labs; **no** es el patrón de producción con expedientes reales.

---

## 2. Traducción firma virtual

### 2.1 Problema de despacho

El abogado (y soporte) necesitan responder:

- ¿Por qué el Gerente pidió tipicidad y no redacción?  
- ¿Hubo tool call / fallo de args?  
- ¿El turno se cortó por HITL, budget o guardrail?  
- ¿Cuánto costó el turno?

Sin RunResult (o su proyección en traza) solo ves el párrafo final → ops a ciegas.

### 2.2 Mapa Idea curso → este repo

| Idea curso | Ruta / símbolo | Práctica en firma |
|---|---|---|
| `final_output` | `runner.py` → `raw_out`; `plan_executor._final_output_text` + `structured_render` | Chat: str + guardrails; plan: Pydantic → texto legible |
| `new_items` | loop `ToolCallItem` / `Handoff*` → `trace.actions` `runtime_event` | Hoy: tipo de evento; poco detalle de args |
| `last_agent` | `_resolve_backoffice_agent` + `_ensure_poc_voice` | Auditoría interna ≠ voz al abogado (siempre POC) |
| `interruptions` | bloque `pending_review` en `runner.py` | Path existe; en **chat** high-risk tools están **off** (HITL = plan) |
| `state` resume SDK | No es el camino principal de chat | Reanudación = **plan aprobado** / Slack EJECUTAR, no freeze del mismo Runner |
| `usage` | `_TraceRunHooks.on_llm_end` → `trace.completion` | Costo por completions; no dependéis de `result.usage` |
| `last_response_id` | Session Postgres / historial propio | No es la estrategia principal de memoria (L12/L13) |
| REPL | Workflow Trace (`chat.js`) + desk soporte + `GET /debug/trace/{session_id}` | Debug con auth; sin CLI sobre datos de cliente |

### 2.3 Flujo post-`Runner.run` (chat)

```text
result = Runner.run(...)
  → contar new_items (span runner:fin)
  → last_agent → backoffice_agent (auditoría)
  → si interruptions → mensaje HITL + pending_review (sin entregar borrador)
  → si no → final_output → guardrails → _ensure_poc_voice
       → post-validaciones → traza (runtime_event + completion)
```

### 2.4 Por qué chat casi no ve interruptions del SDK

Diseño deliberado (L07 + L11 parcial):

- `include_high_risk_tools=False`  
- `require_tool_approval=False`  
- Alto riesgo (redactor / tutela) → **plan HITL**, no pause mid-loop del chat.

El handler de `interruptions` es red de seguridad / futuros paths, no el camino feliz del memorial.

### 2.5 Plan executor = otro consumidor de RunResult

- `final_output` tipado → `render_structured_output`  
- Dictamen calidad `rechazado`/`escalar` → bloquea entrega accionable  
- Misma idea L08: **no te fíes solo del texto**; la estructura decide el gate

---

## 3. Anti-mitos

| Mito | Realidad en este producto |
|---|---|
| “Con el texto del chat basta” | Ops/QA necesitan traza + tools + tokens |
| “last_agent debe ser la voz del chat” | Cara = POC; last_agent/backoffice = auditoría |
| “Hay que portar el REPL del curso” | REPL con expediente real = riesgo 1581 / PII |
| “Hay que volcar raw_responses” | Forensics solo bajo control; default no |
| “Usage solo existe en result.usage” | Aquí usage vive en hooks → `trace.completion` |
| “Interruptions = único HITL” | HITL principal = plan + drafts; interruptions = capa SDK |

---

## 4. Config / mensaje HIGH LEVEL

> **Mensaje high-level:** Para L08, **AJUSTAR** (opcional, bajo esfuerzo).  
> La inspección base ya está: no reescribas el runner “porque el curso”.  
> Si aprobáis código: enriquecer detalle de tool items en traza/soporte + smoke formal.  
> No REPL con datos de cliente. No dump de `raw_responses` a logs públicos.

| Ítem | Hoy | Recomendación | Prioridad | Impacto agentes | Esfuerzo |
|---|---|---|---|---|---|
| Consumo `final_output` / voz POC | Hecho | Mantener | — | — | — |
| `new_items` → solo class name | Parcial | Opcional: tool name + args redactados en traza | P2 | Mejor debug | Bajo |
| Usage | Hooks ✓ | Documentar; no forzar `result.usage` | P3 | Ops | Docs |
| Interruptions path | Código ✓; chat high-risk off | Mantener dualidad plan vs SDK pause | — | — | — |
| REPL curso | No | No adoptar con datos reales | — | Compliance | — |
| Smoke RunResult | Informal | Checklist PASS en ops/clase | P2 | Confianza | Bajo |
| `raw_responses` en UI | No | Seguir sin exponer | — | PII | — |

---

## 5. Desempeño (4 ejes)

| Eje | Efecto de usar bien RunResult |
|---|---|
| Calidad jurídica | Distinguís error de tool / alucinación / gate HITL |
| Costo/ruido | Tokens por turno visibles → menos runs a ciegas |
| Confianza abogado | Trace explica “consulté tipicidad”, no caja negra |
| Latencia/fricción | No añade latencia; añade claridad post-turno |

---

## 6. Mini-laboratorio

| Entrada | Debería | Hoy | PASS/GAP |
|---|---|---|---|
| Consulta tipicidad | Trace con tools/spans + texto POC | Trace + completion | PASS (detalle args GAP opcional) |
| “Redacte memorial” (chat) | Sin interruptions SDK; pide plan | Gate plan antes/sin high-risk tools | PASS |
| Plan con calidad rechazada | Bloqueo por `final_output` estructurado | `_quality_gate_blocks` | PASS |
| Soporte mira turno | Spans + tokens + agentes | desk-soporte + `/debug/trace` | PASS |
| REPL con caso real | No | No | PASS (no hacer) |

---

## 7. Qué NO hacer

- No construir REPL local sobre sesiones de producción.  
- No loguear `raw_responses` / args crudos con PII.  
- No cambiar voz del chat a `last_agent` especialista.  
- No reintroducir handoffs peer “para que last_agent tenga sentido como en el lab”.  
- No mezclar resume-by-`state` del SDK con el flujo de plan sin diseño (L11).

---

## 8. Plan de acción

**Clase:** cerrada.  
**Código:** solo si producto quiere el polish:

```text
aprobado, ejecuta L08
```

Alcance sugerido si se aprueba:

1. En `runner.py`: al recorrer `new_items`, enriquecer `detail` con tool name (y args redactados/truncados).  
2. Smoke documentado: un turno chat + un plan → verificar actions/spans/completion en UI.  
3. Nota ops: usage = hooks; REPL = desk/debug autenticado.

Si no hay urgencia de UI:

```text
cerrar L08, dejar quieto
```

(equivalente operativo: quedarse en AJUSTE pendiente sin implementar).

**Siguiente lección:** L09 — Hosted Tools (esperado: no aplicar `web_search` hosted).
