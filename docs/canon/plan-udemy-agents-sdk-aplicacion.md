# Plan Udemy → Agente jurídico (tablero maestro)

**Fecha apertura:** 2026-07-27  
**Curso:** Mastering Agents with OpenAI Agents SDK & OpenAI Codex (28 lecciones)  
**Fuente transcripts (gitignored):** `documentos/udemy_transcripts/mastering_agents_openai_sdk_codex/`  
**Producto:** firma virtual — [`ESTADO_PROYECTO.md`](../../agente/fases/ESTADO_PROYECTO.md), [`plan-rediseno-firma.md`](./plan-rediseno-firma.md)

## Premisas aprobadas

| Premisa | Valor |
|---|---|
| Curso | Solo este (Agents SDK + Codex) |
| Modo | Lección por lección; código solo tras «aprobado, ejecuta» de esa lección |
| Arquitectura fija | `coordinador_expediente_penal` = única voz; especialistas = `Agent.as_tool`; sin handoffs peer |
| HITL | La IA propone; el abogado aprueba |
| Material Udemy | No se publica ni se commitea |

## Prompt maestro (reutilizar por lección)

```text
Rol: ingeniero del producto «agente de IA jurídico» (firma virtual, Colombia, víctimas/penal).

Fuente curso (solo lectura, no publicar):
- documentos/udemy_transcripts/mastering_agents_openai_sdk_codex/
  INDEX.txt, KB_LESSONS_FAQ.md, txt/NN_*.txt de la lección activa.

Fuente producto (obligatoria):
- agente/fuente/GUIA_PROYECTO_AGENTE_JURIDICO.md
- agente/requisitos/requisitos_asistente.json
- agente/fases/ESTADO_PROYECTO.md
- docs/canon/plan-rediseno-firma.md
- Arquitectura fija: coordinador_expediente_penal = única voz;
  especialistas = Agent.as_tool (NO handoffs peer);
  HITL: la IA propone, el abogado aprueba; no inventar normas/sentencias/radicados.

Modo: lección {NN} — {título}.
Fase actual: {MAPEO | AUDITORIA_ANTES | IMPLEMENTACION | AUDITORIA_DESPUES}.
No escribas código ni edites archivos hasta que diga explícitamente «aprobado, ejecuta».

Entrega obligatoria en cada turno de lección:
1) Checklist Markdown con columnas: Ítem | Antes | Después propuesto | Decisión/por qué | Prioridad (P0/P1/P2/Diferido) | Evidencia (ruta de archivo).
2) Relevancia al producto abogado: qué mejora para el litigante (calidad, riesgo, HITL, costo, UX).
3) Qué NO hacer (anti-patrones del curso o del lab que romperían firma virtual / 1581).
4) Plan de prueba PASS/FAIL mínimo.
5) Actualización propuesta de la fila L{NN} en docs/canon/plan-udemy-agents-sdk-aplicacion.md.

Restricciones:
- No activar WhatsApp/voz sin evaluación 1581/2300.
- No migrar a Bedrock/Sandbox solo porque el curso lo enseña.
- No commitear secretos ni transcripts Udemy.
- Cambios mínimos y alineados a Oleada A/B; Oleada C solo documental.
```

## Flujo

1. Elegir siguiente lección P0/P1 pendiente de implementación.  
2. Pegar prompt maestro con `{NN}` y fase.  
3. Revisar checklist Antes → aprobar con «aprobado, ejecuta».  
4. Implementar → AUDITORIA_DESPUES + PASS/FAIL.  
5. Actualizar esta tabla y, si aplica, `ESTADO_PROYECTO.md`.

Plantilla por lección: [`docs/auditoria/PLANTILLA_udemy-leccion.md`](../auditoria/PLANTILLA_udemy-leccion.md).

---

## Tablero L01–L28

Leyenda estado checklist: `Diferido` · `MAPEO_OK` · `AUDITORIA_ANTES` · `PEND_IMPL` · `HECHO`

### Oleada A — P0 (calidad despacho / runtime)

