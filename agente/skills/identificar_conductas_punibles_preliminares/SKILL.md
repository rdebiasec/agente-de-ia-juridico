<!-- config-version: 3; checksum: 4f9597371c9c3c27 -->
---
name: identificar-conductas-punibles-preliminares
description: Contrato penal-víctimas: Mapear conductas descritas en hechos verificados contra tipos penales hipotéticos, sin conclusión definitiva ni imputación. Activar cuando el plan/HITL o el especialista requiera `identificar_conductas_punibles_preliminares`. No sustituye a `descompone...
disable-model-invocation: true
---

# identificar_conductas_punibles_preliminares

## Scope
- Category: `Skills de tipicidad y responsabilidad penal`
- Skill ID: `identificar_conductas_punibles_preliminares`
- Tier: `operativo`

## Used By Agents
- `analista_responsabilidad_tipicidad`

## Purpose
Mapear conductas descritas en hechos verificados contra tipos penales hipotéticos, sin conclusión definitiva ni imputación.

## Rol en analista_responsabilidad_tipicidad
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
1. Listar conductas narradas con soporte fáctico mínimo.
2. Asociar hipótesis tipicas tentativas (no definitivas) sin forzar tipo.
3. Marcar conductas atípicas o insuficientes como riesgo/pendiente.
4. Derivar descomposición elemental a `descomponer_elementos_tipo_penal`.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `identificar_conductas_punibles_preliminares`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_codigo_penal_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `rag_normativo_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto

## Guardrails
- **No inventar:** No inventar artículos del Código Penal ni conductas no descritas en hechos.
- **Pedir datos faltantes:** Sin hechos soportados mínimos, no proponer tipos; derivar a cronología.
- **Separar hecho de inferencia:** Hipótesis ≠ hecho probado; separar conducta narrada de calificación.
- **Revision humana obligatoria:** HITL obligatorio antes de comunicar calificación a víctima o contraparte.
- **No revictimizar:** No sugerir tipos que revictimicen (ej. calificar defensa de víctima como delito).
- **Aviso de borrador:** Aviso de revisión profesional.

## Handoff
- Requiere entrada de `analista_cronologia_hechos`: cronología + `verificar_hechos_soportados` con recomendación apta.
- Salida alimenta `identificar_conductas_punibles_preliminares` → `descomponer_elementos_tipo_penal` → `mapear_tipo_penal_hecho_prueba`.
- Si `detectar_riesgos_atipicidad` = alto → alertar coordinador y abogado antes de ruta penal.

## No duplicar
- No descomponer elementos (`descomponer_elementos_tipo_penal`).
- No extraer hechos (`extraer_hechos_relevantes`).
- No conclusión de autoría (`analizar_autoria_y_participacion`).

## Riesgo si se omite
Imputación o estrategia basada en tipo penal incorrecto desde el inicio del caso.
