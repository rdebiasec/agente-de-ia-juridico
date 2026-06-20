/**
 * Página dedicada /login — sin SPA ni gates ocultos.
 * Permite que Chrome detecte el inicio de sesión y ofrezca guardar la contraseña.
 */
(function () {
  const errorEl = document.getElementById("auth-error");
  const usernameEl = document.getElementById("auth-username");

  function showError(message) {
    if (!errorEl || !message) return;
    errorEl.hidden = false;
    errorEl.textContent = message;
  }

  function consumeQueryMessages() {
    const params = new URLSearchParams(window.location.search);
    if (params.get("login_error") === "1") {
      showError("Usuario o contraseña incorrectos.");
    } else if (params.get("expired") === "1") {
      showError("Su sesión expiró por inactividad. Ingrese de nuevo.");
    }
    if (params.has("login_error") || params.has("expired")) {
      params.delete("login_error");
      params.delete("expired");
      const qs = params.toString();
      const next = qs ? `${window.location.pathname}?${qs}` : window.location.pathname;
      history.replaceState(null, "", next);
    }
  }

  async function bootstrap() {
    consumeQueryMessages();
    try {
      const res = await fetch("/auth/status", { credentials: "include" });
      if (!res.ok) return;
      const data = await res.json();
      if (!data.auth_enabled || data.authenticated) {
        window.location.replace("/");
        return;
      }
    } catch {
      /* login form still works offline from cache */
    }
    usernameEl?.focus();
  }

  document.addEventListener("DOMContentLoaded", bootstrap);
})();
