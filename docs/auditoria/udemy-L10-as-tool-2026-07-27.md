# Udemy L10 — Function Tools and Agent as Tools — 2026-07-27

**Fase:** AUDITORIA_ANTES  
**Prioridad:** P0 · Oleada A

---

## 1. Checklist Antes / Después

| Ítem | Antes | Después propuesto | Decisión / por qué | Evidencia |
|---|---|---|---|---|
| Patrón manager-specialist | Coordinador + 10 `as_tool` | Mantener; no introducir handoffs peer | Ya es la arquitectura canónica del curso adaptada a firma | `src/agents/orchestrator.py` `build_orchestrator` |
| Naming / descriptions | `tool_name=agent.name` + `_SPECIALIST_TOOL_DESCRIPTIONS` | Revisar textos vs skills reales; alinear con catálogo | Mejor routing → menos llamadas incorrectas | mismo |
| Failure path | `_as_tool_failure_error` sanitiza; re-lanza budgets/tripwires | Ampliar mensajes tipados para soporte | Abogado ve fallo claro, no stack | mismo |
| Nested max turns | Overrides por agente + `settings.agent_nested_max_turns` | Validar en smoke costos/timeouts | Evita loops caros en especialistas | `config.py`, `_NESTED_MAX_TURNS_BY_AGENT` |
| needs_approval | HIGH_RISK agents | Confirmar lista = redactor/tutela/etc. | HITL en tools de alto riesgo | `orchestrator.py` |

---

## 2. Relevancia al producto abogado

- Escala la firma sin exponer caras de especialistas al chat.
- Fallos tipados mejoran confianza del despacho.

## 3. Qué NO hacer

- No reemplazar `as_tool` por handoffs peer “porque el lab L16 lo hace”.
- No subir `max_turns` sin presupuesto de tokens.

## 4. PASS / FAIL

| Verificación | PASS | FAIL | Resultado |
|---|---|---|---|
| Especialista falla | Mensaje sanitizado al chat | Stack/trace al usuario | Pendiente revalidar |
| Alto riesgo | Interruption / HITL | Auto-ejecuta | Pendiente revalidar |

## 5. Pendiente humano

- «aprobado, ejecuta» L10 si se piden ajustes de descripciones/topes.

## 6. Estado tras esta pasada

**Sin cambio de código.** Arquitectura alineada con el curso; trabajo restante = hardening de contratos de tools.
