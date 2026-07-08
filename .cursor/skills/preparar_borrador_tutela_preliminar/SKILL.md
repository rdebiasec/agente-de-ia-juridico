---
name: preparar-borrador-tutela-preliminar
description: Skill estrategico penal-victimas: preparar insumos para borrador de tutela. Use when the workflow requires `preparar_borrador_tutela_preliminar`.
disable-model-invocation: true
---

# preparar_borrador_tutela_preliminar

## Scope
- Category: `Skills constitucionales y tutela`
- Skill ID: `preparar_borrador_tutela_preliminar`
- Tier: `estrategico`

## Used By Agents
- `evaluador_derechos_fundamentales_tutela` (organiza insumos)
- `redactor_documentos_juridicos_penales` (consume insumos para redactar)

## Purpose
Consolidar insumos estructurados para borrador de tutela solo si hay dictamen preliminar de procedencia.

## Rol en evaluador_derechos_fundamentales_tutela
Ejecutar tras `evaluar_procedencia_tutela` con conclusión favorable o con reservas.

## Rol en redactor_documentos_juridicos_penales
Recibir paquete de insumos; no redactar sin gate de procedencia.

## Inputs
- Dictamen de `evaluar_procedencia_tutela` (procedente o con reservas).
- Matriz hecho-derecho (`crear_matriz_hecho_derecho_fundamental`).
- Autoridades accionadas, pretensiones y anexos disponibles.

## Outputs
- Paquete: `hechos_estructurados`, `derechos_vulnerados`, `fundamentos_preliminares`, `pretensiones`, `anexos_referenciados`, `pendientes_verificacion`.
- `dictamen_procedencia_ref` (ID o resumen del evaluador).
- Etiqueta: `INSUMOS TUTELA — NO ES BORRADOR RADICABLE`.

## Steps
1. Consolidar hechos, derechos afectados y pretensiones con fuentes.
2. Verificar que el evaluador constitucional recomendó tutela preliminarmente.
3. Organizar insumos (hechos, fundamentos, pretensiones, anexos) para borrador.
4. Listar pendientes `[PENDIENTE DE VERIFICAR]` antes de pasar al redactor.
5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_plantillas_search`
- `rag_corte_constitucional_search`

## Guardrails (g1–g10)
- **g1:** No inventar hechos ni citas constitucionales.
- **g4:** Gate: sin dictamen de procedencia, detener y devolver a evaluador.
- **g5:** Relato de hechos sin revictimización.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No redactar texto de tutela (`redactar_tutela_penal_preliminar`).
- No evaluar procedencia (`evaluar_procedencia_tutela`).

## Riesgo si se omite
Borrador de tutela armado sin insumos verificados o sin dictamen previo → improcedencia o memorial inconsistente.
