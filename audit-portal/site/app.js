/* Legal Audit Sync v2 — auditoría por paso */

const STORAGE_KEY = 'legal-audit-sync-v2';

const GROUP_LABELS = {
    coordinacion: 'Coordinación',
    especialista: 'Especialistas',
    calidad: 'Control de calidad',
};

let catalog = {
    guardrails: [], agentes: [], skills: [], categorias: [],
    generated_at: '', totals: {}, intro: {},
};
let auditLog = { guardrails: {}, agentes: {}, pasos: {}, custom: null };
let currentModalTarget = null;
let currentAddTarget = null;
let groupByCategory = true;

function ensureCustom() {
    if (!auditLog.custom) {
        auditLog.custom = {
            guardrailsRemoved: [],
            guardrailsAdded: [],
            pasosRemoved: [],
            pasosAdded: {},
        };
    }
    return auditLog.custom;
}

function getEffectiveGuardrails() {
    const custom = ensureCustom();
    const base = catalog.guardrails.filter(g => !custom.guardrailsRemoved.includes(g.id));
    return [...base, ...custom.guardrailsAdded];
}

function getEffectiveSteps(skill) {
    const custom = ensureCustom();
    const sid = skill.id;
    const added = custom.pasosAdded[sid] || [];
    const base = (skill.steps || []).filter(
        st => !custom.pasosRemoved.includes(pasoKey(sid, st.num)),
    );
    const merged = [
        ...base.map(st => ({
            key: pasoKey(sid, st.num),
            text: st.text,
            custom: false,
        })),
        ...added.map(st => ({
            key: pasoKey(sid, st.id),
            text: st.text,
            custom: true,
        })),
    ];
    merged.forEach((st, i) => { st.displayNum = i + 1; });
    return merged;
}

function countEffectivePasos() {
    let n = 0;
    catalog.skills.forEach(s => { n += getEffectiveSteps(s).length; });
    return n;
}

function countEffectiveItems() {
    return getEffectiveGuardrails().length + catalog.agentes.length + countEffectivePasos();
}

function escapeHtml(text) {
    const d = document.createElement('div');
    d.textContent = text ?? '';
    return d.innerHTML;
}

function pasoKey(skillId, num) {
    return `${skillId}::${num}`;
}

function loadAuditLog() {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (!raw) return;
        const parsed = JSON.parse(raw);
        if (parsed.guardrails) auditLog.guardrails = parsed.guardrails;
        if (parsed.agentes) auditLog.agentes = parsed.agentes;
        if (parsed.pasos) auditLog.pasos = parsed.pasos;
        if (parsed.custom) auditLog.custom = parsed.custom;
    } catch (_) { /* ignore */ }
}

function saveAuditLog() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(auditLog));
}

function defaultDecision() {
    return { status: 'PENDIENTE', reason: '', solution: '' };
}

function getDecision(type, id) {
    if (!auditLog[type]) auditLog[type] = {};
    if (!auditLog[type][id]) auditLog[type][id] = defaultDecision();
    return auditLog[type][id];
}

function isReviewed(state) {
    return state.status === 'APROBADO' || state.status === 'AJUSTAR';
}

function cardBorderClass(status) {
    if (status === 'APROBADO') return 'border-emerald-300 bg-emerald-50/30';
    if (status === 'AJUSTAR') return 'border-amber-300 bg-amber-50/30';
    return 'border-slate-200';
}

function btnClass(active, kind) {
    const base = 'px-3 py-1.5 rounded-lg text-[10px] md:text-xs font-bold tracking-wide transition-all border ';
    if (active && kind === 'approve') return base + 'bg-emerald-600 border-emerald-600 text-white shadow-sm';
    if (active && kind === 'adjust') return base + 'bg-amber-500 border-amber-500 text-white shadow-sm';
    if (active && kind === 'pending') return base + 'bg-slate-500 border-slate-500 text-white shadow-sm';
    return base + 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50';
}

function renderAdjustmentBlock(reason, solution) {
    if (!reason) return '';
    return `
        <div class="mt-3 p-3 bg-red-50/60 rounded-xl border border-red-100 text-xs text-red-800 space-y-1">
            <p class="font-bold text-[10px] uppercase text-red-600"><i class="fa-solid fa-gavel mr-1"></i> Dictamen de ajuste</p>
            <p><strong>Razón:</strong> ${escapeHtml(reason)}</p>
            <p><strong>Solución:</strong> ${escapeHtml(solution)}</p>
        </div>`;
}

function bindDecisionButtons(container, type, id) {
    container.querySelector('[data-action="approve"]')?.addEventListener('click', () => setDecision(type, id, 'APROBADO'));
    container.querySelector('[data-action="adjust"]')?.addEventListener('click', () => triggerAdjustment(type, id));
    container.querySelector('[data-action="pending"]')?.addEventListener('click', () => setDecision(type, id, 'PENDIENTE'));
}

