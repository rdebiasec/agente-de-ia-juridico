/* Auditoría de Instrucciones — auditoría por paso */

const STORAGE_KEY = 'legal-audit-sync-v4';
const STORAGE_KEY_LEGACY = 'legal-audit-sync-v3';
const STORAGE_KEY_LEGACY_V2 = 'legal-audit-sync-v2';
const SAVE_DEBOUNCE_MS = 800;
const DECISION_STATUSES = new Set(['APROBADO', 'AJUSTAR']);
const STATUS_RANK = { PENDIENTE: 0, AJUSTAR: 1, APROBADO: 2 };

let serverUpdatedAt = null;
let saveDebounceTimer = null;
let serverSyncEnabled = true;
let initialProgressSynced = false;
let progressUserDirty = false;

function normalizeEmailKey(email) {
    return String(email || '').trim().toLowerCase();
}

function storageKeyForEmail(email) {
    const e = normalizeEmailKey(email);
    return e ? `${STORAGE_KEY}:${e}` : STORAGE_KEY;
}

function decisionCount(payload) {
    if (!payload || typeof payload !== 'object') return 0;
    let count = 0;
    for (const type of ['guardrails', 'agentes', 'guias', 'pasos']) {
        const bucket = payload[type] || {};
        for (const id of Object.keys(bucket)) {
            const st = bucket[id];
            if (st && DECISION_STATUSES.has(st.status)) count += 1;
        }
    }
    const custom = payload.custom || {};
    if (Array.isArray(custom.guardrailsAdded)) count += custom.guardrailsAdded.length;
    if (custom.pasosAdded && typeof custom.pasosAdded === 'object') {
        for (const steps of Object.values(custom.pasosAdded)) {
            if (Array.isArray(steps)) count += steps.length;
        }
    }
    if (Array.isArray(custom.guardrailsRemoved)) count += custom.guardrailsRemoved.length;
    if (Array.isArray(custom.pasosRemoved)) count += custom.pasosRemoved.length;
    return count;
}

function mergeDecisionItem(left, right) {
    const a = left && typeof left === 'object' ? left : {};
    const b = right && typeof right === 'object' ? right : {};
    const aStatus = a.status || 'PENDIENTE';
    const bStatus = b.status || 'PENDIENTE';
    const aRank = STATUS_RANK[aStatus] ?? 0;
    const bRank = STATUS_RANK[bStatus] ?? 0;
    let chosen;
    let status;
    if (bRank > aRank) {
        chosen = b;
        status = bStatus;
    } else if (aRank > bRank) {
        chosen = a;
        status = aStatus;
    } else if (DECISION_STATUSES.has(bStatus)) {
        chosen = b;
        status = bStatus;
    } else {
        chosen = Object.keys(b).length ? b : a;
        status = bStatus || aStatus;
    }
    return {
        status,
        reason: String(chosen.reason || a.reason || b.reason || ''),
        solution: String(chosen.solution || a.solution || b.solution || ''),
    };
}

function mergeBucket(left, right) {
    const a = left && typeof left === 'object' ? left : {};
    const b = right && typeof right === 'object' ? right : {};
    const out = {};
    for (const key of new Set([...Object.keys(a), ...Object.keys(b)])) {
        out[key] = mergeDecisionItem(a[key], b[key]);
    }
    return out;
}

function mergeCustom(left, right) {
    const a = left && typeof left === 'object' ? left : {};
    const b = right && typeof right === 'object' ? right : {};
    const uniq = (arr) => {
        const seen = new Set();
        const out = [];
        for (const item of arr || []) {
            const k = JSON.stringify(item);
            if (seen.has(k)) continue;
            seen.add(k);
            out.push(item);
        }
        return out;
    };
    const pasosAdded = {};
    for (const src of [a.pasosAdded || {}, b.pasosAdded || {}]) {
        for (const [skillId, steps] of Object.entries(src)) {
            if (!Array.isArray(steps)) continue;
            pasosAdded[skillId] = uniq([...(pasosAdded[skillId] || []), ...steps]);
        }
    }
    return {
        guardrailsAdded: uniq([...(a.guardrailsAdded || []), ...(b.guardrailsAdded || [])]),
        guardrailsRemoved: uniq([...(a.guardrailsRemoved || []), ...(b.guardrailsRemoved || [])]),
        pasosAdded,
        pasosRemoved: uniq([...(a.pasosRemoved || []), ...(b.pasosRemoved || [])]),
    };
}

function mergePersistPayload(existing, incoming) {
    const left = existing && typeof existing === 'object' ? existing : {};
    const right = incoming && typeof incoming === 'object' ? incoming : {};
    if (!Object.keys(left).length) return { ...right };
    if (!Object.keys(right).length) return { ...left };
    return {
        version: right.version || left.version || 4,
        savedAt: right.savedAt || left.savedAt || null,
        catalogGeneratedAt: right.catalogGeneratedAt || left.catalogGeneratedAt || null,
        guardrails: mergeBucket(left.guardrails, right.guardrails),
        agentes: mergeBucket(left.agentes, right.agentes),
        guias: mergeBucket(left.guias, right.guias),
        pasos: mergeBucket(left.pasos, right.pasos),
        custom: mergeCustom(left.custom, right.custom),
    };
}

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

function agentGlobalNumber(agentId) {
    const idx = AGENT_ORDER.indexOf(agentId);
    return idx >= 0 ? idx + 1 : null;
}

function sortAgentsByOrder(agents) {
    return [...agents].sort(
        (a, b) => AGENT_ORDER.indexOf(a.id) - AGENT_ORDER.indexOf(b.id),
    );
}

function formatNum2(n) {
    return String(n).padStart(2, '0');
}

function agentRefCode(agentNum) {
    return formatNum2(agentNum);
}

function skillRefCode(agentNum, skillIdx) {
    return `${formatNum2(agentNum)}.${formatNum2(skillIdx)}`;
}

function pasoRefCode(agentNum, skillIdx, pasoNum) {
    return `${formatNum2(agentNum)}.${formatNum2(skillIdx)}.${formatNum2(pasoNum)}`;
}

const GUARDRAIL_EJEMPLOS = {
    g1: 'Si no hay auto en expediente, marca [PENDIENTE DE VERIFICAR] en lugar de citar sentencia o artículo.',
    g2: 'Si falta etapa, radicado o plazo Ley 906, pregunta antes de recomendar tutela, recurso o memorial.',
    g3: 'Distingue relato de víctima (narrado) de conclusión típica (inferida).',
    g4: 'Memorial, tutela o reporte a cliente siempre como borrador para su revisión y firma.',
    g5: 'Evita lenguaje que culpe a la víctima o exponga datos innecesarios del caso.',
    g6: 'No repite cédula, dirección o datos de salud sin necesidad probatoria.',
    g7: 'Consulta civil o laboral se declara fuera de alcance penal-víctimas.',
    g8: 'Cierra con aviso de que la salida requiere revisión profesional.',
    g9: 'Sin fecha de notificación o plazo verificado, no certifica oportunidad procesal.',
    g10: 'No sugiere descartar evidencia sin revisar custodia y preservación digital.',
};

const GUARDRAIL_PROTEGE = {
    g1: 'Integridad factual y normativa',
    g2: 'Oportunidad y datos procesales',
    g3: 'Trazabilidad probatoria',
    g4: 'HITL / firma profesional',
    g5: 'Dignidad de la víctima',
    g6: 'Datos sensibles',
    g7: 'Especialización del sistema',
    g8: 'Transparencia al despacho',
    g9: 'Términos Ley 906',
    g10: 'Cadena probatoria',
};

const FLUJO_CONSULTA = [
    {
        title: '1. Usted escribe',
        sub: 'Describe lo que necesita, como a un practicante del despacho.',
        color: '#64748b',
        icon: 'fa-comment-dots',
    },
    {
        title: '2. El equipo enruta',
        sub: 'El coordinador envía la consulta al especialista correcto.',
        color: '#2563eb',
        icon: 'fa-route',
    },
    {
        title: '3. Se ejecuta la tarea',
        sub: 'El agente sigue la guía y los pasos que usted aprueba en este portal.',
        color: '#d97706',
        icon: 'fa-list-check',
    },
    {
        title: '4. Usted revisa',
        sub: 'Recibe un borrador. Usted decide si lo firma, lo corrige o lo rechaza.',
        color: '#059669',
        icon: 'fa-signature',
    },
];

