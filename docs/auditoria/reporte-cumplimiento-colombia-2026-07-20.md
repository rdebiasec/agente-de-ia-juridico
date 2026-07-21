# Reporte de cumplimiento — servicio firma virtual penal-víctimas (Colombia)

**Fecha:** 2026-07-20  
**Alcance:** código local + superficies públicas en prod (`https://agente-de-ia-juridico.onrender.com`)  
**Marco de referencia:** Ley 1581 de 2012, Decreto 1377/2013 y régimen Habeas Data; ejercicio de la abogacía / secreto profesional; transferencias internacionales; modelo HITL.  
**No es:** dictamen jurídico vinculante ni certificación SIC. Es auditoría técnico-operativa del producto.

**Veredicto global (actualizado 2026-07-20 noche):** **APTO OPERATIVO CON REMANENTES CONTRACTUALES** — se cerraron en código los gaps P0-1, P1-1/2/4 y documentación P0-3/P1-3/P1-5. Quedan fuera del código: firmas DPA con proveedores y RNBD/SIC (decisión jurídica del despacho).

---

## 1. Resumen ejecutivo

| Dimensión | Estado | Nota |
|-----------|--------|------|
| Transparencia (aviso + autorización casos) | PASS | Páginas 200 en local y prod; policy `2026-07-07` |
| Consentimiento portal auditoría | PASS | Hard gate HTTP 428 + PIN + registro Postgres |
| Consentimiento chat web | WARN | Checkboxes HTML; registro API best-effort (no bloquea login) |
| HITL / no sustituir abogado | PASS | Disclaimer obligatorio; revisión humana en salidas accionables |
| ARCO | WARN | Self-service solo progreso auditoría; chat/expediente vía correo o `/chat/reset` |
| Retención declarada | WARN | 3y auditoría / 5y chat en policy; **sin job de purge** |
| Transferencia internacional | WARN | Declarada (Render US + OpenAI); DPA/encargados no verificables en código |
| Términos de servicio / cookies banner | FAIL/N/A | No hay `/legal/terminos`; cookies solo en aviso |
| WhatsApp | N/A | No implementado |
| Local/dev con datos reales | RIESGO | `DEV_AUTO_LOGIN` y memoria pueden saltar o diluir controles |

---

## 2. Evidencia verificada (2026-07-20)

| Superficie | Resultado |
|------------|-----------|
| `GET /legal/privacidad` (ASGI local) | 200 |
| `GET /legal/tratamiento-datos-casos` (ASGI local) | 200 |
| `GET /api/compliance/policy` (ASGI local) | 200 — versión `2026-07-07`, contacto `privacidad@dbxsolutions.com` |
| Mismas URLs en prod Render | 200 |
| Disclaimer HITL (`apply_output_guardrails`) | Presente: *Borrador informativo — requiere revisión y aprobación del abogado.* |

Archivos clave:

- [`static/legal/privacidad.html`](../../static/legal/privacidad.html)
- [`static/legal/tratamiento-datos-casos.html`](../../static/legal/tratamiento-datos-casos.html)
- [`src/compliance/policy.py`](../../src/compliance/policy.py)
- [`src/gateway/compliance_api.py`](../../src/gateway/compliance_api.py)
- [`src/gateway/audit_portal_api.py`](../../src/gateway/audit_portal_api.py)
- [`src/agents/guardrails.py`](../../src/agents/guardrails.py)

---

## 3. Inventario de datos personales / de caso

| Categoría | Dónde | Sensibilidad |
|-----------|--------|--------------|
| Mensajes de chat | `chat_sessions` | Alta (hechos, víctimas) |
| Expediente | `expedientes` (radicado, partes, etapa) | Alta |
| Borradores HITL | `drafts.contenido` | Alta |
| Trazas / previews | `session_traces.payload` (~900 chars input) | Alta |
| Planes de ejecución | `execution_plans.user_message` | Media–alta |
| RAG chunks | `document_chunks` + embeddings | Alta |
| Consentimientos | `compliance_consent` (email/user, IP, UA) | Media |
| Portal auditoría | progreso, PIN hash, access logs | Media |
| Plazos | `deadlines` | Media |

