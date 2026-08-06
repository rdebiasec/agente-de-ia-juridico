<!-- config-version: 3; checksum: b4e23963da398b82 -->
---
name: generar-preguntas-tipicidad
description: Contrato penal-víctimas: Formular preguntas para completar elementos del tipo penal, sin presuponer culpabilidad. Activar cuando el plan/HITL o el especialista requiera `generar_preguntas_tipicidad`. No sustituye a `descomponer_elementos_tipo_penal`.
disable-model-invocation: true
---

# generar_preguntas_tipicidad

## Scope
- Category: `Skills de tipicidad y responsabilidad penal`
- Skill ID: `generar_preguntas_tipicidad`
- Tier: `operativo`

## Used By Agents
- `analista_responsabilidad_tipicidad` (uso principal)
- `analista_cronologia_hechos` (solo vacíos factuales con impacto tipico preliminar)

## Purpose
Formular preguntas para completar elementos del tipo penal, sin presuponer culpabilidad.

## Rol en analista_responsabilidad_tipicidad
**Uso principal:** tras `descomponer_elementos_tipo_penal` y `mapear_tipo_penal_hecho_prueba`, para cerrar vacíos en elementos objetivos o subjetivos. Preguntas alineadas a elemento del tipo, no genéricas.

## Rol en analista_cronologia_hechos
**Uso limitado:** solo cuando un vacío factual obvio impide plantear hipótesis de conducta. Derivar al analista de tipicidad si el vacío es dogmático.

## Inputs
- Vacíos factuales ya documentados (`detectar_vacios_factuales`).
- Hipótesis de conducta preliminar (si existe, marcada como tal).
- Elementos del tipo penal incompletos por falta de hecho, no por análisis jurídico.

## Outputs
- Preguntas: `pregunta`, `elemento_factual_que_aclara`, `riesgo_induccion` (alto | medio | bajo).
- Nota de derivación a `analista_responsabilidad_tipicidad` si el vacío es jurídico-dogmático.
- Etiqueta: `NO SUSTITUYE ANÁLISIS DE TIPICIDAD`.

## Steps
1. Tomar vacíos por elemento del tipo (objetivo/subjetivo) desde descomposición/matriz (`penal.md`).
2. Formular preguntas ligadas a `elemento_factual_que_aclara`; no genéricas.
3. Evitar inducción de culpabilidad y preguntas revictimizantes (p. ej. “¿por qué no denunció antes?”).
4. Si el vacío es dogmático-jurídico, derivar a `analista_responsabilidad_tipicidad` (no resolverlo aquí).
5. Etiqueta `NO SUSTITUYE ANÁLISIS DE TIPICIDAD`; revisión humana antes de enviar a víctima.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `generar_preguntas_tipicidad`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

## Guardrails
- **No inventar:** No asumir que el tipo penal está configurado.
- **Separar hecho de inferencia:** Preguntas aclaran hechos, no califican conducta.
- **No revictimizar:** No preguntas del tipo “¿por qué no denunció antes?” o que presupongan consentimiento.
- **Revision humana obligatoria:** Revisión del abogado antes de enviar a víctima.
- **Aviso de borrador:** Aviso de revisión profesional.


## Fuentes KB (obligatorio consultar antes de citar norma)
- `agente/conocimiento/penal.md` — marco tipico, dolo/culpa, autoría, agravantes.
- `agente/conocimiento/normas-clave.md` — marco Ley 599/906 + checklist de citación.
- Tools: `leer_area_derecho` (penal), `leer_normas_clave`, `buscar_en_conocimiento`.
- Artículo concreto no verificado → `[PENDIENTE DE VERIFICAR]`. No inventar normas.

## No duplicar
- No descomponer tipos penales (`descomponer_elementos_tipo_penal` → `analista_responsabilidad_tipicidad`).
- No preguntas solo factuales sin vínculo tipico (`generar_preguntas_aclaracion`).
- No mapear hecho-prueba (`mapear_tipo_penal_hecho_prueba`).

## Riesgo si se omite
El analista de cronología invade tipicidad sin rigor dogmático, o el analista de tipicidad trabaja sin hechos mínimos.
