---
name: evaluar-dano-y-afectacion
description: Skill atomico penal-victimas: organizar danos y afectaciones alegadas. Use when the workflow requires `evaluar_dano_y_afectacion`.
disable-model-invocation: true
---

# evaluar_dano_y_afectacion

## Scope
- Category: `Skills de representacion de victimas`
- Skill ID: `evaluar_dano_y_afectacion`
- Tier: `operativo`

## Used By Agents
- `analista_representacion_victimas`
- `evaluador_derechos_fundamentales_tutela`

## Purpose
Describir preliminarmente el daño o afectación a la víctima con base documentada (físico, psicológico, patrimonial, social).

## Rol en analista_representacion_victimas
Insumo para teoría del caso y pretensiones de reparación.

## Rol en evaluador_derechos_fundamentales_tutela
Contexto factual para perjuicio; no sustituye `analizar_perjuicio_irremediable`.

## Inputs
- Relatos, informes médicos/psicológicos, declaraciones (si constan).
- Hechos verificados del caso.
- Pretensiones de reparación ya planteadas.

## Outputs
- `tipos_daño`: físico | psicológico | patrimonial | social | otros.
- Por tipo: `descripción`, `fuente`, `gravedad_preliminar` (alta | media | baja | pendiente).
- Etiqueta: `AFECTACIÓN PRELIMINAR — NO ES PERITAJE`.

## Steps
1. Identificar tipos de daño o afectación alegados o documentados.
2. Vincular cada afectación con hechos y fuentes del expediente.
3. Señalar vacíos que requieran prueba pericial o documental.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_expediente_search`

## Guardrails (g1–g10)
- **g1:** No inventar diagnósticos ni secuelas.
- **g5:** No minimizar ni dramatizar el daño sin base.
- **g4:** HITL obligatorio antes de incorporar hallazgos a escritos o comunicación externa.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No perjuicio irremediable constitucional (`analizar_perjuicio_irremediable`).
- No intereses subjetivos (`identificar_intereses_victima`).

## Riesgo si se omite
Pretensiones de reparación desconectadas del daño real o documentado.
