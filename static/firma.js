/**
 * Bandeja HITL, plazos, RAG y drawer del abogado.
 */
(() => {
  "use strict";

  const api = (url, options) => (window.authFetch ? window.authFetch(url, options) : fetch(url, options));
  const $ = (id) => document.getElementById(id);
  const esc = (s) =>
    String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  const toast = (msg, type = "info") => {
    if (typeof Toast !== "undefined" && Toast.show) Toast.show(msg, type);
  };

  const drawer = $("firma-drawer");
  if (!drawer) return;

  const originals = new Map();

  function sessionId() {
    return window.Workspace?.getSessionId?.() || "";
  }

  function autofillIds() {
    window.Workspace?.autofillSessionIds?.();
  }

  function openDrawer() {
    window.Workspace?.openDrawer?.();
    loadBandeja();
    loadTerminos();
    autofillIds();
  }

  function closeDrawer() {
    window.Workspace?.closeDrawer?.();
  }

  $("btn-open-firma")?.addEventListener("click", openDrawer);
  $("btn-close-firma")?.addEventListener("click", closeDrawer);

  function simpleDiff(original, edited) {
    const oLines = String(original || "").split("\n");
    const eLines = String(edited || "").split("\n");
    const max = Math.max(oLines.length, eLines.length);
    const rows = [];
    for (let i = 0; i < max; i += 1) {
      const o = oLines[i];
      const e = eLines[i];
      if (o === e) {
        if (o != null) rows.push(`<div class="diff-line diff-line--same">${esc(o)}</div>`);
      } else {
        if (o != null) rows.push(`<div class="diff-line diff-line--removed">− ${esc(o)}</div>`);
        if (e != null) rows.push(`<div class="diff-line diff-line--added">+ ${esc(e)}</div>`);
      }
    }
    return rows.join("") || '<p class="firma-muted">Sin cambios respecto al borrador original.</p>';
  }

  function renderDraft(d, { compact = false } = {}) {
    if (!originals.has(d.id)) originals.set(d.id, d.contenido || "");
    const original = originals.get(d.id);
    const preview = esc((d.contenido || "").slice(0, compact ? 280 : 600));
    const showDiff = d.contenido !== original;
    return `
      <div class="firma-draft" data-id="${esc(d.id)}">
        <div class="firma-draft-head">
          <span class="firma-badge">${esc(d.tipo)}</span>
          <strong>${esc(d.titulo || d.tipo)}</strong>
          <span class="firma-state firma-state--${esc(d.estado)}">${esc(d.estado)}</span>
        </div>
        <pre class="firma-draft-body">${preview}${(d.contenido || "").length > (compact ? 280 : 600) ? "…" : ""}</pre>
        ${showDiff ? `<details class="draft-diff"><summary>Ver cambios respecto al borrador de la IA</summary><div class="draft-diff-body">${simpleDiff(original, d.contenido)}</div></details>` : ""}
        <textarea class="firma-edit" data-id="${esc(d.id)}" hidden>${esc(d.contenido)}</textarea>
        <div class="firma-draft-actions">
          <button type="button" class="btn-firma-primary" data-act="approve" data-id="${esc(d.id)}">Aprobar</button>
          <button type="button" class="btn-firma-action" data-act="toggle-edit" data-id="${esc(d.id)}">Editar</button>
          <button type="button" class="btn-firma-action" data-act="save-edit" data-id="${esc(d.id)}" hidden>Guardar edición</button>
          <button type="button" class="btn-firma-danger" data-act="reject" data-id="${esc(d.id)}">Rechazar</button>
          <a class="btn-firma-link" href="/drafts/${esc(d.id)}/docx">.docx</a>
          <a class="btn-firma-link" href="/drafts/${esc(d.id)}/pdf">.pdf</a>
        </div>
      </div>`;
  }

  function bindDraftActions(root) {
    root.querySelectorAll("[data-act]").forEach((btn) => {
      btn.addEventListener("click", () => handleDraftAction(btn.dataset.act, btn.dataset.id));
    });
  }

  async function fetchPendingDrafts() {
    const res = await api("/drafts/pendientes");
    const data = await res.json();
    return data.drafts || [];
  }

  function renderDraftLists(drafts) {
    const drawerList = $("firma-bandeja-list");
    const tabList = $("tab-borrador-list");
    const empty = '<p class="firma-muted">No hay borradores pendientes.</p>';
    const html = drafts.length ? drafts.map((d) => renderDraft(d)).join("") : empty;
    const tabHtml = drafts.length
      ? drafts.slice(0, 2).map((d) => renderDraft(d, { compact: true })).join("")
      : '<p class="firma-muted">Sin borradores. Pida al asistente que redacte un documento.</p>';
    if (drawerList) {
      drawerList.innerHTML = html;
      bindDraftActions(drawerList);
    }
    if (tabList) {
      tabList.innerHTML = tabHtml;
      bindDraftActions(tabList);
    }
    window.Workspace?.updateBandejaBadge?.(drafts.length);
  }

  async function loadBandeja() {
    const drawerList = $("firma-bandeja-list");
    const tabList = $("tab-borrador-list");
    if (drawerList) drawerList.innerHTML = '<p class="firma-muted">Cargando…</p>';
    if (tabList) tabList.innerHTML = '<p class="firma-muted">Cargando…</p>';
    try {
      const drafts = await fetchPendingDrafts();
      renderDraftLists(drafts);
    } catch {
      const err = '<p class="firma-error">No se pudo cargar la bandeja.</p>';
      if (drawerList) drawerList.innerHTML = err;
      if (tabList) tabList.innerHTML = err;
    }
  }

  async function handleDraftAction(act, id) {
    if (act === "toggle-edit") {
      const ta = document.querySelector(`textarea.firma-edit[data-id="${id}"]`);
      const save = document.querySelector(`[data-act="save-edit"][data-id="${id}"]`);
      if (ta) ta.hidden = !ta.hidden;
      if (save) save.hidden = !save.hidden;
      return;
    }
    try {
      if (act === "approve") {
        const res = await api(`/drafts/${id}/approve`, jsonBody({ revisor: "abogado" }));
        const data = await res.json();
        if (data.termino_creado) {
          toast(`Borrador aprobado. Término creado: ${data.termino_creado.descripcion}`, "success");
          window.Workspace?.addHito?.("Tutela aprobada — término 10 días");
          window.Workspace?.smartTab?.("plazos");
          loadTerminos();
        } else {
          toast("Borrador aprobado.", "success");
        }
        window.Workspace?.addHito?.("Borrador aprobado");
      } else if (act === "reject") {
        const comentario = prompt("Motivo del rechazo:") || "Rechazado";
        await api(`/drafts/${id}/reject`, jsonBody({ revisor: "abogado", comentario }));
        toast("Borrador rechazado.", "info");
      } else if (act === "save-edit") {
        const ta = document.querySelector(`textarea.firma-edit[data-id="${id}"]`);
        await api(`/drafts/${id}/edit`, jsonBody({ revisor: "abogado", contenido: ta ? ta.value : "" }));
        toast("Edición guardada.", "success");
        window.Workspace?.addHito?.("Borrador editado por abogado");
      }
      loadBandeja();
    } catch {
      toast("No se pudo completar la acción.", "error");
    }
  }

  $("firma-upload-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    autofillIds();
    const fileInput = $("firma-file");
    const out = $("firma-upload-result");
    if (!fileInput.files.length) return;
    const fd = new FormData();
    fd.append("file", fileInput.files[0]);
    fd.append("expediente_id", $("firma-exp-id").value.trim());
    fd.append("ingestar", $("firma-ingest").checked ? "true" : "false");
    out.innerHTML = '<p class="firma-muted">Procesando…</p>';
    try {
      const res = await api("/documents/extract", { method: "POST", body: fd });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "error");
      out.innerHTML = `<p class="firma-ok">Extraídos ${esc(data.caracteres)} caracteres · ${esc(data.fragmentos_indexados)} fragmentos indexados.</p>`;
      window.Workspace?.addHito?.(`Documento indexado: ${fileInput.files[0].name}`);
    } catch (err) {
      out.innerHTML = `<p class="firma-error">${esc(err.message || "No se pudo procesar el archivo.")}</p>`;
    }
  });

  $("firma-search-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    autofillIds();
    const out = $("firma-search-result");
    out.innerHTML = '<p class="firma-muted">Buscando…</p>';
    try {
      const res = await api(
        "/rag/search",
        jsonBody({
          consulta: $("firma-search-q").value.trim(),
          incluir_kb: $("firma-search-kb").checked,
          expediente_id: $("firma-search-exp").value.trim() || null,
          k: 5,
        })
      );
      const data = await res.json();
      const r = data.resultados || [];
      out.innerHTML = r.length
        ? r
            .map(
              (c) =>
                `<div class="firma-hit"><span class="firma-badge">${esc(c.fuente || c.scope)}</span>
                 <span class="firma-score">${c.score != null ? c.score.toFixed(3) : ""}</span>
                 <p>${esc((c.chunk_text || "").slice(0, 300))}…</p></div>`
            )
            .join("")
        : '<p class="firma-muted">Sin resultados.</p>';
    } catch {
      out.innerHTML = '<p class="firma-error">No se pudo buscar.</p>';
    }
  });

  async function loadTerminos() {
    const list = $("firma-terminos-list");
    if (!list) return;
    list.innerHTML = '<p class="firma-muted">Cargando…</p>';
    try {
      const sid = sessionId();
      const url = sid ? `/deadlines?session_id=${encodeURIComponent(sid)}` : "/deadlines";
      const res = await api(url);
      const data = await res.json();
      const items = data.deadlines || [];
      window.Workspace?.updateDeadlineChip?.(items);
      list.innerHTML = items.length
        ? items.map(renderTermino).join("")
        : '<p class="firma-muted">No hay términos registrados.</p>';
      list.querySelectorAll('[data-act="cumplir"]').forEach((btn) => {
        btn.addEventListener("click", () => marcarCumplido(btn.dataset.id));
      });
    } catch {
      list.innerHTML = '<p class="firma-error">No se pudieron cargar los términos.</p>';
    }
  }

  function renderTermino(d) {
    const urgente = d.tipo === "tutela" ? " firma-term--urgente" : "";
    return `<div class="firma-term firma-term--${esc(d.estado)}${urgente}">
      <div><strong>${esc(d.descripcion)}</strong> <span class="firma-badge">${esc(d.tipo)}</span></div>
      <div class="firma-muted">Límite: ${esc(d.fecha_limite || "-")} · ${esc(d.estado)}</div>
      ${d.estado === "pendiente" ? `<button type="button" class="btn-firma-action" data-act="cumplir" data-id="${esc(d.id)}">Marcar cumplido</button>` : ""}
    </div>`;
  }

  async function marcarCumplido(id) {
    try {
      await api(`/deadlines/${id}`, { method: "PATCH", headers: jsonHeaders(), body: JSON.stringify({ estado: "cumplido" }) });
      loadTerminos();
    } catch {
      toast("No se pudo actualizar el término.", "error");
    }
  }

  $("firma-term-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    autofillIds();
    try {
      await api(
        "/deadlines",
        jsonBody({
          session_id: $("firma-term-exp").value.trim(),
          descripcion: $("firma-term-desc").value.trim(),
          dias_habiles: parseInt($("firma-term-dias").value, 10),
        })
      );
      $("firma-term-form").reset();
      autofillIds();
      loadTerminos();
      toast("Término creado.", "success");
    } catch {
      toast("No se pudo crear el término.", "error");
    }
  });

  function jsonHeaders() {
    return { "Content-Type": "application/json" };
  }
  function jsonBody(obj) {
    return { method: "POST", headers: jsonHeaders(), body: JSON.stringify(obj) };
  }

  $("btn-refresh-bandeja")?.addEventListener("click", loadBandeja);
  $("btn-refresh-borrador-tab")?.addEventListener("click", loadBandeja);
  $("btn-refresh-terminos")?.addEventListener("click", loadTerminos);

  document.addEventListener("draft-created", () => {
    loadBandeja();
    window.Workspace?.smartTab?.("borrador");
    window.Workspace?.addHito?.("Borrador enviado a bandeja");
  });

  window.FirmaPanel = { loadBandeja, loadTerminos, fetchPendingDrafts };

  document.addEventListener("DOMContentLoaded", () => {
    autofillIds();
    loadBandeja();
    loadTerminos();
  });
})();
