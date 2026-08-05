<!-- config-version: 2; checksum: a6c4a27c353681e9 -->
---
name: descomponer-elementos-tipo-penal
description: Contrato penal-víctimas: Descomponer tipos penales hipotéticos en elementos objetivos, subjetivos y normativos verificables contra el expediente. Activar cuando el plan/HITL o el especialista requiera `descomponer_elementos_tipo_penal`. No sustituye a `mapear_tipo_penal_hecho_...
disable-model-invocation: true
---

# descomponer_elementos_tipo_penal

## Scope
- Category: `Skills de tipicidad y responsabilidad penal`
- Skill ID: `descomponer_elementos_tipo_penal`
- Tier: `estrategico`

## Used By Agents
- `analista_responsabilidad_tipicidad` (skill primario del agente)

## Purpose
Descomponer tipos penales hipotéticos en elementos objetivos, subjetivos y normativos verificables contra el expediente.

## Rol en analista_responsabilidad_tipicidad
Núcleo dogmático del agente. Ejecutar tras hipótesis de conductas (`identificar_conductas_punibles_preliminares`).

## Inputs
- Hipótesis de tipos penales preliminares.
- Hechos soportados y cronología verificada.
- Artículos del CP verificados en RAG (`citation_checker`).

## Outputs
- Por cada tipo hipotético: `elemento` (conducta | resultado | nexo | tipicidad_especial | dolo | culpa | sujeto), `hecho_soporte`, `estado` (cubierto | parcial | vacío), `duda_tipicidad`.
- Lista de elementos sin soporte factual.
- Etiqueta: `ANÁLISIS DOGMÁTICO PRELIMINAR`.

## Steps
1. Tomar hipótesis tipica tentativa (no definitiva) del contexto.
2. Listar elementos objetivos/subjetivos del tipo y mapear a hechos/prueba disponibles.
3. Marcar elementos sin soporte como brecha / pendiente.
4. No afirmar tipicidad definitiva ni inventar artículos.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `descomponer_elementos_tipo_penal`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_codigo_penal_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `citation_checker` — no implementada

## Guardrails
- **No inventar:** Artículos y elementos normativos solo desde RAG verificado.
- **Separar hecho de inferencia:** Elemento cubierto requiere hecho soportado, no inferencia sola.
- **Revision humana obligatoria:** No usar en escrito de acusación o memorial sin revisión del abogado.
- **No revictimizar:** En delitos sexuales/violencia, no presuponer consentimiento en elementos subjetivos.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No mapear prueba por elemento (`mapear_tipo_penal_hecho_prueba`).
- No evaluar dolo en detalle (`analizar_dolo_culpa_elemento_subjetivo` — aquí solo identificar el elemento).
- No hipótesis iniciales (`identificar_conductas_punibles_preliminares`).

## Riesgo si se omite
Solicitudes y memoriales que omiten elementos objetivos o subjetivos exigidos por el tipo penal.
