---
name: clasificar-fuente-factual
description: Skill estrategico penal-victimas: distinguir documento, relato de victima, relato de tercero, autoridad, inferencia o dato pendiente. Use when the workflow requires `clasificar_fuente_factual`.
disable-model-invocation: true
---

# clasificar_fuente_factual

## Scope
- Category: `Skills de hechos y cronologia`
- Skill ID: `clasificar_fuente_factual`
- Tier: `estrategico`

## Used By Agents
- `coordinador_expediente_penal`

## Purpose
Clasificar cada afirmación factual según su fuente y nivel de soporte, antes de derivar análisis o redacción. Evita que inferencias o relatos no corroborados se traten como hechos probados.

## Rol en coordinador
Primer filtro factual al recibir insumos nuevos (consulta, documentos, relato). No construye cronología completa ni matriz hecho-prueba; solo matriz hecho-fuente preliminar.

## Inputs
- Texto del turno: consulta del abogado, relato de víctima, extractos documentales.
- Documentos o fragmentos disponibles en el expediente (denuncia, informe de policía, actuaciones).
- Referencias de fuente cuando existan (folio, fecha, remitente, timestamp).

## Outputs
- Matriz hecho-fuente preliminar por afirmación: `hecho`, `tipo_fuente` (`documento` | `relato_victima` | `relato_tercero` | `autoridad` | `inferencia` | `pendiente`), `nivel_soporte` (`confirmado` | `narrado` | `inferido` | `sin_fuente`).
- Lista de afirmaciones marcadas `[PENDIENTE DE VERIFICAR]`.
- Nota explícita: no es cronología ni conclusión de tipicidad.

## Steps
1. Inventariar cada afirmación factual en los insumos del turno.
2. Clasificar fuente: documento, relato víctima, tercero, autoridad, inferencia o pendiente.
3. Asignar nivel de soporte sin mezclar hecho confirmado, narrado e inferido.
4. Construir matriz hecho-fuente preliminar (no cronología completa).
5. Señalar afirmaciones sin fuente para verificación humana.
6. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `source_reference_validator`

## Guardrails (g1–g10)
- **g1:** No inventar fuentes, folios ni documentos no aportados.
- **g2:** Si no hay insumos factuales, pedir relato o documentos antes de clasificar.
- **g3:** Obligatorio: separar confirmado, narrado, inferido y pendiente en columnas distintas.
- **g4:** La matriz es insumo interno; no usar como memorial ni escrito externo sin revisión.
- **g5:** Al clasificar relatos de víctima, no usar lenguaje que implique culpa o incredibilidad.
- **g6:** Minimizar datos sensibles en la matriz; referir al documento fuente cuando baste.
- **g8:** Cerrar con aviso de revisión profesional antes de usar en estrategia o redacción.

## Handoff
- Entregar matriz preliminar a `analista_cronologia_hechos_penales` → `crear_matriz_hecho_fuente` (referencias exactas).
- No enviar a tipicidad ni redacción sin pasar por verificación factual.

## No duplicar
- No ordenar línea de tiempo (`construir_cronologia_penal` → `analista_cronologia_hechos_penales`).
- No vincular hechos con prueba (`construir_matriz_hecho_prueba` → `gestor_evidencia_y_soporte_probatorio`).
- No detectar contradicciones entre versiones (`detectar_contradicciones_factuales`).

## Riesgo si se omite
Hechos inferidos o narrados presentados como probados debilitan memoriales y exponen al despacho a rechazo por Fiscalía o juez.
