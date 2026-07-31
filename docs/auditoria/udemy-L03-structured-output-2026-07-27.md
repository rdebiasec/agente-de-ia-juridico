# Udemy L03 — Prompts, Structured Output — 2026-07-27

**Fase:** AUDITORIA_DESPUES  
**Prioridad:** P0 · Oleada A  
**Estado:** HECHO (código + tests)

---

## 1. Checklist Antes / Después

| Ítem | Antes | Después | Decisión / por qué | Evidencia |
|---|---|---|---|---|
| Schemas con `output_type` | 6/10 especialistas | **10/10** especialistas | Contratos JSON → HITL más rápido | `schemas.py`, `orchestrator.py` |
| Sin schema (prosa) | POC + 4 especialistas | Solo **POC** en prosa | Chat = voz de despacho | `build_coordinador_agent` |
| TriageResult | Heurística `triage.py` | Sin cambio | No romper UX conversacional | `triage.py` |
| Render | Cobertura parcial | + ruta 906, víctimas, audiencia, seguimiento | Prosa derivada del schema | `structured_render.py` |
| Schemas nuevos | — | `RutaProcesalLey906`, `RepresentacionVictimas`, `PreparacionAudiencia`, `SeguimientoProcesal` | Prioridad HITL (audiencias/seguimiento ya en HITL_OUTPUT) | `schemas.py` |

---

## 2. Relevancia al producto abogado

- Matrices y dictámenes internos llegan legibles a bandeja/planes.
- Campos opcionales + `pendientes_verificacion` evitan inventar hechos.

## 3. Qué NO hacer (cumplido)

- No se forzó `output_type` en el chat POC.
- Campos core mínimos; listas vacías permitidas (no inventar por schema).

## 4. PASS / FAIL

| Verificación | Resultado |
|---|---|
| `pytest tests/test_l03_structured_output.py` (5) | PASS |
| 10 especialistas con `output_type` | PASS |
| POC sin `output_type` | PASS |
| Render prosa (no JSON dump) | PASS |
| Redactor `BorradorDocumentoPenal` | PASS |

## 5. Pendiente humano

- Ninguno de código. Revisar en desk real que planes de audiencia/seguimiento se lean bien.

## 6. Archivos tocados

- `src/agents/schemas.py`
- `src/agents/orchestrator.py`
- `src/agents/structured_render.py`
- `tests/test_l03_structured_output.py` (nuevo)
- `docs/canon/REGISTRO_UDEMY_REVISIONES.md`
- `docs/canon/CHECKLIST_UDEMY_CIERRE_LECCION.md`
- `docs/canon/plan-udemy-agents-sdk-aplicacion.md`
- `docs/canon/PLAN_UDEMY_CORTO.md`