| Lección | Estado producto hoy | Acción propuesta | Prioridad | Estado checklist | Decisión / por qué | Evidencia |
|---|---|---|---|---|---|---|
| L03 Prompts, Structured Output | 6/10 especialistas con `output_type`; POC en prosa; 4 especialistas en texto libre | Cerrar schemas faltantes de alto valor; mantener prosa en chat POC | P0 | AUDITORIA_ANTES | Structured output mejora HITL; chat en prosa es UX deliberada | [`udemy-L03-structured-output-2026-07-27.md`](../auditoria/udemy-L03-structured-output-2026-07-27.md) |
| L04 Model Settings | Modelo high-risk vs default; sin `ModelSettings` (temp/reasoning) | Perfiles `ModelSettings` por rol de riesgo | P0 | AUDITORIA_ANTES | Determinismo jurídico y costo por criticidad | [`udemy-L04-model-settings-2026-07-27.md`](../auditoria/udemy-L04-model-settings-2026-07-27.md) |
| L05 RunContext | ContextVar + inyección prompt; no `context=` tipado en `Runner.run` | Dataclass tipada (expediente, canal, flags 1581) vía `context=` | P0 | AUDITORIA_ANTES | Anti-IDOR y grounding sin secretos en prompt | [`udemy-L05-runcontext-2026-07-27.md`](../auditoria/udemy-L05-runcontext-2026-07-27.md) |
| L08 RunResult y REPL | Inspección parcial en `runner.py` + Workflow Trace UI | Checklist smoke RunResult; exponer más items en soporte | P0 | AUDITORIA_ANTES | Debug reproducible para ops/abogado | [`udemy-L08-runresult-2026-07-27.md`](../auditoria/udemy-L08-runresult-2026-07-27.md) |
| L10 Function tools y as_tool | Patrón canónico ya en `orchestrator.py` | Auditoría nombres/descripciones/fallos/topes; hardening menor | P0 | AUDITORIA_ANTES | Refuerza arquitectura firma virtual (no handoffs) | [`udemy-L10-as-tool-2026-07-27.md`](../auditoria/udemy-L10-as-tool-2026-07-27.md) |
| L11 Guardrails y Human Review | Guardrails SDK + HITL; fallo de draft silencioso | Fallo HITL visible; `invention_suspect`; test loop draft | P0 | HECHO | Hardening real del loop de revisión humana | [`udemy-L11-guardrails-hitl-2026-07-27.md`](../auditoria/udemy-L11-guardrails-hitl-2026-07-27.md) |
| L17 Monitoring | Trazas propias + OpenAI traces; Sentry opcional básico | Completar scrubbing PII, métricas tripwire/costo, alerting | P0 | AUDITORIA_ANTES | Operación despacho sin adivinar fallos | [`udemy-L17-monitoring-2026-07-27.md`](../auditoria/udemy-L17-monitoring-2026-07-27.md) |

### Oleada B — P1 (sesiones / orquestación / tools)

| Lección | Estado producto hoy | Acción propuesta | Prioridad | Estado checklist | Decisión / por qué | Evidencia |
|---|---|---|---|---|---|---|
| L07 Run Loop | Chat async no streaming; SSE solo en planes aprobados | Evaluar streaming chat vs costo/complejidad; documentar decisión | P1 | AUDITORIA_ANTES | UX abogado vs latencia percibida | [`udemy-L07-run-loop-2026-07-27.md`](../auditoria/udemy-L07-run-loop-2026-07-27.md) |
| L12 Session Management | `RepositoryAgentSession` + compactación | Revisar límites compactación y contaminación cruzada | P1 | AUDITORIA_ANTES | Continuidad multi-turno del expediente | [`udemy-L12-sessions-2026-07-27.md`](../auditoria/udemy-L12-sessions-2026-07-27.md) |
| L13 Sessions Production | Postgres `chat_sessions`; idle 60 min solo en UI; stale de planes 300s | Endurecer lifecycle (idle server-side / retención 1581) | P1 | AUDITORIA_ANTES | Durabilidad y cumplimiento | [`udemy-L13-sessions-prod-2026-07-27.md`](../auditoria/udemy-L13-sessions-prod-2026-07-27.md) |
| L14 Handoffs y orquestación | Sin `handoffs=`; orquestación por planes/templates | Adaptar lección: documentar por qué no se copian handoffs peer | P1 | AUDITORIA_ANTES | Preservar una voz de despacho | [`udemy-L14-L16-handoffs-adaptado-2026-07-27.md`](../auditoria/udemy-L14-L16-handoffs-adaptado-2026-07-27.md) |
| L16 Lab multi-agents | Labs del curso usan handoffs + as_tool | Solo adaptar trazabilidad/ownership; no portar lab | P1 | AUDITORIA_ANTES | Misma decisión que L14 | [`udemy-L14-L16-handoffs-adaptado-2026-07-27.md`](../auditoria/udemy-L14-L16-handoffs-adaptado-2026-07-27.md) |
| L09 Hosted Tools | Cero hosted tools; RAG propio pgvector | Mantener **sin** web_search libre; no FileSearch hosted | P1 | AUDITORIA_ANTES | Evitar citas normativas inventadas | [`udemy-L09-hosted-tools-2026-07-27.md`](../auditoria/udemy-L09-hosted-tools-2026-07-27.md) |
| L15 MCP | `src/mcp/tools.py` = function tools, no servidor MCP | Auditar naming/contrato; no expandir sin caso de uso | P1 | AUDITORIA_ANTES | Interop sin complejidad gratuita | [`udemy-L15-mcp-2026-07-27.md`](../auditoria/udemy-L15-mcp-2026-07-27.md) |

