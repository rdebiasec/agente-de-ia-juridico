<!-- config-version: 3; checksum: 28af5830ee6ad367 -->
---
name: simular-escenarios-audiencia
description: Contrato penal-víctimas: Anticipar escenarios favorable, intermedio y adverso en audiencia y preparar respuesta táctica del abogado. Activar cuando el plan/HITL o el especialista requiera `simular_escenarios_audiencia`. No sustituye a `preparar_guion_intervencion_oral`.
disable-model-invocation: true
---

# simular_escenarios_audiencia

## Scope
- Category: `Skills de audiencias`
- Skill ID: `simular_escenarios_audiencia`
- Tier: `estrategico`

## Used By Agents
- `analista_audiencias`

## Purpose
Anticipar escenarios favorable, intermedio y adverso en audiencia y preparar respuesta táctica del abogado.

## Rol en analista_audiencias
Ejecutar tras `identificar_objetivo_audiencia` y antes o junto al guion oral.

## Fuentes KB
- `agente/conocimiento/proceso-penal-906.md` — checklist O6; escenarios no predicen fallo.
- `agente/conocimiento/normas-clave.md` — no prometer resultado judicial.
- Tools reales: `leer_playbook_proceso`, `leer_normas_clave`, `buscar_en_conocimiento`, `buscar_en_expediente`.

## Inputs
- Objetivo de audiencia y teoría del caso.
- Contraargumentos anticipados (`preparar_contraargumentos`, si existe).
- Fortalezas y debilidades probatorias preliminares.
- Postura probable de Fiscalía y defensa (hipótesis, no certezas).

## Outputs
- Tres escenarios: `favorable`, `intermedio`, `adverso` con descripción breve.
- `respuesta_tactica` por escenario (qué decir, qué pedir, qué evitar).
- `senales_cambio_escenario` durante la audiencia.
- Etiqueta: `SIMULACIÓN PRELIMINAR — NO PREDICE DECISIÓN DEL JUEZ`.

## Steps
0. Anclar tipo de audiencia/etapa/objetivo a Fuentes KB; sin soporte → `[PENDIENTE DE VERIFICAR]`.
1. Plantear escenarios favorable, intermedio y adverso probables.
2. Definir respuesta táctica para cada escenario.
3. Listar señales en audiencia que indiquen cambio de escenario.
4. Cruzar escenarios adverso con plan de contingencia (aplazamiento, solicitud oral, etc.).
5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `simular_escenarios_audiencia`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_expediente_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto

## Guardrails
- **No inventar:** No predecir decisiones del juez ni declaraciones de testigos no documentadas.
- **Separar hecho de inferencia:** Escenarios son hipótesis tácticas, no hechos.
- **Revision humana obligatoria:** HITL; simulación para preparación del abogado, no para la víctima sin filtro.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No guion literal (`preparar_guion_intervencion_oral`).
- No contraargumentos detallados (`preparar_contraargumentos`).

## Riesgo si se omite
Improvisación ante imprevistos de Fiscalía o defensa; pérdida de oportunidad procesal en audiencia.
