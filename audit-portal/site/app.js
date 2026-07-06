/* Auditoría de Instrucciones — auditoría por paso */

const STORAGE_KEY = 'legal-audit-sync-v2';

const GROUP_LABELS = {
    coordinacion: 'Coordinación',
    especialista: 'Especialistas',
    calidad: 'Control de calidad',
};

const GROUP_BADGE_CLASS = {
    coordinacion: 'guia-badge-coord',
    especialista: 'guia-badge-spec',
    calidad: 'guia-badge-cal',
};

const AGENT_ORDER = [
    'coordinador_expediente_penal',
    'analista_cronologia_hechos_penales',
    'analista_tipicidad_y_responsabilidad_penal',
    'analista_ruta_procesal_ley906',
    'analista_representacion_victimas',
    'gestor_evidencia_y_soporte_probatorio',
    'preparador_estrategico_audiencias_penales',
    'redactor_documentos_juridicos_penales',
    'gestor_seguimiento_procesal_penal',
    'evaluador_derechos_fundamentales_tutela',
    'analista_calidad_juridica',
];

const GUARDRAIL_EJEMPLOS = {
    g1: 'Si no hay auto en expediente, marca [PENDIENTE DE VERIFICAR] en lugar de citar sentencia o artículo.',
    g2: 'Si falta etapa procesal o radicado, pregunta antes de recomendar tutela o memorial.',
    g3: 'Distingue relato de víctima (narrado) de conclusión típica (inferida).',
    g4: 'Memorial, tutela o reporte a cliente siempre como borrador para su revisión y firma.',
    g5: 'Evita lenguaje que culpe a la víctima o exponga datos innecesarios del caso.',
    g6: 'No repite cédula, dirección o datos de salud sin necesidad probatoria.',
    g7: 'Consulta civil o laboral se declara fuera de alcance penal-víctimas.',
    g8: 'Cierra con aviso de que la salida requiere revisión profesional.',
};

const GUARDRAIL_PROTEGE = {
    g1: 'Integridad factual y normativa',
    g2: 'Oportunidad procesal',
    g3: 'Trazabilidad probatoria',
    g4: 'HITL / firma profesional',
    g5: 'Dignidad de la víctima',
    g6: 'Datos sensibles',
    g7: 'Especialización del sistema',
    g8: 'Transparencia al despacho',
};

const FLUJO_CONSULTA = [
    {
        title: 'USTED CONSULTA',
        sub: 'Describe la necesidad del caso, como le escribiría a un practicante del despacho.',
        color: '#64748b',
        icon: 'fa-comment-dots',
    },
    {
        title: 'EL EQUIPO ENRUTA',
        sub: 'Coordinación y agente especializado eligen la guía operativa correcta.',
        color: '#2563eb',
        icon: 'fa-route',
    },
    {
        title: 'GUÍA OPERATIVA PASO A PASO',
        sub: 'El asistente sigue las instrucciones en serie o en paralelo que usted aprueba aquí.',
        color: '#d97706',
        icon: 'fa-list-check',
    },
    {
        title: 'USTED REVISA Y FIRMA',
        sub: 'Recibe un borrador con entrada y salida trazables. Usted decide si radica, ajusta o rechaza.',
        color: '#059669',
        icon: 'fa-signature',
    },
];

const PROTO_LAYERS = [
    {
        funnelClass: 'guia-funnel-layer--rules',
        title: 'REGLAS ESTRICTAS',
        countKey: 'guardrails',
        desc: 'Límites que el asistente debe respetar en toda respuesta, antes de cualquier guía operativa.',
    },
    {
        funnelClass: 'guia-funnel-layer--roles',
        title: 'AGENTES',
        countKey: 'agentes',
        desc: 'Once agentes especializados: quien coordina, quien analiza, quien redacta y quien controla calidad.',
    },
    {
        funnelClass: 'guia-funnel-layer--procs',
        title: 'GUÍA OPERATIVA',
        countKey: 'skills',
        desc: 'Instrucciones atómicas del «cómo hacer» cada tarea jurídica penal-víctimas en Colombia.',
    },
    {
        funnelClass: 'guia-funnel-layer--steps',
        title: 'PASOS',
        countKey: 'pasos',
        desc: 'Instrucciones en serie o en paralelo dentro de cada guía. Lo más detallado que usted aprueba o ajusta.',
    },
];

