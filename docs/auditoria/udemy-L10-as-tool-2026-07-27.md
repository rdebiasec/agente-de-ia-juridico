# Udemy L10 — Function Tools and Agent as Tools — 2026-07-27

**Fase:** AUDITORIA_DESPUES  
**Prioridad:** P0 · Oleada A  
**Estado:** HECHO (código + tests)

---

## 1. Checklist Antes / Después

| Ítem | Antes | Después | Decisión / por qué | Evidencia |
|---|---|---|---|---|
| Patrón manager-specialist | Coordinador + 10 `as_tool` | Mantener; sin handoffs peer | Arquitectura canónica firma virtual | `orchestrator.py` `build_orchestrator` |
| Naming / descriptions | Textos genéricos | Skill primario + «Usar / No usar» por especialista | Mejor routing del Gerente | `_SPECIALIST_TOOL_DESCRIPTIONS` |
| Failure path | Mensaje genérico + `type(error).__name__` | Códigos tipados (`max_turns`, `tool_timeout`, …) sin stack/PII; tripwires/budget re-lanzan | Abogado/soporte ven fallo claro | `_as_tool_failure_error` |
| Nested max turns | Overrides por agente | Overrides + techo duro `_NESTED_MAX_TURNS_CEILING=8` | Evita loops caros | `nested_max_turns_for` |
| needs_approval | HIGH_RISK = redactor + tutela | Confirmado + export `APPROVAL_REQUIRED_TOOL_IDS` | HITL en tools de alto riesgo | `skill_catalog.HIGH_RISK_AGENTS` |
| Pruebas | Solo phase2 parcial | `tests/test_l10_as_tool.py` (6) | Cierre verificable | tests |

---

## 2. Relevancia al producto abogado

- El Gerente elige mejor al equipo interno (menos llamadas erróneas).
- Fallos tipados sin stack mejoran confianza del despacho.
- Alto riesgo (memorial/tutela) sigue exigiendo aprobación en chat.

## 3. Qué NO hacer (cumplido)

- No se reemplazó `as_tool` por handoffs peer.
- No se subió `max_turns` sin techo.

## 4. PASS / FAIL

| Verificación | Resultado |
|---|---|
| `pytest tests/test_l10_as_tool.py` (6) | PASS |
| Especialista falla → mensaje sanitizado (sin Traceback/ruta) | PASS |
| Alto riesgo `needs_approval=True` (redactor/tutela) | PASS |
| POC sin `handoffs=` | PASS |
| Descriptions incluyen skill primario + Usar/No usar | PASS |

## 5. Pendiente humano

- Ninguno de código. Ops: seguir usando planes HITL para redacción/tutela en flujo aprobado.

## 6. Archivos tocados

- `src/agents/orchestrator.py`
- `tests/test_l10_as_tool.py` (nuevo)
- `docs/canon/CHECKLIST_UDEMY_CIERRE_LECCION.md`
- `docs/canon/plan-udemy-agents-sdk-aplicacion.md`
- `docs/canon/PLAN_UDEMY_CORTO.md`
