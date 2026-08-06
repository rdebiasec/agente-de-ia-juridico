<!-- config-version: 3; checksum: 2c8bb10156dc1210 -->
---
name: crear-ruta-procesal-recomendada
description: Contrato penal-víctimas: Proponer secuencia de próximos pasos procesales para la representación de la víctima, con responsables y plazos, para revisión del abogado. Activar cuando el plan/HITL o el especialista requiera `crear_ruta_procesal_recomendada`. No sustituye a `evalua...
disable-model-invocation: true
---

# crear_ruta_procesal_recomendada

## Scope
- Category: `Skills de ruta procesal Ley 906`
- Skill ID: `crear_ruta_procesal_recomendada`
- Tier: `estrategico`

## Used By Agents
- `analista_ruta_procesal` (uso principal)

## Purpose
Proponer secuencia de próximos pasos procesales para la representación de la víctima, con responsables y plazos, para revisión del abogado.

## Rol en analista_ruta_procesal
Producto integrador del agente. Ejecutar tras etapa, actuaciones mapeadas, oportunidad y riesgos procesales.

## Rol en coordinador_caso
**MOVE:** este skill ya no es ownership del POC. El coordinador solo lo dispara vía tool del especialista dueño.

## Fuentes KB
- `agente/conocimiento/proceso-penal-906.md` — etapas, enum `etapa_ley906`, términos (días hábiles).
- `agente/conocimiento/normas-clave.md` — criterio operativo y derechos de víctima.
- Herramientas: `leer_playbook_proceso(penal)`, `leer_normas_clave`, `buscar_en_conocimiento` antes de afirmar etapa/plazos.
## Inputs
- Etapa procesal actual (confirmada o `[PENDIENTE DE VERIFICAR]`).
- Actuaciones pendientes y últimas actuaciones del radicado.
- Objetivos preliminares de la víctima (si constan).
- Términos o audiencias próximas conocidas.
- Riesgos procesales (`detectar_riesgos_procesales`).

## Outputs
- Ruta numerada: paso, actuación, responsable, plazo estimado, dependencia.
- Riesgos procesales de la ruta (oportunidad, improcedencia, extemporaneidad).
- Agentes IA o abogados sugeridos por paso.
- Etiqueta: `BORRADOR PARA REVISIÓN — NO EJECUTAR SIN APROBACIÓN`.

## Steps
0. Anclar etapa/ruta a `proceso-penal-906.md` (enum `etapa_ley906`); términos en días hábiles; sin `fecha_base` no certificar plazos.
1. Partir de `etapa_ley906` canónica (playbook) e intereses de la víctima.
2. Proponer secuencia numerada: actuación, responsable, dependencia, plazo estimado (días hábiles / ESTIMACIÓN IA).
3. Separar recomendación de decisión del abogado; HITL para piezas accionables.
4. Registrar riesgos (oportunidad, improcedencia) y pendientes.


## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `crear_ruta_procesal_recomendada`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `task_manager_create` — no implementada
- `audit_log_write` — no implementada

## Guardrails
- **No inventar:** No citar artículos Ley 906 sin verificar en RAG.
- **Pedir datos faltantes:** Sin etapa ni radicado, no proponer ruta cerrada.
- **Separar hecho de inferencia:** Distinguir hechos del expediente de supuestos para planificar.
- **Revision humana obligatoria:** HITL obligatorio: estrategia procesal no se ejecuta sin firma.
- **No revictimizar:** Ruta centrada en derechos de la víctima.
- **Oportunidad y terminos Ley 906:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **Aviso de borrador:** Aviso de borrador y revisión profesional.

## No duplicar
- No evaluar oportunidad de cada actuación (`evaluar_oportunidad_procesal`).
- No redactar memoriales (`redactor_documentos_juridicos`).

## Riesgo si se omite
Actuaciones desordenadas o extemporáneas en representación de víctimas bajo Ley 906.
