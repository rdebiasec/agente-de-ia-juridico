#!/usr/bin/env python3
"""Refina skills Fase 2 (multi-agente) y Fase 3 (operativos) al estándar Fase A."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".cursor" / "skills"

# skill_id -> body after frontmatter (starts with # title)
SKILL_BODIES: dict[str, str] = {}

def _w(sid: str, body: str) -> None:
    SKILL_BODIES[sid] = body.strip()


_w("analizar_derechos_victima", """
# analizar_derechos_victima

## Scope
- Category: `Skills de representacion de victimas`
- Skill ID: `analizar_derechos_victima`
- Tier: `operativo`

## Used By Agents
- `analista_representacion_victimas`
- `evaluador_derechos_fundamentales_tutela`

## Purpose
Mapear derechos de la víctima en el proceso penal (participación, información, reparación, protección) y su vínculo con los hechos.

## Rol en analista_representacion_victimas
Insumo para teoría del caso y plan de actuación ordinaria Ley 906.

## Rol en evaluador_derechos_fundamentales_tutela
Distinguir derechos procesales de víctima vs. derechos fundamentales para tutela; no dictamina procedencia.

## Inputs
- Hechos verificados y etapa procesal Ley 906.
- Conductas u omisiones de Fiscalía, juez o autoridad que afecten a la víctima.
- Normativa de víctimas (Ley 906, Ley 1712, etc.) vía RAG.

## Outputs
- `derechos_mapeados`: participación | información | reparación | protección | otros.
- Por derecho: `hecho_vinculado`, `autoridad_responsable`, `estado` (vulnerado | en_riesgo | respetado | pendiente).
- `prioridad_atencion` (alta | media | baja).
- Etiqueta: `MAPEO DERECHOS VÍCTIMA — NO SUSTITUYE TUTELA`.

## Steps
1. Mapear derechos de participación, información, reparación y protección aplicables.
2. Relacionar derechos con hechos y etapa del proceso.
3. Priorizar derechos más vulnerados o urgentes.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_normas_victimas_search`
- `rag_constitucional_search`

## Guardrails (g1–g8)
- **g1:** No inventar vulneraciones ni normas.
- **g3:** Derecho procesal de víctima ≠ automáticamente tutela.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No intereses subjetivos (`identificar_intereses_victima`).
- No derechos fundamentales para tutela (`identificar_derecho_fundamental_afectado`).

## Riesgo si se omite
Estrategia que ignora derechos procesales de la víctima ya vulnerados en el expediente.
""")

_w("analizar_enfoque_diferencial", """
# analizar_enfoque_diferencial

## Scope
- Category: `Skills de representacion de victimas`
- Skill ID: `analizar_enfoque_diferencial`
- Tier: `operativo`

## Used By Agents
- `analista_representacion_victimas`
- `analista_calidad_juridica`

## Purpose
Identificar factores diferenciales relevantes (género, edad, discapacidad, etnia, etc.) que exijan enfoque especial en la representación.

## Rol en analista_representacion_victimas
Ajustar teoría del caso y comunicación con enfoque de derechos.

## Rol en analista_calidad_juridica
Verificar que escritos y preguntas respeten enfoque diferencial.

## Inputs
- Datos de la víctima disponibles (solo los documentados; no inferir).
- Tipo de delito y contexto del caso.
- Materiales a revisar (teoría, preguntas, memorial).

## Outputs
- `factores_diferenciales` documentados con fuente o `[PENDIENTE DE VERIFICAR]`.
- `ajustes_recomendados` en lenguaje, ritmo procesal o medidas de protección.
- `alertas` si el material ignora enfoque diferencial obligatorio.

## Steps
1. Identificar factores diferenciales relevantes con base documentada.
2. Evaluar impacto en representación, comunicación y medidas de protección.
3. Proponer ajustes concretos al plan de actuación.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_normas_victimas_search`

## Guardrails (g1–g8)
- **g1:** No inferir identidad o condición no documentada.
- **g5:** No estigmatizar a la víctima al nombrar factores diferenciales.
- **g6:** Minimizar datos sensibles innecesarios.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No revisión detallada de revictimización (`controlar_no_revictimizacion`).

## Riesgo si se omite
Revictimización o desatención de garantías especiales aplicables a la víctima.
""")

_w("controlar_audiencias", """
# controlar_audiencias

## Scope
- Category: `Skills de audiencias`
- Skill ID: `controlar_audiencias`
- Tier: `operativo`

## Used By Agents
- `preparador_estrategico_audiencias_penales`
- `analista_calidad_juridica`

## Purpose
Controlar que la preparación de audiencia cumpla requisitos formales y sustantivos Ley 906 antes de la intervención.

## Rol en preparador_estrategico_audiencias_penales
Checklist de control previo a audiencia.

## Rol en analista_calidad_juridica
Segunda revisión si el paquete de audiencia va a uso externo.

## Inputs
- Tipo de audiencia, fecha y etapa procesal.
- Objetivo, guion, preguntas y solicitudes orales preparadas.
- Plazos y requisitos de intervención de la víctima.

## Outputs
- `checklist`: ítem | cumple | no_cumple | pendiente.
- `bloqueantes` que impiden intervenir sin corrección.
- Etiqueta: `CONTROL AUDIENCIA — REVISAR CON ABOGADO`.

