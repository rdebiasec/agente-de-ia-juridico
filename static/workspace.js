/**
 * Mesa de trabajo del abogado: expediente, tabs contextuales, chips de header.
 */
(() => {
  "use strict";

  const runtime = window.DeskRuntime || {};
  const esc = runtime.esc
    ? (s) => runtime.esc(s)
    : (s) =>
        String(s == null ? "" : s)
          .replace(/&/g, "&amp;")
          .replace(/</g, "&lt;")
          .replace(/>/g, "&gt;")
          .replace(/"/g, "&quot;");

  let expedienteState = null;
  let hitos = [];

  function getSessionId() {
    if (runtime.getSessionId) return runtime.getSessionId();
    const uid =
      typeof window.getChatUserId === "function"
        ? window.getChatUserId()
        : localStorage.getItem("agente-juridico-user-id") || "web";
    return `web:${uid}`;
  }

  function partesLabel(exp) {
    if (!exp?.partes?.length) return { accionante: null, accionado: null };
    let accionante = null;
    let accionado = null;
    exp.partes.forEach((p) => {
      const rol = String(p.rol || p.tipo || "").toLowerCase();
      const nombre = p.nombre || p.razon_social || p.nombre_completo;
      if (!nombre) return;
      if (rol.includes("accionante") || rol.includes("demandante")) accionante = nombre;
      if (rol.includes("accionado") || rol.includes("demandado")) accionado = nombre;
    });
    return { accionante, accionado };
  }

  function renderExpedienteFields(exp) {
    const el = document.getElementById("expediente-fields");
    if (!el) return;
    if (!exp) {
      el.innerHTML = '<p class="expediente-empty">Sin datos de expediente aún. Describa el caso en el chat.</p>';
      return;
    }
    const { accionante, accionado } = partesLabel(exp);
    const rows = [
      ["Radicado", exp.radicado],
      ["Accionante", accionante],
      ["Accionado", accionado],
      ["Materia", exp.materia],
      ["Tipo de proceso", exp.tipo_proceso],
      ["Etapa", exp.etapa_actual],
      ["Despacho", exp.despacho_judicial],
      ["Involucra menor", exp.involucra_menor ? "Sí" : "No"],
      ["Datos sensibles", exp.datos_sensibles ? "Sí" : "No"],
    ].filter(([, v]) => v);

    const flags = `
      <div class="expediente-flags" style="margin-top:0.75rem;font-size:0.85rem;">
        <label style="display:flex;gap:0.4rem;align-items:center;margin-bottom:0.35rem;">
          <input type="checkbox" id="flag-involucra-menor" ${exp.involucra_menor ? "checked" : ""} />
          <span>Involucra menor de edad</span>
        </label>
        <label style="display:flex;gap:0.4rem;align-items:center;">
          <input type="checkbox" id="flag-datos-sensibles" ${exp.datos_sensibles ? "checked" : ""} />
          <span>Datos sensibles autorizados</span>
        </label>
      </div>`;

    el.innerHTML =
      (rows.length
        ? `<dl class="expediente-dl">${rows
            .map(([k, v]) => `<div><dt>${esc(k)}</dt><dd>${esc(v)}</dd></div>`)
            .join("")}</dl>`
        : '<p class="expediente-empty">Expediente iniciado sin campos identificados aún.</p>') + flags;

    document.getElementById("flag-involucra-menor")?.addEventListener("change", (ev) => {
      patchExpedienteFlags({ involucra_menor: ev.target.checked });
    });
    document.getElementById("flag-datos-sensibles")?.addEventListener("change", (ev) => {
      patchExpedienteFlags({ datos_sensibles: ev.target.checked });
    });
  }

  async function patchExpedienteFlags(partial) {
    const sid = getSessionId();
    if (!sid || typeof authFetch !== "function") return;
    try {
      const res = await authFetch("/expediente/flags", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sid, ...partial }),
      });
      if (!res.ok) throw new Error("No se pudieron guardar las marcas.");
      const data = await res.json();
      if (data.expediente) setExpediente(data.expediente);
    } catch (err) {
      Toast?.show?.(err?.message || "Error al guardar marcas de sensibilidad.", "error");
    }
  }

  function renderContextChips(exp) {
    const el = document.getElementById("chat-context-chips");
    const caseChip = document.getElementById("workspace-case-chip");
    if (!el) return;
    const chips = [];
    if (exp?.materia) chips.push(exp.materia);
    if (exp?.tipo_proceso) chips.push(exp.tipo_proceso);
    if (exp?.radicado) chips.push(`Rad. ${exp.radicado}`);
    if (exp?.involucra_menor) chips.push("Menor");
    if (exp?.datos_sensibles) chips.push("Datos sensibles");
    el.innerHTML = chips.map((c) => `<span class="context-chip">${esc(c)}</span>`).join("");
    if (caseChip) {
      caseChip.textContent = exp?.radicado ? `Rad. ${exp.radicado}` : exp?.materia ? exp.materia : "Caso activo";
    }
  }

  function addHito(label) {
    if (!label || hitos.includes(label)) return;
    hitos.push(label);
    renderHitos();
  }

  function renderHitos() {
    const wrap = document.getElementById("expediente-hitos");
    const list = document.getElementById("expediente-hitos-list");
    if (!wrap || !list) return;
    if (!hitos.length) {
      wrap.hidden = true;
      return;
    }
    wrap.hidden = false;
    list.innerHTML = hitos.map((h) => `<li>${esc(h)}</li>`).join("");
  }

  function renderBitacora(exp) {
    const wrap = document.getElementById("expediente-bitacora");
    const list = document.getElementById("expediente-bitacora-list");
    if (!wrap || !list) return;
    const entries = Array.isArray(exp?.bitacora) ? exp.bitacora : [];
    if (!entries.length) {
      wrap.hidden = true;
      list.innerHTML = "";
      return;
    }
    wrap.hidden = false;
    const tail = entries.slice(-8).reverse();
    list.innerHTML = tail
      .map((e) => {
        const autor = esc(e.autor || "gerente_caso");
        const tipo = esc(e.tipo || "nota");
        const resumen = esc((e.resumen || "").slice(0, 180));
        return `<li><strong>${autor}</strong> · <em>${tipo}</em><br>${resumen}</li>`;
      })
      .join("");
  }

  function setExpediente(exp) {
    expedienteState = exp || null;
    renderExpedienteFields(expedienteState);
    renderBitacora(expedienteState);
    renderContextChips(expedienteState);
    autofillSessionIds();
    if (expedienteState?.radicado) addHito("Radicado identificado");
    if (expedienteState?.etapa_actual) addHito(`Etapa: ${expedienteState.etapa_actual}`);
  }

  function autofillSessionIds() {
    const sid = getSessionId();
    ["firma-exp-id", "firma-search-exp", "firma-term-exp"].forEach((id) => {
      const input = document.getElementById(id);
      if (input) input.value = sid;
    });
  }

  function normalizeTabId(tabId) {
    if (tabId === "trazas" || tabId === "trace" || tabId === "detalle") return "actividad";
    return tabId;
  }

  function switchTab(tabId) {
    const id = normalizeTabId(tabId);
    document.querySelectorAll(".context-tab").forEach((btn) => {
      const active = btn.dataset.tab === id;
      btn.classList.toggle("is-active", active);
      btn.setAttribute("aria-selected", String(active));
      btn.setAttribute("tabindex", active ? "0" : "-1");
    });
    document.querySelectorAll(".context-tab-panel").forEach((panel) => {
      const active = panel.dataset.panel === id;
      panel.classList.toggle("is-active", active);
      panel.hidden = !active;
    });
    if (
      id === "actividad" ||
      id === "borrador" ||
      id === "plazos" ||
      id === "rag" ||
      id === "equipo" ||
      id === "canal-victima"
    ) {
      try {
        history.replaceState(null, "", `#${id}`);
      } catch {
        /* ignore */
      }
    }
    if (id === "actividad") {
      window.ChatActivity?.refresh?.({ force: true });
    }
    if (id === "equipo") {
      window.EquipoInterno?.refresh?.();
    }
    if (id === "canal-victima") {
      window.CanalVictima?.startPoll?.();
    }
    if (runtime.emit) {
      runtime.emit("workspace:tab", { tab: id });
    } else {
      try {
        document.dispatchEvent(new CustomEvent("workspace:tab", { detail: { tab: id } }));
      } catch {
        /* ignore */
      }
    }
  }

  function smartTab(reason) {
    if (reason === "borrador" || reason === "draft") switchTab("borrador");
    else if (reason === "plazos" || reason === "deadline") switchTab("plazos");
    else if (
      reason === "equipo" ||
      reason === "interno" ||
      reason === "transcript" ||
      reason === "junta" ||
      reason === "junta-del-caso"
    ) {
      switchTab("equipo");
    }
    else if (reason === "canal-victima" || reason === "canal" || reason === "victima") {
      switchTab("canal-victima");
    }
    else if (reason === "trazas" || reason === "trace" || reason === "actividad" || reason === "detalle") {
      switchTab("actividad");
    }
  }

  function initSidebarCollapse() {
    const layout = document.querySelector(".desk-layout, .workspace-layout");
    const sidebar = document.getElementById("expediente-sidebar");
    const collapseBtn = document.getElementById("btn-sidebar-collapse");
    const expandBtn = document.getElementById("btn-sidebar-expand");
    if (!layout || !sidebar) return;
    collapseBtn?.addEventListener("click", () => {
      layout.classList.add("expediente-collapsed");
      if (expandBtn) expandBtn.hidden = false;
    });
    expandBtn?.addEventListener("click", () => {
      layout.classList.remove("expediente-collapsed");
      expandBtn.hidden = true;
    });
  }

  function initTabs() {
    const tabs = Array.from(document.querySelectorAll(".context-tab"));
    const moveTo = (nextIndex) => {
      const safe = ((nextIndex % tabs.length) + tabs.length) % tabs.length;
      const next = tabs[safe];
      if (!next) return;
      switchTab(next.dataset.tab);
      next.focus();
    };
    tabs.forEach((btn, idx) => {
      if (!btn.classList.contains("is-active")) btn.setAttribute("tabindex", "-1");
      btn.addEventListener("click", () => switchTab(btn.dataset.tab));
      btn.addEventListener("keydown", (ev) => {
        if (ev.key === "ArrowRight") {
          ev.preventDefault();
          moveTo(idx + 1);
        } else if (ev.key === "ArrowLeft") {
          ev.preventDefault();
          moveTo(idx - 1);
        } else if (ev.key === "Home") {
          ev.preventDefault();
          moveTo(0);
        } else if (ev.key === "End") {
          ev.preventDefault();
          moveTo(tabs.length - 1);
        } else if (ev.key === "Enter" || ev.key === " ") {
          ev.preventDefault();
          switchTab(btn.dataset.tab);
        }
      });
    });
  }

  function updateDeadlineChip(deadlines) {
    const chip = document.getElementById("workspace-deadline-chip");
    if (!chip) return;
    const pending = (deadlines || []).filter((d) => d.estado === "pendiente");
    if (!pending.length) {
      chip.hidden = true;
      return;
    }
    const sorted = pending.slice().sort((a, b) => String(a.fecha_limite).localeCompare(String(b.fecha_limite)));
    const next = sorted[0];
    const dias = next.dias_habiles != null ? `${next.dias_habiles} días háb.` : "";
    chip.textContent = `${next.descripcion}${dias ? ` · ${dias}` : ""}`;
    chip.className = "workspace-deadline-chip";
    const limit = next.fecha_limite ? new Date(next.fecha_limite) : null;
    if (limit) {
      const daysLeft = Math.ceil((limit - new Date()) / (86400000));
      if (daysLeft <= 3) chip.classList.add("workspace-deadline-chip--urgent");
    }
    chip.hidden = false;
  }

  function updateBandejaBadge(count) {
    const badge = document.getElementById("bandeja-badge");
    if (!badge) return;
    if (!count) {
      badge.hidden = true;
      return;
    }
    badge.hidden = false;
    badge.textContent = String(count);
  }

  let lastFocusedBeforeDrawer = null;

  function drawerFocusableElements() {
    const drawer = document.getElementById("firma-drawer");
    if (!drawer || drawer.hidden) return [];
    return Array.from(
      drawer.querySelectorAll(
        'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
      )
    );
  }

  function handleDrawerKeydown(ev) {
    if (ev.key === "Escape") {
      ev.preventDefault();
      closeDrawer();
      return;
    }
    if (ev.key !== "Tab") return;
    const items = drawerFocusableElements();
    if (!items.length) return;
    const first = items[0];
    const last = items[items.length - 1];
    if (ev.shiftKey && document.activeElement === first) {
      ev.preventDefault();
      last.focus();
    } else if (!ev.shiftKey && document.activeElement === last) {
      ev.preventDefault();
      first.focus();
    }
  }

  function openDrawer() {
    // Camino principal de operación: pestaña Borrador.
    switchTab("borrador");
    // Drawer solo como apoyo en pantallas estrechas.
    if (!window.matchMedia("(max-width: 1180px)").matches) return;
    lastFocusedBeforeDrawer = document.activeElement;
    document.getElementById("firma-drawer")?.removeAttribute("hidden");
    document.getElementById("firma-drawer-backdrop")?.removeAttribute("hidden");
    document.body.classList.add("drawer-open");
    document.addEventListener("keydown", handleDrawerKeydown);
    setTimeout(() => {
      drawerFocusableElements()[0]?.focus();
    }, 0);
  }

  function closeDrawer() {
    document.getElementById("firma-drawer")?.setAttribute("hidden", "");
    document.getElementById("firma-drawer-backdrop")?.setAttribute("hidden", "");
    document.body.classList.remove("drawer-open");
    document.removeEventListener("keydown", handleDrawerKeydown);
    if (lastFocusedBeforeDrawer && typeof lastFocusedBeforeDrawer.focus === "function") {
      lastFocusedBeforeDrawer.focus();
    }
    lastFocusedBeforeDrawer = null;
  }

  document.getElementById("firma-drawer-backdrop")?.addEventListener("click", closeDrawer);

  window.Workspace = {
    getSessionId,
    setExpediente,
    addHito,
    switchTab,
    smartTab,
    updateDeadlineChip,
    updateBandejaBadge,
    openDrawer,
    closeDrawer,
    autofillSessionIds,
  };

  document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    initSidebarCollapse();
    autofillSessionIds();
    document.getElementById("btn-open-actividad")?.addEventListener("click", () => switchTab("equipo"));
    const hash = (location.hash || "").replace(/^#/, "");
    if (hash) switchTab(normalizeTabId(hash));
  });
})();