function buildDecisionButtons(type, id) {
    const current = getDecision(type, id);
    return `
        <div class="flex flex-wrap items-center gap-1.5 shrink-0">
            <button type="button" data-action="approve" class="${btnClass(current.status === 'APROBADO', 'approve')}"><i class="fa-solid fa-check mr-0.5"></i> APROBAR</button>
            <button type="button" data-action="adjust" class="${btnClass(current.status === 'AJUSTAR', 'adjust')}"><i class="fa-solid fa-pen mr-0.5"></i> AJUSTAR</button>
            <button type="button" data-action="pending" class="${btnClass(current.status === 'PENDIENTE', 'pending')}"><i class="fa-solid fa-rotate-left mr-0.5"></i> RESTABLECER</button>
        </div>`;
}

function btnDeleteClass() {
    return 'px-2 py-1 rounded-lg text-[10px] font-semibold border border-red-200 text-red-600 bg-white hover:bg-red-50 transition-all';
}

function buildGuardrailCard(item) {
    const current = getDecision('guardrails', item.id);
    const card = document.createElement('div');
    card.className = `audit-card bg-white p-5 md:p-6 rounded-2xl border transition-all ${cardBorderClass(current.status)}`;
    card.dataset.type = 'guardrails';
    card.dataset.id = item.id;
    card.dataset.search = [item.name, item.desc].filter(Boolean).join(' ').toLowerCase();

    const customBadge = item.custom
        ? '<span class="text-[10px] font-bold uppercase bg-blue-100 text-blue-700 px-2 py-0.5 rounded">Agregada por abogada</span>'
        : '';

    card.innerHTML = `
        <div class="flex flex-col md:flex-row md:items-start justify-between gap-4">
            <div class="space-y-1 flex-1 min-w-0">
                <div class="flex flex-wrap items-center gap-2">
                    <h4 class="font-bold text-slate-950 text-sm md:text-base">${escapeHtml(item.name)}</h4>
                    ${customBadge}
                </div>
                <p class="text-sm text-slate-600">${escapeHtml(item.desc)}</p>
            </div>
            <div class="flex flex-col items-end gap-2 shrink-0">
                ${buildDecisionButtons('guardrails', item.id)}
                <button type="button" data-action="delete-guardrail" data-guardrail-id="${escapeHtml(item.id)}" class="${btnDeleteClass()}">
                    <i class="fa-solid fa-trash-can mr-0.5"></i> Eliminar
                </button>
            </div>
        </div>
        ${renderAdjustmentBlock(current.reason, current.solution)}`;

    bindDecisionButtons(card, 'guardrails', item.id);
    card.querySelector('[data-action="delete-guardrail"]')?.addEventListener('click', () => {
        if (confirm('¿Eliminar esta regla estricta de la auditoría?')) removeGuardrail(item.id);
    });
    return card;
}

function buildSimpleCard(type, item) {
    const current = getDecision(type, item.id);
    const card = document.createElement('div');
    card.className = `audit-card bg-white p-5 md:p-6 rounded-2xl border transition-all ${cardBorderClass(current.status)}`;
    card.dataset.type = type;
    card.dataset.id = item.id;
    card.dataset.search = [item.name, item.desc, item.nombre_corto].filter(Boolean).join(' ').toLowerCase();

    card.innerHTML = `
        <div class="flex flex-col md:flex-row md:items-start justify-between gap-4">
            <div class="space-y-1 flex-1 min-w-0">
                <h4 class="font-bold text-slate-950 text-sm md:text-base">${escapeHtml(item.name)}</h4>
                ${item.nombre_corto ? `<p class="text-xs text-slate-500">${escapeHtml(item.nombre_corto)}</p>` : ''}
                <p class="text-sm text-slate-600">${escapeHtml(item.desc)}</p>
            </div>
            ${buildDecisionButtons(type, item.id)}
        </div>
        ${renderAdjustmentBlock(current.reason, current.solution)}`;

    bindDecisionButtons(card, type, item.id);
    return card;
}

