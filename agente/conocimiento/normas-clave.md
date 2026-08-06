# Normas clave penal-víctimas (REQ-011)

**Última revisión:** 2026-08-05

## Marco normativo principal

- Ley 906 de 2004 (Código de Procedimiento Penal).
- Ley 599 de 2000 (Código Penal), según el tipo penal investigado.
- Constitución Política: debido proceso, acceso a la justicia y derechos de las víctimas.

## Derechos de las víctimas

- Información clara y oportuna sobre el avance del proceso.
- Participación en actuaciones relevantes según Ley 906.
- Protección frente a riesgos de revictimización y amenazas.
- Reparación integral cuando legalmente proceda.

## Criterio operativo del despacho

- Priorizar seguridad, dignidad y enfoque diferencial de la víctima.
- Sustentar cada recomendación en etapa procesal, evidencia disponible y riesgo.
- Tipicidad y ruta = preliminares; piezas accionables pasan por HITL/abogado.

## Checklist representación de víctimas (ancla skills O5)

Uso operativo para `analista_representacion_victimas` (sin inventar artículos):

1. Leer este archivo y `agente/conocimiento/proceso-penal-906.md` (rol + checklist intervención).
2. Separar **intereses** (expectativas de la víctima) de **derechos** procesales (participación, información, protección, reparación).
3. Teoría del caso = preliminar; etiqueta implícita: aprobación abogado (y víctima cuando aplique).
4. Daño/afectación = narrado o documentado; **no es peritaje**; sin soporte → pendiente.
5. Enfoque diferencial: solo factores documentados (edad, género, discapacidad, etnia, etc.); no inferir ni estigmatizar.
6. Riesgo de revictimización: lenguaje que culpe/minimice/exponga; detalle gráfico innecesario → mitigar o escalar.
7. Objetivos priorizados sin prometer resultados judiciales; trade-offs explícitos para el abogado.
8. Comunicación al cliente o pieza accionable → HITL abogado.

## Checklist tipicidad (ancla para skills O1)

Antes de citar CP o cerrar hipótesis:

1. Leer `agente/conocimiento/penal.md` (marco tipico) vía `leer_area_derecho(penal)` / `buscar_en_conocimiento`.
2. Cruzar etapa con `agente/conocimiento/proceso-penal-906.md` cuando la tipicidad dependa de momento procesal.
3. Separar hecho confirmado / narrado / inferido.
4. No sembrar `art. N` sin verificación; usar `[PENDIENTE DE VERIFICAR]`.

## Checklist evidencia / integridad (ancla skills O4)

1. Leer checklist en `agente/conocimiento/proceso-penal-906.md` (evidencia/prueba).
2. No inventar folios, hashes, custodios ni peritajes.
3. Integridad > conveniencia: no “limpiar” metadatos ni alterar originales.
4. Suficiencia = preliminar; nunca certeza judicial ni culpa de la víctima por brechas.
5. Piezas o diligencias accionables (oficios, pericias, contacto a terceros) → HITL abogado.

## Advertencia / Regla de citación

Verificar vigencia y modificaciones antes de citar artículos concretos en escritos.
Sin soporte en KB/RAG → `[PENDIENTE DE VERIFICAR]`. No inventar radicados, sentencias ni numerales.
