# Reporte de gaps — página `/cliente` y mensaje de producto

**Fecha:** 2026-08-04  
**Página revisada:** `http://127.0.0.1:8000/cliente` (webchat víctima)  
**Criterio:** mensaje claro para el propósito de la página (intake víctima + HITL).

---

## Qué se arregló ahora

| Problema | Corrección |
|---|---|
| Título genérico “Consulta penal” | “Consulta para víctimas” |
| Lead sin flujo ni énfasis en revisión humana | Lead + 3 bullets de confianza (alcance, flujo, no emergencia) |
| Sin aviso de peligro inmediato | Pie: policía 123 / línea 155 |
| Errores casi ilegibles (`#f0c9a0`) | Error con contraste naranja/café |
| Link de consentimiento mint sobre fondo claro | Link azul LexiaTek + “leer aviso” |
| Botón Enviar: texto oscuro sobre azul | Texto blanco |
| Bienvenida “Lexiatek” + mensaje largo | “LexiaTek” + “IA prepara / abogado revisa” |
| Estados de chat redundantes / vagos | Copy alineado al flujo revisión → respuesta |

---

## Lo que aún falta (priorizado)

### P0 — producto / confianza
1. **Sync de prompts en prod** (`coordinador_caso` archivo vs DB) — riesgo de tono viejo fuera del early-return OOS.
2. **Gate OOS en `/chat/plan`** — aún puede armar planes para materias fuera de alcance.
3. **CI `validate_fase0` / conteo REQ** — checklist dice 45; validador espera 50.

### P1 — página `/cliente`
4. **Teléfono y correo opcionales:** si ambos vacíos, el canal es solo web; falta decir “la respuesta llega en este chat” para no sugerir contacto externo.
5. **Estado vacío post-start:** si falla el poll, puede mostrar “Aún no hay mensajes” aunque la bienvenida exista — endurecer refresh inmediato + retry.
6. **Indicador de “escribiendo / en revisión”** visual (spinner o tiempo estimado) además del banner de estado.
7. **Persistencia de sesión visible:** botón “continuar consulta” / “salir y borrar datos” (ARCO ligero en UI cliente).
8. **Alcance OOS en copy del chat** (familia/laboral/investigado): microcopy o primer mensaje sistema si triage marca fuera de alcance.

### P1 — escritorio abogado (mensaje claro al profesional)
8. **Bienvenida abogado** sigue siendo corta y genérica (“asistente de IA penal”) — alinear con tesis de valor (agilidad cognitiva + HITL).
9. **Onboarding 1 página dentro de `/abogado`** (modal o panel) enlazando `GUIA_1_PAGINA_ABOGADO.md` — hoy solo existe en docs.
10. **Canal víctima vs Inbox:** etiquetas aún pueden confundir “quién ve qué”; falta leyenda permanente de visibilidad.

### P2 — contenido / catálogo
11. **`lista-aprobacion-agentes-skills-pasos.md` y `documento-unico`** aún mencionan tutela / 11 roles (canon y ejecutiva ya actualizados).
12. **Skills tutela residuales en catálogo DB** (~7 IDs) — limpiar o marcar `retired` para no aparecer en auditorías.
13. **Pack diario no está en UI** — solo markdown; falta superficie en audit-portal o desk.
14. **Guión formación VIF** — Acto 3 histórico de tutela ya archivado; verificar que demos vivas no lo reabran.

### P2 — UX / branding
15. **Hero start sin ancla visual de producto** (solo logo + form) — opcional: atmósfera LexiaTek sin saturar (mantener sobriedad jurídica).
16. **Contraste tagline uppercase** en chat — legible pero denso; valorar frase en oración normal.
17. **Mobile:** composer OK; falta prueba real en viewport pequeño post-cambio.

### P3 — mensajería / legal
18. **Disclaimer de “no constituye asesoría definitiva”** en start (una línea) — hoy implícito en HITL.
19. **Privacidad footer** en start (enlace a `/legal/privacidad` además del aviso de casos).
20. **Idioma / tono trauma-informed** en placeholder y bienvenida — revisión con rol víctimas.

---

## Checklist “mensaje claro” (estado)

| Criterio | Start `/cliente` | Chat `/cliente` | Desk `/abogado` |
|---|---|---|---|
| Para quién es | ✅ Víctimas | 🟡 implícito | 🟡 |
| Qué hace la IA | ✅ | ✅ bienvenida | 🟡 |
| Qué hace el abogado | ✅ | ✅ | ✅ HITL |
| Qué no es (emergencia / tutela / OOS) | ✅ emergencia · 🟡 OOS | 🟡 | 🟡 |
| Qué pasa después de enviar | ✅ | ✅ | ✅ |
| Cumplimiento 1581 | ✅ | — | ✅ login |

---

## Recomendación siguiente

1. Deploy estáticos `/cliente` + welcome.  
2. Cerrar P0 técnicos (sync config, plan OOS, CI REQ).  
3. Meter guía de 1 página en el escritorio abogado (onboarding).  
4. Limpiar docs/catálogo tutela residual.