function buildPasoCardsHtml(skill, options = {}) {
    const { showAddButton = true } = options;
    const steps = getEffectiveSteps(skill);

    const cards = steps.map(st => {
        const d = getDecision('pasos', st.key);
        const customBadge = st.custom
            ? '<span class="text-[10px] font-bold uppercase bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded ml-1">Nuevo</span>'
            : '';
        return `
            <div class="paso-card audit-card p-4 rounded-xl border ${cardBorderClass(d.status)} mt-2" data-paso-id="${escapeHtml(st.key)}" data-skill-id="${escapeHtml(skill.id)}">
                <div class="flex flex-col md:flex-row md:items-start justify-between gap-3">
                    <div class="flex-1">
                        <p class="text-[10px] font-bold uppercase text-slate-400 mb-1">Paso ${st.displayNum}${customBadge}</p>
                        <p class="text-sm text-slate-700">${escapeHtml(st.text)}</p>
                    </div>
                    <div class="flex flex-col items-end gap-2 shrink-0">
                        ${buildDecisionButtons('pasos', st.key)}
                        <button type="button" data-action="delete-paso" data-paso-key="${escapeHtml(st.key)}" data-skill-id="${escapeHtml(skill.id)}" class="${btnDeleteClass()}">
                            <i class="fa-solid fa-trash-can mr-0.5"></i> Eliminar
                        </button>
                    </div>
                </div>
                ${renderAdjustmentBlock(d.reason, d.solution)}
            </div>`;
    }).join('');

    const emptyMsg = steps.length
        ? ''
        : '<p class="text-xs text-slate-400 mb-2">Sin pasos definidos. Agregue uno si lo requiere.</p>';

    const addBtn = showAddButton
        ? `<button type="button" data-action="add-paso" data-skill-id="${escapeHtml(skill.id)}" class="mt-3 w-full md:w-auto px-4 py-2 rounded-xl text-xs font-semibold border border-dashed border-blue-300 text-blue-700 hover:bg-blue-50 transition-all">
                <i class="fa-solid fa-plus mr-1"></i> Agregar paso
           </button>`
        : '';

    return `${emptyMsg}${cards}${addBtn}`;
}

function bindPasoCardsIn(container) {
    container.querySelectorAll('.paso-card').forEach(pasoEl => {
        bindDecisionButtons(pasoEl, 'pasos', pasoEl.dataset.pasoId);
        pasoEl.querySelector('[data-action="delete-paso"]')?.addEventListener('click', () => {
            if (confirm('¿Eliminar este paso de la auditoría?')) {
                removePaso(pasoEl.dataset.pasoKey, pasoEl.dataset.skillId);
            }
        });
    });
    container.querySelectorAll('[data-action="add-paso"]').forEach(btn => {
        btn.addEventListener('click', () => openAddPasoModal(btn.dataset.skillId));
    });
}

function buildAgentSkillsPanel(agent) {
    const skillIds = agent.skill_ids || [];
    if (!skillIds.length) return '';

    const byId = Object.fromEntries(catalog.skills.map(s => [s.id, s]));
    const items = skillIds.map(sid => byId[sid]).filter(Boolean);

    const skillBlocks = items.map(skill => {
        const prog = skillStepProgress(skill);
        let badgeClass = 'bg-slate-100 text-slate-600';
        if (prog.reviewed === prog.total && prog.total > 0) badgeClass = 'bg-emerald-100 text-emerald-700';
        else if (prog.adjust > 0) badgeClass = 'bg-amber-100 text-amber-800';

        return `
            <details class="agent-skill-details bg-white border border-slate-200 rounded-xl overflow-hidden">
                <summary class="cursor-pointer px-4 py-3 flex flex-wrap items-center gap-2 select-none hover:bg-slate-50 list-none">
                    <i class="fa-solid fa-chevron-right text-[10px] text-slate-400 agent-skill-chevron transition-transform"></i>
                    <code class="text-xs font-mono text-slate-800 font-semibold">${escapeHtml(skill.name)}</code>
                    <span class="text-[10px] font-semibold px-2 py-0.5 rounded ${badgeClass}">${prog.reviewed}/${prog.total} pasos</span>
                    <span class="text-[10px] text-slate-400 truncate max-w-full">${escapeHtml(skill.category)}</span>
                </summary>
                <div class="px-4 pb-4 border-t border-slate-100 pt-3">
                    ${skill.instruccion ? `<p class="text-xs text-blue-700 mb-2"><strong>Instrucción tipo:</strong> ${escapeHtml(skill.instruccion)}</p>` : ''}
                    ${skill.desc ? `<p class="text-xs text-slate-600 mb-3">${escapeHtml(skill.desc)}</p>` : ''}
                    ${buildPasoCardsHtml(skill)}
                </div>
            </details>`;
    }).join('');

    const missing = skillIds.filter(sid => !byId[sid]);
    const missingHtml = missing.map(sid =>
        `<p class="text-xs text-red-600">⚠ <code>${escapeHtml(sid)}</code> — no encontrado en catálogo</p>`
    ).join('');

    return `
        <details class="agent-skills-details mt-2 border border-slate-200 rounded-xl bg-slate-50/80 overflow-hidden">
            <summary class="cursor-pointer px-4 py-3 text-sm font-medium text-blue-700 hover:bg-slate-100 select-none list-none flex items-center gap-2">
                <i class="fa-solid fa-chevron-right text-[10px] text-blue-500 agent-panel-chevron transition-transform"></i>
                Ver skills de este agente (${skillIds.length})
            </summary>
            <div class="px-4 pb-4 space-y-2 border-t border-slate-200 pt-3">
                ${missingHtml}
                ${skillBlocks}
            </div>
        </details>`;
}

