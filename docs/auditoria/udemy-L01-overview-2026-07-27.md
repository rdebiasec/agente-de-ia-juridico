# Udemy L01 — Overview on OpenAI Agents — 2026-07-27

**Fase:** HECHO_CLASE  
**Orden pedagógico:** #1 (propósito primero)  
**Modo:** CLASE + mapa · **Decisión:** DEJAR QUIETO (sin código)  
**Fuente curso:** caption L01 inválida → `KB_LESSONS_FAQ.md` + producto

---

## 0. Veredicto

- **Qué es:** visión de Agents SDK: agentes con instrucciones, tools y un runner — no un chatbot suelto.
- **En este repo:** ya aplicado como firma virtual (POC + 10 specialists + HITL + Postgres).
- **¿Mejora desempeño?** Sí como brújula: alinea el equipo en *para qué* existe el stack.
- **¿Tocar config?** No. Solo anclar el propósito.

---

## 1. Clase del concepto

### Problema que resuelve
Un LLM solo responde texto. Un **agente** del SDK puede: seguir un rol, llamar tools, respetar límites y dejar traza. Eso es lo que permite un despacho asistido, no un chat genérico.

### Concepto / tecnología
- **Agent:** nombre + instructions + model + tools (+ opcional output_type, guardrails).
- **Runner:** ejecuta el agente (turno / loop).
- **Tools:** funciones o agentes-anidados que el modelo invoca.
- **No es magia:** el producto decide arquitectura (una voz, HITL, sin web search libre).

### Lab del curso
Overview / foundations. Caption L01 rota en la fuente Udemy — no bloquea: el producto ya vive el overview.

### Traducción a firma virtual
| Idea SDK | Aquí |
|---|---|
| Un agente “cara” | `coordinador_expediente_penal` (POC) |
| Otros agentes | 10 especialistas vía `Agent.as_tool` (backoffice) |
| Humano en el loop | HITL borradores / planes |
| Estado | Postgres, expediente, sesiones |

### Anti-mitos
- Overview ≠ “hay que rehacer el proyecto”.
- Overview ≠ empezar por guardrails (eso es L11, puesto #14).
- Overview ≠ activar voz/sandbox/Bedrock.

---

## 2. Mapa en este proyecto

```
Abogado (web/Slack)
    → POC coordinador_expediente_penal
        → tools: KB + especialistas as_tool
        → planes HITL si alto riesgo
    → Traza / soporte
    → Postgres (sesiones, drafts, expediente)
```

| Idea del curso | Ruta / símbolo | Práctica |
|---|---|---|
| Agent + runner | `src/agents/orchestrator.py`, `runner.py` | Un turno de chat |
| Multi-capacidad | 10 builders + `as_tool` | Backoffice interno |
| Gobernanza persona | `agente/prompts/`, G1–G10 | No inventar normas |
| Propósito producto | `ESTADO_PROYECTO.md`, `plan-rediseno-firma.md` | Firma virtual |

---

## 3. Config — mensaje high-level

> **Mensaje high-level:**  
> «Para L01, **DEJAR QUIETO**. No hay knob de config que falte para “entender el propósito”: el producto ya es una firma Agents SDK. El valor de L01 es alinear el lenguaje (POC, tools, runner, HITL) antes de L02/L06. Si tocáramos algo ahora, solo añadiríamos ruido.»

| Ítem | Hoy | Recomendación | Prioridad | Impacto agentes | Esfuerzo |
|---|---|---|---|---|---|
| Arquitectura POC + as_tool | Operativa | Dejar quieto | — | Base de todo | — |
| Caption L01 Udemy | Inválida | No bloquear; usar KB+código | P2 | Ninguno en runtime | — |
| Código / env | N/A | Sin cambio | — | — | — |

---

## 4. Desempeño (4 ejes)

1. **Calidad jurídica:** el overview no cambia prompts; evita malinterpretar el sistema como “chat GPT con traje”.  
2. **Costo/ruido:** DEJAR QUIETO evita refactors prematuros.  
3. **Confianza:** el abogado entiende “despacho con cola de revisión”, no 11 caras.  
4. **Latencia:** sin cambio.

---

## 5. Mini-laboratorio mental

| Entrada / pregunta | Debería | Hoy | Resultado |
|---|---|---|---|
| “¿Qué es este sistema?” | Firma virtual Agents SDK | ESTADO + plan-rediseno | PASS |
| “¿Hay 11 agentes en el chat?” | No: 1 POC + backoffice | `orchestrator.py` | PASS |
| “¿Empezamos por guardrails?” | No: primero propósito | Orden pedagógico | PASS (docs) |

---

## 6. Qué NO hacer

- No rehacer lab de overview.
- No saltar a L11 como “primera lección”.
- No portar demos del curso que rompan una sola voz.

---

## 7. Cierre

- Comando: `cerrar L01, dejar quieto` — **aplicado**.  
- Siguiente: **L02 Setup**.  
- Tablero: L01 = `HECHO_CLASE`.