const PROTO_LAYERS = [
    {
        funnelClass: 'guia-funnel-layer--rules',
        title: 'REGLAS ESTRICTAS',
        countKey: 'guardrails',
        desc: '10 límites obligatorios en toda respuesta (no inventar normas, plazos 906, custodia probatoria, etc.).',
    },
    {
        funnelClass: 'guia-funnel-layer--roles',
        title: 'AGENTES',
        countKey: 'agentes',
        desc: '11 especialistas: coordinador, cronología, redacción, tutela, calidad, etc.',
    },
    {
        funnelClass: 'guia-funnel-layer--procs',
        title: 'TAREAS (GUÍAS)',
        countKey: 'skills',
        desc: '90 instrucciones concretas: cronología, memorial, audiencia, tutela…',
    },
    {
        funnelClass: 'guia-funnel-layer--steps',
        title: 'PASOS',
        countKey: 'pasos',
        desc: 'El detalle paso a paso dentro de cada tarea.',
    },
];

const GUIA_GLOSARIO = [
    {
        term: 'Regla estricta',
        desc: 'Límite global que aplica a todo el asistente (son 10). Van primero en la revisión.',
    },
    {
        term: 'Agente',
        desc: 'Un especialista del equipo digital: recibe, analiza, redacta o revisa calidad.',
    },
    {
        term: 'Tarea / guía',
        desc: 'Una instrucción concreta, por ejemplo «armar cronología» o «redactar memorial».',
    },
    {
        term: 'Paso',
        desc: 'Cada punto numerado dentro de una tarea. Van en orden (serie) o a la vez (paralelo) según el caso.',
    },
    {
        term: 'Entrada',
        desc: 'Datos que la tarea necesita para empezar: expediente, hechos, etapa del proceso.',
    },
    {
        term: 'Salida',
        desc: 'Lo que produce la tarea: borrador, matriz, alerta o análisis para su revisión.',
    },
    {
        term: 'Instrucción',
        desc: 'Texto que define el objetivo de la tarea (qué debe lograr el asistente).',
    },
    {
        term: 'Reglas de la guía',
        desc: 'Límites solo para esa tarea (distintos de las 10 reglas estrictas globales).',
    },
];

let catalog = {
    guardrails: [], agentes: [], skills: [], categorias: [],
    generated_at: '', totals: {}, intro: {},
};
let auditLog = { guardrails: {}, agentes: {}, guias: {}, pasos: {}, custom: null };
let currentModalTarget = null;
let currentAddTarget = null;
let detailsOpenState = { panels: [], skills: [] };

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

const GUIA_CONTEXT_PARTS = ['instruccion', 'tools', 'guardrails'];

function guiaContextKey(skillId, part) {
    return `${skillId}::${part}`;
}

function getSkillContextKeys(skill) {
    const keys = skill.audit_keys || {};
    return GUIA_CONTEXT_PARTS.map(part => keys[part] || guiaContextKey(skill.id, part));
}

function countEffectiveGuiasContext() {
    return (catalog.skills?.length || 0) * GUIA_CONTEXT_PARTS.length;
}

function countEffectiveItems() {
    return (
        getEffectiveGuardrails().length
        + catalog.agentes.length
        + countEffectiveGuiasContext()
        + countEffectivePasos()
    );
}

function escapeHtml(text) {
    const d = document.createElement('div');
    d.textContent = text ?? '';
    return d.innerHTML;
}