function buildAgentCard(agent) {
    const current = getDecision('agentes', agent.id);
    const card = document.createElement('div');
    card.className = `audit-card bg-white p-5 md:p-6 rounded-2xl border transition-all ${cardBorderClass(current.status)}`;
    card.dataset.type = 'agentes';
    card.dataset.id = agent.id;
    card.dataset.search = [agent.name, agent.nombre_corto, agent.desc, agent.problema].filter(Boolean).join(' ').toLowerCase();

    card.innerHTML = `
        <div class="flex flex-col gap-4">
            <div class="flex flex-col md:flex-row md:items-start justify-between gap-4">
                <div class="space-y-2 flex-1">
                    <h4 class="font-bold text-slate-950 font-mono text-sm">${escapeHtml(agent.name)}</h4>
                    <p class="text-sm font-medium text-purple-700">${escapeHtml(agent.nombre_corto)}</p>
                    <p class="text-sm text-slate-600">${escapeHtml(agent.desc)}</p>
                    <p class="text-xs text-slate-500"><strong>Problema que resuelve:</strong> ${escapeHtml(agent.problema || '—')}</p>
                    <p class="text-xs text-slate-500"><strong>No reemplaza:</strong> ${escapeHtml(agent.no_reemplaza || '—')}</p>
                    <p class="text-xs text-slate-400">${agent.skills_count || 0} skills asignados</p>
                </div>
                ${buildDecisionButtons('agentes', agent.id)}
            </div>
            ${buildAgentSkillsPanel(agent)}
            ${renderAdjustmentBlock(current.reason, current.solution)}
        </div>`;

    bindDecisionButtons(card, 'agentes', agent.id);
    bindPasoCardsIn(card);
    return card;
}

function skillStepProgress(skill) {
    const steps = getEffectiveSteps(skill);
    let reviewed = 0;
    let adjust = 0;
    steps.forEach(st => {
        const d = getDecision('pasos', st.key);
        if (isReviewed(d)) reviewed += 1;
        if (d.status === 'AJUSTAR') adjust += 1;
    });
    return { total: steps.length, reviewed, adjust };
}

function buildSkillCard(skill) {
    const prog = skillStepProgress(skill);
    const card = document.createElement('div');
    card.className = 'skill-card bg-white p-5 md:p-6 rounded-2xl border border-slate-200 transition-all';
    card.dataset.type = 'skills';
    card.dataset.id = skill.id;
    card.dataset.category = skill.category || '';
    card.dataset.agents = (skill.agents || []).join(',');
    card.dataset.search = [skill.name, skill.desc, skill.instruccion, skill.category, ...(skill.agents || [])].filter(Boolean).join(' ').toLowerCase();

    let badgeClass = 'bg-slate-100 text-slate-600';
    if (prog.reviewed === prog.total && prog.total > 0) badgeClass = 'bg-emerald-100 text-emerald-700';
    else if (prog.adjust > 0) badgeClass = 'bg-amber-100 text-amber-800';

    const stepsHtml = buildPasoCardsHtml(skill);

    card.innerHTML = `
        <div class="space-y-2 mb-3">
            <div class="flex flex-wrap items-center gap-2">
                <span class="text-xs font-semibold bg-slate-100 text-slate-600 px-2 py-0.5 rounded">${escapeHtml(skill.category)}</span>
                <span class="text-xs font-semibold px-2 py-0.5 rounded ${badgeClass}">${prog.reviewed}/${prog.total} pasos revisados</span>
            </div>
            <h4 class="font-bold text-slate-950 font-mono text-sm break-all">${escapeHtml(skill.name)}</h4>
            ${skill.instruccion ? `<p class="text-xs text-blue-700"><strong>Instrucción tipo:</strong> ${escapeHtml(skill.instruccion)}</p>` : ''}
            <p class="text-sm text-slate-600">${escapeHtml(skill.desc)}</p>
            ${skill.agents?.length ? `<p class="text-xs text-slate-400">Agentes: ${skill.agents.map(a => `<code class="text-[10px]">${escapeHtml(a)}</code>`).join(', ')}</p>` : ''}
            ${skill.steps_missing ? '<p class="text-xs text-red-600 font-medium">⚠ Pasos pendientes de definir en catálogo</p>' : ''}
        </div>
        <div class="border-t border-slate-100 pt-2">${stepsHtml}</div>`;

    bindPasoCardsIn(card);

    return card;
}

function renderGuardrails() {
    const c = document.getElementById('container-guardrails');
    c.innerHTML = '';
    getEffectiveGuardrails().forEach(g => c.appendChild(buildGuardrailCard(g)));
    const addWrap = document.createElement('div');
    addWrap.className = 'mt-2';
    addWrap.innerHTML = `
        <button type="button" id="btn-add-guardrail" class="w-full md:w-auto px-4 py-2.5 rounded-xl text-sm font-semibold border border-dashed border-blue-400 text-blue-700 hover:bg-blue-50 transition-all">
            <i class="fa-solid fa-plus mr-1"></i> Agregar regla estricta
        </button>`;
    c.appendChild(addWrap);
    document.getElementById('btn-add-guardrail')?.addEventListener('click', openAddGuardrailModal);
}

