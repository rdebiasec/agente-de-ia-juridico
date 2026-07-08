# Plan — Auditoría de contexto por guía operativa (dev)

## Propósito

Completar la auditoría previa a producción: además de los **pasos** numerados, la abogada revisa y aprueba el **contexto** de cada guía operativa (skill).

## Qué audita por guía

| Ítem | Clave en `auditLog.guias` | Fuente canónica |
|------|---------------------------|-----------------|
| Instrucción tipo | `{skill_id}::instruccion` | [`lista-aprobacion-agentes-skills-pasos.md`](lista-aprobacion-agentes-skills-pasos.md) |
| Herramientas | `{skill_id}::tools` | [`agente/skills/<id>/SKILL.md`](../agente/skills/) (sección Tools) |
| Guardrails de la guía | `{skill_id}::guardrails` | `SKILL.md` (sección Guardrails) |
| Pasos operativos | `{skill_id}::{num}` | Lista de aprobación (sin cambio) |

**No confundir:** las **8 reglas estrictas** del panel superior son globales. Los **guardrails de la guía** son límites específicos del skill atómico.

## Reglas de gobernanza

1. El portal **muestra** texto del build; **no edita** `SKILL.md` ni la lista de aprobación.
2. La IA propone; la abogada **Aprueba**, **Ajusta** (con razón y solución) o **Restablece**.
3. El dictamen exportado (.MD) incluye estados de contexto y pasos.
4. Persistencia: servidor por correo + caché local `legal-audit-sync-v4`.

## Criterio de cierre (solo dev)

- [ ] `python scripts/generar_audit_portal.py` genera `audit-data.json` v2.1 con 684 ítems auditable.
- [ ] Portal local: guía expandible permanece abierta al aprobar contexto.
- [ ] Export .MD incluye fila «Contexto de guías».
- [ ] `pytest tests/test_audit_skill_context.py` en verde.
- [ ] Smoke login en `http://127.0.0.1:8000/auditoria/`.

**Producción (GitHub Pages):** desplegar solo tras checklist dev y aprobación del despacho.

## Fuera de alcance (esta fase)

- Inyectar pasos aprobados en el prompt del chat (`plan_executor.py`).
- Auditar cada herramienta como ítem separado (se audita el bloque completo).
