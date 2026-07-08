---
name: analizar-enfoque-diferencial
description: Skill atomico penal-victimas: identificar sujetos de especial proteccion y necesidades diferenciadas. Use when the workflow requires `analizar_enfoque_diferencial`.
disable-model-invocation: true
---

# analizar_enfoque_diferencial

## Scope
- Category: `Skills de representacion de victimas`
- Skill ID: `analizar_enfoque_diferencial`
- Tier: `operativo`

## Used By Agents
- `analista_representacion_victimas`
- `analista_calidad_juridica`

## Purpose
Identificar factores diferenciales relevantes (género, edad, discapacidad, etnia, etc.) que exijan enfoque especial en la representación.

## Rol en analista_representacion_victimas
Ajustar teoría del caso y comunicación con enfoque de derechos.

## Rol en analista_calidad_juridica
Verificar que escritos y preguntas respeten enfoque diferencial.

## Inputs
- Datos de la víctima disponibles (solo los documentados; no inferir).
- Tipo de delito y contexto del caso.
- Materiales a revisar (teoría, preguntas, memorial).

## Outputs
- `factores_diferenciales` documentados con fuente o `[PENDIENTE DE VERIFICAR]`.
- `ajustes_recomendados` en lenguaje, ritmo procesal o medidas de protección.
- `alertas` si el material ignora enfoque diferencial obligatorio.

## Steps
1. Identificar factores diferenciales relevantes con base documentada.
2. Evaluar impacto en representación, comunicación y medidas de protección.
3. Proponer ajustes concretos al plan de actuación.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_normas_victimas_search`

## Guardrails (g1–g10)
- **g1:** No inferir identidad o condición no documentada.
- **g5:** No estigmatizar a la víctima al nombrar factores diferenciales.
- **g6:** Minimizar datos sensibles innecesarios.
- **g4:** HITL obligatorio antes de incorporar hallazgos a escritos o comunicación externa.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No revisión detallada de revictimización (`controlar_no_revictimizacion`).

## Riesgo si se omite
Revictimización o desatención de garantías especiales aplicables a la víctima.
