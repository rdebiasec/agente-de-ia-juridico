# Informe vivo — Inspección config + notepads (F1–F4)

**Plan:** [`PLAN_INSPECCION_CONFIG_NOTEPADS.md`](PLAN_INSPECCION_CONFIG_NOTEPADS.md)  
**Fecha:** 2026-08-05  
**E0:** Auto (humano)  
**Modo:** panel IA personificado + síntesis E0  
**Piloto:** `config/evals/agent_eval_cases.json`  
**Drive:** `https://drive.google.com/drive/folders/0ABOGkPnKHSC5Uk9PVA` (dual DB+Drive; notepads F5 diferido por prioridad #6)

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

---

## F1 — Inventario de cobertura

| Superficie | Conteo | Veredicto |
|---|---|---|
| Skills `agente/skills/*/SKILL.md` | **81** | Cubiertos en catálogo; 0 sin Used By |
| Prompts agentes | **10/10** | Roster canónico completo |
| Guardrails I/O/T por agente | **10/10** (input+output+tools) | PASS cobertura archivos |
| Guardrails globales g1–g10 | **10** | Presentes |
| Eval cases | **33** | Routing/scope/HITL/PII; tipicidad solo `route-tipicidad` |
| Evals → `analista_ruta_procesal` | **0** | **FAIL** cobertura eval |
| Evals → `analista_representacion_victimas` | **0** | **FAIL** cobertura eval |
| Evals → `analista_seguimiento_procesal` | **0** | **FAIL** cobertura eval |
| Referencias KB path en skills O1/O2 | **0/17** | **FAIL** anclaje procedural |
| KB `penal.md` | 17 líneas (notas vacías) | **FAIL** profundidad dogmática |
| KB `proceso-penal-906.md` | 28 líneas (etapas OK, términos diferidos) | PARTIAL |
| KB `normas-clave.md` | 25 líneas (marco + derechos) | PARTIAL |
| Legacy prose residual O1/O2 | varios (“calidad”, “gestor”, “coordinador”) | PARTIAL |

### Matriz agente × primario × secundarios (runtime)

Fuente: `src/agents/skill_catalog.py`.

| Agente | Primario | Secundarios anclados | Gap vs skills owned |
|---|---|---|---|
| `analista_responsabilidad_tipicidad` | `descomponer_elementos_tipo_penal` | conductas, atipicidad, mapear | **No ancla** dolo, autoría, agravantes, preguntas |
| `analista_ruta_procesal` | `identificar_etapa_procesal_ley906` | oportunidad, ruta | No ancla términos / riesgos / impulso |
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
| 1 | H-101 | Enriquecer `penal.md` + `normas-clave.md` (marco tipico/autoría/dolo sin arts inventados) | P0 | **Hecho** |
| 2 | H-102 | `## Fuentes KB` + steps grounding en 8 skills O1 | P0 | **Hecho** (v3) |
| 3 | H-201 | Alinear enum etapas skill ↔ playbook 906 | P0 | **Hecho** |
| 4 | H-202 | Fuentes KB + steps en skills O2 críticos (etapa, ruta, oportunidad, términos) | P1 | **Hecho** (9 skills O2 v3) |
| 5 | H-103 | Ampliar `_SECONDARY_SKILLS` tipicidad (dolo, autoría) | P1 | **Hecho** (+ términos en ruta) |
| 6 | H-104 | Limpiar legacy prose O1 | P1 | **Hecho** |
| 7 | H-105 | Checklists dogmáticos en dolo/autoría/agravantes | P1 | **Hecho** |
| 8 | H-203 | Eval `route-ruta-906` | P1 | **Hecho** (evals 3.2) |
| 9 | H-204 | Endurecer disclaimer términos (días hábiles) | P1 | **Hecho** (skill + playbook) |
| 10 | H-301/H-302 | F3 prompts + schemas tipicidad/ruta frente a KB nueva | P0 | **Hecho** |
| 11 | H-303/H-304 | F3 guardrails específicos + retirar citas no verificadas de planes | P0/P1 | **Hecho** |
| 12 | — | F4: checklist panel 12 (1 día) | P1 | Pendiente |
| 13 | — | F5: notepads `{agent_id}.md` en Drive `0ABOGkPnKHSC5Uk9PVA` | P2 | Diferido |
| 14 | — | Evals tipicidad groundedness (matriz elementos) | P2 | Pendiente |
| 15 | — | Oleadas O3–O8 | P1 | Cola |

---

## Cierre parcial de ejecución (2026-08-05)

**Patches aplicados**
- KB: `agente/conocimiento/{penal,normas-clave,proceso-penal-906}.md`
- 17 skills O1+O2 → `config-version: 3` + `## Fuentes KB` + steps verificables
- `src/agents/skill_catalog.py` secundarios tipicidad/ruta
- Evals `3.2` + caso `route-ruta-906`
- Sync: `python scripts/sync_skills_agente_a_cursor.py` (81 skills)
- F3: prompts y guardrails específicos versionados; schemas/renderer jurídicos; plantillas sin citas sembradas

**Tests**
- Verde: configuración, config store, prompts/skills, I/O/T, schemas, planes HITL y evals: **52 passed**.
- Se corrigieron dos expectativas post-retiro de tutela: catálogo canónico de 81 skills y políticas desk sin alias `g*`.

**Siguiente ejecución sugerida:** O3 (hechos/cronología) o F4 (panel 12 servicio).

---

## Piloto evals (decisión #7)

Usar / ampliar:

- Existentes: `route-tipicidad`, `route-memorial`, `route-cronologia`, `route-evidencia`, `tool-surface-tipicidad`
- Nuevo propuesto: `route-ruta-906` → `analista_ruta_procesal`, `expected_plan_required: false`

---

## Notas panel (personas)

- **L1:** KB vacía es el bloqueante #1 de calidad litigable; skills O1 están bien como contratos pero “huecos” de procedural knowledge.  
- **L3:** términos/ruta deben seguir HITL; playbook ya dice no afirmar arts sin verificar.  
- **T2:** secundarios tipicidad incompletos vs ownership real (9 skills).  
- **T5:** hueco eval ruta/víctimas/seguimiento.  
- **T6:** notepads diferidos; contrato ya en prompts `notas_especialista`; Drive root confirmado.
