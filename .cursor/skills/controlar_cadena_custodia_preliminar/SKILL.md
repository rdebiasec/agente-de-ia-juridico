---
name: controlar-cadena-custodia-preliminar
description: Skill critico penal-victimas: alertar si la evidencia puede requerir cadena de custodia. Use when the workflow requires `controlar_cadena_custodia_preliminar`.
disable-model-invocation: true
---

# controlar_cadena_custodia_preliminar

## Scope
- Category: `Skills de evidencia y soporte probatorio`
- Skill ID: `controlar_cadena_custodia_preliminar`
- Tier: `critico`

## Used By Agents
- `gestor_evidencia_y_soporte_probatorio`
- `analista_calidad_juridica`

## Purpose
Verificar si la evidencia requiere cadena de custodia formal y detectar rupturas que afecten admisibilidad.

## Rol en gestor_evidencia_y_soporte_probatorio
Ejecutar tras `inventariar_evidencia` o `preservar_evidencia_digital` en elementos físicos o digitales críticos.

## Rol en analista_calidad_juridica
Control final antes de citar evidencia en memorial o audiencia.

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
- `chain_of_custody_logger`
- `metadata_extractor`

## Guardrails (g1–g10)
- **g1:** No inventar custodios, fechas ni protocolos.
- **g3:** Ruptura documentada ≠ conclusión de inadmisibilidad automática.
- **g4:** HITL antes de descartar evidencia en estrategia.
- **g9:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No preservar digital (`preservar_evidencia_digital` — hash y copia).
- No inventariar (`inventariar_evidencia`).

## Riesgo si se omite
Evidencia clave excluida en audiencia por ruptura de custodia no detectada a tiempo.
