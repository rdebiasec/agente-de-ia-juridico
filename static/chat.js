const STORAGE_KEY = "agente-juridico-user-id";
const VALIDATION_STORAGE_KEY = "agente-juridico-validation-v2";

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
const validationScoreEl = document.getElementById("validation-score");
const validationScoreBarEl = document.getElementById("validation-score-bar");
const resetValidationBtn = document.getElementById("reset-validation-btn");
const probesSourceBadgeEl = document.getElementById("probes-source-badge");
const chatColumnEl = document.querySelector(".chat-column");

const validationState = loadValidationState();
let validationMarks = validationState.marks || {};
let dynamicProbes = validationState.probes || {};
let probesSource = validationState.probesSource || "default";
let activeBlockId = null;

function getUserId() {
  let id = localStorage.getItem(STORAGE_KEY);
  if (!id) {
    id = `web-${crypto.randomUUID().slice(0, 8)}`;
    localStorage.setItem(STORAGE_KEY, id);
  }
  return id;
}

function loadValidationState() {
  try {
    return JSON.parse(localStorage.getItem(VALIDATION_STORAGE_KEY) || "{}");
  } catch {
    return {};
  }
}

function saveValidationState() {
  localStorage.setItem(
    VALIDATION_STORAGE_KEY,
    JSON.stringify({
      marks: validationMarks,
      probes: dynamicProbes,
      probesSource,
      updated_at: new Date().toISOString(),
    })
  );
}

function updateProbesSourceBadge() {
  if (!probesSourceBadgeEl) return;
  probesSourceBadgeEl.classList.remove("is-llm", "is-loading");
  if (probesSource === "loading") {
    probesSourceBadgeEl.textContent = "Generando preguntas con IA…";
    probesSourceBadgeEl.classList.add("is-loading");
  } else if (probesSource === "llm") {
    probesSourceBadgeEl.textContent = "Preguntas dinámicas generadas por IA";
    probesSourceBadgeEl.classList.add("is-llm");
  } else if (probesSource === "fallback") {
    probesSourceBadgeEl.textContent = "Preguntas de respaldo (sin IA)";
  } else {
    probesSourceBadgeEl.textContent = "Preguntas de ejemplo — pulse Generar para variantes con IA";
  }
}

function getProbesForTest(test) {
  const probes = dynamicProbes[test.id]?.length
    ? dynamicProbes[test.id]
    : test.defaultProbes || [];
  return probes.slice(0, 2);
}

