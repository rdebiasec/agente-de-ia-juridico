# Auditoria de baseline Fase 0

Fecha: 2026-06-26

Objetivo: clasificar cambios pendientes para cierre de Fase 0 sin activar canales.

## Cambios imprescindibles para cierre Fase 0

- `src/agents/guardrails.py`
  - Normaliza salida y evita disclaimer duplicado.
  - Refuerza consistencia de respuestas dentro del alcance.
- `src/agents/runner.py`
  - Bloquea solicitudes fuera de Fase 0 de forma uniforme.
  - Evita respuestas mixtas que filtren capacidades de fases posteriores.
- `tests/test_fase0.py`
  - Agrega regresiones para bloqueo de estrategia/riesgo y consultas mixtas.
  - Verifica deduplicacion de disclaimer.
- `tests/test_validation.py`
  - Endurece validaciones de UI/manual de pruebas.
- `static/login.html`, `static/chat.css`, `static/index.html`, `static/GUIA_FASE0.html`
  - Ajustes de UX para flujo de validacion y autenticacion Fase 0.
- `.env.example`
  - Documenta `DEV_AUTO_LOGIN` para operacion local.

## Cambios diferibles (no bloquean cierre tecnico de Fase 0)

- `agente/fuente/GUIA_PROYECTO_AGENTE_JURIDICO.md`
- `documentos/texto/GUIA_PROYECTO_AGENTE_JURIDICO.md`

Estos archivos son de contenido documental extenso y no afectan ejecucion,
auth ni guardrails del sistema Fase 0.

## Conclusion de auditoria

Para un baseline limpio de Fase 0:
- mantener los cambios funcionales y de pruebas listados como imprescindibles,
- separar los cambios documentales extensos en un lote aparte si se desea un PR
  mas facil de revisar.
