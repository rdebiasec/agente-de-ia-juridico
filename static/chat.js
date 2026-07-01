const STORAGE_KEY = "agente-juridico-user-id";
const SESSION_STORAGE_KEY = "agente-juridico-session-v4";
const LEGACY_V3_KEY = "agente-juridico-session-v3";
const LEGACY_STORAGE_KEY = "agente-juridico-validation-v2";
const ONBOARDING_KEY = "agente-juridico-onboarding-seen";
const ENABLE_SERVER_RUBRIC = true;

const WELCOME_MESSAGE =
  "Bienvenida. Soy el asistente jurídico del despacho. Puedo apoyarla en intake, estrategia, redacción de documentos, conceptos, tutelas y seguimiento de procesos civiles y penales.\n\n¿En qué puedo ayudarla hoy?";

const messagesEl = document.getElementById("messages");
const formEl = document.getElementById("chat-form");
const inputEl = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");
const statusDot = document.getElementById("status-dot");
const statusText = document.getElementById("status-text");
const validationBlocksEl = document.getElementById("validation-blocks");
const validationProgressEl = document.getElementById("validation-progress");
const validationScoreEl = document.getElementById("validation-score");
const validationScoreBarEl = document.getElementById("validation-score-bar");
const resetScoreBtn = document.getElementById("reset-score-btn");
const resetChatBtn = document.getElementById("reset-chat-btn");
const validationStepperEl = document.getElementById("validation-stepper");
const filterPendingEl = document.getElementById("filter-pending-only");
const probesSourceBadgeEl = document.getElementById("probes-source-badge");
const chatColumnEl = document.querySelector(".chat-column");
const traceBodyEl = document.getElementById("trace-body");
const chatFileInputEl = document.getElementById("chat-file-input");
const composerAttachStatusEl = document.getElementById("composer-attach-status");

const sessionState = loadSessionState();
let sessionId = sessionState.sessionId;
let startedAt = sessionState.startedAt;
let lastActivityAt = sessionState.lastActivityAt;
let validationMarks = sessionState.marks || {};
let dynamicProbes = sessionState.probes || {};
let probesSource = sessionState.probesSource || "default";
let checklistChecked = normalizeChecklistChecked(sessionState.checklistChecked);
let chatLog = Array.isArray(sessionState.chatLog) ? sessionState.chatLog : [];
let events = Array.isArray(sessionState.events) ? sessionState.events : [];
let markNotes = sessionState.markNotes || {};
let lastReport = sessionState.lastReport || null;
let activeBlockId = null;
let pendingChatMeta = null;
let sendViaOverride = null;
let filterPendingOnly = false;
let selectedTraceMsgId = sessionState.selectedTraceMsgId || null;
/** Bumped on reset so in-flight /chat responses cannot repopulate the UI. */
let chatEpoch = 0;

function normalizeChecklistChecked(raw) {
  if (!raw || typeof raw !== "object") return {};
  return Object.fromEntries(
    Object.entries(raw).map(([key, value]) => [Number(key), Boolean(value)])
  );
}

function createSessionId() {
  return `sess-${crypto.randomUUID().slice(0, 12)}`;
}

function migrateFromV3() {
  try {
    const raw = localStorage.getItem(LEGACY_V3_KEY);
    if (!raw) return null;
    const v3 = JSON.parse(raw);
    localStorage.removeItem(LEGACY_V3_KEY);
    const migrated = {
      ...v3,
      markNotes: v3.markNotes || {},
      schemaVersion: 4,
    };
    if (migrated.lastReport?.metrics) {
      migrated.lastReport = SessionReport?.normalizeBackendReport?.(migrated.lastReport, migrated) || null;
    }
    return migrated;
  } catch {
    return null;
  }
}

function migrateFromLegacy() {
  try {
    const raw = localStorage.getItem(LEGACY_STORAGE_KEY);
    if (!raw) return null;
    const v2 = JSON.parse(raw);
    localStorage.removeItem(LEGACY_STORAGE_KEY);
    return {
      sessionId: createSessionId(),
      startedAt: v2.updated_at || new Date().toISOString(),
      lastActivityAt: v2.updated_at || new Date().toISOString(),
      marks: v2.marks || {},
      probes: v2.probes || {},
      probesSource: v2.probesSource || "default",
      checklistChecked: v2.checklistChecked || {},
      chatLog: [],
      events: [{ type: "session_start", ts: new Date().toISOString(), reason: "migration_v2" }],
      markNotes: {},
      lastReport: null,
      schemaVersion: 4,
    };
  } catch {
    return null;
  }
}

function loadSessionState() {
  try {
    const raw = localStorage.getItem(SESSION_STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      return { markNotes: {}, schemaVersion: 4, ...parsed };
    }
  } catch {
    /* ignore */
  }
  const fromV3 = migrateFromV3();
  if (fromV3) {
    localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(fromV3));
    return fromV3;
  }
  const migrated = migrateFromLegacy();
  if (migrated) {
    localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(migrated));
    return migrated;
  }
  const now = new Date().toISOString();
  return {
    sessionId: createSessionId(),
    startedAt: now,
    lastActivityAt: now,
    marks: {},
    probes: {},
    probesSource: "default",
    checklistChecked: {},
    chatLog: [],
    events: [{ type: "session_start", ts: now }],
    markNotes: {},
    lastReport: null,
    schemaVersion: 4,
  };
}

function getSessionSnapshot() {
  return {
    sessionId,
    startedAt,
    lastActivityAt,
    marks: { ...validationMarks },
    markNotes: { ...markNotes },
    probes: { ...dynamicProbes },
    probesSource,
    checklistChecked: { ...checklistChecked },
    chatLog: chatLog.slice(),
    events: events.slice(),
    lastReport,
    selectedTraceMsgId,
  };
}

function touchActivity() {
  lastActivityAt = new Date().toISOString();
}

function saveSessionState() {
  touchActivity();
  localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(getSessionSnapshot()));
  SessionReport?.refresh?.();
}

function recordEvent(event) {
  events.push({ ...event, ts: event.ts || new Date().toISOString() });
  if (events.length > 200) events = events.slice(-200);
  saveSessionState();
}

function appendChatLogEntry(entry) {
  const record = {
    id: `msg-${crypto.randomUUID().slice(0, 10)}`,
    ts: new Date().toISOString(),
    ...entry,
  };
  chatLog.push(record);
  if (chatLog.length > 500) chatLog = chatLog.slice(-500);
  saveSessionState();
  return record;
}

function getUserId() {
  let id = localStorage.getItem(STORAGE_KEY);
  if (!id) {
    id = `web-${crypto.randomUUID().slice(0, 8)}`;
    localStorage.setItem(STORAGE_KEY, id);
  }
  return id;
}