function renderAgentes() {
    const c = document.getElementById('container-agentes');
    c.innerHTML = '';
    const order = ['coordinacion', 'especialista', 'calidad'];
    order.forEach(grupo => {
        const agents = catalog.agentes.filter(a => a.grupo === grupo);
        if (!agents.length) return;
        const block = document.createElement('div');
        block.className = 'mb-8 space-y-3';
        block.innerHTML = `
            <h4 class="text-sm font-bold uppercase tracking-wider text-purple-700 border-b border-purple-100 pb-2">
                ${escapeHtml(GROUP_LABELS[grupo] || grupo)} (${agents.length})
            </h4>
            <div class="grid gap-4 agent-group-grid"></div>`;
        const grid = block.querySelector('.agent-group-grid');
        agents.forEach(a => grid.appendChild(buildAgentCard(a)));
        c.appendChild(block);
    });
}

function renderSkills() {
    const c = document.getElementById('container-skills');
    c.innerHTML = '';
    const items = [...catalog.skills];

    const renderList = list => {
        const grid = document.createElement('div');
        grid.className = 'grid gap-4';
        list.forEach(s => grid.appendChild(buildSkillCard(s)));
        return grid;
    };

    if (groupByCategory) {
        const byCat = {};
        items.forEach(s => {
            const cat = s.category || 'Sin categoría';
            if (!byCat[cat]) byCat[cat] = [];
            byCat[cat].push(s);
        });
        Object.keys(byCat).sort().forEach(cat => {
            const catMeta = (catalog.categorias || []).find(x => x.name === cat);
            const block = document.createElement('div');
            block.className = 'mb-8 space-y-3';
            block.dataset.skillGroup = cat;
            block.innerHTML = `
                <div class="border-b border-slate-200 pb-2 scroll-mt-24">
                    <h4 class="text-sm font-bold uppercase tracking-wider text-slate-600">${escapeHtml(cat)} (${byCat[cat].length} skills)</h4>
                    ${catMeta?.desc ? `<p class="text-xs text-slate-500 mt-1">${escapeHtml(catMeta.desc)}</p>` : ''}
                </div>`;
            block.appendChild(renderList(byCat[cat]));
            c.appendChild(block);
        });
    } else {
        c.appendChild(renderList(items));
    }
}

function applyFilters() {
    const q = (document.getElementById('search-input').value || '').trim().toLowerCase();
    const catFilter = document.getElementById('filter-category').value;
    const agentFilter = document.getElementById('filter-agent').value;

    document.querySelectorAll('.audit-card').forEach(card => {
        if (card.classList.contains('paso-card')) return;
        const type = card.dataset.type;
        let visible = true;
        if (q && !(card.dataset.search || '').includes(q)) visible = false;
        if (type === 'skills' || card.closest('.skill-card')) {
            const skillCard = card.classList.contains('skill-card') ? card : card.closest('.skill-card');
            if (skillCard) {
                if (catFilter && skillCard.dataset.category !== catFilter) visible = false;
                if (agentFilter) {
                    const agents = (skillCard.dataset.agents || '').split(',').filter(Boolean);
                    if (!agents.includes(agentFilter)) visible = false;
                }
                if (q && !(skillCard.dataset.search || '').includes(q)) visible = false;
            }
        }
        if (card.classList.contains('skill-card')) {
            /* visibility set above */
        } else if (type !== 'skills') {
            /* guardrails, agentes */
        }
        card.classList.toggle('hidden', !visible);
    });

    document.querySelectorAll('.skill-card').forEach(sc => {
        const q = (document.getElementById('search-input').value || '').trim().toLowerCase();
        const catFilter = document.getElementById('filter-category').value;
        const agentFilter = document.getElementById('filter-agent').value;
        let visible = true;
        if (q && !(sc.dataset.search || '').includes(q)) visible = false;
        if (catFilter && sc.dataset.category !== catFilter) visible = false;
        if (agentFilter) {
            const agents = (sc.dataset.agents || '').split(',').filter(Boolean);
            if (!agents.includes(agentFilter)) visible = false;
        }
        sc.classList.toggle('hidden', !visible);
    });

    document.querySelectorAll('[data-skill-group]').forEach(group => {
        const cards = group.querySelectorAll('.skill-card');
        const anyVisible = [...cards].some(c => !c.classList.contains('hidden'));
        group.classList.toggle('hidden', !anyVisible);
    });
}

function populateFilters() {
    const catSel = document.getElementById('filter-category');
    const agentSel = document.getElementById('filter-agent');
    (catalog.categorias || []).forEach(cat => {
        const o = document.createElement('option');
        o.value = cat.name;
        o.textContent = cat.name;
        catSel.appendChild(o);
    });
    const agents = [...new Set(catalog.skills.flatMap(s => s.agents || []))].sort();
    agents.forEach(a => {
        const o = document.createElement('option');
        o.value = a;
        o.textContent = a;
        agentSel.appendChild(o);
    });
}

