# Reporte — Validación extensa del sistema (2026-07-07 19:16)

## Resumen ejecutivo

**Resultado global: FAIL** — 1 capa(s) con error.

| Capa | Estado | Duración (s) |
|------|--------|-------------:|
| Capa 1 — Skills 7-expertos | OK | 2 |
| Capa 2 — Gates estáticos | OK | 0 |
| Capa 3 — Pytest suite | FAIL | 20 |

### Skills 7-expertos (Capa 1)

Veredictos: `{'APROBADO': 90}`
Detalle: [validacion-7-expertos-reporte.md](validacion-7-expertos-reporte.md)

## Reglas de negocio verificadas

| Regla | Verificación |
|-------|--------------|
| Tutela solo tras evaluador | Cadenas + test_sistema_runtime |
| Ruta 906 no redacta recursos | SKILL.md + cadenas |
| HITL cliente / salidas | compliance + smoke audit |
| IA propone; abogado aprueba | guardrails skills + HITL tests |

## Riesgos residuales

1. LLM real no probado en esta validación (routing determinista).
2. Slack sin token en entorno local.
3. REQ-001…050 sin checklist formal automatizado.
4. Smoke solo local (sin producción Render).
5. 10 skills mono-agente sin sección Rol en (aceptable si atómicos).

## Repetir validación

```bash
./scripts/validacion_sistema_completa.sh
```

## Detalle por capa

### Capa 1 — Skills 7-expertos
```
OK: /Users/ricardodebiase/Documents/agente de IA juridico/docs/auditoria/validacion-7-expertos-baseline.md
OK: /Users/ricardodebiase/Documents/agente de IA juridico/docs/auditoria/validacion-7-expertos-reporte.md
OK: /Users/ricardodebiase/Documents/agente de IA juridico/docs/auditoria/validacion-7-expertos-data.json
Veredictos: {'APROBADO': 90}
```

### Capa 2 — Gates estáticos
```
OK: firma virtual (A+B) — 50 REQ, persona, KB, agentes, esquemas, persistencia, HITL y servicios presentes.
CHECK OK: 90 skills + matriz variable validada
  auth: login vía API /api/audit (auth-config.js legacy desactivado)
  api: mismo origen (AUDIT_API_BASE vacío → /api/audit en el servidor)
OK: /Users/ricardodebiase/Documents/agente de IA juridico/audit-portal/dist — 10 reglas, 11 agentes, 402 pasos (693 items auditable)
Espejo OK: 90 SKILL.md sincronizados
```

### Capa 3 — Pytest suite
```
tests/test_trace_workflow.py::test_debug_trace_returns_session_history
  /Users/ricardodebiase/Documents/agente de IA juridico/.venv/lib/python3.13/site-packages/httpx/_client.py:1859: DeprecationWarning: Setting per-request cookies=<...> is being deprecated, because the expected behaviour on cookie persistence is ambiguous. Set cookies directly on the client instance instead.
    return await self.request(

tests/test_access_control.py::test_plan_bola_blocks_cross_subject
tests/test_conversation.py::test_expediente_sync_from_tutela_message
tests/test_conversation.py::test_repository_agent_session_roundtrip
  /Users/ricardodebiase/Documents/agente de IA juridico/.venv/lib/python3.13/site-packages/alembic/config.py:612: DeprecationWarning: No path_separator found in configuration; falling back to legacy splitting on spaces, commas, and colons for prepend_sys_path.  Consider adding path_separator=os to Alembic config.
    util.warn_deprecated(

tests/test_access_control.py: 4 warnings
tests/test_auth.py: 5 warnings
tests/test_compliance.py: 1 warning
tests/test_trace_workflow.py: 2 warnings
  /Users/ricardodebiase/Documents/agente de IA juridico/.venv/lib/python3.13/site-packages/httpx/_client.py:1768: DeprecationWarning: Setting per-request cookies=<...> is being deprecated, because the expected behaviour on cookie persistence is ambiguous. Set cookies directly on the client instance instead.
    return await self.request(

tests/test_compliance.py::test_audit_progress_history_and_isolation
  /Users/ricardodebiase/Documents/agente de IA juridico/.venv/lib/python3.13/site-packages/httpx/_client.py:1896: DeprecationWarning: Setting per-request cookies=<...> is being deprecated, because the expected behaviour on cookie persistence is ambiguous. Set cookies directly on the client instance instead.
    return await self.request(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_fase3_plan_product.py::test_audit_clear_execution_plans - a...
1 failed, 155 passed, 1 skipped, 7 deselected, 24 warnings in 18.07s
```

