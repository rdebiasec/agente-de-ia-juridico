# Udemy L06 — Lab Basic Agents — 2026-07-28

**Fase:** HECHO_CLASE  
**Orden pedagógico:** #3  
**Modo:** CLASE + mapa · **Decisión:** DEJAR QUIETO  
**Fuente curso:** caption ausente → código del producto (`orchestrator.py`)

---

## 0. Veredicto

- **Qué es:** construir un `Agent` mínimo (nombre, instructions, model, tools) y correrlo.
- **En este repo:** el Agent “básico” del despacho es el POC `coordinador_expediente_penal`; los 10 especialistas son Agents de backoffice.
- **¿Tocar config?** No. El lab ya está vivido en producción.

---

## 1. Clase

Un Agent del SDK ≈ ficha de empleado:

| Campo SDK | Significado | En el POC |
|---|---|---|
| `name` | Quién es | `coordinador_expediente_penal` |
| `instructions` | Cómo debe trabajar | `assemble_instructions(...)` + prompts |
| `model` | Con qué cerebro | `_model_for_agent` |
| `tools` | Qué puede usar | KB + especialistas `as_tool` |
| `output_type` | Formulario de salida (opcional) | POC: **prosa** (sin schema de chat) |
| guardrails | Filtros entrada/salida | `poc_input/output_guardrails` |

Definir ≠ ejecutar: `build_orchestrator` / `build_coordinador_agent` definen; `runner.run_agent` ejecuta.

---

## 2. Mapa

- POC solo (pasos de plan): `build_coordinador_agent`
- POC + firma: `build_orchestrator`
- Especialista: `_build_agent` + `output_type` (schemas)
- Lookup: `get_agent_by_id`

---

## 3. High-level

> **DEJAR QUIETO.** No portar el lab Udemy. El Agent básico del asistente de abogados ya es el Gerente del caso. Cambios de tono van a prompts/skills, no a rehacer `Agent(...)`.

---

## 4. Cierre

Siguiente: **L03** Prompts / Structured Output.