const GUIA_GLOSARIO = [
    {
        term: 'Agente',
        desc: 'Especialista del equipo digital penal-víctimas: recibe la consulta, analiza, redacta, prepara audiencias o controla calidad antes de entregarle el borrador.',
    },
    {
        term: 'Guía operativa',
        desc: 'Instrucción atómica con entrada, pasos y salida — por ejemplo, redactar un memorial o construir una cronología.',
    },
    {
        term: 'Paso',
        desc: 'Cada instrucción numerada. En serie se ejecuta en orden; en paralelo puede correr al mismo tiempo si no hay dependencia.',
    },
    {
        term: 'Entrada',
        desc: 'Datos, documentos o contexto que recibe la guía operativa antes de actuar (expediente, relato, etapa Ley 906, etc.).',
    },
    {
        term: 'Salida',
        desc: 'Producto estructurado que entrega la guía: borrador, matriz, alerta, cronología o dictamen preliminar.',
    },
    {
        term: 'Destinatario',
        desc: 'Quién usa la salida: otro agente, el despacho para firma, o control de calidad antes de compartir.',
    },
];

let catalog = {
    guardrails: [], agentes: [], skills: [], categorias: [],
    generated_at: '', totals: {}, intro: {},
};
let auditLog = { guardrails: {}, agentes: {}, pasos: {}, custom: null };
let currentModalTarget = null;
let currentAddTarget = null;

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
            modo: st.modo || 'serial',
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
    const base = 'audit-btn-row px-3 py-2 rounded-lg font-semibold transition-all border ';
    if (active && kind === 'approve') return base + 'bg-emerald-600 border-emerald-600 text-white shadow-sm';
    if (active && kind === 'adjust') return base + 'bg-amber-500 border-amber-500 text-white shadow-sm';
    if (active && kind === 'pending') return base + 'bg-slate-500 border-slate-500 text-white shadow-sm';
    return base + 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50';
}

function renderAdjustmentBlock(reason, solution) {
    if (!reason) return '';
    return `
        <div class="audit-adjustment mt-3 p-3 bg-red-50/60 rounded-xl border border-red-100 text-red-800 space-y-1">
            <p class="font-semibold text-red-600"><i class="fa-solid fa-gavel mr-1"></i> Dictamen de ajuste</p>
            <p><strong>Razón:</strong> ${escapeHtml(reason)}</p>
            <p><strong>Solución:</strong> ${escapeHtml(solution)}</p>
        </div>`;
}

function btnDeleteClass() {
    return 'px-2 py-1 rounded-lg text-sm font-semibold border border-red-200 text-red-600 bg-white hover:bg-red-50 transition-all';
}

function procBadgeClass(prog) {
    if (prog.reviewed === prog.total && prog.total > 0) return 'audit-badge audit-badge--ok';
    if (prog.adjust > 0) return 'audit-badge audit-badge--warn';
    return 'audit-badge audit-badge--neutral';
}

function agentSearchText(agent) {
    const byId = Object.fromEntries(catalog.skills.map(s => [s.id, s]));
    const parts = [agent.titulo_profesional, agent.nombre_corto, agent.desc, agent.problema, agent.necesidad, agent.no_reemplaza];
    (agent.skill_ids || []).forEach(sid => {
        const s = byId[sid];
        if (!s) return;
        parts.push(skillDisplayName(s), s.desc, s.instruccion, s.category, s.name);
        getEffectiveSteps(s).forEach(st => parts.push(st.text));
    });
    return parts.filter(Boolean).join(' ').toLowerCase();
}

