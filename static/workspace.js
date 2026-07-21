/**
 * Mesa de trabajo del abogado: expediente, tabs contextuales, chips de header.
 */
(() => {
  "use strict";

  const esc = (s) =>
    String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");

  let expedienteState = null;
  let hitos = [];

  function getSessionId() {
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

  function setExpediente(exp) {
    expedienteState = exp || null;
    renderExpedienteFields(expedienteState);
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

  function switchTab(tabId) {
    document.querySelectorAll(".context-tab").forEach((btn) => {
      const active = btn.dataset.tab === tabId;
      btn.classList.toggle("is-active", active);
      btn.setAttribute("aria-selected", String(active));
    });
    document.querySelectorAll(".context-tab-panel").forEach((panel) => {
      const active = panel.dataset.panel === tabId;
      panel.classList.toggle("is-active", active);
      panel.hidden = !active;
    });
  }

  function smartTab(reason) {
    if (reason === "borrador" || reason === "draft") switchTab("borrador");
    else if (reason === "plazos" || reason === "deadline") switchTab("plazos");
    else if (reason === "trazas" || reason === "trace") switchTab("trazas");
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
    document.querySelectorAll(".context-tab").forEach((btn) => {
      btn.addEventListener("click", () => switchTab(btn.dataset.tab));
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
    if (next.tipo === "tutela") chip.classList.add("workspace-deadline-chip--tutela");
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

  function openDrawer() {
    document.getElementById("firma-drawer")?.removeAttribute("hidden");
    document.getElementById("firma-drawer-backdrop")?.removeAttribute("hidden");
    document.body.classList.add("drawer-open");
  }

  function closeDrawer() {
    document.getElementById("firma-drawer")?.setAttribute("hidden", "");
    document.getElementById("firma-drawer-backdrop")?.setAttribute("hidden", "");
    document.body.classList.remove("drawer-open");
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
  });
})();
