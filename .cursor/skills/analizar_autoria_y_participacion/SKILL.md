---
name: analizar-autoria-y-participacion
description: Skill operativo penal-victimas: evaluar posibles roles de los intervinientes de manera preliminar. Use when the workflow requires `analizar_autoria_y_participacion`.
disable-model-invocation: true
---

# analizar_autoria_y_participacion

## Scope
- Category: `Skills de tipicidad y responsabilidad penal`
- Skill ID: `analizar_autoria_y_participacion`
- Tier: `operativo`

## Used By Agents
- `analista_tipicidad_y_responsabilidad_penal`

## Purpose
Evaluar preliminarmente autoría y participación (autor, coautor, cómplice) según hechos, sin imputación formal.

## Rol en analista_tipicidad
Ejecutar tras descomposición de elementos y mapa de actores. En representación de víctimas: identificar posibles responsables, no absolver ni condenar.

## Inputs
- Mapa de actores (`identificar_actores_y_roles`).
- Hechos soportados sobre conducta de cada interviniente.
- Tipo penal hipotético y elementos descompuestos.

## Outputs
- Por actor: `rol_preliminar` (autor | coautor | partícipe | testigo | sin_datos), `hechos_soporte`, `vacios_probatorios`, `riesgo`.
- Etiqueta: `PRELIMINAR — NO IMPUTACIÓN FORMAL`.

## Steps
1. Identificar posibles autores, coautores y partícipes según hechos.
2. Evaluar preliminarmente conductas de cada interviniente.
3. Señalar vacíos probatorios en autoría/participación.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_codigo_penal_search`
- `rag_expediente_search`

## Guardrails (g1–g10)
- **g1:** No atribuir conducta sin hecho soportado.
- **g3:** Distinción entre “mencionado” y “partícipe acreditado”.
- **g4:** No comunicar roles a Fiscalía o víctima sin revisión del abogado.
- **g5:** No sugerir participación de la víctima sin base factual.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No identificar actores (`identificar_actores_y_roles` — solo roles procesales básicos).
- No elemento subjetivo (`analizar_dolo_culpa_elemento_subjetivo`).
- No matriz hecho-prueba (`mapear_tipo_penal_hecho_prueba`).

## Riesgo si se omite
Estrategia dirigida contra persona equivocada o omisión de coautores relevantes.
