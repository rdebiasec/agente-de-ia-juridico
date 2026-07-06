/* Legal Audit Sync — login (auth-config.js generado en build) */

(function () {
    const SESSION_KEY = 'legal-audit-portal-auth';
    const SESSION_HOURS = 8;

    function authConfig() {
        return window.AUDIT_AUTH_CONFIG || { enabled: false };
    }

    function authRequired() {
        return authConfig().enabled === true;
    }

    async function sha256Hex(text) {
        const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
        return Array.from(new Uint8Array(buf))
            .map(b => b.toString(16).padStart(2, '0'))
            .join('');
    }

    function readSession(cfg) {
        try {
            const raw = sessionStorage.getItem(SESSION_KEY);
            if (!raw) return false;
            const data = JSON.parse(raw);
            if (!data.exp || Date.now() > data.exp) return false;
            return data.v === (cfg.passwordHash || '').slice(0, 16);
        } catch (_) {
            return false;
        }
    }

    function writeSession(cfg) {
        const payload = {
            exp: Date.now() + SESSION_HOURS * 3600000,
            v: (cfg.passwordHash || '').slice(0, 16),
        };
        sessionStorage.setItem(SESSION_KEY, JSON.stringify(payload));
    }

    function clearSession() {
        sessionStorage.removeItem(SESSION_KEY);
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

    async function verifyLogin(username, password) {
        const cfg = authConfig();
        const expectedUser = (cfg.username || 'auditor').trim();
        if (username.trim() !== expectedUser) return false;
        const hash = await sha256Hex(password);
        return hash === cfg.passwordHash;
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
            const user = document.getElementById('audit-auth-username')?.value || '';
            const pass = document.getElementById('audit-auth-password')?.value || '';
            if (!pass) {
                showError('Ingrese la contraseña.');
                return;
            }
            const btn = document.getElementById('audit-auth-submit');
            if (btn) {
                btn.disabled = true;
                btn.textContent = 'Verificando…';
            }
            try {
                const ok = await verifyLogin(user, pass);
                if (!ok) {
                    showError('Usuario o contraseña incorrectos.');
                    return;
                }
                writeSession(authConfig());
                hideGate();
                resolve(true);
            } catch (_) {
                showError('No se pudo verificar. Intente de nuevo.');
            } finally {
                if (btn) {
                    btn.disabled = false;
                    btn.textContent = 'Entrar';
                }
            }
        });

        document.getElementById('audit-auth-logout')?.addEventListener('click', () => {
            clearSession();
            showGate();
            location.reload();
        });
    }

    window.__auditAuthPromise = new Promise(resolve => {
        if (!authRequired()) {
            resolve(true);
            return;
        }
        const cfg = authConfig();
        if (readSession(cfg)) {
            hideGate();
            const logoutBtn = document.getElementById('audit-auth-logout');
            if (logoutBtn) logoutBtn.classList.remove('hidden');
            resolve(true);
            return;
        }
        showGate();
        bindGateForm(resolve);
    });

    window.waitForAuditAuth = () => window.__auditAuthPromise;
})();
