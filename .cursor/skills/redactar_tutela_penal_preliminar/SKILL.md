---
name: redactar-tutela-penal-preliminar
description: Skill critico penal-victimas: crear borrador de tutela solo si el evaluador constitucional lo recomienda preliminarmente. Use when the workflow requires `redactar_tutela_penal_preliminar`.
disable-model-invocation: true
---

# redactar_tutela_penal_preliminar

## Scope
- Category: `Skills de redaccion juridica penal`
- Skill ID: `redactar_tutela_penal_preliminar`
- Tier: `critico`

## Used By Agents
- `redactor_documentos_juridicos_penales` (único ejecutor de redacción)

## Purpose
Redactar borrador de tutela solo con dictamen previo de procedencia e insumos del evaluador constitucional.

## Rol en redactor_documentos_juridicos_penales
Ejecutar los 10 pasos solo si `evaluar_procedencia_tutela` dictaminó procedencia preliminar. Si no, detener y devolver a evaluador.

## Inputs
- Dictamen de `evaluar_procedencia_tutela` (procedente o con reservas).
- Paquete de `preparar_borrador_tutela_preliminar`.
- Hechos verificados, derechos afectados, pretensiones y anexos referenciados.

## Outputs
- Borrador numerado: `hechos`, `derechos_vulnerados`, `fundamentos_constitucionales`, `pretensiones`, `pruebas_anexos`.
- `pendientes_verificacion` antes de firma.
- Etiquetas: `BORRADOR — NO RADICAR SIN FIRMA` | `PRELIMINAR CONSTITUCIONAL`.

## Steps
1. Confirmar dictamen previo de procedencia tutela (no redactar si improcedente).
2. Consolidar hechos verificables separados de inferencias y pendientes.
3. Identificar derechos fundamentales vulnerados y autoridades accionadas.
4. Redactar fundamentos constitucionales con citas verificadas en RAG.
5. Formular pretensiones claras, medibles y proporcionales.
6. Listar pruebas y anexos; marcar faltantes como pendientes.
7. Revisar no revictimización en relato y peticiones.
8. Control de competencia, direccionamiento y tono profesional.
9. Entregar borrador numerado listo para revisión de firma (sin radicar).
10. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_constitucion_search`
- `rag_corte_constitucional_search`
- `rag_plantillas_search`

## Guardrails (g1–g10)
- **g1:** No inventar hechos, normas, sentencias ni radicados.
- **g3:** Hecho separado de argumentación constitucional.
- **g4:** Gate obligatorio: sin dictamen de procedencia, no redactar.
- **g5:** No revictimizar en relato ni pretensiones.
- **g8:** Aviso de revisión profesional y firma humana.

## No duplicar
- No evaluar procedencia (`evaluar_procedencia_tutela`).
- No preparar insumos (`preparar_borrador_tutela_preliminar`).

## Riesgo si se omite
Tutela improcedente o mal fundamentada radicada sin control constitucional previo.
