/* Auditoría de Instrucciones — login con consentimiento, PIN y API */

(function () {
    let sessionEmail = null;
    let preloginState = null;

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

    const AUDIT_STORAGE_KEYS = [
        'legal-audit-sync-v4',
        'legal-audit-sync-v3',
        'legal-audit-sync-v2',
    ];

    function clearAuditLocalCache() {
        for (const key of AUDIT_STORAGE_KEYS) {
            try {
                localStorage.removeItem(key);
            } catch (_) {
                /* ignore */
            }
        }
    }

    function showGate() {
        document.getElementById('audit-auth-gate')?.classList.remove('gate-hidden');
        document.getElementById('audit-app-root')?.classList.add('app-gated');
        document.body.classList.add('overflow-hidden');
        document.getElementById('audit-auth-logout')?.classList.add('hidden');
    }

    function hideGate() {
        document.getElementById('audit-auth-gate')?.classList.add('gate-hidden');
        document.getElementById('audit-app-root')?.classList.remove('app-gated');
        document.body.classList.remove('overflow-hidden');
        document.getElementById('audit-auth-logout')?.classList.remove('hidden');
    }

    function showError(msg) {
        const el = document.getElementById('audit-auth-error');
        if (!el) return;
        el.textContent = msg;
        el.classList.remove('hidden');
    }

    function hideError() {
        document.getElementById('audit-auth-error')?.classList.add('hidden');
    }

    function setSessionEmail(email) {
        sessionEmail = email || null;
        window.dispatchEvent(
            new CustomEvent('audit-session-ready', { detail: { email: sessionEmail } }),
        );
    }

    window.getAuditSessionEmail = () => sessionEmail;

    function updateExtraFields(state) {
        const pinBlock = document.getElementById('audit-auth-pin-block');
        const newPinBlock = document.getElementById('audit-auth-new-pin-block');
        const consentBlock = document.getElementById('audit-auth-consent-block');
        if (!pinBlock || !newPinBlock || !consentBlock) return;
        const showConsent = state?.needs_consent !== false;
        consentBlock.classList.toggle('hidden', !showConsent);
        newPinBlock.classList.toggle('hidden', !state?.needs_pin_setup);
        pinBlock.classList.toggle('hidden', !state?.needs_pin);
    }

    async function runPrelogin(email, password) {
        const res = await fetchAuditApi('/api/audit/prelogin', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });
        const data = await res.json().catch(() => ({}));
        if (res.status === 429) throw new Error(data.detail || 'Demasiados intentos. Espere unos minutos.');
        if (!res.ok) throw new Error(data.detail || 'Correo o contraseña incorrectos.');
        preloginState = data;
        updateExtraFields(data);
        return data;
    }

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
            const pin = document.getElementById('audit-auth-pin')?.value || '';
            const newPin = document.getElementById('audit-auth-new-pin')?.value || '';
            const acceptPrivacy = document.getElementById('audit-accept-privacy')?.checked;
            const acceptCases = document.getElementById('audit-accept-cases')?.checked;
            const btn = document.getElementById('audit-auth-submit');
            if (!email.trim() || !pass) {
                showError('Ingrese correo y contraseña del despacho.');
                return;
            }
            if (btn) {
                btn.disabled = true;
                btn.textContent = 'Verificando…';
            }
            try {
                if (!preloginState) {
                    await runPrelogin(email, pass);
                }
                const state = preloginState || {};
                if (state.needs_consent && (!acceptPrivacy || !acceptCases)) {
                    showError('Debe aceptar privacidad y autorización de datos de casos.');
                    return;
                }
                if (state.needs_pin_setup && !newPin) {
                    showError('Defina un PIN personal de 6 a 8 dígitos (primera vez).');
                    return;
                }
                if (state.needs_pin && !pin) {
                    showError('Ingrese su PIN personal.');
                    return;
                }
                const res = await fetchAuditApi('/api/audit/login', {
                    method: 'POST',
                    body: JSON.stringify({
                        email,
                        password: pass,
                        pin: pin || null,
                        new_pin: newPin || null,
                        accept_privacy: !!acceptPrivacy,
                        accept_sensitive_data: !!acceptCases,
                    }),
                });
                const data = await res.json().catch(() => ({}));
                if (res.status === 428) {
                    preloginState = { ...state, needs_consent: true, needs_pin_setup: true };
                    updateExtraFields(preloginState);
                    showError(data.detail || 'Complete consentimiento y PIN.');
                    return;
                }
                if (!res.ok) throw new Error(data.detail || 'No se pudo iniciar sesión.');
                setSessionEmail(data.email || email);
                preloginState = null;
                hideGate();
                resolve(true);
            } catch (err) {
                showError(err.message || 'No se pudo conectar con el servidor.');
            } finally {
                if (btn) {
                    btn.disabled = false;
                    btn.textContent = 'Entrar';
                }
            }
        });

    }

    function bindLogoutButton() {
        const btn = document.getElementById('audit-auth-logout');
        if (!btn || btn.dataset.bound === '1') return;
        btn.dataset.bound = '1';
        btn.addEventListener('click', async () => {
            btn.disabled = true;
            try {
                const res = await fetchAuditApi('/api/audit/logout', { method: 'POST' });
                if (!res.ok) {
                    const data = await res.json().catch(() => ({}));
                    throw new Error(data.detail || `HTTP ${res.status}`);
                }
            } catch (err) {
                console.warn('audit logout:', err);
                alert(err.message || 'No se pudo cerrar sesión. Intente de nuevo.');
                btn.disabled = false;
                return;
            }
            setSessionEmail(null);
            preloginState = null;
            clearAuditLocalCache();
            window.dispatchEvent(new CustomEvent('audit-session-ended'));
            showGate();
            location.reload();
        });
    }

    window.__auditAuthPromise = new Promise(resolve => {
        bindLogoutButton();
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
