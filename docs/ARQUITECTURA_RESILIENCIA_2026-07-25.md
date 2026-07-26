# Reporte de endurecimiento y resiliencia — firma virtual penal-víctimas

Fecha: 2026-07-25  
Alcance: supervisor, especialistas, HITL, PII, RAG, planes, expediente, observabilidad y evaluaciones.

## 1. Resumen ejecutivo

Se cerraron los riesgos P0/P1 identificados en la revisión anterior y se
incorporaron controles P2 de operación. La decisión principal es estructural:
el chat ordinario ya no tiene acceso a las herramientas de redacción ni tutela.
Esas capacidades solo pueden ejecutarse como pasos de un plan aprobado.

La arquitectura conserva el modelo de producto:

- Gerente del Caso Penal como único interlocutor;
- especialistas como backoffice;
- la IA propone y el abogado aprueba;
- ninguna cita, norma, radicado o dato del caso se considera verificado por
  aparecer en la salida del modelo.

## 2. Cambios por riesgo

### R1 — puerta única para capacidades de alto riesgo

Estado: implementado.

- `build_orchestrator` permite excluir físicamente las tools de alto riesgo.
- `run_agent` usa el orquestador sin redactor ni evaluador de tutela.
- El plan aprobado instancia directamente el agente declarado en cada paso.
- La detección por regex continúa ayudando al UX, pero dejó de ser la barrera
  de seguridad.

Resultado: una frase oblicua o un error de triage no puede invocar redacción o
tutela desde el chat.

### R2 — política de PII calibrada

Estado: implementado.

- Se separaron contactos operativos (`email`, `phone`) de PII sensible del
  expediente (`document_id`, `address`, `protected_name`).
- Una salida con email o teléfono ya no dispara la destrucción completa de la
  respuesta.
- Documento, dirección y nombres etiquetados de víctima/menor se enmascaran
  fuera de un plan aprobado.
- Los previews, trazas y mensajes de rechazo continúan enmascarando toda PII.
- El plan aprobado puede conservar datos necesarios para el borrador interno,
  en coherencia con REQ-039 y la autorización de datos de casos.

Resultado: menos falsos positivos sin relajar la protección de víctimas y
menores.

### R3 — frontera contra prompt injection indirecto

Estado: implementado.

- El expediente, los resultados RAG y las salidas previas se delimitan como
  contenido no confiable.
- Las líneas con instrucciones de override, revelación de prompts o bypass de
  guardrails se eliminan antes de inyectarse.
- La detección queda registrada en la traza.
- `contexto_para_prompt` aplica la misma sanitización a las herramientas RAG.

Resultado: documentos y hechos siguen siendo datos, no instrucciones.

### R4 — fail-fast y DAG real

Estado: implementado.

- Se valida unicidad de `step_id`, existencia de dependencias y ausencia de
  ciclos.
- Los pasos se ordenan topológicamente, conservando orden estable.
- Cada paso recibe únicamente las salidas de sus dependencias declaradas.
- Un paso `blocked` detiene el plan; los pendientes quedan `skipped`.
- El estado final es `failed` si nada terminó o `partial` si hubo resultados
  previos. Un plan incompleto ya no aparece como `done`.

Resultado: estado honesto y sin propagación de errores al redactor.

### R5 — checkpoints, recuperación y multi-worker

Estado: implementado sin exigir infraestructura adicional.

- Se persiste checkpoint antes y después de cada paso: owner, timestamp,
  paso actual y salidas por paso.
- En restart/deploy, los planes `executing` huérfanos vuelven a `approved`
  para reanudarse desde los pasos ya completados.
- Una lease temporal evita ejecución simultánea desde dos workers.
- SSE mantiene entrega inmediata local y consulta los eventos persistidos
  cuando productor y suscriptor están en workers distintos.

Resultado: recuperación durable sobre Postgres. Redis queda opcional para una
escala de eventos superior, no como requisito de corrección.

### R6 — degradación explícita del RAG

Estado: implementado.

- El embedding hash se conserva solo para pruebas deterministas de ingesta.
- Runtime, tools y API suprimen sus resultados cuando el embedding semántico
  no está disponible.
- La traza marca `grounding_degraded`; la API responde
  `grounding_status=degraded`.

Resultado: ningún vector hash se presenta como fragmento jurídicamente
relevante.

### R7 — expediente sin read-modify-write inseguro

Estado: implementado.

- El repositorio expone `mutate_expediente`.
- Memoria usa lock reentrante.
- Postgres usa transacción y `SELECT ... FOR UPDATE`.
- Completitud, resultados de especialistas y sincronización desde chat fusionan
  cambios sobre el estado más reciente.

Resultado: se reducen pérdidas de tareas, faltantes y métricas por concurrencia.

### R8 — watchdog de costo, timeout, retry y fallback

Estado: implementado.

- Presupuesto total de tokens por ejecución.
- Timeout separado para chat y paso de plan.
- Reintentos acotados con backoff.
- Modelo alterno configurable.
- Los excesos de presupuesto se detienen con respuesta controlada y traza.

Variables nuevas:

