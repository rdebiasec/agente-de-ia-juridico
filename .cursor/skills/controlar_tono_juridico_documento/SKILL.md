---
name: controlar-tono-juridico-documento
description: Skill atomico penal-victimas: asegurar tono formal, preciso, no agresivo y no especulativo. Use when the workflow requires `controlar_tono_juridico_documento`.
disable-model-invocation: true
---

# controlar_tono_juridico_documento

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `controlar_tono_juridico_documento`
- Tier: `operativo`

## Used By Agents
- `redactor_documentos_juridicos_penales`
- `analista_calidad_juridica`

## Purpose
Revisar que el tono del escrito sea profesional, respetuoso y adecuado al destinatario judicial o administrativo.

## Rol en redactor_documentos_juridicos_penales
Revisión de tono antes de pasar a calidad.

## Rol en analista_calidad_juridica
Control final de estilo en salidas externas.

## Inputs
- Borrador de memorial, petición, tutela o solicitud.
- Destinatario (juez, Fiscalía, autoridad administrativa).

## Outputs
- `hallazgos_tono`: agresivo | coloquial | emocional_excesivo | procesal_inadecuado | ok.
- `reformulaciones` sugeridas por fragmento.
- Etiqueta: `CONTROL TONO JURÍDICO`.

## Steps
1. Revisar registro formal y respeto institucional del escrito.
2. Detectar lenguaje emocional, acusatorio o coloquial impropio.
3. Proponer reformulaciones manteniendo el contenido jurídico.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- Sin herramientas obligatorias

## Guardrails (g1–g10)
- **g5:** Tono respetuoso con la víctima y las autoridades.
- **g4:** HITL obligatorio antes de usar la salida en memorial, estrategia o comunicación con cliente.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No riesgo reputacional público (`controlar_tono_riesgo_reputacional`).
- No revictimización (`controlar_no_revictimizacion`).

## Riesgo si se omite
Escrito que pierde credibilidad ante el despacho o irrita innecesariamente a la contraparte.
