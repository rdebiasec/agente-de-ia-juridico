---
name: generar-preguntas-aclaracion
description: Skill operativo penal-victimas: crear preguntas para victima, testigos o abogado humano sin inducir respuestas. Use when the workflow requires `generar_preguntas_aclaracion`.
disable-model-invocation: true
---

# generar_preguntas_aclaracion

## Scope
- Category: `Skills de hechos y cronologia`
- Skill ID: `generar_preguntas_aclaracion`
- Tier: `operativo`

## Used By Agents
- `analista_cronologia_hechos_penales`
- `gestor_evidencia_y_soporte_probatorio`

## Purpose
Formular preguntas abiertas y no inductivas para cerrar ambigüedades factuales, dirigidas a víctima, testigos o abogado.

## Rol en analista_cronologia
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
- Sin herramientas obligatorias

## Guardrails (g1–g10)
- **g1:** No presuponer respuesta en la formulación de la pregunta.
- **g4:** HITL obligatorio antes de contacto con víctima.
- **g5:** Evitar preguntas sobre vestimenta, conducta previa o vida íntima salvo estricta pertinencia probatoria y aprobación del abogado.
- **g6:** No incluir datos sensibles de terceros en las preguntas.
- **g8:** Aviso de revisión profesional.

## No duplicar
- **vs `generar_preguntas_tipicidad`:** aclaración = lagunas factuales; tipicidad = elementos del tipo penal.
- No preguntas para audiencia formal (`preparar_preguntas_audiencia`).
- No preguntas a peritos (`generar_preguntas_testigos_peritos`).

## Riesgo si se omite
Lagunas factuales persisten o preguntas inductivas revictimizan y debilitan credibilidad en juicio.
