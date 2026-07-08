---
name: evaluar-derecho-peticion
description: Skill estrategico penal-victimas: revisar si existe derecho de peticion incumplido. Use when the workflow requires `evaluar_derecho_peticion`.
disable-model-invocation: true
---

# evaluar_derecho_peticion

## Scope
- Category: `Skills constitucionales y tutela`
- Skill ID: `evaluar_derecho_peticion`
- Tier: `estrategico`

## Used By Agents
- `evaluador_derechos_fundamentales_tutela`
- `redactor_documentos_juridicos_penales`

## Purpose
Verificar si hay petición previa incumplida y si procede derecho de petición antes de tutela u otra vía.

## Rol en evaluador_derechos_fundamentales_tutela
Evaluar agotamiento vía petición para subsidiariedad tutelar.

## Rol en redactor_documentos_juridicos_penales
Solo redactar petición si este skill dictamina procedencia preliminar de petición.

## Inputs
- Copia o datos de petición previa (fecha, destinatario, objeto, radicado si consta).
- Plazo legal de respuesta y fecha de vencimiento.
- Respuesta recibida o constancia de silencio (si existe).

## Outputs
- `peticion_existe`: sí | no | `[PENDIENTE DE VERIFICAR]`.
- `incumplimiento`: sí | no | parcial | no_evaluable.
- `via_recomendada`: nueva_peticion | tutela_por_silencio | solicitud_906 | aguardar_respuesta.
- `plazos_clave` y actuación siguiente.
- Etiqueta: `EVALUACIÓN PETICIÓN — NO SUSTITUYE evaluar_procedencia_tutela`.

## Steps
1. Verificar existencia de petición previa, destinatario y objeto solicitado.
2. Constatar plazo de respuesta y silencio administrativo si aplica.
3. Determinar si procede derecho de petición, tutela u otra vía según el caso.
4. Documentar requisitos faltantes para interponer nueva petición o tutela.
5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `calendar_terms_calculator`
- `rag_constitucional_search`

## Guardrails (g1–g10)
- **g1:** No inventar peticiones ni fechas de radicación.
- **g3:** Silencio administrativo solo si consta plazo y vencimiento.
- **g4:** Redactor solo actúa con evaluación favorable a petición.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No redactar petición (`redactar_derecho_peticion_penal` — redactor).
- No dictaminar tutela completa (`evaluar_procedencia_tutela`).

## Riesgo si se omite
Tutela por silencio sin petición previa válida, o demora innecesaria cuando la petición es la vía más rápida.
