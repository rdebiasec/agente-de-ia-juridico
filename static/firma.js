/**
 * Panel de la Firma: bandeja HITL de borradores, subida con ingesta RAG,
 * búsqueda semántica y términos procesales. Vanilla JS sobre window.authFetch.
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

  const panel = $("firma-panel");
  if (!panel) return;

  // ---------- abrir / cerrar ----------
  function openPanel() {
    panel.hidden = false;
    panel.scrollIntoView({ behavior: "smooth", block: "start" });
    loadBandeja();
    loadTerminos();
  }
  function closePanel() {
    panel.hidden = true;
  }
  $("btn-open-firma")?.addEventListener("click", openPanel);
  $("btn-close-firma")?.addEventListener("click", closePanel);

  // ---------- bandeja de borradores ----------
  async function loadBandeja() {
    const list = $("firma-bandeja-list");
    list.innerHTML = '<p class="firma-muted">Cargando…</p>';
    try {
      const res = await api("/drafts/pendientes");
      const data = await res.json();
      const drafts = data.drafts || [];
      if (!drafts.length) {
        list.innerHTML = '<p class="firma-muted">No hay borradores pendientes.</p>';
        return;
      }
      list.innerHTML = drafts.map(renderDraft).join("");
      bindDraftActions();
    } catch {
      list.innerHTML = '<p class="firma-error">No se pudo cargar la bandeja.</p>';
    }
  }

  function renderDraft(d) {
    const preview = esc((d.contenido || "").slice(0, 400));
    return `
      <div class="firma-draft" data-id="${esc(d.id)}">
        <div class="firma-draft-head">
          <span class="firma-badge">${esc(d.tipo)}</span>
          <strong>${esc(d.titulo || d.tipo)}</strong>
          <span class="firma-state firma-state--${esc(d.estado)}">${esc(d.estado)}</span>
        </div>
        <pre class="firma-draft-body">${preview}${(d.contenido || "").length > 400 ? "…" : ""}</pre>
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

  function bindDraftActions() {
    document.querySelectorAll("#firma-bandeja-list [data-act]").forEach((btn) => {
      btn.addEventListener("click", () => handleDraftAction(btn.dataset.act, btn.dataset.id, btn));
    });
  }

  async function handleDraftAction(act, id, btn) {
    if (act === "toggle-edit") {
      const ta = document.querySelector(`textarea.firma-edit[data-id="${id}"]`);
      const save = document.querySelector(`[data-act="save-edit"][data-id="${id}"]`);
      if (ta) ta.hidden = !ta.hidden;
      if (save) save.hidden = !save.hidden;
      return;
    }
    try {
      if (act === "approve") {
        await api(`/drafts/${id}/approve`, jsonBody({ revisor: "abogado" }));
        toast("Borrador aprobado.", "success");
      } else if (act === "reject") {
        const comentario = prompt("Motivo del rechazo:") || "Rechazado";
        await api(`/drafts/${id}/reject`, jsonBody({ revisor: "abogado", comentario }));
        toast("Borrador rechazado.", "info");
      } else if (act === "save-edit") {
        const ta = document.querySelector(`textarea.firma-edit[data-id="${id}"]`);
        await api(`/drafts/${id}/edit`, jsonBody({ revisor: "abogado", contenido: ta ? ta.value : "" }));
        toast("Edición guardada y aprobada.", "success");
      }
      loadBandeja();
    } catch {
      toast("No se pudo completar la acción.", "error");
    }
  }

  // ---------- subida + ingesta ----------
  $("firma-upload-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
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
      out.innerHTML = `<p class="firma-ok">Extraídos ${esc(data.caracteres)} caracteres · ${esc(
        data.fragmentos_indexados
      )} fragmentos indexados.</p>`;
    } catch (err) {
      out.innerHTML = `<p class="firma-error">${esc(err.message || "No se pudo procesar el archivo.")}</p>`;
    }
  });

  // ---------- búsqueda RAG ----------
  $("firma-search-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
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
        : '<p class="firma-muted">Sin resultados. ¿Indexaste la base con /rag/ingest-kb?</p>';
    } catch {
      out.innerHTML = '<p class="firma-error">No se pudo buscar.</p>';
    }
  });

  // ---------- términos ----------
  async function loadTerminos() {
    const list = $("firma-terminos-list");
    list.innerHTML = '<p class="firma-muted">Cargando…</p>';
    try {
      const res = await api("/deadlines");
      const data = await res.json();
      const items = data.deadlines || [];
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
    return `<div class="firma-term firma-term--${esc(d.estado)}">
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
      loadTerminos();
      toast("Término creado.", "success");
    } catch {
      toast("No se pudo crear el término.", "error");
    }
  });

  // ---------- helpers ----------
  function jsonHeaders() {
    return { "Content-Type": "application/json" };
  }
  function jsonBody(obj) {
    return { method: "POST", headers: jsonHeaders(), body: JSON.stringify(obj) };
  }

  $("btn-refresh-bandeja")?.addEventListener("click", loadBandeja);
  $("btn-refresh-terminos")?.addEventListener("click", loadTerminos);

  // Cuando el chat genera un borrador, refrescar la bandeja (sin abrir el panel).
  document.addEventListener("draft-created", () => {
    if (!panel.hidden) loadBandeja();
  });
})();
