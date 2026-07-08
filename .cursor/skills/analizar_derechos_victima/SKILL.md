---
name: analizar-derechos-victima
description: Skill atomico penal-victimas: mapear derechos de victima aplicables al caso. Use when the workflow requires `analizar_derechos_victima`.
disable-model-invocation: true
---

# analizar_derechos_victima

## Scope
- Category: `Skills de representacion de victimas`
- Skill ID: `analizar_derechos_victima`
- Tier: `operativo`

## Used By Agents
- `analista_representacion_victimas`
- `evaluador_derechos_fundamentales_tutela`

## Purpose
Mapear derechos de la víctima en el proceso penal (participación, información, reparación, protección) y su vínculo con los hechos.

## Rol en analista_representacion_victimas
Insumo para teoría del caso y plan de actuación ordinaria Ley 906.

## Rol en evaluador_derechos_fundamentales_tutela
Distinguir derechos procesales de víctima vs. derechos fundamentales para tutela; no dictamina procedencia.

## Inputs
- Hechos verificados y etapa procesal Ley 906.
- Conductas u omisiones de Fiscalía, juez o autoridad que afecten a la víctima.
- Normativa de víctimas (Ley 906, Ley 1712, etc.) vía RAG.

## Outputs
- `derechos_mapeados`: participación | información | reparación | protección | otros.
- Por derecho: `hecho_vinculado`, `autoridad_responsable`, `estado` (vulnerado | en_riesgo | respetado | pendiente).
- `prioridad_atencion` (alta | media | baja).
- Etiqueta: `MAPEO DERECHOS VÍCTIMA — NO SUSTITUYE TUTELA`.

## Steps
1. Mapear derechos de participación, información, reparación y protección aplicables.
2. Relacionar derechos con hechos y etapa del proceso.
3. Priorizar derechos más vulnerados o urgentes.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_normas_victimas_search`
- `rag_constitucional_search`

## Guardrails (g1–g10)
- **g1:** No inventar vulneraciones ni normas.
- **g3:** Derecho procesal de víctima ≠ automáticamente tutela.
- **g5:** Lenguaje respetuoso con la víctima; sin juicios de credibilidad ni exposición innecesaria.
- **g4:** HITL obligatorio antes de incorporar hallazgos a escritos o comunicación externa.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No intereses subjetivos (`identificar_intereses_victima`).
- No derechos fundamentales para tutela (`identificar_derecho_fundamental_afectado`).

## Riesgo si se omite
Estrategia que ignora derechos procesales de la víctima ya vulnerados en el expediente.
