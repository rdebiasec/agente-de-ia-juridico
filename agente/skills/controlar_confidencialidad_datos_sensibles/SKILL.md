<!-- config-version: 3; checksum: 0d2a5d3173438c42 -->
---
name: controlar-confidencialidad-datos-sensibles
description: Contrato penal-víctimas: Detectar y mitigar exposición innecesaria de datos personales sensibles en salidas del sistema. Activar cuando el plan/HITL o el especialista requiera `controlar_confidencialidad_datos_sensibles`. No sustituye a `controlar_no_revictimizacion`.
disable-model-invocation: true
---

# controlar_confidencialidad_datos_sensibles

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `controlar_confidencialidad_datos_sensibles`
- Tier: `operativo`

## Used By Agents
- `analista_calidad_juridica`

## Purpose
Detectar y mitigar exposición innecesaria de datos personales sensibles en salidas del sistema.

## Rol en analista_calidad_juridica
Control de minimización y datos sensibles antes de salidas externas.
## Inputs
- Texto o documento a revisar.
- Destinatario previsto (interno, cliente, juzgado, tercero).

## Outputs
- `datos_sensibles_detectados`: tipo | fragmento | necesidad (necesario | reducible | eliminar).
- `recomendacion`: publicar | redactar | solo_abogado.
- Etiqueta: `CONTROL LEY 1581 / DATOS SENSIBLES`.

## Steps
1. Detectar PII/datos sensibles/menor en la salida.
2. Proponer redacción mínima necesaria o redacción.
3. No sustituir control de no revictimización ni dictamen de aprobación.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `controlar_confidencialidad_datos_sensibles`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `pii_detector` — no implementada

## Guardrails
- **Confidencialidad:** Minimización de datos por defecto.
- **Revision humana obligatoria:** HITL antes de compartir externamente.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No control de tono revictimizante (`controlar_no_revictimizacion`).
- No dictamen de aprobación (`clasificar_aprobacion_juridica`).

## Riesgo si se omite
Filtración de datos de la víctima o terceros con violación de Ley 1581.