## Steps
1. Verificar tipo de audiencia y competencia del despacho/juez.
2. Contrastar preparación con requisitos Ley 906 de intervención de la víctima.
3. Señalar omisiones formales o sustantivas antes de la audiencia.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_ley906_search`
- `calendar_event_reader`

## Guardrails (g1–g8)
- **g4:** HITL obligatorio antes de audiencia.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No redactar preguntas (`preparar_preguntas_audiencia`).
- No checklist operativo (`crear_checklist_previo_audiencia` — lista táctica).

## Riesgo si se omite
Intervención extemporánea, improcedente o sin cumplir requisitos de la audiencia.
""")

_w("controlar_separacion_hecho_inferencia", """
# controlar_separacion_hecho_inferencia

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `controlar_separacion_hecho_inferencia`
- Tier: `operativo`

## Used By Agents
- `redactor_documentos_juridicos_penales`
- `analista_calidad_juridica`

## Purpose
Verificar que hechos confirmados, narrados, inferidos y pendientes estén claramente separados en la salida.

## Rol en redactor_documentos_juridicos_penales
Autocontrol antes de entregar borrador.

## Rol en analista_calidad_juridica
Control de calidad en documentos para uso externo.

## Inputs
- Texto del memorial, tutela, petición o análisis.
- Matriz hecho-fuente o cronología (si existe).

## Outputs
- `fragmentos`: texto | clasificación (confirmado | narrado | inferido | pendiente) | observación.
- `correcciones_sugeridas` para separar hecho de argumentación.
- Etiqueta: `CONTROL HECHO-INFERENCIA`.

## Steps
1. Identificar afirmaciones fácticas en el texto.
2. Clasificar cada una según soporte documental.
3. Señalar mezclas de hecho con inferencia o calificación penal.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_expediente_search`

## Guardrails (g1–g8)
- **g3:** No reclasificar hecho confirmado sin fuente.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No verificar soporte global (`verificar_hechos_soportados`).
- No redactar hechos (`extraer_hechos_relevantes`).

## Riesgo si se omite
Memorial que presenta inferencias o sospechas como hechos probados ante el juez.
""")

_w("controlar_tono_juridico_documento", """
# controlar_tono_juridico_documento

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `controlar_tono_juridico_documento`
- Tier: `operativo`

## Used By Agents
- `redactor_documentos_juridicos_penales`
- `analista_calidad_juridica`

## Purpose
Revisar que el tono del escrito sea profesional, respetuoso y adecuado al destinatario judicial o administrativo.

## Rol en redactor_documentos_juridicos_penales
Revisión de tono antes de pasar a calidad.

## Rol en analista_calidad_juridica
Control final de estilo en salidas externas.

## Inputs
- Borrador de memorial, petición, tutela o solicitud.
- Destinatario (juez, Fiscalía, autoridad administrativa).

## Outputs
- `hallazgos_tono`: agresivo | coloquial | emocional_excesivo | procesal_inadecuado | ok.
- `reformulaciones` sugeridas por fragmento.
- Etiqueta: `CONTROL TONO JURÍDICO`.

## Steps
1. Revisar registro formal y respeto institucional del escrito.
2. Detectar lenguaje emocional, acusatorio o coloquial impropio.
3. Proponer reformulaciones manteniendo el contenido jurídico.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- Sin herramientas obligatorias

## Guardrails (g1–g8)
- **g5:** Tono respetuoso con la víctima y las autoridades.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No riesgo reputacional público (`controlar_tono_riesgo_reputacional`).
- No revictimización (`controlar_no_revictimizacion`).

## Riesgo si se omite
Escrito que pierde credibilidad ante el despacho o irrita innecesariamente a la contraparte.
""")

_w("controlar_tono_riesgo_reputacional", """
# controlar_tono_riesgo_reputacional

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `controlar_tono_riesgo_reputacional`
- Tier: `operativo`

## Used By Agents
- `redactor_documentos_juridicos_penales`
- `analista_calidad_juridica`

## Purpose
Detectar contenido que exponga al despacho o a la víctima a riesgo reputacional o mediático innecesario.

## Rol en redactor_documentos_juridicos_penales
Filtro antes de radicar o comunicar.

## Rol en analista_calidad_juridica
Control en comunicaciones sensibles.

## Inputs
- Texto destinado a terceros (cliente, prensa, redes, contraparte no procesal).
- Contexto del caso y perfil público de las partes.

## Outputs
- `riesgos_reputacionales`: exposición_mediática | dato_sensible | acusación_pública | ok.
- `mitigaciones` recomendadas.
- Etiqueta: `SOLO_ABOGADO` si hay riesgo alto.

## Steps
1. Identificar afirmaciones que puedan generar exposición pública indebida.
2. Evaluar si el riesgo es necesario para la estrategia procesal.
3. Proponer redacción más reservada cuando sea posible.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- Sin herramientas obligatorias

## Guardrails (g1–g8)
- **g6:** No amplificar datos sensibles en comunicaciones.
- **g4:** HITL obligatorio antes de comunicación externa.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No tono judicial (`controlar_tono_juridico_documento`).
- No resumen al cliente (`preparar_resumen_operativo_cliente`).

## Riesgo si se omite
Daño reputacional al despacho o a la víctima por comunicación imprudente.
""")

_w("crear_checklist_previo_audiencia", """
# crear_checklist_previo_audiencia

