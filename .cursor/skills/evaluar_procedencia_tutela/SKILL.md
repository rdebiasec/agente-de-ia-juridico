---
name: evaluar-procedencia-tutela
description: Skill critico penal-victimas: evaluar legitimacion, subsidiariedad, inmediatez y relevancia constitucional. Use when the workflow requires `evaluar_procedencia_tutela`.
disable-model-invocation: true
---

# evaluar_procedencia_tutela

## Scope
- Category: `Skills constitucionales y tutela`
- Skill ID: `evaluar_procedencia_tutela`
- Tier: `critico`

## Used By Agents
- `evaluador_derechos_fundamentales_tutela` (skill primario del agente)
- `analista_calidad_juridica`

## Purpose
Dictaminar preliminarmente si la tutela procede frente a legitimación, subsidiariedad, inmediatez y relevancia constitucional.

## Rol en evaluador_derechos_fundamentales_tutela
Skill primario. Sin dictamen favorable preliminar no hay borrador ni redacción de tutela.

## Rol en analista_calidad_juridica
Verificar que un borrador de tutela tenga dictamen previo coherente.

## Inputs
- Hechos verificados y derechos fundamentales alegados.
- `revisar_mecanismos_ordinarios`, `analizar_perjuicio_irremediable`, `crear_matriz_hecho_derecho_fundamental` (si existen).
- Titular del derecho y autoridades accionadas.
- Peticiones o silencios administrativos previos.

## Outputs
- `legitimacion_activa`: cumple | no_cumple | `[PENDIENTE DE VERIFICAR]`.
- `legitimacion_pasiva`: cumple | no_cumple | `[PENDIENTE DE VERIFICAR]`.
- `subsidiariedad`: agotado_ordinario | pendiente_ordinario | excepcional_justificada.
- `inmediatez`: alta | media | baja | no_evaluable.
- `conclusion_preliminar`: procedente | improcedente | procedente_con_reservas.
- `requisitos_faltantes` y `via_alternativa` si no procede.
- Etiqueta: `DICTAMEN PRELIMINAR — NO RADICAR SIN FIRMA DE ABOGADO`.

## Steps
1. Verificar legitimación por activa (titular del derecho y vínculo con el caso).
2. Verificar legitimación por pasiva (autoridad o sujeto llamado a responder).
3. Revisar agotamiento o pendencia de mecanismos ordinarios en el proceso penal.
4. Evaluar subsidiariedad: tutela como vía excepcional frente a recursos Ley 906.
5. Evaluar inmediatez del perjuicio y necesidad de medida urgente.
6. Evaluar conexidad constitucional y relevancia del derecho invocado.
7. Documentar requisitos faltantes y riesgo de improcedencia.
8. Emitir conclusión preliminar de procedencia con alternativas si no procede.
9. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_corte_constitucional_search`
- `citation_checker`

## Guardrails (g1–g10)
- **g1:** No inventar hechos, normas, sentencias ni radicados.
- **g3:** Dictamen preliminar; separar hecho de inferencia constitucional.
- **g4:** No autoriza radicación ni redacción sin abogado; gate para `preparar_borrador_tutela_preliminar`.
- **g5:** No revictimizar en fundamentación.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No redactar tutela (`redactar_tutela_penal_preliminar`).
- No triage de vías (`recomendar_via_constitucional_o_alternativa` — coordinador).
- No solo alertar riesgo (`detectar_riesgo_improcedencia_tutela`).

## Riesgo si se omite
Tutela radicada sin requisitos → rechazo, pérdida de tiempo procesal y debilitamiento de la estrategia penal ordinaria.
