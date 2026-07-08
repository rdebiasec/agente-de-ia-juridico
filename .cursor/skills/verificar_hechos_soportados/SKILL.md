---
name: verificar-hechos-soportados
description: Skill operativo penal-victimas: revisar si cada afirmacion factual tiene fuente. Use when the workflow requires `verificar_hechos_soportados`.
disable-model-invocation: true
---

# verificar_hechos_soportados

## Scope
- Category: `Skills transversales`
- Skill ID: `verificar_hechos_soportados`
- Tier: `operativo`

## Used By Agents
- `analista_cronologia_hechos_penales` (control de cierre del pipeline factual)
- `analista_calidad_juridica`
- `redactor_documentos_juridicos_penales`

## Purpose
Cruzar cada afirmación factual del análisis con fuente en expediente y clasificar soporte.

## Rol en analista_cronologia
Último control antes de entregar cronología/matriz al despacho o derivar a tipicidad. Complementa `marcar_pendientes_verificacion` con cruce activo contra expediente.

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
1. Listar afirmaciones factuales en el texto o análisis.
2. Cruzar cada afirmación con fuente documental o expediente.
3. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_expediente_search`
- `source_reference_validator`

## Guardrails (g1–g10)
- **g1:** Implementación operativa de g1 — sin fuente, no soportado.
- **g3:** Distinguir “no encontrado en expediente” de “falso”.
- **g4:** Bloquear uso en memorial si hay hechos no soportados de impacto alto.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No insertar marcadores en texto (`marcar_pendientes_verificacion`).
- No crear matriz desde cero (`crear_matriz_hecho_fuente`).
- No detectar contradicciones (`detectar_contradicciones_factuales`).

## Riesgo si se omite
Cronología “cerrada” con afirmaciones que el abogado asume verificadas y la contraparte desmonta.
