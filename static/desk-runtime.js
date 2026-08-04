/**
 * Utilidades compartidas del escritorio del abogado.
 * Mantiene helpers de sesión, eventos y polling sin mezclar dominio.
 */
(() => {
  "use strict";

  function esc(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function getUserId() {
    if (typeof window.getChatUserId === "function") {
      return window.getChatUserId();
    }
    return localStorage.getItem("agente-juridico-user-id") || "web";
  }

  function getSessionId() {
    return `web:${getUserId()}`;
  }

  function emit(eventName, detail) {
    try {
      document.dispatchEvent(new CustomEvent(eventName, { detail }));
    } catch {
      /* ignore event dispatch failures */
    }
  }

  function on(eventName, handler) {
    document.addEventListener(eventName, handler);
    return () => document.removeEventListener(eventName, handler);
  }

  function isTabActive(tabId) {
    const panel = document.getElementById(`tab-${tabId}`);
    return Boolean(panel && !panel.hidden && panel.classList.contains("is-active"));
  }

  function createTabPoller({ tabId, intervalMs, run }) {
    let timer = null;
    let busy = false;

    function shouldRun() {
      return document.visibilityState !== "hidden" && isTabActive(tabId);
    }

    async function tick({ force = false } = {}) {
      if (busy) return;
      if (!force && !shouldRun()) return;
      busy = true;
      try {
        await run({ force });
      } finally {
        busy = false;
      }
    }

    function start({ immediate = true } = {}) {
      stop();
      if (immediate) void tick({ force: true });
      timer = setInterval(() => {
        void tick();
      }, Math.max(1000, Number(intervalMs) || 3000));
    }

    function stop() {
      if (!timer) return;
      clearInterval(timer);
      timer = null;
    }

    return {
      start,
      stop,
      tick,
      isRunning: () => Boolean(timer),
    };
  }

  window.DeskRuntime = {
    esc,
    getUserId,
    getSessionId,
    emit,
    on,
    isTabActive,
    createTabPoller,
  };
})();
