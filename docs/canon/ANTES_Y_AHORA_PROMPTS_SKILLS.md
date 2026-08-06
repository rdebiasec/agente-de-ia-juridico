# Antes y ahora — prompts y skills

Resumen simple de qué estaba mal y cómo quedó. Sin tecnicismos innecesarios.

---

## Tabla rápida

| Tema | Antes | Ahora |
|---|---|---|
| Prompt del especialista de evidencia | 8 líneas (casi vacío) | 67 líneas (completo) |
| Descripciones de skills genéricas | 81 de 81 | 0 |
| Skills con "dueño" equivocado (IDs viejos) | 48 casos | 0 |
| Skills sin regla de "no duplicar" | 12 | 0 |
| Ejemplos por prompt de especialista | 1 (algunos) | 2 o más (todos) |
| Bloques copiados a mano (riesgo de descuadre) | 8–9 prompts | Plantilla única compartida |
| Guía para repetir la revisión con expertos | No existía | Documento maestro creado |
| Pruebas que avisan si algo se rompe | No cubrían esto | 8 pruebas nuevas, todas en verde |

---

## 1. El especialista de evidencia estaba casi vacío

**Antes:** su instrucción tenía solo 8 líneas. No decía su misión, sus límites ni su formato de salida. En la práctica, ese "experto" no aportaba criterio propio.

**Ahora:** tiene misión, pasos, límites (no alterar evidencia, cuidar cadena de custodia), formato de salida y 2 ejemplos.

**Por qué importa:** un especialista sin instrucciones claras se diluye y el resto del equipo trabaja sin su aporte real.

---

## 2. Las descripciones de skills no servían

**Antes:** las 81 terminaban con la misma frase de relleno:

```
Use when the workflow requires `nombre_del_skill`
```

Eso no le dice a nadie cuándo usar el skill.

**Ahora:** cada una explica qué hace y cuándo activarla. Ejemplo real:

```
Contrato penal-víctimas: recopilar y numerar los elementos probatorios
con metadatos y custodia preliminar. Activar cuando el plan o el especialista
lo requiera. No sustituye a `clasificar_tipo_prueba`.
```

**Por qué importa:** una buena descripción evita que se use el skill equivocado.

---

## 3. Muchos skills apuntaban a "dueños" que ya no existen

**Antes:** 48 secciones mencionaban nombres viejos de agentes (`analista_tipicidad`, `preparador_audiencias`, `gestor_evidencia`, etc.) que ya se renombraron.

**Ahora:** todos usan los nombres actuales del equipo (`analista_responsabilidad_tipicidad`, `analista_audiencias`, `analista_evidencia`, etc.).

**Por qué importa:** si la documentación nombra dueños inexistentes, nadie sabe quién es responsable de cada tarea.

---

## 4. Faltaban reglas de "no duplicar"

**Antes:** 12 skills no aclaraban qué NO les corresponde, y se pisaban con otros.

**Ahora:** todos tienen una sección que dice a qué skill vecino derivar. Ejemplo: `inventariar_evidencia` aclara que no clasifica tipos de prueba ni arma el plan de recaudo (eso es de otros).

**Por qué importa:** evita trabajo repetido y respuestas contradictorias.

---

## 5. Los especialistas tenían pocos ejemplos

**Antes:** varios prompts traían un solo ejemplo, casi siempre "el caso que sale bien".

**Ahora:** cada especialista tiene al menos 2, incluyendo un caso de "qué NO hacer" (por ejemplo: negarse a inventar una hora, o rechazar preparar una tutela porque está fuera del producto).

**Por qué importa:** los ejemplos de error enseñan al asistente a poner límites.

---

## 6. Bloques copiados a mano

**Antes:** dos bloques de texto se repetían pegados en 8–9 prompts. Cambiar uno y olvidar los demás causaba descuadres.

**Ahora:** existe una plantilla única (`agente/prompts/_shared/backoffice_fragments.md`) como fuente de referencia.

**Por qué importa:** un solo lugar que actualizar en lugar de nueve.

---

## 7. No había forma de repetir esta revisión

**Antes:** la calidad dependía del criterio de quien mirara en el momento.

**Ahora:** hay un documento maestro que organiza la revisión como un panel de expertos (abogado penal, ingeniero de prompts, arquitecto, cumplimiento de datos, calidad y experiencia de usuario), cada uno con su pregunta y una rúbrica de puntaje.

**Por qué importa:** la próxima revisión sigue el mismo estándar, sin improvisar.

---

## 8. Ahora hay pruebas que avisan si algo se rompe

Se agregaron 8 pruebas automáticas que fallan si:

- vuelve una descripción genérica,
- reaparece un nombre de agente viejo,
- el prompt de evidencia se queda sin misión,
- un skill pierde su regla de "no duplicar".

Estado actual: **todas en verde.**

---

## Dónde ver el detalle

- Guía de revisión: `docs/canon/PROMPT_REVISION_PROMPTS_Y_SKILLS.md`
- Informe de hallazgos: `docs/canon/INFORME_AUDITORIA_PROMPTS_SKILLS.md`
- Plantilla compartida: `agente/prompts/_shared/backoffice_fragments.md`
- Pruebas: `tests/test_prompt_skill_quality.py`
