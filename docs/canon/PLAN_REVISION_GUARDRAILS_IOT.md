# Plan de revisión — Guardrails Input / Output / Tools

**Estado:** pendiente de tu OK para **ejecutar** (hoy solo plan + prompt).  
**Prompt del panel:** [`PROMPT_PANEL_OPENAI_GUARDRAILS_IOT.md`](PROMPT_PANEL_OPENAI_GUARDRAILS_IOT.md)

---

## Por qué este plan (en una frase)

Los `g1`–`g10` son políticas cortas; el Agents SDK exige guardrails **enforceables** en **input**, **output** y **tools**, y hoy eso solo está completo en el Gerente.

---

## Diagnóstico previo (ya medido, sin cambios)

### Políticas globales

| Archivo | Qué es hoy | Problema |
|---|---|---|
| `config/guardrails/g1.md` … `g10.md` | 1 frase cada uno | No son Input/Output/Tools; no tripwirean solos |

### Políticas por agente (archivos MD)

| Agente | input.md | output.md | tools.md |
|---|---|---|---|
| `coordinador_caso` | Sí | Sí | Sí |
| `analista_calidad_juridica` | No | Sí (corto) | No |
| `redactor_documentos_juridicos` | No | Sí (corto) | No |
| Otros 7 especialistas | No | No | No |

### Código SDK (`sdk_guardrails.py`) vs cableado (`orchestrator.py`)

| Función | Tipo | Quién la usa |
|---|---|---|
| `poc_input_guardrail` | input | Solo Gerente |
| `poc_output_guardrail` | output | Solo Gerente (vacío = tripwire; invención = soft) |
| `specialist_output_guardrail` | output | Especialistas genéricos (casi solo vacío) |
| `redactor_output_guardrail` | output | Redactor |
| `calidad_output_guardrail` | output | Calidad |
| `poc_tool_input_guardrail` | tool input | Tools `as_tool` del Gerente |
| `poc_tool_output_guardrail` | tool output | Tools `as_tool` del Gerente |

**Hueco central:** 7 especialistas sin políticas MD I/O/T; input de especialistas y tools propias casi no documentados; output genérico débil frente a invención/PII/dominio.

---

## Objetivo del plan (qué significa “bien”)

Para cada agente crítico:

1. Política MD estructurada (`input` / `output` / `tools` según aplique).  
2. Función SDK con tripwire o soft-flag **explícito**.  
3. Cableado en el `Agent` / tools.  
4. Eval o test que falle si se quita.

Estándar = práctica Agents SDK + Safety (pre-model, post-model, tool governance).

---

## Fases de revisión (antes de código)

| Fase | Quién | Entrega | Criterio de pase |
|---|---|---|---|
| **A. Inventario** | E1 + E8 | Matriz agente × capa (OK/PARCIAL/AUSENTE) | Matriz completa, sin filas vacías |
| **B. Auditoría por capa** | E2 input, E3 output, E4 tools, E6 privacy, E7 HITL | Hallazgos GR-* con evidencia | Todo P0/P1 con `demo_fallo` |
| **C. Red team / evals** | E5 | Lista de casos de regresión propuestos | ≥1 caso por P0 |
| **D. Síntesis** | E0 | Plan de olas de **implementación** afinado | Tú apruebas por escrito |
| **E. Ejecución** | — | Solo tras OK | Ver olas abajo |

---

## Olas de implementación (propuesta; se afina en Fase D)

No se ejecutan hasta que apruebes.

### Ola G0 — P0 (seguridad / HITL)

- Confirmar que redacción/tutela no se invocan desde chat (tools + eval).  
- Endurecer output del redactor/calidad si el tripwire es insuficiente.  
- Cualquier agente high-risk sin output enforceable → cubrir.

### Ola G1 — Políticas MD faltantes

- Crear `input.md` / `output.md` / `tools.md` (o `N/A` justificado) para los 7 especialistas + gaps de calidad/redactor.  
- Misma estructura que `coordinador_caso` (policies, tripwire_message, output_info_fields), **adaptada al dominio**.

### Ola G2 — Código SDK + cableado

- Funciones por agente o por familia (factual / tipicidad / redacción).  
- No duplicar lógica: reutilizar helpers; especializar tripwires.  
- Cablear en `orchestrator.py` sin romper slim prompts.

### Ola G3 — Evals y tests

- Extender `agent_eval_cases.json` + pytest de guardrails.  
- Casos: injection, OOS, empty output, HITL redactor, PII mask.

### Ola G4 — Publicación

- Bump `config-version`/checksum.  
- Sync portal/config_store si aplica.  
- Nota corta “antes/después” de guardrails (como el de prompts/skills).

---

## Fuera de alcance (salvo que pidas)

- Reescribir los 81 skills otra vez.  
- Reactivar tutela.  
- Cambiar arquitectura de handoffs.  
- LLM-as-judge como único eval (preferimos determinista).

---

## Cómo arrancar cuando digas “OK”

1. Ejecutar el panel con [`PROMPT_PANEL_OPENAI_GUARDRAILS_IOT.md`](PROMPT_PANEL_OPENAI_GUARDRAILS_IOT.md) (Fases A–D).  
2. Entregarte: matriz + hallazgos + olas afinadas.  
3. Esperar tu OK de implementación.  
4. Ejecutar olas G0→G4 con verificación por ola (tests + reporte corto).

---

## Criterios de éxito

- Gerente: trío I/O/T documentado **y** enforceable (ya cerca; validar paridad).  
- Redactor + Calidad: input/output (y tools si aplica) documentados + código + eval.  
- Especialistas: al menos **output** de dominio + política MD; input/tools según matriz.  
- Cero P0 abiertos.  
- Tests verdes.