function renderGuiaCategorias() {
    const el = document.getElementById('guia-categorias');
    const intro = document.getElementById('guia-intro-text');
    if (intro && catalog.intro) {
        const gr = getEffectiveGuardrails().length;
        const pas = countEffectivePasos();
        const total = countEffectiveItems();
        intro.textContent = `Audite ${gr} reglas estrictas, ${catalog.intro.agentes} agentes y ${pas} pasos operativos (${catalog.intro.skills} skills). Total: ${total} ítems.`;
    }
    if (!el) return;
    el.innerHTML = (catalog.categorias || []).map(cat => `
        <div class="bg-slate-50 p-2 rounded-lg border border-slate-100">
            <strong class="text-slate-700">${escapeHtml(cat.name)}</strong>
            <span class="text-slate-500"> — ${escapeHtml(cat.desc)}</span>
        </div>`).join('');
}

function updateProgress() {
    let reviewed = 0;
    const total = countEffectiveItems();

    getEffectiveGuardrails().forEach(g => {
        if (isReviewed(getDecision('guardrails', g.id))) reviewed += 1;
    });
    catalog.agentes.forEach(a => {
        if (isReviewed(getDecision('agentes', a.id))) reviewed += 1;
    });
    catalog.skills.forEach(s => {
        getEffectiveSteps(s).forEach(st => {
            if (isReviewed(getDecision('pasos', st.key))) reviewed += 1;
        });
    });

    const countSection = (type, items, getId) => {
        let secRev = 0;
        items.forEach(item => {
            if (isReviewed(getDecision(type, getId(item)))) secRev += 1;
        });
        return { pending: items.length - secRev, total: items.length };
    };

    const g = countSection('guardrails', getEffectiveGuardrails(), x => x.id);
    const ag = countSection('agentes', catalog.agentes, x => x.id);

    let pasosPending = 0;
    catalog.skills.forEach(s => {
        getEffectiveSteps(s).forEach(st => {
            if (!isReviewed(getDecision('pasos', st.key))) pasosPending += 1;
        });
    });

    const setBadge = (id, pending) => {
        const badge = document.getElementById(id);
        if (!badge) return;
        badge.textContent = pending ? `${pending} pend.` : '✓';
        badge.className = `ml-auto text-[10px] px-1.5 py-0.5 rounded ${pending ? 'bg-amber-900/50 text-amber-300' : 'bg-emerald-900/50 text-emerald-300'}`;
    };
    setBadge('badge-guardrails', g.pending);
    setBadge('badge-agentes', ag.pending);
    setBadge('badge-pasos', pasosPending);

    const chip = document.getElementById('progress-chip');
    if (chip) {
        chip.innerHTML = `<i class="fa-solid fa-chart-pie mr-1 text-blue-400"></i> <strong>${reviewed}</strong> / ${total} revisados`;
    }
}

function renderAll() {
    renderGuardrails();
    renderAgentes();
    renderSkills();
    applyFilters();
    updateProgress();
    saveAuditLog();
}

function removeGuardrail(id) {
    const custom = ensureCustom();
    const isCustom = custom.guardrailsAdded.some(g => g.id === id);
    if (isCustom) {
        custom.guardrailsAdded = custom.guardrailsAdded.filter(g => g.id !== id);
    } else if (!custom.guardrailsRemoved.includes(id)) {
        custom.guardrailsRemoved.push(id);
    }
    delete auditLog.guardrails[id];
    renderAll();
}

function addGuardrail(name, desc) {
    const custom = ensureCustom();
    const id = `custom_g_${Date.now()}`;
    custom.guardrailsAdded.push({ id, name, desc, custom: true });
    renderAll();
}

function removePaso(pasoKeyVal, skillId) {
    const custom = ensureCustom();
    const added = custom.pasosAdded[skillId] || [];
    const customId = pasoKeyVal.split('::')[1];
    const isCustom = added.some(st => st.id === customId);
    if (isCustom) {
        custom.pasosAdded[skillId] = added.filter(st => st.id !== customId);
        if (!custom.pasosAdded[skillId].length) delete custom.pasosAdded[skillId];
    } else if (!custom.pasosRemoved.includes(pasoKeyVal)) {
        custom.pasosRemoved.push(pasoKeyVal);
    }
    delete auditLog.pasos[pasoKeyVal];
    renderAll();
}

function addPaso(skillId, text) {
    const custom = ensureCustom();
    if (!custom.pasosAdded[skillId]) custom.pasosAdded[skillId] = [];
    const id = `c${Date.now()}`;
    custom.pasosAdded[skillId].push({ id, text });
    renderAll();
}

