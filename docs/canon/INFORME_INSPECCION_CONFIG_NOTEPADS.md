# Informe vivo — Inspección config + notepads (F1–F4)

**Plan inspección:** [`PLAN_INSPECCION_CONFIG_NOTEPADS.md`](PLAN_INSPECCION_CONFIG_NOTEPADS.md)  
**Plan análisis por agente:** [`PLAN_ANALISIS_PROMPTS_SKILLS_HERRAMIENTAS.md`](PLAN_ANALISIS_PROMPTS_SKILLS_HERRAMIENTAS.md) (`EN_EJECUCION`)  
**Fecha:** 2026-08-05  
**E0:** Auto (humano)  
**Modo:** panel IA personificado + síntesis E0  
**Piloto:** `config/evals/agent_eval_cases.json` (v3.2)  
**Drive:** `https://drive.google.com/drive/folders/0ABOGkPnKHSC5Uk9PVA` (dual DB+Drive; notepads F5 diferido por prioridad #6)  
**Rama de trabajo A0–A2:** `cursor/analisis-a0-a1-prompts-skills`

---

## Estado de fases

| Fase | Estado |
|---|---|
| F1 Inventario | **Hecho** |
| F2 O1 Tipicidad | **Hecho** (hallazgos + patches H-101…H-105) |
| F2 O2 Ruta 906 | **Hecho** (hallazgos + patches H-201…H-203) |
| F3 Prompts/guardrails/HITL | **Hecho** (H-301…H-304) |
| F4 Panel 12 servicio | **Hecho — NO LISTO** (ver `INFORME_AUDITORIA_12_ESPECIALISTAS_SERVICIO_WEB.md`) |
| F5 Spec notepads | Diferido (prioridad skills) |
| F6 Top acciones E0 | **Hecho** |
| **A0** Re-score tipicidad + ruta | **Hecho** (residuales A-tipi / A-ruta + patches P0/P1) |
| **A1** Deep cronología | **Hecho** (scorecard + A-crono + patches P0/P1) |
| **A2** Deep evidencia | **Hecho** (scorecard + A-evid + patches P0/P1) |

---

## F1 — Inventario de cobertura

| Superficie | Conteo | Veredicto |
|---|---|---|
| Skills `agente/skills/*/SKILL.md` | **81** | Cubiertos en catálogo; 0 sin Used By |
| Prompts agentes | **10/10** | Roster canónico completo |
| Guardrails I/O/T por agente | **10/10** (input+output+tools) | PASS cobertura archivos |
| Guardrails globales g1–g10 | **10** | Presentes |
| Eval cases | **33** | Routing/scope/HITL/PII; tipicidad solo `route-tipicidad` |
| Evals → `analista_ruta_procesal` | **1** (`route-ruta-906`) | **PASS** (A0) |
| Evals → `analista_representacion_victimas` | **0** | **FAIL** cobertura eval |
| Evals → `analista_seguimiento_procesal` | **0** | **FAIL** cobertura eval |
| Referencias KB path en skills O1/O2/O3/O4 | **34** con Fuentes KB | **PASS** (A0–A2) |
| KB `penal.md` | marco tipico operativo | **PASS** (A0) |
| KB `proceso-penal-906.md` | 28 líneas (etapas OK, términos diferidos) | PARTIAL |
| KB `normas-clave.md` | 25 líneas (marco + derechos) | PARTIAL |
| Legacy prose residual O1/O2 | varios (“calidad”, “gestor”, “coordinador”) | PARTIAL |

### Matriz agente × primario × secundarios (runtime)

Fuente: `src/agents/skill_catalog.py`.

| Agente | Primario | Secundarios anclados | Gap vs skills owned |
|---|---|---|---|
| `analista_responsabilidad_tipicidad` | `descomponer_elementos_tipo_penal` | conductas, dolo, autoría | **OK (A0)** — atipicidad/mapear owned sin ancla runtime |
| `analista_ruta_procesal` | `identificar_etapa_procesal_ley906` | oportunidad, ruta, términos | **OK (A0)** — riesgos/impulso owned sin ancla runtime |
| `analista_cronologia_hechos` | `construir_cronologia_penal` | extraer, contradicciones, clasificar_fuente | **OK (A1)** |
| `analista_evidencia` | `inventariar_evidencia` | clasificar_tipo, matriz, brechas | **OK (A2)** — recaudo/custodia/preservar owned sin ancla runtime |
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
| 15 | — | Oleadas A2–A8 (ex O3–O8) | P1 | **A2 Hecho; siguiente A3** |

---

## Cierre parcial F1–F3 (nota de reconciliación A0)

**Hallazgo de proceso (A0):** el bloque “Cierre parcial de ejecución” abajo marcó H-101…H-304 como **Hecho**, pero al iniciar A0 en el árbol de trabajo **no** estaban aplicados (skills sin `## Fuentes KB`, `penal.md` sin marco tipico, schemas sin `etapa_ley906`/`fuentes_kb`, sin `route-ruta-906`).  
Los IDs `H-*` se conservan; la ejecución real de esos residuales se documenta como `A-tipi-*` / `A-ruta-*` / patches A0.

**Patches A0/A1/A2 aplicados (2026-08-05)**
- KB: `agente/conocimiento/{penal,normas-clave,proceso-penal-906}.md` (marco tipico + enum etapas + días hábiles + checklist evidencia O4)
- 34 skills O1–O4 → `## Fuentes KB` + steps verificables + bump checksum
- `src/agents/skill_catalog.py` secundarios tipicidad (dolo/autoría), ruta (términos), cronología (`clasificar_fuente_factual`), evidencia (`clasificar_tipo_prueba`)
- Schemas/renderer: `fuentes_kb`, `estado` elemento, `etapa_ley906`, `evidencia_etapa`, `ruta_detallada`, `InventarioEvidencia.fuentes_kb` + `tipo` Literal
- Prompts tipicidad v5 / ruta v7 / cronología v5 / evidencia v7 + guardrails I/O grounding
- Evals `3.2` + caso `route-ruta-906` (evidencia ya tenía route/tool-surface)
- Sync: `python scripts/sync_skills_agente_a_cursor.py` (81 skills)

**Tests (A0–A2 focused):** **51 passed** (`test_l03_structured_output`, `test_guardrails_iot_coverage`, `test_agent_evals`, `test_skill_config`, `test_fase3_plan_product`, `test_prompt_skill_quality`, `test_bitacora_notas`).

**Siguiente oleada:** **A3** — deep-dive `analista_representacion_victimas` (+ O5 + eval).

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

## Cola E0 (post A0–A2)

| # | ID | Acción | Sev | Estado |
|---|---|---|---|---|
| 1 | A-tipi-* | Patches tipicidad residuales | P0/P1 | **Hecho** |
| 2 | A-ruta-* | Patches ruta + eval | P0/P1 | **Hecho** |
| 3 | A-crono-* | Patches cronología O3 | P1 | **Hecho** |
| 4 | A-evid-* | Patches evidencia O4 | P1 | **Hecho** |
| 5 | — | **A3** deep `analista_representacion_victimas` (+ O5 + eval) | P1 | **Siguiente** |
| 6 | — | Evals seguimiento | P1 | Cola A7 |
| 7 | F-08 | Notepads Drive dual | P2 | Diferido |
| 8 | — | Groundedness eval tipicidad/evidencia campos | P2 | Backlog |

---

## Piloto evals (decisión #7) — actualizado

- Existentes: `route-tipicidad`, `route-memorial`, `route-cronologia`, `route-evidencia`, `tool-surface-tipicidad`, `tool-surface-cronologia`, `tool-surface-evidencia`
- **Hecho:** `route-ruta-906` → `analista_ruta_procesal`, `expected_plan_required: false` (evals v3.2)

---

## Notas panel (personas) — post A0–A2

- **L1:** KB tipicidad/ruta/cronología/evidencia con suelo mínimo litigable; no inventar arts concretos — verificación vía RAG sigue siendo gate.
- **L3:** Términos endurecidos; evidencia no certifica plazos ni admisibilidad.
- **T2:** Secundarios tipicidad/ruta/crono/evidencia alineados a prompts.
- **T5:** Hueco eval ruta cerrado; quedan víctimas/seguimiento.
- **T6:** Notepads diferidos; contrato `notas_especialista` OK en los 4 agentes deep.

---

## Anexo — texto previo “Cierre parcial F1–F3” (histórico)

> Los bullets siguientes reflejan la intención documentada pre-A0; la reconciliación y ejecución real están en §A0–A2 arriba.

**Patches pretendidos (histórico)**
- KB / 17 skills O1+O2 / secundarios / evals 3.2 / F3 prompts — **reclamados como Hecho antes de existir en árbol**; ejecutados en A0–A2.

**Siguiente ejecución sugerida (histórico):** O3 / F4 → **reemplazado por A3 víctimas**.