## Scope
- Category: `Skills de audiencias`
- Skill ID: `crear_checklist_previo_audiencia`
- Tier: `operativo`

## Used By Agents
- `preparador_estrategico_audiencias_penales`
- `analista_calidad_juridica`

## Purpose
Generar lista verificable de tareas y documentos antes de una audiencia penal.

## Rol en preparador_estrategico_audiencias_penales
Checklist operativo tras definir objetivo de audiencia.

## Rol en analista_calidad_juridica
Verificar completitud del paquete de audiencia.

## Inputs
- Tipo de audiencia y fecha.
- Objetivo de audiencia (`identificar_objetivo_audiencia`).
- Materiales preparados (guion, preguntas, pruebas).

## Outputs
- Checklist: `ítem`, `responsable`, `estado` (listo | pendiente | no_aplica).
- `documentos_requeridos` y plazos internos.
- Etiqueta: `CHECKLIST PRE-AUDIENCIA`.

## Steps
1. Listar requisitos formales y materiales según tipo de audiencia.
2. Cruzar con objetivo táctico y prueba disponible.
3. Asignar responsable y estado por ítem.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `hearing_template_loader`
- `calendar_event_reader`

## Guardrails (g1–g8)
- **g4:** HITL antes de audiencia.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No definir objetivo (`identificar_objetivo_audiencia`).
- No control formal Ley 906 (`controlar_audiencias`).

## Riesgo si se omite
Olvido de prueba, memorial o requisito clave el día de la audiencia.
""")

_w("detectar_brechas_probatorias", """
# detectar_brechas_probatorias

## Scope
- Category: `Skills de evidencia y soporte probatorio`
- Skill ID: `detectar_brechas_probatorias`
- Tier: `operativo`

## Used By Agents
- `gestor_evidencia_y_soporte_probatorio`
- `analista_representacion_victimas`

## Purpose
Identificar hechos relevantes sin prueba suficiente en el expediente.

## Rol en gestor_evidencia_y_soporte_probatorio
Antecede plan de recaudo.

## Rol en analista_representacion_victimas
Informa debilidades para teoría del caso.

## Inputs
- Matriz hecho-prueba (`construir_matriz_hecho_prueba`).
- Inventario de evidencia (`inventariar_evidencia`).

## Outputs
- `brechas`: hecho | prueba_ausente_o_débil | impacto (alto | medio | bajo).
- `prioridad_recaudo` ordenada.
- Etiqueta: `BRECHAS PROBATORIAS PRELIMINARES`.

## Steps
1. Contrastar hechos relevantes con prueba disponible en expediente.
2. Clasificar brechas por impacto procesal.
3. Priorizar recaudo urgente según etapa y audiencias próximas.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_expediente_search`

## Guardrails (g1–g8)
- **g1:** No asumir prueba existente sin constar en inventario.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No plan de recaudo (`crear_plan_recaudo_probatorio`).
- No suficiencia global (`evaluar_suficiencia_probatoria`).

## Riesgo si se omite
Estrategia o memorial que depende de prueba que no existe ni está en camino.
""")

_w("detectar_riesgo_revictimizacion", """
# detectar_riesgo_revictimizacion

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `detectar_riesgo_revictimizacion`
- Tier: `operativo`

## Used By Agents
- `analista_representacion_victimas`
- `analista_calidad_juridica`

## Purpose
Alertar tempranamente sobre riesgo de revictimización en materiales o estrategia propuesta.

## Rol en analista_representacion_victimas
Triaje rápido en teoría del caso y comunicación con víctima.

## Rol en analista_calidad_juridica
Alerta antes de revisión profunda (`controlar_no_revictimizacion`).

## Inputs
- Texto o estrategia a evaluar (preguntas, teoría, resumen).
- Tipo de delito y contexto (si consta).

## Outputs
- `nivel_riesgo`: alto | medio | bajo | no_detectado.
- `indicadores` detectados (breve lista).
- `derivar_a`: `controlar_no_revictimizacion` si riesgo medio/alto.

## Steps
1. Escanear lenguaje, preguntas y exposición de datos sensibles.
2. Clasificar nivel de riesgo de revictimización.
3. Recomendar revisión profunda o reformulación inmediata.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `revictimization_risk_checker`

## Guardrails (g1–g8)
- **g5:** Priorizar dignidad y derechos de la víctima.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No revisión exhaustiva (`controlar_no_revictimizacion`).
- No enfoque diferencial (`analizar_enfoque_diferencial`).

## Riesgo si se omite
Material dañino llega a la víctima o a audiencia sin filtro previo.
""")

_w("detectar_riesgos_audiencia", """
# detectar_riesgos_audiencia

## Scope
- Category: `Skills de audiencias`
- Skill ID: `detectar_riesgos_audiencia`
- Tier: `operativo`

## Used By Agents
- `preparador_estrategico_audiencias_penales`
- `analista_calidad_juridica`

## Purpose
Identificar riesgos tácticos y procesales específicos de una audiencia programada.

## Rol en preparador_estrategico_audiencias_penales
Antecede simulación y guion oral.

## Rol en analista_calidad_juridica
Segunda opinión en audiencias de alto riesgo.

## Inputs
- Tipo de audiencia, postura de Fiscalía/defensa (hipótesis).
- Debilidades probatorias y objetivo de audiencia.
- Antecedentes de audiencias previas en el caso.

## Outputs
- `riesgos`: descripción | probabilidad | impacto | mitigación sugerida.
- `riesgo_global`: alto | medio | bajo.
- Etiqueta: `RIESGOS AUDIENCIA PRELIMINARES`.

## Steps
1. Listar riesgos procesales y tácticos de la audiencia concreta.
2. Evaluar probabilidad e impacto en objetivos de la víctima.
3. Proponer mitigaciones (aplazamiento, solicitud oral, prueba).
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_expediente_search`
- `rag_ley906_search`