/** Convierte marcado inline seguro a HTML (negrita, cursiva, código). */
function renderRichHtml(text) {
    if (text == null || text === '') return '';
    let s = escapeHtml(String(text));
    s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    s = s.replace(/`([^`]+)`/g, '<code class="text-xs bg-slate-100 px-1 rounded">$1</code>');
    s = s.replace(/(?<!\*)\*([^*\n]+)\*(?!\*)/g, '<em>$1</em>');
    s = s.replace(/_([^_\n]+)_/g, '<em>$1</em>');
    return s;
}

function renderRichBlock(text) {
    if (!text || !String(text).trim()) {
        return '<p class="audit-meta m-0 text-slate-500">—</p>';
    }
    const raw = String(text).trim();
    const lines = raw.split('\n').map(l => l.trim()).filter(Boolean);
    const listLike = lines.length > 0 && lines.every(l => /^[-*•]\s/.test(l) || /^\d+\.\s/.test(l));
    if (listLike) {
        return `<ul class="audit-guia-list m-0 pl-5">${lines.map(l => {
            const cleaned = l.replace(/^[-*•]\s+/, '').replace(/^\d+\.\s+/, '');
            return `<li>${renderRichHtml(cleaned)}</li>`;
        }).join('')}</ul>`;
    }
    return `<p class="audit-body m-0 text-slate-800">${renderRichHtml(raw).replace(/\n/g, '<br>')}</p>`;
}

function apiBase() {
    const cfg = window.AUDIT_API_CONFIG || {};
    return String(cfg.base || '').replace(/\/$/, '');
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

function hasPersistedDecisions() {
    return decisionCount(buildPersistPayload()) > 0;
}

function saveAuditLogLocalOnly() {
    try {
        const email =
            typeof window.getAuditSessionEmail === 'function' ? window.getAuditSessionEmail() : null;
        const payload = buildPersistPayload();
        const key = storageKeyForEmail(email);
        localStorage.setItem(key, JSON.stringify(payload));
        // Espejo legacy + backup por correo (recuperación si un arreglo limpia la clave activa).
        localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
        if (email) {
            localStorage.setItem(`${STORAGE_KEY}:backup:${normalizeEmailKey(email)}`, JSON.stringify(payload));
        }
    } catch (err) {
        console.error('No se pudo guardar caché local:', err);
    }
}

function markProgressDirty() {
    progressUserDirty = true;
}

async function pushProgressToServer() {
    if (!serverSyncEnabled || !initialProgressSynced) return;
    if (!hasPersistedDecisions()) return;
    const email = typeof window.getAuditSessionEmail === 'function' ? window.getAuditSessionEmail() : null;
    if (!email) return;
    try {
        const res = await fetchAuditApi('/api/audit/progress', {
            method: 'PUT',
            body: JSON.stringify(buildPersistPayload()),
        });
        if (res.status === 409) {
            console.warn('Servidor rechazó regresión de progreso; resincronizando.');
            progressUserDirty = false;
            await syncProgressFromServer();
            renderAll();
            updatePersistStatus({ serverError: true });
            return;
        }
        if (!res.ok) {
            console.warn('No se pudo guardar en servidor:', res.status);
            updatePersistStatus({ serverError: true });
            return;
        }
        const data = await res.json();
        serverUpdatedAt = data.updated_at || new Date().toISOString();
        progressUserDirty = false;
        updatePersistStatus();
    } catch (err) {
        console.warn('Error al sincronizar con servidor:', err);
        updatePersistStatus({ serverError: true });
    }
}

function scheduleServerSave() {
    if (!serverSyncEnabled || !initialProgressSynced) return;
    if (saveDebounceTimer) clearTimeout(saveDebounceTimer);
    saveDebounceTimer = setTimeout(() => {
        saveDebounceTimer = null;
        pushProgressToServer();
    }, SAVE_DEBOUNCE_MS);
}

async function syncProgressFromServer() {
    loadAuditLog();
    const localBefore = buildPersistPayload();
    const localCount = decisionCount(localBefore);
    if (!serverSyncEnabled) {
        updatePersistStatus();
        return;
    }
    try {
        const res = await fetchAuditApi('/api/audit/progress');
        if (res.status === 404) {
            if (localCount > 0) {
                await pushProgressToServer();
            }
            updatePersistStatus();
            return;
        }
        if (!res.ok) {
            updatePersistStatus({ serverError: true });
            return;
        }
        const serverPayload = await res.json();
        const serverCount = decisionCount(serverPayload);
        // Nunca pisar decisiones locales con un servidor vacío o más pobre.
        const merged = mergePersistPayload(serverPayload, localBefore);
        const mergedCount = decisionCount(merged);
        if (applyPersistPayload(merged)) {
            saveAuditLogLocalOnly();
        }
        serverUpdatedAt = merged.savedAt || serverPayload.savedAt || null;
        if (mergedCount > serverCount || (localCount > 0 && serverCount === 0)) {
            progressUserDirty = true;
            await pushProgressToServer();
        }
        updatePersistStatus();
    } catch (err) {
        console.warn('No se pudo cargar progreso del servidor:', err);
        updatePersistStatus({ serverError: true });
    }
}

async function deleteServerProgress() {
    const email =
        typeof window.getAuditSessionEmail === 'function' ? window.getAuditSessionEmail() : null;
    const label = email ? ` (${email})` : '';
    const ok = confirm(
        `¿Borrar todo su progreso en el servidor${label}? Quedará una copia en el historial del servidor para recuperación de emergencia.`,
    );
    if (!ok) return;
    try {
        // Respaldo local de emergencia antes del borrado ARCO.
        try {
            const snap = buildPersistPayload();
            if (email && decisionCount(snap) > 0) {
                localStorage.setItem(
                    `${STORAGE_KEY}:deleted:${normalizeEmailKey(email)}:${Date.now()}`,
                    JSON.stringify(snap),
                );
            }
        } catch (_) { /* ignore */ }
        const res = await fetchAuditApi('/api/audit/progress', { method: 'DELETE' });
        if (res.status !== 404 && !res.ok) {
            alert('No se pudo borrar el progreso en el servidor.');
            return;
        }
        auditLog.guardrails = {};
        auditLog.agentes = {};
        auditLog.guias = {};
        auditLog.pasos = {};
        auditLog.custom = null;
        ensureCustom();
        localStorage.removeItem(STORAGE_KEY);
        localStorage.removeItem(STORAGE_KEY_LEGACY);
        localStorage.removeItem(STORAGE_KEY_LEGACY_V2);
        if (email) {
            localStorage.removeItem(storageKeyForEmail(email));
            localStorage.removeItem(`${STORAGE_KEY}:backup:${normalizeEmailKey(email)}`);
        }
        serverUpdatedAt = null;
        renderAll();
        updatePersistStatus();
        alert('Progreso borrado correctamente.');
    } catch (err) {
        console.error(err);
        alert('No se pudo conectar con el servidor.');
    }
}

function pasoKey(skillId, num) {
    return `${skillId}::${num}`;
}

function applyPersistPayload(parsed) {
    if (!parsed || typeof parsed !== 'object') return false;
    auditLog.guardrails = parsed.guardrails || {};
    auditLog.agentes = parsed.agentes || {};
    auditLog.guias = parsed.guias || {};
    auditLog.pasos = parsed.pasos || {};
    auditLog.custom = parsed.custom || null;
    ensureCustom();
    return true;
}

function buildPersistPayload() {
    return {
        version: 4,
        savedAt: new Date().toISOString(),
        catalogGeneratedAt: catalog.generated_at || null,
        guardrails: auditLog.guardrails,
        agentes: auditLog.agentes,
        guias: auditLog.guias,
        pasos: auditLog.pasos,
        custom: auditLog.custom,
    };
}

function updatePersistStatus(opts = {}) {
    const el = document.getElementById('audit-persist-status');
    if (!el) return;
    const email =
        typeof window.getAuditSessionEmail === 'function' ? window.getAuditSessionEmail() : null;
    let savedAt = serverUpdatedAt;
    if (!savedAt) {
        try {
            const raw = localStorage.getItem(STORAGE_KEY) || localStorage.getItem(STORAGE_KEY_LEGACY);
            if (raw) savedAt = JSON.parse(raw).savedAt;
        } catch (_) { /* ignore */ }
    }
    if (opts.serverError) {
        el.innerHTML =
            '<i class="fa-solid fa-triangle-exclamation mr-1 text-amber-500"></i> Sin conexión al servidor — progreso solo en caché local';
        return;
    }
    if (email && savedAt) {
        const when = new Date(savedAt);
        const label = Number.isNaN(when.getTime())
            ? savedAt
            : when.toLocaleString('es-CO', { dateStyle: 'short', timeStyle: 'short' });
        el.innerHTML = `<i class="fa-solid fa-cloud mr-1 text-emerald-500"></i> Guardado en servidor · <strong>${escapeHtml(email)}</strong> · última edición <strong>${escapeHtml(label)}</strong>`;
    } else if (savedAt) {
        const when = new Date(savedAt);
        const label = Number.isNaN(when.getTime())
            ? savedAt
            : when.toLocaleString('es-CO', { dateStyle: 'short', timeStyle: 'short' });
        el.innerHTML = `<i class="fa-solid fa-floppy-disk mr-1 text-emerald-500"></i> Progreso guardado · última edición <strong>${escapeHtml(label)}</strong>`;
    } else {
        el.innerHTML =
            '<i class="fa-solid fa-floppy-disk mr-1 text-slate-400"></i> Sin ediciones guardadas aún';
    }
}

function loadAuditLog() {
    const email =
        typeof window.getAuditSessionEmail === 'function' ? window.getAuditSessionEmail() : null;
    const keyed = email ? storageKeyForEmail(email) : null;
    const backup = email ? `${STORAGE_KEY}:backup:${normalizeEmailKey(email)}` : null;
    const keys = [keyed, backup, STORAGE_KEY, STORAGE_KEY_LEGACY, STORAGE_KEY_LEGACY_V2].filter(Boolean);
    let best = null;
    let bestCount = -1;
    for (const key of keys) {
        try {
            const raw = localStorage.getItem(key);
            if (!raw) continue;
            const parsed = JSON.parse(raw);
            if (!parsed || typeof parsed !== 'object') continue;
            const count = decisionCount(parsed);
            if (count > bestCount) {
                best = parsed;
                bestCount = count;
            } else if (best && count === bestCount && count > 0) {
                best = mergePersistPayload(best, parsed);
                bestCount = decisionCount(best);
            }
        } catch (_) { /* ignore */ }
    }
    if (best && applyPersistPayload(best)) {
        saveAuditLogLocalOnly();
    }
}

function saveAuditLog() {
    try {
        saveAuditLogLocalOnly();
        updatePersistStatus();
        if (progressUserDirty) scheduleServerSave();
    } catch (err) {
        console.error('No se pudo guardar el progreso:', err);
        const el = document.getElementById('audit-persist-status');
        if (el) {
            el.innerHTML = '<i class="fa-solid fa-triangle-exclamation mr-1 text-amber-500"></i> No se pudo guardar en este navegador. Exporte un respaldo JSON.';
        }
    }
}

function exportarProgresoJson() {
    saveAuditLog();
    const stamp = new Date().toISOString().slice(0, 10);
    const blob = new Blob([JSON.stringify(buildPersistPayload(), null, 2)], { type: 'application/json;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `auditoria-progreso-${stamp}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function importarProgresoJson(file) {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
        try {
            const parsed = JSON.parse(reader.result);
            const merged = mergePersistPayload(buildPersistPayload(), parsed);
            if (!applyPersistPayload(merged)) throw new Error('Formato inválido');
            markProgressDirty();
            saveAuditLog();
            renderAll();
            alert('Progreso restaurado correctamente (fusionado sin perder decisiones previas).');
        } catch (err) {
            console.error(err);
            alert('No se pudo leer el archivo. Verifique que sea un respaldo JSON del portal.');
        }
    };
    reader.readAsText(file);
}

function bindPersistUi() {
    document.getElementById('btn-export-progress')?.addEventListener('click', exportarProgresoJson);
    document.getElementById('btn-publish-config')?.addEventListener('click', () => publicarConfiguracion());
    document.getElementById('btn-delete-progress')?.addEventListener('click', deleteServerProgress);
    const importInput = document.getElementById('audit-import-file');
    document.getElementById('btn-import-progress')?.addEventListener('click', () => importInput?.click());
    importInput?.addEventListener('change', e => {
        const file = e.target.files?.[0];
        if (!file) return;
        const ok = confirm(
            '¿Restaurar el progreso desde este archivo? Se reemplazarán las decisiones actuales en este navegador.',
        );
        if (ok) importarProgresoJson(file);
        e.target.value = '';
    });
    window.addEventListener('storage', e => {
        if (!e.newValue) return;
        const email =
            typeof window.getAuditSessionEmail === 'function' ? window.getAuditSessionEmail() : null;
        const allowed = new Set(
            [STORAGE_KEY, STORAGE_KEY_LEGACY, storageKeyForEmail(email)].filter(Boolean),
        );
        if (!allowed.has(e.key)) return;
        try {
            const incoming = JSON.parse(e.newValue);
            const merged = mergePersistPayload(buildPersistPayload(), incoming);
            if (applyPersistPayload(merged)) renderAll();
        } catch (_) { /* ignore */ }
    });
}

