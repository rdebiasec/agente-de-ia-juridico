<!-- config-version: 2; checksum: c633dc9426b9a1d7 -->
---
name: construir-teoria-caso-victima
description: Skill critico penal-victimas: formular teoria preliminar del caso desde la victima. Use when the workflow requires `construir_teoria_caso_victima`.
disable-model-invocation: true
---

# construir_teoria_caso_victima

## Scope
- Category: `Skills de representacion de victimas`
- Skill ID: `construir_teoria_caso_victima`
- Tier: `critico`

## Used By Agents
- `analista_representacion_victimas` (skill primario del agente)
- `analista_audiencias`

## Purpose
Formular teoría preliminar del caso centrada en la víctima: hechos, intereses, tipicidad preliminar y plan probatorio.

## Rol en analista_representacion_victimas
Producto nuclear del agente. Requiere cronología verificada y tipicidad preliminar.

## Rol en preparador_audiencias
Marco narrativo para audiencia; no reemplaza guion táctico.

## Inputs
- Cronología y hechos soportados.
- Intereses de la víctima (`identificar_intereses_victima`).
- Hipótesis tipicidad y matriz tipo-prueba (si existen).
- Enfoque diferencial y riesgo revictimización.

## Outputs
- Teoría del caso: narrativa factual, objetivos, fortalezas/debilidades, riesgos.
- Vínculo con actuaciones Ley 906 disponibles.
- Etiqueta: `TEORÍA PRELIMINAR — APROBACIÓN ABOGADO Y VÍCTIMA`.

## Steps
1. Precisar intereses y objetivos de la víctima en el caso concreto.
2. Sintetizar narrativa factual centrada en la víctima con fuentes.
3. Vincular teoría con tipicidad preliminar y elementos del tipo.
4. Integrar plan probatorio y actuaciones Ley 906 disponibles.
5. Identificar fortalezas, debilidades y riesgos de la postura.
6. Alinear con enfoque diferencial y no revictimización.
7. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `construir_teoria_caso_victima`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_expediente_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `rag_normativo_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto

## Guardrails (g1–g10)
- **g1:** No inventar hechos ni normas.
- **g3:** Narrativa factual separada de estrategia y de calificación penal definitiva.
- **g4:** HITL obligatorio; no comunicar teoría al cliente sin abogado.
- **g5:** Teoría no culpa ni expone innecesariamente a la víctima.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No priorizar objetivos (`priorizar_objetivos_representacion` — preliminar en coordinador).
- No guion de audiencia (`preparar_guion_intervencion_oral`).

## Riesgo si se omite
Estrategia desconectada de la víctima o de la prueba disponible.
