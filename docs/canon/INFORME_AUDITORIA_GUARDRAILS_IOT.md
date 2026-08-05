# Informe auditoría Guardrails I/O/Tools (Fases A–D)

**Fecha:** 2026-08-05  
**Prompt:** `PROMPT_PANEL_OPENAI_GUARDRAILS_IOT.md`  
**Estado:** auditoría cerrada → ejecución olas G0–G4

---

## Matriz (Fase A)

Leyenda: OK | PARCIAL | AUSENTE | N/A

| agent_id | MD input | MD output | MD tools | Código input | Código output | Código tool | Cableado Agent | Eval |
|---|---|---|---|---|---|---|---|---|
| coordinador_caso | OK | OK | OK | OK | PARCIAL¹ | OK | OK | PARCIAL |
| redactor_documentos_juridicos | AUSENTE | PARCIAL | AUSENTE | AUSENTE | PARCIAL² | vía Gerente | output only | PARCIAL |
| analista_calidad_juridica | AUSENTE | PARCIAL | AUSENTE | AUSENTE | OK (veredicto) | vía Gerente | output only | PARCIAL |
| analista_cronologia_hechos | AUSENTE | AUSENTE | AUSENTE | AUSENTE | PARCIAL³ | vía Gerente | output only | AUSENTE |
| analista_responsabilidad_tipicidad | AUSENTE | AUSENTE | AUSENTE | AUSENTE | PARCIAL³ | vía Gerente | output only | AUSENTE |
| analista_ruta_procesal | AUSENTE | AUSENTE | AUSENTE | AUSENTE | PARCIAL³ | vía Gerente | output only | AUSENTE |
| analista_representacion_victimas | AUSENTE | AUSENTE | AUSENTE | AUSENTE | PARCIAL³ | vía Gerente | output only | AUSENTE |
| analista_evidencia | AUSENTE | AUSENTE | AUSENTE | AUSENTE | PARCIAL³ | vía Gerente | output only | AUSENTE |
| analista_audiencias | AUSENTE | AUSENTE | AUSENTE | AUSENTE | PARCIAL³ | vía Gerente | output only | AUSENTE |
| analista_seguimiento_procesal | AUSENTE | AUSENTE | AUSENTE | AUSENTE | PARCIAL³ | vía Gerente | output only | AUSENTE |

¹ Output Gerente: vacío = tripwire; invención = soft-flag; disclaimer se añade en post-proceso.  
² Redactor: vacío = tripwire; citas sin pendiente = flag, no tripwire.  
³ Especialistas: solo `specialist_output_guardrail` (vacío + PII soft).

`g1`–`g10`: política de producto, no trío I/O/T enforceable.

---

## Hallazgos (Fases B–C)

| ID | Sev | Capa | Hallazgo | Demo fallo |
|---|---|---|---|---|
| GR-001 | P0 | input+policy | Redactor/calidad sin `input.md`; especialistas sin I/O/T MD | Pedido tutela al redactor en plan no tiene política documentada de rechazo en input del agente |
| GR-002 | P0 | input+wiring | Especialistas en plan **sin** `input_guardrails` | Injection/vacío en paso de plan no tripwirea en el especialista |
| GR-003 | P1 | tools | Tutela solo se bloquea si `tool_name==redactor` | Pedido “borrador de tutela” a otro tool podría pasar el check de tool_input |
| GR-004 | P1 | output | Invención/citas sin pendiente = soft en Gerente y redactor | “Sentencia C-999/99” sin `[PENDIENTE]` no tripwirea |
| GR-005 | P1 | policy_md | `g1`–`g10` de 1 línea no sustituyen I/O/T | Portal puede marcar g* APROBADO sin trío por agente |
| GR-006 | P1 | eval | Sin test de “todo agente tiene output MD + input en código” | Regresión silenciosa si se quita un cable |
| GR-007 | P2 | output | Especialistas sin política de dominio en MD (cronología, tipicidad, etc.) | No hay tripwire_message documentado por área |
| GR-008 | P2 | privacy | Tool output solo rechaza PII sensible etiquetada; ok con mask post | Aceptable si se documenta |

---

## Decisiones E0 (síntesis)

1. **Soft-flag de invención se mantiene** en Gerente (HITL del abogado); en redactor se **documenta** y se añade flag en eval, no tripwire duro (evita falsos positivos en borradores).  
2. **Input guardrail de especialistas** sí se cablea (vacío + injection + tutela→redactor).  
3. **Tutela**: ampliar tool_input a cualquier tool si el pedido pide tutela.  
4. **MD I/O/T** para los 10 agentes (tools de especialistas = knowledge tools + N/A redacción).

---

## Olas de ejecución

| Ola | Qué |
|---|---|
| G0 | Ampliar bloqueo tutela en tool_input; input guardrail especialistas + redactor |
| G1 | Crear `input.md`/`output.md`/`tools.md` faltantes |
| G2 | Cablear input en `_build_agent`; helpers export |
| G3 | Tests de cobertura + tutela amplia + input vacío especialista |
| G4 | Doc antes/después + checksums |

---

## Criterio de cierre

Matriz sin `AUSENTE` en celdas obligatorias; tests verdes; doc corta de antes/después.

---

## Cierre de ejecución (2026-08-05)

| Ola | Estado |
|---|---|
| G0 | Hecho — tutela draft en cualquier tool; input especialistas |
| G1 | Hecho — 10 agentes con `input.md` / `output.md` / `tools.md` |
| G2 | Hecho — `specialist_input_guardrail` cableado en `_build_agent` |
| G3 | Hecho — `tests/test_guardrails_iot_coverage.py` (+ phase2/evals) verdes |
| G4 | Hecho — `ANTES_Y_AHORA_GUARDRAILS_IOT.md` |

Verificación: **29 passed** (`test_guardrails_iot_coverage` + `test_phase2_sdk_hardening` + `test_agent_evals`).
