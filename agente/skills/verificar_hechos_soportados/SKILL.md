<!-- config-version: 4; checksum: c34c0b793c6139d3 -->
---
name: verificar-hechos-soportados
description: Contrato penal-víctimas: Cruzar cada afirmación factual del análisis con fuente en expediente y clasificar soporte. Activar cuando el plan/HITL o el especialista requiera `verificar_hechos_soportados`. No sustituye a `marcar_pendientes_verificacion`.
disable-model-invocation: true
---

# verificar_hechos_soportados

## Scope
- Category: `Skills transversales`
- Skill ID: `verificar_hechos_soportados`
- Tier: `operativo`

## Used By Agents
- `analista_cronologia_hechos` (control de cierre del pipeline factual)
- `analista_calidad_juridica`
- `redactor_documentos_juridicos`

## Purpose
Cruzar cada afirmación factual del análisis con fuente en expediente y clasificar soporte.

## Rol en analista_cronologia_hechos
Último control antes de entregar cronología/matriz al despacho o derivar a tipicidad. Complementa `marcar_pendientes_verificacion` con cruce activo contra expediente.

## Fuentes KB
- Relato/expediente del caso (hechos); no inventar fechas ni actuaciones.
- `agente/conocimiento/proceso-penal-906.md` — solo si un evento es actuación procesal (etiquetar etapa con evidencia).
- `agente/conocimiento/normas-clave.md` — no revictimización al ordenar relatos.
- Herramientas: `buscar_en_expediente`, `buscar_en_conocimiento` para anclar; no calificar tipicidad aquí.
## Inputs
- Texto o estructura a verificar (cronología, matriz, lista de hechos).
- Expediente y fuentes disponibles en RAG.
- Matriz hecho-fuente (si existe).

## Outputs
- `hechos_soportados`: afirmación + fuente + nivel de confianza.
- `hechos_no_soportados`: afirmación + motivo + `[PENDIENTE DE VERIFICAR]`.
- `tipo_fuente` por afirmación.
- Recomendación: apto para uso interno | requiere completar fuentes | no apto para memorial.

## Steps
0. Separar confirmado|narrado|inferido|pendiente_verificar; no inventar fechas; no tipificar (otro especialista).
1. Listar afirmaciones factuales en el texto o análisis.
2. Cruzar cada afirmación con fuente documental o expediente.
3. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `verificar_hechos_soportados`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_expediente_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `source_reference_validator` — no implementada

## Guardrails
- **No inventar:** Implementación operativa de g1 — sin fuente, no soportado.
- **Separar hecho de inferencia:** Distinguir “no encontrado en expediente” de “falso”.
- **Revision humana obligatoria:** Bloquear uso en memorial si hay hechos no soportados de impacto alto.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No insertar marcadores en texto (`marcar_pendientes_verificacion`).
- No crear matriz desde cero (`crear_matriz_hecho_fuente`).
- No detectar contradicciones (`detectar_contradicciones_factuales`).

## Riesgo si se omite
Cronología “cerrada” con afirmaciones que el abogado asume verificadas y la contraparte desmonta.
