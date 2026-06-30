/**
 * Consola de soporte: operaciones, spans OpenAI y diagnóstico de sesiones.
 */
(() => {
  "use strict";

  const api = (url, options) => (window.authFetch ? window.authFetch(url, options) : fetch(url, options));
  const esc = (s) =>
    String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");

  let selectedSessionId = null;
  let tracesBySession = new Map();

  function openaiLogUrl(responseId) {
    if (!responseId) return null;
    return `https://platform.openai.com/logs?api=responses&q=${encodeURIComponent(responseId)}`;
  }

  function statusClass(blocked, pending) {
    if (blocked) return "support-op--blocked";
    if (pending) return "support-op--pending";
    return "support-op--ok";
  }

  function renderOpSummary(op) {
    const when = op.created_at ? new Date(op.created_at).toLocaleString("es-CO") : "—";
    return `
      <button type="button" class="support-op ${statusClass(op.blocked, op.pending_review)}" data-session="${esc(op.session_id)}" data-trace="${esc(op.trace_id)}">
        <span class="support-op-time">${esc(when)}</span>
        <strong class="support-op-route">${esc(op.sent_to_agent || op.route || "—")}</strong>
        <span class="support-op-skill">${esc(op.skill_kan || "")}</span>
        <p class="support-op-input">${esc((op.input_summary || "").slice(0, 120))}</p>
        <span class="support-op-meta">${esc(op.span_count)} spans · ${esc(op.tokens_total)} tok · turno ${esc(op.turn_index)}</span>
        ${op.blocked ? '<span class="support-badge support-badge--danger">Bloqueado</span>' : ""}
      </button>`;
  }

  async function loadOperations() {
    const list = document.getElementById("support-ops-list");
    list.innerHTML = '<p class="support-empty">Cargando…</p>';
    try {
      const res = await api("/support/operations?limit=50");
      const data = await res.json();
      const ops = data.operations || [];
      list.innerHTML = ops.length
        ? ops.map(renderOpSummary).join("")
        : '<p class="support-empty">Sin operaciones registradas.</p>';
      list.querySelectorAll(".support-op").forEach((btn) => {
        btn.addEventListener("click", () => selectOperation(btn.dataset.session, btn.dataset.trace));
      });
    } catch {
      list.innerHTML = '<p class="support-empty support-empty--error">No se pudieron cargar operaciones.</p>';
    }
  }

  async function loadSessions() {
    const list = document.getElementById("support-sessions-list");
    list.innerHTML = '<p class="support-empty">…</p>';
    try {
      const res = await api("/support/sessions?limit=20");
      const data = await res.json();
      const sessions = data.sessions || [];
      list.innerHTML = sessions.length
        ? sessions
            .map(
              (s) => `
          <button type="button" class="support-session" data-session="${esc(s.session_id)}">
            <strong>${esc(s.session_id)}</strong>
            <span>${esc(s.message_count)} msgs · ${esc(new Date(s.updated_at).toLocaleString("es-CO"))}</span>
          </button>`
            )
            .join("")
        : '<p class="support-empty">Sin sesiones.</p>';
      list.querySelectorAll(".support-session").forEach((btn) => {
        btn.addEventListener("click", () => loadSessionDetail(btn.dataset.session));
      });
    } catch {
      list.innerHTML = '<p class="support-empty">Error al cargar sesiones.</p>';
    }
  }

  async function loadSessionDetail(sessionId) {
    selectedSessionId = sessionId;
    document.getElementById("support-session-input").value = sessionId;
    const meta = document.getElementById("support-turn-meta");
    meta.innerHTML = '<p class="support-empty">Cargando sesión…</p>';
    try {
      const res = await api(`/support/operations/${encodeURIComponent(sessionId)}?limit=40`);
      const data = await res.json();
      tracesBySession.set(sessionId, data.traces || []);
      meta.innerHTML = `
        <p><strong>Sesión:</strong> <code>${esc(sessionId)}</code></p>
        <p><strong>Mensajes:</strong> ${esc(data.message_count)} · <strong>Turnos trazados:</strong> ${esc((data.traces || []).length)}</p>
        ${data.expediente ? `<p><strong>Expediente:</strong> ${esc(data.expediente.materia || "—")} · ${esc(data.expediente.radicado || "sin radicado")}</p>` : ""}
      `;
      const timeline = document.getElementById("support-span-timeline");
      timeline.innerHTML = (data.traces || [])
        .map((t, i) => {
          const p = t.payload || t;
          return `<button type="button" class="support-turn-btn" data-session="${esc(sessionId)}" data-idx="${i}">
            Turno ${esc(p.turn_index ?? i)} · ${esc(p.sent_to_agent || p.route || "?")} · ${esc((p.input_summary || "").slice(0, 60))}
          </button>`;
        })
        .join("");
      timeline.querySelectorAll(".support-turn-btn").forEach((btn) => {
        btn.addEventListener("click", () => showTraceDetail(sessionId, Number(btn.dataset.idx)));
      });
      if ((data.traces || []).length) showTraceDetail(sessionId, data.traces.length - 1);
    } catch {
      meta.innerHTML = '<p class="support-empty support-empty--error">No se pudo cargar la sesión.</p>';
    }
  }

  function showTraceDetail(sessionId, idx) {
    const traces = tracesBySession.get(sessionId) || [];
    const record = traces[idx];
    if (!record) return;
    const payload = record.payload || record;
    const spans = payload.spans || [];
    const timeline = document.getElementById("support-span-timeline");
    timeline.querySelectorAll(".support-turn-btn").forEach((b, i) => {
      b.classList.toggle("is-active", i === idx);
    });

    const spanHtml = spans.length
      ? spans
          .map((sp) => {
            const st = sp.status || "done";
            return `<div class="support-span support-span--${esc(st)}">
              <span class="support-span-kind">${esc(sp.kind || "")}</span>
              <strong>${esc(sp.name || "")}</strong>
              <p>${esc(sp.detail || "")}</p>
            </div>`;
          })
          .join("")
      : '<p class="support-empty">Sin spans en este turno.</p>';
    document.getElementById("support-turn-meta").innerHTML = `
      <p><strong>Trace:</strong> <code>${esc(payload.trace_id || record.trace_id)}</code></p>
      <p><strong>Agente:</strong> ${esc(payload.sent_to_agent || "—")} · <strong>Skill:</strong> ${esc(payload.skill_kan || "—")}</p>
      <p><strong>Estado:</strong> ${payload.blocked ? "BLOQUEADO" : payload.human_review_required ? "Revisión humana" : "OK"}</p>
      <div class="support-spans-wrap">${spanHtml}</div>
    `;

    const completion = payload.completion || {};
    const calls = completion.calls || [];
    const openaiEl = document.getElementById("support-openai-panel");
    openaiEl.innerHTML = calls.length
      ? calls
          .map((c) => {
            const url = openaiLogUrl(c.response_id);
            return `<div class="support-completion">
              <p><strong>${esc(c.call_id || "completion")}</strong> · ${esc(c.model || "—")}</p>
              <p>Tokens: ${esc(c.usage?.input_tokens)}/${esc(c.usage?.output_tokens)}/${esc(c.usage?.total_tokens)}</p>
              <p class="support-mono">response_id: ${esc(c.response_id || "—")}</p>
              ${url ? `<a class="btn-firma-link" href="${url}" target="_blank" rel="noopener">Ver en OpenAI Logs ↗</a>` : ""}
              <details><summary>Input preview</summary><pre>${esc(c.input_preview || "")}</pre></details>
            </div>`;
          })
          .join("")
      : `<p class="support-empty">${esc(completion.note || "Sin completions en este turno.")}</p>`;

    document.getElementById("support-json").textContent = JSON.stringify(payload, null, 2);
  }

  async function selectOperation(sessionId, traceId) {
    await loadSessionDetail(sessionId);
    const traces = tracesBySession.get(sessionId) || [];
    const idx = traces.findIndex((t) => (t.payload?.trace_id || t.trace_id) === traceId);
    if (idx >= 0) showTraceDetail(sessionId, idx);
  }

  async function checkHealth() {
    const el = document.getElementById("support-health");
    try {
      const res = await fetch("/health");
      const data = await res.json();
      el.textContent = `${data.persistencia} · OpenAI ${data.openai_configured ? "OK" : "off"}`;
      el.className = "support-health support-health--ok";
    } catch {
      el.textContent = "Servicio no disponible";
      el.className = "support-health support-health--error";
    }
  }

  document.getElementById("support-search-form")?.addEventListener("submit", (e) => {
    e.preventDefault();
    const sid = document.getElementById("support-session-input").value.trim();
    if (sid) loadSessionDetail(sid);
  });

  document.getElementById("support-refresh")?.addEventListener("click", () => {
    loadOperations();
    loadSessions();
    checkHealth();
  });

  document.getElementById("auth-logout-btn")?.addEventListener("click", () => {
    window.AgentAuth?.logout(false);
  });

  function boot() {
    checkHealth();
    loadOperations();
    loadSessions();
    setInterval(loadOperations, 60000);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
