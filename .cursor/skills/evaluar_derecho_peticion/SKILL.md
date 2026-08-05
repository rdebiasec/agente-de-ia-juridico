<!-- config-version: 3; checksum: 664ccab649f3d2a3 -->
<!-- config-version: 3; checksum: pending -->
---
name: evaluar-derecho-peticion
description: Contrato penal-víctimas: Verificar si hay petición previa incumplida y si procede un nuevo derecho de petición, impulso o seguimiento en vía penal. Activar cuando el plan/HITL o el especialista requiera `evaluar_derecho_peticion`. No sustituye a `redactar_derecho_peticion_penal`.
disable-model-invocation: true
---

# evaluar_derecho_peticion

## Scope
- Category: `Skills de redaccion y seguimiento procesal`
- Skill ID: `evaluar_derecho_peticion`
- Tier: `estrategico`

## Used By Agents
- `redactor_documentos_juridicos`
- `analista_seguimiento_procesal`

## Purpose
Verificar si hay petición previa incumplida y si procede un nuevo derecho de petición, impulso o seguimiento en vía penal.

## Rol en redactor_documentos_juridicos
Solo redactar petición o impulso si este skill dictamina procedencia preliminar de petición / insistencia.

## Rol en analista_seguimiento_procesal
Insumo para alertas de silencio administrativo y términos de respuesta.

## Inputs
- Copia o datos de petición previa (fecha, destinatario, objeto, radicado si consta).
- Plazo legal de respuesta y fecha de vencimiento.
- Respuesta recibida o constancia de silencio (si existe).

## Outputs
- `peticion_existe`: sí | no | `[PENDIENTE DE VERIFICAR]`.
- `incumplimiento`: sí | no | parcial | no_evaluable.
- `via_recomendada`: nueva_peticion | impulso_procesal | solicitud_906 | aguardar_respuesta.
- `plazos_clave` y actuación siguiente.
- Etiqueta: `EVALUACIÓN PETICIÓN — VÍA PENAL (NO TUTELA)`.

## Steps
1. Verificar existencia de petición previa, destinatario y objeto solicitado.
2. Constatar plazo de respuesta y silencio administrativo si aplica.
3. Determinar si procede nuevo derecho de petición, memorial de impulso u otra vía penal.
4. Documentar requisitos faltantes para interponer nueva petición o impulso.
5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `evaluar_derecho_peticion`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `calendar_terms_calculator` — no implementada

## Guardrails
- **No inventar:** No inventar peticiones ni fechas de radicación.
- **Separar hecho de inferencia:** Silencio administrativo solo si consta plazo y vencimiento.
- **Revision humana obligatoria:** Redactor solo actúa con evaluación favorable a petición/impulso.
- **Aviso de borrador:** Aviso de revisión profesional.
- **Fuera de alcance:** No derivar a vías de otros equipos Lexiatek; limitar a petición/impulso penal-víctimas.

## No duplicar
- No redactar petición (`redactar_derecho_peticion_penal` — redactor).
- No memorial de impulso (`redactar_solicitud_impulso_procesal` — redactor).

## Riesgo si se omite
Impulso o nueva petición sin constatar silencio válido, o demora innecesaria cuando la petición es la vía más rápida.
