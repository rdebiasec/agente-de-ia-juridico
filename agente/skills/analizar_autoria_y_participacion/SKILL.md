<!-- config-version: 3; checksum: 35c7c872eec68c0d -->
---
name: analizar-autoria-y-participacion
description: Contrato penal-víctimas: Evaluar preliminarmente autoría y participación (autor, coautor, cómplice) según hechos, sin imputación formal. Activar cuando el plan/HITL o el especialista requiera `analizar_autoria_y_participacion`. No sustituye a `identificar_actores_y_roles`.
disable-model-invocation: true
---

# analizar_autoria_y_participacion

## Scope
- Category: `Skills de tipicidad y responsabilidad penal`
- Skill ID: `analizar_autoria_y_participacion`
- Tier: `operativo`

## Used By Agents
- `analista_responsabilidad_tipicidad`

## Purpose
Evaluar preliminarmente autoría y participación (autor, coautor, cómplice) según hechos, sin imputación formal.

## Rol en analista_responsabilidad_tipicidad
Ejecutar tras descomposición de elementos y mapa de actores. En representación de víctimas: identificar posibles responsables, no absolver ni condenar.

## Fuentes KB
- `agente/conocimiento/penal.md` — marco tipico preliminar (no imputación).
- `agente/conocimiento/normas-clave.md` — criterio operativo y regla de citación.
- Herramientas: `leer_area_derecho(penal)`, `leer_normas_clave`, `buscar_en_conocimiento` antes de citar CP.
## Inputs
- Mapa de actores (`identificar_actores_y_roles`).
- Hechos soportados sobre conducta de cada interviniente.
- Tipo penal hipotético y elementos descompuestos.

## Outputs
- Por actor: `rol_preliminar` (autor | coautor | partícipe | testigo | sin_datos), `hechos_soporte`, `vacios_probatorios`, `riesgo`.
- Etiqueta: `PRELIMINAR — NO IMPUTACIÓN FORMAL`.

## Steps
0. Antes de citar normas o cerrar hipótesis: leer Fuentes KB (`penal.md` / `normas-clave.md`) vía tools de grounding; sin soporte → `[PENDIENTE DE VERIFICAR]`.
1. Describir aporte fáctico de cada persona (quién hizo qué) sin cerrar título de intervención.
2. Hipótesis preliminar: autor | coautor | cómplice | determinador | indeterminado — con hechos soporte.
3. Sin hechos de aporte → `[PENDIENTE DE VERIFICAR]`; no inventar roles.
4. Etiqueta `NO IMPUTACIÓN`; deferir calificación al abogado.


## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `analizar_autoria_y_participacion`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_codigo_penal_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `rag_expediente_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto

## Guardrails
- **No inventar:** No atribuir conducta sin hecho soportado.
- **Separar hecho de inferencia:** Distinción entre “mencionado” y “partícipe acreditado”.
- **Revision humana obligatoria:** No comunicar roles a Fiscalía o víctima sin revisión del abogado.
- **No revictimizar:** No sugerir participación de la víctima sin base factual.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No identificar actores (`identificar_actores_y_roles` — solo roles procesales básicos).
- No elemento subjetivo (`analizar_dolo_culpa_elemento_subjetivo`).
- No matriz hecho-prueba (`mapear_tipo_penal_hecho_prueba`).

## Riesgo si se omite
Estrategia dirigida contra persona equivocada o omisión de coautores relevantes.
