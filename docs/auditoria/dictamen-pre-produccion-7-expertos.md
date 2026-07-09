# Dictamen pre-producción — panel 7 expertos

**Fecha:** 2026-07-09 (validación técnica re-ejecutada)  
**Baseline:** [`baseline-pre-produccion-2026-07-08.md`](baseline-pre-produccion-2026-07-08.md) — commit `5a9f225`  
**Alcance:** agente web, portal `/auditoria/`, catálogo g1–g10, 90 skills, compliance Ley 1581.  
**Foco operativo del despacho:** desarrollo y auditoría en **local** (`http://127.0.0.1:8000`). Render/GitHub Pages verificados por smoke automatizado; uso en prod es opcional hasta auditoría humana.  
**Auditoría humana (Fase 5):** **pospuesta** por decisión del despacho (2026-07-09) — no bloquea cierre técnico.

---

## 1. Resumen ejecutivo — veredicto

| Nivel | Veredicto | Condición |
|-------|-----------|-----------|
| **GO técnico** | **SÍ** | Capas 1–5 PASS, smoke prod PASS, 90/90 skills APROBADO, 5/5 cadenas OK |
| **GO operativo** (casos reales) | **CONDICIONAL** | Requiere auditoría humana abogada (mín. 10 reglas + 11 agentes) + 3 pruebas chat manuales |
| **GO producción pleno** (693 ítems) | **NO** (aún) | Pendiente revisión completa en portal y «Publicar configuración» |

**Recomendación del comité automatizado:** autorizar **despliegue técnico** en Render/Pages tal como está; **no** sustituir revisión profesional ni publicar config sin firma del despacho.

---

## 2. Validación técnica (5 capas)

Fuente: [`validacion-sistema-completa-reporte.md`](validacion-sistema-completa-reporte.md) — **PASS global** (2026-07-09 16:40).

| Capa | Estado |
|------|--------|
| 1 — Skills 7 expertos | OK — `{'APROBADO': 90}` |
| 2 — Gates estáticos | OK — 693 ítems, espejo 90/90 |
| 3 — Pytest suite | OK — 157 tests (smoke excluido en capa 3) |
| 4 — Runtime | OK |
| 5 — Smoke HTTP local | OK |

**Correcciones aplicadas en este corte:**

- Rubricas E5/E6 ampliadas para **g9** (Ley 906) y **g10** (custodia); métricas `missing_g9=0`, `missing_g10=0`.
- Tests `test_fase3_plan_product.py` estabilizados (auth web + audit prelogin/PIN).
- Script [`scripts/smoke_produccion.sh`](../../scripts/smoke_produccion.sh) añadido.

---

## 3. Dictamen por experto (E1–E7)

| ID | Rol | Resultado | Hallazgo principal |
|----|-----|-----------|-------------------|
| E1 | Arquitecto de prompts | PASS | 90/90 con Purpose, Steps, guardrails; 0 I/O genérico |
| E2 | Socio penal víctimas | PASS | HITL g4 en salidas cliente; g5 en víctimas/hechos |
| E3 | Profesor penal | PASS | g3 hecho/inferencia; tipicidad sin certeza de culpabilidad |
| E4 | Litigante constitucional | PASS | Cadena tutela con gates; sin redacción directa por coordinador |
| E5 | Especialista Ley 906 | PASS | g9 en ruta/seguimiento/evidencia; frontera ruta/redactor |
| E6 | Oficial cumplimiento | PASS | g5/g6 sensibles; g10 custodia; login audit con consentimiento |
| E7 | Ingeniero QA | PASS | Lista canónica ↔ matriz ↔ SKILL.md alineados |

Detalle por skill: [`validacion-7-expertos-reporte.md`](validacion-7-expertos-reporte.md) · JSON: [`validacion-7-expertos-data.json`](validacion-7-expertos-data.json).

### Muestra manual revisada (10 skills representativos)

| Skill | Bloque | E1–E7 | Notas |
|-------|--------|-------|-------|
| `extraer_hechos_relevantes` | D | APROBADO | g3/g5/g4; Rol analista_cronologia |
| `construir_teoria_caso_victima` | E | APROBADO | Centrado víctima, g5 |
| `evaluar_procedencia_tutela` | A | APROBADO | Gate tutela; tier crítico |
| `redactar_memorial_penal` | B | APROBADO | HITL g4; redactor |
| `clasificar_aprobacion_juridica` | B | APROBADO | Último filtro salida |
| `identificar_etapa_procesal_ley906` | C | APROBADO | g9 presente |
| `preservar_evidencia_digital` | D | APROBADO | g10 + cadena evidencia |
| `preparar_preguntas_audiencia` | E | APROBADO | HITL oral; Rol preparador |
| `monitorear_radicado` | F | APROBADO | g9; Rol gestor_seguimiento |
| `revisar_coherencia_estrategica` | B | APROBADO | Calidad pre-salida |

### Cadenas críticas (5/5 OK)

| Cadena | Estado |
|--------|--------|
| tutela | OK |
| recursos_906 | OK |
| calidad_salida | OK |
| cliente | OK |
| evidencia_digital | OK |

