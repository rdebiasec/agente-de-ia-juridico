<!-- config-version: 3; checksum: 037ca6a8d5cd25e3 -->
---
name: preservar-evidencia-digital
description: Contrato penal-víctimas: Proteger mensajes, archivos, audios o videos digitales sin alterarlos, con hash y custodia preliminar. Activar cuando el plan/HITL o el especialista requiera `preservar_evidencia_digital`. No sustituye a `controlar_cadena_custodia_preliminar`.
disable-model-invocation: true
---

# preservar_evidencia_digital

## Scope
- Category: `Skills de evidencia y soporte probatorio`
- Skill ID: `preservar_evidencia_digital`
- Tier: `critico`

## Used By Agents
- `analista_evidencia` (skill crítico del flujo digital)

## Purpose
Proteger mensajes, archivos, audios o videos digitales sin alterarlos, con hash y custodia preliminar.

## Rol en analista_evidencia
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
Skills = contratos (no function_tools invocables). No existe tool LLM `preservar_evidencia_digital`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `file_hash_generator` — no implementada
- `metadata_extractor` — no implementada
- `evidence_vault_store` — no implementada
- `chain_of_custody_logger` — no implementada

## Guardrails
- **Integridad probatoria:** Preservar original, hash y metadatos sin alterar el contenido.
- **No inventar:** No inventar hashes ni metadatos.
- **Confidencialidad:** Minimizar copias innecesarias de material sensible.
- **Revision humana obligatoria:** HITL antes de compartir evidencia digital fuera del despacho.
- **Oportunidad y terminos Ley 906:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **Aviso de borrador:** Aviso de revisión profesional.

## Handoff
- Tras preservar → `controlar_cadena_custodia_preliminar`, `inventariar_evidencia`.

## No duplicar
- No cadena de custodia física completa (`controlar_cadena_custodia_preliminar`).
- No inventario general (`inventariar_evidencia`).

## Riesgo si se omite
Pérdida o alteración de chats, videos o archivos que soportan la versión de la víctima.