## Guardrails (g1–g8)
- **g3:** Riesgos son hipótesis, no predicciones certas.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No simular escenarios (`simular_escenarios_audiencia`).
- No contraargumentos detallados (`preparar_contraargumentos`).

## Riesgo si se omite
Audiencia sin preparación para imprevistos que perjudican a la víctima.
""")

_w("evaluar_dano_y_afectacion", """
# evaluar_dano_y_afectacion

## Scope
- Category: `Skills de representacion de victimas`
- Skill ID: `evaluar_dano_y_afectacion`
- Tier: `operativo`

## Used By Agents
- `analista_representacion_victimas`
- `evaluador_derechos_fundamentales_tutela`

## Purpose
Describir preliminarmente el daño o afectación a la víctima con base documentada (físico, psicológico, patrimonial, social).

## Rol en analista_representacion_victimas
Insumo para teoría del caso y pretensiones de reparación.

## Rol en evaluador_derechos_fundamentales_tutela
Contexto factual para perjuicio; no sustituye `analizar_perjuicio_irremediable`.

## Inputs
- Relatos, informes médicos/psicológicos, declaraciones (si constan).
- Hechos verificados del caso.
- Pretensiones de reparación ya planteadas.

## Outputs
- `tipos_daño`: físico | psicológico | patrimonial | social | otros.
- Por tipo: `descripción`, `fuente`, `gravedad_preliminar` (alta | media | baja | pendiente).
- Etiqueta: `AFECTACIÓN PRELIMINAR — NO ES PERITAJE`.

## Steps
1. Identificar tipos de daño o afectación alegados o documentados.
2. Vincular cada afectación con hechos y fuentes del expediente.
3. Señalar vacíos que requieran prueba pericial o documental.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_expediente_search`

## Guardrails (g1–g8)
- **g1:** No inventar diagnósticos ni secuelas.
- **g5:** No minimizar ni dramatizar el daño sin base.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No perjuicio irremediable constitucional (`analizar_perjuicio_irremediable`).
- No intereses subjetivos (`identificar_intereses_victima`).

## Riesgo si se omite
Pretensiones de reparación desconectadas del daño real o documentado.
""")

_w("generar_preguntas_testigos_peritos", """
# generar_preguntas_testigos_peritos

## Scope
- Category: `Skills de audiencias`
- Skill ID: `generar_preguntas_testigos_peritos`
- Tier: `operativo`

## Used By Agents
- `preparador_estrategico_audiencias_penales`
- `analista_cronologia_hechos_penales`

## Purpose
Formular preguntas para testigos o peritos (no para la víctima) alineadas a hechos pendientes de aclarar.

## Rol en preparador_estrategico_audiencias_penales
Uso principal en preparación de audiencia.

## Rol en analista_cronologia_hechos_penales
Solo para aclarar huecos factuales vía terceros; no preguntas a víctima.

## Inputs
- Matriz hecho-prueba y vacíos factuales.
- Tipo de testigo/perito y objeto de su declaración.
- Objetivo probatorio por bloque.

## Outputs
- Preguntas: `destinatario` (testigo | perito), `pregunta`, `hecho_que_aclara`, `riesgo` (bajo | medio).
- Etiqueta: `PREGUNTAS TERCEROS — NO VÍCTIMA`.

## Steps
1. Identificar hechos que requieren aclaración por testigo o perito.
2. Formular preguntas neutrales y no inductivas.
3. Ordenar por relevancia probatoria.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_expediente_search`

## Guardrails (g1–g8)
- **g4:** HITL antes de audiencia.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No preguntas a víctima (`preparar_preguntas_audiencia`).
- No preguntas de tipicidad (`generar_preguntas_tipicidad`).

## Riesgo si se omite
Pérdida de oportunidad para cerrar huecos factuales con testigos clave.
""")

_w("preparar_resumen_operativo_cliente", """
# preparar_resumen_operativo_cliente

## Scope
- Category: `Skills de seguimiento procesal`
- Skill ID: `preparar_resumen_operativo_cliente`
- Tier: `operativo`

## Used By Agents
- `gestor_seguimiento_procesal_penal`
- `analista_calidad_juridica`

## Purpose
Redactar resumen simple del estado del proceso para la víctima o cliente, sin estrategia sensible.

## Rol en gestor_seguimiento_procesal_penal
Comunicación periódica de avance procesal.

## Rol en analista_calidad_juridica
Aprobar tono y confidencialidad antes de envío.

## Inputs
- Estado del radicado y últimas actuaciones.
- Próximos pasos procesales públicos (no estrategia interna).
- Aprobación previa del abogado (si aplica).

