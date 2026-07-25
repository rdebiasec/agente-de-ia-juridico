/* Editor de configuración — vista por agente + catálogo secundario */

(function () {
    const KIND_LABELS = {
        prompt: 'Prompts',
        guardrail: 'Guardrails G1–G10',
        skill: 'Skills',
        agent_guardrail: 'Guardrails agente',
    };

    const GROUP_ORDER = ['global', 'coordinacion', 'especialista', 'calidad'];
    const GROUP_LABELS = {
        global: 'Global',
        coordinacion: 'Coordinador',
        especialista: 'Especialistas',
        calidad: 'QA / Calidad',
    };

    let catalog = { prompt: [], guardrail: [], skill: [], agent_guardrail: [] };
    let agentsMeta = { agents: [], groups: {}, global: { prompt_key: 'sistema' } };
    let viewMode = 'agent'; // agent | catalog
    let currentAgentId = 'global'; // 'global' | agent_id
    let currentSection = 'prompt'; // prompt | skills | guardrails
    let currentGuardClass = 'input'; // input | output | tools
    let currentKind = 'prompt';
    let currentKey = null;
    let loaded = null;
    let dirty = false;
    let sessionReady = false;
    let sharedBadgeForKey = null;

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

    function escapeHtml(s) {
        return String(s || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
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

    function agentById(id) {
        return (agentsMeta.agents || []).find((a) => a.id === id) || null;
    }

    function shortName(agent) {
        if (!agent) return '';
        const name = agent.nombre_corto || agent.id;
        return name.length > 28 ? `${name.slice(0, 26)}…` : name;
    }

    function setViewMode(mode) {
        if (dirty && !confirm('Hay cambios sin guardar. ¿Descartarlos?')) return;
        viewMode = mode === 'catalog' ? 'catalog' : 'agent';
        document.body.dataset.view = viewMode;
        document.querySelectorAll('.view-mode-btn').forEach((btn) => {
            const active = btn.dataset.view === viewMode;
            btn.classList.toggle('active', active);
            btn.classList.toggle('text-slate-400', !active);
        });
        setDirty(false);
        loaded = null;
        currentKey = null;
        $('cfg-editor').value = '';
        $('cfg-editor').disabled = true;
        $('cfg-current-label').textContent = 'Seleccione un ítem';
        $('cfg-meta').textContent = '—';
        updateSharedBadge(null);
        $('cfg-btn-history').disabled = true;
        $('cfg-btn-reload').disabled = true;
        renderNav();
    }

    function setSectionTabs() {
        const isGlobal = currentAgentId === 'global';
        document.querySelectorAll('.section-tab').forEach((btn) => {
            const active = btn.dataset.section === currentSection;
            btn.classList.toggle('active', active);
            btn.classList.toggle('hover:bg-slate-800', !active);
            if (isGlobal && btn.dataset.section !== 'prompt') {
                btn.classList.add('opacity-40', 'pointer-events-none');
            } else {
                btn.classList.remove('opacity-40', 'pointer-events-none');
            }
        });
        const guardTabs = $('guard-class-tabs');
        if (guardTabs) {
            guardTabs.classList.toggle('hidden', currentSection !== 'guardrails' || isGlobal);
        }
        document.querySelectorAll('.guard-class-tab').forEach((btn) => {
            const active = btn.dataset.clase === currentGuardClass;
            btn.classList.toggle('active', active);
            btn.classList.toggle('hover:bg-slate-800', !active);
        });
    }

    function setKindTabs() {
        document.querySelectorAll('.cfg-kind-tab').forEach((btn) => {
            const active = btn.dataset.kind === currentKind;
            btn.classList.toggle('active-kind', active);
            btn.classList.toggle('hover:bg-slate-800', !active);
        });
    }

    function renderAgentTabs() {
        const host = $('agent-tabs');
        if (!host) return;
        host.innerHTML = '';

        const addGroup = (groupKey, items) => {
            if (!items.length) return;
            const label = document.createElement('span');
            label.className = 'text-[10px] uppercase tracking-wide text-slate-500 px-1 self-center mr-1';
            label.textContent = GROUP_LABELS[groupKey] || groupKey;
            host.appendChild(label);
            for (const item of items) {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = `agent-tab text-[11px] font-semibold px-2.5 py-1.5 rounded-lg bg-slate-950/60 hover:bg-slate-800 transition-all ${
                    currentAgentId === item.id ? 'active' : ''
                }`;
                btn.dataset.group = item.group;
                btn.dataset.agentId = item.id;
                btn.textContent = item.label;
                btn.title = item.title || item.label;
                btn.addEventListener('click', () => selectAgent(item.id));
                host.appendChild(btn);
            }
        };

        addGroup('global', [{ id: 'global', group: 'global', label: 'Global', title: 'Prompt sistema' }]);

        const byGroup = { coordinacion: [], especialista: [], calidad: [] };
        for (const agent of agentsMeta.agents || []) {
            const g = agent.grupo || 'especialista';
            if (!byGroup[g]) byGroup[g] = [];
            byGroup[g].push({
                id: agent.id,
                group: g,
                label: shortName(agent),
                title: agent.titulo_profesional || agent.nombre_corto || agent.id,
            });
        }
        for (const g of ['coordinacion', 'especialista', 'calidad']) {
            addGroup(g, byGroup[g] || []);
        }
    }

    function catalogItemsForKind(kind) {
        return catalog[kind] || [];
    }

    function agentListItems() {
        if (currentAgentId === 'global') {
            const item = catalogItemsForKind('prompt').find((it) => it.key === 'sistema');
            return item ? [item] : [{ kind: 'prompt', key: 'sistema', path: 'agente/prompts/sistema.md', active_version: 0 }];
        }
        const agent = agentById(currentAgentId);
        if (!agent) return [];

        if (currentSection === 'prompt') {
            const item = catalogItemsForKind('prompt').find((it) => it.key === agent.prompt_key);
            return item
                ? [item]
                : [{ kind: 'prompt', key: agent.prompt_key, path: `agente/prompts/agents/${agent.prompt_key}.md`, active_version: 0 }];
        }
        if (currentSection === 'skills') {
            const q = String($('cfg-search')?.value || '').trim().toLowerCase();
            return (agent.skill_ids || [])
                .map((sid) => {
                    const item = catalogItemsForKind('skill').find((it) => it.key === sid);
                    return item || { kind: 'skill', key: sid, path: `.cursor/skills/${sid}/SKILL.md`, active_version: 0 };
                })
                .filter((it) => !q || it.key.toLowerCase().includes(q));
        }
        // guardrails
        const key = (agent.guardrails || {})[currentGuardClass];
        if (!key) return [];
        const item = catalogItemsForKind('agent_guardrail').find((it) => it.key === key);
        return item
            ? [item]
            : [{ kind: 'agent_guardrail', key, path: `config/guardrails/agents/${currentAgentId}/${currentGuardClass}.md`, active_version: 0 }];
    }

    function filteredCatalogItems() {
        const q = String($('cfg-search')?.value || '').trim().toLowerCase();
        const items = catalogItemsForKind(currentKind);
        if (!q) return items;
        return items.filter((it) => it.key.toLowerCase().includes(q) || String(it.path || '').toLowerCase().includes(q));
    }

    function updateSharedBadge(skillKey) {
        const el = $('cfg-shared-badge');
        if (!el) return;
        sharedBadgeForKey = skillKey;
        if (!skillKey || currentAgentId === 'global') {
            el.classList.add('hidden');
            el.textContent = '';
            return;
        }
        const agent = agentById(currentAgentId);
        const others = (agent && agent.skills_shared_with && agent.skills_shared_with[skillKey]) || [];
        if (!others.length) {
            el.classList.add('hidden');
            el.textContent = '';
            return;
        }
        const names = others.map((id) => {
            const a = agentById(id);
            return a ? a.nombre_corto || id : id;
        });
        el.textContent = `Skill compartida (1 sola fuente). Al guardar cambia también para: ${names.join(', ')}`;
        el.classList.remove('hidden');
    }

    function renderList() {
        const list = $('cfg-item-list');
        const count = $('cfg-list-count');
        if (!list) return;

        const items = viewMode === 'catalog' ? filteredCatalogItems() : agentListItems();
        const label =
            viewMode === 'catalog'
                ? KIND_LABELS[currentKind] || 'ítems'
                : currentSection === 'skills'
                  ? 'skills'
                  : currentSection === 'guardrails'
                    ? `guardrail ${currentGuardClass}`
                    : 'prompt';

        if (count) count.textContent = `${items.length} ${label}`;
        list.innerHTML = '';
        if (!items.length) {
            list.innerHTML = '<p class="text-xs text-slate-500 px-2 py-4">Sin resultados.</p>';
            return;
        }

        for (const it of items) {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = `cfg-item w-full text-left px-3 py-2.5 rounded-xl border border-slate-800 hover:bg-slate-800 transition-all text-sm ${
                currentKey === it.key && loaded && loaded.kind === it.kind ? 'active' : 'bg-slate-950/40'
            }`;
            const ver = it.active_version ? `v${it.active_version}` : 'seed';
            let extra = '';
            if (viewMode === 'agent' && currentSection === 'skills') {
                const agent = agentById(currentAgentId);
                const shared = agent && agent.skills_shared_with && agent.skills_shared_with[it.key];
                if (shared && shared.length) {
                    extra = `<div class="text-[10px] text-amber-300/90 mt-0.5">Compartida · ${shared.length} otro(s)</div>`;
                }
            }
            btn.innerHTML = `<div class="font-semibold truncate">${escapeHtml(it.key)}</div>
                <div class="text-[10px] text-slate-400 mt-0.5 flex justify-between gap-2">
                    <span class="truncate">${escapeHtml(it.path || '')}</span>
                    <span>${ver}</span>
                </div>${extra}`;
            btn.addEventListener('click', () => selectItem(it.kind, it.key));
            list.appendChild(btn);
        }
    }

    function renderNav() {
        setSectionTabs();
        setKindTabs();
        renderList();
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
            chip.textContent = `Activos: ${cs.active_items || 0} (P${by.prompt || 0}/G${by.guardrail || 0}/AG${by.agent_guardrail || 0}/S${by.skill || 0})`;
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
        catalog = data.items || { prompt: [], guardrail: [], skill: [], agent_guardrail: [] };
        renderList();
        await refreshStatusChip();
    }

    async function loadAgents() {
        const r = await fetchAuditApi('/api/audit/config/agents');
        if (!r.ok) throw new Error('No se pudo cargar agentes');
        agentsMeta = await r.json();
        renderAgentTabs();
    }

    async function selectAgent(agentId) {
        if (dirty && !confirm('Hay cambios sin guardar. ¿Descartarlos?')) return;
        currentAgentId = agentId;
        currentSection = 'prompt';
        currentGuardClass = 'input';
        setDirty(false);
        loaded = null;
        currentKey = null;
        $('cfg-editor').value = '';
        $('cfg-editor').disabled = true;
        $('cfg-current-label').textContent = 'Seleccione un ítem';
        $('cfg-meta').textContent = '—';
        updateSharedBadge(null);
        $('cfg-btn-history').disabled = true;
        $('cfg-btn-reload').disabled = true;
        renderAgentTabs();
        renderNav();
        const items = agentListItems();
        if (items.length === 1) {
            await selectItem(items[0].kind, items[0].key);
        }
    }

    async function selectItem(kind, key) {
        if (dirty && !confirm('Hay cambios sin guardar. ¿Descartarlos?')) return;
        currentKind = kind;
        currentKey = key;
        renderNav();
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
            if (kind === 'skill' && viewMode === 'agent') {
                updateSharedBadge(key);
            } else {
                updateSharedBadge(null);
            }
            renderList();
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
                toast('Conflicto: alguien guardó antes. Recargando versión activa…');
                setDirty(false);
                await loadCatalog();
                await selectItem(loaded.kind, loaded.key);
                return;
            }
            if (!r.ok) throw new Error(data.detail || `Error ${r.status}`);
            let msg = `Guardado ${data.kind}/${data.key} v${data.version}`;
            if (data.file_exported === false) {
                msg += ' (DB OK; no se pudo exportar archivo)';
            }
            if (loaded.kind === 'skill' && sharedBadgeForKey) {
                msg += ' · skill compartida actualizada para todos';
            }
            toast(msg);
            setDirty(false);
            await loadCatalog();
            await selectItem(data.kind, data.key);
        } catch (e) {
            toast(String(e.message || e));
            setDirty(true);
        } finally {
            if (dirty && loaded) {
                $('cfg-btn-save').disabled = false;
            }
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
                `/api/audit/config/${encodeURIComponent(loaded.kind)}/${encodeURIComponent(loaded.key)}/versions?limit=100`,
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
                            <button type="button" class="cfg-diff-btn text-xs px-2 py-1 rounded border border-slate-300 hover:bg-slate-50" data-version="${v.version}">Diff vs activa</button>
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
            const legend = document.createElement('p');
            legend.className = 'text-[11px] text-slate-500 mb-2';
            legend.textContent = `Diff: v${version} (antigua, líneas −) vs activa v${loaded.version} (líneas +)`;
            body.appendChild(legend);
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
        document.querySelectorAll('.view-mode-btn').forEach((btn) => {
            btn.addEventListener('click', () => setViewMode(btn.dataset.view));
        });

        document.querySelectorAll('.section-tab').forEach((btn) => {
            btn.addEventListener('click', async () => {
                if (dirty && !confirm('Hay cambios sin guardar. ¿Descartarlos?')) return;
                currentSection = btn.dataset.section;
                setDirty(false);
                loaded = null;
                currentKey = null;
                $('cfg-editor').value = '';
                $('cfg-editor').disabled = true;
                $('cfg-current-label').textContent = 'Seleccione un ítem';
                $('cfg-meta').textContent = '—';
                updateSharedBadge(null);
                $('cfg-btn-history').disabled = true;
                $('cfg-btn-reload').disabled = true;
                renderNav();
                const items = agentListItems();
                if (items.length === 1 || (currentSection === 'guardrails' && items.length)) {
                    await selectItem(items[0].kind, items[0].key);
                }
            });
        });

        document.querySelectorAll('.guard-class-tab').forEach((btn) => {
            btn.addEventListener('click', async () => {
                if (dirty && !confirm('Hay cambios sin guardar. ¿Descartarlos?')) return;
                currentGuardClass = btn.dataset.clase;
                setDirty(false);
                renderNav();
                const items = agentListItems();
                if (items[0]) await selectItem(items[0].kind, items[0].key);
            });
        });

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
                updateSharedBadge(null);
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
        document.addEventListener('keydown', (e) => {
            if (!(e.metaKey || e.ctrlKey) || String(e.key).toLowerCase() !== 's') return;
            if (!loaded || !dirty) return;
            e.preventDefault();
            saveCurrent();
        });
        window.addEventListener('beforeunload', (e) => {
            if (!dirty) return;
            e.preventDefault();
            e.returnValue = '';
        });
    }

    async function boot() {
        bindUi();
        document.body.dataset.view = 'agent';
        if (!sessionReady) return;
        try {
            await Promise.all([loadCatalog(), loadAgents()]);
            const firstAgent = (agentsMeta.agents || []).find((a) => a.grupo === 'coordinacion');
            if (firstAgent) {
                await selectAgent(firstAgent.id);
            } else {
                await selectAgent('global');
            }
        } catch (e) {
            toast(String(e.message || e));
        }
    }

    window.addEventListener('audit-session-ready', (ev) => {
        sessionReady = Boolean(ev.detail?.email);
        if (sessionReady) boot();
    });

    if (window.__AUDIT_SESSION_EMAIL__) {
        sessionReady = true;
        boot();
    }
})();
