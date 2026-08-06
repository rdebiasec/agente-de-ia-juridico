<!-- config-version: 3; checksum: 3659be9774e3a46a -->
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
1. Tomar hipótesis tipica tentativa (no definitiva); contrastar norma con `leer_normas_clave` / RAG (`penal.md` §Marco tipico paso 3).
2. Listar elementos **objetivos** (conducta, resultado, nexo, tipicidad especial, sujeto) y **subjetivos** (dolo/culpa) del tipo.
3. Mapear cada elemento a hecho_soporte / prueba; estado = cubierto | parcial | vacío.
4. Elementos sin soporte → brecha + `[PENDIENTE DE VERIFICAR]`; no inventar artículos ni tipicidad definitiva.
5. Etiqueta `ANÁLISIS DOGMÁTICO PRELIMINAR`; dolo detallado → `analizar_dolo_culpa_elemento_subjetivo`.

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


## Fuentes KB (obligatorio consultar antes de citar norma)
- `agente/conocimiento/penal.md` — marco tipico, dolo/culpa, autoría, agravantes.
- `agente/conocimiento/normas-clave.md` — marco Ley 599/906 + checklist de citación.
- Tools: `leer_area_derecho` (penal), `leer_normas_clave`, `buscar_en_conocimiento`.
- Artículo concreto no verificado → `[PENDIENTE DE VERIFICAR]`. No inventar normas.

## No duplicar
- No mapear prueba por elemento (`mapear_tipo_penal_hecho_prueba`).
- No evaluar dolo en detalle (`analizar_dolo_culpa_elemento_subjetivo` — aquí solo identificar el elemento).
- No hipótesis iniciales (`identificar_conductas_punibles_preliminares`).

## Riesgo si se omite
Solicitudes y memoriales que omiten elementos objetivos o subjetivos exigidos por el tipo penal.
