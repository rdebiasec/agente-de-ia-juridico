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

## Used By Agents
- `coordinador_expediente_penal`

## Purpose
Identificar datos y documentos mínimos que faltan en el expediente **antes** de autorizar análisis de fondo o redacción, y bloquear conclusiones prematuras.

## Rol en coordinador
Gate de completitud documental exclusivo del coordinador. Se ejecuta tras `clasificar_tarea_y_etapa` cuando la tarea requiere expediente mínimo.

## Inputs
- Tipo de tarea clasificada (redacción, análisis, audiencia, tutela, etc.).
- Inventario de documentos en expediente o adjuntos del turno.
- Radicado, poder, cédula de víctima, actuaciones procesales conocidas.
- Checklist mínimo por tipo de tarea (definido en el turno o estándar del despacho).

## Outputs
- Lista de faltantes: `elemento`, `prioridad` (`bloqueante` | `deseable`), `motivo`, `responsable_sugerido`.
- `puede_continuar`: sí | no (solo si no hay bloqueantes).
- Tareas creadas para recolección (si aplica).
- Mensaje al abogado con solicitud concreta de completar.

## Steps
1. Inventariar datos y documentos mínimos para el análisis solicitado.
2. Listar faltantes por prioridad (bloqueante vs deseable).
3. Solicitar al abogado completar antes de concluir.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `case_state_reader`
- `rag_expediente_search`
- `task_manager_create`

## Guardrails (g1–g10)
- **g1:** No afirmar que un documento existe si no está en expediente o adjuntos.
- **g2:** Obligatorio pedir faltantes bloqueantes antes de derivar a redactor o evaluador tutela.
- **g3:** Distinguir documento no aportado de documento mencionado pero no verificado.
- **g4:** No autorizar redacción de memorial, tutela o recurso con faltantes bloqueantes sin excepción aprobada por abogado.
- **g6:** No listar datos sensibles innecesarios en la solicitud de completitud.
- **g8:** Aviso de revisión profesional.

## No duplicar
- **vs `detectar_vacios_factuales`:** este skill es **checklist documental/administrativo**; vacíos factuales son lagunas en la narrativa o prueba del hecho.
- No inventariar evidencia probatoria (`inventariar_evidencia`).
- No clasificar fuentes (`clasificar_fuente_factual`).

## Riesgo si se omite
Memoriales o solicitudes con anexos inexistentes, poder inválido o radicado errado → rechazo o nulidad.
