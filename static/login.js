/**
 * Página dedicada /login — sin SPA ni gates ocultos.
 * Permite que Chrome detecte el inicio de sesión y ofrezca guardar la contraseña.
 */
(function () {
  const errorEl = document.getElementById("auth-error");
  const usernameEl = document.getElementById("auth-username");
  const form = document.getElementById("login-form");

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
    } else if (params.get("consent_error") === "1") {
      showError("Debe aceptar el aviso de privacidad y la autorización de datos de casos.");
    }
    if (params.has("login_error") || params.has("expired") || params.has("consent_error")) {
      params.delete("login_error");
      params.delete("expired");
      params.delete("consent_error");
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
        window.location.replace("/abogado");
        return;
      }
    } catch {
      /* login form still works offline from cache */
    }
    usernameEl?.focus();
  }

  document.addEventListener("DOMContentLoaded", bootstrap);

  form?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const privacy = document.getElementById("auth-accept-privacy");
    const cases = document.getElementById("auth-accept-cases");
    const username = document.getElementById("auth-username")?.value?.trim() || "";
    const password = document.getElementById("auth-password")?.value || "";
    if (!privacy?.checked || !cases?.checked) {
      showError("Debe aceptar el aviso de privacidad y la autorización de datos de casos.");
      return;
    }
    if (!username || !password) {
      showError("Ingrese usuario y contraseña.");
      return;
    }
    try {
      const res = await fetch("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        credentials: "include",
        body: JSON.stringify({
          username,
          password,
          accept_privacy: true,
          accept_sensitive_data: true,
        }),
      });
      if (res.status === 428) {
        showError("Debe aceptar el aviso de privacidad y la autorización de datos de casos.");
        return;
      }
      if (res.status === 401) {
        showError("Usuario o contraseña incorrectos.");
        return;
      }
      if (res.status === 429) {
        showError("Demasiados intentos. Espere unos minutos.");
        return;
      }
      if (!res.ok) {
        showError("No se pudo iniciar sesión. Intente de nuevo.");
        return;
      }
      window.location.replace("/abogado");
    } catch {
      showError("Error de red al iniciar sesión.");
    }
  });
})();
