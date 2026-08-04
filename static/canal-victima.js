/** Canal víctima — hilo vivo + escribir como la víctima (desk abogado). */
(() => {
  "use strict";

  const runtime = window.DeskRuntime || {};
  const POLL_MS = 4000;
  let pollTimer = null;
  let tabPoller = null;
  let lastPayload = null;

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function authFetch(url, options) {
    if (typeof window.authFetch === "function") return window.authFetch(url, options);
    return fetch(url, { credentials: "same-origin", ...options });
  }

  function sessionId() {
    if (runtime.getSessionId) return runtime.getSessionId();
    return window.Workspace?.getSessionId?.() || `web:${localStorage.getItem("agente-juridico-user-id") || "web"}`;
  }

  function notify(message, type = "info") {
    if (window.Toast?.show) {
      window.Toast.show(message, type);
      return;
    }
    if (window.showToast) {
      window.showToast(message, type);
    }
  }

  function isTabActive() {
    const panel = document.getElementById("tab-canal-victima");
    return panel && !panel.hidden && panel.classList.contains("is-active");
  }

  function badgeClass(badge) {
    switch (badge) {
      case "escrito_por_despacho":
        return "canal-badge canal-badge--despacho";
      case "borrador_pendiente":
        return "canal-badge canal-badge--pending";
      case "coordinador_enviado":
        return "canal-badge canal-badge--coord";
      case "victima":
      default:
        return "canal-badge canal-badge--victima";
    }
  }

  function renderThread(data) {
    const box = document.getElementById("canal-victima-thread");
    const meta = document.getElementById("canal-victima-meta");
    const link = document.getElementById("canal-victima-webchat-link");
    if (!box) return;

    const url = data.webchat_url || `/cliente?caso=${encodeURIComponent(sessionId())}`;
    if (link) {
      link.href = url;
    }
    if (meta) {
      const name = data.client_display_name || data.subject_label || "Sin nombre aún";
      const consent = data.consent_at
        ? ` · consentimiento ${String(data.consent_at).slice(0, 19)}`
        : data.started
          ? " · consulta iniciada"
          : " · pendiente de inicio en webchat";
      meta.textContent = `${name}${consent}`;
    }

    const messages = Array.isArray(data.messages) ? data.messages : [];
    if (!messages.length) {
      box.innerHTML =
        '<p class="canal-victima-empty">Aún no hay mensajes en el canal. Comparta el webchat o escriba como la víctima.</p>';
      return;
    }

    box.innerHTML = messages
      .map((m) => {
        const badge = m.badge_label || m.badge || m.role || "";
        const pendingNote =
          m.visibility === "pending_hitl" || m.badge === "borrador_pendiente"
            ? '<span class="canal-pending-note">borrador en revisión</span>'
            : "";
        const roleClass =
          m.role === "gerente"
            ? "canal-msg--gerente"
            : m.badge === "escrito_por_despacho"
              ? "canal-msg--despacho"
              : "canal-msg--cliente";
        return `<article class="canal-msg ${roleClass}">
          <span class="${badgeClass(m.badge)}">${esc(badge)}</span>
          ${pendingNote}
          <div class="canal-msg-body">${esc(m.content || "")}</div>
        </article>`;
      })
      .join("");
    box.scrollTop = box.scrollHeight;
  }

  async function refresh() {
    const sid = encodeURIComponent(sessionId());
    try {
      const res = await authFetch(`/abogado/cliente-thread?session_id=${sid}`);
      if (!res.ok) {
        const box = document.getElementById("canal-victima-thread");
        if (box && isTabActive()) {
          box.innerHTML = '<p class="canal-victima-empty">No se pudo cargar el canal víctima.</p>';
        }
        return;
      }
      lastPayload = await res.json();
      if (isTabActive()) renderThread(lastPayload);
    } catch {
      /* ignore poll errors */
    }
  }

  function startPoll() {
    if (tabPoller) {
      tabPoller.start({ immediate: true });
      return;
    }
    stopPoll();
    void refresh();
    pollTimer = setInterval(() => {
      if (isTabActive()) void refresh();
    }, POLL_MS);
  }

  function stopPoll() {
    if (tabPoller) {
      tabPoller.stop();
      return;
    }
    if (pollTimer) {
      clearInterval(pollTimer);
      pollTimer = null;
    }
  }

  async function sendAsClient(text) {
    const res = await authFetch("/abogado/cliente-as-client", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, session_id: sessionId() }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(data.detail || "No se pudo enviar como víctima.");
    }
    return data;
  }

  function init() {
    document.getElementById("btn-refresh-canal-victima")?.addEventListener("click", () => {
      void refresh();
    });

    document.getElementById("canal-victima-form")?.addEventListener("submit", async (event) => {
      event.preventDefault();
      const input = document.getElementById("canal-victima-input");
      const btn = document.getElementById("canal-victima-send");
      const text = (input?.value || "").trim();
      if (!text) return;
      if (btn) btn.disabled = true;
      try {
        await sendAsClient(text);
        if (input) input.value = "";
        await refresh();
        window.FirmaPanel?.loadClienteInbox?.();
      } catch (err) {
        notify(err?.message || "No se pudo registrar el mensaje en el canal víctima.", "error");
      } finally {
        if (btn) btn.disabled = false;
      }
    });

    document.addEventListener("workspace:tab", (ev) => {
      const tab = ev?.detail?.tab;
      if (tab === "canal-victima") startPoll();
      else stopPoll();
    });

    // Si la URL abre directo #canal-victima
    if (location.hash.replace("#", "") === "canal-victima") {
      startPoll();
    }
  }

  if (runtime.createTabPoller) {
    tabPoller = runtime.createTabPoller({
      tabId: "canal-victima",
      intervalMs: POLL_MS,
      run: async () => {
        await refresh();
      },
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  window.CanalVictima = { refresh, startPoll, stopPoll };
})();
