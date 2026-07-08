---
name: preparar-contraargumentos
description: Skill atomico penal-victimas: anticipar argumentos de defensa, Fiscalia u otros intervinientes. Use when the workflow requires `preparar_contraargumentos`.
disable-model-invocation: true
---

# preparar_contraargumentos

## Scope
- Category: `Skills de audiencias`
- Skill ID: `preparar_contraargumentos`
- Tier: `operativo`

## Used By Agents
- `preparador_estrategico_audiencias_penales`

## Purpose
Anticipar argumentos de defensa o Fiscalía y preparar réplicas para audiencia o memorial.


## Rol en preparador_audiencias
Réplicas anticipadas para audiencia o memorial; insumo estratégico, no conclusión.
## Inputs
- Teoría del caso contraria (hipótesis documentada).
- Prueba disponible y matriz hecho-prueba.
- Tipo de audiencia u escrito objetivo.

## Outputs
- `contraargumentos`: argumento_ajeno | réplica_sugerida | prueba_de_apoyo | riesgo.
- Etiqueta: `HIPÓTESIS TÁCTICA — NO AFIRMAR HECHOS NO PROBADOS`.

## Steps
1. Identificar líneas argumentativas probables de la contraparte.
2. Preparar réplicas con hechos soportados y norma aplicable.
3. Señalar puntos débiles de la réplica que requieren prueba adicional.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_expediente_search`
- `rag_ley906_search`

## Guardrails (g1–g10)
- **g3:** Réplicas basadas en hechos soportados, no en especulación.
- **g4:** HITL obligatorio antes de usar en audiencia o memorial.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No guion oral (`preparar_guion_intervencion_oral`).
- No simulación (`simular_escenarios_audiencia`).

## Riesgo si se omite
Improvisación ante argumentos previsibles de defensa o Fiscalía.
