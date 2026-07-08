---
name: preservar-evidencia-digital
description: Skill critico penal-victimas: definir medidas para proteger evidencia digital sin alterarla. Use when the workflow requires `preservar_evidencia_digital`.
disable-model-invocation: true
---

# preservar_evidencia_digital

## Scope
- Category: `Skills de evidencia y soporte probatorio`
- Skill ID: `preservar_evidencia_digital`
- Tier: `critico`

## Used By Agents
- `gestor_evidencia_y_soporte_probatorio` (skill crítico del flujo digital)

## Purpose
Proteger mensajes, archivos, audios o videos digitales sin alterarlos, con hash y custodia preliminar.

## Rol en gestor_evidencia_y_soporte_probatorio
Ejecutar de inmediato cuando ingresa evidencia digital nueva o vulnerable a borrado.

## Inputs
- Archivos digitales: chats, correos, fotos, videos, audios, capturas.
- Origen (dispositivo, cuenta, fecha aproximada de obtención).
- Urgencia de pérdida (plataforma que borra, dispositivo compartido, etc.).

## Outputs
- `hash_integridad` por archivo (algoritmo y valor).
- `metadatos`: nombre, tamaño, fecha extracción, herramienta usada.
- `copia_resguardo`: ubicación segura y custodio designado.
- `cadena_preliminar`: accesos autorizados registrados.
- `escalar`: perito | autoridad | ninguno.
- Etiqueta: `NO MODIFICAR ORIGINAL — COPIA FORENSE SI ES CRÍTICO`.

## Steps
1. Identificar archivos, mensajes o medios vulnerables a alteración o pérdida.
2. Generar hash y metadatos de integridad sin modificar el original.
3. Definir copia forense o resguardo seguro y quién custodia.
4. Documentar cadena de custodia preliminar y accesos autorizados.
5. Escalar a perito o autoridad si la evidencia es crítica para el caso.
6. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `file_hash_generator`
- `metadata_extractor`
- `evidence_vault_store`
- `chain_of_custody_logger`

## Guardrails (g1–g10)
- **g1:** No inventar hashes ni metadatos.
- **g6:** Minimizar copias innecesarias de material sensible.
- **g4:** HITL antes de compartir evidencia digital fuera del despacho.
- **g9:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **g8:** Aviso de revisión profesional.

## Handoff
- Tras preservar → `controlar_cadena_custodia_preliminar`, `inventariar_evidencia`.

## Riesgo si se omite
Pérdida o alteración de chats, videos o archivos que soportan la versión de la víctima.