## Outputs
- Resumen en lenguaje accesible: qué pasó, qué sigue, qué necesita el cliente.
- `excluido_estrategia_sensible`: confirmación explícita.
- Etiqueta: `SOLO_TRAS_APROBACION_ABOGADO — NO ENVIAR DIRECTO`.

## Steps
1. Sintetizar estado del proceso en lenguaje accesible.
2. Incluir próximos pasos sin revelar estrategia sensible.
3. Marcar para revisión humana antes de envío al cliente.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `case_state_reader`
- `approval_gate_submit`

## Guardrails (g1–g8)
- **g4:** HITL obligatorio; nunca envío automático al cliente.
- **g6:** No incluir datos de terceros ni detalles gráficos innecesarios.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No resumen ejecutivo litigante (`crear_resumen_ejecutivo_litigante` — abogado).
- No reporte técnico (`crear_reporte_estado_caso`).

## Riesgo si se omite
Cliente desinformado o, peor, informado con datos estratégicos que no debía conocer.
""")

_w("redactar_derecho_peticion_penal", """
# redactar_derecho_peticion_penal

## Scope
- Category: `Skills de redaccion juridica penal`
- Skill ID: `redactar_derecho_peticion_penal`
- Tier: `operativo`

## Used By Agents
- `redactor_documentos_juridicos_penales` (único ejecutor de redacción)

## Purpose
Redactar borrador de derecho de petición relacionado con el caso penal cuando `evaluar_derecho_peticion` indica procedencia.

## Rol en redactor_documentos_juridicos_penales
Ejecutar redacción solo con evaluación favorable preliminar de petición.

## Inputs
- Salida de `evaluar_derecho_peticion` (procedencia preliminar).
- Destinatario, objeto, hechos y anexos disponibles.
- Plantilla y norma aplicable (RAG).

## Outputs
- Borrador: hechos, fundamentos, peticiones, anexos referenciados.
- `plazo_respuesta_esperado`.
- Etiqueta: `BORRADOR — NO RADICAR SIN FIRMA`.

## Steps
1. Precisar destinatario, objeto y hechos que motivan la petición.
2. Redactar peticiones claras con fundamento constitucional/legal.
3. Incluir anexos y plazo de respuesta esperado.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_constitucional_search`
- `rag_plantillas_search`

## Guardrails (g1–g8)
- **g4:** HITL y firma humana antes de radicar.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No evaluar procedencia de petición (`evaluar_derecho_peticion` — evaluador).

## Riesgo si se omite
Petición mal dirigida, extemporánea o sin fundamento que retrasa la vía útil.
""")

_w("verificar_citas_normativas", """
# verificar_citas_normativas

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `verificar_citas_normativas`
- Tier: `operativo`

## Used By Agents
- `redactor_documentos_juridicos_penales`
- `analista_calidad_juridica`

## Purpose
Verificar que leyes, artículos y decretos citados existan, estén vigentes y sean pertinentes al caso.

## Rol en redactor_documentos_juridicos_penales
Control en borrador antes de calidad.

## Rol en analista_calidad_juridica
Verificación en salida final.

## Inputs
- Lista de citas normativas en el documento.
- Contexto del caso (penal-víctimas Colombia).

## Outputs
- Por cita: `referencia`, `existe_en_rag` (sí | no | pendiente), `vigente` (sí | no | pendiente), `pertinencia` (alta | media | baja).
- `citas_a_corregir` priorizadas.
- Etiqueta: `VERIFICACIÓN NORMATIVA — NO ES APROBACIÓN FINAL`.

## Steps
1. Validar existencia de leyes, artículos y decretos citados.
2. Verificar vigencia y pertinencia al caso penal-víctimas.
3. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `citation_checker`
- `rag_normativo_search`

## Guardrails (g1–g8)
- **g1:** No afirmar vigencia sin verificar en RAG.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No detectar alucinaciones globales (`detectar_alucinaciones_legales`).
- No jurisprudencia (`verificar_jurisprudencia`).

## Riesgo si se omite
Memorial con artículos derogados, inexistentes o irrelevantes citados como fundamento.
""")

# Fase 3 operativos
_w("clasificar_tipo_prueba", """
# clasificar_tipo_prueba

## Scope
- Category: `Skills de evidencia y soporte probatorio`
- Skill ID: `clasificar_tipo_prueba`
- Tier: `operativo`

## Used By Agents
- `gestor_evidencia_y_soporte_probatorio`

## Purpose
Clasificar cada elemento probatorio según tipo procesal (documental, testimonial, pericial, etc.).

## Inputs
- Inventario de evidencia (`inventariar_evidencia`).
- Descripción y origen de cada elemento.

## Outputs
- Por ítem: `id`, `tipo_prueba`, `fuerza_preliminar`, `observaciones`.
- Etiqueta: `CLASIFICACIÓN PROBATORIA PRELIMINAR`.

## Steps
1. Revisar cada elemento del inventario probatorio.
2. Asignar tipo de prueba según naturaleza y origen.
3. Señalar elementos no clasificables como pendientes.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_expediente_search`

## Guardrails (g1–g8)
- **g1:** No inventar tipo ni origen.
- **g8:** Aviso de revisión profesional.

