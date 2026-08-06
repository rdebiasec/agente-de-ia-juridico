<!-- config-version: 4; checksum: 0ed44002038dd402 -->
---
name: priorizar-objetivos-representacion
description: Contrato penal-víctimas: Listar y ordenar objetivos posibles de la representación de la víctima según urgencia, viabilidad y alineación con sus intereses, documentando trade-offs para decisión del abogado. Activar cuando el plan/HITL o el especialista requiera `priorizar_objet...
disable-model-invocation: true
---

# priorizar_objetivos_representacion

## Scope
- Category: `Skills de representacion de victimas`
- Skill ID: `priorizar_objetivos_representacion`
- Tier: `operativo`

## Used By Agents
- `analista_representacion_victimas`

## Purpose
Listar y ordenar objetivos posibles de la representación de la víctima según urgencia, viabilidad y alineación con sus intereses, documentando trade-offs para decisión del abogado.

## Rol en coordinador_caso
**MOVE:** este skill ya no es ownership del POC. El coordinador solo lo dispara vía tool del especialista dueño.

## Fuentes KB
- `agente/conocimiento/normas-clave.md` — priorizar seguridad, dignidad y enfoque diferencial; no prometer resultados.
- `agente/conocimiento/proceso-penal-906.md` — actuaciones posibles según etapa; sin `fecha_base` no certificar plazos.
- Tools reales: `leer_normas_clave`, `leer_playbook_proceso`, `buscar_en_conocimiento`.

## Inputs
- Intereses declarados por la víctima o el abogado (justicia, reparación, celeridad, protección, no confrontación).
- Etapa procesal aparente y actuaciones disponibles.
- Riesgos conocidos (revictimización, términos, debilidad probatoria).
- Objetivos procesales técnicos ya identificados (si existen).

## Outputs
- Lista ordenada: `objetivo`, `prioridad` (1–n), `razón`, `dependencia`, `riesgo` (procesal | probatorio | revictimización).
- Trade-offs explícitos para decisión del abogado (ej. celeridad vs. recaudo probatorio).
- Etiqueta: `PRELIMINAR — VALIDAR CON VÍCTIMA Y ABOGADO TITULAR`.

## Steps
0. Anclar derechos/etapa/no-revictimización a Fuentes KB; sin soporte → `[PENDIENTE DE VERIFICAR]`.
1. Listar objetivos posibles de la representación en el caso.
2. Ordenar por urgencia, viabilidad y alineación con intereses de la víctima.
3. Documentar trade-offs para decisión del abogado.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `priorizar_objetivos_representacion`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

## Guardrails
- **No inventar:** No inventar intereses de la víctima no expresados.
- **Pedir datos faltantes:** Sin input sobre intereses de la víctima, listar solo objetivos procesales genéricos marcados `[PENDIENTE DE VERIFICAR]`.
- **Separar hecho de inferencia:** Objetivos son hipótesis estratégicas, no hechos.
- **Revision humana obligatoria:** HITL obligatorio: estrategia de representación requiere aprobación del abogado y, cuando aplique, consulta con la víctima.
- **No revictimizar:** No presionar rutas que revictimicen (ej. confrontación pública innecesaria).
- **Aviso de borrador:** Aviso de borrador estratégico.

## No duplicar
- No construir teoría del caso (`construir_teoria_caso_victima`).
- No identificar intereses en profundidad (`identificar_intereses_victima`).
- No crear ruta procesal detallada (`crear_ruta_procesal_recomendada`).

## Riesgo si se omite
Estrategia desalineada con la víctima o priorización que sacrifica términos o prueba crítica.
