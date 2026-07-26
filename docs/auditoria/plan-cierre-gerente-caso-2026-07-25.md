# Plan de cierre — Gerente del Caso Penal y ship a producción

**Fecha:** 2026-07-25
**Alcance:** convertir la gerencia del caso en invariante de runtime, publicarla en producción y dejar constancia de lo que solo puede cerrar una persona.

---

## 1. Qué quedó implementado

El coordinador pasó de enrutador a **Gerente del Caso Penal**. El cambio no es de nombre: la verificación de completitud dejó de ser una instrucción al modelo y pasó a ser una regla de código.

| Área | Antes | Después |
|---|---|---|
| Verificación de completitud | Solo pedida en el prompt | Gate determinista en código (`src/agents/completeness.py`) |
| `datos_faltantes_bloqueantes` | Siempre lista vacía | Calculado por destino y riesgo |
| Estado del caso | Se re-derivaba del chat cada turno | Ledger persistido (faltantes, tareas, responsables, métricas) |
| Delegación con expediente incompleto | Posible | Bloqueada antes de invocar especialistas |
| HITL | Dos mecanismos en conflicto | Unificado en el plan aprobado |
| Fallback web | `/chat/plan` podía caer a `/chat` sin aprobación | Fallback eliminado |
| Plazo de tutela | Nacía al aprobar el borrador | Nace al registrar la radicación real |

### Piezas nuevas

- `src/agents/completeness.py` — gate, ledger y captura de pendientes de especialistas.
- `migrations/versions/0008_gerencia_loop.py` — columnas de ledger y métricas en `expedientes`.
- `tests/test_gerencia_loop.py` — invariantes del loop.
- `config/guardrails/agents/coordinador_expediente_penal/{input,output,tools}.md` — políticas editables del agente.

### El agent loop resultante

1. Clasificar la solicitud y la etapa aparente.
2. **Verificar completitud** (paso fijo, no opcional).
3. Detectar urgencia y priorizar términos.
4. Delegar al especialista, solo si el paso 2 pasó.
5. Sintetizar en una sola voz de despacho.
6. Verificar la salida y marcar lo no soportado.

Si el paso 2 no pasa, no se avanza a delegar. Al llegar datos nuevos, se vuelve a verificar.

### Mínimos exigidos por destino

- Consulta general u orientación: hechos mínimos.
- Ruta procesal, audiencias, seguimiento: radicado y etapa o última actuación.
- Redacción y tutela (alto riesgo): radicado, poder o calidad, última actuación y partes.

### Estado de pruebas al momento de este plan

- Suite completa sin smoke en vivo: 222 aprobadas, 1 omitida, 7 deseleccionadas.
- Smoke local del gate: plan incompleto sin especialistas; plan completo con redactor.
- Slack y HITL: 4 aprobadas.

---

## 2. Qué hace este cierre

```mermaid
flowchart LR
  planDoc[PlanDoc] --> tests[PytestSinSmoke]
  tests --> commit[CommitMain]
  commit --> push[PushOrigin]
  push --> render[RenderRedeploy]
  render --> migrate[Alembic0008]
  migrate --> smoke[SmokeProd]
  smoke --> human[ChecklistHumano]
```

### Commit

Se incluye el trabajo de gerencia junto con los cambios ya presentes en el árbol (portal de auditoría, autenticación, configuración y documentos de aprobación).

Se excluye deliberadamente:

- `.env` y cualquier archivo con secretos.
- `documentos/udemy_transcripts/` — material de curso de terceros; no se publica en el repositorio.
- `tools/visual-ui-editor/` — herramienta local del editor, ajena al producto.

### Deploy

Render redespliega desde `render.yaml` al recibir el push. Las migraciones corren al arrancar la aplicación por el camino ya existente en `src/storage/__init__.py`, que lleva Alembic hasta `0008`.

URL de producción: `https://agente-de-ia-juridico.onrender.com`

---

## 3. Criterios de PASS / FAIL del smoke