**Procesadores externos (salida de datos):**

| Destino | Qué sale | Código |
|---------|----------|--------|
| OpenAI | Texto de caso / prompts / embeddings | `runner.py`, `rag.py`, Agents SDK |
| Slack | Cuerpo de borrador (hasta ~2800 chars) + sesión | `hitl/slack_review.py` |
| Twilio | Texto de alerta de plazo (no cuerpo de caso) | `twilio_notify.py` |
| Render (US) | Hosting + Postgres | infraestructura |

---

## 4. Controles existentes alineados a Ley 1581

1. **Información previa:** aviso de privacidad + autorización expresa de datos de casos (incl. sensibles).
2. **Autorización:** checkboxes en login web y gate del portal; registro en `ComplianceConsent` con `policy_version`.
3. **Finalidad limitada:** asistente penal-víctimas + auditoría de instrucciones (declarado).
4. **ARCO / contacto:** `privacidad@dbxsolutions.com`; «Borrar mi progreso» en portal (con archivo previo recuperable).
5. **Seguridad razonable:** `SITE_PASSWORD`, PIN PBKDF2, cookies HttpOnly, rate limit login, headers en prod, OpenAPI off en Render.
6. **Minimización relativa:** disclaimer y “no inventar”; logs de aplicación sin volcar cuerpos de mensaje.
7. **Modelo de servicio jurídico:** IA propone / abogado aprueba (HITL) — reduce riesgo de ejercicio ilegal de la abogacía y de responsabilidad por “sentencia automática”.

---

## 5. Gaps y riesgos (priorizados)

### P0 — cerrar antes de uso intensivo con datos reales de víctimas

| # | Gap | Riesgo legal/operativo | Acción recomendada |
|---|-----|------------------------|--------------------|
| P0-1 | Consentimiento web **no es hard-gate** en servidor: `login.js` no bloquea si falla `/api/compliance/web-consent`; `/auth/login` no exige consentimiento previo | Tratamiento sin autorización demostrable | Exigir consentimiento en backend antes de emitir cookie de sesión (mismo patrón 428 del portal) |
| P0-2 | Transferencia a OpenAI/Render/Slack: declarada, pero **DPA / cláusulas de encargado** no están en el repo | Art. 26 Ley 1581 / transferencias | Firmar y archivar DPA; documentar encargados en el aviso; valorar zero-retention / enterprise OpenAI |
| P0-3 | Local/dev: `DEV_AUTO_LOGIN` y `DATABASE_URL` vacío | Datos reales en laptop sin controles de prod | Política: **prohibido** cargar expedientes reales en dev memoria; usar anonimización |

### P1 — cumplimiento operativo

| # | Gap | Acción |
|---|-----|--------|
| P1-1 | Retención 3y/5y **sin purge automático** | Job (scheduler) que archive/borre según `policy.py` |
| P1-2 | ARCO self-service incompleto (no borra chat/drafts/expediente/traces de un titular) | Endpoint o runbook ARCO unificado + confirmación por `privacidad@` |
| P1-3 | Borrado portal = soft-delete con historial | Definir si el historial cuenta como “supresión” o solo “bloqueo/archivo”; documentar excepción legal |
| P1-4 | Sin página de **Términos de uso** del servicio interno | Añadir `/legal/terminos` (uso exclusivo despacho, no consejo al público, HITL) |
| P1-5 | Slack recibe texto de borradores | Canal privado, retención Slack, DPA Slack; no reenviar a workspaces personales |

### P2 — endurecimiento

