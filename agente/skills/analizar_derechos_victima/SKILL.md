<!-- config-version: 4; checksum: 3ba0fa4951959ebe -->
---
name: analizar-derechos-victima
description: Contrato penal-víctimas: Mapear derechos de la víctima en el proceso penal (participación, información, reparación, protección) y su vínculo con los hechos. Activar cuando el plan/HITL o el especialista requiera `analizar_derechos_victima`. No sustituye a `identificar_interese...
disable-model-invocation: true
---

# analizar_derechos_victima

## Scope
- Category: `Skills de representacion de victimas`
- Skill ID: `analizar_derechos_victima`
- Tier: `operativo`

## Used By Agents
- `analista_representacion_victimas`

## Purpose
Mapear derechos de la víctima en el proceso penal (participación, información, reparación, protección) y su vínculo con los hechos.

## Rol en analista_representacion_victimas
Insumo para teoría del caso y plan de actuación ordinaria Ley 906.

## Fuentes KB
- `agente/conocimiento/normas-clave.md` — checklist derechos/participación/protección/reparación (sin inventar arts).
- `agente/conocimiento/proceso-penal-906.md` — etapa `etapa_ley906` y rol de representación.
- Tools reales: `leer_normas_clave`, `leer_playbook_proceso`, `buscar_en_conocimiento`, `buscar_en_expediente`.

## Inputs
- Hechos verificados y etapa procesal Ley 906.
- Conductas u omisiones de Fiscalía, juez o autoridad que afecten a la víctima.
- Normativa de víctimas vía KB/RAG (`normas-clave.md`, Ley 906); sin inventar artículos.

## Outputs
- `derechos_mapeados`: participación | información | reparación | protección | otros.
- Por derecho: `hecho_vinculado`, `autoridad_responsable`, `estado` (vulnerado | en_riesgo | respetado | pendiente).
- `prioridad_atencion` (alta | media | baja).
- Etiqueta: `MAPEO DERECHOS VÍCTIMA — VÍA PENAL`.

## Steps
0. Anclar derechos/etapa/no-revictimización a Fuentes KB; sin soporte → `[PENDIENTE DE VERIFICAR]`.
1. Mapear derechos aplicables (participación, verdad, justicia, reparación, etc.) al caso.
2. Anclar a hechos y etapa; marcar derechos sin soporte como pendientes.
3. No convertir el análisis en memorial.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `analizar_derechos_victima`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_normas_victimas_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `rag_constitucional_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto

## Guardrails
- **No inventar:** No inventar vulneraciones ni normas.
- **Separar hecho de inferencia:** Derecho procesal de víctima se atiende en vía Ley 906 / petición / impulso.
- **No revictimizar:** Lenguaje respetuoso con la víctima; sin juicios de credibilidad ni exposición innecesaria.
- **Revision humana obligatoria:** HITL obligatorio antes de incorporar hallazgos a escritos o comunicación externa.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No intereses subjetivos (`identificar_intereses_victima`).
- No redactar memoriales (`redactor_documentos_juridicos`).

## Riesgo si se omite
Estrategia que ignora derechos procesales de la víctima ya vulnerados en el expediente.
