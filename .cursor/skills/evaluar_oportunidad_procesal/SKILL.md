<!-- config-version: 3; checksum: 4e320ccefa605c45 -->
---
name: evaluar-oportunidad-procesal
description: Contrato penal-víctimas: Determinar si una actuación propuesta es oportuna, prematura o extemporánea para la víctima en la etapa actual. Activar cuando el plan/HITL o el especialista requiera `evaluar_oportunidad_procesal`. No sustituye a `controlar_terminos_procesales_prelimi...
disable-model-invocation: true
---

# evaluar_oportunidad_procesal

## Scope
- Category: `Skills de ruta procesal Ley 906`
- Skill ID: `evaluar_oportunidad_procesal`
- Tier: `operativo`

## Used By Agents
- `analista_ruta_procesal`
- `analista_calidad_juridica`

## Purpose
Determinar si una actuación propuesta es oportuna, prematura o extemporánea para la víctima en la etapa actual.

## Rol en analista_ruta_procesal
Decisión clave antes de cualquier solicitud, recurso o intervención. Requiere etapa y términos preliminares.

## Inputs
- Actuación o solicitud propuesta (tipo, destinatario, objeto).
- Etapa procesal y actuaciones previas del radicado.
- Fechas límite estimadas (`controlar_terminos_procesales_preliminares`).
- Estado probatorio relevante (si aplica).

## Outputs
- `dictamen_preliminar`: oportuna | prematura | extemporánea | `[PENDIENTE DE VERIFICAR]`.
- `razon`, `consecuencias_de_actuar_o_no`, `fecha_alternativa_sugerida`.
- `datos_faltantes` para cerrar dictamen.
- Advertencia: cálculo de términos requiere verificación humana.

## Steps
1. Relacionar etapa Ley 906 con la actuación pretendida.
2. Señalar ventanas, términos y riesgos de extemporaneidad con fuentes.
3. Marcar plazos no verificados como pendientes.
4. No sustituir alertas operativas (`generar_alertas_terminos_vencimientos`).

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `evaluar_oportunidad_procesal`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_ley906_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `calendar_terms_calculator` — no implementada

## Guardrails
- **No inventar:** No inventar plazos ni actuaciones previas.
- **Pedir datos faltantes:** Sin fecha de notificación de acto a impugnar, dictamen extemporaneidad = pendiente.
- **Separar hecho de inferencia:** Oportunidad es dictamen preliminar, no certeza judicial.
- **Revision humana obligatoria:** HITL obligatorio antes de interponer recurso o solicitud.
- **Oportunidad y terminos Ley 906:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **Aviso de borrador:** Aviso: términos deben verificarse por abogado.


## Fuentes KB (obligatorio consultar antes de citar norma)
- `agente/conocimiento/proceso-penal-906.md` — etapas canónicas y términos (días hábiles).
- `agente/conocimiento/normas-clave.md` — criterio operativo + citación.
- Tools: `leer_playbook_proceso`, `leer_normas_clave`, `buscar_en_conocimiento`.
- Actuación/fecha/artículo no verificado → `[PENDIENTE DE VERIFICAR]`.

## No duplicar
- No calcular todos los términos (`controlar_terminos_procesales_preliminares`).
- No redactar recurso (`redactar_recurso_o_intervencion_preliminar` → redactor).
- No mapear catálogo de actuaciones (`mapear_actuaciones_posibles_victima`).

## Riesgo si se omite
Pérdida de recursos, preclusión o solicitud rechazada por extemporaneidad.
