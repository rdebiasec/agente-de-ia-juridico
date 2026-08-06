<!-- config-version: 3; checksum: 98df36e5ba9caef1 -->
---
name: clasificar-fuente-factual
description: Contrato penal-víctimas: Clasificar cada afirmación factual según su fuente y nivel de soporte, antes de derivar análisis o redacción. Evita que inferencias o relatos no corroborados se traten como hechos probados. Activar cuando el plan/HITL o el especialista requiera `clasif...
disable-model-invocation: true
---

# clasificar_fuente_factual

## Scope
- Category: `Skills de hechos y cronologia`
- Skill ID: `clasificar_fuente_factual`
- Tier: `estrategico`

## Used By Agents
- `analista_cronologia_hechos`

## Purpose
Clasificar cada afirmación factual según su fuente y nivel de soporte, antes de derivar análisis o redacción. Evita que inferencias o relatos no corroborados se traten como hechos probados.

## Rol en coordinador_caso
**MOVE:** este skill ya no es ownership del POC. El coordinador solo lo dispara vía tool del especialista dueño.

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
Skills = contratos (no function_tools invocables). No existe tool LLM `clasificar_fuente_factual`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `source_reference_validator` — no implementada

## Guardrails
- **No inventar:** No inventar fuentes, folios ni documentos no aportados.
- **Pedir datos faltantes:** Si no hay insumos factuales, pedir relato o documentos antes de clasificar.
- **Separar hecho de inferencia:** Obligatorio: separar confirmado, narrado, inferido y pendiente en columnas distintas.
- **Revision humana obligatoria:** La matriz es insumo interno; no usar como memorial ni escrito externo sin revisión.
- **No revictimizar:** Al clasificar relatos de víctima, no usar lenguaje que implique culpa o incredibilidad.
- **Confidencialidad:** Minimizar datos sensibles en la matriz; referir al documento fuente cuando baste.
- **Aviso de borrador:** Cerrar con aviso de revisión profesional antes de usar en estrategia o redacción.

## Handoff
- Entregar matriz preliminar a `analista_cronologia_hechos` → `crear_matriz_hecho_fuente` (referencias exactas).
- No enviar a tipicidad ni redacción sin pasar por verificación factual.

## No duplicar
- No ordenar línea de tiempo (`construir_cronologia_penal` → `analista_cronologia_hechos`).
- No vincular hechos con prueba (`construir_matriz_hecho_prueba` → `analista_evidencia`).
- No detectar contradicciones entre versiones (`detectar_contradicciones_factuales`).

## Riesgo si se omite
Hechos inferidos o narrados presentados como probados debilitan memoriales y exponen al despacho a rechazo por Fiscalía o juez.
