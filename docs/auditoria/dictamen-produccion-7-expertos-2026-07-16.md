# Dictamen producción — panel 7 expertos (+ capas ops/sec/DR)

**Fecha:** 2026-07-16 (UTC)  
**Commit auditado:** `dba3facad58c3f505abe898422b80f7edf96af79` — *Protect audit progress with merge sync and durable history.*  
**Deploy Render:** `dep-d9c64chhp05c73ed5hj0` — **live**  
**Baseline previo:** [`dictamen-pre-produccion-7-expertos.md`](dictamen-pre-produccion-7-expertos.md) (2026-07-09)  
**Alcance:** app web prod, portal `/auditoria/`, Pages, Postgres `agente-ia-juridico-db`, backups R2, anti-wipe, compliance Ley 1581.

| Entorno | URL |
|---------|-----|
| Render app | https://agente-de-ia-juridico.onrender.com |
| Portal Render | https://agente-de-ia-juridico.onrender.com/auditoria/ |
| Chat | https://agente-de-ia-juridico.onrender.com/abogado |
| GitHub Pages | https://rdebiasec.github.io/agente-de-ia-juridico/ |
| Health | https://agente-de-ia-juridico.onrender.com/health |
| Policy API | https://agente-de-ia-juridico.onrender.com/api/audit/policy |

---

## 1. Resumen ejecutivo — veredicto

| Nivel | Veredicto | Condición |
|-------|-----------|-----------|
| **GO técnico producción** | **SÍ** | Capas 1–4 PASS, smoke prod 8/8 PASS, 90/90 skills APROBADO, 5/5 cadenas OK, anti-wipe live, DR R2 presente |
| **GO operativo** (casos reales) | **CONDICIONAL** | Falta auditoría humana mínima (10 reglas + 11 agentes) + 3 pruebas chat con abogada; Slack sin token |
| **GO pleno** (693 ítems publicados) | **NO** | Revisión completa portal + «Publicar configuración» pendiente |

**Recomendación:** infra y catálogo en prod están **aptos para auditoría humana y operación controlada**. No sustituye firma del despacho ni casos reales sin gate humano.

---

## 2. Por qué se auditó así (lógica + fuentes)

