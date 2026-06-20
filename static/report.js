/**
 * Reporte analítico por sesión Fase 0 — métricas, panel UI y exportación.
 */
const SessionReport = (() => {
  const META_LABELS = {
    pass: "Aprobada",
    fail: "Rechazada",
    pending: "Pendiente",
  };

  const LEGAL_DISCLAIMER =
    "Borrador analítico — requiere revisión humana. No constituye dictamen legal.";

  const ENABLE_RULES_AUTO = true;
  let rulesDebounceTimer = null;
  let cachedRulesInsights = null;

  function escapeHtml(text) {
    return String(text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function computeSessionFingerprint(session) {
    const payload = JSON.stringify({
      marks: session.marks || {},
      checklistChecked: session.checklistChecked || {},
      markNotes: session.markNotes || {},
      chatLen: (session.chatLog || []).length,
      lastChatTs: (session.chatLog || []).at(-1)?.ts || null,
    });
    let hash = 5381;
    for (let i = 0; i < payload.length; i += 1) {
      hash = (hash * 33) ^ payload.charCodeAt(i);
    }
    return (hash >>> 0).toString(36);
  }

  function normalizeBackendReport(data, session) {
    if (!data || typeof data !== "object") return null;
    return {
      rules_insights: data.rules_insights || [],
      llm_analysis: data.llm_analysis || null,
      llm_status: data.llm_status || (data.llm_analysis ? "ok" : null),
      llm_message: data.llm_message || "",
      generated_at: data.generated_at || null,
      sessionFingerprint: data.sessionFingerprint || computeSessionFingerprint(session),
    };
  }

  function computeMetrics(session) {
    const marks = session.marks || {};
    const chatLog = session.chatLog || [];
    const events = session.events || [];
    const checklist = session.checklistChecked || {};

    const total = VALIDATION_TOTAL_WEIGHT;
    let score = 0;
    let passed = 0;
    let failed = 0;

    VALIDATION_TESTS.forEach((test) => {
      const mark = marks[test.id];
      if (mark === "pass") {
        score += test.weight || 0;
        passed += 1;
      } else if (mark === "fail") {
        failed += 1;
      }
    });

    const pending = VALIDATION_TESTS.length - passed - failed;
    const userMsgs = chatLog.filter((m) => m.role === "user");
    const assistantMsgs = chatLog.filter((m) => m.role === "assistant");
    const latencies = assistantMsgs
      .map((m) => m.latencyMs)
      .filter((v) => typeof v === "number");
    const avgLatencyMs = latencies.length
      ? Math.round(latencies.reduce((a, b) => a + b, 0) / latencies.length)
      : null;

    const checklistTotal = VALIDATION_CHECKLIST.length;
    const checklistDone = Object.values(checklist).filter(Boolean).length;

    let durationMinutes = null;
    if (session.startedAt && session.lastActivityAt) {
      const ms = new Date(session.lastActivityAt) - new Date(session.startedAt);
      durationMinutes = Math.max(0, Math.round((ms / 60000) * 10) / 10);
    }

    const sections = VALIDATION_TESTS.map((test) => {
      const mark = marks[test.id] || "pending";
      const linked = chatLog.filter((m) => m.blockId === test.id);
      return {
        id: test.id,
        title: test.title,
        weight: test.weight,
        mark,
        pointsEarned: mark === "pass" ? test.weight : 0,
        interactions: linked.length,
        note: (session.markNotes || {})[test.id] || "",
      };
    });

    return {
      sessionId: session.sessionId,
      score,
      totalWeight: total,
      scorePercent: total ? Math.round((score / total) * 100) : 0,
      sectionsPassed: passed,
      sectionsFailed: failed,
      sectionsPending: pending,
      checklistDone,
      checklistTotal,
      checklistPercent: checklistTotal ? Math.round((checklistDone / checklistTotal) * 100) : 0,
      chatTurns: userMsgs.length,
      assistantReplies: assistantMsgs.length,
      probeQuestions: userMsgs.filter((m) => m.via === "probe").length,
      manualQuestions: userMsgs.filter((m) => m.via !== "probe").length,
      avgLatencyMs,
      probeRegenerations: events.filter((e) => e.type === "generate_probes").length,
      durationMinutes,
      sections,
    };
  }

  function formatDuration(minutes) {
    if (minutes == null) return "—";
    if (minutes < 1) return "< 1 min";
    return `${minutes} min`;
  }

  function formatMark(mark) {
    return META_LABELS[mark] || mark;
  }

  function buildExecutiveSummary(metrics) {
    if (metrics.sectionsPending === VALIDATION_TESTS.length) {
      return "Sesión iniciada — aún no hay secciones evaluadas.";
    }
    if (metrics.score === 100) {
      return "Veredicto: puntaje máximo (100/100). Fase 0 puede considerarse validada según la rúbrica.";
    }
    if (metrics.score >= 70 && metrics.sectionsFailed === 0) {
      return `Veredicto: desempeño aceptable (${metrics.score}/100). Revise secciones pendientes antes de cerrar.`;
    }
    if (metrics.sectionsFailed > 0) {
      return `Veredicto: requiere corrección (${metrics.score}/100). Hay ${metrics.sectionsFailed} sección(es) rechazada(s).`;
    }
    return `Veredicto: en progreso (${metrics.score}/100). Complete las pruebas pendientes.`;
  }

  function renderMetricsCards(metrics) {
    return `
      <div class="report-cards">
        <div class="report-card"><span class="report-card-label">Puntaje</span><strong>${metrics.score}/${metrics.totalWeight}</strong><span class="report-card-sub">${metrics.scorePercent}%</span></div>
        <div class="report-card"><span class="report-card-label">Duración</span><strong>${formatDuration(metrics.durationMinutes)}</strong></div>
        <div class="report-card"><span class="report-card-label">Mensajes</span><strong>${metrics.chatTurns}</strong></div>
        <div class="report-card"><span class="report-card-label">Checklist</span><strong>${metrics.checklistDone}/${metrics.checklistTotal}</strong></div>
      </div>`;
  }

  function renderSectionsTable(metrics) {
    const rows = metrics.sections
      .map(
        (s) => `
      <tr class="report-row report-row--${s.mark}">
        <td>${escapeHtml(s.title)}</td>
        <td>${formatMark(s.mark)}</td>
        <td>${s.pointsEarned}/${s.weight}</td>
        <td>${s.interactions}</td>
        <td>${s.note ? escapeHtml(s.note) : "—"}</td>
      </tr>`
      )
      .join("");
    return `
      <table class="report-table">
        <thead><tr><th>Sección</th><th>Estado</th><th>Puntos</th><th>Mensajes vinculados</th><th>Nota del revisor</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>`;
  }

  function renderInsightsList(items, emptyText) {
    if (!items?.length) return `<p class="report-empty">${escapeHtml(emptyText)}</p>`;
    return `<ul class="report-insights">${items.map((i) => `<li>${escapeHtml(i)}</li>`).join("")}</ul>`;
  }

  function renderLlmBlock(llm, status, message, hasGenerated) {
    if (llm && status === "ok") {
      return `
        <p class="report-summary">${escapeHtml(llm.summary || "")}</p>
        <h4>Fortalezas</h4>${renderInsightsList(llm.strengths, "Sin datos.")}
        <h4>Debilidades</h4>${renderInsightsList(llm.weaknesses, "Sin datos.")}
        <h4>Recomendaciones</h4>${renderInsightsList(llm.recommendations, "Sin datos.")}`;
    }
    if (hasGenerated && status && status !== "ok") {
      return `<p class="report-empty report-llm-status report-llm-status--${escapeHtml(status)}">${escapeHtml(message || "Análisis IA no disponible.")}</p>`;
    }
    if (hasGenerated && !llm) {
      return `<p class="report-empty">${escapeHtml(message || "No se generó análisis IA para esta sesión.")}</p>`;
    }
    return `<p class="report-empty">Pulse «Generar / Actualizar análisis» para obtener un resumen con IA basado en esta sesión.</p>`;
  }

  function renderEventsTimeline(events, expanded = false) {
    const all = events || [];
    const keyEvents = (expanded ? all : all.slice(-8)).slice().reverse();
    if (!keyEvents.length) return `<p class="report-empty">Sin eventos registrados aún.</p>`;
    const items = keyEvents
      .map((e) => {
        const time = e.ts ? new Date(e.ts).toLocaleTimeString("es-CO", { hour: "2-digit", minute: "2-digit" }) : "";
        let label = e.type;
        if (e.type === "mark") {
          label = `Marca ${formatMark(e.mark)} — ${e.blockTitle || e.blockId}`;
          if (e.note) label += ` (${e.note})`;
        }
        if (e.type === "checklist") label = `Checklist ítem ${Number(e.index) + 1}: ${e.checked ? "marcado" : "desmarcado"}`;
        if (e.type === "generate_probes") label = `Preguntas IA regeneradas${e.blockId ? ` (${e.blockId})` : ""}`;
        if (e.type === "session_start") label = "Inicio de sesión";
        return `<li><time>${escapeHtml(time)}</time> ${escapeHtml(label)}</li>`;
      })
      .join("");
    const toggle =
      all.length > 8
        ? `<button type="button" class="report-events-toggle" data-expanded="${expanded}">${expanded ? "Ver menos" : `Ver todos (${all.length})`}</button>`
        : "";
    return `<ul class="report-events">${items}</ul>${toggle}`;
  }

  function renderTranscript(chatLog) {
    if (!chatLog?.length) return `<p class="report-empty">Sin conversación en esta sesión.</p>`;
    return chatLog
      .map((entry) => {
        const role = entry.role === "user" ? "Abogada" : "Asistente";
        const test = entry.blockId ? VALIDATION_TESTS.find((t) => t.id === entry.blockId) : null;
        const blockLabel = test ? test.title : entry.blockId || "";
        const meta = blockLabel ? ` · ${blockLabel}` : "";
        const time = entry.ts
          ? new Date(entry.ts).toLocaleTimeString("es-CO", { hour: "2-digit", minute: "2-digit" })
          : "";
        const latency =
          entry.role === "assistant" && typeof entry.latencyMs === "number"
            ? ` · ${entry.latencyMs} ms`
            : "";
        return `<div class="report-transcript-entry report-transcript-entry--${entry.role}">
          <span class="report-transcript-meta">${escapeHtml(role)}${escapeHtml(meta)} · ${escapeHtml(time)}${latency}</span>
          <p>${escapeHtml(entry.text)}</p>
        </div>`;
      })
      .join("");
  }

  function renderStaleBanner(lastReport, session) {
    if (!lastReport?.generated_at) return "";
    const fp = lastReport.sessionFingerprint;
    if (!fp || fp === computeSessionFingerprint(session)) return "";
    const when = new Date(lastReport.generated_at).toLocaleString("es-CO");
    return `<p class="report-stale-banner" role="status">Análisis generado a las ${escapeHtml(when)} — la sesión cambió después; regenere si desea actualizar.</p>`;
  }

  function renderPanel(session, lastReport, rulesOverride) {
    const metrics = computeMetrics(session);
    const normalized = lastReport ? normalizeBackendReport(lastReport, session) : null;
    const rules =
      normalized?.rules_insights?.length
        ? normalized.rules_insights
        : rulesOverride?.length
          ? rulesOverride
          : cachedRulesInsights || [];
    const llm = normalized?.llm_analysis || null;
    const llmStatus = normalized?.llm_status || null;
    const llmMessage = normalized?.llm_message || "";
    const generatedAt = normalized?.generated_at
      ? new Date(normalized.generated_at).toLocaleString("es-CO")
      : null;
    const hasGenerated = Boolean(normalized?.generated_at);

    return `
      <div class="report-panel-inner" id="report-print-area">
        <p class="report-legal-disclaimer">${escapeHtml(LEGAL_DISCLAIMER)}</p>
        <p class="report-session-id">Sesión <code>${escapeHtml(session.sessionId || "—")}</code></p>
        ${renderStaleBanner(normalized, session)}
        <p class="report-executive">${escapeHtml(buildExecutiveSummary(metrics))}</p>
        ${renderMetricsCards(metrics)}
        <p class="report-substats">
          Probe: ${metrics.probeQuestions} · Manual: ${metrics.manualQuestions} ·
          Latencia media: ${metrics.avgLatencyMs != null ? `${metrics.avgLatencyMs} ms` : "—"} ·
          Regeneraciones IA: ${metrics.probeRegenerations}
        </p>
        <h4>Por sección</h4>
        ${renderSectionsTable(metrics)}
        <h4>Eventos recientes</h4>
        <div id="report-events-wrap">${renderEventsTimeline(session.events)}</div>
        <h4>Conclusiones (reglas Fase 0)</h4>
        ${renderInsightsList(rules, "Cargando conclusiones…")}
        <h4>Análisis IA ${generatedAt ? `<span class="report-generated-at">(${escapeHtml(generatedAt)})</span>` : ""}</h4>
        <div id="report-llm-block">${renderLlmBlock(llm, llmStatus, llmMessage, hasGenerated)}</div>
        <p class="report-legal-disclaimer report-legal-disclaimer--footer">${escapeHtml(LEGAL_DISCLAIMER)}</p>
      </div>`;
  }

  let getSessionFn = () => ({});
  let saveSessionFn = () => {};
  let getUserIdFn = () => "web";
  let eventsExpanded = false;

  function init({ getSession, saveSession, getUserId }) {
    getSessionFn = getSession;
    saveSessionFn = saveSession;
    getUserIdFn = getUserId;

    document.getElementById("btn-generate-report")?.addEventListener("click", generateAnalysis);
    document.getElementById("btn-export-pdf")?.addEventListener("click", exportPdf);

    document.getElementById("session-report-body")?.addEventListener("click", (e) => {
      const btn = e.target.closest(".report-events-toggle");
      if (btn) {
        eventsExpanded = btn.dataset.expanded !== "true";
        refresh();
      }
    });

    refresh();
  }

  async function fetchRulesInsights(session) {
    if (!ENABLE_RULES_AUTO) return [];
    try {
      const res = await authFetch("/validation/session-rules", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session }),
      });
      if (!res.ok) return [];
      const data = await res.json();
      cachedRulesInsights = data.rules_insights || [];
      return cachedRulesInsights;
    } catch {
      return [];
    }
  }

  function scheduleRulesRefresh() {
    if (!ENABLE_RULES_AUTO) return;
    clearTimeout(rulesDebounceTimer);
    rulesDebounceTimer = setTimeout(async () => {
      const session = getSessionFn();
      const rules = await fetchRulesInsights(session);
      const body = document.getElementById("session-report-body");
      if (body && rules.length) {
        body.innerHTML = renderPanel(session, session.lastReport, rules);
      }
    }, 300);
  }

  function refresh() {
    const session = getSessionFn();
    const body = document.getElementById("session-report-body");
    const transcript = document.getElementById("session-report-transcript");
    if (body) body.innerHTML = renderPanel(session, session.lastReport, cachedRulesInsights);
    if (transcript) transcript.innerHTML = renderTranscript(session.chatLog);
    scheduleRulesRefresh();
  }

  async function generateAnalysis() {
    const btn = document.getElementById("btn-generate-report");
    const session = getSessionFn();
    if (btn) {
      btn.disabled = true;
      btn.textContent = "Generando…";
    }
    try {
      const res = await authFetch("/validation/session-report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: getUserIdFn(), session }),
      });
      if (!res.ok) {
        if (Toast?.show) Toast.show("No se pudo generar el reporte. Intente de nuevo.", "error");
        else alert("No se pudo generar el reporte. Intente de nuevo.");
        return;
      }
      const data = await res.json();
      const fingerprint = computeSessionFingerprint(session);
      session.lastReport = normalizeBackendReport(
        {
          rules_insights: data.rules_insights,
          llm_analysis: data.llm_analysis,
          llm_status: data.llm_status,
          llm_message: data.llm_message,
          generated_at: data.generated_at,
          sessionFingerprint: fingerprint,
        },
        session
      );
      cachedRulesInsights = data.rules_insights || [];
      saveSessionFn(session);
      refresh();
    } catch {
      if (Toast?.show) Toast.show("Error de conexión al generar el reporte.", "error");
      else alert("Error de conexión al generar el reporte.");
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.textContent = "Generar / Actualizar análisis";
      }
    }
  }

  const PRINT_STYLES = `
    * { box-sizing: border-box; }
    body {
      margin: 0;
      padding: 1.25rem 1.5rem;
      font-family: "Manrope", system-ui, sans-serif;
      font-size: 12px;
      line-height: 1.45;
      color: #111;
      background: #fff;
    }
    h1 {
      margin: 0 0 1rem;
      font-size: 1.15rem;
      color: #0d9488;
      letter-spacing: -0.02em;
    }
    .report-legal-disclaimer { color: #666; font-size: 10px; font-style: italic; margin-bottom: 0.5rem; }
    .report-stale-banner { background: #fff3cd; color: #856404; padding: 0.5rem 0.65rem; border-radius: 6px; font-size: 11px; margin-bottom: 0.5rem; }
    .report-executive { font-weight: 700; color: #222; margin-bottom: 0.55rem; }
    .report-session-id { color: #555; font-size: 11px; margin-bottom: 0.55rem; }
    .report-session-id code { color: #0d9488; }
    .report-cards {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 0.45rem;
      margin-bottom: 0.55rem;
    }
    .report-card {
      padding: 0.55rem 0.65rem;
      border: 1px solid #ddd;
      border-radius: 8px;
      background: #f8f8f8;
    }
    .report-card-label {
      display: block;
      color: #666;
      font-size: 9px;
      font-weight: 800;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      margin-bottom: 0.2rem;
    }
    .report-card-sub { display: block; font-size: 10px; color: #888; margin-top: 0.15rem; }
    .report-card strong { font-size: 13px; color: #111; }
    .report-substats { color: #666; font-size: 10px; margin-bottom: 0.65rem; }
    h4 {
      color: #0d9488;
      font-size: 10px;
      font-weight: 800;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      margin: 0.75rem 0 0.4rem;
    }
    .report-table { width: 100%; border-collapse: collapse; font-size: 11px; }
    .report-table th, .report-table td {
      padding: 0.4rem 0.45rem;
      border-bottom: 1px solid #ddd;
      text-align: left;
    }
    .report-table th { color: #666; font-weight: 800; }
    .report-row--pass td:nth-child(2) { color: #0d9488; }
    .report-row--fail td:nth-child(2) { color: #c05621; }
    .report-insights, .report-events { list-style: none; padding: 0; margin: 0; }
    .report-insights li, .report-events li {
      position: relative;
      padding-left: 0.85rem;
      margin-bottom: 0.35rem;
      color: #444;
    }
    .report-insights li::before, .report-events li::before {
      content: "•";
      position: absolute;
      left: 0;
      color: #0d9488;
    }
    .report-events time { color: #0d9488; font-size: 10px; margin-right: 0.35rem; }
    .report-summary { color: #222; margin-bottom: 0.5rem; }
    .report-empty { color: #888; font-style: italic; }
    .report-generated-at { font-weight: 400; color: #666; text-transform: none; letter-spacing: 0; }
    .report-transcript-entry { margin-bottom: 0.5rem; padding-bottom: 0.35rem; border-bottom: 1px solid #eee; }
    .report-transcript-meta { font-size: 10px; color: #666; }
    @media print {
      body { padding: 0; }
      @page { margin: 1.2cm; }
    }
  `;

  function buildPrintDocument(title, reportHtml, transcriptHtml) {
    const transcriptBlock = transcriptHtml
      ? `<h4>Conversación completa</h4><div class="report-transcript">${transcriptHtml}</div>`
      : "";
    return `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>${escapeHtml(title)}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap" rel="stylesheet">
  <style>${PRINT_STYLES}</style>
</head>
<body>
  <h1>Reporte de sesión — Fase 0</h1>
  <div class="report-panel-inner">${reportHtml}</div>
  ${transcriptBlock}
</body>
</html>`;
  }

  function exportPdf() {
    refresh();
    const area = document.getElementById("report-print-area");
    if (!area || !area.innerHTML.trim()) {
      if (Toast?.show) Toast.show("No hay contenido de reporte para exportar.", "error");
      else alert("No hay contenido de reporte para exportar.");
      return;
    }

    const session = getSessionFn();
    const transcriptHtml = renderTranscript(session.chatLog);
    const docTitle = `Reporte Fase 0 — ${session.sessionId || "sesión"}`;
    const printWin = window.open("", "_blank");
    if (!printWin) {
      if (Toast?.show) Toast.show("Permita ventanas emergentes para exportar a PDF.", "error");
      else alert("Permita ventanas emergentes para exportar a PDF.");
      return;
    }
    printWin.opener = null;

    printWin.document.open();
    printWin.document.write(buildPrintDocument(docTitle, area.innerHTML, transcriptHtml));
    printWin.document.close();
    printWin.document.title = docTitle;

    const triggerPrint = () => {
      printWin.focus();
      printWin.print();
    };

    printWin.addEventListener("afterprint", () => printWin.close());
    if (printWin.document.readyState === "complete") {
      setTimeout(triggerPrint, 300);
    } else {
      printWin.addEventListener("load", () => setTimeout(triggerPrint, 300));
    }
  }

  async function exportDoc() {
    const session = getSessionFn();
    try {
      const res = await authFetch("/validation/session-export", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: getUserIdFn(),
          session,
          report: session.lastReport || {},
        }),
      });
      if (!res.ok) {
        if (Toast?.show) Toast.show("No se pudo descargar el informe.", "error");
        else alert("No se pudo descargar el informe.");
        return;
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `reporte-fase0-${session.sessionId || "sesion"}.doc`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      if (Toast?.show) Toast.show("Error de conexión al descargar.", "error");
      else alert("Error de conexión al descargar.");
    }
  }

  return {
    init,
    refresh,
    computeMetrics,
    computeSessionFingerprint,
    normalizeBackendReport,
  };
})();
