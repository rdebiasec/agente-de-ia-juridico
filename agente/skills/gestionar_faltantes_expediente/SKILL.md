<!-- config-version: 3; checksum: 94a8e2cb3e9d2d6c -->
---
name: gestionar-faltantes-expediente
description: Skill operativo penal-victimas: identificar datos y documentos faltantes antes de analizar o redactar. Use when the workflow requires `gestionar_faltantes_expediente`.
disable-model-invocation: true
---

# gestionar_faltantes_expediente

## Scope
- Category: `Skills transversales`
- Skill ID: `gestionar_faltantes_expediente`
- Tier: `operativo`

## Index Blurb
Gate documental del POC: lista faltantes bloqueantes/deseables y decide si puede continuar.

## Used By Agents
- `coordinador_expediente_penal`

## Purpose
Identificar datos y documentos mínimos que faltan en el expediente **antes** de autorizar análisis de fondo o redacción, y bloquear conclusiones prematuras.

## Rol en coordinador
Gate de completitud documental exclusivo del coordinador. Runtime: `assess_completeness` → `CompletenessResult` (`src/agents/completeness.py`).

## Inputs
- Tipo de tarea / destino clasificado.
- Inventario de documentos en expediente o adjuntos del turno.
- Radicado, poder, actuaciones procesales conocidas.
- Checklist mínimo por destino (código).

## Outputs
- `faltantes_detalle`: lista de `{elemento, prioridad (bloqueante|deseable), motivo, responsable_sugerido}`.
- `faltantes`: `list[str]` (compat; labels de `elemento`).
- `puede_continuar`: bool (false si hay bloqueantes).
- Checklist canónico (labels): hechos mínimos del caso; número de radicado; poder o calidad en que actúa el despacho; última actuación procesal; partes relevantes; etapa o última actuación procesal.
- Tareas de recolección en `tareas_gerencia` (estado `pendiente` hasta cerrar).
- Mensaje al abogado con solicitud concreta (`format_missing_request`).

## Steps
1. Inventariar datos y documentos mínimos para el análisis solicitado.
2. Listar faltantes por prioridad (bloqueante vs deseable).
3. Solicitar al abogado completar antes de concluir.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `gestionar_faltantes_*` ni CRUD de faltantes.

### Function tools (LLM, si aplica en el turno)
- `buscar_en_expediente` (sesión activa vinculada)

### Side-effects de código (no son function_tools)
- `gerencia_ledger` — gate determinista en `src/agents/completeness.py` (`assess_completeness`, `persist_verification`, `tareas_gerencia`)
- `audit_trace` — spans `Gerencia: verificación de completitud` en pipeline/runner

### Tool omitida a propósito
- `consultar_estado_gerencia` no se expone como function_tool: el estado ya llega en `[TRIAGE_SISTEMA]` / expediente / métricas; una tool de lectura sumaría superficie sin beneficio claro en el POC.

## Guardrails (g1–g10)
- **g1:** No afirmar que un documento existe si no está en expediente o adjuntos.
- **g2:** Obligatorio pedir faltantes bloqueantes antes de derivar a redactor o evaluador tutela.
- **g3:** Distinguir documento no aportado de documento mencionado pero no verificado.
- **g4:** No autorizar redacción de memorial, tutela o recurso con faltantes bloqueantes sin excepción aprobada por abogado.
- **g6:** No listar datos sensibles innecesarios en la solicitud de completitud.
- **g8:** Aviso de revisión profesional.

## Handoff
- `puede_continuar=true` → tool del especialista según `tipo_tarea`.
- `puede_continuar=false` → tareas de recolección (`actualizar_tareas_responsable` como contrato) + mensaje al abogado.

## No duplicar
- **vs `detectar_vacios_factuales`:** este skill es **checklist documental/administrativo**; vacíos factuales son lagunas en la narrativa o prueba del hecho (especialista cronología).
- No inventariar evidencia probatoria (`inventariar_evidencia`).
- No clasificar fuentes (`clasificar_fuente_factual`).

## Best Practices
- Pedir 3–5 faltantes concretos, no un cuestionario largo.
- Separar bloqueantes de deseables en la solicitud al abogado.

## Riesgo si se omite
Memoriales o solicitudes con anexos inexistentes, poder inválido o radicado errado → rechazo o nulidad.
