<!-- config-version: 3; checksum: cb2faf58557a3d65 -->
---
name: construir-teoria-caso-victima
description: Contrato penal-víctimas: Formular teoría preliminar del caso centrada en la víctima: hechos, intereses, tipicidad preliminar y plan probatorio. Activar cuando el plan/HITL o el especialista requiera `construir_teoria_caso_victima`. No sustituye a `priorizar_objetivos_represent...
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

## Rol en analista_audiencias
Marco narrativo para audiencia; no reemplaza guion táctico.

## Fuentes KB
- `agente/conocimiento/normas-clave.md` — derechos, no revictimización, HITL antes de comunicar teoría al cliente.
- `agente/conocimiento/proceso-penal-906.md` — checklist representación / intervención víctima y etapa aparente.
- Tools reales: `buscar_en_expediente`, `buscar_en_conocimiento`, lecturas KB (`leer_normas_clave` / `leer_playbook_proceso` / `leer_area_derecho`).

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
0. Anclar derechos/etapa/no-revictimización a Fuentes KB; sin soporte → `[PENDIENTE DE VERIFICAR]`.
1. Integrar hechos, derechos e intereses de la víctima en teoría tentativa.
2. Separar confirmado / narrado / inferido.
3. No prometer resultados judiciales ni culpabilizar a la víctima.
4. Alinear luego con prueba/ruta vía skills vecinos, no invadirlos aquí.

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

## Guardrails
- **No inventar:** No inventar hechos ni normas.
- **Separar hecho de inferencia:** Narrativa factual separada de estrategia y de calificación penal definitiva.
- **Revision humana obligatoria:** HITL obligatorio; no comunicar teoría al cliente sin abogado.
- **No revictimizar:** Teoría no culpa ni expone innecesariamente a la víctima.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No priorizar objetivos (`priorizar_objetivos_representacion` — preliminar en coordinador).
- No guion de audiencia (`preparar_guion_intervencion_oral`).

## Riesgo si se omite
Estrategia desconectada de la víctima o de la prueba disponible.