function openAddGuardrailModal() {
    currentAddTarget = { kind: 'guardrail' };
    document.getElementById('addModalTitle').textContent = 'Agregar regla estricta';
    document.getElementById('addFieldNameWrap').classList.remove('hidden');
    document.getElementById('addFieldName').value = '';
    document.getElementById('addFieldDesc').value = '';
    document.getElementById('addFieldDescLabel').textContent = 'Descripción de la regla';
    document.getElementById('addModal').classList.remove('opacity-0', 'pointer-events-none');
    document.getElementById('addModalBox').classList.remove('scale-95');
}

function openAddPasoModal(skillId) {
    currentAddTarget = { kind: 'paso', skillId };
    document.getElementById('addModalTitle').textContent = 'Agregar paso al skill';
    document.getElementById('addFieldNameWrap').classList.add('hidden');
    document.getElementById('addFieldDesc').value = '';
    document.getElementById('addFieldDescLabel').textContent = 'Texto del paso operativo';
    document.getElementById('addModal').classList.remove('opacity-0', 'pointer-events-none');
    document.getElementById('addModalBox').classList.remove('scale-95');
}

function closeAddModal() {
    document.getElementById('addModal').classList.add('opacity-0', 'pointer-events-none');
    document.getElementById('addModalBox').classList.add('scale-95');
    currentAddTarget = null;
}

function saveAddModal() {
    if (!currentAddTarget) return;
    const desc = document.getElementById('addFieldDesc').value.trim();
    if (!desc) {
        alert('El texto es obligatorio.');
        return;
    }
    if (currentAddTarget.kind === 'guardrail') {
        const name = document.getElementById('addFieldName').value.trim();
        if (!name) {
            alert('El nombre de la regla es obligatorio.');
            return;
        }
        addGuardrail(name, desc);
    } else if (currentAddTarget.kind === 'paso') {
        addPaso(currentAddTarget.skillId, desc);
    }
    closeAddModal();
}

function setDecision(type, id, status) {
    const current = getDecision(type, id);
    if (status === 'PENDIENTE') {
        auditLog[type][id] = defaultDecision();
    } else if (status === 'APROBADO') {
        if (current.status === 'APROBADO') {
            auditLog[type][id] = defaultDecision();
        } else {
            auditLog[type][id] = { status: 'APROBADO', reason: '', solution: '' };
        }
    }
    renderAll();
}

function triggerAdjustment(type, id) {
    currentModalTarget = { type, id };
    const current = getDecision(type, id);
    document.getElementById('modalReason').value = current.reason || '';
    document.getElementById('modalSolution').value = current.solution || '';
    document.getElementById('rejectModal').classList.remove('opacity-0', 'pointer-events-none');
    document.getElementById('modalBox').classList.remove('scale-95');
}

function closeModal() {
    document.getElementById('rejectModal').classList.add('opacity-0', 'pointer-events-none');
    document.getElementById('modalBox').classList.add('scale-95');
    currentModalTarget = null;
}

function saveModalAdjustment() {
    const reason = document.getElementById('modalReason').value.trim();
    const solution = document.getElementById('modalSolution').value.trim();
    if (!reason || !solution) {
        alert('Es obligatorio ingresar la razón jurídica y la solución técnica.');
        return;
    }
    if (currentModalTarget) {
        const { type, id } = currentModalTarget;
        auditLog[type][id] = { status: 'AJUSTAR', reason, solution };
        closeModal();
        renderAll();
    }
}

function countPasosByStatus() {
    const counts = { APROBADO: 0, AJUSTAR: 0, PENDIENTE: 0 };
    catalog.skills.forEach(s => {
        getEffectiveSteps(s).forEach(st => {
            const stt = getDecision('pasos', st.key).status;
            counts[stt] = (counts[stt] || 0) + 1;
        });
    });
    return counts;
}

function countByStatus(type, items, idFn) {
    const counts = { APROBADO: 0, AJUSTAR: 0, PENDIENTE: 0 };
    items.forEach(item => {
        const s = getDecision(type, idFn(item)).status;
        counts[s] = (counts[s] || 0) + 1;
    });
    return counts;
}