| # | Gap | Acción |
|---|-----|--------|
| P2-1 | Sin banner/política de cookies separada | Aceptable si solo cookies esenciales; documentarlo en el aviso |
| P2-2 | Sin cifrado campo a campo en reposo | Evaluar cifrado de `drafts`/`chat` a nivel app o Postgres TDE |
| P2-3 | Sin flag técnico “menor / dato sensible” en expediente | Campo + minimización UI + skill de confidencialidad |
| P2-4 | Copy WhatsApp en reglas vs plan (no implementado) | Alinear reglas a web+Slack únicamente |
| P2-5 | RNBD / bases de datos ante SIC | Evaluar con abogado si la base del despacho debe registrarse (según tipología y rol) |

---

## 6. Matriz normativa (lectura producto)

| Norma / deber | ¿Cubierto en producto? | Comentario |
|---------------|------------------------|------------|
| Ley 1581 — autorización | Parcial | Fuerte en portal; débil en web server-side |
| Ley 1581 — información | Sí | Avisos publicados |
| Ley 1581 — seguridad | Parcial | Controles buenos; retención y ARCO total pendientes |
| Ley 1581 — ARCO | Parcial | Correo + delete progreso; no erase total self-service |
| Transferencia internacional | Declarada | Falta evidencia contractual |
| Secreto profesional | Organizacional + HITL | Depende de proceso y canales |
| No ejercicio ilegal abogacía | Sí (diseño) | Disclaimer + aprobación humana |
| Ley 2300 (contacto) | N/A/bajo | Twilio = alertas transaccionales; WhatsApp off |
| Régimen IA específico CO | N/A | No hay AI Act CO; aplicar 1581 + deontología |

---

## 7. Local vs producción

| Control | Local/dev | Prod (Render) |
|---------|-----------|---------------|
| Páginas legales | Disponibles vía app | 200 OK verificado |
| Consentimiento web | Bypass posible con `DEV_AUTO_LOGIN` | Checkboxes + API best-effort |
| Persistencia | Memoria si no hay `DATABASE_URL` | Postgres |
| OpenAI | Opcional / fallback | Activo → datos salen a US |
| Slack HITL | Solo si hay tokens | Socket Mode (según `/health`) |
| Headers seguridad / HSTS | Limitados | Aplicados en prod |

---

## 8. Checklist de aceptación “listo para despacho”

- [ ] Consentimiento web hard-enforced en `/auth/login`
- [ ] DPA OpenAI + Render + Slack archivados; aviso actualizado si cambia encargado
- [ ] Job de retención/purge alineado a `policy.py`
- [ ] Runbook ARCO end-to-end (chat + drafts + traces + expediente + auditoría)
- [ ] Política escrita: prohibido datos reales de víctimas en laptops/dev
- [ ] Términos de uso internos del servicio
- [ ] Revisión humana obligatoria ya operativa (HITL Slack/web) — **parcialmente hecho**
- [ ] Capacitación corta al equipo sobre no pegar datos de menores sin necesidad

---

## 9. Remediación aplicada (mismo día)

| Gap | Acción en código/docs |
|-----|------------------------|
| P0-1 Consentimiento web | Hard-gate en `/auth/login` (428) + registro server-side |
| P0-2 DPA | Documentado en aviso §9 + runbook (firmas = operación legal) |
| P0-3 Dev datos reales | Runbook + regla global: prohibido en DEV_AUTO_LOGIN/memoria |
| P1-1 Retención | `purge_expired_data` + scheduler mensual + script |
| P1-2 ARCO chat | `POST /api/compliance/arco-erase` + botón ARCO en UI |
| P1-4 Términos | `/legal/terminos` |
| WhatsApp | Regla alineada: no implementado |

## 10. Conclusión

El servicio queda **apto para operación interna del despacho** desde el producto. Remanentes **no automatizables en git**: firmar/archivar DPA con OpenAI/Render/Slack y evaluar RNBD ante SIC con abogado de cumplimiento.

**Próximo paso no-técnico:** checklist DPA trimestral del runbook.
