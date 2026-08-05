<!-- config-version: 2; checksum: b93d991fd9d4cb61 -->
---
name: evaluar-dano-y-afectacion
description: Contrato penal-víctimas: Describir preliminarmente el daño o afectación a la víctima con base documentada (físico, psicológico, patrimonial, social). Activar cuando el plan/HITL o el especialista requiera `evaluar_dano_y_afectacion`. No sustituye a `identificar_intereses_victi...
disable-model-invocation: true
---

# evaluar_dano_y_afectacion

## Scope
- Category: `Skills de representacion de victimas`
- Skill ID: `evaluar_dano_y_afectacion`
- Tier: `operativo`

## Used By Agents
- `analista_representacion_victimas`

## Purpose
Describir preliminarmente el daño o afectación a la víctima con base documentada (físico, psicológico, patrimonial, social).

## Rol en analista_representacion_victimas
Insumo para teoría del caso y pretensiones de reparación.

## Inputs
- Relatos, informes médicos/psicológicos, declaraciones (si constan).
- Hechos verificados del caso.
- Pretensiones de reparación ya planteadas.

## Outputs
- `tipos_daño`: físico | psicológico | patrimonial | social | otros.
- Por tipo: `descripción`, `fuente`, `gravedad_preliminar` (alta | media | baja | pendiente).
- Etiqueta: `AFECTACIÓN PRELIMINAR — NO ES PERITAJE`.

## Steps
1. Identificar tipos de daño o afectación alegados o documentados.
2. Vincular cada afectación con hechos y fuentes del expediente.
3. Señalar vacíos que requieran prueba pericial o documental.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `evaluar_dano_y_afectacion`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_expediente_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto

## Guardrails
- **No inventar:** No inventar diagnósticos ni secuelas.
- **No revictimizar:** No minimizar ni dramatizar el daño sin base.
- **Revision humana obligatoria:** HITL obligatorio antes de incorporar hallazgos a escritos o comunicación externa.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No pretensiones de reparación definitivas sin HITL.
- No intereses subjetivos (`identificar_intereses_victima`).

## Riesgo si se omite
Pretensiones de reparación desconectadas del daño real o documentado.