function initDefaultProbes() {
  VALIDATION_TESTS.forEach((test) => {
    if (!test.defaultProbes?.length) return;
    if (!dynamicProbes[test.id]?.length) {
      dynamicProbes[test.id] = test.defaultProbes.slice(0, 2);
    }
  });
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

function computeScore() {
  return VALIDATION_TESTS.reduce((sum, test) => {
    if (validationMarks[test.id] === "pass") {
      return sum + (test.weight || 0);
    }
    return sum;
  }, 0);
}

function updateBlockVisualState(blockId) {
  const blockEl = document.querySelector(`.validation-block[data-test-id="${blockId}"]`);
  if (!blockEl) return;

  const test = VALIDATION_TESTS.find((t) => t.id === blockId);
  const mark = validationMarks[blockId];
  blockEl.classList.remove("is-pass", "is-fail");
  if (mark === "pass") blockEl.classList.add("is-pass");
  if (mark === "fail") blockEl.classList.add("is-fail");

  const passBtn = blockEl.querySelector('[data-mark="pass"]');
  const failBtn = blockEl.querySelector('[data-mark="fail"]');
  if (passBtn) passBtn.classList.toggle("is-selected", mark === "pass");
  if (failBtn) failBtn.classList.toggle("is-selected", mark === "fail");

  const scoreTag = blockEl.querySelector(".block-score-tag");
  if (scoreTag && test) {
    if (mark === "pass") {
      scoreTag.textContent = `+${test.weight} pts`;
      scoreTag.className = "block-score-tag is-earned";
    } else if (mark === "fail") {
      scoreTag.textContent = "0 pts";
      scoreTag.className = "block-score-tag is-zero";
    } else {
      scoreTag.textContent = `${test.weight} pts posibles`;
      scoreTag.className = "block-score-tag";
    }
  }
}

function updateValidationProgress() {
  const score = computeScore();
  const total = VALIDATION_TOTAL_WEIGHT;
  const marked = VALIDATION_TESTS.filter((t) => validationMarks[t.id]).length;

  if (validationScoreEl) {
    validationScoreEl.textContent = `Puntaje: ${score} / ${total}`;
  }
  if (validationScoreBarEl) {
    validationScoreBarEl.style.width = `${Math.round((score / total) * 100)}%`;
    validationScoreBarEl.setAttribute("aria-valuenow", String(score));
  }
  if (validationProgressEl) {
    validationProgressEl.textContent = `${marked} de ${VALIDATION_TESTS.length} secciones marcadas`;
  }
}

function setValidationMark(blockId, mark) {
  validationMarks[blockId] = mark;
  saveValidationState();
  updateBlockVisualState(blockId);
  updateValidationProgress();
}

function buildProbeList(test) {
  const probeList = document.createElement("div");
  probeList.className = "probe-list";
  probeList.dataset.probeBlock = test.id;

  const probes = getProbesForTest(test);
  probes.forEach((probe, index) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "probe-btn";
    btn.innerHTML = `
      <span class="probe-message"></span>
      <span class="probe-send">Enviar al chat</span>
    `;
    btn.querySelector(".probe-message").textContent = probe.message || probe.label;
    btn.setAttribute("aria-label", `Pregunta ${index + 1}: ${probe.message || probe.label}`);
    btn.addEventListener("click", () => {
      setActiveBlock(test.id);
      scrollToChat();
      sendMessage(probe.message || probe.label);
    });
    probeList.appendChild(btn);
  });

  if (!probes.length) {
    const empty = document.createElement("p");
    empty.className = "probe-empty";
    empty.textContent = "Sin preguntas — pulse «Generar Nuevas Preguntas».";
    probeList.appendChild(empty);
  }

  return probeList;
}

function buildProbesSection(test) {
  const wrap = document.createElement("div");
  wrap.className = "probes-section";
  wrap.dataset.probeBlock = test.id;

  const header = document.createElement("div");
  header.className = "probes-section-header";

  const title = document.createElement("span");
  title.className = "probes-section-title";
  title.textContent = "Preguntas sugeridas (2)";

  const genBtn = document.createElement("button");
  genBtn.type = "button";
  genBtn.className = "btn-generate-inline";
  genBtn.dataset.blockId = test.id;
  genBtn.textContent = "Generar Nuevas Preguntas";
  genBtn.addEventListener("click", () => generateNewProbes({ blockId: test.id }));

  header.appendChild(title);
  header.appendChild(genBtn);
  wrap.appendChild(header);
  wrap.appendChild(buildProbeList(test));
  return wrap;
}

function refreshProbeListForBlock(blockId) {
  const test = VALIDATION_TESTS.find((t) => t.id === blockId);
  const blockEl = document.querySelector(`.validation-block[data-test-id="${blockId}"]`);
  if (!test || !blockEl) return;

  const oldSection = blockEl.querySelector(".probes-section");
  if (oldSection) {
    oldSection.replaceWith(buildProbesSection(test));
  }
}

function refreshAllProbeLists() {
  VALIDATION_TESTS.filter((t) => !t.connectionOnly).forEach((test) => {
    refreshProbeListForBlock(test.id);
  });
}

