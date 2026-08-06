<!-- config-version: 3; checksum: 020d3e7a46b50d37 -->
---
name: generar-preguntas-aclaracion
description: Contrato penal-víctimas: Formular preguntas abiertas y no inductivas para cerrar ambigüedades factuales, dirigidas a víctima, testigos o abogado. Activar cuando el plan/HITL o el especialista requiera `generar_preguntas_aclaracion`. No sustituye a `generar_preguntas_tipicidad`.
disable-model-invocation: true
---

# generar_preguntas_aclaracion

## Scope
- Category: `Skills de hechos y cronologia`
- Skill ID: `generar_preguntas_aclaracion`
- Tier: `operativo`

## Used By Agents
- `analista_cronologia_hechos`
- `analista_evidencia`

## Purpose
Formular preguntas abiertas y no inductivas para cerrar ambigüedades factuales, dirigidas a víctima, testigos o abogado.

## Rol en analista_cronologia_hechos
Ejecutar tras `detectar_vacios_factuales` o `detectar_contradicciones_factuales`. Las preguntas requieren aprobación del abogado antes de enviarse a la víctima.

## Inputs
- Vacíos factuales o contradicciones documentadas.
- Cronología o matriz hecho-fuente.
- Destinatario previsto: víctima | testigo | abogado interno.
- Contexto de sensibilidad (violencia sexual, doméstica, etc.) si consta.

## Outputs
- Preguntas numeradas: `pregunta`, `objetivo_probatorio`, `destinatario`, `prioridad`, `riesgo` (revictimización | inducción | bajo).
- Orden por prioridad probatoria.
- Etiqueta: `REVISAR CON ABOGADO ANTES DE ENVIAR A VÍCTIMA`.

## Steps
1. Identificar puntos ambiguos o incompletos en la narrativa.
2. Redactar preguntas abiertas y no inductivas para víctima, testigos o abogado.
3. Ordenar preguntas por prioridad probatoria.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `generar_preguntas_aclaracion`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

## Guardrails
- **No inventar:** No presuponer respuesta en la formulación de la pregunta.
- **Revision humana obligatoria:** HITL obligatorio antes de contacto con víctima.
- **No revictimizar:** Evitar preguntas sobre vestimenta, conducta previa o vida íntima salvo estricta pertinencia probatoria y aprobación del abogado.
- **Confidencialidad:** No incluir datos sensibles de terceros en las preguntas.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- **vs `generar_preguntas_tipicidad`:** aclaración = lagunas factuales; tipicidad = elementos del tipo penal.
- No preguntas para audiencia formal (`preparar_preguntas_audiencia`).
- No preguntas a peritos (`generar_preguntas_testigos_peritos`).

## Riesgo si se omite
Lagunas factuales persisten o preguntas inductivas revictimizan y debilitan credibilidad en juicio.
