/**
 * Observatorio de soporte: operaciones, spans OpenAI y diagnóstico en vivo.
 * Modo vivo: refresca sola y sigue el último turno sin interacción.
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

  const LIVE_MS = 3000;
  let selectedSessionId = null;
  let selectedTraceId = null;
  let tracesBySession = new Map();
  let liveTimer = null;
  let lastFingerprint = "";
  let quietRefresh = false;

  function liveEnabled() {
    return Boolean(document.getElementById("support-live-toggle")?.checked);
  }

  function followEnabled() {
    return Boolean(document.getElementById("support-follow-toggle")?.checked);
  }

  function setLivePill(on) {
    const pill = document.getElementById("support-live-pill");
    if (!pill) return;
    pill.hidden = !on;
  }

  function openaiLogUrl(responseId) {
    if (!responseId) return null;
    return `https://platform.openai.com/logs?api=responses&q=${encodeURIComponent(responseId)}`;
  }

  function statusClass(blocked, pending) {
    if (blocked) return "support-op--blocked";
    if (pending) return "support-op--pending";
    return "support-op--ok";
  }

  function opFingerprint(ops) {
    if (!ops.length) return "empty";
    const top = ops[0];
    return `${top.trace_id}|${top.created_at}|${ops.length}|${top.span_count}|${top.blocked}|${top.pending_review}`;
  }

  function renderOpSummary(op) {
    const when = op.created_at ? new Date(op.created_at).toLocaleString("es-CO") : "—";
    const followed =
      selectedTraceId && op.trace_id === selectedTraceId ? " is-followed" : "";
    return `
      <button type="button" class="support-op ${statusClass(op.blocked, op.pending_review)}${followed}" data-session="${esc(op.session_id)}" data-trace="${esc(op.trace_id)}">
        <span class="support-op-time">${esc(when)}</span>
        <strong class="support-op-route">${esc(op.sent_to_agent || op.route || "—")}</strong>
        <span class="support-op-skill">${esc(op.skill_kan || "")}</span>
        <p class="support-op-input">${esc((op.input_summary || "").slice(0, 120))}</p>
        <span class="support-op-meta">${esc(op.span_count)} spans · ${esc(op.tokens_total)} tok · turno ${esc(op.turn_index)}${op.budget_exceeded ? " · BUDGET" : ""}${op.estimated_cost_usd != null ? ` · ~$${esc(op.estimated_cost_usd)}` : ""}</span>
        ${op.blocked ? '<span class="support-badge support-badge--danger">Bloqueado</span>' : ""}
        ${op.budget_exceeded ? '<span class="support-badge support-badge--danger">Budget</span>' : ""}
      </button>`;
  }

  async function loadOperations(opts = {}) {
    const { silent = false, autoFollow = false } = opts;
    const list = document.getElementById("support-ops-list");
    if (!list) return;
    if (!silent) list.innerHTML = '<p class="support-empty">Cargando…</p>';
    try {
      const res = await api("/support/operations?limit=50");
      const data = await res.json();
      const ops = data.operations || [];
      const fp = opFingerprint(ops);
      const changed = fp !== lastFingerprint;
      lastFingerprint = fp;

      list.innerHTML = ops.length
        ? ops.map(renderOpSummary).join("")
        : '<p class="support-empty">Sin operaciones registradas. Abra /abogado y envíe un mensaje, o espere tráfico.</p>';
      list.querySelectorAll(".support-op").forEach((btn) => {
        btn.addEventListener("click", () => {
          selectedTraceId = btn.dataset.trace;
          selectOperation(btn.dataset.session, btn.dataset.trace);
        });
      });

      if (ops.length && (autoFollow || (followEnabled() && changed))) {
        const top = ops[0];
        selectedTraceId = top.trace_id;
        await selectOperation(top.session_id, top.trace_id);
      } else if (selectedSessionId && selectedTraceId && changed) {
        await selectOperation(selectedSessionId, selectedTraceId);
      }
    } catch {
      if (!silent) {
        list.innerHTML = '<p class="support-empty support-empty--error">No se pudieron cargar operaciones.</p>';
      }
    }
  }

  async function loadSessions(silent = false) {
    const list = document.getElementById("support-sessions-list");
    if (!list) return;
    if (!silent) list.innerHTML = '<p class="support-empty">…</p>';
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
      if (!silent) list.innerHTML = '<p class="support-empty">Error al cargar sesiones.</p>';
    }
  }

  async function loadSessionDetail(sessionId) {
    selectedSessionId = sessionId;
    const input = document.getElementById("support-session-input");
    if (input) input.value = sessionId;
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
        btn.addEventListener("click", () => {
          const traces = tracesBySession.get(sessionId) || [];
          const rec = traces[Number(btn.dataset.idx)];
          selectedTraceId = rec?.payload?.trace_id || rec?.trace_id || null;
          showTraceDetail(sessionId, Number(btn.dataset.idx));
        });
      });
      if ((data.traces || []).length) {
        let idx = data.traces.length - 1;
        if (selectedTraceId) {
          const found = data.traces.findIndex(
            (t) => (t.payload?.trace_id || t.trace_id) === selectedTraceId
          );
          if (found >= 0) idx = found;
        }
        showTraceDetail(sessionId, idx);
      }
    } catch {
      meta.innerHTML = '<p class="support-empty support-empty--error">No se pudo cargar la sesión.</p>';
    }
  }

  function showTraceDetail(sessionId, idx) {
    const traces = tracesBySession.get(sessionId) || [];
    const record = traces[idx];
    if (!record) return;
    const payload = record.payload || record;
    selectedTraceId = payload.trace_id || record.trace_id || selectedTraceId;
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
              <p>Tokens: ${esc(c.usage?.input_tokens)}/${esc(c.usage?.output_tokens)}/${esc(c.usage?.total_tokens)}${c.estimated_cost_usd != null ? ` · ~USD ${esc(c.estimated_cost_usd)}` : ""}</p>
              <p class="support-mono">response_id: ${esc(c.response_id || "—")}</p>
              ${url ? `<a class="btn-firma-link" href="${url}" target="_blank" rel="noopener">Ver en OpenAI Logs ↗</a>` : ""}
              <details><summary>Input preview</summary><pre>${esc(c.input_preview || "")}</pre></details>
            </div>`;
          })
          .join("")
      : `<p class="support-empty">${esc(completion.note || "Sin completions en este turno.")}</p>`;
    if (completion.budget_exceeded || completion.summary?.estimated_cost_usd != null) {
      openaiEl.insertAdjacentHTML(
        "afterbegin",
        `<p class="support-budget ${completion.budget_exceeded ? "support-budget--warn" : ""}">
          ${completion.budget_exceeded ? "<strong>Presupuesto de tokens excedido.</strong> " : ""}
          Costo turno: ${
            completion.summary?.estimated_cost_usd != null
              ? `~USD ${esc(completion.summary.estimated_cost_usd)}`
              : "—"
          }
          · tope AGENT_MAX_TOTAL_TOKENS
        </p>`
      );
    }

    document.getElementById("support-json").textContent = JSON.stringify(payload, null, 2);
  }

  async function selectOperation(sessionId, traceId) {
    selectedTraceId = traceId;
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

  async function tickLive() {
    if (!liveEnabled() || quietRefresh) return;
    quietRefresh = true;
    try {
      await Promise.all([loadOperations({ silent: true, autoFollow: followEnabled() }), loadSessions(true), checkHealth()]);
    } finally {
      quietRefresh = false;
    }
  }

  function startLive() {
    stopLive();
    setLivePill(liveEnabled());
    if (!liveEnabled()) return;
    liveTimer = setInterval(tickLive, LIVE_MS);
  }

  function stopLive() {
    if (liveTimer) {
      clearInterval(liveTimer);
      liveTimer = null;
    }
    setLivePill(false);
  }

  document.getElementById("support-search-form")?.addEventListener("submit", (e) => {
    e.preventDefault();
    const sid = document.getElementById("support-session-input").value.trim();
    if (sid) loadSessionDetail(sid);
  });

  document.getElementById("support-refresh")?.addEventListener("click", () => {
    lastFingerprint = "";
    loadOperations({ autoFollow: followEnabled() });
    loadSessions();
    checkHealth();
  });

  document.getElementById("support-live-toggle")?.addEventListener("change", () => {
    startLive();
  });

  document.getElementById("auth-logout-btn")?.addEventListener("click", () => {
    window.AgentAuth?.logout(false);
  });

  async function boot() {
    await checkHealth();
    await loadOperations({ autoFollow: true });
    await loadSessions();
    startLive();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