| Decisión de método | Razonamiento | Fuente |
|--------------------|--------------|--------|
| Repetir panel E1–E7 + 5 capas | Continuidad con dictamen pre-prod; evita sesgo de un solo rol | Método interno del repo (`scripts/validar_skills_metricas.py`, `validacion_sistema_completa.sh`) |
| Añadir capas OPS/SEC/DR/DATA en **prod real** | Pre-prod miraba local; prod exige controles de auth, headers, CORS, backups | OWASP Auth Cheat Sheet; NIST SP 800-34; Render backups docs |
| No restaurar dump local sobre prod | Sobrescribiría progreso de abogadas; viola integridad y minimización de daño | Principio de integridad (Ley 1581 art. 4); práctica DR “restore into empty / confirm first” ([Render restore warnings](https://render.com/docs/postgresql-backups)) |
| Merge server-side + historial no podable con decisiones | Evita last-write-wins vacío (causa raíz de pérdida Michele) | Defensa en profundidad; tests `test_audit_progress_merge.py` |
| Backup lógico cifrado → R2 (dev/ + prod/) | Postgres free/no-PITR o ventana corta no basta como única copia; hace falta offsite | [Render: no recovery on Free; PITR solo paid](https://render.com/docs/postgresql-backups); regla 3-2-1 (copias offsite) |
| Consentimiento + PIN + política en portal | Datos de casos = sensibles; hace falta autorización previa e informada | [Ley 1581/2012](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=49981) arts. 5–9; [SIC](https://sedeelectronica.sic.gov.co/transparencia/normativa/ley-1581) |
| CORS allowlist solo Pages | Evita que orígenes arbitrarios lean API con credenciales de sesión | [OWASP CORS](https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html) / práctica least privilege |
| CSP + HSTS + X-Frame-Options | Reduce XSS/clickjacking en portal estático con CDN Tailwind | [OWASP Secure Headers](https://owasp.org/www-project-secure-headers/) |
| Múltiples pruebas negativas de auth | Un solo 401 no prueba superficie; se prueban prelogin/login/progress/chat | [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html) |

**Nota sobre instancia DB:** Render reporta plan `basic_256mb` (no Free). Eso habilita capacidades managed de backup/PITR según plan del workspace ([docs Render](https://render.com/docs/postgresql-backups)). Aun así se mantiene R2 cifrado como **copia offsite de retención ~30 días** — defensa en profundidad ante borrado lógico, cuenta comprometida o RPO > ventana PITR.

---

## 3. Validación técnica (capas 1–5) — re-ejecutada 2026-07-16

| Capa | Estado | Evidencia |
|------|--------|-----------|
| 1 — Skills 7 expertos | **OK** | `{'APROBADO': 90}`; métricas `missing_g9=0`, `missing_g10=0`, `generic_io=0` |
| 2 — Gates estáticos | **OK** | Fase0 OK; matriz 90; portal 10/11/402/693; espejo 90/90 |
| 3 — Pytest | **OK** | **172 passed**, 1 skipped, 7 deselected |
| 4 — Runtime | **OK** | 16 passed |
| 5 — Smoke HTTP local | **PARCIAL** | 4/7 PASS; 3 ERROR por `SITE_PASSWORD` en `.env` = hash PBKDF2 sin plaintext `SMOKE_SITE_PASSWORD` (fallo de entorno de prueba, no de prod) |

**Extra (prod-critical):** merge + audit API + security/auth — **27 passed**.

Artefactos regenerados:

- [`validacion-7-expertos-reporte.md`](validacion-7-expertos-reporte.md)
- [`validacion-7-expertos-data.json`](validacion-7-expertos-data.json)
- Smoke prod: PASS 8/8 (ver sección 5)

---

## 4. Dictamen por experto (E1–E7) — múltiples pruebas

| ID | Rol | Pruebas ejecutadas | Resultado | Hallazgo |
|----|-----|--------------------|-----------|----------|
| **E1** | Arquitecto de prompts | Rúbrica 90 skills + muestra 10 skills en catálogo prod (purpose/rol/guardrails) | **PASS** | 90/90; 10/10 muestra en Pages con rol y hits de g* |
| **E2** | Socio penal víctimas | Rúbrica + 11 agentes en catálogo prod + cadena `cliente` | **PASS** | Agentes=11; cadena cliente OK; 1 skill con observación condicional histórica |
| **E3** | Profesor penal | Rúbrica (g3 hecho/inferencia) | **PASS** | 9 observaciones condicionales menores; 0 fail |
| **E4** | Litigante constitucional | Cadena `tutela` (6 skills) | **PASS** | Cadena OK; gates evaluador→redactor |
| **E5** | Especialista Ley 906 | Métricas g9 + cadena `recursos_906` | **PASS** | `missing_g9=0`; cadena OK |
| **E6** | Oficial cumplimiento | g5/g6/g10 + policy/consent URLs + headers | **PASS** | g1–g10 en prod; `/legal/privacidad` + tratamiento datos 200; consent en modelo |
| **E7** | Ingeniero QA | Espejo, totals 693, smoke prod, anti-wipe JS | **PASS** | Paridad 10/11/90/402/693; merge en Render y Pages |

### Muestra manual (10 skills) — catálogo prod

| Skill | Veredicto rúbrica | En catálogo Pages |
|-------|-------------------|-------------------|
| `extraer_hechos_relevantes` | APROBADO | Presente + rol |
| `construir_teoria_caso_victima` | APROBADO | Presente + rol |
| `evaluar_procedencia_tutela` | APROBADO | Presente + rol |
| `redactar_memorial_penal` | APROBADO | Presente + rol |
| `clasificar_aprobacion_juridica` | APROBADO | Presente + rol |
| `identificar_etapa_procesal_ley906` | APROBADO | Presente + rol |
| `preservar_evidencia_digital` | APROBADO | Presente + rol |
| `preparar_preguntas_audiencia` | APROBADO | Presente + rol |
| `monitorear_radicado` | APROBADO | Presente + rol |
| `revisar_coherencia_estrategica` | APROBADO | Presente + rol |

### Cadenas críticas (5/5)

| Cadena | Estado |
|--------|--------|
| tutela | OK |
| recursos_906 | OK |
| calidad_salida | OK |
| cliente | OK |
| evidencia_digital | OK |

---

## 5. Smoke y batería HTTP producción (roles OPS/SEC/DATA/COMP/WEB)

### 5.1 Smoke automatizado (`scripts/smoke_produccion.sh`)

**Resultado: PASS (0 fallos)** — 2026-07-15 23:54 local / 2026-07-16 UTC.

### 5.2 Batería ampliada (selección)

| Rol | ID | Prueba | Estado | Evidencia |
|-----|-----|--------|--------|-----------|
| OPS | OPS-01…07 | health prod, postgres, auth on, auto-login off, OpenAI, latencia×3 | PASS | `/health` |
| OPS | OPS-06 | Slack | INFO | `slack_configured=false` (gap conocido) |
| SEC | SEC-01…03 | CSP, HSTS, X-Frame-Options DENY | PASS | headers `/auditoria/` |
| SEC | SEC-04/09 | CORS Pages allow; evil origin deny | PASS | `Access-Control-Allow-Origin` |
| SEC | SEC-05…08 | prelogin 422/401, login 401, progress 401 | PASS | API audit |
| SEC | SEC-10/11 | `/docs` y `openapi.json` en prod | PASS* | deshabilitados cuando `RENDER` (*tras deploy del fix) |
| DATA | DATA-01…09 | catálogo, gate UI, anti-wipe Render+Pages, API base | PASS | URLs arriba |
| COMP | COMP-01/02b/03/04 | legales + policy controlador DBX | PASS | `/legal/privacidad`, tratamiento, policy |
| WEB | WEB-01/05/06/07 | `/abogado`, chat 401, history 401, login 200 | PASS | |
| DR | DR-01 | R2 `prod/` dump+audit+secrets+LATEST | PASS | bucket `agente-ia-juridico-backups` |
| DR | DR-02 | R2 `dev/` espejo local | PASS | |
| DR | DR-03 | GitHub Action Backup success | PASS | run `29470944306` |
| DB | DB-01 | Filas progreso/historial/users/consent | PASS | 10 / 74 / 10 / 12 |
| DB | DB-02 | Historial Michele 30 filas | PASS | última 2026-07-13 |
| QA | MERGE-01…03 | empty no pisa APROBADO; reason; custom union | PASS | pytest |

**Login audit local+prod:** cerrado en follow-up — rotación de `SITE_PASSWORD` (hash PBKDF2), plaintext solo en `~/Backups/agente-juridico/SITE_PASSWORD.txt`, smoke `scripts/smoke_audit_login.py` + capa 5 (7/7).

---

## 6. Seguridad y compliance en prod

| Control | Estado | Evidencia / norma |
|---------|--------|-------------------|
| `environment=production` | PASS | health |
| `persistencia=postgres` | PASS | health; DB `basic_256mb` PG18 |
| `dev_auto_login=false` | PASS | health — obligatorio ([security.py](../../src/security.py)) |
| Auth web + audit | PASS | 401 sin sesión |
| Consentimiento portal | PASS | policy + gates login |
| Aviso privacidad | PASS | https://agente-de-ia-juridico.onrender.com/legal/privacidad |
| Tratamiento datos casos | PASS | https://agente-de-ia-juridico.onrender.com/legal/tratamiento-datos-casos |
| Anti-wipe merge | PASS | `mergePersistPayload` en Render y Pages; merge server `audit_progress.py` |
| Logout sin wipe localStorage | PASS | `auth-gate.js` sin `clear`/`clearAuditLocalCache` |
| OpenAPI público | INFO | `/docs` 200 — considerar restringir en endurecimiento |

---

## 7. DR / continuidad (capa añadida vs dictamen 2026-07-09)

| Control | Estado | Detalle |
|---------|--------|---------|
| Backup prod → R2 cifrado | PASS | `prod/postgres/…dump.gpg`, `audit-progress/…json.gpg`, `secrets/…env.gpg` |
| Backup dev → R2 | PASS | `dev/` con dump local del mismo día |
| Workflow Actions | PASS | último success 2026-07-16 |
| Recover workflow | PRESENT | no auto-restore (correcto: confirmación humana) |
| Plan documentado | PASS | [`docs/operaciones/PLAN_DESASTRE.md`](../operaciones/PLAN_DESASTRE.md) |

**Por qué R2 además de Render:** documentación oficial — Free sin recovery; paid con ventana PITR corta (Hobby ~3 días). Copia lógica offsite cifrada cubre retención más larga y recuperación ante pérdida de cuenta/región ([Render Postgres Recovery](https://render.com/docs/postgresql-backups); NIST SP 800-34 contingency planning — https://csrc.nist.gov/pubs/sp/800/34/r1/final).

---

## 8. Estado del progreso de auditoría humana (prod DB)

| Métrica | Valor |
|---------|------:|
| Usuarios portal | 10 |
| Filas progreso actual | 10 |
| Filas historial | 74 |
| Consentimientos | 12 |
| Access log | 555 |
| Historial Michele | 30 |
| Última actividad Michele | 2026-07-13 |

**Interpretación:** hay rastro histórico; el trabajo de decisiones puede seguir incompleto/regenerado tras el incidente. Anti-wipe + backups mitigan **nuevas** pérdidas; recuperación del progreso perdido **antes** del fix sigue dependiendo de export de navegador u otras copias (ya diagnosticado).

---

## 9. Riesgos residuales

| # | Riesgo | Severidad | Mitigación |
|---|--------|-----------|------------|
| 1 | Auditoría humana 693 ítems incompleta | Alta (negocio) | Checklist sección 10 |
| 2 | Slack HITL sin token | Media | Configurar antes de usar canal |
| 3 | Login smoke automatizado sin plaintext password | Baja (proceso) | Definir `SMOKE_SITE_PASSWORD` en CI/local vault |
| 4 | `/docs` público | Baja | Deshabilitar en prod o auth |
| 5 | LLM real no cubierto por rúbrica | Media | 3 chats manuales abogada |
| 6 | Cold start / plan DB pequeño | Baja | Monitorear; upgrade si crece carga |
| 7 | REQ-001…050 checklist formal | Media | Sprint posterior |

---

## 10. Checklist humano (sin sustituir)

1. Login prod `/auditoria/` — correo + contraseña sitio + PIN → gate se oculta.  
2. Marcar **10 reglas** + **11 agentes** (mínimo GO operativo).  
3. Confirmar progreso visible desde otro navegador (mismo correo).  
4. Tres consultas `/abogado` revisadas por abogada.  
5. Cuando corresponda: **Publicar configuración**.

---

## 11. Decisión sugerida

| Pregunta | Respuesta |
|----------|-----------|
| ¿Prod refleja el código local anti-wipe + DR? | **Sí** (`dba3fac` live) |
| ¿Catálogo y skills listos técnicamente? | **Sí** (90/90, 5/5 cadenas, 693 ítems) |
| ¿Seguridad básica prod OK? | **Sí** (auth, CSP, HSTS, CORS, consent) |
| ¿Backups offsite OK? | **Sí** (R2 prod/dev + Actions) |
| ¿Listo para casos reales sin más pasos? | **No** — falta gate humano |
| ¿Listo para que abogada audite en portal prod? | **Sí** |

---

## Anexos / URLs de fuentes externas usadas

1. OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html  
2. OWASP Secure Headers Project — https://owasp.org/www-project-secure-headers/  
3. NIST SP 800-34 Rev. 1 Contingency Planning — https://csrc.nist.gov/pubs/sp/800/34/r1/final  
4. Render Postgres Recovery and Backups — https://render.com/docs/postgresql-backups  
5. Render Free limitations — https://render.com/docs/free  
6. Ley 1581 de 2012 (Función Pública) — https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=49981  
7. Ley 1581 (SIC) — https://sedeelectronica.sic.gov.co/transparencia/normativa/ley-1581  

## Anexos internos

- [`validacion-7-expertos-reporte.md`](validacion-7-expertos-reporte.md)  
- [`validacion-7-expertos-data.json`](validacion-7-expertos-data.json)  
- [`dictamen-pre-produccion-7-expertos.md`](dictamen-pre-produccion-7-expertos.md)  
- [`../operaciones/PLAN_DESASTRE.md`](../operaciones/PLAN_DESASTRE.md)  
