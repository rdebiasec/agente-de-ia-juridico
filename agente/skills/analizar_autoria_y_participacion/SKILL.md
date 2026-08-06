<!-- config-version: 3; checksum: 99f02ad4967f721a -->
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
1. Partir del mapa de actores y hechos soportados por interviniente (`penal.md` §Autoría).
2. Asignar `rol_preliminar` (autor | coautor | partícipe | testigo | sin_datos) con hechos_soporte; sin imputación formal.
3. Señalar vacíos probatorios y riesgo de atribuir conducta no acreditada.
4. Normas de autoría/participación del CP: solo si verificadas en RAG; si no → `[PENDIENTE DE VERIFICAR]`.
5. Etiqueta `PRELIMINAR — NO IMPUTACIÓN FORMAL`; revisión humana antes de comunicar roles.

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


## Fuentes KB (obligatorio consultar antes de citar norma)
- `agente/conocimiento/penal.md` — marco tipico, dolo/culpa, autoría, agravantes.
- `agente/conocimiento/normas-clave.md` — marco Ley 599/906 + checklist de citación.
- Tools: `leer_area_derecho` (penal), `leer_normas_clave`, `buscar_en_conocimiento`.
- Artículo concreto no verificado → `[PENDIENTE DE VERIFICAR]`. No inventar normas.

## No duplicar
- No identificar actores (`identificar_actores_y_roles` — solo roles procesales básicos).
- No elemento subjetivo (`analizar_dolo_culpa_elemento_subjetivo`).
- No matriz hecho-prueba (`mapear_tipo_penal_hecho_prueba`).

## Riesgo si se omite
Estrategia dirigida contra persona equivocada o omisión de coautores relevantes.
