---
name: generar-preguntas-tipicidad
description: Skill operativo penal-victimas: crear preguntas para completar elementos del tipo penal. Use when the workflow requires `generar_preguntas_tipicidad`.
disable-model-invocation: true
---

# generar_preguntas_tipicidad

## Scope
- Category: `Skills de tipicidad y responsabilidad penal`
- Skill ID: `generar_preguntas_tipicidad`
- Tier: `operativo`

## Used By Agents
- `analista_tipicidad_y_responsabilidad_penal` (uso principal)
- `analista_cronologia_hechos_penales` (solo vacíos factuales con impacto tipico preliminar)

## Purpose
Formular preguntas para completar elementos del tipo penal, sin presuponer culpabilidad.

## Rol en analista_tipicidad
**Uso principal:** tras `descomponer_elementos_tipo_penal` y `mapear_tipo_penal_hecho_prueba`, para cerrar vacíos en elementos objetivos o subjetivos. Preguntas alineadas a elemento del tipo, no genéricas.

## Rol en analista_cronologia
**Uso limitado:** solo cuando un vacío factual obvio impide plantear hipótesis de conducta. Derivar al analista de tipicidad si el vacío es dogmático.

## Inputs
- Vacíos factuales ya documentados (`detectar_vacios_factuales`).
- Hipótesis de conducta preliminar (si existe, marcada como tal).
- Elementos del tipo penal incompletos por falta de hecho, no por análisis jurídico.

## Outputs
- Preguntas: `pregunta`, `elemento_factual_que_aclara`, `riesgo_induccion` (alto | medio | bajo).
- Nota de derivación a `analista_tipicidad_y_responsabilidad_penal` si el vacío es jurídico-dogmático.
- Etiqueta: `NO SUSTITUYE ANÁLISIS DE TIPICIDAD`.

## Steps
1. Identificar vacíos en elementos del tipo penal.
2. Formular preguntas para víctima, testigos o abogado.
3. Evitar preguntas que presupongan culpabilidad.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- Sin herramientas obligatorias

## Guardrails (g1–g10)
- **g1:** No asumir que el tipo penal está configurado.
- **g3:** Preguntas aclaran hechos, no califican conducta.
- **g5:** No preguntas del tipo “¿por qué no denunció antes?” o que presupongan consentimiento.
- **g4:** Revisión del abogado antes de enviar a víctima.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No descomponer tipos penales (`descomponer_elementos_tipo_penal` → tipicidad).
- No preguntas solo factuales sin vínculo tipico (`generar_preguntas_aclaracion`).
- No mapear hecho-prueba (`mapear_tipo_penal_hecho_prueba`).

## Riesgo si se omite
El analista de cronología invade tipicidad sin rigor dogmático, o el analista de tipicidad trabaja sin hechos mínimos.
