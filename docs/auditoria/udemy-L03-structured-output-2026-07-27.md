# Udemy L03 — Prompts, Structured Output — 2026-07-27

**Fase:** AUDITORIA_ANTES  
**Prioridad:** P0 · Oleada A

---

## 1. Checklist Antes / Después

| Ítem | Antes | Después propuesto | Decisión / por qué | Evidencia |
|---|---|---|---|---|
| Schemas con `output_type` | Cronología, tipicidad, evidencia, redactor, tutela, calidad | Mantener + ampliar a especialistas aún en prosa si aportan HITL | Contratos JSON → revisión humana más rápida | `src/agents/schemas.py`, `orchestrator.py` |
| Sin schema (prosa) | POC/coordinador; ruta 906; víctimas; audiencias; seguimiento | **Mantener prosa en POC**; valorar schemas parciales en los 4 restantes | Chat debe leerse como despacho, no como JSON crudo | `build_coordinador_agent` |
| TriageResult | Existe pero no es `output_type` del chat | Seguir heurística `triage.py` salvo prueba clara de ganancia | Evitar romper UX conversacional | `schemas.py`, `triage.py` |
| Render | `render_structured_output` para as_tool | Extender cobertura a nuevos schemas | HITL y planes necesitan prosa derivada del schema | `structured_render.py` |
| Prompts como contrato | Prompts en `agente/prompts/` + G1–G10 | Auditar anti-patrones: ownership mixto, nombres duplicados | Lección enfatiza contratos claros | `prompt_assembly.py` |

---

## 2. Relevancia al producto abogado

- Menos alucinación de *forma* en borradores y matrices.
- Dictámenes de calidad más accionables en bandeja HITL.

## 3. Qué NO hacer

- No forzar `output_type` en el chat POC (rompe voz de despacho).
- No inventar campos jurídicos “porque el schema lo pide” sin evidencia en expediente.

## 4. PASS / FAIL

| Verificación | PASS | FAIL | Resultado |
|---|---|---|---|
| Redactor | `BorradorDocumentoPenal` válido | Texto libre sin schema | Ya existe; revalidar |
| Nuevo schema (si se añade) | Render + plan step OK | Plan rompe | Pendiente impl |

## 5. Pendiente humano

- Priorizar cuáles de los 4 especialistas en prosa merecen schema primero.
- «aprobado, ejecuta» L03 para implementación.

## 6. Estado tras esta pasada

**Sin cambio de código.** Gap principal documentado: 4 especialistas + TriageResult.
