---
name: controlar-confidencialidad-datos-sensibles
description: Skill atomico penal-victimas: detectar datos sensibles o innecesarios. Use when the workflow requires `controlar_confidencialidad_datos_sensibles`.
disable-model-invocation: true
---

# controlar_confidencialidad_datos_sensibles

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `controlar_confidencialidad_datos_sensibles`
- Tier: `operativo`

## Used By Agents
- `analista_calidad_juridica`

## Purpose
Detectar y mitigar exposición innecesaria de datos personales sensibles en salidas del sistema.


## Rol en calidad
Control de minimización y datos sensibles antes de salidas externas.
## Inputs
- Texto o documento a revisar.
- Destinatario previsto (interno, cliente, juzgado, tercero).

## Outputs
- `datos_sensibles_detectados`: tipo | fragmento | necesidad (necesario | reducible | eliminar).
- `recomendacion`: publicar | redactar | solo_abogado.
- Etiqueta: `CONTROL LEY 1581 / DATOS SENSIBLES`.

## Steps
1. Identificar datos personales sensibles en la salida.
2. Evaluar si son necesarios para el fin procesal.
3. Proponer redacción o seudonimización cuando sea posible.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `pii_detector`

## Guardrails (g1–g10)
- **g6:** Minimización de datos por defecto.
- **g4:** HITL antes de compartir externamente.
- **g8:** Aviso de revisión profesional.

## Riesgo si se omite
Filtración de datos de la víctima o terceros con violación de Ley 1581.
