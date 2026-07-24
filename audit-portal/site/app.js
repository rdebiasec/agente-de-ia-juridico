/* Editor de configuración — prompts / guardrails / skills */

(function () {
    const KIND_LABELS = {
        prompt: 'Prompts',
        guardrail: 'Guardrails',
        skill: 'Skills',
    };

    let catalog = { prompt: [], guardrail: [], skill: [] };
    let currentKind = 'prompt';
    let currentKey = null;
    let loaded = null; // { kind, key, version, content, checksum, ... }
    let dirty = false;
    let sessionReady = false;

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

    function $(id) {
        return document.getElementById(id);
    }

    function toast(msg, ms = 3200) {
        const el = $('cfg-toast');
        if (!el) return;
        el.textContent = msg;
        el.classList.remove('hidden');
        clearTimeout(toast._t);
        toast._t = setTimeout(() => el.classList.add('hidden'), ms);
    }

    function setDirty(value) {
        dirty = Boolean(value);
        const badge = $('cfg-dirty-badge');
        if (badge) badge.classList.toggle('hidden', !dirty);
        const saveBtn = $('cfg-btn-save');
        if (saveBtn) saveBtn.disabled = !loaded || !dirty;
        const editor = $('cfg-editor');
        if (editor) editor.classList.toggle('cfg-dirty', dirty);
    }

    function setKindTabs() {
        document.querySelectorAll('.cfg-kind-tab').forEach((btn) => {
            const active = btn.dataset.kind === currentKind;
            btn.classList.toggle('bg-blue-600', active);
            btn.classList.toggle('text-white', active);
            btn.classList.toggle('hover:bg-slate-800', !active);
        });
    }

    function filteredItems() {
        const q = String($('cfg-search')?.value || '').trim().toLowerCase();
        const items = catalog[currentKind] || [];
        if (!q) return items;
        return items.filter((it) => it.key.toLowerCase().includes(q) || String(it.path || '').toLowerCase().includes(q));
    }

    function renderList() {
        const list = $('cfg-item-list');
        const count = $('cfg-list-count');
        if (!list) return;
        const items = filteredItems();
        if (count) count.textContent = `${items.length} ${KIND_LABELS[currentKind] || 'ítems'}`;
        list.innerHTML = '';
        if (!items.length) {
            list.innerHTML = '<p class="text-xs text-slate-500 px-2 py-4">Sin resultados.</p>';
            return;
        }
        for (const it of items) {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = `cfg-item w-full text-left px-3 py-2.5 rounded-xl border border-slate-800 hover:bg-slate-800 transition-all text-sm ${
                currentKey === it.key ? 'active' : 'bg-slate-950/40'
            }`;
            const ver = it.active_version ? `v${it.active_version}` : 'seed';
            btn.innerHTML = `<div class="font-semibold truncate">${escapeHtml(it.key)}</div>
                <div class="text-[10px] text-slate-400 mt-0.5 flex justify-between gap-2">
                    <span class="truncate">${escapeHtml(it.path || '')}</span>
                    <span>${ver}</span>
                </div>`;
            btn.addEventListener('click', () => selectItem(currentKind, it.key));
            list.appendChild(btn);
        }
    }

    function escapeHtml(s) {
        return String(s || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    async function refreshStatusChip() {
        const chip = $('config-status-chip');
        if (!chip) return;
        try {
            const r = await fetchAuditApi('/api/audit/config/status');
            if (!r.ok) throw new Error('status ' + r.status);
            const data = await r.json();
            const cs = data.config_store || {};
            const by = cs.by_kind || {};
            chip.textContent = `Activos: ${cs.active_items || 0} (P${by.prompt || 0}/G${by.guardrail || 0}/S${by.skill || 0})`;
            const errs = cs.validation_errors || [];
            chip.title = errs.length ? errs.join('; ') : 'Config store OK';
            chip.classList.toggle('text-amber-300', errs.length > 0);
        } catch (e) {
            chip.textContent = 'Config: sin estado';
        }
    }

    async function loadCatalog() {
        const r = await fetchAuditApi('/api/audit/config/catalog');
        if (!r.ok) throw new Error('No se pudo cargar el catálogo');
        const data = await r.json();
        catalog = data.items || { prompt: [], guardrail: [], skill: [] };
        renderList();
        await refreshStatusChip();
    }

    async function selectItem(kind, key) {
        if (dirty && !confirm('Hay cambios sin guardar. ¿Descartarlos?')) return;
        currentKind = kind;
        currentKey = key;
        setKindTabs();
        renderList();
        $('cfg-btn-history').disabled = true;
        $('cfg-btn-reload').disabled = true;
        $('cfg-btn-save').disabled = true;
        $('cfg-editor').disabled = true;
        $('cfg-editor').value = 'Cargando…';
        $('cfg-current-label').textContent = `${KIND_LABELS[kind] || kind} / ${key}`;
        try {
            const r = await fetchAuditApi(`/api/audit/config/${encodeURIComponent(kind)}/${encodeURIComponent(key)}`);
            if (!r.ok) {
                const err = await r.json().catch(() => ({}));
                throw new Error(err.detail || `Error ${r.status}`);
            }
            loaded = await r.json();
            $('cfg-editor').value = loaded.content || '';
            $('cfg-editor').disabled = false;
            $('cfg-btn-history').disabled = false;
            $('cfg-btn-reload').disabled = false;
            $('cfg-note').value = '';
            updateMeta();
            setDirty(false);
        } catch (e) {
            loaded = null;
            $('cfg-editor').value = '';
            toast(String(e.message || e));
        }
    }

    function updateMeta() {
        const meta = $('cfg-meta');
        if (!meta || !loaded) {
            if (meta) meta.textContent = '—';
            return;
        }
        const parts = [
            `v${loaded.version || 0}`,
            loaded.checksum ? `checksum ${loaded.checksum}` : null,
            loaded.source ? `fuente ${loaded.source}` : null,
            loaded.updated_by ? `por ${loaded.updated_by}` : null,
            loaded.updated_at ? loaded.updated_at.replace('T', ' ').slice(0, 19) : null,
            loaded.path || null,
        ].filter(Boolean);
        meta.textContent = parts.join(' · ');
    }

    async function saveCurrent() {
        if (!loaded || !dirty) return;
        const content = $('cfg-editor').value;
        const note = $('cfg-note').value.trim();
        const body = {
            kind: loaded.kind,
            key: loaded.key,
            content,
            expected_version: loaded.version || 0,
            note,
        };
        $('cfg-btn-save').disabled = true;
        try {
            const r = await fetchAuditApi('/api/audit/config/save', {
                method: 'POST',
                body: JSON.stringify(body),
            });
            const data = await r.json().catch(() => ({}));
            if (r.status === 409) {
                toast('Conflicto: alguien guardó antes. Recargue e intente de nuevo.');
                return;
            }
            if (!r.ok) throw new Error(data.detail || `Error ${r.status}`);
            toast(`Guardado ${data.kind}/${data.key} v${data.version}`);
            setDirty(false);
            await loadCatalog();
            await selectItem(data.kind, data.key);
        } catch (e) {
            toast(String(e.message || e));
            setDirty(true);
        }
    }

    function openHistory() {
        $('cfg-history-drawer')?.classList.add('open');
        $('cfg-history-backdrop')?.classList.add('open');
        loadHistory();
    }

    function closeHistory() {
        $('cfg-history-drawer')?.classList.remove('open');
        $('cfg-history-backdrop')?.classList.remove('open');
        $('cfg-diff-panel')?.classList.add('hidden');
    }

    async function loadHistory() {
        if (!loaded) return;
        $('cfg-history-subtitle').textContent = `${loaded.kind}/${loaded.key}`;
        const list = $('cfg-history-list');
        list.innerHTML = '<p class="text-sm text-slate-500">Cargando…</p>';
        try {
            const r = await fetchAuditApi(
                `/api/audit/config/${encodeURIComponent(loaded.kind)}/${encodeURIComponent(loaded.key)}/versions?limit=40`,
            );
            if (!r.ok) throw new Error('No se pudo cargar historial');
            const data = await r.json();
            const versions = data.versions || [];
            if (!versions.length) {
                list.innerHTML = '<p class="text-sm text-slate-500">Sin versiones en DB (aún seed de archivo).</p>';
                return;
            }
            list.innerHTML = '';
            for (const v of versions) {
                const card = document.createElement('div');
                card.className = 'border border-slate-200 rounded-xl p-3 bg-white space-y-2';
                const isActive = v.version === loaded.version;
                card.innerHTML = `
                    <div class="flex items-start justify-between gap-2">
                        <div>
                            <p class="text-sm font-bold">v${v.version}${isActive ? ' <span class="text-emerald-600">(activa)</span>' : ''}</p>
                            <p class="text-[11px] text-slate-500">${escapeHtml(v.author_email || '—')} · ${escapeHtml((v.created_at || '').replace('T', ' ').slice(0, 19))}</p>
                            <p class="text-[11px] text-slate-600 mt-1">${escapeHtml(v.note || '')}</p>
                            <p class="text-[10px] text-slate-400 font-mono">${escapeHtml(v.checksum || '')}</p>
                        </div>
                        <div class="flex flex-col gap-1">
                            <button type="button" class="cfg-diff-btn text-xs px-2 py-1 rounded border border-slate-300 hover:bg-slate-50" data-version="${v.version}">Diff</button>
                            ${
                                isActive
                                    ? ''
                                    : `<button type="button" class="cfg-restore-btn text-xs px-2 py-1 rounded border border-amber-300 bg-amber-50 text-amber-900 hover:bg-amber-100" data-version="${v.version}">Restaurar</button>`
                            }
                        </div>
                    </div>
                    <pre class="text-[11px] text-slate-600 bg-slate-50 rounded-lg p-2 whitespace-pre-wrap max-h-24 overflow-hidden">${escapeHtml(v.content_preview || '')}</pre>`;
                list.appendChild(card);
            }
            list.querySelectorAll('.cfg-restore-btn').forEach((btn) => {
                btn.addEventListener('click', () => restoreVersion(Number(btn.dataset.version)));
            });
            list.querySelectorAll('.cfg-diff-btn').forEach((btn) => {
                btn.addEventListener('click', () => showDiff(Number(btn.dataset.version)));
            });
        } catch (e) {
            list.innerHTML = `<p class="text-sm text-red-600">${escapeHtml(e.message || e)}</p>`;
        }
    }

    async function restoreVersion(version) {
        if (!loaded) return;
        if (!confirm(`¿Restaurar ${loaded.kind}/${loaded.key} desde v${version}? Se creará una nueva versión activa.`)) return;
        try {
            const r = await fetchAuditApi(
                `/api/audit/config/${encodeURIComponent(loaded.kind)}/${encodeURIComponent(loaded.key)}/restore`,
                {
                    method: 'POST',
                    body: JSON.stringify({ version, note: `Restaurado desde v${version} (UI)` }),
                },
            );
            const data = await r.json().catch(() => ({}));
            if (!r.ok) throw new Error(data.detail || `Error ${r.status}`);
            toast(`Restaurado → v${data.version}`);
            setDirty(false);
            closeHistory();
            await loadCatalog();
            await selectItem(data.kind, data.key);
        } catch (e) {
            toast(String(e.message || e));
        }
    }

    function simpleDiff(a, b) {
        const aLines = String(a || '').split('\n');
        const bLines = String(b || '').split('\n');
        const max = Math.max(aLines.length, bLines.length);
        const out = [];
        for (let i = 0; i < max; i += 1) {
            const left = aLines[i];
            const right = bLines[i];
            if (left === right) {
                if (left !== undefined) out.push(`  ${left}`);
            } else {
                if (left !== undefined) out.push(`- ${left}`);
                if (right !== undefined) out.push(`+ ${right}`);
            }
        }
        return out.join('\n');
    }

    async function showDiff(version) {
        if (!loaded) return;
        try {
            const r = await fetchAuditApi(
                `/api/audit/config/${encodeURIComponent(loaded.kind)}/${encodeURIComponent(loaded.key)}/versions/${version}`,
            );
            if (!r.ok) throw new Error('No se pudo cargar la versión');
            const row = await r.json();
            const panel = $('cfg-diff-panel');
            const body = $('cfg-diff-body');
            const diff = simpleDiff(row.content || '', loaded.content || '');
            body.innerHTML = '';
            diff.split('\n').forEach((line) => {
                const div = document.createElement('div');
                if (line.startsWith('+ ')) div.className = 'diff-add';
                else if (line.startsWith('- ')) div.className = 'diff-del';
                div.textContent = line;
                body.appendChild(div);
            });
            panel.classList.remove('hidden');
        } catch (e) {
            toast(String(e.message || e));
        }
    }

    function bindUi() {
        document.querySelectorAll('.cfg-kind-tab').forEach((btn) => {
            btn.addEventListener('click', () => {
                if (dirty && !confirm('Hay cambios sin guardar. ¿Descartarlos?')) return;
                currentKind = btn.dataset.kind;
                currentKey = null;
                loaded = null;
                setDirty(false);
                $('cfg-editor').value = '';
                $('cfg-editor').disabled = true;
                $('cfg-current-label').textContent = 'Seleccione un ítem';
                $('cfg-meta').textContent = '—';
                $('cfg-btn-history').disabled = true;
                $('cfg-btn-reload').disabled = true;
                setKindTabs();
                renderList();
            });
        });
        $('cfg-search')?.addEventListener('input', renderList);
        $('cfg-editor')?.addEventListener('input', () => {
            if (!loaded) return;
            setDirty($('cfg-editor').value !== (loaded.content || ''));
        });
        $('cfg-btn-save')?.addEventListener('click', saveCurrent);
        $('cfg-btn-reload')?.addEventListener('click', () => {
            if (!loaded) return;
            if (dirty && !confirm('¿Descartar cambios y recargar?')) return;
            selectItem(loaded.kind, loaded.key);
        });
        $('cfg-btn-history')?.addEventListener('click', openHistory);
        $('cfg-history-close')?.addEventListener('click', closeHistory);
        $('cfg-history-backdrop')?.addEventListener('click', closeHistory);
        window.addEventListener('beforeunload', (e) => {
            if (!dirty) return;
            e.preventDefault();
            e.returnValue = '';
        });
    }

    async function boot() {
        bindUi();
        setKindTabs();
        if (!sessionReady) return;
        try {
            await loadCatalog();
            const first = (catalog.prompt || [])[0];
            if (first) await selectItem('prompt', first.key);
        } catch (e) {
            toast(String(e.message || e));
        }
    }

    window.addEventListener('audit-session-ready', (ev) => {
        sessionReady = Boolean(ev.detail?.email);
        if (sessionReady) boot();
    });

    // Si la sesión ya estaba lista antes de registrar el listener
    if (window.__AUDIT_SESSION_EMAIL__) {
        sessionReady = true;
        boot();
    }
})();