function procSearchText(skill) {
    const parts = [skillDisplayName(skill), skill.desc, skill.instruccion, skill.category, skill.name];
    getEffectiveSteps(skill).forEach(st => parts.push(st.text));
    return parts.filter(Boolean).join(' ').toLowerCase();
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

function buildGuardrailCard(item) {
    const current = getDecision('guardrails', item.id);
    const card = document.createElement('div');
    card.className = `audit-card bg-white p-5 md:p-6 rounded-2xl border transition-all ${cardBorderClass(current.status)}`;
    card.dataset.type = 'guardrails';
    card.dataset.id = item.id;
    card.dataset.search = [item.name, item.desc].filter(Boolean).join(' ').toLowerCase();

    const customBadge = item.custom
        ? '<span class="audit-badge audit-badge--new">Agregada por el despacho</span>'
        : '';

    card.innerHTML = `
        <div class="flex flex-col md:flex-row md:items-start justify-between gap-4">
            <div class="space-y-1 flex-1 min-w-0">
                <div class="flex flex-wrap items-center gap-2">
                    <h4 class="audit-title">${escapeHtml(item.name)}</h4>
                    ${customBadge}
                </div>
                <p class="audit-body">${escapeHtml(item.desc)}</p>
            </div>
            <div class="flex flex-col items-end gap-2 shrink-0 audit-btn-row">
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
            ? '<span class="audit-badge audit-badge--new ml-1">Nuevo</span>'
            : '';
        return `
            <div class="paso-card audit-card p-4 rounded-xl border ${cardBorderClass(d.status)} mt-2" data-paso-id="${escapeHtml(st.key)}" data-skill-id="${escapeHtml(skill.id)}">
                <div class="flex flex-col md:flex-row md:items-start justify-between gap-3">
                    <div class="flex-1">
                        <p class="audit-paso-label">PASO ${st.displayNum}${pasoModoBadge(st.modo)}${customBadge}</p>
                        <p class="audit-body text-slate-800">${escapeHtml(st.text)}</p>
                    </div>
                    <div class="flex flex-col items-end gap-2 shrink-0 audit-btn-row">
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
        : '<p class="audit-meta mb-2">Sin pasos definidos. Agregue uno si lo requiere.</p>';

    const addBtn = showAddButton
        ? `<button type="button" data-action="add-paso" data-skill-id="${escapeHtml(skill.id)}" class="mt-3 w-full md:w-auto px-4 py-2 rounded-xl text-base font-semibold border border-dashed border-blue-300 text-blue-700 hover:bg-blue-50 transition-all">
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

function buildAgentSkillsPanel(agent, openProcedures = false) {
    const skillIds = agent.skill_ids || [];
    if (!skillIds.length) return '';

    const byId = Object.fromEntries(catalog.skills.map(s => [s.id, s]));
    const items = skillIds.map(sid => byId[sid]).filter(Boolean);

    const skillBlocks = items.map(skill => {
        const prog = skillStepProgress(skill);
        const displayName = skillDisplayName(skill);

        return `
            <details class="agent-proc-details audit-proc-details bg-white border border-slate-200 rounded-xl overflow-hidden"
                data-category="${escapeHtml(skill.category || '')}"
                data-search="${escapeHtml(procSearchText(skill))}">
                <summary class="flex flex-wrap items-center gap-2 select-none list-none">
                    <i class="fa-solid fa-chevron-right text-slate-400 agent-skill-chevron transition-transform"></i>
                    <span class="audit-proc-summary">${escapeHtml(displayName)}</span>
                    <span class="${procBadgeClass(prog)}">${prog.reviewed}/${prog.total} pasos</span>
                    <span class="audit-meta">${escapeHtml(skill.category || '')}</span>
                </summary>
                <div class="px-4 pb-4 border-t border-slate-100 pt-3">
                    ${buildSkillSpecHtml(skill)}
                    ${skill.desc ? `<p class="audit-body mb-2"><strong>Para qué sirve:</strong> ${escapeHtml(skill.desc)}</p>` : ''}
                    ${skill.instruccion && skill.instruccion !== skill.desc ? `<p class="audit-meta mb-3">${escapeHtml(skill.instruccion)}</p>` : ''}
                    ${buildPasoCardsHtml(skill)}
                </div>
            </details>`;
    }).join('');

    const missing = skillIds.filter(sid => !byId[sid]);
    const missingHtml = missing.map(sid =>
        `<p class="audit-meta text-red-600">Guía operativa no encontrada en catálogo.</p>`
    ).join('');

    const openAttr = openProcedures ? ' open' : '';

    return `
        <details class="agent-skills-details audit-proc-panel mt-2 border border-slate-200 rounded-xl bg-slate-50/80 overflow-hidden"${openAttr}>
            <summary class="cursor-pointer px-4 py-3 select-none list-none flex items-center gap-2 hover:bg-slate-100">
                <i class="fa-solid fa-chevron-right text-blue-500 agent-panel-chevron transition-transform"></i>
                <span class="audit-proc-summary text-blue-800">Ver guías operativas de este agente (${skillIds.length})</span>
            </summary>
            <div class="px-4 pb-4 space-y-2 border-t border-slate-200 pt-3">
                ${missingHtml}
                ${skillBlocks}
            </div>
        </details>`;
}

function buildAgentCard(agent, openProcedures = false) {
    const current = getDecision('agentes', agent.id);
    const card = document.createElement('div');
    card.className = `audit-card bg-white p-5 md:p-6 rounded-2xl border transition-all ${cardBorderClass(current.status)}`;
    card.dataset.type = 'agentes';
    card.dataset.id = agent.id;
    card.dataset.agentName = agent.name;
    card.dataset.search = agentSearchText(agent);

    const procCount = agent.skill_ids?.length || agent.skills_count || 0;

    card.innerHTML = `
        <div class="flex flex-col gap-4">
            <div class="flex flex-col md:flex-row md:items-start justify-between gap-4">
                <div class="space-y-2 flex-1">
                    <p class="audit-subtitle audit-title-caps">${escapeHtml(agentDisplayTitle(agent))}</p>
                    <p class="audit-body">${escapeHtml(agent.desc)}</p>
                    <p class="audit-meta"><strong>Problema que resuelve:</strong> ${escapeHtml(agent.problema || '—')}</p>
                    ${agent.necesidad ? `<p class="audit-meta"><strong>Valor en el caso:</strong> ${escapeHtml(agent.necesidad)}</p>` : ''}
                    <p class="audit-meta"><strong>No reemplaza:</strong> ${escapeHtml(agent.no_reemplaza || '—')}</p>
                    <p class="audit-meta">${procCount} guía${procCount === 1 ? '' : 's'} operativa${procCount === 1 ? '' : 's'}</p>
                </div>
                <div class="audit-btn-row shrink-0">${buildDecisionButtons('agentes', agent.id)}</div>
            </div>
            ${buildAgentSkillsPanel(agent, openProcedures)}
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
            <h4 class="audit-group-heading">
                ${escapeHtml(GROUP_LABELS[grupo] || grupo)} (${agents.length})
            </h4>
            <div class="grid gap-4 agent-group-grid"></div>`;
        const grid = block.querySelector('.agent-group-grid');
        agents.forEach((a, idx) => grid.appendChild(buildAgentCard(a, idx === 0)));
        c.appendChild(block);
    });
}

function applyFilters() {
    const q = (document.getElementById('search-input').value || '').trim().toLowerCase();
    const catFilter = document.getElementById('filter-category').value;
    const agentFilter = document.getElementById('filter-agent').value;

    document.querySelectorAll('.agent-proc-details').forEach(proc => {
        let visible = true;
        if (catFilter && proc.dataset.category !== catFilter) visible = false;
        if (q && !(proc.dataset.search || '').includes(q)) {
            const agentCard = proc.closest('.audit-card[data-type="agentes"]');
            if (!agentCard || !(agentCard.dataset.search || '').includes(q)) visible = false;
        }
        proc.classList.toggle('hidden', !visible);
    });

    document.querySelectorAll('.audit-card[data-type="agentes"]').forEach(card => {
        let visible = true;
        if (agentFilter && card.dataset.id !== agentFilter) visible = false;
        if (q && !(card.dataset.search || '').includes(q)) visible = false;
        if (catFilter) {
            const anyProc = [...card.querySelectorAll('.agent-proc-details')].some(
                p => !p.classList.contains('hidden'),
            );
            if (!anyProc) visible = false;
        }
        card.classList.toggle('hidden', !visible);
    });

    document.querySelectorAll('.audit-card[data-type="guardrails"]').forEach(card => {
        let visible = true;
        if (q && !(card.dataset.search || '').includes(q)) visible = false;
        card.classList.toggle('hidden', !visible);
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
    catalog.agentes.forEach(a => {
        const o = document.createElement('option');
        o.value = a.id;
        o.textContent = agentDisplayTitle(a);
        agentSel.appendChild(o);
    });
}

function renderGuardrails() {
    const c = document.getElementById('container-guardrails');
    c.innerHTML = '';
    getEffectiveGuardrails().forEach(g => c.appendChild(buildGuardrailCard(g)));
    const addWrap = document.createElement('div');
    addWrap.className = 'mt-2';
    addWrap.innerHTML = `
        <button type="button" id="btn-add-guardrail" class="w-full md:w-auto px-4 py-2.5 rounded-xl text-base font-semibold border border-dashed border-blue-400 text-blue-700 hover:bg-blue-50 transition-all">
            <i class="fa-solid fa-plus mr-1"></i> Agregar regla estricta
        </button>`;
    c.appendChild(addWrap);
    document.getElementById('btn-add-guardrail')?.addEventListener('click', openAddGuardrailModal);
}

function agentDisplayTitle(agent) {
    return agent.titulo_profesional || (agent.nombre_corto || '').toUpperCase();
}

function skillDisplayName(skill) {
    if (!skill) return '';
    if (skill.titulo) return skill.titulo;
    const fromInstr = (skill.instruccion || '').replace(/\.$/, '').trim();
    if (fromInstr) return fromInstr.toUpperCase();
    return (skill.desc || skill.name || '').replace(/\.$/, '').toUpperCase();
}

function skillFlujoLabel(skill) {
    if (skill?.flujo_pasos === 'serie_y_paralelo') return 'SERIE Y PARALELO';
    return 'SERIE';
}

function buildSkillSpecHtml(skill) {
    const ejecutores = (skill.agentes_ejecutores || []).join(', ') || '—';
    return `
        <div class="audit-spec-block mb-3">
            <p class="audit-spec-heading">ESPECIFICACIÓN</p>
            <p class="audit-meta"><strong>Entrada que recibe:</strong> ${escapeHtml(skill.inputs || '—')}</p>
            <p class="audit-meta"><strong>Salida que produce:</strong> ${escapeHtml(skill.outputs || '—')}</p>
            <p class="audit-meta"><strong>Quién la ejecuta:</strong> ${escapeHtml(ejecutores)}</p>
            <p class="audit-meta"><strong>Destinatario de la salida:</strong> ${escapeHtml(skill.destinatario || '—')}</p>
            <p class="audit-meta"><strong>Flujo de pasos:</strong> ${skillFlujoLabel(skill)}</p>
        </div>`;
}

function pasoModoBadge(modo) {
    if (modo === 'paralelo') {
        return ' <span class="audit-badge audit-badge--flow-par">PARALELO</span>';
    }
    return '';
}

function agentSkillExamples(agent, limit = 2) {
    const byId = Object.fromEntries(catalog.skills.map(s => [s.id, s]));
    return (agent.skill_ids || []).slice(0, limit).map(sid => {
        const s = byId[sid];
        return s ? skillDisplayName(s) : sid.replace(/_/g, ' ');
    });
}

function renderGuiaDiagrama() {
    const el = document.getElementById('guia-diagrama');
    if (!el) return;

    const counts = {
        guardrails: getEffectiveGuardrails().length,
        agentes: catalog.agentes?.length || 11,
        skills: catalog.intro?.skills || catalog.skills?.length || 90,
        pasos: countEffectivePasos(),
    };

    const layers = PROTO_LAYERS.map(layer => {
        const n = counts[layer.countKey] ?? '—';
        return `
            <div class="guia-funnel-layer ${layer.funnelClass}">
                <h4>${escapeHtml(layer.title)} <span class="guia-count">(${n})</span></h4>
                <p>${escapeHtml(layer.desc)}</p>
            </div>`;
    }).join('');

    el.innerHTML = `<div class="guia-funnel">${layers}</div>`;
}

function renderGuiaGlosario() {
    const el = document.getElementById('guia-glosario');
    if (!el) return;
    el.innerHTML = GUIA_GLOSARIO.map(g => `
        <div class="guia-glossary-item">
            <strong>${escapeHtml(g.term.toUpperCase())}</strong>
            <span>${escapeHtml(g.desc)}</span>
        </div>`).join('');
}

function renderGuiaEjemplo() {
    const el = document.getElementById('guia-ejemplo-completo');
    if (!el) return;

    const dayFlow = FLUJO_CONSULTA.map(s => `
        <div class="guia-day-step">
            <div class="guia-day-step-icon" style="background:${s.color}">
                <i class="fa-solid ${s.icon}"></i>
            </div>
            <h5>${escapeHtml(s.title)}</h5>
            <p>${escapeHtml(s.sub)}</p>
        </div>`).join('');

    const skill = catalog.skills?.find(s => s.id === 'redactar_memorial_penal')
        || catalog.skills?.[0];

    let manualHtml = '<p class="guia-caption">Cargando catálogo…</p>';
    if (skill) {
        const agentName = (skill.agents || [])
            .map(aid => catalog.agentes?.find(a => a.id === aid || a.name === aid))
            .filter(Boolean)
            .map(a => agentDisplayTitle(a))
            .join(', ') || 'Agente asignado';

        const steps = getEffectiveSteps(skill);
        const stepsHtml = steps.slice(0, 4).map(st => `
            <div class="guia-manual-step">
                <span class="guia-manual-step-num">${st.displayNum}</span>
                <span>${escapeHtml(st.text)}${st.modo === 'paralelo' ? ' <em class="guia-flow-tag">(paralelo)</em>' : ''}</span>
            </div>`).join('');

        const more = steps.length > 4
            ? `<p class="guia-manual-more">Y ${steps.length - 4} pasos adicionales en el catálogo completo.</p>`
            : '';

        manualHtml = `
            <div class="guia-manual">
                <div class="guia-manual-head">
                    <p class="guia-label">GUÍA OPERATIVA</p>
                    <h4 class="audit-title-caps">${escapeHtml(skillDisplayName(skill))}</h4>
                </div>
                <div class="guia-manual-body">
                    <p class="guia-manual-meta"><strong>Entrada:</strong> ${escapeHtml(skill.inputs || 'Expediente, hechos y contexto del caso')}</p>
                    <p class="guia-manual-meta"><strong>Salida:</strong> ${escapeHtml(skill.outputs || 'Borrador estructurado para revisión')}</p>
                    <p class="guia-manual-meta"><strong>Agente:</strong> ${escapeHtml(agentName)}</p>
                    <p class="guia-manual-meta"><strong>Destinatario:</strong> ${escapeHtml(skill.destinatario || 'Despacho (borrador para firma y radicación)')}</p>
                    <p class="guia-manual-meta"><strong>Flujo:</strong> ${skillFlujoLabel(skill)}</p>
                    ${stepsHtml || '<p class="guia-caption">Sin pasos definidos</p>'}
                    ${more}
                </div>
            </div>`;
    }

    el.innerHTML = `
        <div class="guia-day-flow">${dayFlow}</div>
        <div class="guia-story">
            <div class="guia-story-intro">
                <strong>Ejemplo:</strong> Usted necesita un <em>memorial de impulso en indagación</em>.
                El agente de coordinación enruta al redactor de escritos; este sigue la guía operativa
                «Crear borrador de memorial penal» paso a paso; calidad revisa el borrador y usted
                lo firma o lo devuelve con observaciones.
            </div>
            ${manualHtml}
        </div>`;
}

function renderGuiaEquipo() {
    const el = document.getElementById('guia-equipo-bandas');
    if (!el || !catalog.agentes?.length) return;

    const byId = Object.fromEntries(catalog.agentes.map(a => [a.id, a]));
    const coord = byId['coordinador_expediente_penal'];
    const calidad = byId['analista_calidad_juridica'];
    const specs = AGENT_ORDER.filter(id =>
        id !== 'coordinador_expediente_penal' && id !== 'analista_calidad_juridica',
    ).map(id => byId[id]).filter(Boolean);

    const specChips = specs.map(a =>
        `<span class="guia-chip audit-title-caps">${escapeHtml(agentDisplayTitle(a))}</span>`,
    ).join('');

    el.innerHTML = `
        <div class="guia-team-grid">
            <div class="guia-team-card guia-team-card--recv">
                <p class="guia-label" style="color:#2563eb">RECEPCIÓN Y COORDINACIÓN</p>
                <h4 class="audit-title-caps">${escapeHtml(agentDisplayTitle(coord) || 'COORDINACIÓN Y ENRUTAMIENTO DEL CASO PENAL')}</h4>
                <p>${escapeHtml(coord?.desc || 'Recibe su consulta y dirige el caso al agente y guía operativa correctos.')}</p>
                <ul class="guia-value-list guia-team-value">
                    <li><strong>Primer contacto:</strong> entiende qué necesita el despacho — memorial, cronología, audiencia, tutela — sin respuestas genéricas.</li>
                    <li><strong>Enrutamiento correcto:</strong> envía el caso al especialista y la guía operativa adecuados según etapa Ley 906 y prioridad legal.</li>
                    <li><strong>Orden del trabajo:</strong> pide datos faltantes antes de concluir y evita perder tiempo en análisis mal enfocados.</li>
                </ul>
            </div>
            <div class="guia-team-card guia-team-card--spec">
                <p class="guia-label" style="color:#7c3aed">ESPECIALISTAS</p>
                <h4 class="audit-title-caps">NUEVE ÁREAS JURÍDICAS</h4>
                <p>Nueve especialistas ejecutan el análisis y la redacción: tipicidad, víctimas, evidencia, audiencias, escritos, seguimiento y tutela bajo la Ley 906.</p>
                <div class="guia-chips">${specChips}</div>
            </div>
            <div class="guia-team-card guia-team-card--qual">
                <p class="guia-label" style="color:#d97706">CONTROL DE CALIDAD</p>
                <h4 class="audit-title-caps">${escapeHtml(agentDisplayTitle(calidad) || 'REVISIÓN DE CALIDAD Y CONTROL DE RIESGOS JURÍDICOS')}</h4>
                <p>${escapeHtml(calidad?.desc || 'Revisa coherencia y riesgos antes de entregarle el borrador.')}</p>
                <ul class="guia-value-list guia-team-value">
                    <li><strong>Último filtro:</strong> revisa toda salida antes de que llegue a usted para firma o radicación.</li>
                    <li><strong>Riesgos jurídicos:</strong> detecta alucinaciones normativas, incoherencia estratégica y contradicciones factuales.</li>
                    <li><strong>Protección de la víctima:</strong> controla confidencialidad, no revictimización y tono adecuado en documentos sensibles.</li>
                </ul>
            </div>
        </div>`;
}

function initGuiaScrollSpy() {
    const sectionIds = ['guia-inicio', 'guia-modelo', 'guia-ejemplo', 'guia-uso-local', 'guia-equipo', 'guia-glosario-sec', 'guia-empezar'];
    const links = document.querySelectorAll('#guia-toc a[data-guia-section]');
    if (!links.length) return;

    const sections = sectionIds
        .map(id => document.getElementById(id))
        .filter(Boolean);

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (!entry.isIntersecting) return;
            const id = entry.target.id;
            links.forEach(a => {
                a.classList.toggle('is-active', a.dataset.guiaSection === id);
            });
        });
    }, { rootMargin: '-20% 0px -60% 0px', threshold: 0 });

    sections.forEach(sec => observer.observe(sec));
}

function initGuiaReadProgress() {
    const guia = document.getElementById('guia');
    const bar = document.getElementById('guia-read-progress-bar');
    if (!guia || !bar) return;

    const update = () => {
        const rect = guia.getBoundingClientRect();
        const scrollTop = window.scrollY || document.documentElement.scrollTop;
        const guiaTop = scrollTop + rect.top;
        const guiaHeight = guia.offsetHeight;
        const viewport = window.innerHeight;
        const scrolled = scrollTop + viewport - guiaTop;
        const pct = Math.min(100, Math.max(0, (scrolled / guiaHeight) * 100));
        bar.style.width = `${pct}%`;
    };

    window.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    update();
}

function renderGuiaCompleta() {
    renderGuiaCategorias();
    renderGuiaDiagrama();
    renderGuiaGlosario();
    renderGuiaEjemplo();
    renderGuiaEquipo();
    initGuiaScrollSpy();
    initGuiaReadProgress();
}

function renderGuiaCategorias() {
    const intro = document.getElementById('guia-intro-text');
    const note = document.getElementById('guia-categorias-note');
    if (intro && catalog.intro) {
        const gr = getEffectiveGuardrails().length;
        const pas = countEffectivePasos();
        const total = countEffectiveItems();
        const guias = catalog.intro?.guias_operativas || catalog.intro?.skills || 0;
        const base = intro.textContent.split(' Catálogo:')[0].trim();
        intro.textContent = `${base} Catálogo: ${total} elementos (${gr} reglas, ${catalog.intro.agentes} agentes, ${guias} guías operativas, ${pas} pasos).`;
    }
    if (note && catalog.categorias?.length) {
        const n = catalog.intro?.guias_operativas || catalog.intro?.skills || catalog.skills?.length || 0;
        note.textContent = `Las ${n} guías operativas se revisan dentro de cada agente en el panel de abajo.`;
    }
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
    const pasosBadge = document.getElementById('badge-pasos');
    if (pasosBadge) {
        pasosBadge.textContent = pasosPending ? `${pasosPending} pasos` : '';
        pasosBadge.className = `text-[10px] px-1.5 py-0.5 rounded ${pasosPending ? 'bg-amber-900/50 text-amber-300' : 'hidden'}`;
    }

    const chip = document.getElementById('progress-chip');
    if (chip) {
        chip.innerHTML = `<i class="fa-solid fa-chart-pie mr-1 text-blue-400"></i> <strong>${reviewed}</strong> / ${total} revisados`;
    }
}

function renderAll() {
    renderGuardrails();
    renderAgentes();
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
    document.getElementById('addModalTitle').textContent = 'Agregar paso a la guía operativa';
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
    md += `**Generado en:** ${genAt} (Auditoría de Instrucciones)\n`;
    md += `**Principio profesional:** La IA propone; usted revisa, ajusta y aprueba.\n\n`;
    const guiasN = catalog.intro?.guias_operativas || catalog.intro?.skills || 90;
    md += `Sistema penal-víctimas Colombia — ${catalog.intro?.agentes || 11} agentes, ${guiasN} guías operativas, ${countEffectivePasos()} pasos auditable.\n\n---\n\n`;

    md += `## Validación de Reglas Estrictas\n\n`;
    getEffectiveGuardrails().forEach(g => {
        const state = getDecision('guardrails', g.id);
        const tag = g.custom ? ' *(agregada por el despacho)*' : '';
        md += `### ${g.name}${tag}\n- **Descripción:** ${g.desc}\n- **Estado:** ${state.status}\n`;
        if (state.reason) md += `- **Razón:** _${state.reason}_\n- **Solución:** _${state.solution}_\n`;
        md += `\n`;
    });

    md += `## Dictamen sobre Agentes del equipo (${catalog.agentes.length})\n\n`;
    const byId = Object.fromEntries(catalog.skills.map(s => [s.id, s]));
    const order = ['coordinacion', 'especialista', 'calidad'];
    order.forEach(grupo => {
        const agents = catalog.agentes.filter(a => a.grupo === grupo);
        if (!agents.length) return;
        md += `### ${GROUP_LABELS[grupo] || grupo}\n\n`;
        agents.forEach(a => {
            const state = getDecision('agentes', a.id);
            md += `#### ${agentDisplayTitle(a)}\n`;
            md += `- **Propósito:** ${a.desc}\n`;
            if (a.necesidad) md += `- **Valor en el caso:** ${a.necesidad}\n`;
            md += `- **Problema que resuelve:** ${a.problema || '—'}\n`;
            md += `- **No reemplaza:** ${a.no_reemplaza || '—'}\n`;
            md += `- **Estado del agente:** ${state.status}\n`;
            if (state.reason) md += `- **Defectos:** _${state.reason}_\n- **Instrucción:** _${state.solution}_\n`;

            const skillIds = a.skill_ids || [];
            skillIds.forEach(sid => {
                const s = byId[sid];
                if (!s) return;
                md += `\n##### GUÍA OPERATIVA: ${skillDisplayName(s)}\n`;
                md += `- **Entrada:** ${s.inputs || '—'}\n`;
                md += `- **Salida:** ${s.outputs || '—'}\n`;
                md += `- **Ejecuta:** ${(s.agentes_ejecutores || []).join(', ') || '—'}\n`;
                md += `- **Destinatario:** ${s.destinatario || '—'}\n`;
                md += `- **Flujo:** ${skillFlujoLabel(s)}\n`;
                md += `- **Para qué sirve:** ${s.desc || s.instruccion || '—'}\n`;
                getEffectiveSteps(s).forEach(st => {
                    const stState = getDecision('pasos', st.key);
                    const tag = st.custom ? ' *(agregado por el despacho)*' : '';
                    const modo = st.modo === 'paralelo' ? ' [PARALELO]' : '';
                    md += `###### Paso ${st.displayNum}${modo}${tag}\n`;
                    md += `- **Texto:** ${st.text}\n- **Estado:** ${stState.status}\n`;
                    if (stState.reason) md += `- **Razón:** _${stState.reason}_\n- **Ajuste:** _${stState.solution}_\n`;
                });
            });
            md += `\n`;
        });
    });

    const g = countByStatus('guardrails', getEffectiveGuardrails(), x => x.id);
    const ag = countByStatus('agentes', catalog.agentes, x => x.id);
    const ps = countPasosByStatus();
    md += `---\n\n## Resumen Ejecutivo\n\n`;
    md += `| Sección | APROBADO | AJUSTAR | PENDIENTE |\n|---|---|---|---|\n`;
    md += `| Reglas estrictas | ${g.APROBADO} | ${g.AJUSTAR} | ${g.PENDIENTE} |\n`;
    md += `| Agentes del equipo | ${ag.APROBADO} | ${ag.AJUSTAR} | ${ag.PENDIENTE} |\n`;
    md += `| Pasos | ${ps.APROBADO} | ${ps.AJUSTAR} | ${ps.PENDIENTE} |\n`;
    md += `\n**Total ítems:** ${countEffectiveItems()}\n`;

    const custom = ensureCustom();
    if (custom.guardrailsRemoved.length || custom.pasosRemoved.length) {
        md += `\n---\n\n## Elementos eliminados de la auditoría\n\n`;
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
    if (typeof window.waitForAuditAuth === 'function') {
        const ok = await window.waitForAuditAuth();
        if (!ok) return;
    }
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
    renderGuiaCompleta();
    populateFilters();

    document.getElementById('search-input').addEventListener('input', applyFilters);
    document.getElementById('filter-category').addEventListener('change', applyFilters);
    document.getElementById('filter-agent').addEventListener('change', applyFilters);

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
