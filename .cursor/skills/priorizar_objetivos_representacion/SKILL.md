---
name: priorizar-objetivos-representacion
description: Skill operativo penal-victimas: ordenar objetivos de la representacion. Use when the workflow requires `priorizar_objetivos_representacion`.
disable-model-invocation: true
---

# priorizar_objetivos_representacion

## Scope
- Category: `Skills de representacion de victimas`
- Skill ID: `priorizar_objetivos_representacion`
- Tier: `operativo`

## Used By Agents
- `analista_representacion_victimas`
- `coordinador_expediente_penal`

## Purpose
Listar y ordenar objetivos posibles de la representación de la víctima según urgencia, viabilidad y alineación con sus intereses, documentando trade-offs para decisión del abogado.

## Rol en coordinador
Priorización **preliminar** en triage (ej. el abogado pregunta “¿qué atacamos primero?”). El análisis completo de intereses y teoría del caso corresponde a `analista_representacion_victimas`.

## Inputs
- Intereses declarados por la víctima o el abogado (justicia, reparación, celeridad, protección, no confrontación).
- Etapa procesal aparente y actuaciones disponibles.
- Riesgos conocidos (revictimización, términos, debilidad probatoria).
- Objetivos procesales técnicos ya identificados (si existen).

## Outputs
- Lista ordenada: `objetivo`, `prioridad` (1–n), `razón`, `dependencia`, `riesgo` (procesal | probatorio | revictimización).
- Trade-offs explícitos para decisión del abogado (ej. celeridad vs. recaudo probatorio).
- Etiqueta: `PRELIMINAR — VALIDAR CON VÍCTIMA Y ABOGADO TITULAR`.

## Steps
1. Listar objetivos posibles de la representación en el caso.
2. Ordenar por urgencia, viabilidad y alineación con intereses de la víctima.
3. Documentar trade-offs para decisión del abogado.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- Sin herramientas obligatorias (usar contexto del expediente ya cargado).

## Guardrails (g1–g10)
- **g1:** No inventar intereses de la víctima no expresados.
- **g2:** Sin input sobre intereses de la víctima, listar solo objetivos procesales genéricos marcados `[PENDIENTE DE VERIFICAR]`.
- **g3:** Objetivos son hipótesis estratégicas, no hechos.
- **g4:** HITL obligatorio: estrategia de representación requiere aprobación del abogado y, cuando aplique, consulta con la víctima.
- **g5:** No presionar rutas que revictimicen (ej. confrontación pública innecesaria).
- **g8:** Aviso de borrador estratégico.

## No duplicar
- No construir teoría del caso (`construir_teoria_caso_victima`).
- No identificar intereses en profundidad (`identificar_intereses_victima`).
- No crear ruta procesal detallada (`crear_ruta_procesal_recomendada`).

## Riesgo si se omite
Estrategia desalineada con la víctima o priorización que sacrifica términos o prueba crítica.
