<!-- config-version: 3; checksum: a50daed6e1dd96bb -->
---
name: analizar-enfoque-diferencial
description: Contrato penal-víctimas: Identificar factores diferenciales relevantes (género, edad, discapacidad, etnia, etc.) que exijan enfoque especial en la representación. Activar cuando el plan/HITL o el especialista requiera `analizar_enfoque_diferencial`. No sustituye a `controlar_n...
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

## Fuentes KB
- `agente/conocimiento/normas-clave.md` — enfoque diferencial y protección frente a revictimización.
- Expediente/relato: solo factores documentados; sin inventar identidad/condición.
- Tools reales: `buscar_en_expediente`, `buscar_en_conocimiento`, `leer_normas_clave`.

## Inputs
- Datos de la víctima disponibles (solo los documentados; no inferir).
- Tipo de delito y contexto del caso.
- Materiales a revisar (teoría, preguntas, memorial).

## Outputs
- `factores_diferenciales` documentados con fuente o `[PENDIENTE DE VERIFICAR]`.
- `ajustes_recomendados` en lenguaje, ritmo procesal o medidas de protección.
- `alertas` si el material ignora enfoque diferencial obligatorio.

## Steps
0. Anclar derechos/etapa/no-revictimización a Fuentes KB; sin soporte → `[PENDIENTE DE VERIFICAR]`.
1. Identificar factores diferenciales relevantes con base documentada.
2. Evaluar impacto en representación, comunicación y medidas de protección.
3. Proponer ajustes concretos al plan de actuación.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `analizar_enfoque_diferencial`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_normas_victimas_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto

## Guardrails
- **No inventar:** No inferir identidad o condición no documentada.
- **No revictimizar:** No estigmatizar a la víctima al nombrar factores diferenciales.
- **Confidencialidad:** Minimizar datos sensibles innecesarios.
- **Revision humana obligatoria:** HITL obligatorio antes de incorporar hallazgos a escritos o comunicación externa.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No revisión detallada de revictimización (`controlar_no_revictimizacion`).

## Riesgo si se omite
Revictimización o desatención de garantías especiales aplicables a la víctima.
