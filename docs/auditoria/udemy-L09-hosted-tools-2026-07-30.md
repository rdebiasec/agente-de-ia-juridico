# Udemy L09 — Hosted Tools — 2026-07-30 (clase formal, profundidad producto)

**Fase:** HECHO_CLASE  
**Orden pedagógico:** #9  
**Decisión global:** DEJAR QUIETO / **no aplicar** hosted tools del curso en prod jurídica  
**Comando código:** ninguno (batch de cambios al final de la serie; L09 no aporta ítem de código)  
**Fuente curso:** `txt/09_hosted_tools.txt` (ok)  
**Auditoría previa:** [`udemy-L09-hosted-tools-2026-07-27.md`](./udemy-L09-hosted-tools-2026-07-27.md)

---

## 0. Veredicto

L09 = herramientas **hospedadas por OpenAI** listas para enchufar al Agent (web, file search, code sandbox, imagen, computer, shell).  
En firma penal-víctimas: **cero** de esas tools en código hoy — y debe seguir así.  
Grounding = KB/expediente propios (`rag.py`, tools de conocimiento), no internet abierta ni vector store de terceros con casos.

---

## 1. Qué enseña el curso (sin omitir)

### Beneficio que vende el curso
Menos TCO operativo: no montás vos la infra de search/sandbox; OpenAI lo opera. Fricción de código casi cero (`tools=[WebSearchTool(), …]`). Las llamadas aparecen en `RunResult.new_items` como cualquier tool.

### Las 6 hosted tools

| Tool | Qué hace | Precio (idea curso) |
|---|---|---|
| Web search | Internet en vivo + citas; context size low/med/high | Por llamadas |
| File search | RAG sobre vector store OpenAI (PDFs); hybrid search + citas | Por llamadas + storage |
| Code interpreter | Sandbox Python; upload/download archivos | Por tiempo de contenedor |
| Image generation | Imágenes (png/webp/jpeg) | Por tokens (incl. conversión pixel) |
| Computer use | Controlar browser (más local; HITL recomendado) | Uso de modelo |
| Shell | CLI en sandbox (hosted o local); runtimes varios; network policies | Por tiempo |

### Patrones cuando hay muchas tools
- **Tool search** — busca semánticamente qué tool usar.  
- **Defer loading** — carga schemas solo al usar.  
Evita saturar context window (cientos de tools → lento, caro, más error).

### Comparación curso: hosted vs function tools
- Hosted = capacidades estándar (search, browser, imagen…).  
- Function tools = APIs propias, DB, lógica de dominio, red privada → **L10**.

### Best practices del curso (resumidas)
Consciente con search context size; compartir vector stores entre agents; no mandar toda la matemática al code interpreter; computer use + HITL; tool search / defer loading si hay muchas tools.

---

## 2. Traducción firma virtual

### Problema de despacho
Si el Gerente “busca en Google” normas o jurisprudencia, el riesgo es **inventar o citar mal** (contra regla: no inventar sentencias/radicados/normas). El abogado necesita fuentes **auditables** (KB del despacho + expediente), no la web abierta.

### Equivalente producto (sin hosted)

| Hosted curso | En esta firma |
|---|---|
| Web search | **No.** Prohibido como grounding jurídico |
| File search OpenAI | RAG propio (`src/services/rag.py`, pgvector) + prefetch por turno + tool KB |
| Code interpreter | No (sin caso litigante inmediato) |
| Image generation | No |
| Computer use / shell | No en el Gerente de chat; sandbox = lecciones L21+ (diferir) |

Evidencia: **cero** imports `WebSearch` / `FileSearch` / hosted equivalentes en `src/`.

### Por qué el consejo “usa hosted para bajar TCO” no aplica aquí
En un SaaS genérico, hosted acelera. En despacho penal:
- citas web = riesgo reputacional/jurídico,  
- PDFs de clientes en vector store OpenAI = DPA / 1581 / datos de casos,  
- shell/computer en el agente cara al abogado = superficie de ataque inaceptable sin diseño sandbox+HITL (más adelante en el curso, y aun así diferible).

---

## 3. High-level

> **Para L09: DEJAR QUIETO / no aplicar.**  
> No actives web_search, file_search hosted, code interpreter, image gen, computer ni shell en el Gerente ni en especialistas de prod.  
> Mantén RAG propio + KB. Los cambios de código de L04/L05/L08 siguen aparcados al batch final de la serie — L09 no añade ítem a ese batch.

| Ítem | Hoy | Recomendación | Prioridad |
|---|---|---|---|
| WebSearchTool | Ausente | No activar | — |
| FileSearch OpenAI | Ausente | RAG propio | — |
| Code / image / computer / shell | Ausente | No en chat firma | — |
| Prefetch RAG + tool KB | Operativo | Mantener | — |
| Tool search / defer loading | N/A (pocas tools, superficie dinámica G1) | Revisar solo si explotan tools (L10+) | P3 |

---

## 4. Desempeño (4 ejes)

| Eje | Efecto de NO aplicar hosted |
|---|---|
| Calidad jurídica | Evita citas web no controladas |
| Costo/ruido | Evita cargos por call/storage/container |
| Confianza abogado | Fuentes = KB/expediente del despacho |
| Latencia | Sin round-trips a search/sandbox hosted |

---

## 5. Mini-laboratorio

| Entrada | Debería | Hoy | Resultado |
|---|---|---|---|
| “¿Qué dice la última sentencia de X en internet?” | No inventar; acotar a KB o pedir fuente del abogado | Sin web_search | PASS (diseño) |
| Pregunta con KB | Fragmentos RAG / tool conocimiento | `rag.py` + runner prefetch | PASS |
| Activar WebSearch “porque L09” | No | Cero imports | PASS |

---

## 6. Qué NO hacer

- No habilitar hosted tools “porque el curso baja el TCO”.  
- No indexar casos reales de clientes en vector stores de terceros sin evaluación/DPA.  
- No sustituir el RAG propio por FileSearch OpenAI.  
- No mezclar computer/shell en el POC de chat.

---

## 7. Encaje pedagógico

L08 inspeccionó tools en el RunResult → L09 serían *otro tipo* de tools (hosted) → **L10** son las tools que sí usáis: function tools + **Agent as tools** (especialistas).

---

## Cierre

- Clase: **HECHO_CLASE**.  
- Código: no.  
- Siguiente: **L10 — Function Tools and Agent as Tools**.
