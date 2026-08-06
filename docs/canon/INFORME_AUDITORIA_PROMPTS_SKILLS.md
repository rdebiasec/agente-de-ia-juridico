# Informe consolidado — panel multi-experto (prompts/skills)

**Generado por:** E7 (síntesis) tras evidencia automatizada + rúbrica de `PROMPT_REVISION_PROMPTS_Y_SKILLS.md`.
**Alcance:** auditoría de estado; las olas de fix siguen este orden.

## Resumen por severidad

- **P0:** 1
- **P1:** 5
- **P2:** 2

## Hallazgos

### H-001 — P0

- **Archivo:** `agente/prompts/agents/analista_evidencia.md`
- **Evidencia:** 8 líneas; solo deliberacion_discutible
- **Experto(s):** E2+E3+E6
- **Impacto:** especialista evidencia diluido frente al Gerente
- **Fix propuesto:** reescribir al estándar de cronología/calidad
- **Porqué:** role prompt casi vacío pese a anclas en skill_catalog

### H-002 — P1

- **Archivo:** `agente/skills/*/SKILL.md`
- **Evidencia:** 81/81 descriptions con plantilla Use when the workflow requires
- **Experto(s):** E2
- **Impacto:** trigger inútil con disable-model-invocation
- **Fix propuesto:** reescribir descriptions con cuándo/para qué/no cuándo
- **Porqué:** viola rúbrica de trigger description del prompt maestro

### H-003 — P1

- **Archivo:** `agente/skills/*/SKILL.md`
- **Evidencia:** 48 secciones Rol en con IDs legacy: {'preparador_audiencias': 5, 'analista_cronologia': 9, 'gestor_seguimiento': 7, 'representacion_victima': 1, 'analista_tipicidad': 9, 'coordinador': 10, 'gestor_evidencia': 2, 'redactor': 4, 'calidad': 1}
- **Experto(s):** E3
- **Impacto:** ownership documentado no coincide con roster runtime
- **Fix propuesto:** mapear a IDs canónicos
- **Porqué:** skill_catalog y agent_ids usan roster nuevo

### H-004 — P1

- **Archivo:** `agente/skills/{12 skills}`
- **Evidencia:** sin No duplicar: ['monitorear_radicado', 'revisar_coherencia_estrategica', 'inventariar_evidencia', 'identificar_objetivo_audiencia', 'crear_reporte_estado_caso', 'seguimiento_documentos_radicados', 'clasificar_tipo_prueba', 'registrar_actuacion_procesal', 'preservar_evidencia_digital', 'redactar_memorial_penal', 'controlar_confidencialidad_datos_sensibles', 'redactar_ampliacion_denuncia']
- **Experto(s):** E3
- **Impacto:** solape en pipelines HITL
- **Fix propuesto:** añadir No duplicar con vecinas
- **Porqué:** rúbrica exige límites de ownership entre skills

### H-005 — P1

- **Archivo:** `agente/prompts/agents/*.md`
- **Evidencia:** 8 prompts con deliberacion_discutible copy-paste
- **Experto(s):** E2
- **Impacto:** drift inevitable entre especialistas
- **Fix propuesto:** plantilla compartida versionada en _shared/
- **Porqué:** anti-drift del prompt maestro

### H-006 — P2

- **Archivo:** `agente/prompts/agents/*`
- **Evidencia:** especialistas con <2 few-shots claros: ['analista_ruta_procesal.md', 'analista_responsabilidad_tipicidad.md', 'analista_seguimiento_procesal.md', 'analista_cronologia_hechos.md', 'analista_representacion_victimas.md', 'analista_audiencias.md']
- **Experto(s):** E2+E6
- **Impacto:** menos anclaje de comportamiento
- **Fix propuesto:** añadir segundo few-shot éxito+fallo por especialista
- **Porqué:** rúbrica prompts exige ≥2

### H-007 — P2