function defaultDecision() {
    return { status: 'PENDIENTE', reason: '', solution: '' };
}

function getDecision(type, id) {
    if (!auditLog[type]) auditLog[type] = {};
    if (!auditLog[type][id]) auditLog[type][id] = defaultDecision();
    return auditLog[type][id];
}

function peekDecision(type, id) {
    const bucket = auditLog[type];
    if (bucket && bucket[id]) return bucket[id];
    return defaultDecision();
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
            <p><strong>Razón:</strong> ${renderRichHtml(reason)}</p>
            <p><strong>Solución:</strong> ${renderRichHtml(solution)}</p>
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
    const parts = [
        skillDisplayName(skill),
        skill.desc,
        skill.instruccion,
        skill.category,
        skill.name,
        skill.tools_text,
        ...(skill.guardrails || []),
    ];
    getEffectiveSteps(skill).forEach(st => parts.push(st.text));
    return parts.filter(Boolean).join(' ').toLowerCase();
}

function guiaContextLabel(part) {
    const labels = {
        instruccion: 'Instrucción tipo',
        tools: 'Herramientas de la guía',
        guardrails: 'Guardrails de esta guía',
    };
    return labels[part] || part;
}

function guiaContextBody(skill, part) {
    if (part === 'instruccion') {
        return renderRichBlock(skill.instruccion || skill.desc || '—');
    }
    if (part === 'tools') {
        const tools = skill.tools || [];
        if (tools.length) {
            return `<ul class="audit-guia-list m-0 pl-5">${tools.map(t => `<li>${renderRichHtml(t)}</li>`).join('')}</ul>`;
        }
        return `<p class="audit-meta m-0">${renderRichHtml(skill.tools_text || 'Sin herramientas obligatorias declaradas.')}</p>`;
    }
    if (part === 'guardrails') {
        const items = skill.guardrails || [];
        if (!items.length) return '<p class="audit-meta m-0">Sin guardrails específicos declarados en SKILL.md.</p>';
        return `<ul class="audit-guia-list m-0 pl-5">${items.map(g => `<li>${renderRichHtml(g)}</li>`).join('')}</ul>`;
    }
    return '—';
}

function buildGuiaContextCard(skill, part, options = {}) {
    const { agentNum = null, skillNum = null } = options;
    const key = (skill.audit_keys && skill.audit_keys[part]) || guiaContextKey(skill.id, part);
    const d = getDecision('guias', key);
    const refSuffix = { instruccion: 'I', tools: 'T', guardrails: 'G' }[part] || part[0].toUpperCase();
    const ref = agentNum && skillNum
        ? `<span class="audit-ref-code" title="Contexto ${guiaContextLabel(part)}">${skillRefCode(agentNum, skillNum)}.${refSuffix}</span>`
        : '';
    return `
        <div class="audit-guia-context-card audit-card p-4 rounded-xl border ${cardBorderClass(d.status)} mt-2"
            data-guia-key="${escapeHtml(key)}" data-skill-id="${escapeHtml(skill.id)}">
            <div class="flex flex-col md:flex-row md:items-start justify-between gap-3">
                <div class="flex-1">
                    <p class="audit-paso-label">${ref} ${escapeHtml(guiaContextLabel(part).toUpperCase())}</p>
                    <div class="audit-body text-slate-800">${guiaContextBody(skill, part)}</div>
                </div>
                <div class="shrink-0 audit-btn-row">${buildDecisionButtons('guias', key)}</div>
            </div>
            ${renderAdjustmentBlock(d.reason, d.solution)}
        </div>`;
}

function buildSkillContextSection(skill, options = {}) {
    const cards = GUIA_CONTEXT_PARTS.map(part => buildGuiaContextCard(skill, part, options)).join('');
    const source = skill.source_path
        ? `<p class="audit-meta mt-3 mb-0"><strong>Fuente canónica:</strong> <code class="text-xs bg-slate-100 px-1 rounded">${escapeHtml(skill.source_path)}</code></p>`
        : '';
    return `
        <div class="audit-guia-context-section space-y-0">
            <p class="audit-spec-heading mt-0 mb-2">REVISAR EN ESTA TAREA</p>
            ${cards}
            ${source}
        </div>`;
}

function bindGuiaContextCardsIn(container) {
    container.querySelectorAll('.audit-guia-context-card').forEach(card => {
        bindDecisionButtons(card, 'guias', card.dataset.guiaKey);
    });
}

function captureDetailsOpenState() {
    detailsOpenState = {
        panels: [...document.querySelectorAll('.agent-skills-details')].map((el, i) => ({
            agentId: el.closest('.audit-card[data-type="agentes"]')?.dataset.id || `idx-${i}`,
            open: el.open,
        })),
        skills: [...document.querySelectorAll('.agent-proc-details')].map(el => ({
            skillId: el.dataset.skillId || '',
            open: el.open,
        })),
    };
}

