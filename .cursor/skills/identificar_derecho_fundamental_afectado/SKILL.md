---
name: identificar-derecho-fundamental-afectado
description: Skill atomico penal-victimas: identificar posibles derechos fundamentales comprometidos. Use when the workflow requires `identificar_derecho_fundamental_afectado`.
disable-model-invocation: true
---

# identificar_derecho_fundamental_afectado

## Scope
- Category: `Skills constitucionales y tutela`
- Skill ID: `identificar_derecho_fundamental_afectado`
- Tier: `operativo`

## Used By Agents
- `evaluador_derechos_fundamentales_tutela`

## Purpose
Identificar qué derechos fundamentales podrían estar comprometidos según los hechos del caso.


## Rol en evaluador_tutela
Primer filtro constitucional antes de subsidiariedad y procedencia.
## Inputs
- Hechos verificados y narrados del caso.
- Conductas u omisiones de autoridades.
- Catálogo constitucional (RAG).

## Outputs
- `derechos_identificados`: derecho | titular | posible_vulnerador | relevancia (alta | media | baja).
- Vacíos para matriz hecho-derecho.
- Etiqueta: `IDENTIFICACIÓN PRELIMINAR — NO DICTAMEN PROCEDENCIA`.

## Steps
1. Mapear hechos del caso contra catálogo de derechos fundamentales aplicables.
2. Precisar titular del derecho y autoridad o sujeto vulnerador.
3. Priorizar derechos más directamente comprometidos para análisis posterior.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `identificar_derecho_fundamental_afectado`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_constitucion_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `rag_expediente_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto

## Guardrails (g1–g10)
- **g1:** No inventar vulneraciones.
- **g3:** Identificación preliminar; hecho sin soporte → `[PENDIENTE DE VERIFICAR]`.
- **g4:** HITL obligatorio; no dictamina procedencia ni autoriza tutela.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No matriz hecho-derecho (`crear_matriz_hecho_derecho_fundamental`).
- No procedencia (`evaluar_procedencia_tutela`).

## Riesgo si se omite
Tutela mal encaminada invocando derechos no comprometidos en los hechos.