- **Archivo:** `docs/canon/reporte-detallado-agentes-prompts-skills-rag.md`
- **Evidencia:** menciona evaluador_derechos_fundamentales_tutela y skills de tutela
- **Experto(s):** E7
- **Impacto:** canon desfasado vs producto actual
- **Fix propuesto:** banner OBSOLETO + apuntar a prompt maestro
- **Porqué:** Gerente declara tutela fuera de alcance

### H-008 — P1

- **Archivo:** `config/evals/agent_eval_cases.json`
- **Evidencia:** evals de routing/scope; no fallan si description genérica o evidencia sin misión
- **Experto(s):** E5
- **Impacto:** regresión silenciosa de calidad de prompts/skills
- **Fix propuesto:** casos deterministas de integridad de prompt evidencia + description
- **Porqué:** cierre de ola 3 del plan

## Matriz ownership (primarios / secundarios)

| Agente | Skill primario | Secundarios |
|---|---|---|
| `coordinador_caso` | `clasificar_tarea_y_etapa` | gestionar_faltantes_expediente, detectar_urgencia_penal, … |
| `analista_cronologia_hechos` | `construir_cronologia_penal` | extraer_hechos_relevantes, detectar_contradicciones_factuales, detectar_vacios_factuales |
| `analista_responsabilidad_tipicidad` | `descomponer_elementos_tipo_penal` | identificar_conductas_punibles_preliminares, detectar_riesgos_atipicidad, mapear_tipo_penal_hecho_prueba |
| `analista_ruta_procesal` | `identificar_etapa_procesal_ley906` | evaluar_oportunidad_procesal, crear_ruta_procesal_recomendada |
| `analista_representacion_victimas` | `construir_teoria_caso_victima` | analizar_derechos_victima, detectar_riesgo_revictimizacion |
| `analista_evidencia` | `inventariar_evidencia` | detectar_brechas_probatorias, construir_matriz_hecho_prueba, crear_plan_recaudo_probatorio |
| `analista_audiencias` | `preparar_preguntas_audiencia` | identificar_objetivo_audiencia, preparar_guion_intervencion_oral |
| `redactor_documentos_juridicos` | `redactar_memorial_penal` | estructurar_hechos_fundamentos_solicitudes, marcar_pendientes_verificacion, controlar_tono_juridico_documento |
| `analista_seguimiento_procesal` | `monitorear_radicado` | generar_alertas_terminos_vencimientos, detectar_inactividad_procesal |
| `analista_calidad_juridica` | `revisar_coherencia_estrategica` | detectar_alucinaciones_legales, controlar_confidencialidad_datos_sensibles, clasificar_aprobacion_juridica |

## Solapes relevantes

- `verificar_citas_normativas` vs `detectar_alucinaciones_legales` — el primero foco normativo; el segundo detección amplia. Mantener `No duplicar` cruzado.
- `extraer_hechos_relevantes` vs `crear_matriz_hecho_fuente` vs `construir_cronologia_penal` — extracción ≠ soporte ≠ orden temporal.
- `inventariar_evidencia` vs `clasificar_tipo_prueba` vs `construir_matriz_hecho_prueba` — inventario ≠ clasificación ≠ matriz.

## Plan de olas (decisión E7)

1. **Ola 0:** H-001 reescribir `analista_evidencia.md`. **HECHO**
2. **Ola 1:** H-002, H-003, H-004 + endurecer skills primarios/secundarios. **HECHO**
3. **Ola 2:** H-005, H-006 plantilla compartida + few-shots. **HECHO**
4. **Ola 3:** H-007, H-008 canon + sync + evals. **HECHO**

## Cierre de ejecución (2026-08-05)

- Prompt maestro: `docs/canon/PROMPT_REVISION_PROMPTS_Y_SKILLS.md`
- Fragmentos compartidos: `agente/prompts/_shared/backoffice_fragments.md`
- Regresión: `tests/test_prompt_skill_quality.py` + evals `3.1` (budget evidencia/redactor, route tutela)
- Espejo: `python scripts/sync_skills_agente_a_cursor.py` OK (81 skills)
- Tests: `test_prompt_skill_quality`, `test_agent_evals`, `test_skill_config`, `test_skill_tools_registry` verdes

