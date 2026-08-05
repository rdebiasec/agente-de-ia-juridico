/** Webchat consumidor — start 1581 + POST /cliente/chat + poll mensajes visibles. */
(function () {
  const STORAGE_SUBJECT = "lexiatek_cliente_subject";
  const STORAGE_LAWYER = "lexiatek_lawyer_session";
  const STORAGE_STARTED = "lexiatek_cliente_started_v1";

  const startEl = document.getElementById("cliente-start");
  const chatEl = document.getElementById("cliente-chat");
  const startForm = document.getElementById("cliente-start-form");
  const startBtn = document.getElementById("cliente-start-btn");
  const startError = document.getElementById("cliente-start-error");
  const nombreEl = document.getElementById("cliente-nombre");
  const telefonoEl = document.getElementById("cliente-telefono");
  const emailEl = document.getElementById("cliente-email");
  const consentStartEl = document.getElementById("cliente-consent-start");

  const messagesEl = document.getElementById("cliente-messages");
  const formEl = document.getElementById("cliente-form");
  const inputEl = document.getElementById("cliente-input");
  const sendBtn = document.getElementById("cliente-send");
  const statusEl = document.getElementById("cliente-status");
  const caseEl = document.getElementById("cliente-case-label");

  let pollTimer = null;

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function uuidLite() {
    if (crypto?.randomUUID) return crypto.randomUUID().slice(0, 12);
    return `c${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`;
  }

  function getSubject() {
    let sid = localStorage.getItem(STORAGE_SUBJECT);
    if (!sid) {
      sid = uuidLite();
      localStorage.setItem(STORAGE_SUBJECT, sid);
    }
    return sid;
  }

  function lawyerSession() {
    const params = new URLSearchParams(window.location.search);
    const fromQuery = (params.get("caso") || params.get("lawyer") || "").trim();
    if (fromQuery) {
      localStorage.setItem(STORAGE_LAWYER, fromQuery);
      return fromQuery;
    }
    return localStorage.getItem(STORAGE_LAWYER) || "web:abogado";
  }

  function shortCaseCode(lawyerSid) {
    const raw = String(lawyerSid || "").replace(/^web:/, "");
    const tail = raw.slice(-6).toUpperCase() || "LOCAL";
    return `CASO-${tail}`;
  }

  function updateCaseLabel(extraLabel) {
    if (!caseEl) return;
    const code = shortCaseCode(lawyerSession());
    const label = extraLabel ? `${extraLabel} · ${code}` : code;
    caseEl.hidden = false;
    caseEl.textContent = label;
  }

  function setStatus(text, mode) {
    if (!statusEl) return;
    statusEl.textContent = text;
    statusEl.classList.toggle("is-review", mode === "review");
    statusEl.classList.toggle("is-ok", mode === "ok");
  }

  function showStartError(msg) {
    if (!startError) return;
    startError.hidden = !msg;
    startError.textContent = msg || "";
  }

  function showChat() {
    if (startEl) {
      startEl.hidden = true;
      startEl.setAttribute("aria-hidden", "true");
    }
    if (chatEl) {
      chatEl.hidden = false;
      chatEl.setAttribute("aria-hidden", "false");
    }
    localStorage.setItem(STORAGE_STARTED, "1");
    document.querySelector(".skip-link")?.setAttribute("href", "#cliente-messages");
    ensurePoll();
  }

  function showStart() {
    if (startEl) {
      startEl.hidden = false;
      startEl.setAttribute("aria-hidden", "false");
    }
    if (chatEl) {
      chatEl.hidden = true;
      chatEl.setAttribute("aria-hidden", "true");
    }
    localStorage.removeItem(STORAGE_STARTED);
  }

  function ensurePoll() {
    if (pollTimer) return;
    pollTimer = setInterval(() => {
      if (chatEl && !chatEl.hidden) void refreshMessages();
    }, 8000);
  }

  function renderMessages(messages) {
    if (!messagesEl) return;
    if (!messages.length) {
      messagesEl.innerHTML =
        '<p class="cliente-empty">Aún no hay mensajes. Escriba su consulta abajo.</p>';
      return;
    }
    messagesEl.innerHTML = messages
      .map((m) => {
        const role = m.role === "gerente" ? "gerente" : "cliente";
        const label = role === "gerente" ? "Coordinador del Caso" : "Usted";
        return `<article class="cliente-msg cliente-msg--${role}">
          <span class="cliente-msg-meta">${escapeHtml(label)}</span>
          ${escapeHtml(m.content || "")}
        </article>`;
      })
      .join("");
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  async function refreshMessages() {
    const subject = encodeURIComponent(getSubject());
    const res = await fetch(`/cliente/messages?cliente_session_id=${subject}`, {
      credentials: "same-origin",
    });
    if (!res.ok) return;
    const data = await res.json();
    if (!data.started) {
      showStart();
      return;
    }
    showChat();
    renderMessages(Array.isArray(data.messages) ? data.messages : []);
    updateCaseLabel(data.client_display_name || data.subject_label || "");
    const label = data.status_label;
    if (data.status === "en_revision") {
      setStatus(
        label || "El despacho está preparando su orientación jurídica.",
        "review"
      );
    } else if (data.status === "en_dialogo") {
      setStatus(
        label ||
          "Sigamos la conversación abajo. El abogado valida la orientación jurídica en paralelo.",
        "ok"
      );
    } else if (data.status === "respuesta_lista") {
      setStatus(label || "Puede seguir escribiendo; estoy aquí para ayudarle.", "ok");
    } else {
      setStatus(
        label || "Cuéntenos su situación. Le responderé de inmediato para armar el caso.",
        "ok"
      );
    }
  }

  async function startConsultation() {
    const nombre = (nombreEl?.value || "").trim();
    const consent = !!consentStartEl?.checked;
    if (!nombre || !consent) {
      showStartError("Indique su nombre y autorice el tratamiento de datos (Ley 1581).");
      return;
    }
    showStartError("");
    if (startBtn) startBtn.disabled = true;
    try {
      const res = await fetch("/cliente/start", {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          nombre,
          telefono: (telefonoEl?.value || "").trim() || null,
          email: (emailEl?.value || "").trim() || null,
          consent_1581: true,
          cliente_session_id: getSubject(),
          lawyer_session_id: lawyerSession(),
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        const detail = data.detail;
        const msg =
          typeof detail === "string"
            ? detail
            : Array.isArray(detail)
              ? detail.map((d) => d.msg || d).join("; ")
              : "No se pudo iniciar la consulta.";
        throw new Error(msg);
      }
      if (data.cliente_session_id) {
        const bare = String(data.cliente_session_id).replace(/^cliente:/, "");
        localStorage.setItem(STORAGE_SUBJECT, bare);
      }
      showChat();
      updateCaseLabel(data.client_display_name || nombre);
      setStatus("Consulta iniciada. Cuéntenos su situación; el abogado revisará la respuesta.", "ok");
      await refreshMessages();
      inputEl?.focus();
    } catch (err) {
      showStartError(err?.message || "Error al iniciar.");
    } finally {
      if (startBtn) startBtn.disabled = false;
    }
  }

  async function sendMessage(text) {
    const res = await fetch("/cliente/chat", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        cliente_session_id: getSubject(),
        lawyer_session_id: lawyerSession(),
      }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(data.detail || "No se pudo enviar el mensaje.");
    }
    return data;
  }

  startForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    await startConsultation();
  });

  formEl?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const text = (inputEl?.value || "").trim();
    if (!text) return;
    sendBtn.disabled = true;
    setStatus("Enviando…", "review");
    try {
      const out = await sendMessage(text);
      inputEl.value = "";
      setStatus(
        out.status_label ||
          out.client_ack ||
          "Le respondí abajo. Sigamos armando su caso.",
        out.status === "en_dialogo" || out.status === "respuesta_lista" ? "ok" : "review"
      );
      await refreshMessages();
    } catch (err) {
      setStatus(err?.message || "Error al enviar.", "review");
    } finally {
      sendBtn.disabled = false;
      inputEl?.focus();
    }
  });

  async function boot() {
    lawyerSession();
    try {
      const res = await fetch("/cliente/session", { credentials: "same-origin" });
      if (res.ok) {
        const info = await res.json();
        if (info.cliente_subject) {
          localStorage.setItem(STORAGE_SUBJECT, info.cliente_subject);
        }
        if (info.started) {
          showChat();
          await refreshMessages();
          return;
        }
      }
    } catch {
      /* show start */
    }
    showStart();
  }

  void boot();
})();
