---
name: descomponer-elementos-tipo-penal
description: Skill estrategico penal-victimas: dividir un posible delito en elementos juridicos verificables. Use when the workflow requires `descomponer_elementos_tipo_penal`.
disable-model-invocation: true
---

# descomponer_elementos_tipo_penal

## Scope
- Category: `Skills de tipicidad y responsabilidad penal`
- Skill ID: `descomponer_elementos_tipo_penal`
- Tier: `estrategico`

## Used By Agents
- `analista_tipicidad_y_responsabilidad_penal` (skill primario del agente)

## Purpose
Descomponer tipos penales hipotéticos en elementos objetivos, subjetivos y normativos verificables contra el expediente.

## Rol en analista_tipicidad
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
1. Seleccionar tipos penales hipotéticos aplicables.
2. Descomponer conducta, resultado, nexo y elementos normativos.
3. Documentar dudas de tipicidad.
4. Registrar dudas de tipicidad por elemento sin concluir culpabilidad.
5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_codigo_penal_search`
- `citation_checker`

## Guardrails (g1–g10)
- **g1:** Artículos y elementos normativos solo desde RAG verificado.
- **g3:** Elemento cubierto requiere hecho soportado, no inferencia sola.
- **g4:** No usar en escrito de acusación o memorial sin revisión del abogado.
- **g5:** En delitos sexuales/violencia, no presuponer consentimiento en elementos subjetivos.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No mapear prueba por elemento (`mapear_tipo_penal_hecho_prueba`).
- No evaluar dolo en detalle (`analizar_dolo_culpa_elemento_subjetivo` — aquí solo identificar el elemento).
- No hipótesis iniciales (`identificar_conductas_punibles_preliminares`).

## Riesgo si se omite
Solicitudes y memoriales que omiten elementos objetivos o subjetivos exigidos por el tipo penal.
