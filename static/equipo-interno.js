/** Junta del caso — transcript legible Coordinador ↔ especialistas (solo abogado). */
(function () {
  const POLL_MS = 3000;
  const COLLAPSE_AT = 420;

  const KIND_LABELS = {
    consult: "Consulta",
    findings: "Hallazgos",
    synthesize: "Síntesis",
    escalate: "Escalamiento",
  };

  let pollTimer = null;
  let lastEntries = [];
  let lastPendientes = [];
  let filterMode = "todos"; // todos | alto | specialist:<id>
  let focusState = null; // { turnRef, afterIso, entryId, highlightUntil }
  let knownSpecialists = [];

  const listEl = () => document.getElementById("equipo-transcript");
  const pendientesEl = () => document.getElementById("junta-pendientes");
  const filtersEl = () => document.getElementById("junta-filters");

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function sessionId() {
    return (
      window.Workspace?.getSessionId?.() ||
      `web:${window.getChatUserId?.() || window.getUserId?.() || "abogado"}`
    );
  }

  function authFetch(url, options) {
    if (typeof window.authFetch === "function") return window.authFetch(url, options);
    return fetch(url, options);
  }

  function formatWhen(iso) {
    if (!iso) return "";
    try {
      const d = new Date(iso);
      if (Number.isNaN(d.getTime())) return iso;
      return d.toLocaleString("es-CO", { dateStyle: "short", timeStyle: "short" });
    } catch {
      return iso;
    }
  }

  function kindLabel(kind) {
    if (!kind) return "";
    return KIND_LABELS[kind] || kind;
  }

  function isTabVisible() {
    const panel = document.getElementById("tab-equipo");
    if (!panel) return false;
    return !panel.hidden && panel.classList.contains("is-active");
  }

  function collapsibleHtml(text, cssClass) {
    const raw = String(text || "—");
    if (raw.length <= COLLAPSE_AT) {
      return `<p class="${cssClass}">${escapeHtml(raw)}</p>`;
    }
    const short = escapeHtml(raw.slice(0, COLLAPSE_AT));
    const full = escapeHtml(raw);
    return `
      <div class="${cssClass} junta-collapse" data-expanded="0">
        <p class="junta-collapse-short">${short}…</p>
        <p class="junta-collapse-full" hidden>${full}</p>
        <button type="button" class="junta-toggle">Ver más</button>
      </div>`;
  }

  function entryMatchesFocus(e) {
    if (!focusState) return false;
    if (focusState.entryId && e.id === focusState.entryId) return true;
    if (focusState.turnRef) {
      const ref = e.turn_ref || e.trace_id || "";
      if (ref && ref === focusState.turnRef) return true;
    }
    if (focusState.afterIso && e.created_at) {
      try {
        const t = new Date(e.created_at).getTime();
        const after = new Date(focusState.afterIso).getTime();
        if (!Number.isNaN(t) && !Number.isNaN(after) && t >= after) return true;
      } catch {
        /* ignore */
      }
    }
    return false;
  }

  function filteredEntries(entries) {
    if (filterMode === "todos") return entries;
    if (filterMode === "alto") return entries.filter((e) => e.alto_riesgo);
    if (filterMode.startsWith("specialist:")) {
      const sid = filterMode.slice("specialist:".length);
      return entries.filter((e) => (e.specialist_id || "") === sid);
    }
    return entries;
  }

  function renderFilters(entries) {
    const root = filtersEl();
    if (!root) return;
    const specs = [];
    for (const e of entries) {
      const id = e.specialist_id || "";
      const label = e.to_label || id;
      if (id && !specs.some((s) => s.id === id)) specs.push({ id, label });
    }
    knownSpecialists = specs;
    const chips = [
      { mode: "todos", label: "Todos" },
      { mode: "alto", label: "Alto riesgo" },
      ...specs.map((s) => ({ mode: `specialist:${s.id}`, label: s.label })),
    ];
    root.innerHTML = chips
      .map((c) => {
        const active = filterMode === c.mode ? " is-active" : "";
        const risk = c.mode === "alto" ? " junta-chip--risk" : "";
        return `<button type="button" class="junta-chip${active}${risk}" data-filter="${escapeHtml(c.mode)}">${escapeHtml(c.label)}</button>`;
      })
      .join("");
    root.querySelectorAll(".junta-chip").forEach((btn) => {
      btn.addEventListener("click", () => {
        filterMode = btn.dataset.filter || "todos";
        renderEntries(lastEntries);
        renderFilters(lastEntries);
      });
    });
  }

  function renderPendientes(list) {
    const root = pendientesEl();
    if (!root) return;
    const items = Array.isArray(list) ? list.filter(Boolean) : [];
    if (!items.length) {
      root.hidden = true;
      root.innerHTML = "";
      return;
    }
    root.hidden = false;
    root.innerHTML = `
      <strong class="junta-pendientes-title">Pendientes de verificar</strong>
      <ul class="junta-pendientes-list">
        ${items.map((p) => `<li>${escapeHtml(p)}</li>`).join("")}
      </ul>`;
  }

  function renderEntries(entries) {
    const root = listEl();
    if (!root) return;
    const visible = filteredEntries(entries);
    if (!visible.length) {
      root.innerHTML = entries.length
        ? '<p class="equipo-empty">No hay intercambios con el filtro seleccionado.</p>'
        : '<p class="equipo-empty">Aún no hay consultas en la Junta del caso. Cuando el Coordinador del Caso delegue a un especialista, el intercambio aparecerá aquí.</p>';
      return;
    }

    root.innerHTML = visible
      .map((e) => {
        const fromL = escapeHtml(e.from_label || "Coordinador");
        const toL = escapeHtml(e.to_label || "Especialista");
        const when = escapeHtml(formatWhen(e.created_at));
        const ronda = e.ronda != null ? `Ronda ${escapeHtml(String(e.ronda))}` : "";
        const kind = escapeHtml(e.kind_label || kindLabel(e.kind) || "Hallazgos");
        const focused = entryMatchesFocus(e) ? " is-focused" : "";
        const risk = e.alto_riesgo ? " is-risk" : "";
        const turnRef = escapeHtml(e.turn_ref || e.trace_id || "");
        return `
          <article class="junta-exchange equipo-turn${focused}${risk}"
            data-entry-id="${escapeHtml(e.id || "")}"
            data-turn-ref="${turnRef}"
            data-specialist="${escapeHtml(e.specialist_id || "")}">
            <header class="equipo-turn-head junta-exchange-head">
              <span class="equipo-route">${fromL} ↔ ${toL}</span>
              <span class="junta-meta">
                ${ronda ? `<span class="junta-ronda">${ronda}</span>` : ""}
                <span class="junta-kind">${kind}</span>
                <time class="equipo-when">${when}</time>
              </span>
            </header>
            <div class="junta-bubble junta-bubble--pedido">
              <span class="junta-bubble-who">${fromL} → ${toL} · Consulta</span>
              ${collapsibleHtml(e.pedido || "—", "junta-bubble-body")}
            </div>
            <div class="junta-bubble junta-bubble--retorno">
              <span class="junta-bubble-who">${toL} → ${fromL} · Hallazgos</span>
              ${collapsibleHtml(e.respuesta || "—", "junta-bubble-body")}
            </div>
          </article>`;
      })
      .join("");

    root.querySelectorAll(".junta-toggle").forEach((btn) => {
      btn.addEventListener("click", (ev) => {
        ev.stopPropagation();
        const wrap = btn.closest(".junta-collapse");
        if (!wrap) return;
        const expanded = wrap.dataset.expanded === "1";
        wrap.dataset.expanded = expanded ? "0" : "1";
        wrap.querySelector(".junta-collapse-short")?.toggleAttribute("hidden", !expanded);
        wrap.querySelector(".junta-collapse-full")?.toggleAttribute("hidden", expanded);
        btn.textContent = expanded ? "Ver más" : "Ver menos";
      });
    });

    if (focusState) {
      const target =
        root.querySelector(".junta-exchange.is-focused") ||
        root.querySelector(`[data-entry-id="${CSS.escape(focusState.entryId || "")}"]`);
      if (target) {
        target.scrollIntoView({ block: "nearest", behavior: "smooth" });
      }
    }
  }

  async function loadPendientesForFocus(entries) {
    const turnRef = focusState?.turnRef;
    if (!turnRef) {
      // Fallback: scrape [PENDIENTE DE VERIFICAR] from visible returns.
      const found = [];
      for (const e of entries.slice(-12)) {
        const blob = String(e.respuesta || "");
        if (/\[PENDIENTE DE VERIFICAR\]/i.test(blob)) {
          for (const part of blob.split(/[\n;•]+/)) {
            const chunk = part.trim();
            if (/\[PENDIENTE DE VERIFICAR\]/i.test(chunk) && !found.includes(chunk)) {
              found.push(chunk.slice(0, 220));
            }
          }
        }
      }
      lastPendientes = found.slice(0, 12);
      renderPendientes(lastPendientes);
      return;
    }
    try {
      const sid = encodeURIComponent(sessionId());
      const res = await authFetch(`/support/operations/${sid}?limit=40`);
      if (!res.ok) {
        lastPendientes = [];
        renderPendientes([]);
        return;
      }
      const data = await res.json();
      const rows = Array.isArray(data.traces) ? data.traces : Array.isArray(data) ? data : [];
      let pendientes = [];
      for (const row of rows) {
        const payload = row.payload || row.trace || row;
        const tid = payload.trace_id || row.trace_id || "";
        if (tid !== turnRef) continue;
        const summary = payload.deliberation?.summary || {};
        pendientes = Array.isArray(summary.open_pendientes) ? summary.open_pendientes : [];
        break;
      }
      lastPendientes = pendientes;
      renderPendientes(pendientes);
    } catch {
      lastPendientes = [];
      renderPendientes([]);
    }
  }

  async function refresh(opts = {}) {
    const root = listEl();
    if (!root) return;
    if (!opts.quiet) root.setAttribute("aria-busy", "true");
    try {
      const sid = encodeURIComponent(sessionId());
      const res = await authFetch(`/abogado/internal-transcript?session_id=${sid}&limit=100`);
      if (!res.ok) {
        if (!opts.quiet) {
          root.innerHTML =
            '<p class="equipo-empty">No se pudo cargar la Junta del caso.</p>';
        }
        return;
      }
      const data = await res.json();
      lastEntries = Array.isArray(data.entries) ? data.entries : [];
      renderFilters(lastEntries);
      renderEntries(lastEntries);
      void loadPendientesForFocus(lastEntries);
    } catch {
      if (!opts.quiet) {
        root.innerHTML =
          '<p class="equipo-empty">Error de red al cargar la Junta del caso.</p>';
      }
    } finally {
      root.removeAttribute("aria-busy");
    }
  }

  function startPoll() {
    stopPoll();
    pollTimer = setInterval(() => {
      if (isTabVisible() && document.visibilityState !== "hidden") {
        void refresh({ quiet: true });
      }
    }, POLL_MS);
  }

  function stopPoll() {
    if (pollTimer) {
      clearInterval(pollTimer);
      pollTimer = null;
    }
  }

  function onTabShown() {
    void refresh();
    startPoll();
  }

  function onTabHidden() {
    stopPoll();
  }

  /**
   * Abre/enfoca la Junta para un turno del Coordinador.
   * @param {{ turnRef?: string, afterIso?: string, entryId?: string, openTab?: boolean }} opts
   */
  function focusTurn(opts = {}) {
    focusState = {
      turnRef: opts.turnRef || opts.traceId || null,
      afterIso: opts.afterIso || null,
      entryId: opts.entryId || null,
      highlightUntil: Date.now() + 12000,
    };
    if (opts.openTab !== false) {
      window.Workspace?.switchTab?.("equipo");
    }
    void refresh().then(() => {
      renderEntries(lastEntries);
    });
  }

  async function focusAttribution(opts = {}) {
    const sid = sessionId();
    try {
      const params = new URLSearchParams({ session_id: sid });
      if (opts.hint) params.set("hint", opts.hint);
      if (opts.turnRef) params.set("turn_ref", opts.turnRef);
      const res = await authFetch(`/abogado/attribution-entry?${params}`);
      if (res.ok) {
        const data = await res.json();
        if (data.entry?.id) {
          focusTurn({
            entryId: data.entry.id,
            turnRef: data.entry.turn_ref || opts.turnRef,
            openTab: true,
          });
          return;
        }
      }
    } catch {
      /* fallback below */
    }
    focusTurn({
      turnRef: opts.turnRef || null,
      afterIso: opts.afterIso || null,
      openTab: true,
    });
  }

  function init() {
    document.getElementById("btn-refresh-equipo")?.addEventListener("click", () => {
      void refresh();
    });
    document.addEventListener("workspace:tab", (ev) => {
      if (ev.detail?.tab === "equipo") onTabShown();
      else onTabHidden();
    });
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "hidden") stopPoll();
      else if (isTabVisible()) startPoll();
    });
    document.addEventListener("workspace:chat-activity", () => {
      if (isTabVisible()) void refresh({ quiet: true });
    });
    // Clear stale highlight
    setInterval(() => {
      if (focusState?.highlightUntil && Date.now() > focusState.highlightUntil) {
        focusState = null;
        if (lastEntries.length) renderEntries(lastEntries);
      }
    }, 2000);
  }

  window.EquipoInterno = {
    refresh,
    init,
    focusTurn,
    focusAttribution,
    startPoll,
    stopPoll,
  };
  // Alias de producto
  window.JuntaDelCaso = window.EquipoInterno;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
