<!-- config-version: 3; checksum: 253196d5d4811d27 -->
---
name: preparar-preguntas-audiencia
description: Contrato penal-víctimas: Redactar preguntas neutrales y no inductivas para víctima, testigos o peritos, alineadas a matriz hecho-prueba y objetivo de audiencia. Activar cuando el plan/HITL o el especialista requiera `preparar_preguntas_audiencia`. No sustituye a `preparar_guio...
disable-model-invocation: true
---

# preparar_preguntas_audiencia

## Scope
- Category: `Skills de audiencias`
- Skill ID: `preparar_preguntas_audiencia`
- Tier: `operativo`

## Used By Agents
- `analista_audiencias` (skill primario del agente)

## Purpose
Redactar preguntas neutrales y no inductivas para víctima, testigos o peritos, alineadas a matriz hecho-prueba y objetivo de audiencia.

## Rol en analista_audiencias
Guion probatorio oral alineado con hechos y teoría del caso.
## Fuentes KB
- `agente/conocimiento/proceso-penal-906.md` — checklist preparación O6; no revictimizar.
- `agente/conocimiento/normas-clave.md` — dignidad/protección; minimizar exposición íntima no pertinente.
- Tools reales: `leer_playbook_proceso`, `leer_normas_clave`, `buscar_en_conocimiento`, `buscar_en_expediente`.

## Inputs
- Objetivo de audiencia (`identificar_objetivo_audiencia`).
- Matriz hecho-prueba y cronología verificada.
- Tipo de audiencia y etapa Ley 906.

## Outputs
- Preguntas por bloque: `destinatario`, `objetivo_probatorio`, `pregunta`, `riesgo`, `alternativa_segura`.
- Orden lógico; preguntas de alto riesgo señaladas.
- Etiqueta: `REVISAR CON ABOGADO — ESPECIALMENTE PREGUNTAS A VÍCTIMA`.

## Steps
0. Anclar tipo de audiencia/etapa/objetivo a Fuentes KB; sin soporte → `[PENDIENTE DE VERIFICAR]`.
1. Definir objetivo de la audiencia y hechos a acreditar.
2. Redactar preguntas abiertas/cerradas sin revictimizar.
3. Separar preguntas a testigos/peritos vs solicitudes orales.
4. No sustituir guion completo ni simulación.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `preparar_preguntas_audiencia`.

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
- **Revision humana obligatoria:** HITL obligatorio antes de audiencia.
- **No revictimizar:** No revictimizar; evitar preguntas sobre vida íntima no pertinente.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No guion completo (`preparar_guion_intervencion_oral`).
- No preguntas genéricas de aclaración (`generar_preguntas_aclaracion`).

## Riesgo si se omite
Audiencia improvisada con preguntas inductivas o revictimizantes.
