---
name: identificar-conductas-punibles-preliminares
description: Skill operativo penal-victimas: proponer posibles conductas punibles con base en hechos, sin conclusion definitiva. Use when the workflow requires `identificar_conductas_punibles_preliminares`.
disable-model-invocation: true
---

# identificar_conductas_punibles_preliminares

## Scope
- Category: `Skills de tipicidad y responsabilidad penal`
- Skill ID: `identificar_conductas_punibles_preliminares`
- Tier: `operativo`

## Used By Agents
- `analista_tipicidad_y_responsabilidad_penal`

## Purpose
Mapear conductas descritas en hechos verificados contra tipos penales hipotéticos, sin conclusión definitiva ni imputación.

## Rol en analista_tipicidad
Punto de entrada del agente tras cronología verificada. Alimenta `descomponer_elementos_tipo_penal` y `detectar_riesgos_atipicidad`.

## Inputs
- Cronología y hechos soportados (`verificar_hechos_soportados` del analista de cronología).
- Mapa de actores.
- Objetivos de la víctima (si constan).
- Tipos penales a explorar (si el abogado los indicó).

## Outputs
- Hipótesis: `tipo_penal_hipotetico`, `articulo_cp` (solo si verificado en RAG), `conducta_mapeada`, `nivel_confianza` (alta | media | baja), `motivo`.
- Atipicidad evidente descartada (con razón).
- Etiqueta obligatoria: `HIPÓTESIS PRELIMINAR — NO IMPUTACIÓN`.

## Steps
1. Mapear conductas descritas contra tipos penales del catálogo.
2. Priorizar hipótesis más sólidas y descartar atipicidad evidente.
3. Presentar como hipótesis, no conclusión.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_codigo_penal_search`
- `rag_normativo_search`

## Guardrails (g1–g10)
- **g1:** No inventar artículos del Código Penal ni conductas no descritas en hechos.
- **g2:** Sin hechos soportados mínimos, no proponer tipos; derivar a cronología.
- **g3:** Hipótesis ≠ hecho probado; separar conducta narrada de calificación.
- **g4:** HITL obligatorio antes de comunicar calificación a víctima o contraparte.
- **g5:** No sugerir tipos que revictimicen (ej. calificar defensa de víctima como delito).
- **g8:** Aviso de revisión profesional.

## Handoff
- Requiere entrada de `analista_cronologia_hechos_penales`: cronología + `verificar_hechos_soportados` con recomendación apta.
- Salida alimenta `identificar_conductas_punibles_preliminares` → `descomponer_elementos_tipo_penal` → `mapear_tipo_penal_hecho_prueba`.
- Si `detectar_riesgos_atipicidad` = alto → alertar coordinador y abogado antes de ruta penal.

## No duplicar
- No descomponer elementos (`descomponer_elementos_tipo_penal`).
- No extraer hechos (`extraer_hechos_relevantes`).
- No conclusión de autoría (`analizar_autoria_y_participacion`).

## Riesgo si se omite
Imputación o estrategia basada en tipo penal incorrecto desde el inicio del caso.
