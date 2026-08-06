"""Render legible de output_type estructurados (plan + as_tool)."""

from __future__ import annotations

from typing import Any


def render_structured_output(output: Any) -> str:
    """Convierte final_output (str | pydantic) en texto útil para abogado/gerente."""
    if output is None:
        return ""
    if isinstance(output, str):
        return output
    if not hasattr(output, "model_dump"):
        return str(output)

    data = output.model_dump()
    # BorradorDocumentoPenal
    cuerpo = data.get("cuerpo")
    if isinstance(cuerpo, str) and cuerpo.strip():
        titulo = str(data.get("titulo") or "").strip()
        pendientes = data.get("pendientes_verificacion") or []
        fuentes = data.get("fuentes_kb") or []
        header = f"{titulo}\n\n" if titulo else ""
        extras = ""
        if fuentes:
            extras += "\n\nFuentes KB:\n- " + "\n- ".join(str(f) for f in fuentes)
        if pendientes:
            extras += "\n\nPendientes de verificación:\n- " + "\n- ".join(
                str(p) for p in pendientes
            )
        return f"{header}{cuerpo}{extras}".strip()

    # DictamenCalidad
    if "veredicto" in data:
        lines = [f"Dictamen de calidad: {data.get('veredicto')}"]
        resumen = str(data.get("resumen") or "").strip()
        if resumen:
            lines.append(resumen)
        for label, key in (
            ("Hallazgos", "hallazgos"),
            ("Cambios requeridos", "cambios_requeridos"),
            ("Riesgos", "riesgos"),
            ("Fuentes KB", "fuentes_kb"),
            ("Pendientes de verificación", "pendientes_verificacion"),
        ):
            items = data.get(key) or []
            if items:
                lines.append(f"\n{label}:")
                lines.extend(f"- {x}" for x in items)
        return "\n".join(lines).strip()

    # CronologiaPenal
    if "eventos" in data and isinstance(data.get("eventos"), list):
        lines = [str(data.get("titulo") or "Cronología penal").strip(), ""]
        for i, ev in enumerate(data["eventos"], 1):
            if not isinstance(ev, dict):
                continue
            lines.append(
                f"{i}. [{ev.get('fecha_o_momento', '?')}] "
                f"({ev.get('clasificacion', 'narrado')}) {ev.get('descripcion', '')}"
            )
            fuente = str(ev.get("fuente") or "").strip()
            if fuente:
                lines.append(f"   Fuente: {fuente}")
        for label, key in (
            ("Contradicciones", "contradicciones"),
            ("Vacíos fácticos", "vacios_factuales"),
            ("Fuentes KB", "fuentes_kb"),
            ("Pendientes de verificación", "pendientes_verificacion"),
        ):
            items = data.get(key) or []
            if items:
                lines.append(f"\n{label}:")
                lines.extend(f"- {x}" for x in items)
        return "\n".join(lines).strip()

    # MatrizTipicidad
    if "hipotesis_tipica" in data:
        lines = [
            "Matriz de tipicidad preliminar",
            f"Hipótesis: {data.get('hipotesis_tipica')}",
        ]
        if data.get("tipo_penal_sugerido"):
            lines.append(f"Tipo sugerido: {data['tipo_penal_sugerido']}")
        if data.get("etiqueta_preliminar"):
            lines.append(f"Etiqueta: {data['etiqueta_preliminar']}")
        if data.get("autoria_participacion"):
            lines.append(f"Autoría/participación: {data['autoria_participacion']}")
        if data.get("dolo_culpa"):
            lines.append(f"Dolo/culpa: {data['dolo_culpa']}")
        elementos = data.get("elementos") or []
        if elementos:
            lines.append("\nElementos:")
            for el in elementos:
                if isinstance(el, dict):
                    estado = el.get("estado") or ""
                    estado_txt = f" [{estado}]" if estado else ""
                    lines.append(
                        f"- {el.get('elemento')}{estado_txt}: {el.get('riesgo_o_brecha') or '—'}"
                    )
        for label, key in (
            ("Riesgos de atipicidad", "riesgos_atipicidad"),
            ("Agravantes/atenuantes", "agravantes_atenuantes"),
            ("Fuentes KB", "fuentes_kb"),
            ("Pendientes de verificación", "pendientes_verificacion"),
        ):
            items = data.get(key) or []
            if items:
                lines.append(f"\n{label}:")
                lines.extend(f"- {x}" for x in items)
        return "\n".join(lines).strip()

    # InventarioEvidencia
    if "items" in data and ("brechas_probatorias" in data or "plan_recaudo_sugerido" in data):
        lines = [str(data.get("titulo") or "Inventario de evidencia").strip(), ""]
        for i, item in enumerate(data.get("items") or [], 1):
            if not isinstance(item, dict):
                continue
            lines.append(
                f"{i}. [{item.get('tipo', 'otro')}] {item.get('descripcion', '')} "
                f"(cadena: {item.get('cadena_custodia', 'desconocida')})"
            )
        for label, key in (
            ("Brechas probatorias", "brechas_probatorias"),
            ("Plan de recaudo sugerido", "plan_recaudo_sugerido"),
            ("Fuentes KB", "fuentes_kb"),
            ("Pendientes de verificación", "pendientes_verificacion"),
        ):
            items = data.get(key) or []
            if items:
                lines.append(f"\n{label}:")
                lines.extend(f"- {x}" for x in items)
        return "\n".join(lines).strip()


    # RutaProcesalLey906
    if "ruta_recomendada" in data and (
        "etapa_aparente" in data or "etapa_ley906" in data
    ):
        etapa = data.get("etapa_ley906") or data.get("etapa_aparente") or "pendiente_verificar"
        lines = [
            "Ruta procesal Ley 906 (preliminar)",
            str(data.get("resumen") or "").strip(),
            f"Etapa Ley 906: {etapa}",
        ]
        if data.get("evidencia_etapa"):
            lines.append(f"Evidencia de etapa: {data['evidencia_etapa']}")
        for label, key in (
            ("Oportunidades de intervención", "oportunidades_intervencion"),
            ("Términos / vencimientos", "terminos_o_vencimientos"),
            ("Riesgos procesales", "riesgos_procesales"),
            ("Ruta recomendada", "ruta_recomendada"),
            ("Ruta detallada", "ruta_detallada"),
            ("Fuentes KB", "fuentes_kb"),
            ("Pendientes de verificación", "pendientes_verificacion"),
        ):
            items = data.get(key) or []
            if items:
                lines.append(f"\n{label}:")
                lines.extend(f"- {x}" for x in items)
        return "\n".join(lines).strip()

    # RepresentacionVictimas
    if "teoria_caso" in data:
        lines = [
            "Representación de víctimas (preliminar)",
            f"Teoría del caso: {data.get('teoria_caso')}",
        ]
        dano = str(data.get("dano_afectacion") or "").strip()
        if dano:
            lines.append(f"Daño/afectación: {dano}")
        for label, key in (
            ("Derechos relevantes", "derechos_relevantes"),
            ("Enfoque diferencial", "enfoque_diferencial"),
            ("Riesgos de revictimización", "riesgos_revictimizacion"),
            ("Objetivos de representación", "objetivos_representacion"),
            ("Fuentes KB", "fuentes_kb"),
            ("Pendientes de verificación", "pendientes_verificacion"),
        ):
            items = data.get(key) or []
            if items:
                lines.append(f"\n{label}:")
                lines.extend(f"- {x}" for x in items)
        return "\n".join(lines).strip()

    # PreparacionAudiencia
    if "objetivo_audiencia" in data:
        lines = [
            "Preparación de audiencia (preliminar)",
            f"Objetivo: {data.get('objetivo_audiencia')}",
        ]
        for label, key in (
            ("Guion / puntos", "guion_puntos"),
            ("Solicitudes orales", "solicitudes_orales"),
            ("Preguntas clave", "preguntas_clave"),
            ("Riesgos", "riesgos_audiencia"),
            ("Checklist", "checklist"),
            ("Fuentes KB", "fuentes_kb"),
            ("Pendientes de verificación", "pendientes_verificacion"),
        ):
            items = data.get(key) or []
            if items:
                lines.append(f"\n{label}:")
                lines.extend(f"- {x}" for x in items)
        return "\n".join(lines).strip()

    # SeguimientoProcesal
    if "actuaciones_relevantes" in data and "proximas_acciones" in data:
        lines = [
            "Seguimiento procesal",
            str(data.get("resumen") or "").strip(),
            f"Radicado/referencia: {data.get('radicado_o_referencia')}",
        ]
        inac = str(data.get("inactividad_detectada") or "").strip()
        if inac:
            lines.append(f"Inactividad: {inac}")
        for label, key in (
            ("Actuaciones relevantes", "actuaciones_relevantes"),
            ("Términos / alertas", "terminos_alertas"),
            ("Próximas acciones", "proximas_acciones"),
            ("Fuentes KB", "fuentes_kb"),
            ("Pendientes de verificación", "pendientes_verificacion"),
        ):
            items = data.get(key) or []
            if items:
                lines.append(f"\n{label}:")
                lines.extend(f"- {x}" for x in items)
        return "\n".join(lines).strip()

    return str(data)


def extract_dictamen_calidad(output: Any) -> dict | None:
    """Extrae dictamen de calidad desde final_output o texto con claves conocidas."""
    if output is None:
        return None
    if hasattr(output, "model_dump"):
        data = output.model_dump()
        if "veredicto" in data:
            return data
        return None
    if isinstance(output, dict) and "veredicto" in output:
        return output
    return None
