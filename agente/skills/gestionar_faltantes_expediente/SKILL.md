<!-- config-version: 4; checksum: 0028dc15671ab806 -->
---
name: gestionar-faltantes-expediente
description: Contrato penal-víctimas: Identificar datos y documentos mínimos que faltan en el expediente **antes** de autorizar análisis de fondo o redacción, y bloquear conclusiones prematuras. Activar cuando el plan/HITL o el especialista requiera `gestionar_faltantes_expediente`. No sus...
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
- `coordinador_caso`

## Purpose
Identificar datos y documentos mínimos que faltan en el expediente **antes** de autorizar análisis de fondo o redacción, y bloquear conclusiones prematuras.

## Rol en coordinador_caso
Gate de completitud documental exclusivo del coordinador. Runtime: `assess_completeness` → `CompletenessResult` (`src/agents/completeness.py`).

## Fuentes KB
- `agente/conocimiento/proceso-penal-906.md` — checklist gerencia/POC (gate documental vs vacíos factuales).
- `agente/conocimiento/normas-clave.md` — no inventar documentos; pedir faltantes bloqueantes antes de redactor.
- Convención: checklist administrativo ≠ `detectar_vacios_factuales` (cronología).

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
0. Contrastar inventario con Fuentes KB/checklist gerencia; no inventar documentos ni cerrar el gate sin soporte.
1. Listar faltantes críticos que bloquean el pedido.
2. Priorizar preguntas concretas al abogado.
3. No inventar datos para cerrar el gate.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `gestionar_faltantes_*` ni CRUD de faltantes.

### Function tools (LLM, si aplica en el turno)
- `buscar_en_expediente` (sesión activa vinculada)

### Side-effects de código (no son function_tools)
- `gerencia_ledger` — gate determinista en `src/agents/completeness.py` (`assess_completeness`, `persist_verification`, `tareas_gerencia`)
- `audit_trace` — spans `Gerencia: verificación de completitud` en pipeline/runner

### Tool omitida a propósito
- `consultar_estado_gerencia` no se expone como function_tool: el estado ya llega en `[TRIAGE_SISTEMA]` / expediente / métricas; una tool de lectura sumaría superficie sin beneficio claro en el POC.

## Guardrails
- **No inventar:** No afirmar que un documento existe si no está en expediente o adjuntos.
- **Pedir datos faltantes:** Obligatorio pedir faltantes bloqueantes antes de derivar a redactor.
- **Separar hecho de inferencia:** Distinguir documento no aportado de documento mencionado pero no verificado.
- **Revision humana obligatoria:** No autorizar redacción de memorial, petición o recurso con faltantes bloqueantes sin excepción aprobada por abogado.
- **Confidencialidad:** No listar datos sensibles innecesarios en la solicitud de completitud.
- **Aviso de borrador:** Aviso de revisión profesional.

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
