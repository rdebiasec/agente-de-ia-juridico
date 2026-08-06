---
caso_id: "{{caso_id}}"
agent_id: "redactor_documentos_juridicos"
agent_label: "Redacción Documentos"
updated_at: "{{updated_at}}"
eval_or_session: "{{eval_or_session}}"
source_of_truth: "Expediente.bitacora (Postgres)"
mirror: "Drive Lexiatek casos/<id>/notepads/redactor_documentos_juridicos.md"
---

# Notepad — Redacción Documentos

> Espejo de lectura por especialista. **No** es fuente de verdad.
> Solo datos sintéticos/anonimizados en local hasta DPA Google.
> Contrato: `docs/canon/PLAN_INSPECCION_CONFIG_NOTEPADS.md` §4.5.

## Metadatos

| Campo | Valor |
|---|---|
| caso_id / session | `{{caso_id}}` |
| agent_id | `redactor_documentos_juridicos` |
| updated_at | {{updated_at}} |
| eval_or_session | {{eval_or_session}} |

## Hechos usados (con fuente)

{{hechos_usados}}

## Inferencias (separadas de hechos)

{{inferencias}}

## Pendientes `[PENDIENTE DE VERIFICAR]`

{{pendientes}}

## Citas KB / normas usadas

{{citas_kb}}

## Decisiones HITL relevantes

{{hitl}}

## Próxima pregunta al Gerente / abogado

{{proxima_pregunta}}

## Entradas de bitácora (espejo filtrado)

{{entradas}}
