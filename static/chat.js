const STORAGE_KEY = "agente-juridico-user-id";
const VALIDATION_STORAGE_KEY = "agente-juridico-validation";

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
const validationBlocksEl = document.getElementById("validation-blocks");
const validationProgressEl = document.getElementById("validation-progress");
const chatColumnEl = document.querySelector(".chat-column");

let validationMarks = loadValidationMarks();
let activeBlockId = null;

function getUserId() {
  let id = localStorage.getItem(STORAGE_KEY);
  if (!id) {
    id = `web-${crypto.randomUUID().slice(0, 8)}`;
    localStorage.setItem(STORAGE_KEY, id);
  }
  return id;
}

function loadValidationMarks() {
  try {
    return JSON.parse(localStorage.getItem(VALIDATION_STORAGE_KEY) || "{}");
  } catch {
    return {};
  }
}

function saveValidationMarks() {
  localStorage.setItem(VALIDATION_STORAGE_KEY, JSON.stringify(validationMarks));
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

function scrollToChat() {
  if (window.matchMedia("(max-width: 1024px)").matches && chatColumnEl) {
    chatColumnEl.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

function setActiveBlock(blockId) {
  activeBlockId = blockId;
  document.querySelectorAll(".validation-block[data-test-id]").forEach((el) => {
    el.classList.toggle("is-active", el.dataset.testId === blockId);
  });
}

function updateBlockVisualState(blockId) {
  const blockEl = document.querySelector(`.validation-block[data-test-id="${blockId}"]`);
  if (!blockEl) return;

  const mark = validationMarks[blockId];
  blockEl.classList.remove("is-pass", "is-fail");
  if (mark === "pass") blockEl.classList.add("is-pass");
  if (mark === "fail") blockEl.classList.add("is-fail");

  const passBtn = blockEl.querySelector('[data-mark="pass"]');
  const failBtn = blockEl.querySelector('[data-mark="fail"]');
  if (passBtn) passBtn.classList.toggle("is-selected", mark === "pass");
  if (failBtn) failBtn.classList.toggle("is-selected", mark === "fail");
}

function updateValidationProgress() {
  if (!validationProgressEl) return;

  const testable = VALIDATION_TESTS.filter((t) => !t.connectionOnly);
  const marked = testable.filter((t) => validationMarks[t.id]).length;
  validationProgressEl.textContent = `${marked} de ${testable.length} pruebas marcadas`;
}

function setValidationMark(blockId, mark) {
  validationMarks[blockId] = mark;
  saveValidationMarks();
  updateBlockVisualState(blockId);
  updateValidationProgress();
}

function renderScopeBlock() {
  const section = document.createElement("section");
  section.className = "validation-block validation-block--scope";
  section.innerHTML = `
    <h3>${VALIDATION_SCOPE.title}</h3>
    <ul>
      ${VALIDATION_SCOPE.items
        .map(
          (item) =>
            `<li><strong>${item.label}:</strong> ${item.text}</li>`
        )
        .join("")}
    </ul>
  `;
  return section;
}

function renderTestBlock(test, index) {
  const section = document.createElement("section");
  section.className = "validation-block";
  section.dataset.testId = test.id;

  const heading = document.createElement("h3");
  heading.textContent = `${index + 1}. ${test.title}`;
  if (test.reqTag) {
    const tag = document.createElement("span");
    tag.className = "req-tag";
    tag.textContent = test.reqTag;
    heading.appendChild(document.createTextNode(" "));
    heading.appendChild(tag);
  }
  section.appendChild(heading);

  const dl = document.createElement("dl");
  dl.className = "test-item";

  const addRow = (label, contentNode) => {
    const dt = document.createElement("dt");
    dt.textContent = label;
    const dd = document.createElement("dd");
    if (typeof contentNode === "string") {
      dd.textContent = contentNode;
    } else {
      dd.appendChild(contentNode);
    }
    dl.appendChild(dt);
    dl.appendChild(dd);
  };

  addRow("Qué hacer", test.instructions);

  if (test.probes.length > 0) {
    const probeList = document.createElement("div");
    probeList.className = "probe-list";
    test.probes.forEach((probe) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "probe-btn";
      btn.dataset.blockId = test.id;
      btn.innerHTML = `
        <span class="probe-label">Enviar al chat</span>
        <span class="probe-text"></span>
      `;
      btn.querySelector(".probe-text").textContent = probe.label;
      btn.addEventListener("click", () => {
        setActiveBlock(test.id);
        scrollToChat();
        sendMessage(probe.message);
      });
      probeList.appendChild(btn);
    });
    addRow("Preguntas sugeridas", probeList);
  }

  if (test.connectionOnly) {
    const status = document.createElement("p");
    status.className = "connection-status";
    status.id = "connection-status";
    status.textContent = "Verificando conexión…";
    addRow("Estado", status);
  }

  addRow("Qué esperar", test.expect);

  const passDd = document.createElement("dd");
  passDd.className = "criteria pass";
  passDd.textContent = test.passCriteria;
  dl.appendChild(Object.assign(document.createElement("dt"), { textContent: "Aprobada si" }));
  dl.appendChild(passDd);

  const failDd = document.createElement("dd");
  failDd.className = "criteria fail";
  failDd.textContent = test.failCriteria;
  dl.appendChild(Object.assign(document.createElement("dt"), { textContent: "Rechazada si" }));
  dl.appendChild(failDd);

  section.appendChild(dl);

  const markActions = document.createElement("div");
  markActions.className = "mark-actions";
  ["pass", "fail"].forEach((mark) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = `mark-btn mark-btn--${mark}`;
    btn.dataset.mark = mark;
    btn.dataset.blockId = test.id;
    btn.textContent = mark === "pass" ? "Aprobada" : "Rechazada";
    btn.addEventListener("click", () => setValidationMark(test.id, mark));
    markActions.appendChild(btn);
  });
  section.appendChild(markActions);

  return section;
}

function renderChecklistBlock() {
  const section = document.createElement("section");
  section.className = "validation-block validation-checklist";
  section.innerHTML = `
    <h3>Checklist final para la abogada</h3>
    <ul class="checklist">
      ${VALIDATION_CHECKLIST.map(
        (item) =>
          `<li><span class="check-box" aria-hidden="true"></span> ${item}</li>`
      ).join("")}
    </ul>
    <p class="validation-note">
      Si todas las pruebas están aprobadas, Fase 0 puede considerarse validada para
      continuar con Fase 1. Si alguna falla, documente el caso y repórtelo al equipo técnico.
    </p>
  `;
  return section;
}

function renderValidationPanel() {
  if (!validationBlocksEl) return;

  validationBlocksEl.appendChild(renderScopeBlock());

  VALIDATION_TESTS.forEach((test, index) => {
    validationBlocksEl.appendChild(renderTestBlock(test, index));
  });

  validationBlocksEl.appendChild(renderChecklistBlock());

  VALIDATION_TESTS.forEach((test) => updateBlockVisualState(test.id));
  updateValidationProgress();
}

function updateConnectionStatus(connected) {
  const el = document.getElementById("connection-status");
  if (!el) return;
  el.textContent = connected
    ? "Estado actual: Conectado · Fase 0 activa"
    : "Estado actual: sin conexión o Fase 0 no confirmada";
  el.classList.toggle("is-ok", connected);
}

async function checkHealth() {
  try {
    const res = await fetch("/health");
    const data = await res.json();
    const connected = data.status === "ok" && data.fase_activa === 0;
    if (data.status === "ok" && data.openai_configured) {
      statusDot.classList.add("online");
      statusText.textContent = "Conectado · Fase 0 activa";
    } else {
      statusText.textContent = "Servicio disponible · OpenAI no configurada";
    }
    updateConnectionStatus(connected && data.openai_configured);
    return connected;
  } catch {
    statusText.textContent = "No se pudo conectar al servidor";
    updateConnectionStatus(false);
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

renderValidationPanel();
renderSuggestions();
checkHealth();
initValidationPanel();
inputEl.focus();