window.getChatUserId = getUserId;

function getWebSessionId() {
  return `web:${getUserId()}`;
}

function normalizeHistoryText(role, content) {
  const raw = String(content ?? "");
  if (role !== "assistant") {
    return stripInjectedContext(raw);
  }
  const trimmed = raw.trim();
  if (trimmed.startsWith("{") && trimmed.includes("text")) {
    try {
      const parsed = JSON.parse(trimmed.replace(/'/g, '"'));
      if (parsed && typeof parsed.text === "string") return parsed.text;
    } catch {
      /* legacy Python dict — handled below */
    }
    const m = trimmed.match(/['"]text['"]:\s*['"]((?:\\.|[^'\\])*)['"]/);
    if (m) {
      try {
        return JSON.parse(`"${m[1]}"`);
      } catch {
        return m[1].replace(/\\n/g, "\n");
      }
    }
  }
  return raw;
}

function stripInjectedContext(text) {
  const raw = String(text ?? "").trim();
  if (
    raw.includes("[Base de conocimiento") ||
    raw.includes("[Expediente del caso]") ||
    (raw.match(/## Etapas/g) || []).length >= 2 ||
    raw.includes("[Fuente 1:")
  ) {
    const parts = raw.split(/\n\n+/).map((p) => p.trim()).filter(Boolean);
    for (let i = parts.length - 1; i >= 0; i -= 1) {
      const p = parts[i];
      if (p.startsWith("[") || p.startsWith("[Fuente")) continue;
      if (p.startsWith("##") && p.length > 160) continue;
      return p;
    }
  }
  const parts = raw.split(/\n\n+/).map((p) => p.trim()).filter((p) => p && !p.startsWith("["));
  return parts.length ? parts.join("\n\n") : raw;
}

async function loadServerHistory() {
  try {
    const res = await authFetch(`/chat/history?user_id=${encodeURIComponent(getUserId())}`);
    if (!res.ok) return false;
    const data = await res.json();
    if (data.expediente && window.Workspace?.setExpediente) {
      window.Workspace.setExpediente(data.expediente);
    }
    if (Array.isArray(data.messages) && data.messages.length) {
      chatLog = data.messages.map((m, i) => {
        const role = m.role === "assistant" ? "assistant" : "user";
        return {
          id: `srv-${i}-${m.ts || i}`,
          role,
          text: normalizeHistoryText(role, m.content || ""),
          ts: m.ts ? new Date(Number(m.ts) * 1000).toISOString() : new Date().toISOString(),
        };
      });
      saveSessionState();
      return true;
    }
  } catch {
    /* fallback a localStorage */
  }
  return false;
}

async function uploadChatAttachment(file) {
  if (!file) return;
  const sid = getWebSessionId();
  const fd = new FormData();
  fd.append("file", file);
  fd.append("expediente_id", sid);
  fd.append("ingestar", "true");
  if (composerAttachStatusEl) {
    composerAttachStatusEl.hidden = false;
    composerAttachStatusEl.textContent = `Subiendo ${file.name}…`;
    composerAttachStatusEl.className = "composer-attach-status composer-attach-status--loading";
  }
  try {
    const res = await authFetch("/documents/extract", { method: "POST", body: fd });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "No se pudo subir el archivo.");
    if (composerAttachStatusEl) {
      composerAttachStatusEl.textContent = `${file.name} indexado (${data.fragmentos_indexados || 0} fragmentos).`;
      composerAttachStatusEl.className = "composer-attach-status composer-attach-status--ok";
    }
    window.Workspace?.addHito?.(`Documento adjunto: ${file.name}`);
    Toast?.show?.("Documento indexado al expediente.", "success");
  } catch (err) {
    if (composerAttachStatusEl) {
      composerAttachStatusEl.textContent = err?.message || "Error al subir el archivo.";
      composerAttachStatusEl.className = "composer-attach-status composer-attach-status--error";
    }
    Toast?.show?.(err?.message || "No se pudo subir el archivo.", "error");
  }
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
  if (typeof VALIDATION_TESTS === "undefined") return;
  VALIDATION_TESTS.forEach((test) => {
    if (!test.defaultProbes?.length) return;
    if (!dynamicProbes[test.id]?.length) {
      dynamicProbes[test.id] = test.defaultProbes.slice(0, 2);
    }
  });
}

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function formatText(text) {
  const safe = escapeHtml(text);
  return safe
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/\n/g, "<br>");
}

function getBlockTitle(blockId) {
  if (!blockId) return "";
  const test = VALIDATION_TESTS.find((t) => t.id === blockId);
  return test?.title || blockId;
}

function buildMessageMeta(role, options = {}) {
  const { blockId, via, latencyMs, agent } = options;
  const parts = [];
  if (role === "user") parts.push("Usted");
  else if (role === "assistant") parts.push("Asistente jurídico");

  if (blockId) {
    const title = getBlockTitle(blockId);
    parts.push(`<button type="button" class="message-block-badge" data-block-id="${escapeHtml(blockId)}">${escapeHtml(title)}</button>`);
  }
  if (via === "probe") parts.push('<span class="message-via-badge">probe</span>');
  if (role === "assistant" && agent) {
    const route = formatAgentRoute(agent);
    if (route) parts.push(`<span class="message-agent-route">${escapeHtml(route)}</span>`);
  }
  if (role === "assistant" && typeof latencyMs === "number") {
    parts.push(`<span class="message-latency">${latencyMs} ms</span>`);
  }
  return parts.join(" · ");
}

const AGENT_ROUTE_LABELS = {
  agente_coordinador_principal: "Coordinador principal",
  agente_conocimiento_derecho: "Conocimiento del derecho",
  agente_recepcionista: "Recepcionista",
  agente_estrategia_casos: "Estrategia de casos",
  agente_servicio_cliente: "Servicio al cliente",
  agente_redaccion_documental: "Redacción documental",
  agente_conceptos_juridicos: "Conceptos jurídicos",
  agente_tutela_constitucional: "Tutela constitucional",
  agente_seguimiento_procesal: "Seguimiento procesal",
  agente_coordinador_penal: "Coordinador penal (víctima)",
  subagente_investigacion_victima: "Penal — Investigación víctima",
  subagente_penal_garantias: "Penal — Garantías",
  subagente_penal_juicios: "Penal — Juicios",
  subagente_penal_pruebas: "Penal — Pruebas",
  subagente_penal_reparacion: "Penal — Reparación",
  subagente_penal_negociacion: "Penal — Negociación",
  subagente_penal_recursos: "Penal — Recursos",
  agente_coordinador_civil: "Coordinador civil (CGP)",
  agente_civil_demanda: "Civil — Demanda",
  agente_civil_contestacion: "Civil — Contestación",
  agente_civil_audiencia_inicial: "Civil — Audiencia inicial (372)",
  agente_civil_instruccion: "Civil — Instrucción (373)",
  agente_civil_prueba: "Civil — Prueba",
  agente_civil_recursos: "Civil — Recursos",
  agente_civil_ejecucion: "Civil — Ejecución",
  fallback: "Modo respaldo",
  guardrail: "Bloqueo de seguridad",
  error: "Ruta de error controlado",
  // históricos
  orquestador: "Coordinador principal",
  socio_coordinador: "Coordinador principal",
  conocimiento_areas: "Conocimiento del derecho",
  areas_derecho: "Conocimiento del derecho",
  intake: "Recepcionista",
  recepcion_casos: "Recepción de casos",
  estratega: "Estrategia de casos",
  estrategia_caso: "Estrategia de casos",
  comunicacion_clientes: "Servicio al cliente",
  atencion_cliente: "Servicio al cliente",
  redaccion_escritos: "Redacción documental",
  redaccion_documental: "Redacción documental",
  conceptos: "Conceptos jurídicos",
  conceptos_juridicos: "Conceptos jurídicos",
  tutela: "Tutela constitucional",
  tutela_constitucional: "Tutela constitucional",
  dependiente_judicial: "Seguimiento procesal",
  seguimiento_procesal: "Seguimiento procesal",
  coordinador_penal: "Coordinador penal (víctima)",
  penal_fiscalia: "Penal — Investigación víctima",
  penal_garantias: "Penal — Garantías",
  penal_juicio: "Penal — Juicios",
  penal_prueba: "Penal — Pruebas",
  penal_reparacion: "Penal — Reparación",
  penal_negociacion: "Penal — Negociación",
  penal_recursos: "Penal — Recursos",
  coordinador_civil: "Coordinador civil (CGP)",
  litigante_civil: "Coordinador civil (CGP)",
  civil_demanda: "Civil — Demanda",
  civil_contestacion: "Civil — Contestación",
  civil_audiencia_inicial: "Civil — Audiencia inicial (372)",
  civil_instruccion: "Civil — Instrucción (373)",
  civil_prueba: "Civil — Prueba",
  civil_recursos: "Civil — Recursos",
  civil_ejecucion: "Civil — Ejecución",
  litigante_orquestador_penal: "Coordinador penal (víctima)",
  litigante_investigacion_victima: "Penal — Investigación víctima",
  litigante_garantias: "Penal — Garantías",
  litigante_conocimiento: "Penal — Juicios",
  litigante_prueba: "Penal — Pruebas",
  litigante_reparacion_integral: "Penal — Reparación",
  litigante_negociacion_victima: "Penal — Negociación",
  litigante_recursos_penales: "Penal — Recursos",
};

function formatAgentRoute(agent) {
  if (!agent) return "";
  return AGENT_ROUTE_LABELS[agent] || agent;
}

function inferTrace(options = {}, text = "") {
  const blocked = /(no está activa|no esta activa|no puedo|no tengo la habilidad)/i.test(text || "");
  const disclaimer = /borrador informativo/i.test(text || "");
  const route = options.agent ? formatAgentRoute(options.agent) : "Ruta no reportada";
  const needsReview = Boolean(options.pendingReview);
  return {
    trace_version: "2.0",
    trace_id: "local-inferido",
    session_id: null,
    route: options.agent || "unknown",
    received_by_agent: "agente_coordinador_principal",
    sent_to_agent: options.agent || "none",
    skill_kan: "KAN-N/A",
    skill_reason: "Inferido localmente por falta de metadata backend.",
    selected_agent: options.agent || "",
    blocked,
    human_review_required: needsReview,
    completion: {
      available: false,
      provider: "openai-responses",
      calls: [],
      summary: { calls: 0, input_tokens: 0, output_tokens: 0, total_tokens: 0 },
      note: "Sin completion backend reportado.",
    },
    conversation_continues: false,
    turn_index: 0,
    spans: [],
    actions: [],
    steps: [
      { step: "Recibí su consulta", status: "done", detail: "Consulta recibida por el asistente." },
      {
        step: "Validé alcance de fase",
        status: blocked ? "blocked" : "done",
        detail: blocked
          ? "La solicitud corresponde a una fase posterior y se bloqueó."
          : "La solicitud está dentro del alcance de la fase activa.",
      },
      {
        step: "Enruté al flujo de respuesta",
        status: "done",
        detail: route,
      },
      {
        step: "Apliqué aviso legal",
        status: disclaimer ? "done" : "blocked",
        detail: disclaimer
          ? "Respuesta marcada como borrador informativo."
          : "No se detectó aviso legal en la respuesta.",
      },
      {
        step: "Revisión humana",
        status: needsReview ? "pending" : "done",
        detail: needsReview
          ? "Pendiente de aprobación del abogado."
          : "No requiere aprobación adicional para este tipo de salida.",
      },
    ],
  };
}

function getAssistantEntryByMsgId(msgId) {
  if (!msgId) return null;
  return chatLog.find((entry) => entry.id === msgId && entry.role === "assistant") || null;
}

function getLatestAssistantEntry() {
  for (let i = chatLog.length - 1; i >= 0; i -= 1) {
    if (chatLog[i].role === "assistant") return chatLog[i];
  }
  return null;
}

function buildSessionTimelineHtml(trace, serverTraces = []) {
  const flow = Array.isArray(trace.session_flow) ? trace.session_flow : [];
  const merged = [];
  const seen = new Set();
  for (const row of flow) {
    if (!row?.trace_id || seen.has(row.trace_id)) continue;
    merged.push(row);
    seen.add(row.trace_id);
  }
  for (const row of serverTraces) {
    if (!row?.trace_id || seen.has(row.trace_id)) continue;
    merged.push({
      turn_index: row.turn_index,
      trace_id: row.trace_id,
      input_summary: row.input_summary,
      sent_to_agent: row.sent_to_agent,
      spans_count: Array.isArray(row.spans) ? row.spans.length : 0,
      conversation_continues: row.conversation_continues,
    });
    seen.add(row.trace_id);
  }
  if (trace.trace_id && !seen.has(trace.trace_id)) {
    merged.push({
      turn_index: trace.turn_index,
      trace_id: trace.trace_id,
      input_summary: trace.input_summary,
      sent_to_agent: trace.sent_to_agent,
      spans_count: Array.isArray(trace.spans) ? trace.spans.length : 0,
      conversation_continues: trace.conversation_continues,
      current: true,
    });
  }
  merged.sort((a, b) => (a.turn_index || 0) - (b.turn_index || 0));
  if (!merged.length) {
    return "<p class=\"trace-muted\">Aún no hay turnos persistidos en el servidor para esta sesión.</p>";
  }
  return `<ol class="trace-session-timeline">${merged
    .map(
      (row) => `
      <li class="trace-session-turn${row.current ? " trace-session-turn--current" : ""}">
        <strong>Turno ${escapeHtml(String(row.turn_index ?? "—"))}</strong>
        <span>${escapeHtml(row.trace_id || "")}</span>
        <p>${escapeHtml(row.input_summary || "Sin resumen")}</p>
        <p class="trace-turn-meta">
          Agente: ${escapeHtml(row.sent_to_agent || "n/a")} ·
          Spans: ${escapeHtml(String(row.spans_count ?? 0))} ·
          Continúa: ${row.conversation_continues ? "Sí" : "No"}
        </p>
      </li>`
    )
    .join("")}</ol>`;
}

function buildHistoryPreviewHtml(trace) {
  const rows = Array.isArray(trace.session_history_preview) ? trace.session_history_preview : [];
  if (!rows.length) {
    return "<p class=\"trace-muted\">Sin historial previo cargado en este turno.</p>";
  }
  return `<ul class="trace-history-preview">${rows
    .map(
      (row) => `
      <li>
        <strong>${escapeHtml(row.role || "?")}</strong>
        <span>${escapeHtml(row.preview || "")}</span>
      </li>`
    )
    .join("")}</ul>`;
}

async function fetchSessionTracesFromServer() {
  try {
    const res = await authFetch(`/debug/trace/web:${encodeURIComponent(getUserId())}?limit=40`);
    if (!res.ok) return [];
    const data = await res.json();
    return Array.isArray(data.traces) ? data.traces : [];
  } catch {
    return [];
  }
}

async function renderTracePanelForEntry(entry) {
  if (!traceBodyEl) return;
  if (!entry) {
    traceBodyEl.innerHTML = `
      <div class="trace-empty">
        Seleccione un mensaje del asistente en el Panel de Chat para ver la trazabilidad de decisiones, metadatos y acciones.
      </div>
    `;
    return;
  }
  const trace = entry.trace || inferTrace({ agent: entry.agent, pendingReview: entry.pendingReview }, entry.text);
  const serverTraces = await fetchSessionTracesFromServer();
  const sessionTimeline = buildSessionTimelineHtml(trace, serverTraces);
  const historyPreview = buildHistoryPreviewHtml(trace);
  const statusLabel = trace.blocked
    ? "Bloqueada por alcance de fase"
    : trace.human_review_required
      ? "Pendiente de aprobación humana"
      : "Completada";
  const actionsSource = Array.isArray(trace.actions) && trace.actions.length ? trace.actions : trace.steps || [];
  const actions = actionsSource
    .map((step) => `
      <li>
        <strong>${escapeHtml(step.step || step.type || "Acción")}</strong>
        <span>${escapeHtml(step.detail || "")}</span>
      </li>
    `)
    .join("");
  const receiver = trace.received_by_agent || "agente_coordinador_principal";
  const destination = trace.sent_to_agent || trace.selected_agent || "none";
  const skill = trace.skill_kan || "KAN-N/A";
  const completion = trace.completion || { available: false, calls: [], summary: null, note: "Sin datos." };
  const completionCalls = Array.isArray(completion.calls) ? completion.calls : [];
  const completionRows = completionCalls
    .map((call) => `
      <li>
        <strong>${escapeHtml(call.call_id || "completion")}</strong>
        <span>
          Modelo: ${escapeHtml(call.model || "No reportado")} ·
          Hora: ${escapeHtml(call.started_at_iso || "No reportada")} ·
          Tokens I/O/T: ${escapeHtml(String(call.usage?.input_tokens ?? 0))}/${escapeHtml(String(call.usage?.output_tokens ?? 0))}/${escapeHtml(String(call.usage?.total_tokens ?? 0))}
        </span>
        <span>Response ID: ${escapeHtml(call.response_id || "N/A")} · Request ID: ${escapeHtml(call.request_id || "N/A")}</span>
        <span>Prompt: ${escapeHtml(call.system_prompt || "No reportado")}</span>
        <span>Input enviado: ${escapeHtml(call.input_preview || "No reportado")}</span>
      </li>
    `)
    .join("");
  const spanRows = (Array.isArray(trace.spans) ? trace.spans : [])
    .map(
      (span) => `
      <li class="trace-span trace-span--${escapeHtml(span.status || "done")}">
        <strong>${escapeHtml(span.name || "span")}</strong>
        <span class="trace-span-kind">${escapeHtml(span.kind || "")}</span>
        <p>${escapeHtml(span.detail || "")}</p>
      </li>`
    )
    .join("");
  traceBodyEl.innerHTML = `
    <article class="trace-card">
      <h3>Resumen</h3>
      <div class="trace-kv">
        <p><strong>Estado:</strong> ${escapeHtml(statusLabel)}</p>
        <p><strong>Skill determinado:</strong> ${escapeHtml(skill)}</p>
        <p><strong>Ruta usada:</strong> ${escapeHtml(formatAgentRoute(entry.agent || destination || trace.route || "Sin ruta"))}</p>
      </div>
    </article>
    <article class="trace-card">
      <h3>Enrutamiento de agentes</h3>
      <div class="trace-kv">
        <p><strong>Agente receptor:</strong> ${escapeHtml(receiver)}</p>
        <p><strong>Agente destino:</strong> ${escapeHtml(destination)}</p>
        <p><strong>Motivo skill:</strong> ${escapeHtml(trace.skill_reason || "Sin motivo reportado.")}</p>
      </div>
    </article>
    <article class="trace-card">
      <h3>Metadatos clave</h3>
      <div class="trace-kv">
        <p><strong>Trace ID:</strong> ${escapeHtml(trace.trace_id || "No reportado")}</p>
        <p><strong>Session:</strong> ${escapeHtml(trace.session_id || "No reportado")}</p>
        <p><strong>Mensaje:</strong> ${escapeHtml(entry.id || "No reportado")}</p>
        <p><strong>Canal:</strong> ${escapeHtml(trace.channel || "web")}</p>
        <p><strong>Turno:</strong> ${escapeHtml(String(trace.turn_index ?? "—"))}</p>
        <p><strong>Mensajes en sesión:</strong> ${escapeHtml(String(trace.session_message_count ?? "—"))}</p>
        <p><strong>Trazas previas:</strong> ${escapeHtml(String(trace.prior_traces_count ?? "—"))}</p>
        <p><strong>Spans en este turno:</strong> ${escapeHtml(String(trace.span_count ?? (trace.spans || []).length))}</p>
        <p><strong>Conversación continúa:</strong> ${trace.conversation_continues ? "Sí" : "No"}</p>
      </div>
    </article>
    <article class="trace-card">
      <h3>Continuidad de sesión (${(trace.prior_traces_count ?? 0) + 1} turnos)</h3>
      ${sessionTimeline}
    </article>
    <article class="trace-card">
      <h3>Historial cargado en este turno</h3>
      ${historyPreview}
    </article>
    <article class="trace-card">
      <h3>Completion LLM</h3>
      <div class="trace-kv">
        <p><strong>Proveedor:</strong> ${escapeHtml(completion.provider || "openai-responses")}</p>
        <p><strong>Llamadas:</strong> ${escapeHtml(String(completion.summary?.calls ?? completionCalls.length ?? 0))}</p>
        <p><strong>Tokens entrada/salida/total:</strong> ${escapeHtml(String(completion.summary?.input_tokens ?? 0))} / ${escapeHtml(String(completion.summary?.output_tokens ?? 0))} / ${escapeHtml(String(completion.summary?.total_tokens ?? 0))}</p>
        <p><strong>Nota:</strong> ${escapeHtml(completion.note || "Sin nota")}</p>
      </div>
      <ul class="trace-actions">${completionRows || "<li><span>Sin completions reportados para este mensaje.</span></li>"}</ul>
    </article>
    <article class="trace-card">
      <h3>Spans del flujo (${(trace.spans || []).length})</h3>
      <ul class="trace-actions trace-spans-list">${spanRows || "<li><span>Sin spans detallados.</span></li>"}</ul>
    </article>
    <article class="trace-card">
      <h3>Acciones ejecutadas</h3>
      <ul class="trace-actions">${actions || "<li><span>Sin acciones reportadas.</span></li>"}</ul>
    </article>
  `;
}

function setSelectedTraceMessage(msgId, options = {}) {
  selectedTraceMsgId = msgId || null;
  const { skipSave = false } = options;
  document.querySelectorAll(".message.assistant[data-msg-id]").forEach((el) => {
    el.classList.toggle("message--selected", el.dataset.msgId === selectedTraceMsgId);
  });
  const selected = getAssistantEntryByMsgId(selectedTraceMsgId) || getLatestAssistantEntry();
  if (!selectedTraceMsgId && selected?.id) selectedTraceMsgId = selected.id;
  void renderTracePanelForEntry(selected || null);
  if (selectedTraceMsgId) window.Workspace?.smartTab?.("trazas");
  if (!skipSave) saveSessionState();
}

function scrollToBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function addMessageToUI(role, text, meta = "", options = {}) {
  const el = document.createElement("div");
  el.className = `message ${role}`;
  if (options.msgId) el.dataset.msgId = options.msgId;
  if (options.blockId) el.dataset.blockId = options.blockId;

  const metaHtml = meta || buildMessageMeta(role, options);
  el.innerHTML = `
    ${metaHtml ? `<span class="message-meta">${metaHtml}</span>` : ""}
    <div class="message-body">${formatText(text)}</div>
    ${role === "assistant" ? '<span class="message-phase-badge">Fase 1 · Borrador</span>' : ""}
  `;

  el.querySelector(".message-block-badge")?.addEventListener("click", (e) => {
    const bid = e.currentTarget.dataset.blockId;
    if (bid) {
      setActiveBlock(bid);
      const blockEl = document.querySelector(`.validation-block[data-test-id="${bid}"]`);
      if (blockEl) scrollBlockIntoValidationPanel(blockEl);
    }
  });
  if (role === "assistant" && options.msgId) {
    el.addEventListener("click", () => {
      setSelectedTraceMessage(options.msgId);
    });
  }

  messagesEl.appendChild(el);
  scrollToBottom();
  return el;
}

function showWelcomeMessage() {
  addMessageToUI("assistant", WELCOME_MESSAGE, "Asistente jurídico");
}

function clearChatUI() {
  const container = document.getElementById("messages");
  if (!container) return;
  container.innerHTML = "";
  hideTyping();
}

function restoreChatFromLog() {
  clearChatUI();
  if (!chatLog.length) {
    showWelcomeMessage();
    void renderTracePanelForEntry(null);
    return;
  }
  chatLog.forEach((entry) => {
    addMessageToUI(entry.role, entry.text, "", {
      msgId: entry.id,
      blockId: entry.blockId,
      via: entry.via,
      latencyMs: entry.latencyMs,
      agent: entry.agent,
      pendingReview: entry.pendingReview,
      trace: entry.trace || null,
    });
  });
  const preferred = getAssistantEntryByMsgId(selectedTraceMsgId) || getLatestAssistantEntry();
  setSelectedTraceMessage(preferred?.id || null, { skipSave: true });
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

function scrollToLinkedMessage(blockId) {
  const first = messagesEl.querySelector(`.message[data-block-id="${blockId}"]`);
  if (!first) {
    scrollToChat();
    Toast?.show?.("No hay mensajes vinculados a esta sección en el chat.", "info");
    return;
  }
  scrollToChat();
  first.scrollIntoView({ behavior: "smooth", block: "center" });
  first.classList.add("message--highlight");
  setTimeout(() => first.classList.remove("message--highlight"), 2000);
}

function countLinkedMessages(blockId) {
  // Solo cuenta preguntas enviadas para validar, no respuestas del asistente.
  return chatLog.filter((m) => m.blockId === blockId && m.role === "user").length;
}

function refreshLinkedMessagesUI(blockId) {
  const blockEl = document.querySelector(`.validation-block[data-test-id="${blockId}"]`);
  if (!blockEl) return;
  let linked = blockEl.querySelector(".linked-messages");
  const count = countLinkedMessages(blockId);
  if (!linked) {
    linked = document.createElement("div");
    linked.className = "linked-messages";
    blockEl.querySelector(".mark-actions")?.before(linked);
  }
  if (count === 0) {
    linked.innerHTML = `<span class="linked-messages-empty">Sin mensajes vinculados en el chat.</span>`;
    return;
  }
  linked.innerHTML = `
    <span class="linked-messages-count">${count} mensaje(s) vinculado(s)</span>
    <button type="button" class="btn-linked-messages" data-block-id="${blockId}">Ver en chat</button>
  `;
  linked.querySelector(".btn-linked-messages")?.addEventListener("click", () => {
    scrollToLinkedMessage(blockId);
  });
}

function refreshAllLinkedMessagesUI() {
  VALIDATION_TESTS.forEach((t) => refreshLinkedMessagesUI(t.id));
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

  let noteEl = blockEl.querySelector(".mark-note-display");
  const noteText = markNotes[blockId];
  if (noteText) {
    if (!noteEl) {
      noteEl = document.createElement("p");
      noteEl.className = "mark-note-display";
      blockEl.querySelector(".mark-actions")?.before(noteEl);
    }
    noteEl.innerHTML = `<strong>Nota:</strong> ${escapeHtml(noteText)} <button type="button" class="mark-note-edit" data-block-id="${blockId}">Editar nota</button>`;
    noteEl.querySelector(".mark-note-edit")?.addEventListener("click", () => {
      requestValidationMark(blockId, validationMarks[blockId] || "pass");
    });
  } else if (noteEl) {
    noteEl.remove();
  }

  refreshLinkedMessagesUI(blockId);
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
  if (validationStepperEl) {
    const nextPending = VALIDATION_TESTS.find((t) => !validationMarks[t.id]);
    const stepIndex = nextPending
      ? VALIDATION_TESTS.findIndex((t) => t.id === nextPending.id) + 1
      : VALIDATION_TESTS.length;
    const stepTitle = nextPending ? nextPending.title : "Checklist final";
    validationStepperEl.textContent = `Paso ${stepIndex} de ${VALIDATION_TESTS.length} · ${stepTitle}`;
  }
  applyPendingFilter();
  SessionReport?.refresh?.();
}

function applyPendingFilter() {
  if (!validationBlocksEl) return;
  filterPendingOnly = Boolean(filterPendingEl?.checked);
  validationBlocksEl.querySelectorAll(".validation-block[data-test-id]").forEach((el) => {
    const id = el.dataset.testId;
    const mark = validationMarks[id];
    const isPending = !mark;
    el.classList.toggle("is-filtered-hidden", filterPendingOnly && !isPending);
  });
}

function scrollBlockIntoValidationPanel(targetEl) {
  if (!validationBlocksEl || !targetEl) return;

  const containerTop = validationBlocksEl.getBoundingClientRect().top;
  const targetTop = targetEl.getBoundingClientRect().top;
  const nextScrollTop = validationBlocksEl.scrollTop + (targetTop - containerTop) - 8;

  validationBlocksEl.scrollTo({
    top: Math.max(0, nextScrollTop),
    behavior: "smooth",
  });
}

function scrollToNextValidationBlock(currentBlockId) {
  if (!validationBlocksEl) return;

  const currentIndex = VALIDATION_TESTS.findIndex((t) => t.id === currentBlockId);
  if (currentIndex === -1) return;

  let targetEl = null;
  if (currentIndex < VALIDATION_TESTS.length - 1) {
    const nextTest = VALIDATION_TESTS[currentIndex + 1];
    targetEl = validationBlocksEl.querySelector(
      `.validation-block[data-test-id="${nextTest.id}"]`
    );
    setActiveBlock(nextTest.id);
  } else {
    targetEl = validationBlocksEl.querySelector(".validation-checklist");
    setActiveBlock(null);
  }

  if (!targetEl) return;

  requestAnimationFrame(() => {
    scrollBlockIntoValidationPanel(targetEl);
  });
}

function setValidationMark(blockId, mark, note = undefined) {
  const previousMark = validationMarks[blockId];
  validationMarks[blockId] = mark;
  if (note !== undefined) {
    if (note.trim()) markNotes[blockId] = note.trim();
    else delete markNotes[blockId];
  }
  const test = VALIDATION_TESTS.find((t) => t.id === blockId);
  recordEvent({
    type: "mark",
    blockId,
    blockTitle: test?.title,
    mark,
    note: markNotes[blockId] || "",
    score: computeScore(),
  });
  updateBlockVisualState(blockId);
  refreshLinkedMessagesUI(blockId);
  updateValidationProgress();
  if (mark === "pass" && previousMark !== "pass") {
    scrollToNextValidationBlock(blockId);
  }
}

function openMarkNoteDialog(blockId, mark) {
  const test = VALIDATION_TESTS.find((t) => t.id === blockId);
  const existing = markNotes[blockId] || "";
  const panel = document.createElement("div");
  panel.className = "mark-note-panel";
  panel.innerHTML = `
    <p class="mark-note-title">${mark === "pass" ? "Aprobada" : "Rechazada"} — ${escapeHtml(test?.title || blockId)}</p>
    <label class="mark-note-label">Nota opcional (criterio del revisor)</label>
    <textarea class="mark-note-input" rows="3" maxlength="500" placeholder="¿Por qué marca esta sección?"></textarea>
    <div class="mark-note-actions">
      <button type="button" class="mark-note-confirm">Confirmar</button>
      <button type="button" class="mark-note-skip">Omitir nota</button>
    </div>
  `;
  const textarea = panel.querySelector(".mark-note-input");
  if (textarea && existing) textarea.value = existing;

  const blockEl = document.querySelector(`.validation-block[data-test-id="${blockId}"]`);
  blockEl?.querySelector(".mark-note-panel")?.remove();
  blockEl?.querySelector(".mark-actions")?.after(panel);

  const close = () => panel.remove();

  panel.querySelector(".mark-note-confirm")?.addEventListener("click", () => {
    const note = panel.querySelector(".mark-note-input")?.value || "";
    setValidationMark(blockId, mark, note);
    close();
  });
  panel.querySelector(".mark-note-skip")?.addEventListener("click", () => {
    setValidationMark(blockId, mark, "");
    close();
  });
}

function requestValidationMark(blockId, mark) {
  openMarkNoteDialog(blockId, mark);
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
      sendViaOverride = "probe";
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
    btn.addEventListener("click", () => requestValidationMark(test.id, mark));
    markActions.appendChild(btn);
  });
  section.appendChild(markActions);

  refreshLinkedMessagesUI(test.id);

  return section;
}

function toggleChecklistItem(index) {
  checklistChecked[index] = !checklistChecked[index];
  recordEvent({
    type: "checklist",
    index,
    checked: Boolean(checklistChecked[index]),
  });
  updateChecklistItemVisual(index);
  SessionReport?.refresh?.();
}

function updateChecklistItemVisual(index) {
  const btn = document.querySelector(`.checklist-toggle[data-index="${index}"]`);
  if (!btn) return;
  const checked = Boolean(checklistChecked[index]);
  btn.classList.toggle("is-checked", checked);
  btn.setAttribute("aria-checked", String(checked));
}

function renderChecklistBlock() {
  const section = document.createElement("section");
  section.className = "validation-block validation-checklist";

  const heading = document.createElement("h3");
  heading.textContent = "Checklist final para la abogada";
  section.appendChild(heading);

  const list = document.createElement("ul");
  list.className = "checklist";

  VALIDATION_CHECKLIST.forEach((item, index) => {
    const li = document.createElement("li");
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "checklist-toggle";
    btn.dataset.index = String(index);
    btn.setAttribute("role", "checkbox");
    btn.setAttribute("aria-checked", String(Boolean(checklistChecked[index])));
    if (checklistChecked[index]) btn.classList.add("is-checked");

    const box = document.createElement("span");
    box.className = "check-box";
    box.setAttribute("aria-hidden", "true");

    const label = document.createElement("span");
    label.className = "checklist-text";
    label.textContent = item;

    btn.append(box, label);
    btn.addEventListener("click", () => toggleChecklistItem(index));
    li.appendChild(btn);
    list.appendChild(li);
  });

  section.appendChild(list);

  const note = document.createElement("p");
  note.className = "validation-note";
  note.textContent = `Puntaje máximo: ${VALIDATION_TOTAL_WEIGHT}/100. Si todas las secciones están aprobadas, Fase 1 puede considerarse validada. Si alguna falla, documente el caso y repórtelo al equipo técnico.`;
  section.appendChild(note);

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
    const res = await authFetch("/validation/generate-probes", {
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
        Toast?.show?.(err.detail || "No se pudieron generar preguntas. Intente en unos segundos.", "error");
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
    recordEvent({
      type: "generate_probes",
      blockId: blockId || null,
      blocks,
      source: probesSource,
    });

    if (blockId) {
      refreshProbeListForBlock(blockId);
    } else {
      refreshAllProbeLists();
    }
    updateProbesSourceBadge();
    return true;
  } catch {
    if (!silent) {
      Toast?.show?.("Error de conexión al generar preguntas.", "error");
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

function resetChatConversation() {
  chatEpoch += 1;
  pendingChatMeta = null;
  sendViaOverride = null;
  chatLog = [];
  selectedTraceMsgId = null;
  clearChatUI();
  showWelcomeMessage();
  void renderTracePanelForEntry(null);
  if (sendBtn) sendBtn.disabled = false;
}

function setResetButtonsBusy(busy) {
  [resetChatBtn, document.getElementById("reset-chat-btn-header")].forEach((btn) => {
    if (!btn) return;
    btn.disabled = busy;
    btn.textContent = busy ? "Reiniciando…" : btn.dataset.defaultLabel || "⟲ Reiniciar chat";
  });
}

async function resetChatSession() {
  let pendingDrafts = 0;
  try {
    pendingDrafts = (await window.FirmaPanel?.fetchPendingDrafts?.())?.length || 0;
  } catch {
    /* ignore */
  }
  const warnPending = pendingDrafts
    ? `\n\nAtención: hay ${pendingDrafts} borrador(es) pendiente(s) de aprobación.`
    : "";
  if (
    !confirm(
      `¿Reiniciar la conversación con el agente? Se borrará el historial en el servidor y podrá empezar de cero sin esperar 6 horas.${warnPending}`
    )
  ) {
    return;
  }
  if (resetChatBtn) resetChatBtn.dataset.defaultLabel = resetChatBtn.textContent;
  const resetHeaderBtn = document.getElementById("reset-chat-btn-header");
  if (resetHeaderBtn) resetHeaderBtn.dataset.defaultLabel = resetHeaderBtn.textContent;
  setResetButtonsBusy(true);
  try {
    const res = await authFetch("/chat/reset", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ channel: "web", user_id: getUserId() }),
    });
    if (!res.ok) {
      let detail = "No se pudo reiniciar el chat.";
      try {
        const err = await res.json();
        if (err?.detail) detail = typeof err.detail === "string" ? err.detail : detail;
      } catch {
        /* ignore */
      }
      throw new Error(detail);
    }
    resetChatConversation();
    recordEvent({ type: "reset_chat" });
    saveSessionState();
    window.Workspace?.setExpediente?.(null);
    window.FirmaPanel?.loadBandeja?.();
    window.FirmaPanel?.loadTerminos?.();
    if (typeof Toast !== "undefined" && Toast.show) {
      Toast.show("Conversación reiniciada. El agente no recordará mensajes anteriores.", "info");
    }
  } catch (err) {
    if (typeof Toast !== "undefined" && Toast.show) {
      Toast.show(err?.message || "No se pudo reiniciar el chat. Intente de nuevo.", "error");
    }
  } finally {
    setResetButtonsBusy(false);
    if (resetChatBtn) resetChatBtn.textContent = "⟲ Reiniciar";
    if (resetHeaderBtn) resetHeaderBtn.textContent = "⟲ Reiniciar chat";
  }
}

function resetScoreOnly() {
  if (
    !confirm(
      "¿Reiniciar puntaje, marcas, checklist, notas y conversación? Se conservan las preguntas generadas."
    )
  ) {
    return;
  }
  validationMarks = {};
  markNotes = {};
  checklistChecked = {};
  lastReport = null;
  resetChatConversation();
  recordEvent({ type: "reset_score" });
  VALIDATION_TESTS.forEach((test) => updateBlockVisualState(test.id));
  VALIDATION_CHECKLIST.forEach((_, index) => updateChecklistItemVisual(index));
  refreshAllLinkedMessagesUI();
  updateValidationProgress();
  saveSessionState();
}

function updateConnectionStatus(connected) {
  const el = document.getElementById("connection-status");
  if (!el) return;
  el.textContent = connected
    ? "Estado actual: Conectado · Fase 1 activa"
    : "Estado actual: sin conexión o Fase 1 no confirmada";
  el.classList.toggle("is-ok", connected);
}

async function checkHealth() {
  try {
    const res = await fetch("/health");
    const data = await res.json();
    const connected = data.status === "ok";
    if (data.status === "ok" && data.openai_configured) {
      statusDot.classList.add("online");
      statusText.textContent = "Conectado · Firma activa";
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

  const epochAtSend = chatEpoch;
  const via = sendViaOverride || (activeBlockId ? "probe" : "manual");
  const blockId = activeBlockId || null;
  sendViaOverride = null;

  addMessageToUI("user", trimmed, "", { blockId, via });
  const userEntry = appendChatLogEntry({
    role: "user",
    text: trimmed,
    via,
    blockId,
  });

  const abortIfStale = () => {
    if (epochAtSend === chatEpoch) return false;
    if (chatLog.some((entry) => entry.id === userEntry.id)) {
      chatLog = chatLog.filter((entry) => entry.id !== userEntry.id);
      saveSessionState();
    }
    hideTyping();
    if (sendBtn) sendBtn.disabled = false;
    pendingChatMeta = null;
    return true;
  };

  const userEl = messagesEl.lastElementChild;
  if (userEl && userEntry.id) userEl.dataset.msgId = userEntry.id;
  pendingChatMeta = { userEntryId: userEntry.id, startedAt: Date.now(), epoch: epochAtSend };

  inputEl.value = "";
  sendBtn.disabled = true;
  showTyping();

  let assistantText =
    "No pude procesar la consulta en este momento. Intente de nuevo en unos segundos.";
  let assistantAgent = "error";
  let assistantPendingReview = false;
  let assistantTrace = null;
  let assistantDraftId = null;

  try {
    const res = await authFetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: trimmed,
        channel: "web",
        user_id: getUserId(),
      }),
    });

    if (abortIfStale()) return;

    hideTyping();

    if (res.ok) {
      const data = await res.json();
      assistantText = data.text;
      assistantAgent = data.agent || assistantAgent;
      assistantPendingReview = Boolean(data.pending_review);
      assistantTrace = data.trace || null;
      assistantDraftId = data.draft_id || null;
    }
  } catch {
    if (abortIfStale()) return;
    hideTyping();
    assistantText =
      "Error de conexión. Verifique su red o espere si el servicio estaba inactivo.";
  }

  if (abortIfStale()) return;

  const latencyMs = pendingChatMeta ? Date.now() - pendingChatMeta.startedAt : null;
  const assistantEntry = appendChatLogEntry({
    role: "assistant",
    text: assistantText,
    blockId,
    latencyMs,
    replyTo: pendingChatMeta?.userEntryId,
    agent: assistantAgent,
    pendingReview: assistantPendingReview,
    trace: assistantTrace || inferTrace({ agent: assistantAgent, pendingReview: assistantPendingReview }, assistantText),
  });
  addMessageToUI("assistant", assistantText, "", {
    msgId: assistantEntry.id,
    blockId,
    latencyMs,
    agent: assistantAgent,
    pendingReview: assistantPendingReview,
    trace: assistantEntry.trace,
  });
  const assistantEl = messagesEl.lastElementChild;
  if (assistantEl && assistantEntry.id) assistantEl.dataset.msgId = assistantEntry.id;
  setSelectedTraceMessage(assistantEntry.id, { skipSave: true });
  saveSessionState();
  pendingChatMeta = null;

  if (assistantDraftId) {
    document.dispatchEvent(
      new CustomEvent("draft-created", { detail: { draftId: assistantDraftId } })
    );
    window.Workspace?.updateBandejaBadge?.(
      ((await window.FirmaPanel?.fetchPendingDrafts?.()) || []).length
    );
    if (typeof Toast !== "undefined" && Toast.show) {
      Toast.show("Borrador enviado a la bandeja del abogado para aprobación.", "info");
    }
  }

  sendBtn.disabled = false;
  inputEl.focus();
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

function initCollapsiblePanel(panelId, toggleId) {
  const panel = document.getElementById(panelId);
  const toggle = document.getElementById(toggleId);
  if (!panel || !toggle) return;

  toggle.addEventListener("click", () => {
    const isOpen = panel.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", String(isOpen));
  });
}

function initValidationPanel() {
  initCollapsiblePanel("trace-panel", "trace-toggle");
  initCollapsiblePanel("report-panel", "report-toggle");
  resetScoreBtn?.addEventListener("click", resetScoreOnly);
  resetChatBtn?.addEventListener("click", () => {
    resetChatSession();
  });
  document.getElementById("reset-chat-btn-header")?.addEventListener("click", () => {
    resetChatSession();
  });
  filterPendingEl?.addEventListener("change", applyPendingFilter);
  chatFileInputEl?.addEventListener("change", () => {
    const file = chatFileInputEl.files?.[0];
    if (file) void uploadChatAttachment(file);
    chatFileInputEl.value = "";
  });
}

async function syncRubricFromServer() {
  if (!ENABLE_SERVER_RUBRIC) return;
  try {
    const res = await authFetch("/validation/rubric");
    if (!res.ok) return;
    const data = await res.json();
    const weightMap = {};
    if (data.connection) weightMap[data.connection.id] = data.connection.weight;
    (data.blocks || []).forEach((b) => {
      weightMap[b.id] = b.weight;
    });
    VALIDATION_TESTS.forEach((test) => {
      if (weightMap[test.id] != null) test.weight = weightMap[test.id];
    });
    if (data.total_weight) {
      window.VALIDATION_TOTAL_WEIGHT = data.total_weight;
    }
    updateValidationProgress();
  } catch {
    /* fallback to bundled rubric */
  }
}

function initOnboarding() {
  const modal = document.getElementById("onboarding-modal");
  const closeBtn = document.getElementById("onboarding-close");
  if (!modal || localStorage.getItem(ONBOARDING_KEY)) return;
  modal.hidden = false;
  closeBtn?.addEventListener("click", () => {
    modal.hidden = true;
    localStorage.setItem(ONBOARDING_KEY, "1");
  });
}

async function bootstrapValidationProbes() {
  updateProbesSourceBadge();
  if (probesSource === "llm" && Object.keys(dynamicProbes).length > 0) {
    refreshAllProbeLists();
    return;
  }
  // No llamar a OpenAI al cargar: en Render free tier puede tumbar el servicio
  // justo después del login (cold start + LLM). Las preguntas de ejemplo bastan
  // hasta que la abogada pulse «Generar Nuevas Preguntas».
  initDefaultProbes();
  refreshAllProbeLists();
}

let appBooted = false;
let sessionReportReady = false;

async function bootAgentApp() {
  if (appBooted) return;
  appBooted = true;
  const hadServerHistory = await loadServerHistory();
  restoreChatFromLog();
  if (hadServerHistory && typeof Toast !== "undefined" && Toast.show) {
    Toast.show("Sesión restaurada desde el servidor.", "info");
  }
  checkHealth();
  if (typeof VALIDATION_TESTS !== "undefined") {
    syncRubricFromServer();
    bootstrapValidationProbes();
  }
  if (!sessionReportReady) {
    SessionReport.init({
      getSession: getSessionSnapshot,
      saveSession: (snapshot) => {
        lastReport = snapshot.lastReport || null;
        saveSessionState();
        refreshAllLinkedMessagesUI();
      },
      getUserId,
    });
    sessionReportReady = true;
  }
  try {
    inputEl?.focus({ preventScroll: true });
  } catch {
    /* iOS Safari puede rechazar focus automático */
  }
  window.addEventListener("load", () => {
    window.scrollTo(0, 0);
    document.documentElement.scrollTop = 0;
    document.body.scrollTop = 0;
  });
}

window.bootAgentApp = bootAgentApp;

if (typeof VALIDATION_TESTS !== "undefined") {
  initDefaultProbes();
  renderValidationPanel();
}
initValidationPanel();
