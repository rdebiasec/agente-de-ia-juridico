---
name: evaluar-suficiencia-probatoria
description: Skill estrategico penal-victimas: evaluar preliminarmente fuerza de soporte probatorio. Use when the workflow requires `evaluar_suficiencia_probatoria`.
disable-model-invocation: true
---

# evaluar_suficiencia_probatoria

## Scope
- Category: `Skills de evidencia y soporte probatorio`
- Skill ID: `evaluar_suficiencia_probatoria`
- Tier: `estrategico`

## Used By Agents
- `gestor_evidencia_y_soporte_probatorio`
- `analista_representacion_victimas`

## Purpose
Evaluar preliminarmente la fuerza del soporte probatorio sin afirmar certeza judicial ni condena.

## Rol en gestor_evidencia_y_soporte_probatorio
Cierre analítico tras matriz hecho-prueba e inventario.

## Rol en analista_representacion_victimas
Informar fortalezas/debilidades para teoría del caso y audiencias.

## Inputs
- Matriz hecho-prueba (`construir_matriz_hecho_prueba`).
- Inventario de evidencia y clasificación de prueba.
- Elementos del tipo penal (preliminar, si existen).

## Outputs
- Por elemento/hecho: `fuerza` (directa | indirecta | circunstancial | ausente).
- `suficiencia_global_preliminar`: robusta | media | débil | no_evaluable.
- Elementos críticos sin soporte adecuado.
- Advertencia: `NO ES CERTEZA JUDICIAL NI DICTAMEN DE CULPABILIDAD`.
- Etiqueta: `ANÁLISIS PRELIMINAR PROBATORIO`.

## Steps
1. Evaluar fuerza preliminar del soporte (directo, indirecto, circunstancial).
2. Identificar elementos del tipo penal con soporte débil o ausente.
3. Conclusión preliminar de suficiencia sin afirmar certeza judicial.
4. Relacionar debilidades con plan de recaudo sugerido.
5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_expediente_search`

## Guardrails (g1–g10)
- **g1:** No inventar pruebas ni testimonios.
- **g3:** Suficiencia preliminar ≠ más allá de duda razonable demostrado.
- **g5:** No usar lenguaje que culpe a la víctima por “falta de prueba”.
- **g9:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **g4:** HITL obligatorio antes de usar la salida en memorial, estrategia o comunicación con cliente.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No detectar brechas (`detectar_brechas_probatorias`).
- No plan de recaudo (`crear_plan_recaudo_probatorio`).

## Riesgo si se omite
Estrategia basada en prueba imaginaria o, al revés, abandono prematuro de líneas argumentativas viables.
