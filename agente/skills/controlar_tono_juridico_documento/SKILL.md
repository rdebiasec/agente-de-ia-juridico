<!-- config-version: 2; checksum: e6cbd7119a40fbff -->
---
name: controlar-tono-juridico-documento
description: Contrato penal-víctimas: Revisar que el tono del escrito sea profesional, respetuoso y adecuado al destinatario judicial o administrativo. Activar cuando el plan/HITL o el especialista requiera `controlar_tono_juridico_documento`. No sustituye a `controlar_tono_riesgo_reputaci...
disable-model-invocation: true
---

# controlar_tono_juridico_documento

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `controlar_tono_juridico_documento`
- Tier: `operativo`

## Used By Agents
- `redactor_documentos_juridicos`
- `analista_calidad_juridica`

## Purpose
Revisar que el tono del escrito sea profesional, respetuoso y adecuado al destinatario judicial o administrativo.

## Rol en redactor_documentos_juridicos
Revisión de tono antes de pasar a calidad.

## Rol en analista_calidad_juridica
Control final de estilo en salidas externas.

## Inputs
- Borrador de memorial, petición o solicitud.
- Destinatario (juez, Fiscalía, autoridad administrativa).

## Outputs
- `hallazgos_tono`: agresivo | coloquial | emocional_excesivo | procesal_inadecuado | ok.
- `reformulaciones` sugeridas por fragmento.
- Etiqueta: `CONTROL TONO JURÍDICO`.

## Steps
1. Revisar tono: formal, preciso, respetuoso con la víctima.
2. Señalar lenguaje revictimizante, coloquial o sobreprometedor.
3. Proponer ajustes puntuales; no reescribir todo el memorial.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `controlar_tono_juridico_documento`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

## Guardrails
- **No revictimizar:** Tono respetuoso con la víctima y las autoridades.
- **Revision humana obligatoria:** HITL obligatorio antes de usar la salida en memorial, estrategia o comunicación con cliente.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No riesgo reputacional público (`controlar_tono_riesgo_reputacional`).
- No revictimización (`controlar_no_revictimizacion`).

## Riesgo si se omite
Escrito que pierde credibilidad ante el despacho o irrita innecesariamente a la contraparte.