- `OPENAI_MODEL_FALLBACK`
- `AGENT_RUN_TIMEOUT_SECONDS`
- `AGENT_PLAN_STEP_TIMEOUT_SECONDS`
- `AGENT_MAX_RETRIES`
- `AGENT_MAX_TOTAL_TOKENS`
- `PLAN_STALE_AFTER_SECONDS`

### R9 — cierre del loop HITL

Estado: implementado.

- Aprobar, editar o rechazar publica el resultado en la sesión de origen.
- La aprobación indica el artefacto disponible.
- El rechazo devuelve el comentario para corrección.
- Los eventos usan marcador idempotente para no duplicarse ante reintentos de
  Slack.

Resultado: la aprobación deja de ser un estado aislado en la base de datos.

### R10 — evaluaciones de seguridad y comportamiento

Estado: implementado en la suite de regresión.

Se añadieron casos para:

- ausencia estructural de tools de alto riesgo en chat;
- prompt injection indirecto;
- contactos permitidos y PII sensible enmascarada;
- orden DAG, ciclos y dependencias inexistentes;
- mutaciones atómicas del expediente;
- cierre idempotente del HITL.

El canary continúa siendo shadow-only y nunca promueve prompts automáticamente.

## 3. Observabilidad

Las trazas ahora incluyen:

- reintentos y modelo alterno;
- presupuesto excedido;
- estado de grounding;
- señales de contenido no confiable;
- checkpoints del plan;
- estado `partial`;
- replay durable de eventos.

Los previews de entrada, salida y completions se enmascaran antes de persistir.

## 4. Compatibilidad y decisiones

- No se cambió la topología Supervisor + especialistas-as-tools.
- No se activó WhatsApp.
- No se eliminó el fallback hash de pruebas; se impidió su uso como grounding.
- No se introdujo una cola externa obligatoria. Postgres es el checkpoint
  durable; Redis puede agregarse para throughput, no para integridad básica.
- Los borradores aprobados pueden contener datos completos porque son
  artefactos internos autorizados; chat, logs y previews no.

## 5. Verificación

Comandos:

```bash
.venv/bin/python scripts/run_agent_evals.py
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest -q
git diff --check
```

La evidencia final de ejecución se consigna en el reporte de entrega de la
conversación. Cualquier fallo de la suite completa debe impedir considerar
terminada esta intervención.

## 6. Riesgos remanentes

1. El lock de creación de un expediente inexistente depende de la restricción
   única de Postgres; conviene medir conflictos si se escala a muchos writers.
2. El detector de nombres protegidos es deliberadamente conservador y depende
   de etiquetas como “víctima” o “menor”; NER especializado sería una mejora
   futura, sujeto a evaluación de privacidad.
3. El retry no debe usarse para errores de política: guardrails y presupuesto
   están explícitamente excluidos del reintento.
4. Evals jurídicos semánticos con juez LLM requieren dataset aprobado por el
   abogado y ejecución controlada por costo; no deben auto-promover prompts.

## 7. Criterio de aceptación

La entrega se considera aceptable únicamente si:

- evals deterministas = 100 %;
- suite completa sin fallos;
- ningún tool de redacción/tutela aparece en el chat normal;
- un paso bloqueado no produce plan `done`;
- RAG degradado no devuelve resultados;
- el resultado HITL aparece en la sesión de origen.

## 8. Conciliación con auditorías independientes

Tras la implementación, se conciliaron los hallazgos de:

- auditoría de seguridad/RAG;
- auditoría de planes/concurrencia;
- auditoría de runtime/HITL/evals.

### Cubiertos en esta entrega

| Hallazgo | Estado |
|---|---|
| Chat con tools de alto riesgo | Cerrado: `include_high_risk_tools=False` |
| PII tripwire all-or-nothing | Cerrado: mascara sensible; contactos no destruyen salida |
| Injection vía RAG/expediente | Cerrado: `context_security` + spotlighting |
| RAG hash como grounding | Cerrado: se suprime en runtime/API/tools |
| `depends_on` decorativo / no fail-fast | Cerrado: DAG + `partial`/`failed` |
| Planes `executing` huérfanos | Cerrado: checkpoint + recover on startup |
| Carreras de expediente | Cerrado: `mutate_expediente` + `FOR UPDATE` |
| Timeout/retry/fallback/presupuesto | Cerrado: `resilience.run_with_retries` |
| HITL Slack sin retorno a sesión | Cerrado: publicación idempotente en chat |
| Mensaje de presupuesto confundido con guardrail | Cerrado en follow-up |
| Reintentos sobre errores no transitorios | Cerrado: filtro + jitter |
| IDOR `buscar_en_expediente` | Cerrado: `session_context` |

### Remanentes conscientes (no bloqueantes)

1. Modal Slack de “Editar” — la API web ya tiene `/drafts/{id}/edit`; falta UI Slack.
2. Allowlist de aprobadores Slack por user ID.
3. Golden-transcripts LLM-mocked end-to-end (más allá de evals deterministas).
4. Canary condicional en CI solo cuando cambian prompts.
5. Cap de `stream_events` / tabla hija para evitar crecimiento O(n²) en planes muy largos.
6. Presupuesto por sesión/día y costo monetario (hoy es por ejecución y en tokens).

Estos remanentes no reabren los P0 de la revisión original.
