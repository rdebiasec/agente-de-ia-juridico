const STORAGE_KEY = "agente-juridico-user-id";

const suggestions = [
  "¿Qué áreas del derecho maneja el despacho?",
  "Quiero divorciarme por mutuo acuerdo",
  "¿Cuál es el perfil del asistente jurídico?",
  "Redacta un contrato de prestación de servicios",
];

const messagesEl = document.getElementById("messages");
const formEl = document.getElementById("chat-form");
const inputEl = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");
const suggestionsEl = document.getElementById("suggestions");
const statusDot = document.getElementById("status-dot");
const statusText = document.getElementById("status-text");

function getUserId() {
  let id = localStorage.getItem(STORAGE_KEY);
  if (!id) {
    id = `web-${crypto.randomUUID().slice(0, 8)}`;
    localStorage.setItem(STORAGE_KEY, id);
  }
  return id;
}

function formatText(text) {
  return text
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/\n/g, "<br>");
}

function scrollToBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function addMessage(role, text, meta = "") {
  const el = document.createElement("div");
  el.className = `message ${role}`;
  el.innerHTML = `
    ${meta ? `<span class="message-meta">${meta}</span>` : ""}
    <div class="message-body">${formatText(text)}</div>
  `;
  messagesEl.appendChild(el);
  scrollToBottom();
  return el;
}

function showTyping() {
  const el = document.createElement("div");
  el.className = "typing";
  el.id = "typing-indicator";
  el.innerHTML = "<span></span><span></span><span></span>";
  messagesEl.appendChild(el);
  scrollToBottom();
}

function hideTyping() {
  document.getElementById("typing-indicator")?.remove();
}

async function checkHealth() {
  try {
    const res = await fetch("/health");
    const data = await res.json();
    if (data.status === "ok" && data.openai_configured) {
      statusDot.classList.add("online");
      statusText.textContent = "Conectado · Fase 0 activa";
      return true;
    }
    statusText.textContent = "Servicio disponible · OpenAI no configurada";
    return false;
  } catch {
    statusText.textContent = "No se pudo conectar al servidor";
    return false;
  }
}

async function sendMessage(text) {
  const trimmed = text.trim();
  if (!trimmed) return;

  addMessage("user", trimmed, "Usted");
  inputEl.value = "";
  sendBtn.disabled = true;
  showTyping();

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: trimmed,
        channel: "web",
        user_id: getUserId(),
      }),
    });

    hideTyping();

    if (!res.ok) {
      addMessage(
        "assistant",
        "No pude procesar la consulta en este momento. Intente de nuevo en unos segundos.",
        "Asistente"
      );
      return;
    }

    const data = await res.json();
    addMessage("assistant", data.text, "Asistente jurídico");
  } catch {
    hideTyping();
    addMessage(
      "assistant",
      "Error de conexión. Verifique su red o espere si el servicio estaba inactivo.",
      "Asistente"
    );
  } finally {
    sendBtn.disabled = false;
    inputEl.focus();
  }
}

function renderSuggestions() {
  suggestions.forEach((text) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "chip";
    btn.textContent = text;
    btn.addEventListener("click", () => sendMessage(text));
    suggestionsEl.appendChild(btn);
  });
}

formEl.addEventListener("submit", (event) => {
  event.preventDefault();
  sendMessage(inputEl.value);
});

inputEl.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage(inputEl.value);
  }
});

addMessage(
  "assistant",
  "Bienvenida. Soy el asistente jurídico del despacho (Fase 0). Puedo orientarla sobre el perfil del despacho y las áreas del derecho en nuestra base de conocimiento.\n\n¿En qué puedo ayudarla hoy?",
  "Asistente jurídico"
);

function initValidationPanel() {
  const panel = document.getElementById("validation-panel");
  const toggle = document.getElementById("validation-toggle");
  if (!panel || !toggle) return;

  toggle.addEventListener("click", () => {
    const isOpen = panel.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", String(isOpen));
  });
}

renderSuggestions();
checkHealth();
initValidationPanel();
inputEl.focus();
