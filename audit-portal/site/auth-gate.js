/* Auditoría de Instrucciones — login correo + contraseña vía API */

(function () {
    let sessionEmail = null;

    function apiConfig() {
        return window.AUDIT_API_CONFIG || { base: '' };
    }

    function apiBase() {
        return String(apiConfig().base || '').replace(/\/$/, '');
    }

    function auditApiUrl(path) {
        const base = apiBase();
        return base ? `${base}${path}` : path;
    }

    async function fetchAuditApi(path, options = {}) {
        const headers = { ...(options.headers || {}) };
        if (options.body && !headers['Content-Type']) {
            headers['Content-Type'] = 'application/json';
        }
        return fetch(auditApiUrl(path), {
            credentials: 'include',
            ...options,
            headers,
        });
    }

    function showGate() {
        const gate = document.getElementById('audit-auth-gate');
        const app = document.getElementById('audit-app-root');
        if (gate) gate.classList.remove('gate-hidden');
        if (app) app.classList.add('app-gated');
        document.body.classList.add('overflow-hidden');
    }

    function hideGate() {
        const gate = document.getElementById('audit-auth-gate');
        const app = document.getElementById('audit-app-root');
        if (gate) gate.classList.add('gate-hidden');
        if (app) app.classList.remove('app-gated');
        document.body.classList.remove('overflow-hidden');
        const logoutBtn = document.getElementById('audit-auth-logout');
        if (logoutBtn) logoutBtn.classList.remove('hidden');
    }

    function showError(msg) {
        const el = document.getElementById('audit-auth-error');
        if (!el) return;
        el.textContent = msg;
        el.classList.remove('hidden');
    }

    function hideError() {
        const el = document.getElementById('audit-auth-error');
        if (el) el.classList.add('hidden');
    }

    function setSessionEmail(email) {
        sessionEmail = email || null;
        window.dispatchEvent(
            new CustomEvent('audit-session-ready', { detail: { email: sessionEmail } }),
        );
    }

    window.getAuditSessionEmail = () => sessionEmail;

    async function checkSession() {
        const res = await fetchAuditApi('/api/audit/session');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        if (!data.auth_enabled) {
            throw new Error('Auditoría no disponible: configure SITE_PASSWORD en el servidor.');
        }
        if (data.authenticated && data.email) {
            setSessionEmail(data.email);
            return true;
        }
        setSessionEmail(null);
        return false;
    }

    async function login(email, password) {
        const res = await fetchAuditApi('/api/audit/login', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });
        if (res.status === 401) return false;
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `Error ${res.status}`);
        }
        const data = await res.json();
        setSessionEmail(data.email || email);
        return true;
    }

    async function logout() {
        try {
            await fetchAuditApi('/api/audit/logout', { method: 'POST' });
        } catch (_) {
            /* ignore */
        }
        setSessionEmail(null);
        showGate();
        location.reload();
    }

    function bindGateForm(resolve) {
        const form = document.getElementById('audit-auth-form');
        if (!form) {
            resolve(true);
            return;
        }
        form.addEventListener('submit', async e => {
            e.preventDefault();
            hideError();
            const email = document.getElementById('audit-auth-email')?.value || '';
            const pass = document.getElementById('audit-auth-password')?.value || '';
            if (!email.trim()) {
                showError('Ingrese su correo electrónico.');
                return;
            }
            if (!pass) {
                showError('Ingrese la contraseña del despacho.');
                return;
            }
            const btn = document.getElementById('audit-auth-submit');
            if (btn) {
                btn.disabled = true;
                btn.textContent = 'Verificando…';
            }
            try {
                const ok = await login(email, pass);
                if (!ok) {
                    showError('Correo o contraseña incorrectos.');
                    return;
                }
                hideGate();
                resolve(true);
            } catch (err) {
                showError(err.message || 'No se pudo conectar con el servidor. Verifique que la API esté activa.');
            } finally {
                if (btn) {
                    btn.disabled = false;
                    btn.textContent = 'Entrar';
                }
            }
        });

        document.getElementById('audit-auth-logout')?.addEventListener('click', () => logout());
    }

    window.__auditAuthPromise = new Promise(resolve => {
        (async () => {
            try {
                const active = await checkSession();
                if (active) {
                    hideGate();
                    resolve(true);
                    return;
                }
                showGate();
                bindGateForm(resolve);
            } catch (err) {
                showGate();
                showError(err.message || 'No se pudo verificar la sesión.');
                bindGateForm(resolve);
            }
        })();
    });

    window.waitForAuditAuth = () => window.__auditAuthPromise;
})();
