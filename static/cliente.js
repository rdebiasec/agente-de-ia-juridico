/** Front-office víctima — POST /cliente/chat + poll mensajes visibles. */
(function () {
  const STORAGE_SUBJECT = "lexiatek_cliente_subject";
  const STORAGE_CONSENT = "lexiatek_cliente_consent_v1";
  const STORAGE_LAWYER = "lexiatek_lawyer_session";
  const STORAGE_PIN = "lexiatek_cliente_pin";

  const messagesEl = document.getElementById("cliente-messages");
  const formEl = document.getElementById("cliente-form");
  const inputEl = document.getElementById("cliente-input");
  const sendBtn = document.getElementById("cliente-send");
  const consentEl = document.getElementById("cliente-consent");
  const statusEl = document.getElementById("cliente-status");
  const caseEl = document.getElementById("cliente-case-label");

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

  function getOrCreatePin() {
    let pin = localStorage.getItem(STORAGE_PIN);
    if (!pin) {
      pin = String(100000 + Math.floor(Math.random() * 900000));
      localStorage.setItem(STORAGE_PIN, pin);
    }
    return pin;
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
    const pin = getOrCreatePin();
    const label = extraLabel ? `${extraLabel} · ${code}` : code;
    caseEl.hidden = false;
    caseEl.textContent = `${label} · clave local ${pin}`;
  }

  function setStatus(text, mode) {
    if (!statusEl) return;
    statusEl.textContent = text;
    statusEl.classList.toggle("is-review", mode === "review");
    statusEl.classList.toggle("is-ok", mode === "ok");
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
    renderMessages(Array.isArray(data.messages) ? data.messages : []);
    updateCaseLabel(data.subject_label || "");
    const label = data.status_label;
    if (data.status === "en_revision") {
      setStatus(label || "Su mensaje está en revisión del despacho.", "review");
    } else if (data.status === "respuesta_lista") {
      setStatus(label || "Hay respuesta del Coordinador del Caso para usted.", "ok");
    } else {
      setStatus(
        label || "Escriba su mensaje. El despacho revisará la respuesta antes de enviársela.",
        "ok"
      );
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

  function initConsent() {
    if (!consentEl) return;
    if (localStorage.getItem(STORAGE_CONSENT) === "1") {
      consentEl.checked = true;
    }
    consentEl.addEventListener("change", () => {
      if (consentEl.checked) localStorage.setItem(STORAGE_CONSENT, "1");
      else localStorage.removeItem(STORAGE_CONSENT);
    });
  }

  formEl?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const text = (inputEl?.value || "").trim();
    if (!text || !consentEl?.checked) return;
    sendBtn.disabled = true;
    setStatus("Enviando…", "review");
    try {
      const out = await sendMessage(text);
      inputEl.value = "";
      setStatus(
        out.status_label || out.client_ack || "Mensaje recibido. En revisión del despacho.",
        "review"
      );
      await refreshMessages();
    } catch (err) {
      setStatus(err?.message || "Error al enviar.", "review");
    } finally {
      sendBtn.disabled = false;
      inputEl?.focus();
    }
  });

  initConsent();
  updateCaseLabel("");
  void refreshMessages();
  setInterval(() => {
    void refreshMessages();
  }, 8000);
})();
