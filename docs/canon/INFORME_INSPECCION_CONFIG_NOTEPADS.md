# Informe vivo — Inspección config + notepads (F1–F4)

**Plan inspección:** [`PLAN_INSPECCION_CONFIG_NOTEPADS.md`](PLAN_INSPECCION_CONFIG_NOTEPADS.md)  
**Plan análisis por agente:** [`PLAN_ANALISIS_PROMPTS_SKILLS_HERRAMIENTAS.md`](PLAN_ANALISIS_PROMPTS_SKILLS_HERRAMIENTAS.md) (`A0–A8 COMPLETO` + oleada **X COMPLETA** 2026-08-05)  
**Fecha:** 2026-08-05  
**E0:** Auto (humano)  
**Modo:** panel IA personificado + síntesis E0  
**Piloto:** `config/evals/agent_eval_cases.json` (v3.9)  
**Drive:** `https://drive.google.com/drive/folders/0ABOGkPnKHSC5Uk9PVA` (dual DB+Drive; **F5 notepads en progreso** — plantillas + sync)  
**Rama de trabajo A0–A8/X:** `cursor/analisis-a0-a1-prompts-skills` (merged PR #9)  
**PR análisis:** https://github.com/rdebiasec/agente-de-ia-juridico/pull/9  
**Rama F5 / Top-15:** `cursor/f5-notepads-top15`

### Nota ops — Sync config post PR #9 (2026-08-06)

- **Fallo:** run [`31068465432`](https://github.com/rdebiasec/agente-de-ia-juridico/actions/runs/31068465432) — headers A0–A8 > versiones activas en prod → `unknown` / «falta baseline de header».
- **No usar `--allow-conflicts`:** omite bloqueados; no publica el repo.
- **Remediación:** header adelantado → `file_ahead` (GitOps archivo→DB). Detalle: [`docs/operaciones/NOTA_SYNC_CONFIG_POST_PR9.md`](../operaciones/NOTA_SYNC_CONFIG_POST_PR9.md).
- **Fuera de alcance:** F4 auth, F5 notepads.

---

## Estado de fases

| Fase | Estado |
|---|---|
| F1 Inventario | **Hecho** |
| F2 O1 Tipicidad | **Hecho** (hallazgos + patches H-101…H-105) |
| F2 O2 Ruta 906 | **Hecho** (hallazgos + patches H-201…H-203) |
| F3 Prompts/guardrails/HITL | **Hecho** (H-301…H-304) |
| F4 Panel 12 servicio | **Hecho — NO LISTO** (ver `INFORME_AUDITORIA_12_ESPECIALISTAS_SERVICIO_WEB.md`) |
| F5 Spec notepads | **En progreso** — plantillas `agente/notepads/`, render DB, sync Drive, runbook |
| F6 Top acciones E0 | **Hecho** |
| **A0** Re-score tipicidad + ruta | **Hecho** (residuales A-tipi / A-ruta + patches P0/P1) |
| **A1** Deep cronología | **Hecho** (scorecard + A-crono + patches P0/P1) |
| **A2** Deep evidencia | **Hecho** (scorecard + A-evid + patches P0/P1) |
| **A3** Deep víctimas | **Hecho** (scorecard + A-vict + patches P0/P1 + eval) |
| **A4** Deep audiencias | **Hecho** (scorecard + A-aud + patches P0/P1 + eval) |
| **A5** Deep redactor | **Hecho** (scorecard + A-reda + patches P0/P1 + eval) |
| **A6** Deep calidad | **Hecho** (scorecard + A-cali + patches P0/P1 + eval) |
| **A7** Deep seguimiento | **Hecho** (scorecard + A-segu + patches P0/P1 + eval) |
| **A8** Deep coordinador | **Hecho** (scorecard + A-coord + O8 gerencia + patches P0/P1 + eval) |
| **X** Cruzado | **Hecho** (A-xcut + Top 15 post-X + F-05 residual + F-06 CI + evals v3.9) |

---

## Resumen ejecutivo scorecards A0–A8

| Oleada | Agente | Veredicto | Técnica (min) | Jurídico (min) | Hallazgos clave |
|---|---|---|---|---|---|
| A0a | tipicidad | PASS post-patch | ≥4 | ≥4 | Fuentes KB O1 + schema `fuentes_kb` |
| A0b | ruta 906 | PASS post-patch | ≥4 | ≥4 | Enum etapas + eval route-ruta |
| A1 | cronología | PASS post-patch | ≥4 | ≥4 | O3 hechos/contradicciones |
| A2 | evidencia | PASS post-patch | ≥4 | ≥4 | O4 cadena custodia / brechas |
| A3 | víctimas | PASS post-patch | ≥4 | ≥4 | O5 + eval route-victimas |
| A4 | audiencias | PASS post-patch | ≥4 | ≥4 | O6 + HITL oralidad |
| A5 | redactor | PASS post-patch | ≥4 | ≥4 | O7 + HITL obligatorio chat |
| A6 | calidad | PASS post-patch | ≥4 | ≥4 | O7 citas / gate rechazado |
| A7 | seguimiento | PASS post-patch | ≥4 | ≥4 | O8 términos + eval surface |
| A8 | coordinador | PASS post-patch | ≥4 | ≥4 | O8 gerencia + anclas POC + surface |

**Cierre deep-dives:** A0–A8 **completos**. Oleada **X** **completa** (PR #9 merged). Track F5 notepads + quick wins P1 (F-03/F-04/F-11) en `cursor/f5-notepads-top15`. F4 auth portal = track aparte.

---

## F1 — Inventario de cobertura

| Superficie | Conteo | Veredicto |
|---|---|---|
| Skills `agente/skills/*/SKILL.md` | **81** | Cubiertos en catálogo; 0 sin Used By |
| Prompts agentes | **10/10** | Roster canónico completo |
| Guardrails I/O/T por agente | **10/10** (input+output+tools) | PASS cobertura archivos |
| Guardrails globales g1–g10 | **10** | Presentes |
| Eval cases | **49** (v3.9) | Routing/scope/HITL/PII + tool-surface/budget A0–A8 + X (ruta/tipicidad) |
| Evals → `analista_ruta_procesal` | **1** (`route-ruta-906`) | **PASS** (A0) |
| Evals → `analista_representacion_victimas` | **3** (`route-victimas`, `tool-surface-victimas`, `instruction-budget-victimas`) | **PASS** (A3) |
| Evals → `analista_audiencias` | **3** (`route-audiencia`, `tool-surface-audiencias`, `instruction-budget-audiencias`) | **PASS** (A4) |
| Evals → `redactor_documentos_juridicos` | **4** (`route-memorial`, `completeness-*`, `instruction-budget-redactor`, `tool-surface-redactor`) | **PASS** (A5) |
| Evals → `analista_calidad_juridica` | **4+** (`route-calidad-via-plan`, `tool-surface-calidad`, `instruction-budget-calidad`, `quality-gate-*`) | **PASS** (A6) |
| Evals → `analista_seguimiento_procesal` | **3** (`route-seguimiento`, `tool-surface-seguimiento`, `instruction-budget-seguimiento`) | **PASS** (A7) |
| Referencias KB path en skills O1–O8 | **81/81** con Fuentes KB | **PASS** (X: residual `controlar_separacion_hecho_inferencia`) |
| KB `penal.md` | marco tipico operativo | **PASS** (A0) |
| KB `proceso-penal-906.md` | etapas + checklists evidencia/intervención/prep. audiencia/redacción/calidad/seguimiento | **PASS** (A0–A7) |
| KB `normas-clave.md` | marco + derechos + checklist O5/O6/O7/O8 seguimiento | **PASS** (A3–A7) |
| Legacy prose residual O1/O2 | varios (“calidad”, “gestor”, “coordinador”) | PARTIAL |

### Matriz agente × primario × secundarios (runtime)

Fuente: `src/agents/skill_catalog.py`.

| Agente | Primario | Secundarios anclados | Gap vs skills owned |
|---|---|---|---|
| `analista_responsabilidad_tipicidad` | `descomponer_elementos_tipo_penal` | conductas, dolo, autoría | **OK (A0)** — atipicidad/mapear owned sin ancla runtime |
| `analista_ruta_procesal` | `identificar_etapa_procesal_ley906` | oportunidad, ruta, términos | **OK (A0)** — riesgos/impulso owned sin ancla runtime |
| `analista_cronologia_hechos` | `construir_cronologia_penal` | extraer, contradicciones, clasificar_fuente | **OK (A1)** |
| `analista_evidencia` | `inventariar_evidencia` | clasificar_tipo, matriz, brechas | **OK (A2)** — recaudo/custodia/preservar owned sin ancla runtime |
| `analista_representacion_victimas` | `construir_teoria_caso_victima` | derechos, riesgo_revictimizacion, priorizar_objetivos | **OK (A3)** — intereses/daño/diferencial/mapear owned sin ancla runtime |
| `analista_audiencias` | `preparar_preguntas_audiencia` | objetivo, guion, detectar_riesgos | **OK (A4)** — solicitudes/checklist/simulación/intervención owned sin ancla runtime |
| `redactor_documentos_juridicos` | `redactar_memorial_penal` | estructurar, marcar_pendientes, controlar_tono | **OK (A5)** — otras `redactar_*` owned sin ancla runtime |
| `analista_calidad_juridica` | `revisar_coherencia_estrategica` | alucinaciones, verificar_citas, clasificar_aprobacion | **OK (A6)** — jurisprudencia/confidencialidad/tono owned sin ancla runtime |
| `analista_seguimiento_procesal` | `monitorear_radicado` | alertas, inactividad, crear_reporte | **OK (A7)** — registrar/documentos/resumen/impulso owned sin ancla runtime |
| Resto | ver informe prompts previo | — | OK para esta ola |

---

## F2 / O1 — Tipicidad (L1 + T2)

### Scorecard rápido (rúbrica ≥4)

| Skill | Contrato estructural | Conocimiento procedural | Cita KB path | Veredicto |
|---|---|---|---|---|
| `identificar_conductas_punibles_preliminares` | 4 | 3 | 1 | PARTIAL |
| `descomponer_elementos_tipo_penal` | 4 | 3 | 1 | PARTIAL |
| `analizar_dolo_culpa_elemento_subjetivo` | 4 | 3 | 1 | PARTIAL |
| `analizar_autoria_y_participacion` | 4 | 3 | 1 | PARTIAL |
| `detectar_agravantes_atenuantes` | 4 | 3 | 1 | PARTIAL |
| `detectar_riesgos_atipicidad` | 4 | 3 | 1 | PARTIAL |
| `generar_preguntas_tipicidad` | 4 | 3 | 1 | PARTIAL |
| `mapear_tipo_penal_hecho_prueba` | 4 | 2 | 1 | PARTIAL |

Estructura (Purpose/Steps/No duplicar/No inventar) está en buen nivel post-ola previa.  
**Falla de calidad jurídica:** steps genéricos (“analizar…”) sin checklist dogmático anclado a KB; **ningún** skill O1 apunta a `agente/conocimiento/*`.

### Hallazgos O1

```yaml
id: H-101
severidad: P0
bloque: skills
archivo: agente/conocimiento/penal.md (+ normas-clave.md)
experto: L1
veredicto: FAIL
evidencia_repo: "penal.md 17 líneas; sección Notas del despacho vacía _(Completar)_"
evidencia_kb: "agente/conocimiento/penal.md; normas-clave.md (Ley 599 / 906 citadas sin marco tipico operativo)"
impacto: "skills de tipicidad mandan usar buscar_en_conocimiento/leer_normas_clave pero la KB no aporta checklist dogmático → alucinación o superficialidad"
fix_propuesto: "enriquecer KB con marco tipicidad/autoría/dolo SIN inventar artículos concretos; marcar verificación vía RAG"
porque: "prioridad #6 = calidad jurídica/procedural; sin KB el contrato de skill no tiene suelo"
evals_a_ampliar: ["route-tipicidad"]
```

```yaml
id: H-102
severidad: P0
bloque: skills
archivo: agente/skills/{O1}/*/SKILL.md
experto: L1+T2
veredicto: FAIL
evidencia_repo: "0/8 skills O1 contienen path agente/conocimiento o proceso-penal-906"
evidencia_kb: "proceso-penal-906.md §Rol del despacho; normas-clave.md §Criterio operativo"
impacto: "ancla de instrucciones no fuerza grounding en playbook oficial del repo"
fix_propuesto: "añadir ## Fuentes KB + steps que exijan leer_area_derecho/leer_normas_clave antes de citar CP"
porque: "Persistent Instruction Anchoring; skill_contract_brief no basta si el MD no nombra fuentes"
evals_a_ampliar: ["route-tipicidad"]
```

```yaml
id: H-103
severidad: P1
bloque: skills
archivo: src/agents/skill_catalog.py (_SECONDARY_SKILLS tipicidad)
experto: T2
veredicto: PARTIAL
evidencia_repo: "secundarios = conductas, atipicidad, mapear; omiten analizar_dolo_*, analizar_autoria_*, detectar_agravantes_*, generar_preguntas_tipicidad"
evidencia_kb: "penal.md (marco tipico); prompt analista_responsabilidad_tipicidad.md pasos 3–4"
impacto: "chat slim puede omitir anclas de dolo/autoría en turnos tipicidad"
fix_propuesto: "ampliar _SECONDARY_SKILLS tipicidad a incluir dolo + autoría (máx 2–3; rotar o ampliar techo)"
porque: "prompt del agente exige esos ejes; el ancla runtime no los trae"
evals_a_ampliar: ["tool-surface-tipicidad"]
```

```yaml
id: H-104
severidad: P1
bloque: skills
archivo: mapear_tipo_penal_hecho_prueba/SKILL.md; detectar_riesgos_atipicidad; generar_preguntas_tipicidad
experto: T2
veredicto: PARTIAL
evidencia_repo: "mapear L24 'gestor evidencia'; atipicidad No duplicar '→ calidad'; preguntas '→ tipicidad'"
evidencia_kb: "N/A (higiene de roster)"
impacto: "ownership documentado confunde con IDs legacy"
fix_propuesto: "IDs canónicos: analista_evidencia, analista_calidad_juridica, analista_responsabilidad_tipicidad"
porque: "H-003 previo; residual en O1"
evals_a_ampliar: []
```

```yaml
id: H-105
severidad: P1
bloque: skills
archivo: analizar_dolo_*; analizar_autoria_*; detectar_agravantes_*
experto: L1
veredicto: PARTIAL
evidencia_repo: "Steps 4 líneas genéricas; no checklist de indicios (conocimiento/voluntad) ni categorías de participación ancladas a KB"
evidencia_kb: "[PENDIENTE DE VERIFICAR] artículos concretos CP; marco en penal.md a enriquecer"
impacto: "salida dogmática inconsistente entre turnos"
fix_propuesto: "steps con checklist verificable + etiqueta NO IMPUTACIÓN + fuentes KB"
porque: "rúbrica Steps 3–7 verificables; calidad litigable"
evals_a_ampliar: ["route-tipicidad"]
```

---

## F2 / O2 — Ruta Ley 906 (L1 + L3)

```yaml
id: H-201
severidad: P0
bloque: skills
archivo: identificar_etapa_procesal_ley906/SKILL.md
experto: L1
veredicto: PARTIAL
evidencia_repo: "Outputs etapa_ley906: indagación|investigación|etapa_intermedia|juicio|ejecución_penal|archivo"
evidencia_kb: "proceso-penal-906.md Etapas 1–8 (indagación/investigación, preliminares, imputación, medida, acusación, preparatoria, juicio, recursos)"
impacto: "taxonomía del skill no mapea 1:1 al playbook oficial → rutas/oportunidad mal etiquetadas"
fix_propuesto: "alinear enum a etapas del playbook + campo evidencia_etapa; mapear aliases"
porque: "fuente sagrada de etapas es el playbook KB"
evals_a_ampliar: ["route-ruta-906 (nuevo)"]
```

```yaml
id: H-202
severidad: P1
bloque: skills
archivo: O2 skills (9)
experto: L1
veredicto: FAIL
evidencia_repo: "0/9 con path KB; crear_ruta Steps solo 3 genéricos"
evidencia_kb: "proceso-penal-906.md; normas-clave.md §Criterio operativo"
impacto: "ruta procesal sin ancla a etapas oficiales del repo"
fix_propuesto: "## Fuentes KB + steps que listen etapas playbook antes de proponer secuencia"
porque: "prioridad procedural knowledge"
evals_a_ampliar: ["route-ruta-906"]
```

```yaml
id: H-203
severidad: P1
bloque: evals
archivo: config/evals/agent_eval_cases.json
experto: T5
veredicto: FAIL
evidencia_repo: "ningún case expected_destination=analista_ruta_procesal"
evidencia_kb: "proceso-penal-906.md"
impacto: "regresión de routing ruta 906 silenciosa"
fix_propuesto: "añadir route-ruta-906 + completeness opcional"
porque: "cobertura eval asimétrica vs tipicidad/evidencia"
evals_a_ampliar: ["route-ruta-906"]
```

```yaml
id: H-204
severidad: P1
bloque: skills
archivo: controlar_terminos_*; proceso-penal-906.md §Términos
experto: L3
veredicto: PARTIAL
evidencia_repo: "playbook: 'cálculo automático… fase posterior'; skill estima fechas con ESTIMACIÓN IA"
evidencia_kb: "proceso-penal-906.md §Términos"
impacto: "riesgo de falsa certeza de plazos si steps no reiteran días hábiles + verificación"
fix_propuesto: "step explícito: días hábiles Ley 906; nunca certificar sin fecha_base; HITL"
porque: "ética + no autonomía indebida en plazos"
evals_a_ampliar: []
```

---

## F3 — Prompts, guardrails I/O/T y HITL

```yaml
id: H-301
severidad: P0
bloque: prompts
archivo: agente/prompts/agents/{analista_responsabilidad_tipicidad,analista_ruta_procesal}.md
veredicto: PARTIAL
evidencia_repo: "prompts no exigían fuentes KB ni el enum canónico 906; formato ruta era prosa libre"
evidencia_kb: "penal.md; normas-clave.md; proceso-penal-906.md"
impacto: "el runtime podía ignorar la procedural knowledge añadida en O1/O2"
fix_aplicado: "grounding obligatorio, checklist dogmático, enum 906, fecha base/días hábiles y formatos estructurados"
```

```yaml
id: H-302
severidad: P0
bloque: schemas
archivo: src/agents/schemas.py; src/agents/structured_render.py
veredicto: FAIL
evidencia_repo: "RutaProcesalLey906 solo exponía etapa_aparente libre y listas de strings; MatrizTipicidad no registraba fuentes KB ni estado del elemento"
evidencia_kb: "proceso-penal-906.md §Etapas; penal.md §Marco tipico"
impacto: "las reglas de prompts no eran enforceable mediante output_type"
fix_aplicado: "campos etapa_ley906 Literal, evidencia_etapa, ruta_detallada; fuentes_kb, etiqueta preliminar y estado por elemento; renderer actualizado"
```

```yaml
id: H-303
severidad: P1
bloque: guardrails
archivo: config/guardrails/agents/{tipicidad,ruta}/{input,output}.md
veredicto: PARTIAL
evidencia_repo: "guardrails genéricos; domain_limits de ruta vacío"
evidencia_kb: "penal.md; proceso-penal-906.md"
impacto: "el control declaraba I/O/T pero no exigía grounding, fecha base, días hábiles ni HITL accionable"
fix_aplicado: "required_context_policy + groundedness_policy + límites jurídicos específicos; headers versionados"
```

```yaml
id: H-304
severidad: P0
bloque: hitl
archivo: src/agents/plan_templates.py
veredicto: FAIL
evidencia_repo: "plantillas incluían art. 229 C.P., art. 134 y Ley 1826 sin fuente KB asociada"
evidencia_kb: "normas-clave.md §Regla de citación"
impacto: "el propio plan podía sembrar una cita no verificada antes de ejecutar guardrails del especialista"
fix_aplicado: "retirar números concretos del texto de plantilla; exigir norma verificada; test de regresión"
```

### Verificación F3

- `tests/test_guardrails_iot_coverage.py`: grounding tipicidad/ruta.
- `tests/test_l03_structured_output.py`: enum, evidencia de etapa y ruta detallada.
- `tests/test_fase3_plan_product.py`: plantillas sin citas normativas no verificadas.
- Suite completa de cierre F3: **52 passed**.

---

## Top 15 acciones E0 (prioridad #6)

| # | ID | Acción | Severidad | Estado |
|---|---|---|---|---|
| 1 | H-101 | Enriquecer `penal.md` + `normas-clave.md` (marco tipico/autoría/dolo sin arts inventados) | P0 | **Hecho (A0)** |
| 2 | H-102 | `## Fuentes KB` + steps grounding en 8 skills O1 | P0 | **Hecho (A0)** |
| 3 | H-201 | Alinear enum etapas skill ↔ playbook 906 | P0 | **Hecho (A0)** |
| 4 | H-202 | Fuentes KB + steps en skills O2 críticos (etapa, ruta, oportunidad, términos) | P1 | **Hecho (A0)** |
| 5 | H-103 | Ampliar `_SECONDARY_SKILLS` tipicidad (dolo, autoría) | P1 | **Hecho (A0)** |
| 6 | H-104 | Limpiar legacy prose O1 | P1 | **Hecho (A0)** |
| 7 | H-105 | Checklists dogmáticos en dolo/autoría/agravantes | P1 | **Hecho (A0)** |
| 8 | H-203 | Eval `route-ruta-906` | P1 | **Hecho (A0)** |
| 9 | H-204 | Endurecer disclaimer términos (días hábiles) | P1 | **Hecho (A0)** |
| 10 | H-301/H-302 | F3 prompts + schemas tipicidad/ruta frente a KB nueva | P0 | **Hecho (A0)** |
| 11 | H-303/H-304 | F3 guardrails específicos + retirar citas no verificadas de planes | P0/P1 | **Hecho (A0)** / H-304 ya limpio |
| 12 | — | F4: checklist panel 12 (1 día) | P1 | Pendiente |
| 13 | — | F5: notepads `{agent_id}.md` en Drive `0ABOGkPnKHSC5Uk9PVA` | P2 | Diferido |
| 14 | — | Evals tipicidad groundedness (matriz elementos) | P2 | Pendiente |
| 15 | — | Oleadas A3–A8 (ex O5–O8) | P1 | **A3–A8 Hecho; siguiente X** |

---

## Cierre parcial F1–F3 (nota de reconciliación A0)

**Hallazgo de proceso (A0):** el bloque “Cierre parcial de ejecución” abajo marcó H-101…H-304 como **Hecho**, pero al iniciar A0 en el árbol de trabajo **no** estaban aplicados (skills sin `## Fuentes KB`, `penal.md` sin marco tipico, schemas sin `etapa_ley906`/`fuentes_kb`, sin `route-ruta-906`).  
Los IDs `H-*` se conservan; la ejecución real de esos residuales se documenta como `A-tipi-*` / `A-ruta-*` / patches A0.

**Patches A0–A8 aplicados (2026-08-05)**
- KB: `agente/conocimiento/{penal,normas-clave,proceso-penal-906}.md` (marco tipico + enum etapas + días hábiles + checklists evidencia O4 + representación O5 + prep. audiencia O6 + redacción O7 + calidad/citas O7 + seguimiento O8 + **gerencia/POC O8**)
- Skills O1–O6 + O7 redacción/calidad + O8 parcial (seguimiento) + **O8 gerencia (4 skills POC + marcar_pendientes ya OK)** → `## Fuentes KB` + steps verificables + bump checksum
- `src/agents/skill_catalog.py` secundarios tipicidad/ruta/cronología/evidencia/víctimas/audiencias/redactor/calidad/seguimiento/**coordinador_caso**
- Schemas/renderer: `fuentes_kb` en tipicidad/ruta/crono/evidencia/víctimas/audiencias/redactor/DictamenCalidad/SeguimientoProcesal (POC chat = prosa + TriageResult en código)
- Prompts tipicidad…seguimiento + **coordinador v28** (`contratos_gerencia` + Fuentes KB) + guardrails I/O grounding
- Evals `3.8` + `route-coordinador-gerencia` + `tool-surface-coordinador` (+ cobertura previa A0–A7)
- Sync: espejo `.cursor/skills` en skills O8 gerencia tocados
- **A-vict-006 cerrado en A4:** `analizar_intervencion_victima` permanece Used By ruta+audiencias (sin MOVE a víctimas)
- **A-reda-005:** `marcar_pendientes_verificacion` Used By + Rol redactor (secundario)
- **A-cali-***: ver scorecard A6
- **A-segu-***: ver scorecard A7
- **A-coord-***: ver scorecard A8; G01–G09 reafirmados PASS

**Tests (A0–A8 + X focused):** ver commit oleada X (`test_prompt_skill_quality`, `test_agent_evals`, `test_l03_structured_output`, `test_guardrails_iot_coverage`, `test_skill_config`, `test_fase3_plan_product`). Evals suite **v3.9**.

**Siguiente oleada:** **X** — hallazgos cruzados + Top 15 (o PR de rama de análisis).

---

## A0a — Scorecard `analista_responsabilidad_tipicidad`

| Campo | Valor |
|---|---|
| Fecha | 2026-08-05 |
| Oleada | A0a |
| Expertos | L1, L3, T1, T2, T3, T5, E0 |
| Primario | `descomponer_elementos_tipo_penal` |
| Secundarios anclados | conductas, dolo, autoría |
| Skills owned (#) | 8 |
| Veredicto global | **PARTIAL → PASS tras patches** |

### Técnica (0–5)

| Eje | Score | Nota 1 línea |
|---|---|---|
| Prompt | 5 | v5: grounding KB + etiqueta NO IMPUTACIÓN + formato MatrizTipicidad |
| Few-shots / anti-drift | 4 | 2 few-shots; bloques `_shared` vía notas/deliberación |
| Ancla skills | 5 | Secundarios alineados a ejes dolo/autoría del prompt |
| Tools honesty | 5 | Solo REAL tools en skills |
| Guardrails I/O/T | 5 | groundedness + domain_limits específicos |
| Schema | 5 | `fuentes_kb`, `estado`, `etiqueta_preliminar` |
| HITL | 4 | No high-risk; memorial vía redactor HITL |
| Evals | 4 | `route-tipicidad` + `tool-surface-tipicidad` |
| Config parity | 4 | Headers versionados; sync skills OK |

### Jurídico-procedural (0–5)

| Eje | Score | Nota 1 línea |
|---|---|---|
| Grounding KB | 5 | `penal.md` + `normas-clave.md` en prompt/skills |
| Etapa 906 | 3 | N/A fuerte (delega a ruta); no inventa etapas |
| Tipicidad/dogmática | 5 | Checklist marco tipico + NO IMPUTACIÓN |
| Derechos víctima | 3 | Indirecto (no revictimizar en dolo sexual) |
| Hecho vs inferencia | 4 | Elementos con estado / pendientes |
| Términos/oportunidad | 2 | Fuera de dominio |
| Citas | 5 | Regla anti-siembra art. N |
| HITL accionable | 4 | No pieza radicable desde tipicidad |
| Alcance | 5 | Solo tipicidad preliminar penal-víctimas |
| Litigabilidad | 4 | Matriz usable por abogado |

### Hallazgos A0a

```yaml
id: A-tipi-001
severidad: P0
bloque: kb+skills
archivo: agente/conocimiento/penal.md; agente/skills/{O1}/*/SKILL.md
experto: L1
veredicto: PASS (patched)
evidencia_repo: "Al inicio A0: 0 Fuentes KB en O1; penal.md sin marco tipico (H-101/H-102 no aplicados en árbol)"
evidencia_kb: "agente/conocimiento/penal.md §Marco tipico; normas-clave.md §Checklist tipicidad"
impacto: "Hipótesis tipica sin suelo dogmático → alucinación o superficialidad"
fix_aplicado: "KB enriquecida + Fuentes KB + steps 0 grounding en 8 skills O1"
porque: "prioridad procedural knowledge; residual H-101/H-102"
evals_a_ampliar: ["route-tipicidad groundedness campos fuentes_kb (P2)"]
```

```yaml
id: A-tipi-002
severidad: P1
bloque: catalog
archivo: src/agents/skill_catalog.py
experto: T2
veredicto: PASS (patched)
evidencia_repo: "secundarios omitían dolo/autoría pese a prompt pasos 3–4 (H-103)"
evidencia_kb: "penal.md §Marco tipico pasos 4–5"
impacto: "ancla runtime incompleta en chat slim"
fix_aplicado: "_SECONDARY_SKILLS tipicidad = conductas + dolo + autoría"
porque: "prompt exige ejes; techo 3 secundarios"
evals_a_ampliar: ["tool-surface-tipicidad"]
```

```yaml
id: A-tipi-003
severidad: P0
bloque: schema
archivo: src/agents/schemas.py
experto: T3+L1
veredicto: PASS (patched)
evidencia_repo: "MatrizTipicidad sin fuentes_kb/estado/etiqueta (H-302 residual)"
evidencia_kb: "penal.md etiqueta NO IMPUTACIÓN"
impacto: "reglas de prompt no enforceables"
fix_aplicado: "campos estado, fuentes_kb, etiqueta_preliminar + renderer"
porque: "output_type debe reflejar contrato jurídico"
evals_a_ampliar: []
```

---

## A0b — Scorecard `analista_ruta_procesal`

| Campo | Valor |
|---|---|
| Fecha | 2026-08-05 |
| Oleada | A0b |
| Expertos | L1, L3, T1, T2, T3, T5, E0 |
| Primario | `identificar_etapa_procesal_ley906` |
| Secundarios anclados | oportunidad, ruta, términos |
| Skills owned (#) | ~9 |
| Veredicto global | **PARTIAL → PASS tras patches** |

### Técnica (0–5)

| Eje | Score | Nota 1 línea |
|---|---|---|
| Prompt | 5 | v7: enum `etapa_ley906`, fecha_base, formato schema |
| Few-shots / anti-drift | 4 | 2 few-shots anti-invención plazos |
| Ancla skills | 5 | + términos en secundarios |
| Tools honesty | 4 | Planned `process_lookup_query` marcado no invocable |
| Guardrails I/O/T | 5 | groundedness + domain_limits (ya no vacío) |
| Schema | 5 | Literal etapa + evidencia + ruta_detallada |
| HITL | 4 | Impulso/recurso → HITL redactor; no certifica plazos |
| Evals | 5 | `route-ruta-906` añadido (v3.2) |
| Config parity | 4 | Headers OK |

### Jurídico-procedural (0–5)

| Eje | Score | Nota 1 línea |
|---|---|---|
| Grounding KB | 5 | playbook 906 + normas-clave |
| Etapa 906 | 5 | Enum 1:1 playbook + aliases |
| Tipicidad/dogmática | 2 | Fuera de dominio |
| Derechos víctima | 4 | Ruta orientada a representación víctima |
| Hecho vs inferencia | 4 | evidencia_etapa vs pendiente |
| Términos/oportunidad | 5 | Días hábiles + ESTIMACIÓN IA |
| Citas | 4 | Sin arts sembrados en prompt |
| HITL accionable | 5 | No radicar por alerta IA |
| Alcance | 5 | Solo Ley 906 penal-víctimas |
| Litigabilidad | 4 | Ruta usable con evidencia_etapa |

### Hallazgos A0b

```yaml
id: A-ruta-001
severidad: P0
bloque: skills+schema
archivo: identificar_etapa_procesal_ley906; schemas.RutaProcesalLey906
experto: L1
veredicto: PASS (patched)
evidencia_repo: "enum skill indagación|investigación|etapa_intermedia… no mapeaba playbook 8 etapas (H-201)"
evidencia_kb: "proceso-penal-906.md §Etapas + §Enum operativo"
impacto: "oportunidad/ruta mal etiquetadas"
fix_aplicado: "enum canónico + Literal etapa_ley906 + evidencia_etapa"
porque: "fuente sagrada de etapas = playbook KB"
evals_a_ampliar: ["route-ruta-906"]
```

```yaml
id: A-ruta-002
severidad: P1
bloque: skills+guardrails
archivo: O2 skills; config/guardrails/agents/analista_ruta_procesal/output.md
experto: L1+L3+T3
veredicto: PASS (patched)
evidencia_repo: "0 Fuentes KB; domain_limits vacío; términos sin días hábiles explícitos (H-202/H-204/H-303)"
evidencia_kb: "proceso-penal-906.md §Términos"
impacto: "falsa certeza de plazos / ruta sin ancla"
fix_aplicado: "Fuentes KB O2 + guardrails grounding + steps fecha_base/días hábiles"
porque: "ética L3 + procedural knowledge"
evals_a_ampliar: []
```

```yaml
id: A-ruta-003
severidad: P1
bloque: evals
archivo: config/evals/agent_eval_cases.json
experto: T5
veredicto: PASS (patched)
evidencia_repo: "ningún case expected_destination=analista_ruta_procesal (H-203)"
evidencia_kb: "proceso-penal-906.md"
impacto: "regresión routing silenciosa"
fix_aplicado: "case route-ruta-906; version 3.2"
porque: "cobertura asimétrica vs tipicidad"
evals_a_ampliar: []
```

---

## A1 — Scorecard `analista_cronologia_hechos`

| Campo | Valor |
|---|---|
| Fecha | 2026-08-05 |
| Oleada | A1 |
| Expertos | L1, L2, L3, T1–T7, E0 |
| Primario | `construir_cronologia_penal` |
| Secundarios anclados | extraer_hechos, contradicciones, clasificar_fuente |
| Skills owned / O3 | 9 (cronología + hechos) |
| Veredicto global | **PARTIAL → PASS tras patches** |

### Técnica (0–5)

| Eje | Score | Nota 1 línea |
|---|---|---|
| Prompt | 5 | v5: clasificación fáctica, tools reales, no tipicidad |
| Few-shots / anti-drift | 4 | Anti-invención de hora; few-shots OK |
| Ancla skills | 5 | + `clasificar_fuente_factual` (antes vacíos) |
| Tools honesty | 5 | Prompt alineado a REAL_FUNCTION_TOOL_NAMES |
| Guardrails I/O/T | 5 | groundedness + no tipicidad/no inventar fechas |
| Schema | 4 | CronologiaPenal + fuentes_kb; clasificación en Evento |
| HITL | 4 | Cronología para memorial/audiencia → revisión abogado (skill) |
| Evals | 5 | `route-cronologia` + `tool-surface-cronologia` + budget |
| Config parity | 4 | Prompt/guardrails/skills versionados |

### Jurídico-procedural (0–5)

| Eje | Score | Nota 1 línea |
|---|---|---|
| Grounding KB | 4 | Fuentes KB en O3; hechos viven en expediente |
| Etapa 906 | 3 | Solo si evento=actuación; remite playbook |
| Tipicidad/dogmática | 5 | Explicitamente fuera (límite correcto) |
| Derechos víctima | 4 | No revictimizar al ordenar relatos (L2) |
| Hecho vs inferencia | 5 | Enum clasificación en schema+skills |
| Términos/oportunidad | 2 | Fuera de dominio |
| Citas | 4 | No cita normas; pendiente si actuación |
| HITL accionable | 4 | Uso externo requiere abogado |
| Alcance | 5 | Solo hechos/cronología penal-víctimas |
| Litigabilidad | 5 | Línea de tiempo accionable para despacho |

### Análisis panel (síntesis)

- **L1:** Separación confirmado/narrado/inferido es el núcleo litigable; O3 ya tenía estructura; faltaba ancla Fuentes KB y refuerzo anti-invención de fechas.
- **L2:** Skill primario ya ordena no implicar incredibilidad/culpa de la víctima; guardrail output ahora lo reitera.
- **L3:** Cronología no es high-risk, pero skill exige HITL antes de memorial/audiencia — correcto.
- **T1:** Prompt slim post-F3 estándar; añadido `fuentes_kb` y tools honestas (antes mezclaba lecturas KB sin listar REAL tools claras).
- **T2:** Ownership O3 coherente; secundario `detectar_vacios` sustituido por `clasificar_fuente_factual` (mejor ancla al paso 2 del prompt).
- **T3:** I/O ahora exige fuente o `pendiente_verificar`.
- **T4:** No fuga de pieza accionable desde cronología.
- **T5:** Cobertura eval ya existía; no faltaba case routing.
- **T6:** `notas_especialista` + `notas_trabajo` en schema OK; Drive notepad diferido.
- **T7:** PII minimizada en guardrails; ejemplos sintéticos.

### Hallazgos A1

```yaml
id: A-crono-001
severidad: P1
bloque: skills
archivo: agente/skills/{O3}/*/SKILL.md
experto: L1+T2
veredicto: PASS (patched)
evidencia_repo: "0/9 O3 con Fuentes KB al inicio A1"
evidencia_kb: "proceso-penal-906.md (actuaciones); normas-clave.md (no revictimización)"
impacto: "cronología sin contrato explícito de grounding / anti-tipicidad en skill MD"
fix_aplicado: "Fuentes KB + step 0 separación fáctica en 9 skills O3"
porque: "F-05 convención Fuentes KB; prioridad procedural"
evals_a_ampliar: []
```

```yaml
id: A-crono-002
severidad: P1
bloque: prompt+schema+guardrails
archivo: analista_cronologia_hechos.md; schemas.CronologiaPenal; guardrails output
experto: T1+T3
veredicto: PASS (patched)
evidencia_repo: "prompt no listaba fuentes_kb; guardrail domain_limits genérico; schema sin fuentes_kb"
evidencia_kb: "N/A (contrato fáctico)"
impacto: "drift prompt↔schema; invención de fechas menos enforceable"
fix_aplicado: "prompt v5 + fuentes_kb schema/renderer + groundedness_policy"
porque: "alineación tipicidad/ruta post-F3 como estándar"
evals_a_ampliar: ["completeness eventos.clasificacion (P2)"]
```

```yaml
id: A-crono-003
severidad: P2
bloque: catalog
archivo: src/agents/skill_catalog.py
experto: T2
veredicto: PASS (patched)
evidencia_repo: "secundarios incluían vacíos pero prompt enfatiza clasificación de fuente"
evidencia_kb: "N/A"
impacto: "ancla subóptima vs misión"
fix_aplicado: "secundario clasificar_fuente_factual (vacíos siguen owned)"
porque: "mejor match pasos 1–2 del prompt"
evals_a_ampliar: []
```

---

## A2 — Scorecard `analista_evidencia`

| Campo | Valor |
|---|---|
| Fecha | 2026-08-05 |
| Oleada | A2 |
| Expertos | L1, L2, L3, T1–T7, E0 |
| Primario | `inventariar_evidencia` |
| Secundarios anclados | clasificar_tipo_prueba, construir_matriz_hecho_prueba, detectar_brechas_probatorias |
| Skills owned / O4 core | 8 (+ shared: extraer_hechos, preguntas_aclaracion, mapear_tipo) |
| Veredicto global | **PARTIAL → PASS tras patches** |

### Técnica (0–5)

| Eje | Score | Nota 1 línea |
|---|---|---|
| Prompt | 5 | v7: pasos clasificar/matriz/brechas, tools reales, fuentes_kb |
| Few-shots / anti-drift | 4 | Few-shots integridad + no tipicidad |
| Ancla skills | 5 | + `clasificar_tipo_prueba` (antes recaudo en ancla) |
| Tools honesty | 5 | REAL_FUNCTION_TOOL_NAMES listadas; Planned en skills |
| Guardrails I/O/T | 5 | groundedness + integridad + no revictimizar |
| Schema | 5 | InventarioEvidencia + tipo Literal + fuentes_kb |
| HITL | 4 | Inventario no es high-risk; oficios/recaudo → abogado (skills) |
| Evals | 5 | `route-evidencia` + `tool-surface-evidencia` + budget |
| Config parity | 4 | Prompt/guardrails/skills versionados |

### Jurídico-procedural (0–5)

| Eje | Score | Nota 1 línea |
|---|---|---|
| Grounding KB | 5 | Fuentes KB O4 + checklist 906/normas |
| Etapa 906 | 4 | Checklist descubrimiento/juicio; sin arts inventados |
| Tipicidad/dogmática | 5 | Explicitamente fuera (límite correcto) |
| Derechos víctima | 4 | No culpar por falta de prueba (L2) |
| Hecho vs inferencia | 4 | Matriz: ausente ≠ hecho probado |
| Términos/oportunidad | 3 | Remite fecha_base; no certifica plazos |
| Citas | 4 | No siembra arts; pendiente si cita CPP |
| HITL accionable | 5 | Recaudo/oficios/pericias requieren abogado |
| Alcance | 5 | Solo evidencia penal-víctimas |
| Litigabilidad | 5 | Inventario + brechas + plan usable por despacho |

### Análisis panel (síntesis)

- **L1:** Cadena inventario→clasificación→matriz→brechas/recaudo es litigable; KB tenía hueco de checklist evidencia — cerrado sin inventar artículos.
- **L2:** Suficiencia/brechas ya pedían no culpar a la víctima; guardrail output lo refuerza.
- **L3:** Agente fuera de `HITL_OUTPUT_AGENTS` es correcto (salida analítica); skills marcan HITL antes de oficios/memorial — OK.
- **T1:** Prompt v6 mezclaba “KB” vago; v7 alinea tools + `fuentes_kb` como tipicidad/cronología.
- **T2:** Secundario `crear_plan_recaudo` sustituido por `clasificar_tipo_prueba` (mejor match paso 2); recaudo/custodia/preservar siguen owned.
- **T3:** I/O ahora exige fuente/ubicación o pendiente; domain_limits anti-admisibilidad.
- **T4:** No fuga de pieza radicable desde evidencia.
- **T5:** Cobertura eval ya existía; no faltaba case routing.
- **T6:** `notas_trabajo` en schema OK; Drive notepad diferido.
- **T7:** PII/minimización en guardrails; integridad digital enfatizada.

### Hallazgos A2

```yaml
id: A-evid-001
severidad: P1
bloque: skills
archivo: agente/skills/{O4 core}/*/SKILL.md
experto: L1+T2
veredicto: PASS (patched)
evidencia_repo: "0/8 O4 core con Fuentes KB al inicio A2"
evidencia_kb: "proceso-penal-906.md (checklist evidencia); normas-clave.md (integridad)"
impacto: "evidencia sin contrato explícito de grounding / anti-admisibilidad inventada"
fix_aplicado: "Fuentes KB en 8 skills O4 + bump version/checksum + sync .cursor"
porque: "F-05 convención Fuentes KB; prioridad procedural"
evals_a_ampliar: []
```

```yaml
id: A-evid-002
severidad: P1
bloque: prompt+schema+guardrails
archivo: analista_evidencia.md; schemas.InventarioEvidencia; guardrails output
experto: T1+T3
veredicto: PASS (patched)
evidencia_repo: "prompt sin fuentes_kb; tipo free-string; groundedness_policy ausente"
evidencia_kb: "proceso-penal-906.md checklist evidencia"
impacto: "drift prompt↔schema; invención de custodia/hashes menos enforceable"
fix_aplicado: "prompt v7 + fuentes_kb + tipo Literal + groundedness_policy + domain_limits"
porque: "alineación tipicidad/ruta/cronología post-F3 como estándar"
evals_a_ampliar: ["completeness items.fuente_o_ubicacion (P2)"]
```

```yaml
id: A-evid-003
severidad: P2
bloque: catalog
archivo: src/agents/skill_catalog.py
experto: T2
veredicto: PASS (patched)
evidencia_repo: "secundarios: brechas/matriz/recaudo; prompt paso 2 enfatiza clasificar tipo"
evidencia_kb: "N/A"
impacto: "ancla subóptima vs misión de clasificación"
fix_aplicado: "secundario clasificar_tipo_prueba (recaudo sigue owned)"
porque: "mejor match pasos 1–2 del prompt"
evals_a_ampliar: []
```

```yaml
id: A-evid-004
severidad: P1
bloque: kb
archivo: agente/conocimiento/proceso-penal-906.md; normas-clave.md
experto: L1
veredicto: PASS (patched)
evidencia_repo: "KB sin checklist evidencia/integridad antes de A2"
evidencia_kb: "playbook etapas 6–7 + checklist O4 (sin arts inventados)"
impacto: "skills O4 sin ancla procedural concreta en conocimiento/"
fix_aplicado: "checklist evidencia/prueba + checklist integridad normas-clave"
porque: "F-15 KB enrichment; no inventar numerales CPP"
evals_a_ampliar: []
```

```yaml
id: A-evid-005
severidad: P2
bloque: ownership
archivo: alinear_estrategia_prueba_proceso; generar_preguntas_testigos_peritos
experto: T2
veredicto: PASS (documentado)
evidencia_repo: "O4 plan lista alinear/preguntas_testigos; Used By = víctimas/audiencias"
evidencia_kb: "N/A"
impacto: "oleada O4 no implica ownership exclusivo evidencia"
fix_aplicado: "sin MOVE; evidencia consume matriz/recaudo; alinear queda en víctimas/calidad"
porque: "evitar solape ownership; A3/A4 revisan esos skills"
evals_a_ampliar: []
```

---

## A3 — Scorecard `analista_representacion_victimas`

| Campo | Valor |
|---|---|
| Fecha | 2026-08-05 |
| Oleada | A3 |
| Expertos | L1, L2, L3, T1–T7, E0 |
| Primario | `construir_teoria_caso_victima` |
| Secundarios anclados | analizar_derechos_victima, detectar_riesgo_revictimizacion, priorizar_objetivos_representacion |
| Skills owned / O5 core | 10 (+ shared: mapear_actuaciones, analizar_intervencion vía ruta/audiencias) |
| Veredicto global | **PARTIAL → PASS tras patches** |

### Técnica (0–5)

| Eje | Score | Nota 1 línea |
|---|---|---|
| Prompt | 5 | v6: pasos con skills, tools reales, `fuentes_kb`, schema explícito |
| Few-shots / anti-drift | 4 | Menor/sexual + fallo culpabilizante |
| Ancla skills | 5 | + `priorizar_objetivos` (antes solo 2 secundarios) |
| Tools honesty | 5 | REAL tools; Planned checkers no invocables |
| Guardrails I/O/T | 5 | groundedness + no_revictimizar + HITL teoría→cliente |
| Schema | 5 | RepresentacionVictimas + `fuentes_kb` |
| HITL | 4 | Fuera HITL_OUTPUT (analítico OK); skills marcan HITL comunicación/cliente |
| Evals | 5 | route + tool-surface + instruction-budget |
| Config parity | 4 | Prompt/guardrails/skills versionados |

### Jurídico-procedural (0–5)

| Eje | Score | Nota 1 línea |
|---|---|---|
| Grounding KB | 5 | Checklist O5 en normas-clave + 906 |
| Etapa 906 | 4 | Remite etapa/actuaciones; sin arts inventados |
| Tipicidad/dogmática | 5 | Fuera de alcance (límite correcto) |
| Derechos víctima | 5 | Intereses≠derechos; no revictimizar; diferencial |
| Hecho vs inferencia | 4 | Teoría preliminar; daño no es peritaje |
| Términos/oportunidad | 3 | Remite fecha_base vía 906; no certifica plazos |
| Citas | 4 | Quitó Ley 1712 inventada en skill derechos |
| HITL accionable | 5 | Teoría/objetivos → abogado; no “lista para cliente” |
| Alcance | 5 | Solo representación penal-víctimas |
| Litigabilidad | 5 | Teoría + derechos + riesgos + objetivos usable |

### Análisis panel (síntesis)

- **L1:** Cadena intereses/derechos→teoría→daño/diferencial/riesgo→objetivos es litigable; KB tenía hueco checklist O5 — cerrado.
- **L2:** Few-shots y skills ya protegían no culpabilizar; guardrail output + groundedness lo refuerzan; minimizar relato gráfico.
- **L3:** Agente fuera de `HITL_OUTPUT_AGENTS` correcto; skills etiquetan HITL antes de comunicar teoría al cliente — OK.
- **T1:** Prompt v5 genérico; v6 alinea skills nombrados + schema como evidencia/tipicidad.
- **T2:** Secundario `priorizar_objetivos` añadido (paso 4); `analizar_intervencion` sigue owned por ruta/audiencias (O5 consume).
- **T3:** I/O groundedness + domain_limits anti-promesa / anti-estigma.
- **T4:** No fuga de pieza radicable desde víctimas.
- **T5:** Hueco eval cerrado (route/tool-surface/budget).
- **T6:** `notas_trabajo` OK; Drive diferido.
- **T7:** PII/minimización gráfica en guardrails.

### Hallazgos A3

```yaml
id: A-vict-001
severidad: P1
bloque: skills
archivo: agente/skills/{O5 core}/*/SKILL.md
experto: L1+T2
veredicto: PASS (patched)
evidencia_repo: "9/10 O5 sin Fuentes KB al inicio A3 (mapear sí tenía)"
evidencia_kb: "normas-clave.md checklist O5; proceso-penal-906.md checklist intervención"
impacto: "representación sin contrato explícito de grounding / anti-invención de facultades"
fix_aplicado: "Fuentes KB en 11 skills O5/shared + bump version/checksum + sync .cursor"
porque: "F-05 convención Fuentes KB; prioridad procedural"
evals_a_ampliar: []
```

```yaml
id: A-vict-002
severidad: P1
bloque: prompt+schema+guardrails
archivo: analista_representacion_victimas.md; schemas.RepresentacionVictimas; guardrails output
experto: T1+T3
veredicto: PASS (patched)
evidencia_repo: "prompt v5 sin fuentes_kb/tools; schema sin fuentes_kb; groundedness_policy ausente"
evidencia_kb: "normas-clave.md derechos + checklist O5"
impacto: "drift prompt↔schema; invención de vulneraciones/diagnósticos menos enforceable"
fix_aplicado: "prompt v6 + fuentes_kb + groundedness_policy + domain_limits"
porque: "alineación tipicidad/ruta/cronología/evidencia post-F3 como estándar"
evals_a_ampliar: ["completeness intereses documentados (P2)"]
```

```yaml
id: A-vict-003
severidad: P1
bloque: evals
archivo: config/evals/agent_eval_cases.json
experto: T5
veredicto: PASS (patched)
evidencia_repo: "0 evals hacia analista_representacion_victimas (FAIL F1)"
evidencia_kb: "N/A"
impacto: "regresión de routing/superficie víctimas invisible en CI"
fix_aplicado: "route-victimas + tool-surface-victimas + instruction-budget-victimas (evals v3.3)"
porque: "plan A3 hueco eval; F-07/F-12"
evals_a_ampliar: []
```

```yaml
id: A-vict-004
severidad: P1
bloque: kb
archivo: agente/conocimiento/normas-clave.md; proceso-penal-906.md
experto: L1+L2
veredicto: PASS (patched)
evidencia_repo: "KB sin checklist representación/intervención O5"
evidencia_kb: "checklist O5 (intereses≠derechos, no peritaje, diferencial documentado)"
impacto: "skills O5 sin ancla procedural concreta"
fix_aplicado: "checklist representación + checklist intervención víctima"
porque: "F-15 KB enrichment; no inventar arts CPP"
evals_a_ampliar: []
```

```yaml
id: A-vict-005
severidad: P2
bloque: catalog
archivo: src/agents/skill_catalog.py
experto: T2
veredicto: PASS (patched)
evidencia_repo: "solo 2 secundarios; prompt paso 4 prioriza objetivos"
evidencia_kb: "N/A"
impacto: "ancla incompleta vs misión"
fix_aplicado: "secundario priorizar_objetivos_representacion"
porque: "mejor match pasos 1–4 del prompt (techo 3)"
evals_a_ampliar: []
```

```yaml
id: A-vict-006
severidad: P2
bloque: ownership
archivo: analizar_intervencion_victima
experto: T2
veredicto: PASS (documentado)
evidencia_repo: "O5 lista intervención; Used By = ruta/audiencias"
evidencia_kb: "N/A"
impacto: "oleada O5 no implica ownership exclusivo víctimas"
fix_aplicado: "Fuentes KB sin MOVE; víctimas consume derechos/teoría; intervención queda ruta/A4 → cerrado A-aud-006"
porque: "evitar solape ownership"
evals_a_ampliar: []
```

---

## A4 — Scorecard `analista_audiencias`

| Campo | Valor |
|---|---|
| Fecha | 2026-08-05 |
| Oleada | A4 |
| Expertos | L1, L2, L3, T1–T7, E0 |
| Primario | `preparar_preguntas_audiencia` |
| Secundarios anclados | identificar_objetivo_audiencia, preparar_guion_intervencion_oral, detectar_riesgos_audiencia |
| Skills owned / O6 core | 9 O6 + shared (intervención, resumen litigante, preguntas testigos/peritos) |
| Veredicto global | **PARTIAL → PASS tras patches** |

### Técnica (0–5)

| Eje | Score | Nota 1 línea |
|---|---|---|
| Prompt | 5 | v5: pasos con skills, tools reales, `fuentes_kb`, schema explícito |
| Few-shots / anti-drift | 5 | Imputación/medidas + fallo revictimizante menor |
| Ancla skills | 5 | + `detectar_riesgos_audiencia` (antes 2 secundarios) |
| Tools honesty | 5 | REAL tools; Planned checkers no invocables |
| Guardrails I/O/T | 5 | groundedness + no_revictimizar + HITL estrados |
| Schema | 5 | PreparacionAudiencia + `fuentes_kb` |
| HITL | 5 | En `HITL_OUTPUT_AGENTS` — correcto para oralidad |
| Evals | 5 | route + tool-surface + instruction-budget |
| Config parity | 4 | Prompt/guardrails/skills versionados |

### Jurídico-procedural (0–5)

| Eje | Score | Nota 1 línea |
|---|---|---|
| Grounding KB | 5 | Checklist O6 en 906 + normas-clave |
| Etapa 906 | 5 | Tipo audiencia / garantías vs conocimiento sin arts inventados |
| Tipicidad/dogmática | 5 | Fuera de alcance (límite correcto) |
| Derechos víctima | 5 | Intervención vía marco ruta+audiencias; no revictimizar |
| Hecho vs inferencia | 5 | Guion/hipótesis tácticas ≠ hechos probados |
| Términos/oportunidad | 4 | Sin fecha fundante → pendiente; no certifica plazos |
| Citas | 4 | Remite playbook; no siembra arts CPP |
| HITL accionable | 5 | Preparación interna; ensayo abogado antes de estrados |
| Alcance | 5 | Solo prep. oral; no memorial |
| Litigabilidad | 5 | Objetivo+guion+preguntas+riesgos+checklist usable |

### Análisis panel (síntesis)

- **L1:** Cadena objetivo→guion/solicitudes/preguntas→riesgos→checklist litigable; KB tenía hueco O6 — cerrado.
- **L2:** Few-shots y skills protegen no-revictimizar; groundedness refuerza ancla expediente/KB.
- **L3:** Agente en `HITL_OUTPUT_AGENTS` correcto (oralidad accionable); no sustituye estrados.
- **T1:** Prompt v4 genérico; v5 alinea skills nombrados + schema como evidencia/víctimas.
- **T2:** Secundario `detectar_riesgos` añadido; `analizar_intervencion` permanece ruta+audiencias (cierra A-vict-006).
- **T3:** I/O groundedness + domain_limits anti-fecha inventada / anti-oralidad sustituta.
- **T4:** No fuga a memorial; redactor excluido en tool-surface eval.
- **T5:** route ya existía; añadidos tool-surface + budget.
- **T6:** `notas_trabajo` OK; Drive diferido.
- **T7:** PII/minimización gráfica en preguntas/guion.

### Hallazgos A4

```yaml
id: A-aud-001
severidad: P1
bloque: skills
archivo: agente/skills/{O6 core + shared}/*/SKILL.md
experto: L1+T2
veredicto: PASS (patched)
evidencia_repo: "11/11 O6/shared sin Fuentes KB al inicio A4 (intervención ya tenía desde A3)"
evidencia_kb: "proceso-penal-906.md checklist O6; normas-clave.md checklist prep. audiencia"
impacto: "preparación oral sin contrato explícito de grounding / anti-invención de fechas/facultades"
fix_aplicado: "Fuentes KB en 11 skills + bump version/checksum + sync .cursor"
porque: "F-05 convención Fuentes KB; prioridad procedural"
evals_a_ampliar: []
```

```yaml
id: A-aud-002
severidad: P1
bloque: prompt+schema+guardrails
archivo: analista_audiencias.md; schemas.PreparacionAudiencia; guardrails output
experto: T1+T3
veredicto: PASS (patched)
evidencia_repo: "prompt v4 sin fuentes_kb/tools nombrados; schema sin fuentes_kb; groundedness_policy ausente"
evidencia_kb: "proceso-penal-906.md checklist O6"
impacto: "drift prompt↔schema; invención de fechas/facultades menos enforceable"
fix_aplicado: "prompt v5 + fuentes_kb + groundedness_policy + domain_limits"
porque: "alineación tipicidad/ruta/cronología/evidencia/víctimas post-F3 como estándar"
evals_a_ampliar: ["completeness tipo audiencia documentado (P2)"]
```

```yaml
id: A-aud-003
severidad: P1
bloque: evals
archivo: config/evals/agent_eval_cases.json
experto: T5
veredicto: PASS (patched)
evidencia_repo: "solo route-audiencia; sin tool-surface/budget (hueco parcial F1)"
evidencia_kb: "N/A"
impacto: "regresión de superficie/tokens audiencias invisible en CI"
fix_aplicado: "tool-surface-audiencias + instruction-budget-audiencias (evals v3.4)"
porque: "plan A4 oralidad/HITL; F-07/F-12"
evals_a_ampliar: []
```

```yaml
id: A-aud-004
severidad: P1
bloque: kb
archivo: agente/conocimiento/proceso-penal-906.md; normas-clave.md
experto: L1+L2
veredicto: PASS (patched)
evidencia_repo: "KB sin checklist preparación audiencia O6"
evidencia_kb: "checklist O6 (objetivo→guion→riesgos→HITL; no inventar fechas)"
impacto: "skills O6 sin ancla procedural concreta"
fix_aplicado: "checklist preparación audiencias en 906 + normas-clave"
porque: "F-15 KB enrichment; no inventar arts CPP"
evals_a_ampliar: []
```

```yaml
id: A-aud-005
severidad: P2
bloque: catalog
archivo: src/agents/skill_catalog.py
experto: T2
veredicto: PASS (patched)
evidencia_repo: "solo 2 secundarios; prompt paso 3 anticipa riesgos"
evidencia_kb: "N/A"
impacto: "ancla incompleta vs misión"
fix_aplicado: "secundario detectar_riesgos_audiencia"
porque: "mejor match pasos 1–3 del prompt (techo 3)"
evals_a_ampliar: []
```

```yaml
id: A-aud-006
severidad: P2
bloque: ownership
archivo: analizar_intervencion_victima
experto: T2
veredicto: PASS (documentado — cierra A-vict-006)
evidencia_repo: "Used By = analista_ruta_procesal + analista_audiencias; O5 lista consumo; no víctimas"
evidencia_kb: "checklist O6 paso 3 marco intervención"
impacto: "clarifica dueño: marco procesal (ruta) + consumo táctico oral (audiencias)"
fix_aplicado: "sin MOVE; prompt audiencias nombra skill; víctimas no owner"
porque: "evitar solape ownership; grounded en skill_catalog/Used By"
evals_a_ampliar: []
```

---

## A5 — Scorecard `redactor_documentos_juridicos`

| Campo | Valor |
|---|---|
| Fecha | 2026-08-05 |
| Oleada | A5 |
| Expertos | L1, L2, L3, T1–T7, E0 |
| Primario | `redactar_memorial_penal` |
| Secundarios anclados | estructurar_hechos_fundamentos_solicitudes, marcar_pendientes_verificacion, controlar_tono_juridico_documento |
| Skills owned / O7 redacción | 5 `redactar_*` + estructurar + marcar_pendientes + tono_juridico (+ evaluar_derecho_peticion shared) |
| Veredicto global | **PARTIAL → PASS tras patches** |

### Técnica (0–5)

| Eje | Score | Nota 1 línea |
|---|---|---|
| Prompt | 5 | v5: pasos con skills, tools reales, `fuentes_kb`, HITL HIGH RISK |
| Few-shots / anti-drift | 5 | Impulso + fallo divorcio fuera de alcance |
| Ancla skills | 5 | Primario + 3 secundarios ya correctos; Used By marcar alineado |
| Tools honesty | 5 | REAL tools; Planned checkers no invocables |
| Guardrails I/O/T | 5 | groundedness + HITL + domain_limits anti-radicado inventado |
| Schema | 5 | BorradorDocumentoPenal + `fuentes_kb` |
| HITL | 5 | `HIGH_RISK_AGENTS` + plan_required memorial — reforzado en prompt/guardrail |
| Evals | 5 | route + completeness + budget + tool-surface |
| Config parity | 4 | Prompt/guardrails/skills versionados |

### Jurídico-procedural (0–5)

| Eje | Score | Nota 1 línea |
|---|---|---|
| Grounding KB | 5 | Checklist O7 en 906 + normas-clave |
| Etapa 906 | 5 | Ancla etapa; sin actuación → pendiente |
| Tipicidad/dogmática | 5 | Fuera de alcance (límite correcto) |
| Derechos víctima | 5 | Tono/no revictimizar; petición vía evaluar |
| Hecho vs inferencia | 5 | Estructura hechos→fundamentos→peticiones |
| Términos/oportunidad | 4 | Sin fecha_base → pendiente; no certifica plazos |
| Citas | 4 | Remite KB/pendiente; calidad profunda en A6 |
| HITL accionable | 5 | Borrador; no firmar/radicar sin abogado |
| Alcance | 5 | Solo penal-víctimas; no otras materias Lexiatek |
| Litigabilidad | 5 | Memorial/impulso/petición/ampliación usable |

### Análisis panel (síntesis)

- **L1:** Cadena estructurar→redactar_*→tono→pendientes litigable; KB tenía hueco O7 — cerrado.
- **L2:** Few-shots y skills protegen no-inventar radicados/normas; groundedness refuerza ancla.
- **L3:** Ya en HIGH_RISK/HITL_OUTPUT; refuerzo explícito en prompt/guardrail (no bypass chat).
- **T1:** Prompt v4 genérico; v5 alinea skills nombrados + schema como audiencias.
- **T2:** Secundarios OK; `marcar_pendientes` Used By ahora incluye redactor.
- **T3:** I/O groundedness + domain_limits anti-radicado / anti-firma.
- **T4:** tool-surface vecinos calidad+ruta; excluye audiencias.
- **T5:** route/completeness/budget existían; añadido tool-surface (evals v3.5).
- **T6:** `notas_trabajo` OK; Drive diferido.
- **T7:** PII/minimización gráfica en cuerpo.

### Hallazgos A5

```yaml
id: A-reda-001
severidad: P1
bloque: skills
archivo: agente/skills/{O7 redacción}/*/SKILL.md
experto: L1+T2
veredicto: PASS (patched)
evidencia_repo: "8/8 O7-redacción sin Fuentes KB al inicio A5 (recurso ya tenía; evaluar header corrupto parcial)"
evidencia_kb: "proceso-penal-906.md checklist O7; normas-clave.md checklist redacción"
impacto: "borradores sin contrato explícito de grounding / anti-invención de radicados"
fix_aplicado: "Fuentes KB en 8 skills + bump version/checksum + sync .cursor; header evaluar limpio"
porque: "F-05 convención Fuentes KB; prioridad procedural"
evals_a_ampliar: []
```

```yaml
id: A-reda-002
severidad: P1
bloque: prompt+schema+guardrails
archivo: redactor_documentos_juridicos.md; schemas.BorradorDocumentoPenal; guardrails output
experto: T1+T3
veredicto: PASS (patched)
evidencia_repo: "prompt v4 sin fuentes_kb/tools nombrados; schema sin fuentes_kb; groundedness_policy ausente"
evidencia_kb: "proceso-penal-906.md checklist O7"
impacto: "drift prompt↔schema; invención de radicados/normas menos enforceable"
fix_aplicado: "prompt v5 + fuentes_kb + groundedness_policy + domain_limits HITL"
porque: "alineación tipicidad/ruta/…/audiencias post-F3 como estándar"
evals_a_ampliar: ["enum tipo ampliación/petición explícito (P2)"]
```

```yaml
id: A-reda-003
severidad: P1
bloque: evals
archivo: config/evals/agent_eval_cases.json
experto: T5
veredicto: PASS (patched)
evidencia_repo: "route+completeness+budget; sin tool-surface-redactor"
evidencia_kb: "N/A"
impacto: "regresión de superficie/vecinos redactor invisible en CI"
fix_aplicado: "tool-surface-redactor (evals v3.5): vecinos calidad+ruta; chat excluye HIGH RISK redactor"
porque: "plan A5 high-risk HITL; F-07/F-12; chat-without-high-risk-tools"
evals_a_ampliar: []
```

```yaml
id: A-reda-004
severidad: P1
bloque: kb
archivo: agente/conocimiento/proceso-penal-906.md; normas-clave.md
experto: L1+L2
veredicto: PASS (patched)
evidencia_repo: "KB sin checklist redacción O7"
evidencia_kb: "checklist O7 (hechos→fundamentos→peticiones; HITL; no inventar radicados)"
impacto: "skills O7 sin ancla procedural concreta"
fix_aplicado: "checklist redacción en 906 + normas-clave"
porque: "F-15 KB enrichment; no inventar arts CPP"
evals_a_ampliar: []
```

```yaml
id: A-reda-005
severidad: P2
bloque: ownership
archivo: marcar_pendientes_verificacion
experto: T2
veredicto: PASS (patched)
evidencia_repo: "Used By solo coordinador_caso; secundario runtime del redactor"
evidencia_kb: "N/A"
impacto: "drift catalog Used By vs skill_catalog secundarios"
fix_aplicado: "Used By + Rol redactor; Fuentes KB"
porque: "honestidad de ownership; techo secundarios ya correcto"
evals_a_ampliar: []
```

```yaml
id: A-reda-006
severidad: P1
bloque: hitl
archivo: prompt + guardrails output + HIGH_RISK_AGENTS
experto: L3+T3
veredicto: PASS (patched — refuerzo)
evidencia_repo: "HITL wiring ya correcto; prompt/guardrail genéricos sobre borrador"
evidencia_kb: "checklist O7 paso 7 HITL"
impacto: "riesgo de tono 'listo para radicar' sin refuerzo contractual"
fix_aplicado: "prompt v5 + hitl_policy/domain_limits: no firmar/radicar; HIGH RISK explícito"
porque: "plan A5 high-risk drafts must go through HITL"
evals_a_ampliar: []
```

---

## A6 — Scorecard `analista_calidad_juridica`

| Campo | Valor |
|---|---|
| Fecha | 2026-08-05 |
| Oleada | A6 |
| Expertos | L1, L2, L3, T1–T7, E0 |
| Primario | `revisar_coherencia_estrategica` |
| Secundarios anclados | detectar_alucinaciones_legales, verificar_citas_normativas, clasificar_aprobacion_juridica |
| Skills owned / O7 calidad | coherencia + alucinaciones + citas + jurisprudencia + aprobación + confidencialidad + tono_reputacional (+ hechos_soportados shared) |
| Veredicto global | **PARTIAL → PASS tras patches** |

### Técnica (0–5)

| Eje | Score | Nota 1 línea |
|---|---|---|
| Prompt | 5 | v7: pasos con skills, tools reales, `fuentes_kb`, gate duro |
| Few-shots / anti-drift | 5 | Cita inventada + fallo confidencialidad (Ley 1581) |
| Ancla skills | 5 | Primario + 3 secundarios (citas en ancla A6) |
| Tools honesty | 5 | REAL tools; Planned checkers no invocables |
| Guardrails I/O/T | 5 | groundedness + no_invention + schema veredicto |
| Schema | 5 | DictamenCalidad + `fuentes_kb` |
| HITL | 5 | Gate duro plan_executor rechazado/escalar |
| Evals | 5 | route + budget + quality-gate + tool-surface |
| Config parity | 4 | Prompt/guardrails/skills versionados |

### Jurídico-procedural (0–5)

| Eje | Score | Nota 1 línea |
|---|---|---|
| Grounding KB | 5 | Checklist calidad O7 en 906 + normas-clave |
| Etapa 906 | 4 | Coherencia con etapa si aplica; no certifica plazos |
| Tipicidad/dogmática | 5 | Fuera de alcance (límite correcto) |
| Derechos víctima | 5 | No revictimización + confidencialidad en cadena |
| Hecho vs inferencia | 5 | verificar_hechos + pendientes |
| Términos/oportunidad | 4 | No certifica; remite pendientes |
| Citas | 5 | Citas/jurisprudencia/alucinaciones ancladas a KB |
| HITL accionable | 5 | Gate duro bloquea entrega accionable |
| Alcance | 5 | Solo dictamen; no reescribe memorial |
| Litigabilidad | 5 | Dictamen usable por gerente/abogado |

### Análisis panel (síntesis)

- **L1:** Cadena coherencia→alucinaciones/citas/jurisprudencia→aprobación litigable; KB tenía hueco O7 calidad — cerrado.
- **L2:** Confidencialidad/no-revictimización en pipeline; few-shot menor/salud.
- **L3:** Gate duro ya cableado; refuerzo contractual prompt/guardrail.
- **T1:** Prompt v6 genérico; v7 alinea skills nombrados + schema.
- **T2:** Secundarios: citas reemplaza confidencialidad en ancla (confidencialidad owned).
- **T3:** I/O groundedness + tools honesty anti-checkers inventados.
- **T4:** tool-surface vecinos cronología+ruta; excluye redactor/audiencias.
- **T5:** route/budget/quality-gate existían; añadido tool-surface-calidad (evals v3.6).
- **T6:** `notas_trabajo` OK; Drive diferido.
- **T7:** PII/1581 en skill confidencialidad + few-shot.

### Hallazgos A6

```yaml
id: A-cali-001
severidad: P1
bloque: skills
archivo: agente/skills/{O7 calidad}/*/SKILL.md
experto: L1+T2
veredicto: PASS (patched)
evidencia_repo: "7/7 O7-calidad sin Fuentes KB al inicio A6"
evidencia_kb: "proceso-penal-906.md checklist calidad; normas-clave.md checklist citas"
impacto: "dictámenes sin contrato explícito de grounding / anti-invención de citas"
fix_aplicado: "Fuentes KB en 7 skills + bump version/checksum + sync .cursor; clasificar: rechazado (no rechazar)"
porque: "F-05 convención Fuentes KB; prioridad citas/alucinación diferida de A5"
evals_a_ampliar: []
```

```yaml
id: A-cali-002
severidad: P1
bloque: prompt+schema+guardrails
archivo: analista_calidad_juridica.md; schemas.DictamenCalidad; guardrails output/tools
experto: T1+T3
veredicto: PASS (patched)
evidencia_repo: "prompt v6 sin skills nombrados/fuentes_kb; schema sin fuentes_kb; few-shot truncado; groundedness ausente"
evidencia_kb: "proceso-penal-906.md checklist calidad"
impacto: "drift prompt↔schema; invención de citas menos enforceable"
fix_aplicado: "prompt v7 + fuentes_kb + groundedness_policy + tools allowlist honestas + few-shot 1581"
porque: "alineación tipicidad/…/redactor post-F3 como estándar"
evals_a_ampliar: []
```

```yaml
id: A-cali-003
severidad: P1
bloque: ownership
archivo: src/agents/skill_catalog.py _SECONDARY_SKILLS
experto: T2
veredicto: PASS (patched)
evidencia_repo: "secundarios sin verificar_citas_normativas (misión A6)"
evidencia_kb: "N/A"
impacto: "ancla runtime no priorizaba verificación de citas"
fix_aplicado: "secundarios: alucinaciones + verificar_citas + clasificar_aprobacion"
porque: "A6 foco citas/alucinación; confidencialidad sigue owned"
evals_a_ampliar: []
```

```yaml
id: A-cali-004
severidad: P1
bloque: kb
archivo: agente/conocimiento/proceso-penal-906.md; normas-clave.md
experto: L1+L2
veredicto: PASS (patched)
evidencia_repo: "KB sin checklist control calidad / citas O7"
evidencia_kb: "checklist calidad (cadena + gate duro + no inventar sentencias)"
impacto: "skills O7 calidad sin ancla procedural concreta"
fix_aplicado: "checklist calidad en 906 + normas-clave"
porque: "F-15 KB enrichment; no inventar arts/sentencias"
evals_a_ampliar: []
```

```yaml
id: A-cali-005
severidad: P1
bloque: evals
archivo: config/evals/agent_eval_cases.json
experto: T5
veredicto: PASS (patched)
evidencia_repo: "route+budget+quality-gate; sin tool-surface-calidad"
evidencia_kb: "N/A"
impacto: "regresión de superficie/vecinos calidad invisible en CI"
fix_aplicado: "tool-surface-calidad (evals v3.6): vecinos cronología+ruta; chat excluye redactor/audiencias"
porque: "plan A6; F-07/F-12"
evals_a_ampliar: []
```

```yaml
id: A-cali-006
severidad: P2
bloque: hitl
archivo: plan_executor + calidad_output_guardrail
experto: L3+T4
veredicto: PASS (ya cableado; refuerzo documental)
evidencia_repo: "gate duro rechazado/escalar ya en plan_executor; tests quality_gate verdes"
evidencia_kb: "checklist calidad paso 5 gate duro"
impacto: "riesgo de tono 'aprobable' sin hallazgos — mitigado por silent_approval_policy"
fix_aplicado: "refuerzo prompt/guardrail; sin cambio runtime gate"
porque: "gate ya correcto; A6 refuerza contrato"
evals_a_ampliar: []
```

---

## Cola E0 (post A0–A8 + X)

| # | ID | Acción | Sev | Estado |
|---|---|---|---|---|
| 1 | A-tipi-* | Patches tipicidad residuales | P0/P1 | **Hecho** |
| 2 | A-ruta-* | Patches ruta + eval | P0/P1 | **Hecho** |
| 3 | A-crono-* | Patches cronología O3 | P1 | **Hecho** |
| 4 | A-evid-* | Patches evidencia O4 | P1 | **Hecho** |
| 5 | A-vict-* | Patches víctimas O5 + eval | P1 | **Hecho** |
| 6 | A-aud-* | Patches audiencias O6 + eval | P1 | **Hecho** |
| 7 | A-reda-* | Patches redactor O7 + eval | P1 | **Hecho** |
| 8 | A-cali-* | Patches calidad O7 + eval | P1 | **Hecho** |
| 9 | A-segu-* | Patches seguimiento O8 + eval | P1 | **Hecho** |
| 10 | A-coord-* | Patches coordinador O8 gerencia + eval | P1 | **Hecho** |
| 11 | A-xcut-* | **X** hallazgos cruzados + Top 15 + quick wins | P0/P1 | **Hecho** |
| 12 | — | PR `#9` rama `cursor/analisis-a0-a1-prompts-skills` | P1 | **Abierto** |
| 13 | — | F5 notepads / F4 auth portal | P2/P1 | **Diferido** (documentado) |

### Evals gap (post X)

- **Hecho A7/A8:** surfaces + budgets seguimiento/coordinador
- **Hecho X:** `tool-surface-ruta`, `instruction-budget-tipicidad`, `instruction-budget-ruta` (evals v3.9)
- **Pendiente P2:** groundedness por campos schema (`fuentes_kb` en runtime LLM); ampliar secundarios runtime (>3) si tokens lo permiten

## Notas panel (personas) — post A0–A8 + X

- **L1:** Checklists O1–O8 en KB; 81/81 Fuentes KB; sin arts/radicados inventados.
- **T2:** Secundarios 2–3 por agente = techo token consciente; owned-sin-ancla = backlog P2 no conflicto de ownership.
- **T5:** Suite evals v3.9; F-06 CI Fuentes KB + anti-`art. N`.
- **L3:** HITL redactor/audiencias/seguimiento cableado; POC una voz.

> Deep-dives A0–A8 + oleada X cerrados en esta rama. PR abierto para revisión.

**Siguiente:** merge tras CI verde + revisión humana; F4/F5 fuera de este track.

---

## Oleada X — hallazgos cruzados (2026-08-05)

### Matriz cruzada (síntesis)

| Tema | Hallazgo | Severidad | Acción X |
|---|---|---|---|
| Duplicación / ownership | Skills owned sin ancla `_SECONDARY` (máx 3) en casi todos los agentes | P2 | **Aceptado** — techo tokens; documentado en matriz F1 |
| Ownership POC vs MOVE | `POC_OWNED_SKILLS` + `_MOVED_SKILL_OWNERS` coherentes post-A8 | PASS | Ninguna |
| Fuentes KB | 80/81 → residual `controlar_separacion_hecho_inferencia` | P0 | **Patched** (A-xcut-001) |
| Evals F-07/F-12 | Tipicidad sin budget; ruta sin tool-surface dedicado | P1 | **Patched** (evals v3.9) |
| CI F-06 | No había lint Fuentes KB / art. N en skills+prompts | P0 | **Patched** (`test_prompt_skill_quality`) |
| HITL | Redactor/audiencias/seguimiento en `HITL_OUTPUT_AGENTS`; memorial vía plan | PASS | Ninguna |
| Tools honesty | Skills ≠ function_tools; allowlist `REAL_FUNCTION_TOOL_NAMES` | PASS | Mantener F-11 |
| Notepads F5 / Drive | Dual DB+Drive diferido | P2 | **Documentado** — no impl |
| Auth portal F4 | Panel 12 servicio **NO LISTO** | P1 (servicio) | **Documentado** — track aparte |
| Legacy prose | IDs/roles legacy residuales en skills O1/O2 | P2 | Lint `test_no_legacy_rol` ya existe; prosa OK |

### Hallazgos A-xcut

```yaml
id: A-xcut-001
severidad: P0
bloque: skills
archivo: agente/skills/controlar_separacion_hecho_inferencia/SKILL.md
experto: L1+T2
veredicto: PASS (patched)
evidencia_repo: "único skill 81 sin ## Fuentes KB post A0–A8"
evidencia_kb: "proceso-penal-906.md + normas-clave.md (hecho vs inferencia)"
impacto: "brecha F-05 residual en skill transversal calidad/redactor"
fix_aplicado: "Fuentes KB + bump v3 + sync .cursor"
porque: "cerrar cobertura 81/81 antes de merge"
evals_a_ampliar: []
```

```yaml
id: A-xcut-002
severidad: P0
bloque: ci
archivo: tests/test_prompt_skill_quality.py
experto: T5+T3
veredicto: PASS (patched)
evidencia_repo: "F-06 planificado; solo planes tenían anti-art en test_fase3"
evidencia_kb: "H-304 patrón"
impacto: "regresión de siembra art. N o skills sin Fuentes KB invisible en CI"
fix_aplicado: "test_all_skills_have_fuentes_kb + test_skills_and_agent_prompts_do_not_seed_bare_article_numbers"
porque: "F-06 P0 del plan análisis"
evals_a_ampliar: []
```

```yaml
id: A-xcut-003
severidad: P1
bloque: evals
archivo: config/evals/agent_eval_cases.json
experto: T5
veredicto: PASS (patched)
evidencia_repo: "tipicidad sin instruction-budget; ruta sin tool-surface propio"
evidencia_kb: "N/A"
impacto: "hueco F-07/F-12 en dos agentes canónicos A0"
fix_aplicado: "tool-surface-ruta + instruction-budget-tipicidad/ruta; version 3.9 (49 cases)"
porque: "cierre matriz agente×eval mínima"
evals_a_ampliar: ["groundedness schema campos fuentes_kb (P2)"]
```

```yaml
id: A-xcut-004
severidad: P2
bloque: ownership
archivo: src/agents/skill_catalog.py _SECONDARY_SKILLS
experto: T2
veredicto: PASS (aceptado)
evidencia_repo: "owned skills sin ancla runtime en tipicidad/ruta/evidencia/víctimas/audiencias/redactor/calidad/seguimiento"
evidencia_kb: "N/A"
impacto: "primario+3 secundarios no cubren todo el Used By; riesgo de under-anchor en pasos raros"
fix_aplicado: "ninguno (techo tokens documentado); rotar secundarios solo con evidencia de fallo"
porque: "no hervir el océano; anclas actuales pasan scorecard ≥4"
evals_a_ampliar: []
```

```yaml
id: A-xcut-005
severidad: P1
bloque: servicio
archivo: INFORME_AUDITORIA_12_ESPECIALISTAS_SERVICIO_WEB.md
experto: E0
veredicto: OPEN (fuera de track)
evidencia_repo: "F4 auth portal NO LISTO; F5 notepads Drive diferido"
evidencia_kb: "N/A"
impacto: "bloquea escala comercial / memoria de caso, no calidad skills A0–A8"
fix_aplicado: "documentado en Top 15; no implementar en esta PR"
porque: "decisión #6 prioridad skills; F4/F5 tracks separados"
evals_a_ampliar: []
```

### Top 15 acciones priorizadas (post-X)

| # | ID | Acción | Sev | Estado |
|---|---|---|---|---|
| 1 | A-xcut-001 | Fuentes KB residual (81/81) | P0 | **Hecho** |
| 2 | A-xcut-002 | CI F-06 Fuentes KB + anti-art. N | P0 | **Hecho** |
| 3 | A-xcut-003 | Evals tipicidad/ruta budget+surface | P1 | **Hecho** |
| 4 | F-11 | Ampliar registry honesty CI (Planned vs REAL) | P1 | **Hecho** (test overlap + Planned escape) |
| 5 | F-03 | Script score skill quality (Fuentes KB/Used By) | P1 | **Hecho** (`scripts/score_skill_quality.py`) |
| 6 | F-04 | Diff prompt↔I/O/T↔schema (portal/script) | P1 | **Hecho** (`scripts/diff_agent_contract.py`) |
| 7 | A-xcut-004 | Rotar secundarios runtime si evals fallan | P2 | Aceptado/monitor |
| 8 | F-07+ | Groundedness `fuentes_kb` en outputs LLM | P2 | **Parcial** (schema CI; runtime LLM = backlog) |
| 9 | Legacy prose | Limpiar “gestor/calidad” residual O1/O2 | P2 | Backlog |
| 10 | F-08/F5 | Notepads `{agent_id}.md` Drive+DB piloto | P2 | **En progreso** (plantillas + sync + runbook) |
| 11 | F4 | Auth portal / panel 12 servicio | P1 | **Diferido** (NO LISTO; track aparte) |
| 12 | F-10 | Portal checklist análisis por agente | P2 | Tras F4 |
| 13 | F-13 | Plantilla notepad inspección sin PII | P1 | **Hecho** (`agente/notepads/_TEMPLATE.md`) |
| 14 | PR #9 | Review humano + merge si CI verde | P1 | **Merged** |
| 15 | F-14 | Mantener sync skills en todo patch | P0 | Proceso (hecho en X) |

---

## Piloto evals (decisión #7) — actualizado

- Existentes: `route-tipicidad`, `route-memorial`, `route-cronologia`, `route-evidencia`, `route-ruta-906`, `route-victimas`, `route-audiencia`, `route-calidad-via-plan`, `route-seguimiento`, `route-coordinador-gerencia`, `tool-surface-*` (tipicidad/cronología/evidencia/víctimas/audiencias/redactor/calidad/seguimiento/coordinador/**ruta**), budgets (incl. tipicidad/ruta), `quality-gate-*`
- **Hecho A8:** route + tool-surface coordinador (evals v3.8)
- **Hecho X:** `tool-surface-ruta` + `instruction-budget-tipicidad` + `instruction-budget-ruta` (evals **v3.9**, 49 cases)
- Backlog P2: groundedness eval por campos schema `fuentes_kb`; notepads F-08; F4 auth portal

---

## A7 — Scorecard `analista_seguimiento_procesal`

| Campo | Valor |
|---|---|
| Fecha | 2026-08-05 |
| Oleada | A7 |
| Expertos | L1, L2, L3, T1–T7, E0 |
| Primario | `monitorear_radicado` |
| Secundarios anclados | generar_alertas_terminos_vencimientos, detectar_inactividad_procesal, crear_reporte_estado_caso |
| Skills owned / O8 parcial | monitorear + registrar + documentos + alertas + inactividad + reporte + resumen cliente (+ impulso shared redactor; términos shared ruta) |
| Veredicto global | **PARTIAL → PASS tras patches** |

### Técnica (0–5)

| Eje | Score | Nota 1 línea |
|---|---|---|
| Prompt | 5 | v5: skills nombrados, tools reales, `fuentes_kb`, HITL |
| Few-shots / anti-drift | 5 | Inactividad 4m + fallo inventar radicado 999999 |
| Ancla skills | 5 | Primario + 3 secundarios (reporte en ancla A7) |
| Tools honesty | 5 | REAL tools; planned lookup/calendar no invocables |
| Guardrails I/O/T | 5 | groundedness + no_invention + schema fuentes_kb |
| Schema | 5 | SeguimientoProcesal + `fuentes_kb` |
| HITL | 5 | Ya en HITL_OUTPUT_AGENTS + planes impulso |
| Evals | 5 | route + tool-surface + budget |
| Config parity | 4 | Prompt/guardrails/skills versionados |

### Jurídico-procedural (0–5)

| Eje | Score | Nota 1 línea |
|---|---|---|
| Grounding KB | 5 | Checklist seguimiento O8 en 906 + normas-clave |
| Etapa 906 | 4 | Remite ruta; no redefine etapas |
| Tipicidad/dogmática | 5 | Fuera de alcance (límite correcto) |
| Derechos víctima | 4 | Resumen cliente HITL; no revictimizar vía políticas |
| Hecho vs inferencia | 5 | Actuaciones con fuente; inactividad inferida = pendiente |
| Términos/oportunidad | 5 | Días hábiles; sin fecha_base no certificar |
| Citas | 4 | No inventa normas; remite KB/pendiente |
| HITL accionable | 5 | HITL_OUTPUT + no cliente sin abogado |
| Alcance | 5 | Operativo; no tipicidad ni redacción |
| Litigabilidad | 5 | Reporte accionable para gerente/abogado |

### Análisis panel (síntesis)

- **L1:** Cadena monitorear→actuaciones/documentos→inactividad/alertas→reporte litigable; KB tenía hueco O8 — cerrado.
- **L2:** Resumen cliente con HITL; confidencialidad en policies.
- **L3:** HITL ya cableado; refuerzo contractual prompt/guardrail.
- **T1:** Prompt v4 genérico; v5 alinea skills + schema.
- **T2:** Secundarios: +`crear_reporte_estado_caso` (misión paso 3).
- **T3:** groundedness + tools honesty anti-planned.
- **T4:** tool-surface vecinos ruta+calidad; excluye redactor/audiencias.
- **T5:** añadidos route/surface/budget seguimiento (evals v3.7).
- **T6:** `notas_trabajo` OK; Drive diferido.
- **T7:** PII en tools/args; no inventar radicados.

### Hallazgos A7

```yaml
id: A-segu-001
severidad: P1
bloque: skills
archivo: agente/skills/{O8 parcial}/*/SKILL.md
experto: L1+T2
veredicto: PASS (patched)
evidencia_repo: "6/6 core O8 sin Fuentes KB al inicio A7 (monitorear/registrar/documentos/alertas/reporte/resumen)"
evidencia_kb: "proceso-penal-906.md checklist seguimiento; normas-clave.md checklist O8"
impacto: "reportes sin contrato explícito de grounding / anti-invención de radicados"
fix_aplicado: "Fuentes KB + step 0 ancla en 6 skills + clarify planned process_lookup en inactividad; bump + sync .cursor"
porque: "F-05 convención Fuentes KB; O8 parcial plan A7"
evals_a_ampliar: []
```

```yaml
id: A-segu-002
severidad: P1
bloque: prompt+schema+guardrails
archivo: analista_seguimiento_procesal.md; schemas.SeguimientoProcesal; guardrails I/O/T
experto: T1+T3
veredicto: PASS (patched)
evidencia_repo: "prompt v4 sin skills nombrados/fuentes_kb; schema sin fuentes_kb; groundedness ausente"
evidencia_kb: "proceso-penal-906.md checklist seguimiento"
impacto: "drift prompt↔schema; invención de radicados/actuaciones menos enforceable"
fix_aplicado: "prompt v5 + fuentes_kb schema/render + groundedness_policy + tools allowlist honestas"
porque: "alineación tipicidad/…/calidad post-F3 como estándar"
evals_a_ampliar: []
```

```yaml
id: A-segu-003
severidad: P1
bloque: ownership
archivo: src/agents/skill_catalog.py _SECONDARY_SKILLS
experto: T2
veredicto: PASS (patched)
evidencia_repo: "secundarios solo alertas+inactividad (sin reporte de estado)"
evidencia_kb: "N/A"
impacto: "ancla runtime no priorizaba reporte accionable (paso 3 misión)"
fix_aplicado: "secundarios: alertas + inactividad + crear_reporte_estado_caso"
porque: "A7 foco operativo reporte; registrar/documentos siguen owned"
evals_a_ampliar: []
```

```yaml
id: A-segu-004
severidad: P1
bloque: kb
archivo: agente/conocimiento/proceso-penal-906.md; normas-clave.md
experto: L1+L2
veredicto: PASS (patched)
evidencia_repo: "KB sin checklist seguimiento operativo O8"
evidencia_kb: "checklist seguimiento (radicado→alertas→reporte→HITL; no inventar radicados)"
impacto: "skills O8 sin ancla procedural concreta"
fix_aplicado: "checklist seguimiento en 906 + normas-clave"
porque: "F-15 KB enrichment; no inventar arts/radicados"
evals_a_ampliar: []
```

```yaml
id: A-segu-005
severidad: P1
bloque: evals
archivo: config/evals/agent_eval_cases.json
experto: T5
veredicto: PASS (patched)
evidencia_repo: "0 evals seguimiento al inicio A7 (hueco plan)"
evidencia_kb: "N/A"
impacto: "regresión route/superficie/budget seguimiento invisible en CI"
fix_aplicado: "route-seguimiento + tool-surface-seguimiento + instruction-budget-seguimiento (evals v3.7)"
porque: "plan A7; F-07/F-12"
evals_a_ampliar: []
```

```yaml
id: A-segu-006
severidad: P2
bloque: hitl
archivo: skill_catalog.HITL_OUTPUT_AGENTS + plan_templates
experto: L3+T4
veredicto: PASS (ya cableado; refuerzo documental)
evidencia_repo: "seguimiento ya en HITL_OUTPUT_AGENTS; planes indagacion_impulso incluyen paso seguimiento"
evidencia_kb: "checklist seguimiento paso 7 HITL"
impacto: "riesgo de comunicar estado a cliente sin abogado — mitigado por skill resumen + prompt"
fix_aplicado: "refuerzo prompt/guardrail; sin cambio runtime HITL"
porque: "HITL ya correcto; A7 refuerza contrato"
evals_a_ampliar: []
```

---

## A8 — Scorecard `coordinador_caso`

| Campo | Valor |
|---|---|
| Fecha | 2026-08-05 |
| Oleada | A8 |
| Expertos | L1–L3, T1–T7, E0 |
| Primario | `clasificar_tarea_y_etapa` |
| Secundarios anclados | gestionar_faltantes_expediente, detectar_urgencia_penal, actualizar_tareas_responsable |
| Skills owned / O8 gerencia | POC_OWNED_SKILLS (5) + marcar_pendientes shared redactor |
| Previo G01–G09 | **Hecho** (reafirmado; sin reopen) |
| Veredicto global | **PARTIAL → PASS tras patches** |

### Técnica (0–5)

| Eje | Score | Nota 1 línea |
|---|---|---|
| Prompt | 5 | v28: `contratos_gerencia` + Fuentes KB + triage/HITL/voz |
| Few-shots / anti-drift | 5 | A–E: route, plan, OOS, rol, atribución, bitácora, deliberación |
| Ancla skills | 5 | Primario + 3 secundarios gerencia (antes: sin `_SECONDARY_SKILLS`) |
| Tools honesty | 5 | Skills=contratos; chat sin redactor; REAL tools |
| Guardrails I/O/T | 5 | groundedness + domain_limits + tools honesty POC |
| Schema | 4 | TriageResult en código (chat prosa OK); sin `fuentes_kb` en TriageResult |
| HITL | 5 | Redacción solo plan; urgencia critica/alta escala humano |
| Evals | 5 | route-gerencia + tool-surface + budget + urgency/scope previos |
| Config parity | 4 | Prompt/guardrails/skills versionados; G08 parity vigente |

### Jurídico-procedural (0–5)

| Eje | Score | Nota 1 línea |
|---|---|---|
| Grounding KB | 5 | Checklist gerencia O8 en 906 + normas-clave |
| Etapa 906 | 4 | `etapa_aparente` hipótesis; rigor → ruta |
| Tipicidad/dogmática | 5 | Fuera de alcance (delega) |
| Derechos víctima | 5 | Alcance penal-víctimas; OOS investigado/conductor |
| Hecho vs inferencia | 5 | Bitácora + pendientes; no inventar hechos de caso |
| Términos/oportunidad | 4 | Urgencia/días hábiles vía contrato; no certifica plazos |
| Citas | 5 | No inventa normas; remite KB/pendiente |
| HITL accionable | 5 | Memorial/impulso → plan; una voz |
| Alcance | 5 | Solo penal-víctimas Colombia; OOS otros equipos |
| Litigabilidad | 5 | Síntesis accionable + bitácora + próximos pasos |

### Análisis panel (síntesis)

- **L1:** Cadena triage→faltantes→urgencia→tareas→síntesis; KB sin checklist gerencia — cerrado.
- **L2:** Alcance víctimas + no revictimizar en escalamiento.
- **L3:** HITL redacción ya cableado; G01–G09 no reabiertos.
- **T1:** Prompt ya maduro (v27); v28 nombra contratos + Fuentes KB.
- **T2:** Ancla secundaria POC ausente → añadida.
- **T3:** groundedness_policy + tools honesty skills≠tools.
- **T4:** tool-surface POC = todos chat excepto redactor.
- **T5:** route-coordinador-gerencia + tool-surface-coordinador (evals v3.8).
- **T6/T7:** notepads diferidos; PII en args tools.

### Hallazgos A8

```yaml
id: A-coord-001
severidad: P1
bloque: skills
archivo: agente/skills/{clasificar,gestionar_faltantes,detectar_urgencia,actualizar_tareas}/SKILL.md
experto: L1+T2
veredicto: PASS (patched)
evidencia_repo: "4/5 POC_OWNED sin Fuentes KB (marcar_pendientes ya tenía)"
evidencia_kb: "proceso-penal-906.md + normas-clave.md checklist gerencia"
impacto: "contratos gerencia sin ancla KB explícita / anti-invención de etapa-urgencia"
fix_aplicado: "Fuentes KB + step 0 en 4 skills; bump + sync .cursor"
porque: "F-05; O8 gerencia plan A8"
evals_a_ampliar: []
```

```yaml
id: A-coord-002
severidad: P1
bloque: kb
archivo: agente/conocimiento/proceso-penal-906.md; normas-clave.md
experto: L1+L2
veredicto: PASS (patched)
evidencia_repo: "KB sin checklist gerencia/POC O8"
evidencia_kb: "checklist gerencia (triage→faltantes→urgencia→tareas→HITL)"
impacto: "skills gerencia sin ancla procedural concreta"
fix_aplicado: "checklist gerencia en 906 + normas-clave"
porque: "F-15; no inventar hechos/etapa/radicados"
evals_a_ampliar: []
```

```yaml
id: A-coord-003
severidad: P1
bloque: ownership
archivo: src/agents/skill_catalog.py _SECONDARY_SKILLS
experto: T2
veredicto: PASS (patched)
evidencia_repo: "coordinador_caso ausente de _SECONDARY_SKILLS (solo primario)"
evidencia_kb: "N/A"
impacto: "ancla runtime no priorizaba faltantes/urgencia/tareas"
fix_aplicado: "secundarios: faltantes + urgencia + actualizar_tareas"
porque: "A8 O8 gerencia; marcar_pendientes queda owned + shared redactor"
evals_a_ampliar: []
```

```yaml
id: A-coord-004
severidad: P1
bloque: prompt+guardrails
archivo: coordinador_caso.md; guardrails output/tools
experto: T1+T3
veredicto: PASS (patched)
evidencia_repo: "prompt sin bloque contratos_gerencia/Fuentes KB; output sin groundedness_policy"
evidencia_kb: "checklist gerencia"
impacto: "drift enforceable menor frente a especialistas post-F3"
fix_aplicado: "prompt v28 + groundedness/domain_limits + tools honesty POC_OWNED"
porque: "alineación estándar A0–A7"
evals_a_ampliar: []
```

```yaml
id: A-coord-005
severidad: P1
bloque: evals
archivo: config/evals/agent_eval_cases.json
experto: T5
veredicto: PASS (patched)
evidencia_repo: "budget+urgency+scope sí; sin route/tool-surface explícitos de gerencia POC"
evidencia_kb: "N/A"
impacto: "regresión superficie POC / route faltantes invisible en CI"
fix_aplicado: "route-coordinador-gerencia + tool-surface-coordinador (evals v3.8)"
porque: "plan A8; F-07/F-12"
evals_a_ampliar: []
```

```yaml
id: A-coord-006
severidad: P2
bloque: schema
archivo: schemas.TriageResult
experto: T1
veredicto: PASS (aceptado)
evidencia_repo: "TriageResult sin fuentes_kb; chat POC es prosa (correcto)"
evidencia_kb: "N/A"
impacto: "bajo — triage es determinista en código, no output_type LLM"
fix_aplicado: "ninguno (documentado); grounding vía prompt/skills/KB"
porque: "no forzar schema conversacional; G02 triage único"
evals_a_ampliar: []
```

---

## Anexo — texto previo “Cierre parcial F1–F3” (histórico)

> Los bullets siguientes reflejan la intención documentada pre-A0; la reconciliación y ejecución real están en §A0–A7 arriba.

**Patches pretendidos (histórico)**
- KB / 17 skills O1+O2 / secundarios / evals 3.2 / F3 prompts — **reclamados como Hecho antes de existir en árbol**; ejecutados en A0–A7.

**Siguiente ejecución sugerida (histórico):** O3 / F4 → **reemplazado por A8 coordinador**.
