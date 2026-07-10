# Checkpoint — pausa para auditoría humana

**Fecha:** 2026-07-09 19:54 (UTC-5)  
**Estado:** **PAUSA ACTIVA** — no más cambios de producto ni despliegues hasta que la abogada termine su revisión.

---

## Commit congelado (local = prod)

| Campo | Valor |
|-------|-------|
| SHA | `5aebc42f5e79776b7227665977df24543dd050e4` |
| Mensaje | docs(auditoria): dictamen pre-producción y validación 5 capas PASS |
| Rama | `main` (pusheado a `origin/main`) |

---

## URLs

| Entorno | URL |
|---------|-----|
| **Local (auditoría abogada)** | http://127.0.0.1:8000/auditoria/ |
| Local chat | http://127.0.0.1:8000/abogado |
| Render | https://agente-de-ia-juridico.onrender.com/auditoria/ |
| GitHub Pages | https://rdebiasec.github.io/agente-de-ia-juridico/ |

**Recomendación:** la abogada audita en **local** mientras dura la pausa. Render tiene el mismo código y catálogo; la base de datos de progreso es independiente por entorno.

---

## Catálogo (paridad verificada)

| Métrica | Local API | Render API | dist estático |
|---------|----------:|-----------:|--------------:|
| Reglas (guardrails) | 10 | 10 | 10 |
| Agentes | 11 | 11 | 11 |
| Skills | 90 | 90 | 90 |
| Pasos | 402 | 402 | 402 |
| Contextos guía | 270 | 270 | 270 |
| Ítems auditables | 693 | 693 | 693 |

---

## Validación técnica en este checkpoint

| Prueba | Resultado | Evidencia |
|--------|-----------|-----------|
| 5 capas local (Postgres) | **PASS** | [`validacion-sistema-completa-reporte.md`](validacion-sistema-completa-reporte.md) — 2026-07-09 19:52 |
| Smoke manual local | **9/10** | health, login audit, 10 reglas, agentes, skill ejemplo, chat+trace |
| Smoke prod automatizado | **PASS 8/8** | [`smoke-produccion-reporte.md`](smoke-produccion-reporte.md) — 2026-07-09 19:54 |
| Paridad pre/post push | **OK** | Conteos idénticos local = Render |

**Nota smoke manual:** `inventariar_evidencia` incluye **g9** en guardrails de la guía; **g10** aplica como regla global (panel de 10 reglas).

---

## Configuración operativa publicada

| Archivo | Estado |
|---------|--------|
| `data/audit/approved-skill-config.json` | **No existe** (correcto — aún no hay publicación) |

---

## Qué debe hacer la abogada (cuando retomen)

1. `./scripts/start-local.sh` (si el servidor no está corriendo).
2. Entrar en http://127.0.0.1:8000/auditoria/ — correo + `SITE_PASSWORD` + PIN.
3. Revisar y marcar:
   - **10 reglas estrictas** (globales g1–g10)
   - **11 agentes**
   - **90 skills** (instrucción, tools, guardrails por guía)
   - **402 pasos** (y contextos de guía si aplica alcance completo)
4. Exportar dictamen `.MD` desde el portal.
5. Cuando **todos** los ítems exigidos estén APROBADO → **Publicar configuración**.

**Mínimo operativo sugerido (opción B del dictamen):** 10 reglas + 11 agentes + skills críticos; publicar solo si el botón lo permite (requiere todo APROBADO según regla actual del portal).

---

## Qué NO hacer durante la pausa

- No modificar `SKILL.md`, matriz de pasos ni catálogo sin coordinación.
- No `git push` a `main` salvo emergencia acordada.
- No publicar configuración desde dev sin revisión completa.
- No declarar GO operativo sin dictamen de la abogada + 3 pruebas chat documentadas.

---

## Cómo retomar (después de la abogada)

1. Revisar export `.MD` y progreso en Postgres (correo de la abogada).
2. Si hay AJUSTAR con solución → aplicar en fuentes canónicas → regenerar portal → nueva validación técnica.
3. Publicar configuración cuando corresponda.
4. 3 consultas chat reales con revisión humana.
5. Reunión GO operativo / CONDICIONAL / NO-GO.

---

## Referencias

- [dictamen-pre-produccion-7-expertos.md](dictamen-pre-produccion-7-expertos.md)
- [baseline-pre-produccion-2026-07-08.md](baseline-pre-produccion-2026-07-08.md)