## Riesgo si se omite
Matriz hecho-prueba y estrategia con prueba mal categorizada o inadmisible.
""")

_w("controlar_confidencialidad_datos_sensibles", """
# controlar_confidencialidad_datos_sensibles

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `controlar_confidencialidad_datos_sensibles`
- Tier: `operativo`

## Used By Agents
- `analista_calidad_juridica`

## Purpose
Detectar y mitigar exposición innecesaria de datos personales sensibles en salidas del sistema.

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

## Guardrails (g1–g8)
- **g6:** Minimización de datos por defecto.
- **g4:** HITL antes de compartir externamente.
- **g8:** Aviso de revisión profesional.

## Riesgo si se omite
Filtración de datos de la víctima o terceros con violación de Ley 1581.
""")

_w("crear_reporte_estado_caso", """
# crear_reporte_estado_caso

## Scope
- Category: `Skills de seguimiento procesal`
- Skill ID: `crear_reporte_estado_caso`
- Tier: `operativo`

## Used By Agents
- `gestor_seguimiento_procesal_penal`

## Purpose
Generar reporte interno del estado del caso para el despacho (no para cliente).

## Inputs
- Radicado, actuaciones recientes, tareas pendientes.
- Alertas de términos y seguimiento documental.

## Outputs
- Reporte: etapa, últimas actuaciones, pendientes, riesgos procesales, próximos pasos.
- Etiqueta: `REPORTE INTERNO DESPACHO`.

## Steps
1. Consolidar estado procesal y actuaciones recientes.
2. Listar pendientes, responsables y plazos.
3. Incluir alertas de términos relevantes.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `case_state_reader`
- `audit_log_write`

## Guardrails (g1–g8)
- **g6:** Reporte interno; no incluir datos innecesarios.
- **g8:** Aviso de revisión profesional.

## Riesgo si se omite
Despacho opera sin panorama actualizado del caso y pierde plazos.
""")

_w("crear_resumen_ejecutivo_litigante", """
# crear_resumen_ejecutivo_litigante

## Scope
- Category: `Skills de representacion de victimas`
- Skill ID: `crear_resumen_ejecutivo_litigante`
- Tier: `operativo`

## Used By Agents
- `preparador_estrategico_audiencias_penales`
- `analista_representacion_victimas`

## Purpose
Síntesis ejecutiva del caso para el abogado litigante (estrategia y estado, no para cliente).

## Inputs
- Teoría del caso, etapa procesal, prueba clave.
- Objetivos de representación y próximas audiencias.

## Outputs
- Resumen: situación | fortalezas | debilidades | próximos pasos | decisiones pendientes.
- Etiqueta: `RESUMEN ABOGADO — CONFIDENCIAL`.

## Steps
1. Sintetizar estado factual y procesal del caso.
2. Destacar fortalezas, debilidades y decisiones pendientes.
3. Proponer próximos pasos prioritarios para el litigante.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `case_state_reader`
- `rag_expediente_search`

## Guardrails (g1–g8)
- **g6:** Confidencial; no formato cliente.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No resumen cliente (`preparar_resumen_operativo_cliente`).

## Riesgo si se omite
Abogado litigante sin panorama rápido antes de audiencia o reunión estratégica.
""")

_w("estructurar_hechos_fundamentos_solicitudes", """
# estructurar_hechos_fundamentos_solicitudes

## Scope
- Category: `Skills de redaccion juridica penal`
- Skill ID: `estructurar_hechos_fundamentos_solicitudes`
- Tier: `operativo`

## Used By Agents
- `redactor_documentos_juridicos_penales`

## Purpose
Organizar esquema hechos-fundamentos-peticiones antes de redactar memorial o escrito.

## Inputs
- Hechos soportados y pretensiones.
- Norma y plantilla aplicable.
- Tipo de escrito (memorial, solicitud, recurso).

## Outputs
- Esquema numerado: bloque hechos | fundamentos | peticiones con referencias cruzadas.
- Pendientes `[PENDIENTE DE VERIFICAR]` por bloque.
- Etiqueta: `ESQUEMA — NO ES BORRADOR FINAL`.

## Steps
1. Agrupar hechos verificados por tema o cronología.
2. Vincular fundamentos normativos a cada bloque fáctico.
3. Formular peticiones derivadas de cada fundamento.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_plantillas_search`
- `rag_normativo_search`

## Guardrails (g1–g8)
- **g3:** Esquema separa hecho de argumento.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No redactar memorial completo (`redactar_memorial_penal`).

## Riesgo si se omite
Borrador desordenado con peticiones desconectadas de los hechos probados.
""")

_w("identificar_derecho_fundamental_afectado", """
# identificar_derecho_fundamental_afectado

## Scope
- Category: `Skills constitucionales y tutela`
- Skill ID: `identificar_derecho_fundamental_afectado`
- Tier: `operativo`

## Used By Agents
- `evaluador_derechos_fundamentales_tutela`

## Purpose
Identificar qué derechos fundamentales podrían estar comprometidos según los hechos del caso.

## Inputs
- Hechos verificados y narrados del caso.
- Conductas u omisiones de autoridades.
- Catálogo constitucional (RAG).

## Outputs
- `derechos_identificados`: derecho | titular | posible_vulnerador | relevancia (alta | media | baja).
- Vacíos para matriz hecho-derecho.
- Etiqueta: `IDENTIFICACIÓN PRELIMINAR — NO DICTAMEN PROCEDENCIA`.

## Steps
1. Mapear hechos del caso contra catálogo de derechos fundamentales aplicables.
2. Precisar titular del derecho y autoridad o sujeto vulnerador.
3. Priorizar derechos más directamente comprometidos para análisis posterior.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_constitucion_search`
- `rag_expediente_search`

