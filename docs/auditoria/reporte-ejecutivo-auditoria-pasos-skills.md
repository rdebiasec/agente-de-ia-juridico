# Reporte ejecutivo — Auditoría gerencial de pasos por skill (v2)

**Fecha:** 2026-07-05  
**Alcance:** 90 skills · pasos **variables** (mín. 2, sin tope máximo)  
**Fuente:** `scripts/lib/pasos_gerencia_matrix.py` → `docs/canon/lista-aprobacion-agentes-skills-pasos.md`

---

## Resumen

| Concepto | Antes (plantilla 4) | Después (matriz v2) |
|---|---:|---:|
| Skills | 90 | 90 |
| **Pasos totales** | 360 | **404** |
| Pasos por skill (único valor) | 4 fijos | **9 tallas distintas** (2–10) |

**No se creó ni eliminó ningún skill.** Solo cambió la **cantidad y el contenido** de los pasos por skill.

---

## Histograma — pasos por skill (propuesta gerencia v2)

| Pasos/skill | Nº skills |
|---:|---:|
| 2 | 4 |
| 3 | 7 |
| 4 | 49 |
| 5 | 16 |
| 6 | 6 |
| 7 | 4 |
| 8 | 2 |
| 9 | 1 |
| 10 | 1 |

**Total:** 404 pasos auditable en portal (8 reglas + 11 agentes + 404 pasos = **423 ítems**).

---

## Skills atómicos (2 pasos: 1 operativo + HITL)

- `marcar_pendientes_verificacion`
- `monitorear_radicado`
- `actualizar_tareas_responsable`
- `registrar_actuacion_procesal`

---

## Skills críticos con más pasos (gerencia)

| Skill | Pasos | Tier |
|---|---:|---|
| `redactar_tutela_penal_preliminar` | 10 | crítico |
| `evaluar_procedencia_tutela` | 9 | crítico |
| `preparar_guion_intervencion_oral` | 8 | crítico |
| `detectar_riesgo_improcedencia_tutela` | 8 | crítico |

Cada skill incluye **reasoning gerencial** en `docs/auditoria/auditoria-pasos-skills-gerencia-penal.md`.

---

## Reglas aplicadas

- HITL siempre como **último paso** explícito.
- Sin tope máximo de pasos; sin uniformidad artificial.
- Matriz validada: `python scripts/lib/pasos_gerencia_matrix.py`
- Catálogo: `python scripts/auditar_pasos_skills_gerencia.py --check` → OK

---

## Comandos de mantenimiento

```bash
# Reconstruir matriz tras editar tiers en _build_pasos_matrix.py
python3 scripts/_build_pasos_matrix.py

# Auditar, aplicar y regenerar documentos + portal
python3 scripts/auditar_pasos_skills_gerencia.py --apply --regenerar
```

---

*Auditoría detallada: [`auditoria-pasos-skills-gerencia-penal.md`](auditoria-pasos-skills-gerencia-penal.md)*