function exportarMarkdown() {
    const genAt = catalog.generated_at || new Date().toISOString();
    let md = `# Reporte Consolidado de Aprobación Técnico-Legal\n\n`;
    md += `**Generado en:** ${genAt} (Legal Audit Sync v2)\n`;
    md += `**Principio profesional:** La IA propone; la abogada revisa, ajusta y aprueba.\n\n`;
    md += `Sistema penal-víctimas Colombia — ${catalog.intro?.agentes || 11} agentes, ${catalog.intro?.skills || 90} skills, ${countEffectivePasos()} pasos auditable.\n\n---\n\n`;

    md += `## 1. Validación de Reglas Estrictas\n\n`;
    getEffectiveGuardrails().forEach(g => {
        const state = getDecision('guardrails', g.id);
        const tag = g.custom ? ' *(agregada por abogada)*' : '';
        md += `### ${g.name}${tag}\n- **Descripción:** ${g.desc}\n- **Estado:** ${state.status}\n`;
        if (state.reason) md += `- **Razón:** _${state.reason}_\n- **Solución:** _${state.solution}_\n`;
        md += `\n`;
    });

    md += `## 2. Dictamen sobre Agentes (${catalog.agentes.length})\n\n`;
    catalog.agentes.forEach(a => {
        const state = getDecision('agentes', a.id);
        md += `### \`${a.name}\` (${a.grupo})\n`;
        md += `- **Nombre corto:** ${a.nombre_corto}\n- **Estado:** ${state.status}\n`;
        if (state.reason) md += `- **Defectos:** _${state.reason}_\n- **Instrucción:** _${state.solution}_\n`;
        md += `\n`;
    });

    md += `## 3. Auditoría de Pasos por Skill\n\n`;
    const byCat = {};
    catalog.skills.forEach(s => {
        const cat = s.category || 'Sin categoría';
        if (!byCat[cat]) byCat[cat] = [];
        byCat[cat].push(s);
    });
    Object.keys(byCat).sort().forEach(cat => {
        md += `### Categoría: ${cat}\n\n`;
        byCat[cat].forEach(s => {
            md += `#### Skill: \`${s.name}\`\n`;
            md += `- **Instrucción tipo:** ${s.instruccion || s.desc}\n`;
            getEffectiveSteps(s).forEach(st => {
                const state = getDecision('pasos', st.key);
                const tag = st.custom ? ' *(agregado por abogada)*' : '';
                md += `##### Paso ${st.displayNum}${tag}\n`;
                md += `- **Texto:** ${st.text}\n- **Estado:** ${state.status}\n`;
                if (state.reason) md += `- **Razón:** _${state.reason}_\n- **Ajuste:** _${state.solution}_\n`;
            });
            md += `\n`;
        });
    });

    const g = countByStatus('guardrails', getEffectiveGuardrails(), x => x.id);
    const ag = countByStatus('agentes', catalog.agentes, x => x.id);
    const ps = countPasosByStatus();
    md += `---\n\n## 4. Resumen Ejecutivo\n\n`;
    md += `| Sección | APROBADO | AJUSTAR | PENDIENTE |\n|---|---|---|---|\n`;
    md += `| Reglas estrictas | ${g.APROBADO} | ${g.AJUSTAR} | ${g.PENDIENTE} |\n`;
    md += `| Agentes | ${ag.APROBADO} | ${ag.AJUSTAR} | ${ag.PENDIENTE} |\n`;
    md += `| Pasos (skills) | ${ps.APROBADO} | ${ps.AJUSTAR} | ${ps.PENDIENTE} |\n`;
    md += `\n**Total ítems:** ${countEffectiveItems()}\n`;

    const custom = ensureCustom();
    if (custom.guardrailsRemoved.length || custom.pasosRemoved.length) {
        md += `\n---\n\n## 5. Elementos eliminados de la auditoría\n\n`;
        if (custom.guardrailsRemoved.length) {
            md += `### Reglas estrictas eliminadas\n`;
            custom.guardrailsRemoved.forEach(id => {
                const orig = catalog.guardrails.find(g => g.id === id);
                md += `- \`${id}\`${orig ? ` — ${orig.name}` : ''}\n`;
            });
        }
        if (custom.pasosRemoved.length) {
            md += `\n### Pasos eliminados\n`;
            custom.pasosRemoved.forEach(pk => { md += `- \`${pk}\`\n`; });
        }
    }

    const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'Documento_Unico_Aprobacion_Sincronizado.md';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

async function init() {
    loadAuditLog();
    ensureCustom();
    try {
        const res = await fetch('./audit-data.json');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        catalog = await res.json();
    } catch (err) {
        document.getElementById('progress-chip').textContent = 'Error al cargar audit-data.json';
        console.error(err);
        return;
    }

    document.getElementById('generated-at').textContent = catalog.generated_at || '—';
    const buildEl = document.getElementById('build-generated-at');
    if (buildEl && catalog.generated_at) {
        buildEl.textContent = `· catálogo ${catalog.generated_at}`;
        buildEl.classList.remove('hidden');
    }
    renderGuiaCategorias();
    populateFilters();

    document.getElementById('search-input').addEventListener('input', applyFilters);
    document.getElementById('filter-category').addEventListener('change', applyFilters);
    document.getElementById('filter-agent').addEventListener('change', applyFilters);
    document.getElementById('group-by-category').addEventListener('change', e => {
        groupByCategory = e.target.checked;
        renderSkills();
        applyFilters();
    });

    renderAll();
}

window.setDecision = setDecision;
window.triggerAdjustment = triggerAdjustment;
window.closeModal = closeModal;
window.saveModalAdjustment = saveModalAdjustment;
window.closeAddModal = closeAddModal;
window.saveAddModal = saveAddModal;
window.openAddGuardrailModal = openAddGuardrailModal;
window.openAddPasoModal = openAddPasoModal;
window.exportarMarkdown = exportarMarkdown;

document.addEventListener('DOMContentLoaded', init);