## Guardrails (g1–g8)
- **g1:** No inventar vulneraciones.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No matriz hecho-derecho (`crear_matriz_hecho_derecho_fundamental`).
- No procedencia (`evaluar_procedencia_tutela`).

## Riesgo si se omite
Tutela mal encaminada invocando derechos no comprometidos en los hechos.
""")

_w("identificar_intereses_victima", """
# identificar_intereses_victima

## Scope
- Category: `Skills de representacion de victimas`
- Skill ID: `identificar_intereses_victima`
- Tier: `operativo`

## Used By Agents
- `analista_representacion_victimas`

## Purpose
Identificar intereses y expectativas de la víctima en el proceso (reparación, verdad, seguridad, celeridad, etc.).

## Inputs
- Relato o declaración de la víctima (si consta).
- Notas del abogado sobre objetivos del cliente.
- Etapa procesal y opciones disponibles.

## Outputs
- `intereses`: lista priorizada con fuente (declarada | inferida_documentada | pendiente).
- `tensiones` entre intereses si las hay.
- Etiqueta: `INTERVIEW HITL — NO SUSTITUYE DECISIÓN ABOGADO`.

## Steps
1. Recopilar intereses expresados por la víctima o documentados.
2. Clasificar y priorizar sin imponer objetivos ajenos.
3. Señalar intereses que requieren confirmación con la víctima.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_expediente_search`

## Guardrails (g1–g8)
- **g2:** Sin input de la víctima, marcar pendiente; no inventar intereses.
- **g5:** No presionar objetivos que revictimicen.
- **g4:** HITL obligatorio.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No derechos procesales (`analizar_derechos_victima`).
- No teoría del caso (`construir_teoria_caso_victima`).

## Riesgo si se omite
Representación que persigue metas procesales ajenas a lo que la víctima necesita.
""")

_w("preparar_contraargumentos", """
# preparar_contraargumentos

## Scope
- Category: `Skills de audiencias`
- Skill ID: `preparar_contraargumentos`
- Tier: `operativo`

## Used By Agents
- `preparador_estrategico_audiencias_penales`

## Purpose
Anticipar argumentos de defensa o Fiscalía y preparar réplicas para audiencia o memorial.

## Inputs
- Teoría del caso contraria (hipótesis documentada).
- Prueba disponible y matriz hecho-prueba.
- Tipo de audiencia u escrito objetivo.

## Outputs
- `contraargumentos`: argumento_ajeno | réplica_sugerida | prueba_de_apoyo | riesgo.
- Etiqueta: `HIPÓTESIS TÁCTICA — NO AFIRMAR HECHOS NO PROBADOS`.

## Steps
1. Identificar líneas argumentativas probables de la contraparte.
2. Preparar réplicas con hechos soportados y norma aplicable.
3. Señalar puntos débiles de la réplica que requieren prueba adicional.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_expediente_search`
- `rag_ley906_search`

## Guardrails (g1–g8)
- **g3:** Réplicas basadas en hechos soportados, no en especulación.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No guion oral (`preparar_guion_intervencion_oral`).
- No simulación (`simular_escenarios_audiencia`).

## Riesgo si se omite
Improvisación ante argumentos previsibles de defensa o Fiscalía.
""")

_w("redactar_ampliacion_denuncia", """
# redactar_ampliacion_denuncia

## Scope
- Category: `Skills de redaccion juridica penal`
- Skill ID: `redactar_ampliacion_denuncia`
- Tier: `operativo`

## Used By Agents
- `redactor_documentos_juridicos_penales`

## Purpose
Redactar borrador de ampliación de denuncia con nuevos hechos o elementos.

## Inputs
- Denuncia o informe previo (si consta).
- Nuevos hechos verificados o narrados con fuente.
- Radicado o número de noticia criminal (si existe).

## Outputs
- Borrador de ampliación: hechos nuevos, relación con denuncia previa, peticiones.
- Etiqueta: `BORRADOR — NO RADICAR SIN FIRMA`.

## Steps
1. Identificar hechos nuevos no incluidos en denuncia anterior.
2. Redactar ampliación vinculando con radicado o noticia existente.
3. Marcar hechos sin fuente como pendientes.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_expediente_search`
- `rag_plantillas_search`

## Guardrails (g1–g8)
- **g1:** No inventar radicados ni hechos.
- **g4:** HITL y firma humana.
- **g8:** Aviso de revisión profesional.

## Riesgo si se omite
Hechos nuevos no incorporados formalmente al expediente penal.
""")

_w("redactar_solicitud_impulso_procesal", """
# redactar_solicitud_impulso_procesal

## Scope
- Category: `Skills de redaccion juridica penal`
- Skill ID: `redactar_solicitud_impulso_procesal`
- Tier: `operativo`

## Used By Agents
- `redactor_documentos_juridicos_penales`
- `gestor_seguimiento_procesal_penal`

## Purpose
Redactar solicitud de impulso procesal ante inactividad de Fiscalía o juez.

## Rol en redactor_documentos_juridicos_penales
Redacta borrador formal.

## Rol en gestor_seguimiento_procesal_penal
Aporta hechos de inactividad (`detectar_inactividad_procesal`); no redacta texto final.

## Inputs
- Registro de inactividad y última actuación.
- Etapa procesal y actuación solicitada.
- Norma Ley 906 que fundamente el impulso.

## Outputs
- Borrador: hechos de parálisis, fundamentos, petición concreta de actuación.
- Etiqueta: `BORRADOR — NO RADICAR SIN FIRMA`.

## Steps
1. Documentar inactividad procesal con fechas y actuaciones omitidas.
2. Fundamentar solicitud en Ley 906 y derechos de la víctima.
3. Formular petición concreta de actuación al Fiscal o juez.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_ley906_search`
- `rag_plantillas_search`
- `case_state_reader`

