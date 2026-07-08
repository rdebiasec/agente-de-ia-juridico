---
name: controlar-separacion-hecho-inferencia
description: Skill atomico penal-victimas: verificar que no se confundan hechos probados, narrados, inferidos y pendientes. Use when the workflow requires `controlar_separacion_hecho_inferencia`.
disable-model-invocation: true
---

# controlar_separacion_hecho_inferencia

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `controlar_separacion_hecho_inferencia`
- Tier: `operativo`

## Used By Agents
- `redactor_documentos_juridicos_penales`
- `analista_calidad_juridica`

## Purpose
Verificar que hechos confirmados, narrados, inferidos y pendientes estén claramente separados en la salida.

## Rol en redactor_documentos_juridicos_penales
Autocontrol antes de entregar borrador.

## Rol en analista_calidad_juridica
Control de calidad en documentos para uso externo.

## Inputs
- Texto del memorial, tutela, petición o análisis.
- Matriz hecho-fuente o cronología (si existe).

## Outputs
- `fragmentos`: texto | clasificación (confirmado | narrado | inferido | pendiente) | observación.
- `correcciones_sugeridas` para separar hecho de argumentación.
- Etiqueta: `CONTROL HECHO-INFERENCIA`.

## Steps
1. Identificar afirmaciones fácticas en el texto.
2. Clasificar cada una según soporte documental.
3. Señalar mezclas de hecho con inferencia o calificación penal.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_expediente_search`

## Guardrails (g1–g10)
- **g3:** No reclasificar hecho confirmado sin fuente.
- **g4:** HITL obligatorio antes de usar la salida en memorial, estrategia o comunicación con cliente.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No verificar soporte global (`verificar_hechos_soportados`).
- No redactar hechos (`extraer_hechos_relevantes`).

## Riesgo si se omite
Memorial que presenta inferencias o sospechas como hechos probados ante el juez.
