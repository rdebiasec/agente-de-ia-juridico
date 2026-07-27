# Udemy L09 — Hosted Tools — 2026-07-27

**Fase:** AUDITORIA_ANTES  
**Prioridad:** P1 · Oleada B

---

## 1. Checklist Antes / Después

| Ítem | Antes | Después propuesto | Decisión / por qué | Evidencia |
|---|---|---|---|---|
| WebSearchTool | No usado | **No activar** en prod jurídica | Riesgo de citas/normas inventadas | repo sin matches |
| FileSearchTool | No usado; RAG propio pgvector | Mantener RAG propio | Control de corpus y degradación embeddings | `src/services/rag.py` |
| Code interpreter | No usado | No activar | Sin caso de uso litigante inmediato | — |
| Prefetch RAG | Una vez por turno + tools de fallback | Mantener; no sustituir por hosted | Grounding controlado | `runner.py` |

---

## 2. Relevancia al producto abogado

- El conocimiento legal debe venir de KB/expediente auditables, no de la web abierta.
- Cumple “no inventar sentencias/normas”.

## 3. Qué NO hacer

- No habilitar web search “porque el curso lo muestra”.
- No indexar casos reales de clientes en vector stores de terceros sin DPA.

## 4. PASS / FAIL

| Verificación | PASS | FAIL | Resultado |
|---|---|---|---|
| Hosted tools en código | Cero imports | Aparece WebSearch/FileSearch | PASS (hoy) |
| Grounding degradado | Flag en traza; no inventa | Responde como si hubiera KB | Revalidar |

## 5. Pendiente humano

- Ninguno salvo cambio de premisa de producto.

## 6. Estado tras esta pasada

**Sin cambio de código.** Decisión: hosted tools del curso = **no aplicar** en producción.
