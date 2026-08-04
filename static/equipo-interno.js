/** Pestaña Equipo interno — transcript legible Coordinador ↔ especialistas (solo lectura). */
(function () {
  const listEl = () => document.getElementById("equipo-transcript");

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

  function renderEntries(entries) {
    const root = listEl();
    if (!root) return;
    if (!entries.length) {
      root.innerHTML =
        '<p class="equipo-empty">Aún no hay consultas internas en esta sesión. Cuando el Coordinador del Caso delegue a un especialista, el intercambio aparecerá aquí.</p>';
      return;
    }
    root.innerHTML = entries
      .map((e) => {
        const fromL = escapeHtml(e.from_label || e.from_actor || "Coordinador");
        const toL = escapeHtml(e.to_label || e.to_actor || "Especialista");
        const pedido = escapeHtml(e.pedido || "—");
        const respuesta = escapeHtml(e.respuesta || "—");
        const when = escapeHtml(formatWhen(e.created_at));
        return `
          <article class="equipo-turn" data-entry-id="${escapeHtml(e.id || "")}">
            <header class="equipo-turn-head">
              <span class="equipo-route">${fromL} → ${toL}</span>
              <time class="equipo-when">${when}</time>
            </header>
            <p class="equipo-pedido"><span class="equipo-k">Pedido</span> ${pedido}</p>
            <p class="equipo-respuesta"><span class="equipo-k">Retorno</span> ${respuesta}</p>
          </article>`;
      })
      .join("");
  }

  async function refresh() {
    const root = listEl();
    if (!root) return;
    root.setAttribute("aria-busy", "true");
    try {
      const sid = encodeURIComponent(sessionId());
      const res = await authFetch(`/abogado/internal-transcript?session_id=${sid}&limit=100`);
      if (!res.ok) {
        root.innerHTML =
          '<p class="equipo-empty">No se pudo cargar el transcript del equipo interno.</p>';
        return;
      }
      const data = await res.json();
      renderEntries(Array.isArray(data.entries) ? data.entries : []);
    } catch {
      root.innerHTML =
        '<p class="equipo-empty">Error de red al cargar el transcript interno.</p>';
    } finally {
      root.removeAttribute("aria-busy");
    }
  }

  function init() {
    document.getElementById("btn-refresh-equipo")?.addEventListener("click", () => {
      void refresh();
    });
    document.addEventListener("workspace:tab", (ev) => {
      if (ev.detail?.tab === "equipo") void refresh();
    });
  }

  window.EquipoInterno = { refresh, init };
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
