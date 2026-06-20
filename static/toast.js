/**
 * Toasts no intrusivos — reemplazo de alert() en flujos de validación.
 */
const Toast = (() => {
  let container = null;

  function ensureContainer() {
    if (container) return container;
    container = document.getElementById("toast-container");
    if (!container) {
      container = document.createElement("div");
      container.id = "toast-container";
      container.className = "toast-container";
      container.setAttribute("aria-live", "polite");
      document.body.appendChild(container);
    }
    return container;
  }

  function show(message, type = "info", durationMs = 4500) {
    const root = ensureContainer();
    const el = document.createElement("div");
    el.className = `toast toast--${type}`;
    el.textContent = message;
    root.appendChild(el);
    requestAnimationFrame(() => el.classList.add("is-visible"));
    setTimeout(() => {
      el.classList.remove("is-visible");
      setTimeout(() => el.remove(), 300);
    }, durationMs);
  }

  return { show };
})();