## Guardrails (g1–g8)
- **g1:** No inventar actuaciones ni fechas.
- **g4:** HITL antes de radicar.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No detectar inactividad (`detectar_inactividad_procesal` — seguimiento).

## Riesgo si se omite
Proceso paralizado sin presión formal y pérdida de oportunidades probatorias.
""")

_w("registrar_actuacion_procesal", """
# registrar_actuacion_procesal

## Scope
- Category: `Skills de seguimiento procesal`
- Skill ID: `registrar_actuacion_procesal`
- Tier: `atomico`

## Used By Agents
- `gestor_seguimiento_procesal_penal`

## Purpose
Registrar en el sistema una actuación procesal nueva con fuente y fecha.

## Inputs
- Descripción de la actuación, fecha, documento fuente.
- Radicado del caso.

## Outputs
- Registro: `actuacion`, `fecha`, `fuente`, `timestamp_registro`.
- Confirmación de actualización de estado del caso.

## Steps
1. Registrar actuación con descripción, fecha y fuente documental.
2. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `case_state_writer`
- `audit_log_write`

## Guardrails (g1–g8)
- **g1:** No inventar actuaciones.
- **g8:** Aviso de revisión profesional.

## Riesgo si se omite
Expediente interno desactualizado y errores en alertas de términos.
""")

_w("seguimiento_documentos_radicados", """
# seguimiento_documentos_radicados

## Scope
- Category: `Skills de seguimiento procesal`
- Skill ID: `seguimiento_documentos_radicados`
- Tier: `operativo`

## Used By Agents
- `gestor_seguimiento_procesal_penal`

## Purpose
Hacer seguimiento a documentos enviados o radicados y su estado de respuesta.

## Inputs
- Lista de documentos radicados (fecha, destinatario, radicado interno).
- Plazos de respuesta esperados.

## Outputs
- Por documento: `estado` (pendiente | respondido | vencido | desconocido), `días_transcurridos`, `acción_sugerida`.
- Alertas de vencimiento.

## Steps
1. Cruzar documentos radicados con plazos y respuestas recibidas.
2. Marcar vencidos y próximos a vencer.
3. Sugerir acción de seguimiento (llamado, memorial, petición).
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `case_state_reader`
- `calendar_terms_calculator`

## Guardrails (g1–g8)
- **g1:** No inventar respuestas de autoridad.
- **g8:** Aviso de revisión profesional.

## Riesgo si se omite
Silencios administrativos no detectados y pérdida de términos útiles.
""")

_w("verificar_jurisprudencia", """
# verificar_jurisprudencia

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `verificar_jurisprudencia`
- Tier: `operativo`

## Used By Agents
- `analista_calidad_juridica`
- `redactor_documentos_juridicos_penales`

## Purpose
Verificar que sentencias citadas existan en RAG y sean pertinentes al argumento.

## Rol en redactor_documentos_juridicos_penales
Control en borrador antes de calidad.

## Rol en analista_calidad_juridica
Verificación final.

## Inputs
- Citas jurisprudenciales en el documento.
- Tema jurídico del argumento donde se citan.

## Outputs
- Por sentencia: `referencia`, `localizada` (sí | no | pendiente), `pertinencia`, `extracto_relevante` (si aplica).
- Etiqueta: `VERIFICACIÓN JURISPRUDENCIAL`.

## Steps
1. Buscar cada sentencia citada en RAG jurisprudencial.
2. Evaluar pertinencia al argumento del caso.
3. Marcar citas no localizadas o irrelevantes.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_jurisprudencia_search`
- `citation_checker`

## Guardrails (g1–g8)
- **g1:** No inventar sentencias ni extractos.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No citas normativas (`verificar_citas_normativas`).
- No alucinaciones globales (`detectar_alucinaciones_legales`).

## Riesgo si se omite
Argumento sustentado en jurisprudencia inventada o mal aplicada.
""")


def _read_frontmatter(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return f"---{parts[1]}---\n\n"
    return ""


def main() -> None:
    for sid, body in SKILL_BODIES.items():
        path = SKILLS / sid / "SKILL.md"
        if not path.exists():
            raise SystemExit(f"Missing {path}")
        fm = _read_frontmatter(path)
        path.write_text(fm + body + "\n", encoding="utf-8")
        print(f"OK {sid}")
    print(f"Refined {len(SKILL_BODIES)} skills")


if __name__ == "__main__":
    main()