### Oleada C — diferidas (solo documental)

| Lección | Estado producto hoy | Acción propuesta | Prioridad | Estado checklist | Decisión / por qué | Evidencia |
|---|---|---|---|---|---|---|
| L01 Overview OpenAI Agents | Stack productivo ya en marcha; caption L01 inválida en fuente | Baseline documental; no rehacer overview | Diferido | Diferido | Entorno y arquitectura ya existen; caption rota | [`udemy-oleada-C-diferidos-2026-07-27.md`](../auditoria/udemy-oleada-C-diferidos-2026-07-27.md) |
| L02 Lab Setup Codex + API Key | API key + Render/local operativos | No rehacer lab de setup | Diferido | Diferido | Setup ya cerrado en prod | mismo |
| L06 Lab Basic Agents | Sin caption URL en Udemy | Cubrir con L03+L05+código actual | Diferido | Diferido | Gap de fuente, no de producto | mismo |
| L18 Realtime Voice | No hay canal voz | No implementar | Diferido | Diferido | Voz ≈ canal sensible; 1581/2300 | mismo |
| L19 Chained Voice | No aplica | No implementar | Diferido | Diferido | Idem L18 | mismo |
| L20 Lab Voice | No aplica | No implementar | Diferido | Diferido | Idem L18 | mismo |
| L21 Sandbox Agents | Runtime = Render, no sandbox OpenAI | No adoptar sandbox como runtime | Diferido | Diferido | Fuera del hosting actual | mismo |
| L22 SandboxRunConfig / Manifest | No aplica | Mapear idea de capabilities a guardrails/tools existentes (doc) | Diferido | Diferido | Gobernanza ya vía G1–G10 + tool guardrails | mismo |
| L23 Sandbox Provider / Credentials | Secrets en env Render | No montar sandbox credentials | Diferido | Diferido | Modelo de secretos ya definido | mismo |
| L24 AGENTS.md, Skills, Sandbox Memory | Catálogo `agente/skills` + prompts versionados | No portar AGENTS.md de sandbox; skills propios son la fuente | Diferido | Diferido | Equivalente de producto ya existe | mismo |
| L25 Sandbox State / Composition | Ledger expediente + planes | No sandbox state | Diferido | Diferido | Estado vive en Postgres/ledger | mismo |
| L26 Lab SandboxAgents | No aplica | No portar lab | Diferido | Diferido | Runtime distinto | mismo |
| L27 Lab SQL Analyzer | No aplica | No portar lab SQL sandbox | Diferido | Diferido | Sin caso de uso abogado inmediato | mismo |
| L28 Bonus AWS Bedrock AgentCore | Hosting Render | No migrar | Diferido | Diferido | Bedrock no es el target de deploy | mismo |

---

## Orden de implementación (cuando digas «aprobado, ejecuta»)

1. **L11 → L10 → L03 → L05 → L04 → L17 → L08** (Oleada A)  
2. **L12/L13 → L07 → L14/L16 (solo adaptaciones) → L09/L15** (Oleada B)  
3. Oleada C permanece `Diferido` salvo cambio de premisa de producto.

## Criterio de éxito

No es “terminar el curso”. Es: cada patrón del SDK que mejore completitud, HITL, structured output, guardrails, sesiones Postgres, trazas y `as_tool` queda **aplicado** o **diferido con razón**, con checklist Antes/Después.
