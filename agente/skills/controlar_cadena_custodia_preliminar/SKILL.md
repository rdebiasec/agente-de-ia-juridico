<!-- config-version: 5; checksum: 8b40ee1430d87eeb -->
---
name: controlar-cadena-custodia-preliminar
description: Contrato penal-víctimas: Verificar si la evidencia requiere cadena de custodia formal y detectar rupturas que afecten admisibilidad. Activar cuando el plan/HITL o el especialista requiera `controlar_cadena_custodia_preliminar`. No sustituye a `preservar_evidencia_digital`.
disable-model-invocation: true
---

# controlar_cadena_custodia_preliminar

## Scope
- Category: `Skills de evidencia y soporte probatorio`
- Skill ID: `controlar_cadena_custodia_preliminar`
- Tier: `critico`

## Used By Agents
- `analista_evidencia`
- `analista_calidad_juridica`

## Purpose
Verificar si la evidencia requiere cadena de custodia formal y detectar rupturas que afecten admisibilidad.

## Rol en analista_evidencia
Ejecutar tras `inventariar_evidencia` o `preservar_evidencia_digital` en elementos físicos o digitales críticos.

## Rol en analista_calidad_juridica
Control final antes de citar evidencia en memorial o audiencia.

## Fuentes KB
- Inventario/metadatos del expediente; no inventar custodios, fechas ni protocolos.
- `agente/conocimiento/proceso-penal-906.md` — alerta de ruptura vs admisibilidad (preliminar; no dictamen pericial).
- `agente/conocimiento/normas-clave.md` — integridad probatoria; HITL antes de descartar evidencia en estrategia.
- Tools reales: `buscar_en_expediente`, `buscar_en_conocimiento` (logger de custodia = Planned).

## Inputs
- Inventario de evidencia (`inventariar_evidencia`) con origen, fecha y custodio.
- Protocolo de recolección documentado (si existe).
- Tipo de prueba: biológica, digital, arma, documento original, etc.

## Outputs
- `requiere_cadena_formal`: sí | no | `[PENDIENTE DE VERIFICAR]`.
- `registro_custodia`: quién recolectó, cuándo, dónde, traslados, almacenamiento.
- `rupturas_detectadas`: lista con impacto en admisibilidad (alto | medio | bajo).
- `medidas_correctivas`: perito, oficio, nueva copia forense, etc.
- Etiqueta: `CUSTODIA PRELIMINAR — NO AFIRMAR ADMISIBILIDAD SIN PERITO/AUTORIDAD`.

## Steps
1. Identificar evidencia que exija cadena de custodia formal.
2. Revisar recolección: quién, cuándo, dónde y protocolo usado.
3. Verificar traslado, almacenamiento y cadena de acceso documentada.
4. Detectar rupturas o vacíos que afecten admisibilidad.
5. Alertar necesidad de perito, cadena certificada u oficio urgente.
6. Proponer medidas correctivas sin alterar el elemento probatorio.
7. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `controlar_cadena_custodia_preliminar`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `chain_of_custody_logger` — no implementada
- `metadata_extractor` — no implementada

## Guardrails
- **Integridad probatoria:** Documentar custodia, rupturas y riesgos de admisibilidad sin alterar evidencia.
- **No inventar:** No inventar custodios, fechas ni protocolos.
- **Separar hecho de inferencia:** Ruptura documentada ≠ conclusión de inadmisibilidad automática.
- **Revision humana obligatoria:** HITL antes de descartar evidencia en estrategia.
- **Oportunidad y terminos Ley 906:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No preservar digital (`preservar_evidencia_digital` — hash y copia).
- No inventariar (`inventariar_evidencia`).

## Riesgo si se omite
Evidencia clave excluida en audiencia por ruptura de custodia no detectada a tiempo.
