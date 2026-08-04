## Nota (2026-08-03)

REQ-038…042 (acciones de tutela) **retirados del producto**. Checklist activo = 45 requisitos.

# Checklist REQ-001…050 — estado de cierre

Fuente: `agente/requisitos/requisitos_asistente.json`.  
Leyenda: **código** = capacidad en agentes/API · **prueba** = validación manual pendiente · **parcial** · **diferido**.

## Cómo cerrar

Para cada REQ: ejecutar una prueba corta en web (o Slack) y marcar `activo` + nota de prueba en el JSON, o dejar `diferido` con motivo.

## Bloques (resumen operativo 2026-07-24)

| Bloque | REQ aprox. | Código | Prueba formal |
|--------|------------|--------|---------------|
| Perfil / tono / áreas | 001–011 | listo | pendiente checklist |
| Hechos / tipicidad / ruta 906 | 012–025 | listo | pendiente checklist |
| Víctimas / evidencia / audiencias | 026–037 | listo | pendiente checklist |
| Tutela / constitucional | 038–042 | mejorado (`output_type=Tutela` en evaluador) | pendiente checklist |
| Seguimiento / informes | 043–047 | parcial (agente + plazos) | pendiente / integraciones externas |
| Calidad / HITL / canales | 048–050 | web+HITL listo; Slack token prod pendiente | pendiente |

**WhatsApp:** diferido — no construir hasta decisión 1581/2300.

Este archivo no sustituye el JSON de requisitos; es el tablero de cierre para gerencia.