### Reglas de negocio globales

| Regla | Estado |
|-------|--------|
| Tutela solo tras evaluador | OK |
| Ruta 906 no redacta recursos finales | OK |
| Preguntas víctima con HITL | OK |
| IA propone; abogado aprueba | OK |
| Guardrails globales g1–g10 | OK |

---

## 4. Smoke producción (Render + GitHub Pages)

Fuente: [`smoke-produccion-reporte.md`](smoke-produccion-reporte.md) — **PASS** (8/8 checks automatizados, 2026-07-09).

| Entorno | URL |
|---------|-----|
| Render | https://agente-de-ia-juridico.onrender.com/auditoria/ |
| Pages | https://rdebiasec.github.io/agente-de-ia-juridico/ |

**Paridad catálogo:** local = Render API = Pages estático → 10 guardrails, 90 skills, 402 pasos.

### Smoke manual pendiente (despacho — pospuesto)

- [ ] Login local `/auditoria/` — gate se oculta; panel con 10 reglas y agentes.
- [ ] Skill `inventariar_evidencia` — CONTENIDO con g9, g10 y Rol.
- [ ] GitHub Pages — mismo correo/PIN; progreso sincronizado.
- [ ] Chat `/abogado` — consulta penal-víctimas; trace visible; aviso g8 al final.

---

## 5. Seguridad Render (checklist DEPLOY)

Fuente: `GET /health` producción (2026-07-08).

| Control | Estado | Evidencia |
|---------|--------|-----------|
| `persistencia: postgres` | PASS | health |
| `environment: production` | PASS | health |
| `web_auth_enabled: true` | PASS | health |
| `dev_auto_login: false` | PASS | health |
| `openai_configured: true` | PASS | health |
| `slack_configured` | N/A prod | `false` — fuera de alcance este corte |
| CSP `/auditoria/` Tailwind+FA | PASS | smoke prod |
| CORS Pages | PASS | smoke prod |
| Secretos fuertes (SITE_PASSWORD, SESSION_SECRET) | PASS* | app arranca en Render; no valores débiles en logs |
| Migraciones 0004/0005 | PASS* | deploy exitoso post-push |

\*Verificación indirecta; rotación periódica de secretos recomendada.

---

## 6. Auditoría humana del portal (Fase 5)

**Estado:** **POSPUESTA** — explícitamente fuera de este corte (2026-07-09). No sustituible por rúbrica automatizada cuando se retome.

### Checklist para la abogada líder (cuando se active)

1. Entrar en **local** `http://127.0.0.1:8000/auditoria/` (o Render si el despacho lo elige) — correo + `SITE_PASSWORD` + PIN.
2. Revisar y marcar **10 reglas estrictas** (Aprobar / Ajustar).
3. Revisar **11 agentes** y sus guías prioritarias.
4. (Opcional completo) Revisar 402 pasos y 270 contextos de guía.
5. Exportar dictamen `.MD` desde el portal.
6. Cuando todo esté APROBADO → **Publicar configuración** (activa `skill_config` en runtime).

**Registro:** progreso en Postgres por correo; respaldo JSON opcional.

**Para GO operativo:** completar pasos 1–3 + publicar config + 3 pruebas chat documentadas.

---

## 7. Riesgos residuales

| # | Riesgo | Mitigación |
|---|--------|------------|
| 1 | LLM real no probado en suite automatizada | 3 consultas manuales chat con revisión abogada |
| 2 | Slack HITL sin token en prod | Configurar antes de usar canal Slack |
| 3 | REQ-001…050 sin checklist formal | Sprint posterior; ver `requisitos_asistente.json` |
| 4 | WhatsApp no implementado | Fuera de alcance |
| 5 | Cold start Render | Esperar ~30s primer request |
| 6 | 1 skill sin `## Rol en` (89/90 with_rol) | Aceptable si atómico; revisar en portal |
| 7 | Aprobación humana 693 ítems incompleta | Gate de negocio antes de casos reales |

---

## 8. Decisión sugerida

| Pregunta | Respuesta |
|----------|-----------|
| ¿Infraestructura y catálogo listos en prod? | **Sí** |
| ¿Skills y cadenas listos técnicamente? | **Sí** (90/90, g1–g10) |
| ¿Listo para casos reales sin más pasos? | **No** — falta gate humano (sección 6) |
| ¿Listo para que abogada audite en portal prod? | **Sí** |

**Próximo paso técnico (hecho en este corte):** validación 5 capas + smoke prod + commit de artefactos en repo.

**Próximo paso humano (cuando el despacho decida):** auditoría mínima (10 reglas + 11 agentes) en portal local, publicar configuración, 3 pruebas chat → entonces **GO operativo**.

---

## Anexos

- [baseline-pre-produccion-2026-07-08.md](baseline-pre-produccion-2026-07-08.md)
- [validacion-7-expertos-reporte.md](validacion-7-expertos-reporte.md)
- [validacion-sistema-completa-reporte.md](validacion-sistema-completa-reporte.md)
- [smoke-produccion-reporte.md](smoke-produccion-reporte.md)
