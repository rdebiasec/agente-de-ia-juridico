/**
 * Sesión en la app — login en /login (página dedicada para el llavero de Chrome).
 */
const AgentAuth = (() => {
  function debugClientLog(hypothesisId, location, message, data = {}) {
    // region agent log
    fetch("/debug/client-log", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        runId: "post-fix",
        hypothesisId,
        location,
        message,
        data: { ...data, ua: navigator.userAgent.slice(0, 160) },
      }),
    }).catch(() => {});
    // endregion
  }

  const IDLE_MS_DEFAULT = 30 * 60 * 1000;
  let idleMs = IDLE_MS_DEFAULT;
  let idleTimer = null;
  let onLogoutCallback = null;
  let isLoggingOut = false;
  let activityHandler = null;

  function redirectToLogin(reason = "") {
    clearIdleTimer();
    const url = reason === "expired" ? "/login?expired=1" : "/login";
    window.location.replace(url);
  }

  function authFetch(url, options = {}) {
    return fetch(url, { credentials: "include", ...options }).then(async (res) => {
      const isMobile = /iPhone|iPad|Android|Mobile/i.test(navigator.userAgent);
      if (res.status >= 400) {
        debugClientLog("H4", "auth.js:authFetch", "api_error", {
          url: String(url),
          status: res.status,
          mobile: isMobile,
        });
      }
      if (res.status === 401 && !String(url).includes("/auth/")) {
        redirectToLogin("expired");
        throw new Error("Unauthorized");
      }
      return res;
    });
  }

  function showApp() {
    const err = document.getElementById("auth-error");
    if (err) err.hidden = true;
    resetIdleTimer();
  }

  function clearIdleTimer() {
    if (idleTimer) {
      clearTimeout(idleTimer);
      idleTimer = null;
    }
  }

  function resetIdleTimer() {
    clearIdleTimer();
    idleTimer = setTimeout(() => {
      logout(true);
    }, idleMs);
  }

  function bindActivityListeners() {
    const events = ["mousedown", "keydown", "scroll", "touchstart"];
    let lastPing = 0;
    activityHandler = () => {
      if (isLoggingOut) return;
      resetIdleTimer();
      const now = Date.now();
      if (now - lastPing > 60_000) {
        lastPing = now;
        authFetch("/auth/heartbeat", { method: "POST" }).catch(() => {});
      }
    };
    events.forEach((ev) => window.addEventListener(ev, activityHandler, { passive: true }));
  }

  function unbindActivityListeners() {
    if (!activityHandler) return;
    const events = ["mousedown", "keydown", "scroll", "touchstart"];
    events.forEach((ev) => window.removeEventListener(ev, activityHandler));
    activityHandler = null;
  }

  async function checkStatus() {
    const isMobile = /iPhone|iPad|Android|Mobile/i.test(navigator.userAgent);
    try {
      const res = await fetch("/auth/status", { credentials: "include" });
      if (res.status >= 500) {
        debugClientLog("H6", "auth.js:checkStatus", "server_error", {
          status: res.status,
          mobile: isMobile,
        });
        return { auth_enabled: true, authenticated: false, server_error: true };
      }
      if (!res.ok) {
        return { auth_enabled: false, authenticated: true };
      }
      return res.json();
    } catch {
      debugClientLog("H6", "auth.js:checkStatus", "network_error", { mobile: isMobile });
      return { auth_enabled: true, authenticated: false, server_error: true };
    }
  }

  function showServerWaking() {
    const statusText = document.getElementById("status-text");
    if (statusText) {
      statusText.textContent = "Servicio iniciando… recargue en unos segundos.";
    }
  }

  async function logout(sessionExpired = false) {
    isLoggingOut = true;
    unbindActivityListeners();
    clearIdleTimer();
    await fetch("/auth/logout", { method: "POST", credentials: "include" }).catch(() => {});
    if (onLogoutCallback) onLogoutCallback();
    redirectToLogin(sessionExpired ? "expired" : "");
  }

  function initForm() {
    const logoutBtn = document.getElementById("auth-logout-btn");
    logoutBtn?.addEventListener("click", () => logout(false));
  }

  async function bootstrap() {
    const isMobile = /iPhone|iPad|Android|Mobile/i.test(navigator.userAgent);
    debugClientLog("H5", "auth.js:bootstrap", "auth_bootstrap_start", {
      mobile: isMobile,
      path: window.location.pathname,
    });
    initForm();
    bindActivityListeners();

    const status = await checkStatus();
    if (status.idle_minutes) idleMs = status.idle_minutes * 60 * 1000;

    if (status.server_error) {
      showServerWaking();
      debugClientLog("H6", "auth.js:bootstrap", "server_waking", { mobile: isMobile });
      return;
    }

    if (!status.auth_enabled) {
      updateSessionBadge(status);
      showApp();
      window.__agentAuthed = true;
      window.bootAgentApp?.();
      return;
    }

    if (status.authenticated) {
      updateSessionBadge(status);
      showApp();
      window.__agentAuthed = true;
      window.bootAgentApp?.();
      return;
    }

    debugClientLog("H5", "auth.js:bootstrap", "auth_redirect_login", { mobile: isMobile });
    redirectToLogin("");
  }

  function updateSessionBadge(status) {
    const badge = document.getElementById("session-user-badge");
    if (!badge) return;
    if (!status.auth_enabled || !status.authenticated) {
      badge.hidden = true;
      return;
    }
    const user = status.username || "usuario";
    const mins = status.idle_minutes || 30;
    badge.hidden = false;
    badge.textContent = `${user} · sesión ${mins} min`;
    badge.title = `Sesión activa. Cierre automático tras ${mins} min de inactividad.`;
  }

  function onLogout(fn) {
    onLogoutCallback = fn;
  }

  return { bootstrap, authFetch, logout, redirectToLogin };
})();

window.authFetch = AgentAuth.authFetch;

document.addEventListener("DOMContentLoaded", () => {
  window.addEventListener("error", (event) => {
    debugClientLog("H4", "window:onerror", event.message || "script_error", {
      mobile: /iPhone|iPad|Android|Mobile/i.test(navigator.userAgent),
      source: event.filename || "",
      line: event.lineno || 0,
    });
  });
  window.addEventListener("unhandledrejection", (event) => {
    const reason =
      event.reason instanceof Error ? event.reason.message : String(event.reason || "rejection");
    debugClientLog("H4", "window:unhandledrejection", reason.slice(0, 200), {
      mobile: /iPhone|iPad|Android|Mobile/i.test(navigator.userAgent),
    });
  });
  AgentAuth.bootstrap();
});
