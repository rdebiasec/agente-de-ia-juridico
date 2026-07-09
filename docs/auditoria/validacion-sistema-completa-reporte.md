# Reporte — Validación extensa del sistema (2026-07-09 16:41)

## Resumen ejecutivo

**Resultado global: PASS** — todas las capas completadas.

| Capa | Estado | Duración (s) |
|------|--------|-------------:|
| Capa 1 — Skills 7-expertos | OK | 2 |
| Capa 2 — Gates estáticos | OK | 1 |
| Capa 3 — Pytest suite | OK | 15 |
| Capa 4 — Runtime | OK | 2 |
| Capa 5 — Smoke HTTP local | OK | 6 |

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
    return await self.request(

tests/test_compliance.py::test_audit_progress_history_and_isolation
  /Users/ricardodebiase/Documents/agente de IA juridico/.venv/lib/python3.13/site-packages/httpx/_client.py:1896: DeprecationWarning: Setting per-request cookies=<...> is being deprecated, because the expected behaviour on cookie persistence is ambiguous. Set cookies directly on the client instance instead.
    return await self.request(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
157 passed, 1 skipped, 7 deselected, 24 warnings in 14.79s
```

### Capa 4 — Runtime
```
................                                                         [100%]
16 passed in 0.87s
```

### Capa 5 — Smoke HTTP local
```
tests/test_smoke_local.py::test_login_page PASSED                        [ 28%]
tests/test_smoke_local.py::test_auditoria_static_has_auth_gate PASSED    [ 42%]
tests/test_smoke_local.py::test_audit_login_and_progress PASSED          [ 57%]
tests/test_smoke_local.py::test_audit_catalog_live PASSED                [ 71%]
tests/test_smoke_local.py::test_web_chat_with_trace PASSED               [ 85%]
tests/test_smoke_local.py::test_chat_plan_flow PASSED                    [100%]

============================== 7 passed in 3.86s ===============================
```

