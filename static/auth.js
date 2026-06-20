/**
 * Sesión en la app — login en /login (página dedicada para el llavero de Chrome).
 */
const AgentAuth = (() => {
  const IDLE_MS_DEFAULT = 30 * 60 * 1000;
  let idleMs = IDLE_MS_DEFAULT;
  let idleTimer = null;
  let onLogoutCallback = null;

  function redirectToLogin(reason = "") {
    clearIdleTimer();
    const url = reason === "expired" ? "/login?expired=1" : "/login";
    window.location.replace(url);
  }

  function authFetch(url, options = {}) {
    return fetch(url, { credentials: "include", ...options }).then(async (res) => {
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
    const onActivity = () => {
      resetIdleTimer();
      const now = Date.now();
      if (now - lastPing > 60_000) {
        lastPing = now;
        authFetch("/auth/heartbeat", { method: "POST" }).catch(() => {});
      }
    };
    events.forEach((ev) => window.addEventListener(ev, onActivity, { passive: true }));
  }

  async function checkStatus() {
    const res = await fetch("/auth/status", { credentials: "include" });
    if (!res.ok) return { auth_enabled: false, authenticated: true };
    return res.json();
  }

  async function logout(sessionExpired = false) {
    await fetch("/auth/logout", { method: "POST", credentials: "include" }).catch(() => {});
    if (onLogoutCallback) onLogoutCallback();
    redirectToLogin(sessionExpired ? "expired" : "");
  }

  function initForm() {
    const logoutBtn = document.getElementById("auth-logout-btn");
    logoutBtn?.addEventListener("click", () => logout(false));
  }

  async function bootstrap() {
    initForm();
    bindActivityListeners();

    const status = await checkStatus();
    if (status.idle_minutes) idleMs = status.idle_minutes * 60 * 1000;

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
  AgentAuth.bootstrap();
});
