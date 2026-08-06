<!-- config-version: 3; checksum: 22b07fae999888bb -->
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