function renderScopeBlock() {
  const section = document.createElement("section");
  section.className = "validation-block validation-block--scope";
  section.innerHTML = `
    <h3>${VALIDATION_SCOPE.title}</h3>
    <ul>
      ${VALIDATION_SCOPE.items
        .map((item) => `<li><strong>${item.label}:</strong> ${item.text}</li>`)
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
  heading.innerHTML = `${index + 1}. ${test.title} <span class="block-weight">${test.weight} pts</span>`;
  if (test.reqTag) {
    const tag = document.createElement("span");
    tag.className = "req-tag";
    tag.textContent = test.reqTag;
    heading.appendChild(document.createTextNode(" "));
    heading.appendChild(tag);
  }
  section.appendChild(heading);

  const scoreTag = document.createElement("span");
  scoreTag.className = "block-score-tag";
  scoreTag.textContent = `${test.weight} pts posibles`;
  section.appendChild(scoreTag);

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

  if (!test.connectionOnly) {
    const probesDt = document.createElement("dt");
    probesDt.className = "probes-dt-sr";
    probesDt.textContent = "Preguntas sugeridas";
    const probesDd = document.createElement("dd");
    probesDd.className = "probes-dd";
    probesDd.appendChild(buildProbesSection(test));
    dl.appendChild(probesDt);
    dl.appendChild(probesDd);
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
        (item) => `<li><span class="check-box" aria-hidden="true"></span> ${item}</li>`
      ).join("")}
    </ul>
    <p class="validation-note">
      Puntaje máximo: ${VALIDATION_TOTAL_WEIGHT}/100. Si todas las secciones están aprobadas,
      Fase 0 puede considerarse validada. Si alguna falla, documente el caso y repórtelo al equipo técnico.
    </p>
  `;
  return section;
}

function renderValidationPanel() {
  if (!validationBlocksEl) return;

  validationBlocksEl.innerHTML = "";
  validationBlocksEl.appendChild(renderScopeBlock());

  VALIDATION_TESTS.forEach((test, index) => {
    validationBlocksEl.appendChild(renderTestBlock(test, index));
  });

  validationBlocksEl.appendChild(renderChecklistBlock());

  VALIDATION_TESTS.forEach((test) => updateBlockVisualState(test.id));
  updateValidationProgress();
}

async function generateNewProbes(options = {}) {
  const { silent = false, blockId = null } = options;
  const generatableIds = VALIDATION_TESTS.filter((t) => !t.connectionOnly).map((t) => t.id);
  const blocks = blockId ? [blockId] : generatableIds;

  const inlineButtons = blockId
    ? document.querySelectorAll(`.btn-generate-inline[data-block-id="${blockId}"]`)
    : document.querySelectorAll(".btn-generate-inline");

  inlineButtons.forEach((btn) => {
    btn.disabled = true;
    btn.dataset.prevText = btn.textContent;
    btn.textContent = "Generando…";
  });

  probesSource = "loading";
  updateProbesSourceBadge();

  try {
    const res = await fetch("/validation/generate-probes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: getUserId(),
        blocks,
        probes_per_block: 2,
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      if (!silent) {
        alert(err.detail || "No se pudieron generar preguntas. Intente en unos segundos.");
      }
      probesSource = Object.keys(dynamicProbes).length ? "fallback" : "default";
      updateProbesSourceBadge();
      return false;
    }

    const data = await res.json();
    Object.entries(data.blocks).forEach(([id, probes]) => {
      dynamicProbes[id] = probes.slice(0, 2);
    });
    probesSource = data.source === "llm" ? "llm" : "fallback";
    saveValidationState();

    if (blockId) {
      refreshProbeListForBlock(blockId);
    } else {
      refreshAllProbeLists();
    }
    updateProbesSourceBadge();
    return true;
  } catch {
    if (!silent) {
      alert("Error de conexión al generar preguntas.");
    }
    probesSource = "default";
    updateProbesSourceBadge();
    return false;
  } finally {
    inlineButtons.forEach((btn) => {
      btn.disabled = false;
      btn.textContent = btn.dataset.prevText || "Generar Nuevas Preguntas";
    });
  }
}

function resetValidation() {
  if (!confirm("¿Reiniciar marcas y puntaje? Las preguntas actuales se conservan.")) {
    return;
  }
  validationMarks = {};
  saveValidationState();
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

  resetValidationBtn?.addEventListener("click", resetValidation);
}

async function bootstrapValidationProbes() {
  updateProbesSourceBadge();
  if (probesSource === "llm" && Object.keys(dynamicProbes).length > 0) {
    refreshAllProbeLists();
    return;
  }
  const healthRes = await fetch("/health").catch(() => null);
  const health = healthRes ? await healthRes.json().catch(() => ({})) : {};
  if (health.openai_configured) {
    await generateNewProbes({ silent: true });
  }
}

initDefaultProbes();
renderValidationPanel();
renderSuggestions();
checkHealth();
initValidationPanel();
bootstrapValidationProbes();
inputEl.focus();
