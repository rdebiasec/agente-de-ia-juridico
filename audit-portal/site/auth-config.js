/* Auth del portal: gate real = auth-gate.js + /api/audit/* (SITE_PASSWORD en el servidor).
   enabled:false solo desactiva el login legado estático; no abre el portal sin API. */
window.AUDIT_AUTH_CONFIG = { enabled: false, mode: "api" };