function restoreDetailsOpenState() {
    const panels = document.querySelectorAll('.agent-skills-details');
    detailsOpenState.panels.forEach((saved, i) => {
        const el = [...panels].find(
            p => p.closest('.audit-card[data-type="agentes"]')?.dataset.id === saved.agentId,
        ) || panels[i];
        if (el && saved.open) el.open = true;
    });
    detailsOpenState.skills.forEach(saved => {
        if (!saved.skillId) return;
        const el = document.querySelector(`.agent-proc-details[data-skill-id="${CSS.escape(saved.skillId)}"]`);
        if (el && saved.open) el.open = true;
    });
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
                <p class="audit-body">${renderRichHtml(item.desc)}</p>
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
                <p class="text-sm text-slate-600">${renderRichHtml(item.desc)}</p>
            </div>
            ${buildDecisionButtons(type, item.id)}
        </div>
        ${renderAdjustmentBlock(current.reason, current.solution)}`;

    bindDecisionButtons(card, type, item.id);
    return card;
}

function buildPasoCardsHtml(skill, options = {}) {
    const { showAddButton = true, agentNum = null, skillNum = null } = options;
    const steps = getEffectiveSteps(skill);

    const cards = steps.map(st => {
        const d = getDecision('pasos', st.key);
        const customBadge = st.custom
            ? '<span class="audit-badge audit-badge--new ml-1">Nuevo</span>'
            : '';
        const ref = agentNum && skillNum
            ? `<span class="audit-ref-code" title="Paso ${st.displayNum} de la guía ${skillRefCode(agentNum, skillNum)}">${pasoRefCode(agentNum, skillNum, st.displayNum)}</span>`
            : '';
        const pasoOrdinal = steps.length > 1
            ? ` <span class="audit-paso-ordinal">(${st.displayNum} de ${steps.length})</span>`
            : '';
        return `
            <div class="paso-card audit-card p-4 rounded-xl border ${cardBorderClass(d.status)} mt-2" data-paso-id="${escapeHtml(st.key)}" data-skill-id="${escapeHtml(skill.id)}">
                <div class="flex flex-col md:flex-row md:items-start justify-between gap-3">
                    <div class="flex-1">
                        <p class="audit-paso-label">${ref} PASO${pasoOrdinal}${pasoModoBadge(st.modo)}${customBadge}</p>
                        <p class="audit-body text-slate-800">${renderRichHtml(st.text)}</p>
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

    const agentNum = agentGlobalNumber(agent.id);
    const byId = Object.fromEntries(catalog.skills.map(s => [s.id, s]));
    const items = skillIds.map(sid => byId[sid]).filter(Boolean);

    const skillBlocks = items.map((skill, skillIdx) => {
        const skillNum = skillIdx + 1;
        const ref = agentNum ? skillRefCode(agentNum, skillNum) : '';
        const prog = skillStepProgress(skill);
        const displayName = skillDisplayName(skill);

        return `
            <div class="agent-proc-details audit-proc-card bg-white border border-slate-200 rounded-xl overflow-hidden mb-3"
                data-skill-id="${escapeHtml(skill.id)}"
                data-category="${escapeHtml(skill.category || '')}"
                data-search="${escapeHtml(procSearchText(skill))}">
                <div class="px-4 py-3 border-b border-slate-100 bg-slate-50/80 flex flex-wrap items-center gap-2">
                    ${ref ? `<span class="audit-ref-code" title="Guía ${skillNum} del agente ${agentNum}">${ref}</span>` : ''}
                    <span class="audit-proc-summary font-semibold text-slate-900">${escapeHtml(displayName)}</span>
                    <span class="audit-meta audit-skill-ordinal">Guía ${skillNum} de ${items.length}</span>
                    <span class="${procBadgeClass(prog)}">${prog.reviewed}/${prog.total} ítems</span>
                    <span class="audit-meta">${escapeHtml(skill.category || '')}</span>
                </div>
                <div class="px-4 pb-4 pt-3">
                    ${buildSkillFullContentHtml(skill)}
                    ${buildSkillContextSection(skill, { agentNum, skillNum })}
                    <p class="audit-spec-heading mt-4 mb-2">PASOS OPERATIVOS</p>
                    ${buildPasoCardsHtml(skill, { agentNum, skillNum })}
                </div>
            </div>`;
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
    const agentNum = agentGlobalNumber(agent.id);
    const card = document.createElement('div');
    card.className = `audit-card bg-white p-5 md:p-6 rounded-2xl border transition-all ${cardBorderClass(current.status)}`;
    card.dataset.type = 'agentes';
    card.dataset.id = agent.id;
    card.dataset.agentName = agent.name;
    card.dataset.search = agentSearchText(agent);

    const procCount = agent.skill_ids?.length || agent.skills_count || 0;
    const agentBadge = agentNum
        ? `<span class="audit-num-badge" title="Agente ${agentNum} de ${AGENT_ORDER.length}">${agentRefCode(agentNum)}</span>`
        : '';

    card.innerHTML = `
        <div class="flex flex-col gap-4">
            <div class="flex flex-col md:flex-row md:items-start justify-between gap-4">
                <div class="space-y-2 flex-1">
                    <div class="flex flex-wrap items-center gap-2">
                        ${agentBadge}
                        <p class="audit-subtitle audit-title-caps m-0">${escapeHtml(agentDisplayTitle(agent))}</p>
                    </div>
                    <p class="audit-meta"><strong>Referencia:</strong> Agente ${agentNum || '—'} de ${AGENT_ORDER.length}${procCount ? ` · ${procCount} guía${procCount === 1 ? '' : 's'} operativa${procCount === 1 ? '' : 's'} (${agentNum ? `${agentRefCode(agentNum)}.01–${skillRefCode(agentNum, procCount)}` : '—'})` : ''}</p>
                    <p class="audit-body">${renderRichHtml(agent.desc)}</p>
                    <p class="audit-meta"><strong>Problema que resuelve:</strong> ${renderRichHtml(agent.problema || '—')}</p>
                    ${agent.necesidad ? `<p class="audit-meta"><strong>Valor en el caso:</strong> ${renderRichHtml(agent.necesidad)}</p>` : ''}
                    <p class="audit-meta"><strong>No reemplaza:</strong> ${renderRichHtml(agent.no_reemplaza || '—')}</p>
                </div>
                <div class="audit-btn-row shrink-0">${buildDecisionButtons('agentes', agent.id)}</div>
            </div>
            ${buildAgentSkillsPanel(agent, openProcedures)}
            ${renderAdjustmentBlock(current.reason, current.solution)}
        </div>`;

    bindDecisionButtons(card, 'agentes', agent.id);
    bindGuiaContextCardsIn(card);
    bindPasoCardsIn(card);
    return card;
}

function skillStepProgress(skill) {
    const steps = getEffectiveSteps(skill);
    const contextKeys = getSkillContextKeys(skill);
    let reviewed = 0;
    let adjust = 0;
    contextKeys.forEach(key => {
        const d = getDecision('guias', key);
        if (isReviewed(d)) reviewed += 1;
        if (d.status === 'AJUSTAR') adjust += 1;
    });
    steps.forEach(st => {
        const d = getDecision('pasos', st.key);
        if (isReviewed(d)) reviewed += 1;
        if (d.status === 'AJUSTAR') adjust += 1;
    });
    return { total: contextKeys.length + steps.length, reviewed, adjust };
}

function renderAgentes() {
    const c = document.getElementById('container-agentes');
    c.innerHTML = '';
    const order = ['coordinacion', 'especialista', 'calidad'];
    order.forEach(grupo => {
        const agents = sortAgentsByOrder(catalog.agentes.filter(a => a.grupo === grupo));
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
    sortAgentsByOrder(catalog.agentes).forEach(a => {
        const num = agentGlobalNumber(a.id);
        const o = document.createElement('option');
        o.value = a.id;
        o.textContent = num ? `${agentRefCode(num)} · ${agentDisplayTitle(a)}` : agentDisplayTitle(a);
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

function formatSkillFieldHtml(text) {
    return renderRichBlock(text);
}

function buildSkillFieldRow(label, html) {
    return `<div class="audit-skill-field"><p class="audit-paso-label mb-1">${escapeHtml(label)}</p>${html}</div>`;
}

function buildSkillFullContentHtml(skill) {
    const ejecutores = (skill.agentes_ejecutores || []).join(', ') || '—';
    const tierBadge = skill.tier
        ? `<span class="audit-badge ml-2 text-[10px] uppercase tracking-wide px-2 py-0.5 rounded bg-slate-200 text-slate-700">${escapeHtml(skill.tier)}</span>`
        : '';
    const fields = [
        buildSkillFieldRow('PROPÓSITO', formatSkillFieldHtml(skill.purpose || skill.desc)),
        buildSkillFieldRow('INSTRUCCIÓN TIPO (lista de aprobación)', formatSkillFieldHtml(skill.instruccion)),
        buildSkillFieldRow('ENTRADAS', formatSkillFieldHtml(skill.inputs)),
        buildSkillFieldRow('SALIDAS', formatSkillFieldHtml(skill.outputs)),
    ];
    if (skill.rol) fields.push(buildSkillFieldRow('ROL EN EL AGENTE', formatSkillFieldHtml(skill.rol)));
    if (skill.no_duplicar) fields.push(buildSkillFieldRow('NO DUPLICAR', formatSkillFieldHtml(skill.no_duplicar)));
    if (skill.handoff) fields.push(buildSkillFieldRow('HANDOFF', formatSkillFieldHtml(skill.handoff)));
    if (skill.riesgo) fields.push(buildSkillFieldRow('RIESGO SI SE OMITE', formatSkillFieldHtml(skill.riesgo)));

    return `
        <div class="audit-skill-full border border-slate-200 rounded-xl p-4 mb-4 bg-white">
            <p class="audit-spec-heading mt-0 mb-3">CONTENIDO DEL SKILL (SKILL.md)</p>
            <p class="audit-meta mb-3">
                <strong>Quién la ejecuta:</strong> ${escapeHtml(ejecutores)}${tierBadge}
                · <strong>Destinatario:</strong> ${escapeHtml(skill.destinatario || '—')}
                · <strong>Flujo:</strong> ${skillFlujoLabel(skill)}
            </p>
            <div class="audit-skill-fields space-y-3">${fields.join('')}</div>
        </div>`;
}

function buildSkillSpecHtml(skill) {
    return buildSkillFullContentHtml(skill);
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
                <strong>Ejemplo:</strong> Usted pide un <em>memorial de impulso</em>.
                El coordinador lo envía al redactor de escritos; este sigue la tarea «redactar memorial penal» paso a paso;
                calidad revisa el borrador y se lo entrega para que usted lo firme o lo devuelva con correcciones.
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
                    <li><strong>Primer contacto:</strong> entiende qué pide el despacho (memorial, cronología, tutela, etc.).</li>
                    <li><strong>Envío correcto:</strong> manda el caso al especialista y la tarea adecuados.</li>
                    <li><strong>Pide lo que falta:</strong> no concluye si faltan datos importantes.</li>
                </ul>
            </div>
            <div class="guia-team-card guia-team-card--spec">
                <p class="guia-label" style="color:#7c3aed">ESPECIALISTAS</p>
                <h4 class="audit-title-caps">NUEVE ÁREAS JURÍDICAS</h4>
                <p>Nueve especialistas hacen el trabajo jurídico: hechos, tipicidad, víctimas, prueba, audiencias, escritos, seguimiento y tutela.</p>
                <div class="guia-chips">${specChips}</div>
            </div>
            <div class="guia-team-card guia-team-card--qual">
                <p class="guia-label" style="color:#d97706">CONTROL DE CALIDAD</p>
                <h4 class="audit-title-caps">${escapeHtml(agentDisplayTitle(calidad) || 'REVISIÓN DE CALIDAD Y CONTROL DE RIESGOS JURÍDICOS')}</h4>
                <p>${escapeHtml(calidad?.desc || 'Revisa coherencia y riesgos antes de entregarle el borrador.')}</p>
                <ul class="guia-value-list guia-team-value">
                    <li><strong>Última revisión:</strong> nada llega a usted sin pasar por calidad.</li>
                    <li><strong>Detecta errores:</strong> citas inventadas, incoherencias y riesgos procesales.</li>
                    <li><strong>Protege a la víctima:</strong> confidencialidad, tono adecuado y no revictimización.</li>
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
        const total = countEffectiveItems();
        const base = intro.textContent.split(' El contador')[0].split(' Catálogo:')[0].trim();
        intro.textContent = `${base} El contador superior muestra cuántos de los ${total} ítems lleva revisados.`;
    }
    if (note && catalog.categorias?.length) {
        const n = catalog.intro?.guias_operativas || catalog.intro?.skills || catalog.skills?.length || 0;
        note.textContent = `Las ${n} tareas se revisan dentro de cada agente, en el panel de abajo.`;
    }
}

function updateProgress() {
    let reviewed = 0;
    const total = countEffectiveItems();

    getEffectiveGuardrails().forEach(g => {
        if (isReviewed(peekDecision('guardrails', g.id))) reviewed += 1;
    });
    catalog.agentes.forEach(a => {
        if (isReviewed(peekDecision('agentes', a.id))) reviewed += 1;
    });
    catalog.skills.forEach(s => {
        getSkillContextKeys(s).forEach(key => {
            if (isReviewed(peekDecision('guias', key))) reviewed += 1;
        });
        getEffectiveSteps(s).forEach(st => {
            if (isReviewed(peekDecision('pasos', st.key))) reviewed += 1;
        });
    });

    const countSection = (type, items, getId) => {
        let secRev = 0;
        items.forEach(item => {
            if (isReviewed(peekDecision(type, getId(item)))) secRev += 1;
        });
        return { pending: items.length - secRev, total: items.length };
    };

    const g = countSection('guardrails', getEffectiveGuardrails(), x => x.id);
    const ag = countSection('agentes', catalog.agentes, x => x.id);

    let pasosPending = 0;
    let guiasCtxPending = 0;
    catalog.skills.forEach(s => {
        getSkillContextKeys(s).forEach(key => {
            if (!isReviewed(peekDecision('guias', key))) guiasCtxPending += 1;
        });
        getEffectiveSteps(s).forEach(st => {
            if (!isReviewed(peekDecision('pasos', st.key))) pasosPending += 1;
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
        const pendingItems = guiasCtxPending + pasosPending;
        const parts = [];
        if (guiasCtxPending) parts.push(`${guiasCtxPending} ctx.`);
        if (pasosPending) parts.push(`${pasosPending} pasos`);
        pasosBadge.textContent = pendingItems ? parts.join(' · ') : '';
        pasosBadge.className = `text-[10px] px-1.5 py-0.5 rounded ${pendingItems ? 'bg-amber-900/50 text-amber-300' : 'hidden'}`;
    }

    const chip = document.getElementById('progress-chip');
    if (chip) {
        chip.innerHTML = `<i class="fa-solid fa-chart-pie mr-1 text-blue-400"></i> <strong>${reviewed}</strong> de ${total} revisados`;
    }
}

function renderAll() {
    captureDetailsOpenState();
    renderGuardrails();
    renderAgentes();
    restoreDetailsOpenState();
    applyFilters();
    updateProgress();
    saveAuditLog();
}

function removeGuardrail(id) {
    markProgressDirty();
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
    markProgressDirty();
    const custom = ensureCustom();
    const id = `custom_g_${Date.now()}`;
    custom.guardrailsAdded.push({ id, name, desc, custom: true });
    renderAll();
}

function removePaso(pasoKeyVal, skillId) {
    markProgressDirty();
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
    markProgressDirty();
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
    markProgressDirty();
    const current = getDecision(type, id);
    if (status === 'PENDIENTE') {
        auditLog[type][id] = defaultDecision();
    } else if (status === 'APROBADO') {
        if (current.status === 'APROBADO') {
            auditLog[type][id] = defaultDecision();
        } else {
            auditLog[type][id] = {
                status: 'APROBADO',
                reason: current.reason || '',
                solution: current.solution || '',
            };
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
        markProgressDirty();
        auditLog[type][id] = { status: 'AJUSTAR', reason, solution };
        closeModal();
        renderAll();
    }
}

function countGuiasContextByStatus() {
    const counts = { APROBADO: 0, AJUSTAR: 0, PENDIENTE: 0 };
    catalog.skills.forEach(s => {
        getSkillContextKeys(s).forEach(key => {
            const stt = getDecision('guias', key).status;
            counts[stt] = (counts[stt] || 0) + 1;
        });
    });
    return counts;
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
    publicarConfiguracion({ silent: false, thenExportMd: true });
}

let configPublishedMeta = null;

async function loadConfigStatus() {
    try {
        const res = await fetchAuditApi('/api/audit/config/status');
        if (res.ok) configPublishedMeta = await res.json();
    } catch (_) {
        configPublishedMeta = null;
    }
    updateConfigStatusBanner();
}

function updateConfigStatusBanner() {
    const el = document.getElementById('config-status-chip');
    if (!el) return;
    const meta = configPublishedMeta;
    if (!meta?.published) {
        el.innerHTML = '<i class="fa-solid fa-triangle-exclamation mr-1 text-amber-400"></i> Sin config publicada';
        el.className = 'text-xs bg-amber-950/50 border border-amber-800 px-3 py-2 rounded-lg text-amber-200 hidden md:block';
        return;
    }
    el.innerHTML = `<i class="fa-solid fa-shield-check mr-1 text-emerald-400"></i> Config v<strong>${meta.version}</strong> · ${escapeHtml(meta.published_at || '')}`;
    el.className = 'text-xs bg-slate-800 border border-slate-700 px-3 py-2 rounded-lg text-slate-300 hidden md:block';
}

async function publicarConfiguracion({ silent = false, thenExportMd = false } = {}) {
    if (!silent && !thenExportMd) {
        const ok = confirm(
            'Publicar fija la configuración aprobada para el servicio (local y producción).\n\n'
            + 'Todos los ítems deben estar en APROBADO. ¿Continuar?',
        );
        if (!ok) return { ok: false, cancelled: true };
    }

    await pushProgressToServer();
    const res = await fetchAuditApi('/api/audit/config/publish', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(buildPersistPayload()),
    });
    let data = {};
    try {
        data = await res.json();
    } catch (_) { /* ignore */ }

    if (!res.ok) {
        const msg = data.detail || 'No se pudo publicar. Revise que todos los ítems estén APROBADO.';
        if (!silent) alert(msg);
        return { ok: false, error: msg };
    }

    await loadCatalog();
    await loadConfigStatus();
    renderAll();

    if (thenExportMd) {
        exportarMarkdownFile();
        if (!silent) {
            alert(`Configuración publicada (v${data.published?.version}). Se descargó el reporte .md.`);
        }
    } else if (!silent) {
        alert(`Configuración publicada (v${data.published?.version}). El servicio ya usa esta versión.`);
    }
    return { ok: true, data };
}

function exportarMarkdownFile() {
    const genAt = catalog.generated_at || new Date().toISOString();
    let md = `# Reporte Consolidado de Aprobación Técnico-Legal\n\n`;
    md += `**Generado en:** ${genAt} (Auditoría de Instrucciones)\n`;
    md += `**Principio profesional:** La IA propone; usted revisa, ajusta y aprueba.\n\n`;
    const guiasN = catalog.intro?.guias_operativas || catalog.intro?.skills || 90;
    const ctxN = countEffectiveGuiasContext();
    md += `Sistema penal-víctimas Colombia — ${catalog.intro?.agentes || 11} agentes, ${guiasN} guías operativas, ${ctxN} contextos auditables de guía, ${countEffectivePasos()} pasos.\n\n---\n\n`;

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
        const agents = sortAgentsByOrder(catalog.agentes.filter(a => a.grupo === grupo));
        if (!agents.length) return;
        md += `### ${GROUP_LABELS[grupo] || grupo}\n\n`;
        agents.forEach(a => {
            const agentNum = agentGlobalNumber(a.id);
            const state = getDecision('agentes', a.id);
            const agentLabel = agentNum ? `Agente ${agentRefCode(agentNum)} — ${agentDisplayTitle(a)}` : agentDisplayTitle(a);
            md += `#### ${agentLabel}\n`;
            md += `- **Propósito:** ${a.desc}\n`;
            if (a.necesidad) md += `- **Valor en el caso:** ${a.necesidad}\n`;
            md += `- **Problema que resuelve:** ${a.problema || '—'}\n`;
            md += `- **No reemplaza:** ${a.no_reemplaza || '—'}\n`;
            md += `- **Estado del agente:** ${state.status}\n`;
            if (state.reason) md += `- **Defectos:** _${state.reason}_\n- **Instrucción:** _${state.solution}_\n`;

            const skillIds = a.skill_ids || [];
            skillIds.forEach((sid, skillIdx) => {
                const s = byId[sid];
                if (!s) return;
                const skillNum = skillIdx + 1;
                const ref = agentNum ? skillRefCode(agentNum, skillNum) : '';
                md += `\n##### GUÍA OPERATIVA ${ref ? `${ref} — ` : ''}${skillDisplayName(s)}\n`;
                md += `- **Entrada:** ${s.inputs || '—'}\n`;
                md += `- **Salida:** ${s.outputs || '—'}\n`;
                md += `- **Ejecuta:** ${(s.agentes_ejecutores || []).join(', ') || '—'}\n`;
                md += `- **Destinatario:** ${s.destinatario || '—'}\n`;
                md += `- **Flujo:** ${skillFlujoLabel(s)}\n`;
                md += `- **Para qué sirve:** ${s.desc || s.instruccion || '—'}\n`;
                if (s.source_path) md += `- **Fuente canónica:** \`${s.source_path}\`\n`;
                GUIA_CONTEXT_PARTS.forEach(part => {
                    const key = (s.audit_keys && s.audit_keys[part]) || guiaContextKey(s.id, part);
                    const ctxState = getDecision('guias', key);
                    let body = '';
                    if (part === 'instruccion') body = s.instruccion || s.desc || '—';
                    else if (part === 'tools') body = s.tools_text || (s.tools || []).join(', ') || '—';
                    else body = (s.guardrails || []).join(' · ') || '—';
                    md += `###### Contexto — ${guiaContextLabel(part)}\n`;
                    md += `- **Contenido:** ${body}\n- **Estado:** ${ctxState.status}\n`;
                    if (ctxState.reason) md += `- **Razón:** _${ctxState.reason}_\n- **Ajuste:** _${ctxState.solution}_\n`;
                });
                getEffectiveSteps(s).forEach(st => {
                    const stState = getDecision('pasos', st.key);
                    const tag = st.custom ? ' *(agregado por el despacho)*' : '';
                    const modo = st.modo === 'paralelo' ? ' [PARALELO]' : '';
                    const pasoRef = agentNum ? pasoRefCode(agentNum, skillNum, st.displayNum) : `${st.displayNum}`;
                    md += `###### Paso ${pasoRef}${modo}${tag}\n`;
                    md += `- **Texto:** ${st.text}\n- **Estado:** ${stState.status}\n`;
                    if (stState.reason) md += `- **Razón:** _${stState.reason}_\n- **Ajuste:** _${stState.solution}_\n`;
                });
            });
            md += `\n`;
        });
    });

    const g = countByStatus('guardrails', getEffectiveGuardrails(), x => x.id);
    const ag = countByStatus('agentes', catalog.agentes, x => x.id);
    const gx = countGuiasContextByStatus();
    const ps = countPasosByStatus();
    md += `---\n\n## Resumen Ejecutivo\n\n`;
    md += `| Sección | APROBADO | AJUSTAR | PENDIENTE |\n|---|---|---|---|\n`;
    md += `| Reglas estrictas | ${g.APROBADO} | ${g.AJUSTAR} | ${g.PENDIENTE} |\n`;
    md += `| Agentes del equipo | ${ag.APROBADO} | ${ag.AJUSTAR} | ${ag.PENDIENTE} |\n`;
    md += `| Contexto de guías | ${gx.APROBADO} | ${gx.AJUSTAR} | ${gx.PENDIENTE} |\n`;
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

const EXEC_TEMPLATE_LABELS = {
    cronologia: 'Cronología y hechos',
    tutela: 'Acción de tutela',
    audiencia: 'Preparación de audiencia',
    generico: 'Consulta general',
};

const EXEC_STATUS_LABELS = {
    pending_approval: 'Pendiente de aprobación',
    approved: 'Aprobado',
    executing: 'En ejecución',
    done: 'Completado',
    failed: 'Fallido',
    rejected: 'Rechazado',
    draft: 'Borrador',
};

function execStatusBadge(status) {
    const labels = {
        pending_approval: 'bg-amber-100 text-amber-900',
        approved: 'bg-blue-100 text-blue-900',
        executing: 'bg-indigo-100 text-indigo-900',
        done: 'bg-emerald-100 text-emerald-900',
        failed: 'bg-red-100 text-red-900',
        rejected: 'bg-slate-200 text-slate-700',
    };
    const cls = labels[status] || 'bg-slate-100 text-slate-700';
    const text = EXEC_STATUS_LABELS[status] || status;
    return `<span class="inline-block px-2 py-0.5 rounded-full text-xs font-semibold ${cls}">${escapeHtml(text)}</span>`;
}

function formatExecDate(iso) {
    if (!iso) return '—';
    try {
        return new Date(iso).toLocaleString('es-CO', { dateStyle: 'short', timeStyle: 'short' });
    } catch {
        return String(iso).slice(0, 16);
    }
}

async function loadExecutionDashboard() {
    const kpiEl = document.getElementById('execution-dashboard-kpis');
    const tableEl = document.getElementById('execution-dashboard-table');
    const statusEl = document.getElementById('execution-dashboard-by-status');
    const templateEl = document.getElementById('execution-dashboard-by-template');
    const generatedEl = document.getElementById('execution-dashboard-generated');
    if (!kpiEl || !tableEl) return;

    kpiEl.innerHTML = '<p class="text-sm text-slate-500 col-span-full">Cargando planes…</p>';
    tableEl.innerHTML = '';
    if (statusEl) statusEl.innerHTML = '';
    if (templateEl) templateEl.innerHTML = '';

    try {
        const res = await fetchAuditApi('/api/audit/execution-plans/dashboard');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        if (generatedEl) {
            generatedEl.textContent = data.generated_at
                ? `Actualizado: ${formatExecDate(data.generated_at)}`
                : '';
        }

        const cards = [
            ['Total', data.total || 0, 'slate'],
            ['Pendientes', data.pending_approval || 0, 'amber'],
            ['Aprobados', data.approved || 0, 'blue'],
            ['En ejecución', data.executing || 0, 'indigo'],
            ['Completados', data.done || 0, 'emerald'],
            ['Fallidos / rechazados', (data.failed || 0) + (data.rejected || 0), 'red'],
        ];
        kpiEl.innerHTML = cards
            .map(
                ([label, value, tone]) => `
            <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
                <p class="text-xs uppercase tracking-wide text-slate-500 m-0">${escapeHtml(label)}</p>
                <p class="text-2xl font-bold text-${tone}-700 m-0 mt-1">${value}</p>
            </div>`,
            )
            .join('');

        if (statusEl && data.by_status) {
            const rows = Object.entries(data.by_status)
                .sort((a, b) => b[1] - a[1])
                .map(
                    ([st, n]) =>
                        `<li class="flex justify-between text-sm py-1 border-b border-slate-50 last:border-0">
                            <span>${execStatusBadge(st)}</span>
                            <span class="font-semibold text-slate-700">${n}</span>
                        </li>`,
                )
                .join('');
            statusEl.innerHTML = `<p class="text-xs font-bold uppercase text-slate-500 mb-2">Por estado</p><ul class="m-0 p-0 list-none">${rows || '<li class="text-sm text-slate-500">Sin datos</li>'}</ul>`;
        }

        if (templateEl && data.by_template) {
            const rows = Object.entries(data.by_template)
                .sort((a, b) => b[1] - a[1])
                .map(
                    ([kind, n]) =>
                        `<li class="flex justify-between text-sm py-1 border-b border-slate-50 last:border-0">
                            <span>${escapeHtml(EXEC_TEMPLATE_LABELS[kind] || kind)}</span>
                            <span class="font-semibold text-slate-700">${n}</span>
                        </li>`,
                )
                .join('');
            templateEl.innerHTML = `<p class="text-xs font-bold uppercase text-slate-500 mb-2">Por plantilla</p><ul class="m-0 p-0 list-none">${rows || '<li class="text-sm text-slate-500">Sin datos</li>'}</ul>`;
        }

        const rows = data.recent || [];
        if (!rows.length) {
            tableEl.innerHTML =
                '<p class="text-sm text-slate-500 p-4 m-0">Aún no hay planes registrados. Use el chat en <a href="/abogado" class="text-blue-600 underline">/abogado</a> para generar el primero.</p>';
            return;
        }

        const body = rows
            .map((row) => {
                const kind = EXEC_TEMPLATE_LABELS[row.template_kind] || row.template_kind || '—';
                const exportUrl = auditApiUrl(
                    `/api/audit/execution-plans/${encodeURIComponent(row.plan_id)}/export.md`,
                );
                const flags = [
                    row.pattern_reused ? 'patrón reutilizado' : '',
                    row.has_result ? 'con resultado' : '',
                    row.stream_events_count ? `${row.stream_events_count} eventos SSE` : '',
                ]
                    .filter(Boolean)
                    .join(' · ');
                return `<tr class="border-t border-slate-100 hover:bg-slate-50/80">
                    <td class="px-3 py-3 text-xs font-mono align-top">${escapeHtml(row.plan_id)}</td>
                    <td class="px-3 py-3 align-top">${execStatusBadge(row.status)}</td>
                    <td class="px-3 py-3 text-sm align-top">${escapeHtml(kind)}</td>
                    <td class="px-3 py-3 text-sm text-slate-700 align-top max-w-xs">
                        <div class="font-medium line-clamp-2">${escapeHtml(row.objective || '—')}</div>
                        <div class="text-xs text-slate-500 mt-1 line-clamp-1" title="${escapeHtml(row.user_message_preview || '')}">Consulta: ${escapeHtml(row.user_message_preview || '—')}</div>
                    </td>
                    <td class="px-3 py-3 text-xs text-slate-600 align-top">
                        ${row.steps_count || 0} pasos · ${row.agents_count || 0} agentes<br>
                        <span class="text-slate-400">${escapeHtml(row.channel || 'web')}</span>
                    </td>
                    <td class="px-3 py-3 text-xs text-slate-500 align-top whitespace-nowrap">${formatExecDate(row.updated_at)}</td>
                    <td class="px-3 py-3 text-xs align-top">
                        ${flags ? `<span class="text-slate-500">${escapeHtml(flags)}</span><br>` : ''}
                        <a class="text-emerald-700 hover:underline font-semibold" href="${exportUrl}" download>Exportar .md</a>
                    </td>
                </tr>`;
            })
            .join('');

        tableEl.innerHTML = `<div class="overflow-x-auto"><table class="min-w-full text-left">
            <thead class="bg-slate-50 text-xs uppercase text-slate-500">
                <tr>
                    <th class="px-3 py-3">Plan ID</th>
                    <th class="px-3 py-3">Estado</th>
                    <th class="px-3 py-3">Plantilla</th>
                    <th class="px-3 py-3">Objetivo / consulta</th>
                    <th class="px-3 py-3">Alcance</th>
                    <th class="px-3 py-3">Actualizado</th>
                    <th class="px-3 py-3">Detalle</th>
                </tr>
            </thead>
            <tbody>${body}</tbody>
        </table></div>`;
    } catch (err) {
        console.warn('Dashboard de planes no disponible:', err);
        kpiEl.innerHTML =
            '<p class="text-sm text-amber-700 col-span-full">No se pudo cargar el dashboard. Inicie sesión en el portal y verifique que el agente esté en ejecución.</p>';
        tableEl.innerHTML = '';
    }
}

function bindExecutionDashboardRefresh() {
    const btn = document.getElementById('execution-dashboard-refresh');
    if (!btn || btn.dataset.bound) return;
    btn.dataset.bound = '1';
    btn.addEventListener('click', () => {
        btn.disabled = true;
        loadExecutionDashboard().finally(() => {
            btn.disabled = false;
        });
    });
}

function bindExecutionDashboardReset() {
    const btn = document.getElementById('execution-dashboard-reset');
    if (!btn || btn.dataset.bound) return;
    btn.dataset.bound = '1';
    btn.addEventListener('click', async () => {
        const ok = window.confirm(
            '¿Reiniciar el historial de planes de ejecución?\n\n' +
                'Se borrarán todos los registros del dashboard (contadores y tabla). ' +
                'No afecta su progreso de auditoría de instrucciones ni el chat en curso, ' +
                'pero ya no podrá exportar .md de planes anteriores.\n\n' +
                'Esta acción no se puede deshacer.',
        );
        if (!ok) return;
        btn.disabled = true;
        try {
            const res = await fetchAuditApi('/api/audit/execution-plans', { method: 'DELETE' });
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                window.alert(err.detail || 'No se pudo reiniciar el historial de planes.');
                return;
            }
            const data = await res.json();
            await loadExecutionDashboard();
            window.alert(
                data.deleted
                    ? `Historial reiniciado: se eliminaron ${data.deleted} registro(s).`
                    : 'El historial ya estaba vacío.',
            );
        } catch (err) {
            console.warn(err);
            window.alert('Error de conexión al reiniciar planes.');
        } finally {
            btn.disabled = false;
        }
    });
}

async function loadCatalog() {
    const sources = [
        { url: auditApiUrl('/api/audit/catalog'), label: 'API' },
        { url: './audit-data.json', label: 'estático' },
    ];
    let lastErr = null;
    for (const { url } of sources) {
        try {
            const res = await fetch(url, { credentials: 'include' });
            if (!res.ok) {
                lastErr = new Error(`${url}: HTTP ${res.status}`);
                continue;
            }
            const data = await res.json();
            if (!data?.skills?.length) {
                lastErr = new Error(`${url}: catálogo vacío`);
                continue;
            }
            catalog = data;
            return true;
        } catch (err) {
            lastErr = err;
        }
    }
    const chip = document.getElementById('progress-chip');
    if (chip) chip.textContent = 'Error al cargar catálogo de auditoría';
    console.error(lastErr);
    return false;
}

function bindCatalogUi() {
    document.getElementById('generated-at').textContent = catalog.generated_at || '—';
    const buildEl = document.getElementById('build-generated-at');
    if (buildEl && catalog.generated_at) {
        buildEl.textContent = `· catálogo ${catalog.generated_at}`;
        buildEl.classList.remove('hidden');
    }
    renderGuiaCompleta();
    populateFilters();
    document.getElementById('search-input')?.addEventListener('input', applyFilters);
    document.getElementById('filter-category')?.addEventListener('change', applyFilters);
    document.getElementById('filter-agent')?.addEventListener('change', applyFilters);
    bindPersistUi();
    bindExecutionDashboardRefresh();
    bindExecutionDashboardReset();
}

async function init() {
    ensureCustom();
    const catalogOk = await loadCatalog();
    if (!catalogOk) return;

    bindCatalogUi();

    const authOk = typeof window.waitForAuditAuth === 'function'
        ? await window.waitForAuditAuth()
        : true;
    if (!authOk) return;

    serverSyncEnabled = false;
    await syncProgressFromServer();
    initialProgressSynced = true;
    serverSyncEnabled = true;
    progressUserDirty = false;

    renderAll();
    updatePersistStatus();
    await loadConfigStatus();
    void loadExecutionDashboard();
}

window.publicarConfiguracion = publicarConfiguracion;

window.setDecision = setDecision;
window.triggerAdjustment = triggerAdjustment;
window.closeModal = closeModal;
window.saveModalAdjustment = saveModalAdjustment;
window.closeAddModal = closeAddModal;
window.saveAddModal = saveAddModal;
window.openAddGuardrailModal = openAddGuardrailModal;
window.openAddPasoModal = openAddPasoModal;
window.exportarProgresoJson = exportarProgresoJson;
window.exportarMarkdown = exportarMarkdown;

document.addEventListener('DOMContentLoaded', init);

window.addEventListener('audit-session-ended', () => {
    auditLog.guardrails = {};
    auditLog.agentes = {};
    auditLog.guias = {};
    auditLog.pasos = {};
    auditLog.custom = null;
    ensureCustom();
    serverUpdatedAt = null;
    serverSyncEnabled = true;
    initialProgressSynced = false;
    progressUserDirty = false;
});
