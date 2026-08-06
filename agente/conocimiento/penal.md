# Procesos penales (REQ-007)

**Última revisión:** 2026-08-05

## Ámbito

Representación de víctimas en investigación y juzgamiento penal bajo Ley 906.
La IA propone hipótesis tipicas y matrices; el abogado revisa, decide y firma.
No afirmar tipicidad definitiva ni inventar artículos del Código Penal.

## Normas clave Colombia

- Ley 906 de 2004 (Código de Procedimiento Penal)
- Ley 599 de 2000 (Código Penal)
- Constitución Política — garantías de acceso a la justicia y protección de víctimas

Ver también: `normas-clave.md`, `proceso-penal-906.md`.
Antes de citar un artículo concreto: `leer_normas_clave` / `buscar_en_conocimiento` y marcar `[PENDIENTE DE VERIFICAR]` si no está soportado en RAG.

## Marco tipico operativo (hipótesis, no imputación)

Usar este orden en análisis de tipicidad/responsabilidad:

1. **Hechos soportados** (cronología verificada) ≠ inferencias.
2. **Hipótesis de conducta** → tipos penales tentativos (`HIPÓTESIS PRELIMINAR — NO IMPUTACIÓN`).
3. **Descomposición del tipo** por elementos:
   - objetivos (conducta, resultado si aplica, nexo, tipicidad especial / sujeto);
   - subjetivos (dolo / culpa según el tipo);
   - normativos (solo con norma verificada).
4. **Autoría y participación** preliminar (autor, coautor, partícipe, sin_datos) sin imputación formal.
5. **Agravantes / atenuantes / cualificadoras** solo con hecho + norma verificada.
6. **Riesgo de atipicidad** y prueba faltante por elemento → matriz tipo–hecho–prueba.
7. Toda calificación a víctima/Fiscalía/memorial pasa por **HITL** del abogado.

## Elemento subjetivo (checklist de indicios)

Sin afirmar certeza. Separar hecho de indicio:

- Conocimiento del hecho / de la ilicitud (si consta).
- Voluntad o aceptación del resultado (dolo directo / eventual — hipótesis).
- Inobservancia del deber objetivo de cuidado (culpa — hipótesis).
- Si solo hay resultado dañoso sin indicios de conocimiento/voluntad → `indeterminado` + pendientes.

## Autoría y participación (categorías analíticas)

Etiquetas de trabajo (no condena):

| Rol preliminar | Cuándo usarlo |
|---|---|
| autor | Quien realiza la conducta típica según hechos soportados |
| coautor | División de trabajo / aporte esencial conjunto (hipótesis) |
| partícipe | Aporte accesorio (inducción, complicidad — hipótesis) |
| testigo / sin_datos | Mención sin conducta típica acreditada |

Normas concretas de autoría/participación del CP: **verificar en RAG**; no inventar números de artículo.

## Agravantes y atenuantes

- Solo registrar circunstancia con `hecho_soporte` + `norma_cp` verificada o `[PENDIENTE DE VERIFICAR]`.
- No usar “provocación” u otras fórmulas que culpen a la víctima sin base factual.
- No prometer pena ni resultado al cliente.

## Relación con skills

| Skill | Uso de esta KB |
|---|---|
| `identificar_conductas_punibles_preliminares` | §Marco tipico pasos 1–2 |
| `descomponer_elementos_tipo_penal` | §Marco tipico paso 3 |
| `analizar_dolo_culpa_elemento_subjetivo` | §Elemento subjetivo |
| `analizar_autoria_y_participacion` | §Autoría |
| `detectar_agravantes_atenuantes` | §Agravantes |
| `detectar_riesgos_atipicidad` / `mapear_tipo_penal_hecho_prueba` | pasos 5–6 |

## Notas del despacho

- Etiqueta de salida tipica: preliminar, revisable, no vinculante.
- En delitos sexuales / VIF: no presuponer consentimiento; aplicar no-revictimización (`g5`/`g6` y skills de representación).