| Verificación | PASS | FAIL |
|---|---|---|
| Salud del servicio | `status: ok` y persistencia `postgres` | Cualquier otro valor o sin respuesta |
| Migración | Esquema en `0008`; el ledger acepta lectura y escritura | Error de columna inexistente |
| Gate incompleto | Plan en `awaiting_input`, único paso del gerente, sin especialistas | Aparece cualquier especialista |
| Gate completo | Plan en `pending_approval` e incluye el especialista correcto | Queda bloqueado con datos suficientes |
| Aprobación | Un plan en `awaiting_input` no se puede aprobar ni ejecutar | Se aprueba o ejecuta |
| Catálogo de auditoría | 10 guardrails y 90 skills | Conteos distintos |
| Portal de auditoría | Login entra y la aplicación carga igual que en local | El gate no se oculta o la app no carga |
| Slack | Mensaje sin datos mínimos responde pidiéndolos; no propone plan ejecutable | Propone plan ejecutable sin verificar |

Un FAIL no se oculta: se documenta con su causa y su bloqueo.

---

## 4. Resultado del cierre

Ejecutado el 2026-07-25. Commit `bb82c50` en `main`, deploy `dep-d9ilavsvikkc73cv1670` en vivo.

| Verificación | Resultado |
|---|---|
| Suite sin smoke en vivo | PASS — 222 aprobadas, 1 omitida |
| Salud de producción | PASS — `status: ok`, persistencia `postgres` |
| Migración | PASS — esquema en `0008`, seis columnas del ledger presentes |
| Smoke de infraestructura | PASS — 0 fallos |
| Gate incompleto en producción | PASS — `awaiting_input`, solo el gerente, faltantes reportados |
| Aprobación de plan incompleto | PASS — rechazada con HTTP 400 |
| Gate completo en producción | PASS — `pending_approval` con el redactor incluido |
| Ledger en producción | PASS — bloqueo registrado y tarea cerrada al llegar el dato |
| Login del portal, local y producción | PASS en ambos, con el mismo login |
| Slack | PASS — 6 pruebas verdes, socket activo, `awaiting_input` manejado |

Detalle y evidencia en [`smoke-gerencia-2026-07-25.md`](smoke-gerencia-2026-07-25.md) y [`smoke-produccion-reporte.md`](smoke-produccion-reporte.md).

Dos checks de smoke daban falso FAIL por estar desactualizados frente al rediseño del portal y frente a `DEV_AUTO_LOGIN`. Se corrigieron los scripts, no el producto.

## 5. Riesgo detectado en el smoke

La base que producción usa hoy es `agente-db` (plan gratuito) y tiene fecha de expiración **2026-08-16**. El workspace además conserva una segunda base, `agente-ia-juridico-db` (plan básico), que ya no recibe escrituras.

Sin acción, los datos del caso en producción desaparecen en pocas semanas. La decisión de a cuál base apuntar y con qué plan es del dueño del proyecto, no del código.

## 6. Pendiente humano

Estos puntos no se pueden cerrar con código y quedan abiertos a propósito.

- **Base de datos de producción:** migrar a un plan que no expire y retirar la base que quedó sin uso. Ver la sección anterior.
- **DPA y contratos de tratamiento de datos:** sin firmar. Requiere decisión y firma del despacho.
- **Cuentas individuales por abogado:** hoy el acceso es por contraseña compartida. Falta identidad por persona para trazabilidad real de quién aprueba.
- **WhatsApp y Twilio:** integración inactiva a propósito. No se habilita sin evaluación previa frente a la Ley 1581 y la Ley 2300.
- **Checklist regulatorio REQ-001 a REQ-050:** sin validación humana registrada.
- **HITL de Slack de punta a punta:** `scripts/smoke_slack_hitl_drafts.py` publica borradores reales en `#revision-abogado` y exige que una persona pulse Aprobar y Rechazar. No se ejecutó para no dejar ruido en el canal del despacho.

---

## 7. Criterio de hecho de este cierre

- [x] Este documento publicado en `docs/auditoria/`.
- [x] Commit en `main` con el trabajo de gerencia, sin secretos ni material de terceros.
- [x] Push a `origin` completado.
- [x] Deploy de Render en vivo, con salud correcta y migración `0008` aplicada.
- [x] Smoke de producción ejecutado, con resultado PASS.
- [x] Pendiente humano listado sin declararlo cerrado.
