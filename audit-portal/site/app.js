/* Editor de configuración de agentes — equipos → agentes → Prompt/Skills/Guardrails */

(function () {

    const GROUP_ORDER = ['coordinacion', 'especialista', 'calidad'];
    const GROUP_LABELS = {
        coordinacion: 'COORDINACIÓN',
        especialista: 'ESPECIALISTAS',
        calidad: 'CALIDAD',
    };

    /** Legacy agent IDs → canonical (stored traces / old catalog keys). */
    const LEGACY_AGENT_ALIASES = {
        coordinador_expediente_penal: 'coordinador_caso',
        gerente: 'coordinador_caso',
        gerente_caso: 'coordinador_caso',
        analista_cronologia_hechos_penales: 'analista_cronologia_hechos',
        analista_tipicidad_y_responsabilidad_penal: 'analista_responsabilidad_tipicidad',
        analista_ruta_procesal_ley906: 'analista_ruta_procesal',
        gestor_evidencia_y_soporte_probatorio: 'analista_evidencia',
        preparador_estrategico_audiencias_penales: 'analista_audiencias',
        redactor_documentos_juridicos_penales: 'redactor_documentos_juridicos',
        gestor_seguimiento_procesal_penal: 'analista_seguimiento_procesal',
    };

    function resolveAgentId(agentId) {
        if (!agentId) return '';
        return LEGACY_AGENT_ALIASES[agentId] || agentId;
    }

    /** Etiquetas de pestaña (MAYÚSCULAS). Preferir nombre_corto del catálogo si existe. */
    const AGENT_TAB_LABEL = {
        coordinador_caso: 'COORDINADOR DEL CASO',
        coordinador_expediente_penal: 'COORDINADOR DEL CASO', // legacy alias
        analista_cronologia_hechos: 'CRONOLOGÍA HECHOS',
        analista_cronologia_hechos_penales: 'CRONOLOGÍA HECHOS', // legacy
        analista_responsabilidad_tipicidad: 'TIPICIDAD RESPONSABILIDAD',
        analista_tipicidad_y_responsabilidad_penal: 'TIPICIDAD RESPONSABILIDAD', // legacy
        analista_ruta_procesal: 'RUTA PROCESAL',
        analista_ruta_procesal_ley906: 'RUTA PROCESAL', // legacy
        analista_representacion_victimas: 'REPRESENTACIÓN VÍCTIMAS',
        analista_evidencia: 'EVIDENCIA PRUEBA',
        gestor_evidencia_y_soporte_probatorio: 'EVIDENCIA PRUEBA', // legacy
        analista_audiencias: 'AUDIENCIAS PENALES',
        preparador_estrategico_audiencias_penales: 'AUDIENCIAS PENALES', // legacy
        redactor_documentos_juridicos: 'REDACTOR DOCUMENTOS',
        redactor_documentos_juridicos_penales: 'REDACTOR DOCUMENTOS', // legacy
        analista_seguimiento_procesal: 'SEGUIMIENTO PROCESAL',
        gestor_seguimiento_procesal_penal: 'SEGUIMIENTO PROCESAL', // legacy
        analista_calidad_juridica: 'CALIDAD JURÍDICA',
    };

    /** Índice editable cargado desde GET /api/audit/config/catalog. */
    let configIndex = { prompt: [], guardrail: [], skill: [], agent_guardrail: [] };
    let agentsMeta = { agents: [], groups: {}, global: { prompt_key: 'sistema' } };
    let editorMode = 'agent'; // agent | sistema
    let workspaceView = 'editor'; // editor | map
    let currentGroup = 'coordinacion';
    let currentAgentId = null;
    let currentSection = null; // prompt | skills | guardrails | null hasta elegir hijo
    let currentGuardClass = null; // input | output | tools | null hasta elegir en el layer Guardrails
    let currentPromptPart = null; // funcion | trabajo | reglas | comunicacion | null
    let currentKey = null;
    let loaded = null;
    let dirty = false;
    let sessionReady = false;
    let sharedBadgeForKey = null;
    let uiBound = false;
    let bootInFlight = null;
    let selectGen = 0;
    let connectorRaf = 0;
    let connectorTimer = 0;
    let connectorPositioning = false;
    let traySyncDepth = 0;
    let draftSaveTimer = null;
    let noteIdleTimer = null;
    let noteManual = false;

    const DRAFT_PREFIX = 'audit-cfg-draft:v1:';

    function draftStorageKey(kind, key) {
        return `${DRAFT_PREFIX}${kind}:${key}`;
    }

    function readDraft(kind, key) {
        try {
            const raw = localStorage.getItem(draftStorageKey(kind, key));
            if (!raw) return null;
            const parsed = JSON.parse(raw);
            if (!parsed || typeof parsed.content !== 'string') return null;
            return parsed;
        } catch {
            return null;
        }
    }

    function writeDraft(kind, key, payload) {
        try {
            localStorage.setItem(
                draftStorageKey(kind, key),
                JSON.stringify({
                    content: payload.content,
                    note: payload.note || '',
                    noteManual: Boolean(payload.noteManual),
                    baseVersion: payload.baseVersion || 0,
                    savedAt: Date.now(),
                }),
            );
        } catch {
            /* quota / private mode */
        }
    }

    function clearDraft(kind, key) {
        try {
            localStorage.removeItem(draftStorageKey(kind, key));
        } catch {
            /* ignore */
        }
    }

    function persistEditorDraft() {
        if (!loaded) return;
        const editor = $('cfg-editor');
        if (!editor || editor.disabled) return;
        syncStructuredToEditor();
        const content = getEditorContent();
        const note = $('cfg-note') ? $('cfg-note').value : '';
        writeDraft(loaded.kind, loaded.key, {
            content,
            note,
            noteManual,
            baseVersion: loaded.version || 0,
        });
        setDirty(!contentEquals(content, baselineContent()));
    }

    function scheduleDraftPersist() {
        clearTimeout(draftSaveTimer);
        draftSaveTimer = setTimeout(persistEditorDraft, 180);
    }

    function kindNoteLabel(kind) {
        if (kind === 'skill') return 'skill';
        if (kind === 'agent_guardrail' || kind === 'guardrail') return 'guardrail';
        return 'prompt';
    }

    /** Resumen breve del diff para el campo Nota (máx. 240). */
    function summarizeEdit(before, after, kind) {
        const a = String(before || '');
        const b = String(after || '');
        if (a === b) return '';

        const aLines = a.split('\n');
        const bLines = b.split('\n');
        const countMap = (lines) => {
            const m = new Map();
            for (const line of lines) m.set(line, (m.get(line) || 0) + 1);
            return m;
        };
        const ma = countMap(aLines);
        const mb = countMap(bLines);
        let added = 0;
        let removed = 0;
        for (const [line, ca] of ma) {
            const cb = mb.get(line) || 0;
            if (ca > cb) removed += ca - cb;
        }
        for (const [line, cb] of mb) {
            const ca = ma.get(line) || 0;
            if (cb > ca) added += cb - ca;
        }

        const parts = [];
        if (added && removed) parts.push(`+${added}/-${removed} líneas`);
        else if (added) parts.push(`+${added} líneas`);
        else if (removed) parts.push(`-${removed} líneas`);
        else {
            let edits = 0;
            const n = Math.min(aLines.length, bLines.length);
            for (let i = 0; i < n; i += 1) {
                if (aLines[i] !== bLines[i]) edits += 1;
            }
            parts.push(edits ? `${edits} líneas modificadas` : 'ajuste de texto');
        }

        let hint = '';
        const maxLines = Math.max(aLines.length, bLines.length);
        for (let i = 0; i < maxLines; i += 1) {
            if ((aLines[i] || '') === (bLines[i] || '')) continue;
            const snip = String(bLines[i] || aLines[i] || '')
                .trim()
                .replace(/\s+/g, ' ');
            if (!snip || snip.startsWith('<!--')) continue;
            hint = snip.slice(0, 72);
            break;
        }

        let note = `Edición de ${kindNoteLabel(kind)}: ${parts.join(', ')}`;
        if (hint) note += ` · «${hint}${hint.length >= 72 ? '…' : ''}»`;
        return note.slice(0, 240);
    }

    function applyAutoNote() {
        if (!loaded || noteManual) return;
        const editor = $('cfg-editor');
        const noteEl = $('cfg-note');
        if (!editor || !noteEl || editor.disabled) return;
        syncStructuredToEditor();
        const before = loaded.content || '';
        const after = getEditorContent();
        if (contentEquals(after, before)) {
            noteEl.value = '';
            persistEditorDraft();
            return;
        }
        noteEl.value = summarizeEdit(before, after, loaded.kind);
        persistEditorDraft();
    }

    function scheduleAutoNote() {
        clearTimeout(noteIdleTimer);
        noteIdleTimer = setTimeout(applyAutoNote, 1000);
    }

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

    function autosizeField(el) {
        if (!el || el.tagName !== 'TEXTAREA') return;
        el.style.height = 'auto';
        el.style.height = `${Math.max(el.scrollHeight, 44)}px`;
    }

    function autosizeEditor() {
        autosizeField($('cfg-editor'));
        autosizeField($('cfg-field-mision'));
        autosizeField($('cfg-field-instrucciones'));
        autosizeField($('cfg-skill-extras'));
        document.querySelectorAll('#cfg-form-anatomy textarea.cfg-anatomy-input').forEach(autosizeField);
        document.querySelectorAll('#cfg-form-anatomy .cfg-rich').forEach(autosizeRich);
        document.querySelectorAll('#cfg-form-skill textarea.cfg-anatomy-input').forEach(autosizeField);
        document.querySelectorAll('#cfg-form-skill .cfg-rich').forEach(autosizeRich);
        document.querySelectorAll('#cfg-form-guard textarea.cfg-anatomy-input').forEach(autosizeField);
        document.querySelectorAll('#cfg-form-guard .cfg-rich').forEach(autosizeRich);
    }

    /**
     * Interno: orden de secciones ## en el markdown (compatibilidad).
     * UI: 4 pestañas con campos estructurados.
     */
    const ANATOMY_SECTION_IDS = [
        'role',
        'tasks',
        'boundaries',
        'voice_rules',
        'tool_routing',
        'good_behavior',
        'bad_behavior',
        'few_shots',
        'fallback_behavior',
        'closing_rule',
    ];

    const ANATOMY_UI_GROUPS = [
        {
            id: 'funcion',
            label: 'Función y alcance',
            trayLabel: 'Función',
            hint: 'Título/rol del asistente y hasta dónde llega su función.',
            tone: '',
        },
        {
            id: 'trabajo',
            label: 'Tareas de trabajo',
            trayLabel: 'Tareas',
            hint: 'Pasos en serie y en orden. El agente los completa uno tras otro.',
            tone: '',
        },
        {
            id: 'reglas',
            label: 'Responsabilidades y obligaciones',
            trayLabel: 'Responsabilidades',
            hint: 'Agregue cada responsabilidad. Clasifique si es prohibición, obligación, error o faltante.',
            tone: 'risk',
        },
        {
            id: 'comunicacion',
            label: 'Estilo de comunicación',
            trayLabel: 'Estilo',
            hint: 'Personalidad y modo completo de comunicación, campo por campo.',
            tone: 'voice',
        },
    ];

    const RESP_TYPES = [
        { id: 'boundaries', label: 'Prohibición' },
        { id: 'good_behavior', label: 'Obligación' },
        { id: 'bad_behavior', label: 'Error grave' },
        { id: 'fallback_behavior', label: 'Si faltan datos' },
    ];

    const COMM_FIELDS = [
        {
            id: 'personalidad',
            label: 'Personalidad',
            hint: 'Cómo es el asistente: serio, prudente, claro, de despacho…',
            rows: 3,
            section: 'voice_rules',
            marker: 'Personalidad',
        },
        {
            id: 'modo',
            label: 'Modo de comunicación',
            hint: 'Cómo habla de extremo a extremo: una sola voz, formalidad, ritmo…',
            rows: 3,
            section: 'voice_rules',
            marker: 'Modo de comunicación',
        },
        {
            id: 'tono',
            label: 'Tono',
            hint: 'Registro lingüístico: técnico, llano, empático sin coloquialismos…',
            rows: 2,
            section: 'voice_rules',
            marker: 'Tono',
        },
        {
            id: 'transparencia',
            label: 'Transparencia con el abogado',
            hint: 'Qué puede decir del equipo interno y qué no (IDs técnicos, roles…)',
            rows: 3,
            section: 'voice_rules',
            marker: 'Transparencia',
        },
        {
            id: 'nivel_detalle',
            label: 'Nivel de detalle',
            hint: 'Qué tan breve o exhaustiva debe ser cada respuesta.',
            rows: 2,
            section: 'voice_rules',
            marker: 'Nivel de detalle',
        },
        {
            id: 'cierre',
            label: 'Frase de cierre',
            hint: 'Aviso fijo al terminar cada respuesta (revisión humana).',
            rows: 2,
            section: 'closing_rule',
            marker: null,
        },
        {
            id: 'ejemplos',
            label: 'Ejemplos de respuesta',
            hint: 'Consulta → respuesta esperada. Mejora la precisión del agente.',
            rows: 8,
            section: 'few_shots',
            marker: null,
        },
    ];

    function escapeHtmlText(s) {
        return String(s || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }


    /** Markdown liviano → HTML para edición visual (negrita sin ver **). */
    function mdToEditorHtml(md) {
        const raw = String(md || '').replace(/\r\n/g, '\n').trimEnd();
        if (!raw.trim()) return '<div><br></div>';
        const lines = raw.split('\n');
        const out = [];
        let i = 0;
        const inline = (t) => escapeHtmlText(t)
            .replace(/`([^`]+)`/g, '<span class="md-term">$1</span>')
            .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
            .replace(/(^|[^*])\*([^*\n]+)\*(?!\*)/g, '$1<em>$2</em>');

        while (i < lines.length) {
            const line = lines[i];
            const trimmed = line.trim();
            if (!trimmed) {
                out.push('<div><br></div>');
                i += 1;
                continue;
            }
            const h = trimmed.match(/^(#{1,4})\s+(.*)$/);
            if (h) {
                out.push(`<div class="md-h"><strong>${inline(h[2])}</strong></div>`);
                i += 1;
                continue;
            }
            if (/^[-*]\s+/.test(trimmed)) {
                const items = [];
                while (i < lines.length && /^[-*]\s+/.test(lines[i].trim())) {
                    items.push(`<li>${inline(lines[i].trim().replace(/^[-*]\s+/, ''))}</li>`);
                    i += 1;
                }
                out.push(`<ul>${items.join('')}</ul>`);
                continue;
            }
            if (/^\d+[.)]\s+/.test(trimmed)) {
                const items = [];
                while (i < lines.length && /^\d+[.)]\s+/.test(lines[i].trim())) {
                    items.push(`<li>${inline(lines[i].trim().replace(/^\d+[.)]\s+/, ''))}</li>`);
                    i += 1;
                }
                out.push(`<ol>${items.join('')}</ol>`);
                continue;
            }
            out.push(`<div>${inline(trimmed)}</div>`);
            i += 1;
        }
        return out.join('');
    }

    /** HTML del editor visual → markdown liviano al guardar. */
    function editorHtmlToMd(html) {
        const wrap = document.createElement('div');
        wrap.innerHTML = String(html || '');

        const inlineMd = (node) => {
            let s = '';
            node.childNodes.forEach((child) => {
                if (child.nodeType === Node.TEXT_NODE) {
                    s += child.textContent || '';
                    return;
                }
                if (child.nodeType !== Node.ELEMENT_NODE) return;
                const tag = child.tagName.toLowerCase();
                const inner = inlineMd(child);
                if (tag === 'strong' || tag === 'b') s += `**${inner}**`;
                else if (tag === 'em' || tag === 'i') s += `*${inner}*`;
                else if (tag === 'code' || (tag === 'span' && child.classList && child.classList.contains('md-term'))) s += '`' + inner + '`';
                else if (tag === 'br') s += '\n';
                else s += inner;
            });
            return s;
        };

        const blocks = [];
        const pushBlock = (s) => {
            const t = String(s || '').replace(/[ \t]+\n/g, '\n').trimEnd();
            if (t !== '') blocks.push(t);
            else if (blocks.length) blocks.push('');
        };

        const walkBlocks = (parent) => {
            parent.childNodes.forEach((node) => {
                if (node.nodeType === Node.TEXT_NODE) {
                    const t = (node.textContent || '').trim();
                    if (t) pushBlock(t);
                    return;
                }
                if (node.nodeType !== Node.ELEMENT_NODE) return;
                const tag = node.tagName.toLowerCase();
                if (tag === 'ul') {
                    [...node.children].forEach((li) => {
                        if (li.tagName.toLowerCase() === 'li') pushBlock(`- ${inlineMd(li).trim()}`);
                    });
                    return;
                }
                if (tag === 'ol') {
                    let n = 1;
                    [...node.children].forEach((li) => {
                        if (li.tagName.toLowerCase() === 'li') {
                            pushBlock(`${n}. ${inlineMd(li).trim()}`);
                            n += 1;
                        }
                    });
                    return;
                }
                if (tag === 'div' || tag === 'p' || tag === 'h1' || tag === 'h2' || tag === 'h3' || tag === 'h4' || tag === 'section') {
                    if (node.classList && node.classList.contains('md-h')) {
                        pushBlock(`### ${inlineMd(node).trim()}`);
                    } else {
                        pushBlock(inlineMd(node).trim() || '');
                    }
                    return;
                }
                if (tag === 'br') {
                    pushBlock('');
                    return;
                }
                pushBlock(inlineMd(node).trim());
            });
        };

        walkBlocks(wrap);
        return blocks.join('\n').replace(/\n{3,}/g, '\n\n').trim() + (blocks.length ? '\n' : '');
    }

    function autosizeRich(el) {
        if (!el) return;
        el.style.height = 'auto';
        el.style.minHeight = '4.5rem';
        el.style.height = `${Math.max(el.scrollHeight, 72)}px`;
    }

    function richEditorHtml(id, placeholder, extraClass = '') {
        const ph = escapeHtmlText(placeholder || '');
        return `
            <div class="cfg-rich-wrap">
                <div
                    id="${id}"
                    class="cfg-field-control cfg-rich cfg-anatomy-input ${extraClass}"
                    contenteditable="false"
                    role="textbox"
                    aria-multiline="true"
                    data-placeholder="${ph}"
                ></div>
            </div>
        `;
    }

    function readRichMd(id) {
        const el = $(id);
        if (!el) return '';
        if (el.classList.contains('cfg-rich')) {
            return editorHtmlToMd(el.innerHTML).replace(/\n$/, '');
        }
        return (el.value || '').trim();
    }

    function writeRichMd(id, md) {
        const el = $(id);
        if (!el) return;
        const text = String(md || '');
        if (el.classList.contains('cfg-rich')) {
            el.innerHTML = mdToEditorHtml(text);
            el.classList.toggle('is-empty', !text.trim());
            autosizeRich(el);
            return;
        }
        el.value = text;
        autosizeField(el);
    }

    let fmtTarget = null;

    function isFmtTarget(el) {
        if (!el || el.nodeType !== Node.ELEMENT_NODE) return false;
        if (el.classList.contains('cfg-rich') && el.getAttribute('contenteditable') === 'true') return true;
        if (el.id === 'cfg-editor' && !el.disabled) return true;
        return false;
    }

    function syncFmtBarState() {
        const bar = $('cfg-fmt-bar');
        if (!bar) return;
        const active = isFmtTarget(fmtTarget);
        bar.dataset.disabled = active ? 'false' : 'true';
        bar.querySelectorAll('.cfg-fmt-btn[data-fmt="bold"], .cfg-fmt-btn[data-fmt="italic"]').forEach((btn) => {
            const cmd = btn.dataset.fmt;
            let on = false;
            try {
                on = active && fmtTarget.classList.contains('cfg-rich') && document.queryCommandState(cmd);
            } catch (_) {
                on = false;
            }
            btn.classList.toggle('is-active', Boolean(on));
        });
    }

    function wrapTextareaSelection(el, before, after) {
        const start = el.selectionStart ?? 0;
        const end = el.selectionEnd ?? 0;
        const val = el.value || '';
        const selected = val.slice(start, end) || 'texto';
        const next = val.slice(0, start) + before + selected + after + val.slice(end);
        el.value = next;
        const selStart = start + before.length;
        el.setSelectionRange(selStart, selStart + selected.length);
        el.dispatchEvent(new Event('input', { bubbles: true }));
    }

    function insertTextareaLinePrefix(el, prefix) {
        const start = el.selectionStart ?? 0;
        const val = el.value || '';
        const lineStart = val.lastIndexOf('\n', Math.max(0, start - 1)) + 1;
        el.value = val.slice(0, lineStart) + prefix + val.slice(lineStart);
        const pos = start + prefix.length;
        el.setSelectionRange(pos, pos);
        el.dispatchEvent(new Event('input', { bubbles: true }));
    }

    function applyTextFormat(fmt) {
        const el = fmtTarget;
        if (!isFmtTarget(el)) return;
        el.focus();

        if (el.classList.contains('cfg-rich')) {
            const run = (cmd, value) => {
                try {
                    document.execCommand(cmd, false, value);
                } catch (_) { /* ignore */ }
            };
            if (fmt === 'bold') run('bold');
            else if (fmt === 'italic') run('italic');
            else if (fmt === 'ul') run('insertUnorderedList');
            else if (fmt === 'ol') run('insertOrderedList');
            else if (fmt === 'undo') run('undo');
            else if (fmt === 'redo') run('redo');
            else if (fmt === 'clear') run('removeFormat');
            else if (fmt === 'code') {
                const sel = window.getSelection();
                const text = sel && !sel.isCollapsed ? sel.toString() : 'término';
                run('insertHTML', `<span class="md-term">${escapeHtmlText(text)}</span>`);
            } else if (fmt === 'h3') {
                const sel = window.getSelection();
                const text = (sel && !sel.isCollapsed ? sel.toString() : 'Título').trim() || 'Título';
                run('insertHTML', `<div class="md-h"><strong>${escapeHtmlText(text)}</strong></div><div><br></div>`);
            }
            el.classList.toggle('is-empty', !editorHtmlToMd(el.innerHTML).trim());
            autosizeRich(el);
            el.dispatchEvent(new Event('input', { bubbles: true }));
            syncFmtBarState();
            return;
        }

        if (el.id === 'cfg-editor') {
            if (fmt === 'bold') wrapTextareaSelection(el, '**', '**');
            else if (fmt === 'italic') wrapTextareaSelection(el, '*', '*');
            else if (fmt === 'code') wrapTextareaSelection(el, '`', '`');
            else if (fmt === 'h3') insertTextareaLinePrefix(el, '### ');
            else if (fmt === 'ul') insertTextareaLinePrefix(el, '- ');
            else if (fmt === 'ol') insertTextareaLinePrefix(el, '1. ');
            else if (fmt === 'clear') {
                const start = el.selectionStart ?? 0;
                const end = el.selectionEnd ?? 0;
                if (end > start) {
                    const plain = (el.value || '').slice(start, end).replace(/[*_`#]+/g, '');
                    el.setRangeText(plain, start, end, 'select');
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }
            // undo/redo: browser nativo del textarea
            else if (fmt === 'undo') {
                try { document.execCommand('undo'); } catch (_) { /* ignore */ }
            } else if (fmt === 'redo') {
                try { document.execCommand('redo'); } catch (_) { /* ignore */ }
            }
            syncFmtBarState();
        }
    }

    function wireFmtToolbar() {
        const bar = $('cfg-fmt-bar');
        if (!bar || bar.dataset.wired === '1') return;
        bar.dataset.wired = '1';
        bar.addEventListener('mousedown', (e) => {
            // Evita que el botón robe el foco del editor antes del click.
            if (e.target.closest('.cfg-fmt-btn')) e.preventDefault();
        });
        bar.addEventListener('click', (e) => {
            const btn = e.target.closest('.cfg-fmt-btn');
            if (!btn || !bar.contains(btn)) return;
            applyTextFormat(btn.dataset.fmt);
        });
        document.addEventListener('focusin', (e) => {
            const t = e.target;
            if (isFmtTarget(t)) {
                fmtTarget = t;
                syncFmtBarState();
            }
        });
        document.addEventListener('selectionchange', () => {
            if (fmtTarget && fmtTarget.classList.contains('cfg-rich')) syncFmtBarState();
        });
        syncFmtBarState();
    }

    function activateAnatomyTab(groupId, { fromTray = false } = {}) {
        const hasSelection = ANATOMY_UI_GROUPS.some((group) => group.id === groupId);
        const selectedId = hasSelection ? groupId : null;
        currentPromptPart = selectedId;

        document.querySelectorAll('.cfg-anatomy-tab, .prompt-part-tab').forEach((tab) => {
            const id = tab.dataset.group || tab.dataset.part;
            const active = Boolean(selectedId) && id === selectedId;
            tab.classList.toggle('active', active);
            tab.setAttribute('aria-selected', active ? 'true' : 'false');
            tab.tabIndex = active ? 0 : -1;
        });

        const pick = $('cfg-prompt-pick');
        const fields = $('cfg-anatomy-fields');
        if (pick) pick.classList.toggle('hidden', Boolean(selectedId));
        if (fields) fields.classList.toggle('hidden', !selectedId);

        ANATOMY_UI_GROUPS.forEach((group) => {
            const card = $(`cfg-anatomy-card-${group.id}`);
            if (!card) return;
            const active = Boolean(selectedId) && group.id === selectedId;
            card.classList.toggle('hidden', !active);
            card.setAttribute('aria-hidden', active ? 'false' : 'true');
        });
        autosizeEditor();
        scheduleGroupConnector();
    }

    function ensurePromptPartTabsBuilt() {
        const host = $('prompt-part-tabs');
        if (!host) return;
        if (host.dataset.built === '1') return;
        host.dataset.built = '1';
        host.innerHTML = '';
        ANATOMY_UI_GROUPS.forEach((group) => {
            const tab = document.createElement('button');
            tab.type = 'button';
            tab.className = 'prompt-part-tab';
            tab.dataset.part = group.id;
            tab.textContent = group.trayLabel || group.label;
            tab.title = group.label;
            tab.addEventListener('click', () => selectPromptPart(group.id));
            host.appendChild(tab);
        });
    }

    async function selectPromptPart(partId) {
        ensureAnatomyFormBuilt();
        ensurePromptPartTabsBuilt();
        currentPromptPart = partId;
        activateAnatomyTab(partId, { fromTray: true });
        setSectionTabs();
        const group = ANATOMY_UI_GROUPS.find((g) => g.id === partId);
        const label = $('cfg-current-label');
        if (label && group) {
            const agent = agentById(currentAgentId);
            const base = agent?.nombre_corto || displayName(currentAgentId) || 'Prompt';
            label.textContent = `${base} · ${group.label}`;
        }
        scheduleGroupConnector();
    }

    function ensureAnatomyFormBuilt() {
        const host = $('cfg-anatomy-fields');
        const nav = $('cfg-anatomy-nav');
        if (!host) return;
        if (host.dataset.built === 'form-v2') return;
        host.dataset.built = 'form-v2';
        if (nav) nav.innerHTML = '';
        host.innerHTML = '';

        ANATOMY_UI_GROUPS.forEach((group, idx) => {
            const n = idx + 1;
            if (nav) {
                const tab = document.createElement('button');
                tab.type = 'button';
                tab.className = 'cfg-anatomy-tab';
                tab.dataset.group = group.id;
                tab.id = `cfg-anatomy-tab-${group.id}`;
                tab.setAttribute('role', 'tab');
                tab.setAttribute('aria-controls', `cfg-anatomy-card-${group.id}`);
                tab.setAttribute('aria-selected', 'false');
                tab.textContent = group.label;
                tab.addEventListener('click', () => activateAnatomyTab(group.id));
                nav.appendChild(tab);
            }
            const card = document.createElement('section');
            card.className = 'cfg-anatomy-card';
            card.id = `cfg-anatomy-card-${group.id}`;
            card.setAttribute('role', 'tabpanel');
            card.setAttribute('aria-labelledby', `cfg-anatomy-tab-${group.id}`);
            if (group.tone) card.setAttribute('data-tone', group.tone);
            const hint = escapeHtmlText(group.hint || '');
            card.innerHTML = `
                <div class="cfg-anatomy-card-head">
                    <span class="cfg-anatomy-num" aria-hidden="true">${n}</span>
                    <div class="cfg-anatomy-card-copy">
                        <h4 class="cfg-anatomy-title">${escapeHtmlText(group.label)}</h4>
                        ${hint ? `<p class="cfg-anatomy-hint">${hint}</p>` : ''}
                    </div>
                </div>
                <div id="cfg-anatomy-body-${group.id}" class="cfg-anatomy-body"></div>
            `;
            host.appendChild(card);
        });

        buildFuncionFields();
        buildPasosFields();
        buildResponsabilidadesFields();
        buildComunicacionFields();
        if (currentPromptPart) activateAnatomyTab(currentPromptPart, { fromTray: true });
        else activateAnatomyTab(null);
    }

    function buildFuncionFields() {
        const body = $('cfg-anatomy-body-funcion');
        if (!body) return;
        body.innerHTML = `
            <div class="cfg-anatomy-field">
                <label class="cfg-anatomy-field-label" for="cfg-anatomy-funcion">Función (título / rol)</label>
                <p class="cfg-anatomy-field-hint">Quién es, qué cargo cumple y qué gerencia frente al abogado.</p>
                ${richEditorHtml('cfg-anatomy-funcion', 'Ej.: Coordinador del Caso; único interlocutor; coordina el caso de extremo a extremo…')}
            </div>
            <div class="cfg-anatomy-field">
                <label class="cfg-anatomy-field-label" for="cfg-anatomy-alcance">Alcance de su función</label>
                <p class="cfg-anatomy-field-hint">Qué casos cubre, límites frente al abogado y qué queda fuera.</p>
                ${richEditorHtml('cfg-anatomy-alcance', 'Ej.: Solo penal-víctimas Colombia (Ley 906). No firma. Fuera de alcance: otros asuntos…')}
            </div>
        `;
    }

    function buildPasosFields() {
        const body = $('cfg-anatomy-body-trabajo');
        if (!body) return;
        body.innerHTML = `
            <div class="cfg-anatomy-field">
                <div class="cfg-anatomy-list-head">
                    <div>
                        <p class="cfg-anatomy-field-label">Pasos</p>
                        <p class="cfg-anatomy-field-hint">En serie y en orden. El agente debe completarlos uno tras otro.</p>
                    </div>
                    <button type="button" class="cfg-anatomy-add" data-action="add-paso">+ Agregar paso</button>
                </div>
                <div id="cfg-anatomy-pasos" class="cfg-anatomy-list"></div>
            </div>
            <div class="cfg-anatomy-field">
                <label class="cfg-anatomy-field-label" for="cfg-anatomy-regla-loop">Regla del ciclo</label>
                <p class="cfg-anatomy-field-hint">Opcional. Qué hacer si un paso no se cumple (ej. no avanzar sin verificación).</p>
                ${richEditorHtml('cfg-anatomy-regla-loop', 'Ej.: Si la verificación no pasa, no delegue; pida lo faltante al abogado…')}
            </div>
            <div class="cfg-anatomy-field">
                <label class="cfg-anatomy-field-label" for="cfg-anatomy-tool-routing">A qué área interna pedir ayuda</label>
                <p class="cfg-anatomy-field-hint">Cuándo consultar cada especialista / tool interna.</p>
                ${richEditorHtml('cfg-anatomy-tool-routing', 'Ej.: Cronología → analista_cronologia_hechos…')}
            </div>
        `;
        renderPasosList([]);
    }

    function renderPasosList(steps) {
        const host = $('cfg-anatomy-pasos');
        if (!host) return;
        const items = Array.isArray(steps) && steps.length ? steps : [''];
        host.innerHTML = items.map((text, idx) => `
            <div class="cfg-anatomy-item" data-paso-idx="${idx}">
                <span class="cfg-anatomy-item-num" aria-hidden="true">${idx + 1}</span>
                ${richEditorHtml(`cfg-paso-${idx}`, `Describa el paso ${idx + 1}…`, 'cfg-paso-text')}
                <button type="button" class="cfg-anatomy-remove" data-action="remove-paso" aria-label="Quitar paso" ${items.length <= 1 ? 'disabled' : ''}>×</button>
            </div>
        `).join('');
        host.querySelectorAll('.cfg-paso-text').forEach((el, idx) => writeRichMd(el.id, items[idx] || ''));
    }

    function readPasosFromDom() {
        return [...document.querySelectorAll('#cfg-anatomy-pasos .cfg-paso-text')]
            .map((el) => readRichMd(el.id))
            .filter(Boolean);
    }

    function buildResponsabilidadesFields() {
        const body = $('cfg-anatomy-body-reglas');
        if (!body) return;
        body.innerHTML = `
            <div class="cfg-anatomy-field">
                <div class="cfg-anatomy-list-head">
                    <div>
                        <p class="cfg-anatomy-field-label">Responsabilidades</p>
                        <p class="cfg-anatomy-field-hint">Agregue una por una. Indique si es prohibición, obligación, error o faltante.</p>
                    </div>
                    <button type="button" class="cfg-anatomy-add" data-action="add-resp">+ Agregar responsabilidad</button>
                </div>
                <div id="cfg-anatomy-responsabilidades" class="cfg-anatomy-list"></div>
            </div>
        `;
        renderResponsabilidadesList([]);
    }

    function renderResponsabilidadesList(items) {
        const host = $('cfg-anatomy-responsabilidades');
        if (!host) return;
        const list = Array.isArray(items) && items.length ? items : [{ type: 'good_behavior', text: '' }];
        const opts = RESP_TYPES.map((t) => `<option value="${t.id}">${t.label}</option>`).join('');
        host.innerHTML = list.map((item, idx) => `
            <div class="cfg-anatomy-item cfg-anatomy-item-resp" data-resp-idx="${idx}">
                <select class="cfg-anatomy-select cfg-resp-type" disabled>
                    ${opts}
                </select>
                ${richEditorHtml(`cfg-resp-${idx}`, 'Describa la responsabilidad…', 'cfg-resp-text')}
                <button type="button" class="cfg-anatomy-remove" data-action="remove-resp" aria-label="Quitar" ${list.length <= 1 ? 'disabled' : ''}>×</button>
            </div>
        `).join('');
        host.querySelectorAll('.cfg-anatomy-item-resp').forEach((row, idx) => {
            const sel = row.querySelector('.cfg-resp-type');
            if (sel) sel.value = list[idx].type || 'good_behavior';
            const rich = row.querySelector('.cfg-resp-text');
            if (rich) writeRichMd(rich.id, list[idx].text || '');
        });
    }

    function readResponsabilidadesFromDom() {
        return [...document.querySelectorAll('#cfg-anatomy-responsabilidades .cfg-anatomy-item-resp')].map((row) => ({
            type: row.querySelector('.cfg-resp-type')?.value || 'good_behavior',
            text: readRichMd(row.querySelector('.cfg-resp-text')?.id || ''),
        })).filter((item) => item.text);
    }

    function buildComunicacionFields() {
        const body = $('cfg-anatomy-body-comunicacion');
        if (!body) return;
        body.innerHTML = COMM_FIELDS.map((field) => `
            <div class="cfg-anatomy-field">
                <label class="cfg-anatomy-field-label" for="cfg-anatomy-comm-${field.id}">${escapeHtmlText(field.label)}</label>
                <p class="cfg-anatomy-field-hint">${escapeHtmlText(field.hint)}</p>
                ${richEditorHtml(`cfg-anatomy-comm-${field.id}`, field.hint)}
            </div>
        `).join('');
    }

    function splitMarkedSections(md, markers) {
        const text = String(md || '').replace(/\r\n/g, '\n').trim();
        const out = {};
        markers.forEach((m) => { out[m] = ''; });
        if (!text) return out;
        const re = new RegExp(
            `(?:^|\\n)\\*\\*(${markers.map((m) => m.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')}):\\*\\*\\s*`,
            'gi'
        );
        const matches = [...text.matchAll(re)];
        if (!matches.length) {
            out[markers[0]] = text;
            return out;
        }
        for (let i = 0; i < matches.length; i += 1) {
            const key = matches[i][1];
            const canon = markers.find((m) => m.toLowerCase() === key.toLowerCase()) || key;
            const start = matches[i].index + matches[i][0].length;
            const end = i + 1 < matches.length ? matches[i + 1].index : text.length;
            out[canon] = text.slice(start, end).replace(/^\n+/, '').replace(/\n+$/, '').trim();
        }
        // Prefacio antes del primer marcador → primer campo si vacío
        const firstStart = matches[0].index;
        if (firstStart > 0 && !out[markers[0]]) {
            const preface = text.slice(0, firstStart).trim();
            if (preface) out[markers[0]] = preface;
        }
        return out;
    }

    function joinMarkedSections(pairs) {
        return pairs
            .filter((p) => String(p.value || '').trim())
            .map((p) => `**${p.marker}:**\n${String(p.value).trim()}`)
            .join('\n\n') + '\n';
    }

    function splitRoleFields(roleMd) {
        const marked = splitMarkedSections(roleMd, ['Función', 'Alcance']);
        let funcion = String(marked.Función || '').trim();
        let alcance = String(marked.Alcance || '').trim();

        // Si solo hay marcador de Función (o ninguno), partir también por "Alcance único:".
        const blob = alcance ? '' : (funcion || String(roleMd || '').replace(/\r\n/g, '\n').trim());
        if (blob) {
            const m = blob.match(/(?:^|\n)\s*(?:\*\*)?Alcance(?:\s+único)?(?:\*\*)?\s*:\s*/i);
            if (m && m.index != null) {
                funcion = blob.slice(0, m.index).trim();
                alcance = blob.slice(m.index + m[0].length).trim();
            } else if (!funcion) {
                funcion = blob;
            }
        }
        return { funcion, alcance };
    }

    function joinRoleFields(funcion, alcance) {
        return joinMarkedSections([
            { marker: 'Función', value: funcion },
            { marker: 'Alcance', value: alcance },
        ]);
    }

    function parseStepsFromTasks(tasksMd) {
        const text = String(tasksMd || '').replace(/\r\n/g, '\n');
        const steps = [];
        const other = [];
        text.split('\n').forEach((line) => {
            const m = line.match(/^\s*\d+[.)]\s+(.*)$/);
            if (m) {
                steps.push(m[1].replace(/^\*\*(.+)\*\*$/, '$1').trim());
            } else if (line.trim()) {
                // Omitir encabezado típico del loop
                if (/ciclo de trabajo|agent loop|en CADA turno/i.test(line)) return;
                other.push(line.trim());
            }
        });
        return { steps, regla: other.join('\n').trim() };
    }

    function joinStepsToTasks(steps, regla) {
        const list = (steps && steps.length ? steps : ['']).filter((s) => String(s || '').trim());
        const lines = ['Tu ciclo de trabajo (agent loop) en CADA turno, en orden:'];
        list.forEach((step, idx) => {
            lines.push(`${idx + 1}. ${String(step).trim()}`);
        });
        if (regla && String(regla).trim()) {
            lines.push('');
            lines.push(String(regla).trim());
        }
        return `${lines.join('\n')}\n`;
    }

    function bulletsToList(md) {
        return String(md || '')
            .split('\n')
            .map((line) => line.replace(/^\s*[-*]\s+/, '').replace(/^\s*\d+[.)]\s+/, '').trim())
            .filter(Boolean);
    }

    function listToBullets(items) {
        return (items || []).map((t) => `- ${String(t).trim()}`).join('\n') + ((items || []).length ? '\n' : '');
    }

    function listToNumbered(items) {
        return (items || []).map((t, i) => `${i + 1}. ${String(t).trim()}`).join('\n') + ((items || []).length ? '\n' : '');
    }

    function responsabilidadesFromFields(fields) {
        const items = [];
        RESP_TYPES.forEach((t) => {
            bulletsToList(fields[t.id]).forEach((text) => items.push({ type: t.id, text }));
        });
        return items;
    }

    function fieldsFromResponsabilidades(items) {
        const fields = {
            boundaries: '',
            good_behavior: '',
            bad_behavior: '',
            fallback_behavior: '',
        };
        const buckets = {
            boundaries: [],
            good_behavior: [],
            bad_behavior: [],
            fallback_behavior: [],
        };
        (items || []).forEach((item) => {
            if (!item.text) return;
            const key = buckets[item.type] ? item.type : 'good_behavior';
            buckets[key].push(item.text);
        });
        fields.boundaries = listToBullets(buckets.boundaries);
        fields.good_behavior = listToBullets(buckets.good_behavior);
        fields.bad_behavior = listToBullets(buckets.bad_behavior);
        fields.fallback_behavior = listToNumbered(buckets.fallback_behavior);
        return fields;
    }

    function splitVoiceFields(voiceMd) {
        const markers = COMM_FIELDS.filter((f) => f.section === 'voice_rules').map((f) => f.marker);
        return splitMarkedSections(voiceMd, markers);
    }

    function joinVoiceFields(values) {
        return joinMarkedSections(
            COMM_FIELDS
                .filter((f) => f.section === 'voice_rules')
                .map((f) => ({ marker: f.marker, value: values[f.id] || '' }))
        );
    }

    function readAnatomyFieldsFromDom() {
        const fields = {};
        ANATOMY_SECTION_IDS.forEach((id) => { fields[id] = ''; });

        fields.role = joinRoleFields(
            readRichMd('cfg-anatomy-funcion'),
            readRichMd('cfg-anatomy-alcance')
        );
        fields.tasks = joinStepsToTasks(readPasosFromDom(), readRichMd('cfg-anatomy-regla-loop'));
        fields.tool_routing = readRichMd('cfg-anatomy-tool-routing');

        Object.assign(fields, fieldsFromResponsabilidades(readResponsabilidadesFromDom()));

        const voiceValues = {};
        COMM_FIELDS.filter((f) => f.section === 'voice_rules').forEach((f) => {
            voiceValues[f.id] = readRichMd(`cfg-anatomy-comm-${f.id}`);
        });
        fields.voice_rules = joinVoiceFields(voiceValues);
        fields.closing_rule = readRichMd('cfg-anatomy-comm-cierre');
        fields.few_shots = readRichMd('cfg-anatomy-comm-ejemplos');
        return fields;
    }

    function writeAnatomyFieldsToDom(fields) {
        ensureAnatomyFormBuilt();
        const role = splitRoleFields((fields && fields.role) || '');
        writeRichMd('cfg-anatomy-funcion', role.funcion);
        writeRichMd('cfg-anatomy-alcance', role.alcance);

        const parsedSteps = parseStepsFromTasks((fields && fields.tasks) || '');
        renderPasosList(parsedSteps.steps.length ? parsedSteps.steps : ['']);
        writeRichMd('cfg-anatomy-regla-loop', parsedSteps.regla || '');
        writeRichMd('cfg-anatomy-tool-routing', (fields && fields.tool_routing) || '');

        const respItems = responsabilidadesFromFields(fields || {});
        renderResponsabilidadesList(respItems.length ? respItems : [{ type: 'good_behavior', text: '' }]);

        const voice = splitVoiceFields((fields && fields.voice_rules) || '');
        COMM_FIELDS.forEach((f) => {
            if (f.section === 'voice_rules') writeRichMd(`cfg-anatomy-comm-${f.id}`, voice[f.marker] || '');
            else if (f.id === 'cierre') writeRichMd('cfg-anatomy-comm-cierre', (fields && fields.closing_rule) || '');
            else if (f.id === 'ejemplos') writeRichMd('cfg-anatomy-comm-ejemplos', (fields && fields.few_shots) || '');
        });
        if ((fields && fields.voice_rules) && !COMM_FIELDS.filter((f) => f.section === 'voice_rules').some((f) => voice[f.marker])) {
            const modoVal = readRichMd('cfg-anatomy-comm-modo');
            if (!modoVal) writeRichMd('cfg-anatomy-comm-modo', fields.voice_rules);
        }
        autosizeEditor();
    }

    function setAnatomyDisabled(disabled) {
        const form = $('cfg-form-anatomy');
        if (!form) return;
        form.querySelectorAll('textarea, select, button.cfg-anatomy-add, button.cfg-anatomy-remove').forEach((el) => {
            el.disabled = Boolean(disabled);
        });
        form.querySelectorAll('.cfg-rich').forEach((el) => {
            el.setAttribute('contenteditable', disabled ? 'false' : 'true');
            el.classList.toggle('is-disabled', Boolean(disabled));
        });
        if (!disabled) {
            const pasos = document.querySelectorAll('#cfg-anatomy-pasos .cfg-anatomy-item');
            pasos.forEach((row) => {
                const btn = row.querySelector('[data-action="remove-paso"]');
                if (btn) btn.disabled = pasos.length <= 1;
            });
            const resps = document.querySelectorAll('#cfg-anatomy-responsabilidades .cfg-anatomy-item-resp');
            resps.forEach((row) => {
                const btn = row.querySelector('[data-action="remove-resp"]');
                if (btn) btn.disabled = resps.length <= 1;
            });
        }
    }

    function anatomyActive() {
        const el = $('cfg-form-anatomy');
        return Boolean(el && !el.classList.contains('hidden'));
    }

    function structuredActive() {
        const structured = $('cfg-form-structured');
        return Boolean(structured && !structured.classList.contains('hidden'));
    }

    function skillFormActive() {
        const el = $('cfg-form-skill');
        return Boolean(el && !el.classList.contains('hidden'));
    }

    /* ── Skill anatomy (SKILL.md) ─────────────────────────────────────── */

    const SKILL_SECTION_DEFS = [
        { id: 'scope', title: 'Scope', label: 'Alcance', hint: 'Categoría, Skill ID y tier. Define el perímetro del skill.' },
        { id: 'index_blurb', title: 'Index Blurb', label: 'Resumen corto', hint: 'Una frase para el índice / catálogo del skill.' },
        { id: 'used_by', title: 'Used By Agents', label: 'Agentes que lo usan', hint: 'Lista de agentes que invocan este skill.' },
        { id: 'purpose', title: 'Purpose', label: 'Propósito', hint: 'Qué debe lograr el skill para que el flujo funcione bien.' },
        {
            id: 'rol',
            title: 'Rol en coordinador',
            label: 'Rol en el flujo',
            hint: 'Cuándo se ejecuta dentro del agente (el encabezado ## Rol en … se conserva).',
            matchPrefix: 'rol en ',
        },
        { id: 'inputs', title: 'Inputs', label: 'Entradas necesarias', hint: 'Datos, documentos o contexto mínimos para ejecutar.' },
        {
            id: 'outputs',
            title: 'Outputs',
            label: 'Salida esperada',
            hint: 'Formato / campos que debe devolver el skill.',
            matchPrefix: 'outputs',
        },
        { id: 'steps', title: 'Steps', label: 'Pasos', hint: 'Instrucciones en orden. El agente las sigue una tras otra.' },
        { id: 'tools', title: 'Tools', label: 'Herramientas', hint: 'Tools que puede usar este skill.' },
        {
            id: 'guardrails',
            title: 'Guardrails',
            label: 'Reglas y límites',
            hint: 'Políticas del despacho (desk I/O/T) y restricciones que no puede romper.',
            aliases: ['Guardrails (g1-g10)', 'Guardrails (g1–g10)', 'Guardrails'],
        },
        { id: 'handoff', title: 'Handoff', label: 'Derivación (handoff)', hint: 'A dónde pasar según el resultado o el fallo.' },
        { id: 'no_duplicar', title: 'No duplicar', label: 'No duplicar', hint: 'Qué no debe hacer porque otro skill ya lo cubre.' },
        { id: 'best_practices', title: 'Best Practices', label: 'Buenas prácticas', hint: 'Criterios de calidad al ejecutar.' },
        { id: 'riesgo', title: 'Riesgo si se omite', label: 'Riesgo si se omite', hint: 'Qué falla en el caso si este skill no corre.' },
    ];

    function normalizeSkillHeading(h) {
        return String(h || '')
            .trim()
            .toLowerCase()
            .replace(/[–—]/g, '-')
            .replace(/\s+/g, ' ');
    }

    function matchSkillSection(heading) {
        const raw = String(heading || '').trim();
        const n = normalizeSkillHeading(raw);
        for (const def of SKILL_SECTION_DEFS) {
            if (def.matchPrefix) {
                if (def.id === 'outputs') {
                    if (n === 'outputs' || n.startsWith('outputs (')) {
                        return { def, matchedTitle: raw };
                    }
                    continue;
                }
                if (n.startsWith(def.matchPrefix)) {
                    return { def, matchedTitle: raw };
                }
                continue;
            }
            const titles = [def.title, ...(def.aliases || [])];
            if (titles.some((t) => normalizeSkillHeading(t) === n)) {
                return { def, matchedTitle: def.title };
            }
        }
        return null;
    }

    function parseSimpleFrontmatter(fmBody) {
        const fields = {};
        const order = [];
        String(fmBody || '')
            .replace(/\r\n/g, '\n')
            .split('\n')
            .forEach((line) => {
                const m = line.match(/^([A-Za-z0-9_-]+)\s*:\s*(.*)$/);
                if (!m) return;
                const key = m[1];
                if (!Object.prototype.hasOwnProperty.call(fields, key)) order.push(key);
                fields[key] = m[2];
            });
        return { fields, order };
    }

    function parseNumberedSteps(md) {
        const lines = String(md || '').replace(/\r\n/g, '\n').split('\n');
        const steps = [];
        let current = null;
        const orphan = [];
        lines.forEach((line) => {
            const m = line.match(/^\s*(\d+)[.)]\s+(.*)$/);
            if (m) {
                if (current != null) steps.push(current.replace(/\n+$/, ''));
                current = m[2];
                return;
            }
            if (current != null) {
                current += `\n${line}`;
                return;
            }
            if (line.trim()) orphan.push(line);
        });
        if (current != null) steps.push(current.replace(/\n+$/, ''));
        if (!steps.length && orphan.length) {
            return { steps: [orphan.join('\n')], orphan: '' };
        }
        return { steps, orphan: orphan.join('\n') };
    }

    function serializeNumberedSteps(steps) {
        const items = (steps || []).map((s) => String(s || '').trim()).filter(Boolean);
        if (!items.length) return '';
        return items.map((s, i) => `${i + 1}. ${s}`).join('\n') + '\n';
    }

    /**
     * Parsea SKILL.md del repo (frontmatter + ## Purpose/Inputs/Steps…).
     * mode=form si hay anatomía reconocible; si no, raw (textarea).
     */
    function parseSkillMarkdown(content) {
        let body = String(content || '').replace(/^\uFEFF/, '').replace(/\r\n/g, '\n');
        let prefixComment = '';
        const commentMatch = body.match(/^<!--[\s\S]*?-->\s*/);
        if (commentMatch) {
            prefixComment = commentMatch[0].replace(/\s+$/, '') + '\n';
            body = body.slice(commentMatch[0].length);
        }

        let frontmatter = {};
        let frontmatterOrder = [];
        let hadFrontmatter = false;
        if (body.startsWith('---')) {
            const end = body.indexOf('\n---', 3);
            if (end !== -1) {
                hadFrontmatter = true;
                const fmRaw = body.slice(3, end).replace(/^\n/, '');
                const parsedFm = parseSimpleFrontmatter(fmRaw);
                frontmatter = parsedFm.fields;
                frontmatterOrder = parsedFm.order;
                body = body.slice(end + 4).replace(/^\n+/, '');
            }
        }

        const headingRe = /^##\s+(.+?)\s*$/gm;
        const matches = [...body.matchAll(headingRe)];
        const fields = {};
        const sectionTitles = {};
        SKILL_SECTION_DEFS.forEach((d) => {
            fields[d.id] = '';
            sectionTitles[d.id] = d.title;
        });
        const unknownSections = [];
        let preamble = '';

        if (!matches.length) {
            const titleMatch = body.match(/^#\s+(.+)$/m);
            return {
                mode: hadFrontmatter ? 'form' : 'raw',
                prefixComment,
                frontmatter,
                frontmatterOrder,
                title: titleMatch ? titleMatch[1].trim() : '',
                fields,
                sectionTitles,
                steps: [''],
                unknownSections,
                extras: body.replace(/^#\s+.+\n?/, '').trim(),
            };
        }

        preamble = body.slice(0, matches[0].index).trim();
        const titleMatch = preamble.match(/^#\s+(.+)$/m);
        const title = titleMatch ? titleMatch[1].trim() : '';
        const preambleExtra = preamble.replace(/^#\s+.+$/m, '').trim();

        for (let i = 0; i < matches.length; i += 1) {
            const heading = matches[i][1].trim();
            const start = matches[i].index + matches[i][0].length;
            const end = i + 1 < matches.length ? matches[i + 1].index : body.length;
            const sectionBody = body.slice(start, end).replace(/^\n+/, '').replace(/\n+$/, '');
            const matched = matchSkillSection(heading);
            if (matched) {
                const { def, matchedTitle } = matched;
                if (fields[def.id]) {
                    // Segunda sección del mismo tipo → extras (p. ej. varios "Rol en …").
                    unknownSections.push({ title: heading, body: sectionBody });
                } else {
                    fields[def.id] = sectionBody;
                    sectionTitles[def.id] = matchedTitle || def.title;
                }
            } else {
                unknownSections.push({ title: heading, body: sectionBody });
            }
        }

        const coreHit =
            Boolean(fields.purpose) ||
            Boolean(fields.inputs) ||
            Boolean(fields.outputs) ||
            Boolean(fields.steps) ||
            Boolean(fields.scope);
        const mode = hadFrontmatter || coreHit ? 'form' : 'raw';

        const parsedSteps = parseNumberedSteps(fields.steps);
        const extrasParts = [];
        if (preambleExtra) extrasParts.push(preambleExtra);
        if (parsedSteps.orphan) extrasParts.push(parsedSteps.orphan);
        unknownSections.forEach((u) => {
            extrasParts.push(`## ${u.title}\n${u.body}`.trim());
        });

        return {
            mode,
            prefixComment,
            frontmatter,
            frontmatterOrder,
            title,
            fields,
            sectionTitles,
            steps: parsedSteps.steps.length ? parsedSteps.steps : [''],
            unknownSections,
            extras: extrasParts.join('\n\n').trim(),
        };
    }

    function serializeSkillMarkdown(parsed) {
        const fm = { ...(parsed.frontmatter || {}) };
        const order = [...(parsed.frontmatterOrder || [])];
        ['name', 'description', 'disable-model-invocation'].forEach((k) => {
            if (!order.includes(k) && fm[k] != null && String(fm[k]).trim() !== '') order.push(k);
        });
        Object.keys(fm).forEach((k) => {
            if (!order.includes(k)) order.push(k);
        });

        const fmLines = order
            .filter((k) => fm[k] != null && String(fm[k]).trim() !== '')
            .map((k) => `${k}: ${String(fm[k]).trim()}`);

        const parts = [];
        if (parsed.prefixComment) parts.push(String(parsed.prefixComment).trimEnd());
        if (fmLines.length) {
            parts.push('---');
            parts.push(...fmLines);
            parts.push('---');
            parts.push('');
        }

        const title = String(parsed.title || fm.name || '').trim() || 'skill';
        parts.push(`# ${title}`);
        parts.push('');

        const fields = { ...(parsed.fields || {}) };
        fields.steps = serializeNumberedSteps(parsed.steps || []).replace(/\n$/, '');
        const titles = { ...(parsed.sectionTitles || {}) };

        SKILL_SECTION_DEFS.forEach((def) => {
            const body = String(fields[def.id] || '').trim();
            if (!body) return;
            const heading = titles[def.id] || def.title;
            parts.push(`## ${heading}`);
            parts.push(body);
            parts.push('');
        });

        const extras = String(parsed.extras || '').trim();
        if (extras) {
            parts.push(extras);
            parts.push('');
        }

        return `${parts.join('\n').replace(/\n+$/, '')}\n`;
    }

    function ensureSkillFormBuilt() {
        const host = $('cfg-skill-fields');
        if (!host) return;
        if (host.dataset.built === 'skill-v2') return;
        host.dataset.built = 'skill-v2';

        const fieldBlock = (id, label, hint, placeholder) => `
            <div class="cfg-anatomy-field">
                <label class="cfg-anatomy-field-label" for="${id}">${escapeHtmlText(label)}</label>
                <p class="cfg-anatomy-field-hint">${escapeHtmlText(hint)}</p>
                ${richEditorHtml(id, placeholder)}
            </div>
        `;

        const byId = Object.fromEntries(SKILL_SECTION_DEFS.map((d) => [d.id, d]));

        host.innerHTML = `
            <section class="cfg-anatomy-card" data-tone="control">
                <div class="cfg-anatomy-card-head">
                    <span class="cfg-anatomy-num" aria-hidden="true">S</span>
                    <div class="cfg-anatomy-card-copy">
                        <h4 class="cfg-anatomy-title">Anatomía del skill</h4>
                        <p class="cfg-anatomy-hint">Text fields del formato SKILL.md: lo que el skill necesita para funcionar bien. Se serializan a las secciones ## del markdown.</p>
                    </div>
                </div>
                <div class="cfg-anatomy-body">
                    <div class="cfg-skill-grid-2">
                        <div class="cfg-anatomy-field">
                            <label class="cfg-anatomy-field-label" for="cfg-skill-name">Nombre</label>
                            <p class="cfg-anatomy-field-hint">Frontmatter name (identificador del skill).</p>
                            <input id="cfg-skill-name" type="text" class="cfg-field-control cfg-anatomy-input" placeholder="ej. detectar-urgencia-penal" disabled>
                        </div>
                        <div class="cfg-anatomy-field">
                            <label class="cfg-anatomy-field-label" for="cfg-skill-title">Título (H1)</label>
                            <p class="cfg-anatomy-field-hint">Encabezado principal del SKILL.md.</p>
                            <input id="cfg-skill-title" type="text" class="cfg-field-control cfg-anatomy-input" placeholder="ej. detectar_urgencia_penal" disabled>
                        </div>
                    </div>
                    ${fieldBlock('cfg-skill-when', 'Cuándo usarlo', 'Frontmatter description: disparador del skill en el flujo.', 'Use when the workflow requires…')}
                    ${fieldBlock('cfg-skill-purpose', byId.purpose.label, byId.purpose.hint, 'Qué debe lograr…')}
                    ${fieldBlock('cfg-skill-scope', byId.scope.label, byId.scope.hint, 'Category, Skill ID, Tier…')}
                    ${fieldBlock('cfg-skill-blurb', byId.index_blurb.label, byId.index_blurb.hint, 'Una frase para el índice…')}
                    ${fieldBlock('cfg-skill-used-by', byId.used_by.label, byId.used_by.hint, '- agente_id')}
                    ${fieldBlock('cfg-skill-rol', byId.rol.label, byId.rol.hint, 'Cuándo se ejecuta en la secuencia…')}
                    ${fieldBlock('cfg-skill-inputs', byId.inputs.label, byId.inputs.hint, 'Liste las entradas…')}
                    <div class="cfg-anatomy-field">
                        <div class="cfg-anatomy-list-head">
                            <div>
                                <p class="cfg-anatomy-field-label">${escapeHtmlText(byId.steps.label)}</p>
                                <p class="cfg-anatomy-field-hint">${escapeHtmlText(byId.steps.hint)}</p>
                            </div>
                            <button type="button" class="cfg-anatomy-add" data-action="add-skill-paso">+ Agregar paso</button>
                        </div>
                        <div id="cfg-skill-pasos" class="cfg-anatomy-list"></div>
                    </div>
                    ${fieldBlock('cfg-skill-outputs', byId.outputs.label, byId.outputs.hint, 'Campos / formato de salida…')}
                    ${fieldBlock('cfg-skill-tools', byId.tools.label, byId.tools.hint, '- tool_a')}
                    ${fieldBlock('cfg-skill-guardrails', byId.guardrails.label, byId.guardrails.hint, 'g1: …')}
                    ${fieldBlock('cfg-skill-handoff', byId.handoff.label, byId.handoff.hint, 'Si X → …')}
                    ${fieldBlock('cfg-skill-no-duplicar', byId.no_duplicar.label, byId.no_duplicar.hint, 'No hacer X (otro skill)…')}
                    ${fieldBlock('cfg-skill-practices', byId.best_practices.label, byId.best_practices.hint, 'Preferir… Evitar…')}
                    ${fieldBlock('cfg-skill-riesgo', byId.riesgo.label, byId.riesgo.hint, 'Qué falla si se omite…')}
                    <div id="cfg-skill-raw-wrap" class="cfg-anatomy-field hidden">
                        <label class="cfg-anatomy-field-label" for="cfg-skill-extras">Contenido adicional (preservar)</label>
                        <p class="cfg-anatomy-field-hint">Secciones no reconocidas. Se conservan al guardar para no perder contenido legacy.</p>
                        <textarea id="cfg-skill-extras" rows="4" class="cfg-field-control cfg-anatomy-input" disabled></textarea>
                    </div>
                </div>
            </section>
        `;
        renderSkillPasosList(['']);
    }

    function renderSkillPasosList(steps) {
        const host = $('cfg-skill-pasos');
        if (!host) return;
        const items = Array.isArray(steps) && steps.length ? steps : [''];
        host.innerHTML = items
            .map(
                (text, idx) => `
            <div class="cfg-anatomy-item" data-skill-paso-idx="${idx}">
                <span class="cfg-anatomy-item-num" aria-hidden="true">${idx + 1}</span>
                ${richEditorHtml(`cfg-skill-paso-${idx}`, `Describa el paso ${idx + 1}…`, 'cfg-skill-paso-text')}
                <button type="button" class="cfg-anatomy-remove" data-action="remove-skill-paso" aria-label="Quitar paso" ${items.length <= 1 ? 'disabled' : ''}>×</button>
            </div>
        `,
            )
            .join('');
        host.querySelectorAll('.cfg-skill-paso-text').forEach((el, idx) => writeRichMd(el.id, items[idx] || ''));
    }

    function readSkillPasosFromDom() {
        return [...document.querySelectorAll('#cfg-skill-pasos .cfg-skill-paso-text')]
            .map((el) => readRichMd(el.id))
            .filter(Boolean);
    }

    function readSkillFieldsFromDom() {
        const form = $('cfg-form-skill');
        const fmOrder = (form && form.dataset.fmOrder ? form.dataset.fmOrder.split('\u0001') : []) || [];
        const prefixComment = (form && form.dataset.prefixComment) || '';
        const disableInv = (form && form.dataset.disableModelInvocation) || 'true';
        let extraFm = {};
        let sectionTitles = {};
        try {
            extraFm = form && form.dataset.extraFm ? JSON.parse(form.dataset.extraFm) : {};
        } catch (_) {
            extraFm = {};
        }
        try {
            sectionTitles = form && form.dataset.sectionTitles ? JSON.parse(form.dataset.sectionTitles) : {};
        } catch (_) {
            sectionTitles = {};
        }

        const name = ($('cfg-skill-name')?.value || '').trim();
        const title = ($('cfg-skill-title')?.value || '').trim();
        const description = readRichMd('cfg-skill-when');
        const frontmatter = {
            ...extraFm,
            name: name || extraFm.name || '',
            description: description || extraFm.description || '',
            'disable-model-invocation': disableInv,
        };

        const fields = {};
        SKILL_SECTION_DEFS.forEach((d) => {
            fields[d.id] = '';
            if (!sectionTitles[d.id]) sectionTitles[d.id] = d.title;
        });
        fields.purpose = readRichMd('cfg-skill-purpose');
        fields.scope = readRichMd('cfg-skill-scope');
        fields.index_blurb = readRichMd('cfg-skill-blurb');
        fields.rol = readRichMd('cfg-skill-rol');
        fields.inputs = readRichMd('cfg-skill-inputs');
        fields.outputs = readRichMd('cfg-skill-outputs');
        fields.guardrails = readRichMd('cfg-skill-guardrails');
        fields.no_duplicar = readRichMd('cfg-skill-no-duplicar');
        fields.best_practices = readRichMd('cfg-skill-practices');
        fields.handoff = readRichMd('cfg-skill-handoff');
        fields.riesgo = readRichMd('cfg-skill-riesgo');
        fields.tools = readRichMd('cfg-skill-tools');
        fields.used_by = readRichMd('cfg-skill-used-by');

        return {
            mode: 'form',
            prefixComment,
            frontmatter,
            frontmatterOrder: fmOrder.length ? fmOrder : Object.keys(frontmatter),
            title,
            fields,
            sectionTitles,
            steps: readSkillPasosFromDom(),
            extras: ($('cfg-skill-extras')?.value || '').trim(),
        };
    }

    function writeSkillFieldsToDom(parsed) {
        ensureSkillFormBuilt();
        const form = $('cfg-form-skill');
        if (form) {
            form.dataset.prefixComment = parsed.prefixComment || '';
            form.dataset.fmOrder = (parsed.frontmatterOrder || []).join('\u0001');
            form.dataset.disableModelInvocation =
                (parsed.frontmatter && parsed.frontmatter['disable-model-invocation']) || 'true';
            const reserved = new Set(['name', 'description', 'disable-model-invocation']);
            const extraFm = {};
            Object.entries(parsed.frontmatter || {}).forEach(([k, v]) => {
                if (!reserved.has(k)) extraFm[k] = v;
            });
            form.dataset.extraFm = JSON.stringify(extraFm);
            form.dataset.sectionTitles = JSON.stringify(parsed.sectionTitles || {});
        }
        if ($('cfg-skill-name')) $('cfg-skill-name').value = (parsed.frontmatter && parsed.frontmatter.name) || '';
        if ($('cfg-skill-title')) $('cfg-skill-title').value = parsed.title || '';
        writeRichMd('cfg-skill-purpose', (parsed.fields && parsed.fields.purpose) || '');
        writeRichMd('cfg-skill-when', (parsed.frontmatter && parsed.frontmatter.description) || '');
        writeRichMd('cfg-skill-scope', (parsed.fields && parsed.fields.scope) || '');
        writeRichMd('cfg-skill-blurb', (parsed.fields && parsed.fields.index_blurb) || '');
        writeRichMd('cfg-skill-rol', (parsed.fields && parsed.fields.rol) || '');
        writeRichMd('cfg-skill-inputs', (parsed.fields && parsed.fields.inputs) || '');
        writeRichMd('cfg-skill-outputs', (parsed.fields && parsed.fields.outputs) || '');
        writeRichMd('cfg-skill-guardrails', (parsed.fields && parsed.fields.guardrails) || '');
        writeRichMd('cfg-skill-no-duplicar', (parsed.fields && parsed.fields.no_duplicar) || '');
        writeRichMd('cfg-skill-practices', (parsed.fields && parsed.fields.best_practices) || '');
        writeRichMd('cfg-skill-handoff', (parsed.fields && parsed.fields.handoff) || '');
        writeRichMd('cfg-skill-riesgo', (parsed.fields && parsed.fields.riesgo) || '');
        writeRichMd('cfg-skill-tools', (parsed.fields && parsed.fields.tools) || '');
        writeRichMd('cfg-skill-used-by', (parsed.fields && parsed.fields.used_by) || '');
        renderSkillPasosList(parsed.steps && parsed.steps.length ? parsed.steps : ['']);
        const extras = parsed.extras || '';
        if ($('cfg-skill-extras')) $('cfg-skill-extras').value = extras;
        const rawWrap = $('cfg-skill-raw-wrap');
        if (rawWrap) rawWrap.classList.toggle('hidden', !extras.trim());
        autosizeEditor();
    }

    function setSkillFormDisabled(disabled) {
        const form = $('cfg-form-skill');
        if (!form) return;
        form.querySelectorAll('textarea, input, button.cfg-anatomy-add, button.cfg-anatomy-remove').forEach((el) => {
            el.disabled = Boolean(disabled);
        });
        form.querySelectorAll('.cfg-rich').forEach((el) => {
            el.setAttribute('contenteditable', disabled ? 'false' : 'true');
            el.classList.toggle('is-disabled', Boolean(disabled));
        });
        if (!disabled) {
            const pasos = document.querySelectorAll('#cfg-skill-pasos .cfg-anatomy-item');
            pasos.forEach((row) => {
                const btn = row.querySelector('[data-action="remove-skill-paso"]');
                if (btn) btn.disabled = pasos.length <= 1;
            });
        }
    }

    /* ── Guardrail anatomy (config/guardrails/agents/.../{input|output|tools}.md) ── */

    const GUARD_CLASS_ORDER = ['input', 'output', 'tools'];
    const GUARD_CLASS_LABEL = {
        input: 'Input',
        output: 'Output',
        tools: 'Tools',
    };
    const GUARD_SECTION_DEFS = {
        input: [
            { id: 'scope_policy', label: 'Política de alcance', hint: 'Qué consultas se admiten (p. ej. penal-víctimas Ley 906) y qué queda fuera.' },
            { id: 'max_length_policy', label: 'Longitud máxima', hint: 'Límite de caracteres y qué hacer con pegados masivos.' },
            { id: 'required_anchors', label: 'Anclas requeridas', hint: 'Señales que anclan el alcance penal (términos / contexto de expediente).' },
            { id: 'out_of_scope_examples', label: 'Ejemplos fuera de alcance', hint: 'Casos hard fuera de alcance y reacción (tripwire, no tools).' },
            { id: 'injection_policy', label: 'Política anti-inyección', hint: 'Ignorar órdenes para revelar prompt, desactivar guardrails o actuar fuera de alcance.' },
            { id: 'missing_data_policy', label: 'Datos faltantes', hint: 'Qué preguntar antes de concluir o derivar cuando faltan hechos/etapa/radicado.' },
            { id: 'tripwire_message', label: 'Mensaje de tripwire', hint: 'Texto que se muestra o registra cuando la entrada dispara el tripwire.' },
            { id: 'output_info_fields', label: 'Campos de auditoría', hint: 'Campos a registrar en auditoría (reason, anchors_found, etc.).' },
        ],
        output: [
            { id: 'no_invention_policy', label: 'No invención', hint: 'No inventar normas, radicados, jurisprudencia ni hechos sin fuente.' },
            { id: 'fact_vs_inference_policy', label: 'Hecho vs inferencia', hint: 'Separar hecho confirmado / narrado / inferido; no presentar inferencias como hechos.' },
            { id: 'pending_marker_policy', label: 'Marcador de pendientes', hint: 'Cuándo y cómo usar [PENDIENTE DE VERIFICAR].' },
            { id: 'pii_policy', label: 'Datos personales (PII)', hint: 'Qué datos sensibles no exponer en la respuesta.' },
            { id: 'non_revictimization_policy', label: 'No revictimización', hint: 'Tono respetuoso; evitar culpar o detalle gráfico innecesario.' },
            { id: 'disclaimer_policy', label: 'Aviso de borrador', hint: 'Disclaimer obligatorio al cierre de la respuesta.' },
            { id: 'empty_output_policy', label: 'Salida vacía', hint: 'Qué hacer si la salida está vacía o solo whitespace.' },
            { id: 'tripwire_message', label: 'Mensaje de tripwire', hint: 'Texto cuando la salida viola políticas de calidad/seguridad.' },
            { id: 'output_info_fields', label: 'Campos de auditoría', hint: 'Campos a registrar (reason, chars, has_disclaimer, etc.).' },
        ],
        tools: [
            { id: 'allowed_tools_policy', label: 'Tools permitidas', hint: 'Qué tools se pueden invocar y restricción de relevancia al turno.' },
            { id: 'routing_constraints', label: 'Restricciones de enrutamiento', hint: 'Reglas de a qué especialista derivar (redacción, calidad, seguimiento…).' },
            { id: 'needs_approval_tools', label: 'Tools con aprobación', hint: 'Tools que requieren HITL / plan aprobado antes de invocarse.' },
            { id: 'approval_prompt', label: 'Prompt de aprobación', hint: 'Texto de solicitud de aprobación al abogado.' },
            { id: 'args_sensitivity_policy', label: 'Sensibilidad de argumentos', hint: 'Qué PII no pasar en argumentos de tools.' },
            { id: 'ask_before_invoke_policy', label: 'Preguntar antes de invocar', hint: 'Cuándo pedir aclaración antes de invocar especialistas costosos.' },
            { id: 'tripwire_message', label: 'Mensaje de tripwire', hint: 'Texto cuando no se invoca la tool por política o faltantes.' },
            { id: 'output_info_fields', label: 'Campos de auditoría', hint: 'Campos a registrar (tool_name, reason, approved…).' },
        ],
    };

    function guardSectionDefsFor(clase) {
        return GUARD_SECTION_DEFS[clase] || [];
    }

    function guardFieldDomId(sectionId) {
        return `cfg-guard-field-${String(sectionId || '').replace(/[^a-z0-9_]/gi, '_')}`;
    }

    function parseAgentGuardrailMarkdown(content, clase) {
        const defs = guardSectionDefsFor(clase);
        const known = new Set(defs.map((d) => d.id));
        let body = String(content || '').replace(/^\uFEFF/, '').replace(/\r\n/g, '\n');
        let prefixComment = '';
        const commentMatch = body.match(/^<!--[\s\S]*?-->\s*/);
        if (commentMatch) {
            prefixComment = commentMatch[0].replace(/\s+$/, '') + '\n';
            body = body.slice(commentMatch[0].length);
        }

        const headingRe = /^##\s+([a-z][a-z0-9_]*)\s*$/gim;
        const matches = [...body.matchAll(headingRe)];
        const fields = {};
        defs.forEach((d) => {
            fields[d.id] = '';
        });
        const unknownSections = [];
        let title = '';
        let preambleExtra = '';

        if (!matches.length) {
            const titleMatch = body.match(/^#\s+(.+)$/m);
            title = titleMatch ? titleMatch[1].trim() : '';
            const extras = body.replace(/^#\s+.+\n?/, '').trim();
            return {
                mode: 'raw',
                clase,
                prefixComment,
                title,
                fields,
                unknownSections,
                extras,
            };
        }

        const preamble = body.slice(0, matches[0].index).trim();
        const titleMatch = preamble.match(/^#\s+(.+)$/m);
        title = titleMatch ? titleMatch[1].trim() : '';
        preambleExtra = preamble.replace(/^#\s+.+$/m, '').trim();

        for (let i = 0; i < matches.length; i += 1) {
            const id = matches[i][1].toLowerCase();
            const start = matches[i].index + matches[i][0].length;
            const end = i + 1 < matches.length ? matches[i + 1].index : body.length;
            const sectionBody = body.slice(start, end).replace(/^\n+/, '').replace(/\n+$/, '');
            if (known.has(id) && !fields[id]) {
                fields[id] = sectionBody;
            } else {
                unknownSections.push({ title: id, body: sectionBody });
            }
        }

        const coreHit = defs.some((d) => Boolean(String(fields[d.id] || '').trim()));
        const extrasParts = [];
        if (preambleExtra) extrasParts.push(preambleExtra);
        unknownSections.forEach((u) => {
            extrasParts.push(`## ${u.title}\n${u.body}`.trim());
        });

        return {
            mode: coreHit ? 'form' : 'raw',
            clase,
            prefixComment,
            title,
            fields,
            unknownSections,
            extras: extrasParts.join('\n\n').trim(),
        };
    }

    function serializeAgentGuardrailMarkdown(parsed) {
        const clase = parsed.clase || 'input';
        const defs = guardSectionDefsFor(clase);
        const parts = [];
        if (parsed.prefixComment) parts.push(String(parsed.prefixComment).trimEnd());
        const title =
            String(parsed.title || '').trim() ||
            `Guardrails de ${clase === 'input' ? 'entrada' : clase === 'output' ? 'salida' : 'tools'}`;
        parts.push(`# ${title}`);
        parts.push('');
        const fields = parsed.fields || {};
        defs.forEach((def) => {
            const body = String(fields[def.id] || '').trim();
            if (!body) return;
            parts.push(`## ${def.id}`);
            parts.push(body);
            parts.push('');
        });
        const extras = String(parsed.extras || '').trim();
        if (extras) {
            parts.push(extras);
            parts.push('');
        }
        return `${parts.join('\n').replace(/\n+$/, '')}\n`;
    }

    function ensureGuardFormBuilt(clase) {
        const host = $('cfg-guard-fields');
        if (!host) return;
        const cls = clase || 'input';
        if (host.dataset.built === `guard-${cls}`) return;
        host.dataset.built = `guard-${cls}`;
        const defs = guardSectionDefsFor(cls);
        const fieldBlock = (id, label, hint) => `
            <div class="cfg-anatomy-field">
                <label class="cfg-anatomy-field-label" for="${id}">${escapeHtmlText(label)}</label>
                <p class="cfg-anatomy-field-hint">${escapeHtmlText(hint)}</p>
                ${richEditorHtml(id, 'Escriba la política…')}
            </div>
        `;
        const claseLabel = GUARD_CLASS_LABEL[cls] || cls;
        host.innerHTML = `
            <section class="cfg-anatomy-card" data-tone="control">
                <div class="cfg-anatomy-card-head">
                    <span class="cfg-anatomy-num" aria-hidden="true">G</span>
                    <div class="cfg-anatomy-card-copy">
                        <h4 class="cfg-anatomy-title">Anatomía del guardrail · ${escapeHtmlText(claseLabel)}</h4>
                        <p class="cfg-anatomy-hint">Campos del archivo ${escapeHtmlText(cls)}.md (secciones ##). Se conservan comentarios y secciones desconocidas al guardar.</p>
                    </div>
                </div>
                <div class="cfg-anatomy-body">
                    <div class="cfg-anatomy-field">
                        <label class="cfg-anatomy-field-label" for="cfg-guard-title">Título (H1)</label>
                        <p class="cfg-anatomy-field-hint">Encabezado principal del markdown del guardrail.</p>
                        <input id="cfg-guard-title" type="text" class="cfg-field-control cfg-anatomy-input" placeholder="Guardrails de …" disabled>
                    </div>
                    ${defs.map((d) => fieldBlock(guardFieldDomId(d.id), d.label, d.hint)).join('')}
                    <div id="cfg-guard-raw-wrap" class="cfg-anatomy-field hidden">
                        <label class="cfg-anatomy-field-label" for="cfg-guard-extras">Contenido adicional (preservar)</label>
                        <p class="cfg-anatomy-field-hint">Secciones no reconocidas o preámbulo. Se conservan al guardar.</p>
                        <textarea id="cfg-guard-extras" rows="4" class="cfg-field-control cfg-anatomy-input" disabled></textarea>
                    </div>
                </div>
            </section>
        `;
    }

    function readGuardFieldsFromDom() {
        const form = $('cfg-form-guard');
        const clase = (form && form.dataset.clase) || currentGuardClass || 'input';
        const prefixComment = (form && form.dataset.prefixComment) || '';
        const defs = guardSectionDefsFor(clase);
        const fields = {};
        defs.forEach((d) => {
            fields[d.id] = readRichMd(guardFieldDomId(d.id));
        });
        return {
            mode: 'form',
            clase,
            prefixComment,
            title: ($('cfg-guard-title')?.value || '').trim(),
            fields,
            extras: ($('cfg-guard-extras')?.value || '').trim(),
        };
    }

    function writeGuardFieldsToDom(parsed) {
        const clase = parsed.clase || currentGuardClass || 'input';
        ensureGuardFormBuilt(clase);
        const form = $('cfg-form-guard');
        if (form) {
            form.dataset.clase = clase;
            form.dataset.prefixComment = parsed.prefixComment || '';
        }
        if ($('cfg-guard-title')) $('cfg-guard-title').value = parsed.title || '';
        guardSectionDefsFor(clase).forEach((d) => {
            writeRichMd(guardFieldDomId(d.id), (parsed.fields && parsed.fields[d.id]) || '');
        });
        const extras = parsed.extras || '';
        if ($('cfg-guard-extras')) $('cfg-guard-extras').value = extras;
        const rawWrap = $('cfg-guard-raw-wrap');
        if (rawWrap) rawWrap.classList.toggle('hidden', !extras.trim());
        autosizeEditor();
    }

    function setGuardFormDisabled(disabled) {
        const form = $('cfg-form-guard');
        if (!form) return;
        form.querySelectorAll('textarea, input').forEach((el) => {
            el.disabled = Boolean(disabled);
        });
        form.querySelectorAll('.cfg-rich').forEach((el) => {
            el.setAttribute('contenteditable', disabled ? 'false' : 'true');
            el.classList.toggle('is-disabled', Boolean(disabled));
        });
    }

    function guardFormActive() {
        const el = $('cfg-form-guard');
        return Boolean(el && !el.classList.contains('hidden'));
    }

    /** Compara contenido ignorando espacios finales para evitar dirty falso. */
    function contentEquals(a, b) {
        const norm = (s) => String(s == null ? '' : s).replace(/[ \t]+$/gm, '').replace(/\s+$/, '');
        return norm(a) === norm(b);
    }

    /** Forma canónica del contenido cargado (para dirty sin falsos positivos de whitespace/HTML comment). */
    function baselineContent() {
        if (!loaded) return '';
        const raw = loaded.content || '';
        if (anatomyActive()) {
            const parsed = parseAnatomyPrompt(raw);
            if (parsed.mode === 'anatomy') return serializeAnatomyPrompt(parsed);
        }
        if (skillFormActive()) {
            const parsed = parseSkillMarkdown(raw);
            if (parsed.mode === 'form') return serializeSkillMarkdown(parsed);
        }
        if (guardFormActive()) {
            const clase = ($('cfg-form-guard')?.dataset.clase) || currentGuardClass || 'input';
            const parsed = parseAgentGuardrailMarkdown(raw, clase);
            if (parsed.mode === 'form') return serializeAgentGuardrailMarkdown(parsed);
        }
        if (structuredActive()) {
            const parsed = parseAgentPrompt(raw);
            if (parsed.mode === 'form') return serializeAgentPrompt(parsed);
        }
        return raw;
    }

    /**
     * Detecta anatomía SDK: markdown con ## role / ## tasks / …
     * Preserva título H1; el comentario <!-- config-version --> se omite al parsear.
     */
    function parseAnatomyPrompt(content) {
        let body = String(content || '').replace(/^\uFEFF/, '');
        body = body.replace(/^<!--[\s\S]*?-->\s*/m, '');
        const known = new Set(ANATOMY_SECTION_IDS);
        const headingRe = /^##\s+([a-z][a-z0-9_]*)\s*$/gim;
        const matches = [...body.matchAll(headingRe)];
        if (!matches.length) return { mode: 'raw' };
        const ids = matches.map((m) => m[1].toLowerCase());
        if (!ids.includes('role') && !ids.includes('tasks')) return { mode: 'raw' };
        if (!ids.some((id) => known.has(id))) return { mode: 'raw' };

        const titleMatch = body.match(/^#\s+(.+)$/m);
        const title = titleMatch ? titleMatch[1].trim() : '';
        const fields = {};
        ANATOMY_SECTION_IDS.forEach((id) => {
            fields[id] = '';
        });

        for (let i = 0; i < matches.length; i += 1) {
            const id = matches[i][1].toLowerCase();
            if (!known.has(id)) continue;
            const start = matches[i].index + matches[i][0].length;
            const end = i + 1 < matches.length ? matches[i + 1].index : body.length;
            fields[id] = body.slice(start, end).replace(/^\n+/, '').replace(/\n+$/, '');
        }
        return { mode: 'anatomy', title, fields };
    }

    function serializeAnatomyPrompt({ title, fields }) {
        const heading =
            String(title || '').trim() ||
            'Instrucciones del agente — text fields (Agents SDK instructions)';
        const parts = [`# ${heading}`, ''];
        ANATOMY_SECTION_IDS.forEach((id) => {
            parts.push(`## ${id}`);
            const body = String((fields && fields[id]) || '').trim();
            parts.push(body);
            parts.push('');
        });
        return parts.join('\n').replace(/\n+$/, '') + '\n';
    }

    /** Divide un prompt "Rol:/Misión:" en campos legibles (legado). */
    function parseAgentPrompt(content) {
        const body = String(content || '').replace(/^\uFEFF/, '').replace(/^<!--[\s\S]*?-->\s*/m, '');
        const rolMatch = body.match(/^\s*Rol:\s*(.*)$/im);
        if (!rolMatch) return { mode: 'raw' };
        const afterRol = body.slice(rolMatch.index + rolMatch[0].length).replace(/^\n/, '');
        const misMatch = afterRol.match(/^\s*Misión:\s*/im);
        if (!misMatch) return { mode: 'raw' };
        const rest = afterRol.slice(misMatch.index + misMatch[0].length);
        const lines = rest.split('\n');
        const misionLines = [];
        const instrLines = [];
        let inMision = true;
        for (const line of lines) {
            const t = line.trim();
            if (inMision && misionLines.length > 0 && (t === '' || /^(No |Nunca |Cuando |Tu |Devuelve |Si |Mantén |Explicit|Toda |Antes |Cualquier |Marca |Separa )/i.test(t))) {
                inMision = false;
            }
            if (!inMision && instrLines.length === 0 && t === '') continue;
            (inMision ? misionLines : instrLines).push(line);
        }
        return {
            mode: 'form',
            rol: rolMatch[1].trim(),
            mision: misionLines.join('\n').trim(),
            instrucciones: instrLines.join('\n').trim(),
        };
    }

    function serializeAgentPrompt({ rol, mision, instrucciones }) {
        let out = `Rol: ${String(rol || '').trim()}\nMisión: ${String(mision || '').trim()}`;
        const instr = String(instrucciones || '').trim();
        if (instr) out += `\n${instr}`;
        return out;
    }

    function getEditorContent() {
        if (anatomyActive()) {
            const title = $('cfg-form-anatomy')?.dataset.title || '';
            return serializeAnatomyPrompt({
                title,
                fields: readAnatomyFieldsFromDom(),
            });
        }
        if (skillFormActive()) {
            return serializeSkillMarkdown(readSkillFieldsFromDom());
        }
        if (guardFormActive()) {
            return serializeAgentGuardrailMarkdown(readGuardFieldsFromDom());
        }
        if (structuredActive()) {
            return serializeAgentPrompt({
                rol: $('cfg-field-rol')?.value || '',
                mision: $('cfg-field-mision')?.value || '',
                instrucciones: $('cfg-field-instrucciones')?.value || '',
            });
        }
        return $('cfg-editor')?.value || '';
    }

    /** Refleja los campos estructurados en el textarea fuente (#cfg-editor). */
    function syncStructuredToEditor() {
        if (!anatomyActive() && !structuredActive() && !skillFormActive() && !guardFormActive()) return;
        const editor = $('cfg-editor');
        if (editor) editor.value = getEditorContent();
    }

    function setFormFieldsDisabled(disabled) {
        ['cfg-field-rol', 'cfg-field-mision', 'cfg-field-instrucciones', 'cfg-editor'].forEach((id) => {
            const el = $(id);
            if (el) el.disabled = Boolean(disabled);
        });
        setAnatomyDisabled(disabled);
        setSkillFormDisabled(disabled);
        setGuardFormDisabled(disabled);
    }

    function hideAllPromptForms() {
        $('cfg-form-anatomy')?.classList.add('hidden');
        $('cfg-form-structured')?.classList.add('hidden');
        $('cfg-form-skill')?.classList.add('hidden');
        $('cfg-form-guard')?.classList.add('hidden');
        $('cfg-form-prose')?.classList.remove('hidden');
        $('cfg-editor')?.classList.remove('raw-hidden');
    }

    function setEditorValue(value, { disabled = false, kind = null } = {}) {
        ensureAnatomyFormBuilt();
        ensureSkillFormBuilt();
        const editor = $('cfg-editor');
        if (!editor) return;

        const text = value == null ? '' : String(value);
        const useKind = kind || (loaded && loaded.kind) || null;

        hideAllPromptForms();

        if (useKind === 'prompt' && !disabled) {
            const anatomy = parseAnatomyPrompt(text);
            if (anatomy.mode === 'anatomy') {
                const form = $('cfg-form-anatomy');
                const prose = $('cfg-form-prose');
                if (form) {
                    form.classList.remove('hidden');
                    form.dataset.title = anatomy.title || '';
                }
                if (prose) prose.classList.add('hidden');
                editor.classList.add('raw-hidden');
                writeAnatomyFieldsToDom(anatomy.fields);
                editor.value = serializeAnatomyPrompt(anatomy);
                setFormFieldsDisabled(disabled);
                autosizeEditor();
                return;
            }
            const legacy = parseAgentPrompt(text);
            if (legacy.mode === 'form') {
                const structured = $('cfg-form-structured');
                const prose = $('cfg-form-prose');
                if (structured) structured.classList.remove('hidden');
                if (prose) prose.classList.add('hidden');
                editor.classList.add('raw-hidden');
                if ($('cfg-field-rol')) $('cfg-field-rol').value = legacy.rol || '';
                if ($('cfg-field-mision')) $('cfg-field-mision').value = legacy.mision || '';
                if ($('cfg-field-instrucciones')) $('cfg-field-instrucciones').value = legacy.instrucciones || '';
                editor.value = text;
                setFormFieldsDisabled(disabled);
                autosizeEditor();
                return;
            }
        }

        if (useKind === 'skill' && !disabled) {
            const skill = parseSkillMarkdown(text);
            if (skill.mode === 'form') {
                const form = $('cfg-form-skill');
                const prose = $('cfg-form-prose');
                if (form) form.classList.remove('hidden');
                if (prose) prose.classList.add('hidden');
                editor.classList.add('raw-hidden');
                writeSkillFieldsToDom(skill);
                editor.value = serializeSkillMarkdown(skill);
                setFormFieldsDisabled(disabled);
                autosizeEditor();
                return;
            }
        }

        if (useKind === 'agent_guardrail' && !disabled) {
            let clase = currentGuardClass || 'input';
            const key = String((loaded && loaded.key) || '');
            if (key.includes('__')) {
                const parts = key.split('__');
                const maybe = parts[parts.length - 1];
                if (GUARD_CLASS_ORDER.includes(maybe)) clase = maybe;
            }
            const guard = parseAgentGuardrailMarkdown(text, clase);
            if (guard.mode === 'form') {
                const form = $('cfg-form-guard');
                const prose = $('cfg-form-prose');
                if (form) form.classList.remove('hidden');
                if (prose) prose.classList.add('hidden');
                editor.classList.add('raw-hidden');
                writeGuardFieldsToDom(guard);
                editor.value = serializeAgentGuardrailMarkdown(guard);
                setFormFieldsDisabled(disabled);
                autosizeEditor();
                return;
            }
        }

        editor.value = text;
        setFormFieldsDisabled(disabled);
        autosizeEditor();
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

    function titleFromKey(key) {
        if (key === 'sistema') return 'Prompt Sistema';
        return String(key || '')
            .replace(/__/g, ' ')
            .replace(/_/g, ' ')
            .trim()
            .replace(/\b\w/g, (c) => c.toUpperCase());
    }

    function itemDisplayTitle(kind, key) {
        if (kind === 'prompt') {
            if (key === 'sistema') return 'Prompt Sistema';
            const agent = agentById(key) || (agentsMeta.agents || []).find((a) => a.prompt_key === key);
            if (agent) {
                return agent.nombre_corto || agent.titulo_profesional || displayName(agent.id);
            }
            return displayName(key);
        }
        if (kind === 'agent_guardrail') {
            const [agentId, clase] = String(key || '').split('__');
            const base = displayName(agentId);
            const claseLabel = { input: 'Input', output: 'Output', tools: 'Tools' }[clase] || titleFromKey(clase);
            return `${base} · ${claseLabel}`;
        }
        if (kind === 'skill') {
            return skillTrayLabel(key);
        }
        return titleFromKey(key);
    }

    /** Etiqueta legible para skill (sin ids crudos con guiones bajos). */
    function skillTrayLabel(skillKey) {
        return titleFromKey(skillKey);
    }

    function setEditorChrome(kind, key) {
        const label = $('cfg-current-label');
        const editorLabel = $('cfg-editor-label');
        if (label) {
            label.textContent = key ? itemDisplayTitle(kind, key) : 'Seleccione un ítem';
        }
        if (editorLabel) {
            const field =
                kind === 'skill' ? 'Skill' : kind === 'guardrail' || kind === 'agent_guardrail' ? 'Guardrail' : 'Prompt';
            editorLabel.textContent = field;
        }
        const meta = $('cfg-meta');
        if (meta) {
            meta.classList.add('hidden');
            meta.textContent = '';
        }
    }

    function agentById(id) {
        return (agentsMeta.agents || []).find((a) => a.id === id) || null;
    }

    function displayName(agentId) {
        const agent = agentById(agentId);
        if (agent && agent.nombre_corto) {
            return String(agent.nombre_corto).trim().toUpperCase();
        }
        if (AGENT_TAB_LABEL[agentId]) return AGENT_TAB_LABEL[agentId];
        if (!agent) return String(agentId || '').toUpperCase();
        const raw = String(agent.id || '').trim();
        const words = raw.replace(/_/g, ' ').split(/\s+/).filter(Boolean);
        if (words.length >= 2) return `${words[0]} ${words[1]}`.toUpperCase();
        return raw.toUpperCase();
    }

    function tabLabel(agentId) {
        if (AGENT_TAB_LABEL[agentId]) return AGENT_TAB_LABEL[agentId];
        const agent = agentById(agentId);
        if (agent && agent.nombre_corto) {
            // Pestaña compacta: primeras palabras significativas del nombre corto.
            const words = String(agent.nombre_corto).trim().split(/\s+/).filter(Boolean);
            if (words.length >= 3 && /^(de|del|la|el|y)$/i.test(words[1])) {
                return `${words[0]} ${words[2]}`.toUpperCase();
            }
            if (words.length >= 2) return `${words[0]} ${words[1]}`.toUpperCase();
            return String(agent.nombre_corto).toUpperCase();
        }
        return displayName(agentId);
    }

    function agentsInGroup(groupKey) {
        return (agentsMeta.agents || [])
            .filter((a) => (a.grupo || 'especialista') === groupKey)
            .map((a) => ({
                id: a.id,
                group: a.grupo || 'especialista',
                label: tabLabel(a.id),
                title: a.titulo_profesional || a.nombre_corto || a.id,
            }));
    }

    function syncTrayChrome() {
        // Re-entrancy guard: nested callers (setSectionTabs → sync → …) must not
        // stack connector schedules or rebuild skills mid-pass.
        if (traySyncDepth > 0) return;
        traySyncDepth += 1;
        try {
            const tray = $('agent-tray');
            const groupTray = $('group-tray');
            const sectionTray = $('section-tray');
            const guardTray = $('guard-tray');
            const sistema = $('btn-sistema');
            document.body.dataset.mode = editorMode;
            /* Misma tarjeta centrada + gutters azul para Prompt, Skills y Guardrails. */
            const configLayer =
                editorMode === 'sistema' ||
                currentSection === 'prompt' ||
                currentSection === 'skills' ||
                currentSection === 'guardrails';
            document.body.dataset.configActive = String(Boolean(configLayer));
            if (configLayer && currentSection) {
                document.body.dataset.configSection = currentSection;
            } else if (editorMode === 'sistema') {
                document.body.dataset.configSection = 'sistema';
            } else {
                delete document.body.dataset.configSection;
            }
            if (tray) {
                tray.dataset.group = currentGroup;
            }
            if (groupTray) {
                groupTray.dataset.group = editorMode === 'agent' ? currentGroup : '';
            }
            if (sectionTray) {
                sectionTray.dataset.group = currentGroup;
                const show = editorMode === 'agent' && Boolean(currentAgentId);
                sectionTray.classList.toggle('hidden', !show);
            }
            if (guardTray) {
                guardTray.dataset.group = currentGroup;
                const showGuard =
                    editorMode === 'agent' && Boolean(currentAgentId) && currentSection === 'guardrails';
                guardTray.classList.toggle('hidden', !showGuard);
                if (showGuard) renderGuardrailsTray();
            }
            const promptTray = $('prompt-tray');
            if (promptTray) {
                promptTray.dataset.group = currentGroup;
                const showPrompt =
                    editorMode === 'agent' && Boolean(currentAgentId) && currentSection === 'prompt';
                promptTray.classList.toggle('hidden', !showPrompt);
                if (showPrompt) ensurePromptPartTabsBuilt();
            }
            const skillsTray = $('skills-tray');
            if (skillsTray) {
                skillsTray.dataset.group = currentGroup;
                const showSkills =
                    editorMode === 'agent' && Boolean(currentAgentId) && currentSection === 'skills';
                skillsTray.classList.toggle('hidden', !showSkills);
                if (showSkills) renderSkillsTray();
            }
            if (sistema) sistema.classList.toggle('active', editorMode === 'sistema');
            updateEditorVisibility();
            scheduleGroupConnector();
        } finally {
            traySyncDepth -= 1;
        }
    }

    function updateEditorVisibility() {
        const panel = $('cfg-editor-panel');
        const empty = $('cfg-editor-empty');
        if (!panel || !empty) return;
        const showEditor =
            editorMode === 'sistema' ||
            currentSection === 'prompt' ||
            currentSection === 'skills' ||
            currentSection === 'guardrails';
        panel.classList.toggle('hidden', !showEditor);
        empty.classList.toggle('hidden', showEditor);
        updateSidebarVisibility();
        updateProseWorkspace();
        const pick = $('cfg-prompt-pick');
        const fields = $('cfg-anatomy-fields');
        if (currentSection === 'prompt') {
            if (pick) pick.classList.toggle('hidden', Boolean(currentPromptPart));
            if (fields) fields.classList.toggle('hidden', !currentPromptPart);
        }
    }

    /** Lista lateral retirada: Prompt / Skills / Guardrails usan trays + editor amplio. */
    function updateSidebarVisibility() {
        const sidebar = $('cfg-sidebar');
        if (sidebar) sidebar.classList.add('hidden');
    }

    /** Editor amplio para Skills/Guardrails; mensaje de elección si aún no hay ítem. */
    function updateProseWorkspace() {
        const prose = $('cfg-form-prose');
        const pick = $('cfg-prose-pick');
        const fields = $('cfg-prose-fields');
        const skillForm = $('cfg-form-skill');
        const guardForm = $('cfg-form-guard');
        const useWorkspace =
            currentSection === 'skills' ||
            currentSection === 'guardrails' ||
            (loaded && (loaded.kind === 'skill' || loaded.kind === 'agent_guardrail'));
        if (prose) prose.classList.toggle('is-workspace', Boolean(useWorkspace));

        const waitingSkill = currentSection === 'skills' && !currentKey;
        const waitingGuard = currentSection === 'guardrails' && !currentGuardClass;
        if (pick) {
            if (waitingSkill) {
                pick.textContent = 'Elija un skill del flujo con flechas para abrir su anatomía.';
                pick.classList.remove('hidden');
            } else if (waitingGuard) {
                pick.textContent = 'Elija Input, Output o Tools del flujo con flechas para abrir su anatomía.';
                pick.classList.remove('hidden');
            } else {
                pick.classList.add('hidden');
            }
        }
        const skillStructured = Boolean(skillForm && !skillForm.classList.contains('hidden'));
        const guardStructured = Boolean(guardForm && !guardForm.classList.contains('hidden'));
        if (fields) {
            const hideFields =
                ((currentSection === 'skills' || currentSection === 'guardrails') && !currentKey) ||
                skillStructured ||
                guardStructured;
            fields.classList.toggle('hidden', Boolean(hideFields));
        }
        if (prose && (skillStructured || guardStructured)) {
            prose.classList.add('hidden');
        } else if (prose && !anatomyActive() && !structuredActive()) {
            prose.classList.remove('hidden');
        }
    }

    function skillFlowArrowEl() {
        const el = document.createElement('div');
        el.className = 'skill-flow-arrow';
        el.setAttribute('aria-hidden', 'true');
        el.innerHTML =
            '<svg viewBox="0 0 14 22" fill="none" xmlns="http://www.w3.org/2000/svg">' +
            '<path d="M7 1v15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>' +
            '<path d="M2 11.5 7 19l5-7.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>' +
            '</svg>';
        return el;
    }

    function makeSkillNode(sid, { active = false } = {}) {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.setAttribute('role', 'option');
        btn.className = `skill-tab${active ? ' active' : ''}`;
        btn.dataset.skillId = sid;
        btn.title = sid;
        btn.setAttribute('aria-selected', active ? 'true' : 'false');
        const label = document.createElement('span');
        label.className = 'skill-tab-label';
        label.textContent = skillTrayLabel(sid);
        btn.appendChild(label);
        btn.addEventListener('click', () => {
            if (currentKey === sid && currentSection === 'skills') return;
            selectItem('skill', sid);
        });
        return btn;
    }

    function clearSkillFocus() {
        persistEditorDraft();
        selectGen += 1;
        setDirty(false);
        loaded = null;
        currentKey = null;
        setEditorValue('', { disabled: true });
        setEditorChrome(null, null);
        updateSharedBadge(null);
        const hist = $('cfg-btn-history');
        const reload = $('cfg-btn-reload');
        if (hist) hist.disabled = true;
        if (reload) reload.disabled = true;
        const host = $('skill-tabs');
        if (host) delete host.dataset.sig;
        setSectionTabs({ sync: false });
        renderSkillsTray();
        updateProseWorkspace();
        updateEditorVisibility();
        scheduleGroupConnector();
    }

    function bindSkillsBackBtn() {
        const back = $('skills-back-btn');
        if (!back || back.dataset.bound === '1') return;
        back.dataset.bound = '1';
        back.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            clearSkillFocus();
        });
    }

    function renderSkillsTray() {
        const host = $('skill-tabs');
        const tray = $('skills-tray');
        if (!host) return;
        bindSkillsBackBtn();
        const agent = agentById(currentAgentId);
        const ids = (agent && agent.skill_ids) || [];
        const focused = Boolean(currentKey && ids.includes(currentKey));
        const sig = `${currentAgentId || ''}|${ids.join(',')}|focus:${focused ? currentKey : ''}`;
        if (tray) tray.classList.toggle('is-focused', focused);
        if (host.dataset.sig === sig) {
            host.querySelectorAll('.skill-tab').forEach((btn) => {
                const active = btn.dataset.skillId === currentKey;
                btn.classList.toggle('active', active);
                btn.setAttribute('aria-selected', active ? 'true' : 'false');
            });
            return;
        }
        host.dataset.sig = sig;
        host.innerHTML = '';
        if (!ids.length) {
            host.innerHTML =
                '<p class="text-xs text-slate-500 uppercase tracking-wide px-2">Sin skills en este agente.</p>';
            return;
        }
        if (focused) {
            host.appendChild(makeSkillNode(currentKey, { active: true }));
            return;
        }
        ids.forEach((sid, index) => {
            if (index > 0) host.appendChild(skillFlowArrowEl());
            host.appendChild(makeSkillNode(sid, { active: false }));
        });
    }

    function makeGuardNode(clase, { active = false } = {}) {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.setAttribute('role', 'option');
        btn.className = `guard-class-tab${active ? ' active' : ''}`;
        btn.dataset.clase = clase;
        btn.title = GUARD_CLASS_LABEL[clase] || clase;
        btn.setAttribute('aria-selected', active ? 'true' : 'false');
        const label = document.createElement('span');
        label.className = 'guard-class-tab-label';
        label.textContent = GUARD_CLASS_LABEL[clase] || clase;
        btn.appendChild(label);
        btn.addEventListener('click', () => {
            if (currentGuardClass === clase && currentSection === 'guardrails' && currentKey) return;
            selectGuardClass(clase);
        });
        return btn;
    }

    function clearGuardFocus() {
        persistEditorDraft();
        selectGen += 1;
        setDirty(false);
        loaded = null;
        currentKey = null;
        currentGuardClass = null;
        setEditorValue('', { disabled: true });
        setEditorChrome(null, null);
        updateSharedBadge(null);
        const hist = $('cfg-btn-history');
        const reload = $('cfg-btn-reload');
        if (hist) hist.disabled = true;
        if (reload) reload.disabled = true;
        const host = $('guard-class-tabs');
        if (host) delete host.dataset.sig;
        setSectionTabs({ sync: false });
        renderGuardrailsTray();
        updateProseWorkspace();
        updateEditorVisibility();
        scheduleGroupConnector();
    }

    function bindGuardrailsBackBtn() {
        const back = $('guardrails-back-btn');
        if (!back || back.dataset.bound === '1') return;
        back.dataset.bound = '1';
        back.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            clearGuardFocus();
        });
    }

    function renderGuardrailsTray() {
        const host = $('guard-class-tabs');
        const tray = $('guard-tray');
        if (!host) return;
        bindGuardrailsBackBtn();
        const classes = GUARD_CLASS_ORDER.slice();
        const focused = Boolean(currentGuardClass && classes.includes(currentGuardClass));
        const sig = `${currentAgentId || ''}|${classes.join(',')}|focus:${focused ? currentGuardClass : ''}`;
        if (tray) tray.classList.toggle('is-focused', focused);
        if (host.dataset.sig === sig) {
            host.querySelectorAll('.guard-class-tab').forEach((btn) => {
                const active = btn.dataset.clase === currentGuardClass;
                btn.classList.toggle('active', active);
                btn.setAttribute('aria-selected', active ? 'true' : 'false');
            });
            return;
        }
        host.dataset.sig = sig;
        host.innerHTML = '';
        if (focused) {
            host.appendChild(makeGuardNode(currentGuardClass, { active: true }));
            return;
        }
        classes.forEach((clase, index) => {
            if (index > 0) host.appendChild(skillFlowArrowEl());
            host.appendChild(makeGuardNode(clase, { active: false }));
        });
    }

    async function selectGuardClass(clase) {
        persistEditorDraft();
        currentSection = 'guardrails';
        currentGuardClass = clase;
        currentPromptPart = null;
        setDirty(false);
        selectGen += 1;
        renderNav();
        const items = agentListItems();
        if (items[0]) await selectItem(items[0].kind, items[0].key);
        else {
            renderGuardrailsTray();
            scheduleGroupConnector();
        }
    }

    function cancelGroupConnectorSchedule() {
        if (connectorRaf) {
            cancelAnimationFrame(connectorRaf);
            connectorRaf = 0;
        }
        if (connectorTimer) {
            clearTimeout(connectorTimer);
            connectorTimer = 0;
        }
    }

    /** Coalesce connector redraws: one layout pass + one post-transition pass. */
    function scheduleGroupConnector() {
        cancelGroupConnectorSchedule();
        connectorRaf = requestAnimationFrame(() => {
            connectorRaf = 0;
            positionGroupConnector();
            // After tray/tab transitions (~0.22s)
            connectorTimer = setTimeout(() => {
                connectorTimer = 0;
                positionGroupConnector();
            }, 240);
        });
    }

    /**
     * Une dos nodos con un codo ortogonal (solo H/V) y punta de flecha en el destino.
     * Ruta mínima: vertical → horizontal → vertical. Sin curvas ni diagonales.
     * Devuelve el markup SVG (path + polygon) o '' si no hay espacio vertical.
     */
    function treeBranch(from, to, { active = false, arrowH = 7, arrowW = 5 } = {}) {
        const tipY = to.top - 2;
        const endY = tipY - arrowH;
        if (endY - from.y < 6) return '';
        const dx = to.cx - from.cx;
        let d;
        if (Math.abs(dx) < 3) {
            d = `M ${from.cx} ${from.y} V ${endY}`;
        } else {
            const busY = from.y + Math.max(4, (endY - from.y) * 0.42);
            d = `M ${from.cx} ${from.y} V ${busY} H ${to.cx} V ${endY}`;
        }
        const cls = active ? ' is-active' : '';
        return (
            `<path class="tree-line${cls}" d="${d}" />` +
            `<polygon class="tree-head${cls}" points="${to.cx} ${tipY}, ${to.cx - arrowW} ${endY}, ${
                to.cx + arrowW
            } ${endY}" />`
        );
    }

    /**
     * Dibuja el árbol:
     *  1) equipo → Agentes → miembros
     *  2) agente → Configuración → Prompt / Skills / Guardrails
     *  3) si Guardrails: → layer Guardrails → Input / Output / Tools
     *  4) si Prompt: → layer Prompt → apartados
     *  5) si Skills: → layer Skills (flujo con flechas entre skills; foco = un skill)
     */
    function positionGroupConnector() {
        if (connectorPositioning) return;
        connectorPositioning = true;
        try {
            const bar = $('agent-tabs-bar');
            const svg = $('group-connector');
            const tray = $('agent-tray');
            const label = tray && tray.querySelector('.agent-tray-label');
            if (!bar || !svg || !tray || !label) return;

            const hide = () => {
                svg.classList.remove('visible');
                svg.innerHTML = '';
            };

            if (editorMode !== 'agent') return hide();

            const groupTab = bar.querySelector('.group-tab.active');
            const agentTabs = Array.from(bar.querySelectorAll('.agent-tab'));
            if (!groupTab || !agentTabs.length) return hide();

            const barRect = bar.getBoundingClientRect();
            const rel = (rect) => ({
                cx: rect.left + rect.width / 2 - barRect.left,
                top: rect.top - barRect.top,
                bottom: rect.bottom - barRect.top,
            });

            const source = rel(groupTab.getBoundingClientRect());
            const hub = rel(label.getBoundingClientRect());

            const rects = agentTabs.map((el) => ({ el, box: el.getBoundingClientRect() }));
            const firstRowTop = Math.min(...rects.map((r) => r.box.top));
            const targets = [];
            for (const item of rects) {
                const inFirstRow = item.box.top - firstRowTop < 4;
                const caret = inFirstRow ? 'svg' : 'css';
                if (item.el.dataset.caret !== caret) item.el.dataset.caret = caret;
                if (inFirstRow) targets.push({ el: item.el, ...rel(item.box) });
            }
            if (!targets.length) return hide();

            const parts = [];
            const activeId = currentAgentId;
            const trunkTop = source.bottom - 1;

            // Nivel 1: equipo → label "Agentes".
            parts.push(treeBranch({ cx: source.cx, y: trunkTop }, hub, { active: true }));
            parts.push(`<circle class="tree-origin" cx="${source.cx}" cy="${trunkTop}" r="3.5" />`);

            // Nivel 2: label "Agentes" → cada miembro.
            const hubBottom = { cx: hub.cx, y: hub.bottom + 1 };
            for (const target of targets) {
                parts.push(treeBranch(hubBottom, target, { active: target.el.dataset.agentId === activeId }));
            }

            // Nivel 3: agente seleccionado → label "Configuración" → Prompt / Skills / Guardrails.
            const sectionTray = $('section-tray');
            const activeAgent = targets.find((t) => t.el.dataset.agentId === activeId);
            if (sectionTray && !sectionTray.classList.contains('hidden') && activeAgent) {
                const sectionLabel = sectionTray.querySelector('.section-tray-label');
                const sectionTabs = Array.from(sectionTray.querySelectorAll('.section-tab'));
                if (sectionLabel && sectionTabs.length) {
                    const sectionHub = rel(sectionLabel.getBoundingClientRect());
                    parts.push(treeBranch({ cx: activeAgent.cx, y: activeAgent.bottom + 1 }, sectionHub, { active: true }));
                    const sectionHubBottom = { cx: sectionHub.cx, y: sectionHub.bottom + 1 };
                    for (const tab of sectionTabs) {
                        parts.push(
                            treeBranch(sectionHubBottom, rel(tab.getBoundingClientRect()), {
                                active: tab.dataset.section === currentSection,
                            }),
                        );
                    }

                    // Nivel 4a: Guardrails → label (flujo con flechas entre clases; foco = una clase).
                    const guardTray = $('guard-tray');
                    const guardrailsTab = sectionTabs.find((t) => t.dataset.section === 'guardrails');
                    if (
                        guardTray &&
                        !guardTray.classList.contains('hidden') &&
                        currentSection === 'guardrails' &&
                        guardrailsTab
                    ) {
                        const guardLabel = guardTray.querySelector('.guard-tray-label');
                        if (guardLabel) {
                            const guardHub = rel(guardLabel.getBoundingClientRect());
                            const guardSrc = rel(guardrailsTab.getBoundingClientRect());
                            parts.push(
                                treeBranch({ cx: guardSrc.cx, y: guardSrc.bottom + 1 }, guardHub, {
                                    active: true,
                                }),
                            );
                            if (currentGuardClass) {
                                const activeGuard = Array.from(
                                    guardTray.querySelectorAll('.guard-class-tab'),
                                ).find((el) => el.dataset.clase === currentGuardClass);
                                if (activeGuard) {
                                    parts.push(
                                        treeBranch(
                                            { cx: guardHub.cx, y: guardHub.bottom + 1 },
                                            rel(activeGuard.getBoundingClientRect()),
                                            { active: true },
                                        ),
                                    );
                                }
                            }
                        }
                    }

                    // Nivel 4b: Prompt → label → Función / Tareas / Responsabilidades / Estilo.
                    const promptTray = $('prompt-tray');
                    const promptTab = sectionTabs.find((t) => t.dataset.section === 'prompt');
                    if (
                        promptTray &&
                        !promptTray.classList.contains('hidden') &&
                        currentSection === 'prompt' &&
                        promptTab
                    ) {
                        const promptLabel = promptTray.querySelector('.prompt-tray-label');
                        const promptTabs = Array.from(promptTray.querySelectorAll('.prompt-part-tab'));
                        if (promptLabel && promptTabs.length) {
                            const promptHub = rel(promptLabel.getBoundingClientRect());
                            const promptSrc = rel(promptTab.getBoundingClientRect());
                            parts.push(treeBranch({ cx: promptSrc.cx, y: promptSrc.bottom + 1 }, promptHub, { active: true }));
                            const promptHubBottom = { cx: promptHub.cx, y: promptHub.bottom + 1 };
                            for (const tab of promptTabs) {
                                parts.push(
                                    treeBranch(promptHubBottom, rel(tab.getBoundingClientRect()), {
                                        active: tab.dataset.part === currentPromptPart,
                                    }),
                                );
                            }
                        }
                    }

                    // Nivel 4c: Skills → label del tray (flujo con flechas entre nodos en el tray).
                    const skillsTray = $('skills-tray');
                    const skillsTab = sectionTabs.find((t) => t.dataset.section === 'skills');
                    if (
                        skillsTray &&
                        !skillsTray.classList.contains('hidden') &&
                        currentSection === 'skills' &&
                        skillsTab
                    ) {
                        const skillsLabel = skillsTray.querySelector('.skills-tray-label');
                        if (skillsLabel) {
                            const skillsHub = rel(skillsLabel.getBoundingClientRect());
                            const skillsSrc = rel(skillsTab.getBoundingClientRect());
                            parts.push(
                                treeBranch({ cx: skillsSrc.cx, y: skillsSrc.bottom + 1 }, skillsHub, {
                                    active: true,
                                }),
                            );
                            // En foco: flecha SVG también al nodo del skill seleccionado.
                            if (currentKey) {
                                const activeSkill = Array.from(
                                    skillsTray.querySelectorAll('.skill-tab'),
                                ).find((el) => el.dataset.skillId === currentKey);
                                if (activeSkill) {
                                    parts.push(
                                        treeBranch(
                                            { cx: skillsHub.cx, y: skillsHub.bottom + 1 },
                                            rel(activeSkill.getBoundingClientRect()),
                                            { active: true },
                                        ),
                                    );
                                }
                            }
                        }
                    }
                }
            }

            const nextGroup = groupTab.dataset.group || currentGroup;
            const markup = parts.join('');
            if (svg.dataset.group !== nextGroup) svg.dataset.group = nextGroup;
            if (svg.innerHTML !== markup) svg.innerHTML = markup;
            svg.classList.add('visible');
        } finally {
            connectorPositioning = false;
        }
    }

    function setSectionTabs({ sync = true } = {}) {
        const isSistema = editorMode === 'sistema';
        document.querySelectorAll('.section-tab').forEach((btn) => {
            const active = btn.dataset.section === currentSection;
            btn.classList.toggle('active', active);
            if (isSistema && btn.dataset.section !== 'prompt') {
                btn.classList.add('opacity-40', 'pointer-events-none');
            } else {
                btn.classList.remove('opacity-40', 'pointer-events-none');
            }
        });
        document.querySelectorAll('.guard-class-tab').forEach((btn) => {
            btn.classList.toggle('active', btn.dataset.clase === currentGuardClass);
            btn.setAttribute('aria-selected', btn.dataset.clase === currentGuardClass ? 'true' : 'false');
        });
        document.querySelectorAll('.prompt-part-tab').forEach((btn) => {
            btn.classList.toggle('active', btn.dataset.part === currentPromptPart);
        });
        document.querySelectorAll('.skill-tab').forEach((btn) => {
            const active = btn.dataset.skillId === currentKey;
            btn.classList.toggle('active', active);
            btn.setAttribute('aria-selected', active ? 'true' : 'false');
        });
        if (sync) syncTrayChrome();
        renderCompactNav();
    }

    function renderGroupTabs() {
        const host = $('group-tabs');
        if (!host) return;
        if (host.dataset.built !== '1') {
            host.dataset.built = '1';
            host.innerHTML = '';
            for (const groupKey of GROUP_ORDER) {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'group-tab';
                btn.dataset.group = groupKey;
                btn.textContent = GROUP_LABELS[groupKey] || groupKey.toUpperCase();
                btn.addEventListener('click', () => selectGroup(groupKey));
                host.appendChild(btn);
            }
        }
        host.querySelectorAll('.group-tab').forEach((btn) => {
            btn.classList.toggle(
                'active',
                currentGroup === btn.dataset.group && editorMode === 'agent',
            );
        });
    }

    function renderAgentTabs() {
        const host = $('agent-tabs');
        if (!host) return;
        if (editorMode !== 'agent') {
            host.dataset.sig = '';
            host.innerHTML = '';
            return;
        }
        const items = agentsInGroup(currentGroup);
        const sig = `${currentGroup}|${items.map((i) => i.id).join(',')}`;
        if (host.dataset.sig !== sig) {
            host.dataset.sig = sig;
            host.innerHTML = '';
            if (!items.length) {
                host.innerHTML =
                    '<p class="text-xs text-slate-500 uppercase tracking-wide">Sin agentes en este grupo.</p>';
                return;
            }
            for (const item of items) {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'agent-tab';
                btn.dataset.group = item.group;
                btn.dataset.agentId = item.id;
                btn.textContent = item.label;
                btn.title = item.title || item.label;
                btn.addEventListener('click', () => selectAgent(item.id));
                host.appendChild(btn);
            }
        }
        host.querySelectorAll('.agent-tab').forEach((btn) => {
            btn.classList.toggle('active', btn.dataset.agentId === currentAgentId);
        });
    }

    function configItemsForKind(kind) {
        return configIndex[kind] || [];
    }

    function agentListItems() {
        if (editorMode === 'sistema') {
            const item = configItemsForKind('prompt').find((it) => it.key === 'sistema');
            return item ? [item] : [{ kind: 'prompt', key: 'sistema', path: 'agente/prompts/sistema.md', active_version: 0 }];
        }
        const agent = agentById(currentAgentId);
        if (!agent || !currentSection) return [];

        if (currentSection === 'prompt') {
            const item = configItemsForKind('prompt').find((it) => it.key === agent.prompt_key);
            return item
                ? [item]
                : [{ kind: 'prompt', key: agent.prompt_key, path: `agente/prompts/agents/${agent.prompt_key}.md`, active_version: 0 }];
        }
        if (currentSection === 'skills') {
            const q = String($('cfg-search')?.value || '').trim().toLowerCase();
            return (agent.skill_ids || [])
                .map((sid) => {
                    const item = configItemsForKind('skill').find((it) => it.key === sid);
                    return item || { kind: 'skill', key: sid, path: `.cursor/skills/${sid}/SKILL.md`, active_version: 0 };
                })
                .filter((it) => !q || it.key.toLowerCase().includes(q));
        }
        const key = currentGuardClass && (agent.guardrails || {})[currentGuardClass];
        if (!key) return [];
        const item = configItemsForKind('agent_guardrail').find((it) => it.key === key);
        return item
            ? [item]
            : [{ kind: 'agent_guardrail', key, path: `config/guardrails/agents/${currentAgentId}/${currentGuardClass}.md`, active_version: 0 }];
    }

    function updateSharedBadge(skillKey) {
        const el = $('cfg-shared-badge');
        if (!el) return;
        sharedBadgeForKey = skillKey;
        if (!skillKey || editorMode === 'sistema') {
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
        const names = others.map((id) => displayName(id));
        el.textContent = `SKILL COMPARTIDA (1 SOLA FUENTE). AL GUARDAR CAMBIA TAMBIÉN PARA: ${names.join(', ')}`;
        el.classList.remove('hidden');
    }

    function renderList() {
        const list = $('cfg-item-list');
        const count = $('cfg-list-count');
        const header = $('cfg-list-header');
        if (!list) return;

        const items = agentListItems();
        let label = 'PROMPT';
        if (currentSection === 'skills') label = 'SKILLS';
        else if (currentSection === 'guardrails') {
            label = currentGuardClass
                ? `GUARDRAIL ${String(currentGuardClass).toUpperCase()}`
                : 'GUARDRAILS';
        } else if (!currentSection) {
            label = 'CONFIG';
        }

        if (count) count.textContent = `${items.length} ${label}`;
        list.innerHTML = '';
        // Con la lista vacía y sin búsqueda activa el panel queda solo fondo;
        // si hay búsqueda se conserva el campo para poder borrarla.
        const hasQuery = Boolean(String($('cfg-search')?.value || '').trim());
        if (header) header.classList.toggle('hidden', !items.length && !hasQuery);
        if (!items.length) return;

        for (const it of items) {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = `cfg-item w-full text-left px-3 py-2.5 rounded-xl border border-slate-800 hover:bg-slate-800 transition-all text-sm ${
                currentKey === it.key && loaded && loaded.kind === it.kind ? 'active' : 'bg-slate-950/40'
            }`;
            const ver = it.active_version ? `v${it.active_version}` : 'seed';
            let extra = '';
            if (currentSection === 'skills') {
                const agent = agentById(currentAgentId);
                const shared = agent && agent.skills_shared_with && agent.skills_shared_with[it.key];
                if (shared && shared.length) {
                    extra = `<div class="text-[11px] text-amber-300/90 mt-0.5 uppercase tracking-wide">Compartida · ${shared.length} otro(s)</div>`;
                }
            }
            btn.innerHTML = `<div class="font-bold truncate uppercase tracking-wide text-sm">${escapeHtml(it.key)}</div>
                <div class="text-[11px] text-slate-400 mt-0.5 flex justify-between gap-2">
                    <span class="truncate">${escapeHtml(it.path || '')}</span>
                    <span class="font-semibold">${ver}</span>
                </div>${extra}`;
            btn.addEventListener('click', () => selectItem(it.kind, it.key));
            list.appendChild(btn);
        }
    }

    function closeUxCrumbMenus() {
        document.querySelectorAll('.ux-crumb-menu.open').forEach((menu) => {
            menu.classList.remove('open');
        });
        ['ux-crumb-group', 'ux-crumb-agent'].forEach((id) => {
            const btn = $(id);
            if (btn) btn.setAttribute('aria-expanded', 'false');
        });
    }

    function renderMapPanel() {
        const groupHost = $('map-group-chips');
        const agentHost = $('map-agent-chips');
        if (groupHost) {
            groupHost.innerHTML = '';
            GROUP_ORDER.forEach((g) => {
                const chip = document.createElement('span');
                chip.className = 'map-chip' + (g === currentGroup && workspaceView === 'map' ? ' active' : '');
                chip.textContent = GROUP_LABELS[g] || g;
                groupHost.appendChild(chip);
            });
        }
        if (agentHost) {
            agentHost.innerHTML = '';
            const agents = agentsInGroup(currentGroup);
            if (!agents.length) {
                const empty = document.createElement('span');
                empty.className = 'map-chip';
                empty.textContent = 'Sin agentes en este equipo';
                agentHost.appendChild(empty);
            } else {
                agents.forEach((a) => {
                    const chip = document.createElement('button');
                    chip.type = 'button';
                    chip.className = 'map-chip' + (a.id === currentAgentId ? ' active' : '');
                    chip.textContent = a.label || a.id;
                    chip.title = a.title || a.id;
                    chip.addEventListener('click', async () => {
                        await setWorkspaceView('editor');
                        await selectAgent(a.id, { groupAlreadySet: true });
                    });
                    agentHost.appendChild(chip);
                });
            }
        }
    }

    async function setWorkspaceView(view) {
        workspaceView = view === 'map' ? 'map' : 'editor';
        document.body.classList.toggle('ux-map-view', workspaceView === 'map');
        document.querySelectorAll('.ux-view-tab').forEach((btn) => {
            const active = btn.dataset.view === workspaceView;
            btn.classList.toggle('active', active);
            btn.setAttribute('aria-selected', active ? 'true' : 'false');
        });
        if (workspaceView === 'map') {
            closeUxCrumbMenus();
            renderMapPanel();
            return;
        }
        // Volver al editor: asegurar un apartado abierto.
        if (editorMode === 'agent' && currentAgentId && !currentSection) {
            await openConfigSection('prompt');
        } else {
            renderCompactNav();
        }
    }

    function fillUxCrumbMenu(menu, items, { activeValue, onPick } = {}) {
        if (!menu) return;
        menu.innerHTML = '';
        if (!items.length) {
            const empty = document.createElement('button');
            empty.type = 'button';
            empty.disabled = true;
            empty.textContent = 'Sin opciones';
            menu.appendChild(empty);
            return;
        }
        items.forEach((it) => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.setAttribute('role', 'menuitem');
            btn.textContent = it.label;
            if (it.title) btn.title = it.title;
            btn.classList.toggle('active', it.value === activeValue);
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                closeUxCrumbMenus();
                if (typeof onPick === 'function') onPick(it.value);
            });
            menu.appendChild(btn);
        });
    }

    function renderCompactNav() {
        const crumbGroup = $('ux-crumb-group');
        const crumbAgent = $('ux-crumb-agent');
        const menuGroup = $('ux-menu-group');
        const menuAgent = $('ux-menu-agent');
        const crumbSection = $('ux-crumb-section');
        const crumbPart = $('ux-crumb-part');
        const sepSection = $('ux-crumb-sep-section');
        const sepPart = $('ux-crumb-sep-part');
        const partRow = $('ux-part-pills');
        if (!crumbGroup || !crumbAgent) return;

        const groupLabel = GROUP_LABELS[currentGroup] || currentGroup || 'Equipo';
        crumbGroup.textContent = editorMode === 'sistema' ? 'Sistema' : groupLabel;
        crumbGroup.disabled = editorMode === 'sistema';

        const agents = agentsInGroup(currentGroup);
        const agent = agentById(currentAgentId);
        const agentLabel = agent
            ? agent.nombre_corto || agent.titulo_profesional || tabLabel(agent.id)
            : agents[0]?.label || 'Agente';
        crumbAgent.textContent = editorMode === 'sistema' ? 'Prompt sistema' : agentLabel;
        crumbAgent.disabled = editorMode === 'sistema' || !agents.length;

        fillUxCrumbMenu(
            menuGroup,
            GROUP_ORDER.map((g) => ({ value: g, label: GROUP_LABELS[g] || g })),
            {
                activeValue: currentGroup,
                onPick: (g) => selectGroup(g),
            },
        );
        fillUxCrumbMenu(
            menuAgent,
            agents.map((a) => ({
                value: a.id,
                label: a.label || a.id,
                title: a.title || a.id,
            })),
            {
                activeValue: currentAgentId,
                onPick: (id) => selectAgent(id),
            },
        );

        const sectionLabel =
            editorMode === 'sistema'
                ? 'Sistema'
                : currentSection === 'prompt'
                  ? 'Prompt'
                  : currentSection === 'skills'
                    ? 'Skills'
                    : currentSection === 'guardrails'
                      ? 'Guardrails'
                      : '—';
        if (crumbSection) {
            crumbSection.textContent = sectionLabel;
            crumbSection.classList.toggle('current', Boolean(currentSection) || editorMode === 'sistema');
        }
        if (sepSection) sepSection.classList.toggle('hidden', editorMode === 'sistema');

        document.querySelectorAll('#ux-section-pills .ux-pill').forEach((btn) => {
            btn.classList.toggle('active', btn.dataset.section === currentSection);
            btn.disabled = editorMode === 'sistema';
        });
        $('ux-section-pills')?.classList.toggle('hidden', editorMode === 'sistema');

        if (!partRow) return;
        if (editorMode === 'sistema' || !currentSection) {
            partRow.classList.add('hidden');
            partRow.innerHTML = '';
            if (crumbPart) crumbPart.classList.add('hidden');
            if (sepPart) sepPart.classList.add('hidden');
            return;
        }

        partRow.classList.remove('hidden');
        let partLabel = '—';
        if (currentSection === 'prompt') {
            const sig = `prompt|${ANATOMY_UI_GROUPS.map((g) => g.id).join(',')}`;
            if (partRow.dataset.sig !== sig) {
                partRow.dataset.sig = sig;
                partRow.innerHTML = '';
                ANATOMY_UI_GROUPS.forEach((g) => {
                    const btn = document.createElement('button');
                    btn.type = 'button';
                    btn.className = 'ux-pill';
                    btn.dataset.part = g.id;
                    btn.textContent = g.trayLabel || g.label;
                    btn.addEventListener('click', () => selectPromptPart(g.id));
                    partRow.appendChild(btn);
                });
            }
            partRow.querySelectorAll('.ux-pill').forEach((btn) => {
                btn.classList.toggle('active', btn.dataset.part === currentPromptPart);
            });
            const g = ANATOMY_UI_GROUPS.find((x) => x.id === currentPromptPart);
            partLabel = g ? g.trayLabel || g.label : '—';
        } else if (currentSection === 'skills') {
            const ag = agentById(currentAgentId);
            const ids = (ag && ag.skill_ids) || [];
            const sig = `skills|${currentAgentId || ''}|${ids.join(',')}`;
            if (partRow.dataset.sig !== sig) {
                partRow.dataset.sig = sig;
                partRow.innerHTML = '';
                if (!ids.length) {
                    partRow.innerHTML =
                        '<span class="ux-crumb" style="cursor:default">Sin skills en este agente</span>';
                } else {
                    ids.forEach((sid) => {
                        const btn = document.createElement('button');
                        btn.type = 'button';
                        btn.className = 'ux-pill';
                        btn.dataset.skillId = sid;
                        btn.textContent = skillTrayLabel(sid);
                        btn.title = sid;
                        btn.addEventListener('click', () => selectItem('skill', sid));
                        partRow.appendChild(btn);
                    });
                }
            }
            partRow.querySelectorAll('.ux-pill[data-skill-id]').forEach((btn) => {
                btn.classList.toggle('active', btn.dataset.skillId === currentKey);
            });
            partLabel = currentKey ? skillTrayLabel(currentKey) : '—';
        } else if (currentSection === 'guardrails') {
            const sig = `guard|${GUARD_CLASS_ORDER.join(',')}`;
            if (partRow.dataset.sig !== sig) {
                partRow.dataset.sig = sig;
                partRow.innerHTML = '';
                GUARD_CLASS_ORDER.forEach((clase) => {
                    const btn = document.createElement('button');
                    btn.type = 'button';
                    btn.className = 'ux-pill';
                    btn.dataset.clase = clase;
                    btn.textContent = GUARD_CLASS_LABEL[clase] || clase;
                    btn.addEventListener('click', () => selectGuardClass(clase));
                    partRow.appendChild(btn);
                });
            }
            partRow.querySelectorAll('.ux-pill').forEach((btn) => {
                btn.classList.toggle('active', btn.dataset.clase === currentGuardClass);
            });
            partLabel = currentGuardClass
                ? GUARD_CLASS_LABEL[currentGuardClass] || currentGuardClass
                : '—';
        }

        const showPart =
            (currentSection === 'prompt' && currentPromptPart) ||
            (currentSection === 'skills' && currentKey) ||
            (currentSection === 'guardrails' && currentGuardClass);
        if (crumbPart) {
            crumbPart.textContent = partLabel;
            crumbPart.classList.toggle('hidden', !showPart);
            crumbPart.classList.toggle('current', Boolean(showPart));
        }
        if (sepPart) sepPart.classList.toggle('hidden', !showPart);
        if (workspaceView === 'map') renderMapPanel();
    }

    async function openConfigSection(section) {
        if (!section || editorMode === 'sistema') return;
        persistEditorDraft();
        currentSection = section;
        currentGuardClass = null;
        currentPromptPart = null;
        setDirty(false);
        loaded = null;
        currentKey = null;
        updateSharedBadge(null);
        const hist = $('cfg-btn-history');
        const reload = $('cfg-btn-reload');
        if (hist) hist.disabled = true;
        if (reload) reload.disabled = true;
        renderNav();

        try {
            if (section === 'guardrails') {
                const guardHost = $('guard-class-tabs');
                if (guardHost) delete guardHost.dataset.sig;
                $('guard-tray')?.classList.remove('is-focused');
                await selectGuardClass(GUARD_CLASS_ORDER[0] || 'input');
                return;
            }
            if (section === 'skills') {
                const skillHost = $('skill-tabs');
                if (skillHost) delete skillHost.dataset.sig;
                $('skills-tray')?.classList.remove('is-focused');
                updateProseWorkspace();
                const items = agentListItems();
                if (items[0]) await selectItem(items[0].kind, items[0].key);
                else {
                    renderSkillsTray();
                    scheduleGroupConnector();
                }
                return;
            }
            if (section === 'prompt') {
                const items = agentListItems();
                if (items[0]) await selectItem(items[0].kind, items[0].key);
                ensurePromptPartTabsBuilt();
                const firstPart = ANATOMY_UI_GROUPS[0]?.id;
                if (firstPart) await selectPromptPart(firstPart);
                else activateAnatomyTab(null);
            }
        } catch (err) {
            toast(String(err.message || err));
        } finally {
            renderCompactNav();
        }
    }

    function renderNav() {
        renderGroupTabs();
        renderAgentTabs();
        setSectionTabs({ sync: false });
        try {
            renderList();
        } catch (err) {
            console.warn('renderList:', err);
        }
        syncTrayChrome();
        renderCompactNav();
    }

    async function loadConfigIndex() {
        const r = await fetchAuditApi('/api/audit/config/catalog');
        if (!r.ok) throw new Error('No se pudo cargar el índice de configuración');
        const data = await r.json();
        configIndex = data.items || { prompt: [], guardrail: [], skill: [], agent_guardrail: [] };
        renderList();
    }

    async function loadAgents() {
        const r = await fetchAuditApi('/api/audit/config/agents');
        if (!r.ok) throw new Error('No se pudo cargar agentes');
        agentsMeta = await r.json();
        renderNav();
    }

    async function selectGroup(groupKey) {
        persistEditorDraft();
        editorMode = 'agent';
        currentGroup = groupKey;
        const items = agentsInGroup(groupKey);
        const first = items[0];
        if (!first) {
            currentAgentId = null;
            renderNav();
            return;
        }
        await selectAgent(first.id, { skipDirtyConfirm: true, groupAlreadySet: true });
    }

    async function selectSistema() {
        persistEditorDraft();
        selectGen += 1;
        editorMode = 'sistema';
        document.body.dataset.mode = 'sistema';
        currentAgentId = null;
        currentSection = 'prompt';
        currentPromptPart = null;
        currentGuardClass = null;
        setDirty(false);
        loaded = null;
        currentKey = null;
        setEditorValue('', { disabled: true });
        setEditorChrome('prompt', 'sistema');
        updateSharedBadge(null);
        $('cfg-btn-history').disabled = true;
        $('cfg-btn-reload').disabled = true;
        renderNav();
        const items = agentListItems();
        if (items[0]) await selectItem(items[0].kind, items[0].key);
    }

    async function selectAgent(agentId, opts = {}) {
        if (!opts.skipDirtyConfirm) persistEditorDraft();
        selectGen += 1;
        editorMode = 'agent';
        currentAgentId = agentId;
        if (!opts.groupAlreadySet) {
            const agent = agentById(agentId);
            currentGroup = (agent && agent.grupo) || 'especialista';
        }
        // UX compacta: al elegir agente se abre Prompt → primer apartado.
        currentSection = null;
        currentGuardClass = null;
        currentPromptPart = null;
        setDirty(false);
        loaded = null;
        currentKey = null;
        setEditorValue('', { disabled: true });
        setEditorChrome(null, null);
        updateSharedBadge(null);
        $('cfg-btn-history').disabled = true;
        $('cfg-btn-reload').disabled = true;
        renderNav();
        await openConfigSection('prompt');
    }

    async function selectItem(kind, key, opts = {}) {
        const gen = ++selectGen;
        if (loaded && (loaded.kind !== kind || loaded.key !== key)) {
            persistEditorDraft();
        }
        currentKey = key;
        setSectionTabs({ sync: false });
        renderList();
        $('cfg-btn-history').disabled = true;
        $('cfg-btn-reload').disabled = true;
        $('cfg-btn-save').disabled = true;
        setEditorValue('Cargando…', { disabled: true });
        setEditorChrome(kind, key);
        try {
            const r = await fetchAuditApi(`/api/audit/config/${encodeURIComponent(kind)}/${encodeURIComponent(key)}`);
            if (gen !== selectGen) return;
            if (!r.ok) {
                const err = await r.json().catch(() => ({}));
                throw new Error(err.detail || `Error ${r.status}`);
            }
            loaded = await r.json();
            if (gen !== selectGen) return;
            if (opts.discardDraft) clearDraft(kind, key);

            const serverContent = loaded.content || '';
            const draft = opts.discardDraft ? null : readDraft(kind, key);
            let content = serverContent;
            let note = '';
            let isDirty = false;
            noteManual = false;
            if (draft && draft.content !== serverContent) {
                content = draft.content;
                note = draft.note || '';
                noteManual = Boolean(draft.noteManual);
                isDirty = true;
            } else if (draft) {
                // Borrador idéntico al servidor: limpiar.
                clearDraft(kind, key);
                note = draft.noteManual ? draft.note || '' : '';
                noteManual = Boolean(draft.noteManual && note);
            }

            if (gen !== selectGen) return;
            setEditorValue(content, { disabled: false });
            if ($('cfg-note')) $('cfg-note').value = note;
            if (isDirty && !noteManual && !note) {
                applyAutoNote();
            }
            $('cfg-btn-history').disabled = false;
            $('cfg-btn-reload').disabled = false;
            setEditorChrome(kind, key);
            setDirty(isDirty);
            if (kind === 'skill') {
                updateSharedBadge(key);
            } else {
                updateSharedBadge(null);
            }
            renderList();
            updateProseWorkspace();
            if (kind === 'skill' && currentSection === 'skills') {
                renderSkillsTray();
            }
            if (kind === 'agent_guardrail' && currentSection === 'guardrails') {
                renderGuardrailsTray();
            }
            if (kind === 'prompt' && currentSection === 'prompt' && editorMode === 'agent') {
                ensurePromptPartTabsBuilt();
                activateAnatomyTab(currentPromptPart);
            }
            scheduleGroupConnector();
        } catch (e) {
            if (gen !== selectGen) return;
            loaded = null;
            setEditorValue('', { disabled: true });
            toast(String(e.message || e));
        }
    }

    function updateMeta() {
        // Metadatos técnicos ocultos: el encabezado muestra solo el nombre legible.
        const meta = $('cfg-meta');
        if (meta) {
            meta.classList.add('hidden');
            meta.textContent = '';
        }
    }

    async function saveCurrent() {
        if (!loaded || !dirty) return;
        syncStructuredToEditor();
        const content = getEditorContent();
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
                await loadConfigIndex();
                await selectItem(loaded.kind, loaded.key);
                return;
            }
            if (!r.ok) throw new Error(data.detail || `Error ${r.status}`);
            clearDraft(data.kind, data.key);
            let msg = `Guardado en DB ${data.kind}/${data.key} v${data.version}`;
            if (data.file_exported === false) {
                msg += ' (DB OK; no se pudo exportar archivo)';
            }
            if (loaded.kind === 'skill' && sharedBadgeForKey) {
                msg += ' · skill compartida actualizada para todos';
            }
            toast(msg);
            setDirty(false);
            await loadConfigIndex();
            await selectItem(data.kind, data.key, { discardDraft: true });
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
        list.innerHTML = '<p class="text-base text-slate-500">Cargando…</p>';
        try {
            const r = await fetchAuditApi(
                `/api/audit/config/${encodeURIComponent(loaded.kind)}/${encodeURIComponent(loaded.key)}/versions?limit=100`,
            );
            if (!r.ok) throw new Error('No se pudo cargar historial');
            const data = await r.json();
            const versions = data.versions || [];
            if (!versions.length) {
                list.innerHTML = '<p class="text-base text-slate-400">Sin versiones en DB (aún seed de archivo).</p>';
                return;
            }
            list.innerHTML = '';
            for (const v of versions) {
                const card = document.createElement('div');
                card.className = 'border border-slate-600 rounded-xl p-4 space-y-2 bg-slate-800';
                const isActive = v.version === loaded.version;
                card.innerHTML = `
                    <div class="flex items-start justify-between gap-2">
                        <div>
                            <p class="text-base font-bold text-slate-100">v${v.version}${isActive ? ' <span class="text-emerald-400">(activa)</span>' : ''}</p>
                            <p class="text-sm text-slate-400">${escapeHtml(v.author_email || '—')} · ${escapeHtml((v.created_at || '').replace('T', ' ').slice(0, 19))}</p>
                            <p class="text-sm text-slate-300 mt-1">${escapeHtml(v.note || '')}</p>
                            <p class="text-xs text-slate-500 font-mono">${escapeHtml(v.checksum || '')}</p>
                        </div>
                        <div class="flex flex-col gap-2">
                            <button type="button" class="cfg-diff-btn ui-btn text-sm px-3 py-2 rounded-lg border border-slate-600 bg-slate-800/80 text-slate-100 hover:bg-slate-700" data-version="${v.version}">Diff vs activa</button>
                            ${
                                isActive
                                    ? ''
                                    : `<button type="button" class="cfg-restore-btn ui-btn text-sm px-3 py-2 rounded-lg border border-amber-700/60 bg-amber-950/50 text-amber-200 hover:bg-amber-900/60" data-version="${v.version}">Restaurar</button>`
                            }
                        </div>
                    </div>
                    <pre class="text-sm text-slate-300 rounded-lg p-3 whitespace-pre-wrap max-h-28 overflow-hidden border border-slate-700" style="background:#0f172a">${escapeHtml(v.content_preview || '')}</pre>`;
                list.appendChild(card);
            }
            list.querySelectorAll('.cfg-restore-btn').forEach((btn) => {
                btn.addEventListener('click', () => restoreVersion(Number(btn.dataset.version)));
            });
            list.querySelectorAll('.cfg-diff-btn').forEach((btn) => {
                btn.addEventListener('click', () => showDiff(Number(btn.dataset.version)));
            });
        } catch (e) {
            list.innerHTML = `<p class="text-base text-red-600">${escapeHtml(e.message || e)}</p>`;
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
            await loadConfigIndex();
            await selectItem(data.kind, data.key, { discardDraft: true });
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
            legend.className = 'text-sm text-slate-500 mb-2';
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
        if (uiBound) return;
        uiBound = true;
        $('btn-sistema')?.addEventListener('click', async () => {
            await setWorkspaceView('editor');
            selectSistema();
        });

        document.querySelectorAll('.ux-view-tab').forEach((btn) => {
            btn.addEventListener('click', () => {
                void setWorkspaceView(btn.dataset.view);
            });
        });
        $('map-go-editor')?.addEventListener('click', () => {
            void setWorkspaceView('editor');
        });
        $('map-go-gerente')?.addEventListener('click', async () => {
            await setWorkspaceView('editor');
            const gerente = (agentsMeta.agents || []).find(
                (a) => resolveAgentId(a.id) === 'coordinador_caso' || a.grupo === 'coordinacion',
            );
            if (gerente) await selectAgent(gerente.id, { groupAlreadySet: true });
        });

        document.querySelectorAll('.section-tab').forEach((btn) => {
            btn.addEventListener('click', async () => {
                await setWorkspaceView('editor');
                await openConfigSection(btn.dataset.section);
            });
        });
        document.querySelectorAll('#ux-section-pills .ux-pill').forEach((btn) => {
            btn.addEventListener('click', async () => {
                await setWorkspaceView('editor');
                await openConfigSection(btn.dataset.section);
            });
        });
        $('cfg-editor-empty')?.addEventListener('click', async (e) => {
            const btn = e.target.closest('[data-empty-section]');
            if (!btn) return;
            await openConfigSection(btn.dataset.emptySection);
        });
        const toggleCrumbMenu = (btnId, menuId) => {
            const btn = $(btnId);
            const menu = $(menuId);
            if (!btn || !menu) return;
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                if (btn.disabled) return;
                const willOpen = !menu.classList.contains('open');
                closeUxCrumbMenus();
                if (willOpen) {
                    menu.classList.add('open');
                    btn.setAttribute('aria-expanded', 'true');
                }
            });
        };
        toggleCrumbMenu('ux-crumb-group', 'ux-menu-group');
        toggleCrumbMenu('ux-crumb-agent', 'ux-menu-agent');
        document.addEventListener('click', (e) => {
            if (e.target.closest('.ux-crumb-wrap')) return;
            closeUxCrumbMenus();
        });
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') closeUxCrumbMenus();
        });

        $('cfg-search')?.addEventListener('input', renderList);
        const onEditorInput = () => {
            autosizeEditor();
            if (!loaded) return;
            syncStructuredToEditor();
            setDirty(!contentEquals(getEditorContent(), baselineContent()));
            scheduleDraftPersist();
            scheduleAutoNote();
        };
        ['cfg-editor', 'cfg-field-rol', 'cfg-field-mision', 'cfg-field-instrucciones'].forEach((id) => {
            $(id)?.addEventListener('input', onEditorInput);
            $(id)?.addEventListener('blur', applyAutoNote);
        });
        // Campos de anatomía estructurados + listas dinámicas.
        const anatomyForm = $('cfg-form-anatomy');
        anatomyForm?.addEventListener('input', (e) => {
            if (!e.target || !e.target.closest('#cfg-form-anatomy')) return;
            if (e.target.classList && e.target.classList.contains('cfg-rich')) {
                e.target.classList.toggle('is-empty', !editorHtmlToMd(e.target.innerHTML).trim());
                autosizeRich(e.target);
            }
            onEditorInput();
        });
        anatomyForm?.addEventListener('change', (e) => {
            if (!e.target || !e.target.closest('#cfg-form-anatomy')) return;
            onEditorInput();
        });
        anatomyForm?.addEventListener('blur', (e) => {
            if (e.target && (e.target.matches('textarea.cfg-anatomy-input, select.cfg-anatomy-select') || e.target.classList?.contains('cfg-rich'))) {
                applyAutoNote();
            }
        }, true);
        anatomyForm?.addEventListener('click', (e) => {
            const btn = e.target && e.target.closest('[data-action]');
            if (!btn || !anatomyForm.contains(btn)) return;
            const action = btn.dataset.action;
            if (action === 'add-paso') {
                const steps = [...document.querySelectorAll('#cfg-anatomy-pasos .cfg-paso-text')]
                    .map((el) => readRichMd(el.id));
                steps.push('');
                renderPasosList(steps);
                setAnatomyDisabled(false);
                onEditorInput();
                return;
            }
            if (action === 'remove-paso') {
                const row = btn.closest('.cfg-anatomy-item');
                if (row) row.remove();
                const steps = [...document.querySelectorAll('#cfg-anatomy-pasos .cfg-paso-text')]
                    .map((el) => readRichMd(el.id));
                renderPasosList(steps.length ? steps : ['']);
                setAnatomyDisabled(false);
                onEditorInput();
                return;
            }
            if (action === 'add-resp') {
                const items = [...document.querySelectorAll('#cfg-anatomy-responsabilidades .cfg-anatomy-item-resp')].map((row) => ({
                    type: row.querySelector('.cfg-resp-type')?.value || 'good_behavior',
                    text: readRichMd(row.querySelector('.cfg-resp-text')?.id || ''),
                }));
                items.push({ type: 'good_behavior', text: '' });
                renderResponsabilidadesList(items);
                setAnatomyDisabled(false);
                onEditorInput();
                return;
            }
            if (action === 'remove-resp') {
                const row = btn.closest('.cfg-anatomy-item-resp');
                if (row) row.remove();
                const items = [...document.querySelectorAll('#cfg-anatomy-responsabilidades .cfg-anatomy-item-resp')].map((r) => ({
                    type: r.querySelector('.cfg-resp-type')?.value || 'good_behavior',
                    text: readRichMd(r.querySelector('.cfg-resp-text')?.id || ''),
                }));
                renderResponsabilidadesList(items.length ? items : [{ type: 'good_behavior', text: '' }]);
                setAnatomyDisabled(false);
                onEditorInput();
            }
        });

        // Anatomía de skills (text fields SKILL.md).
        const skillForm = $('cfg-form-skill');
        skillForm?.addEventListener('input', (e) => {
            if (!e.target || !e.target.closest('#cfg-form-skill')) return;
            if (e.target.classList && e.target.classList.contains('cfg-rich')) {
                e.target.classList.toggle('is-empty', !editorHtmlToMd(e.target.innerHTML).trim());
                autosizeRich(e.target);
            }
            onEditorInput();
        });
        skillForm?.addEventListener('change', (e) => {
            if (!e.target || !e.target.closest('#cfg-form-skill')) return;
            onEditorInput();
        });
        skillForm?.addEventListener('blur', (e) => {
            if (
                e.target &&
                (e.target.matches('textarea.cfg-anatomy-input, input.cfg-anatomy-input') ||
                    e.target.classList?.contains('cfg-rich'))
            ) {
                applyAutoNote();
            }
        }, true);
        skillForm?.addEventListener('click', (e) => {
            const btn = e.target && e.target.closest('[data-action]');
            if (!btn || !skillForm.contains(btn)) return;
            const action = btn.dataset.action;
            if (action === 'add-skill-paso') {
                const steps = [...document.querySelectorAll('#cfg-skill-pasos .cfg-skill-paso-text')].map((el) =>
                    readRichMd(el.id),
                );
                steps.push('');
                renderSkillPasosList(steps);
                setSkillFormDisabled(false);
                onEditorInput();
                return;
            }
            if (action === 'remove-skill-paso') {
                const row = btn.closest('.cfg-anatomy-item');
                if (row) row.remove();
                const steps = [...document.querySelectorAll('#cfg-skill-pasos .cfg-skill-paso-text')].map((el) =>
                    readRichMd(el.id),
                );
                renderSkillPasosList(steps.length ? steps : ['']);
                setSkillFormDisabled(false);
                onEditorInput();
            }
        });

        const guardForm = $('cfg-form-guard');
        guardForm?.addEventListener('input', (e) => {
            if (!e.target || !e.target.closest('#cfg-form-guard')) return;
            if (e.target.classList && e.target.classList.contains('cfg-rich')) {
                e.target.classList.toggle('is-empty', !editorHtmlToMd(e.target.innerHTML).trim());
                autosizeRich(e.target);
            }
            onEditorInput();
        });
        guardForm?.addEventListener('change', (e) => {
            if (!e.target || !e.target.closest('#cfg-form-guard')) return;
            onEditorInput();
        });
        guardForm?.addEventListener('blur', (e) => {
            if (
                e.target &&
                (e.target.matches('textarea.cfg-anatomy-input, input.cfg-anatomy-input') ||
                    e.target.classList?.contains('cfg-rich'))
            ) {
                applyAutoNote();
            }
        }, true);

        const NOTE_COLLAPSE_KEY = 'audit-cfg-note-collapsed';
        const noteBar = $('cfg-note-bar');
        const noteToggle = $('cfg-note-toggle');
        const applyNoteCollapsed = (collapsed) => {
            if (!noteBar || !noteToggle) return;
            noteBar.classList.toggle('is-collapsed', Boolean(collapsed));
            noteToggle.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
        };
        try {
            // Default colapsada (mock UX); solo expandir si el usuario la dejó abierta.
            applyNoteCollapsed(localStorage.getItem(NOTE_COLLAPSE_KEY) !== '0');
        } catch (_) {
            applyNoteCollapsed(true);
        }
        noteToggle?.addEventListener('click', () => {
            const next = !noteBar?.classList.contains('is-collapsed');
            applyNoteCollapsed(next);
            try { localStorage.setItem(NOTE_COLLAPSE_KEY, next ? '1' : '0'); } catch (_) { /* ignore */ }
        });

        $('cfg-note')?.addEventListener('input', () => {
            if (!loaded) return;
            noteManual = Boolean(($('cfg-note').value || '').trim());
            scheduleDraftPersist();
        });
        window.addEventListener('resize', autosizeEditor);
        $('cfg-btn-save')?.addEventListener('click', saveCurrent);
        $('cfg-btn-reload')?.addEventListener('click', () => {
            if (!loaded) return;
            if (dirty && !confirm('¿Descartar el borrador local y recargar desde el servidor?')) return;
            selectItem(loaded.kind, loaded.key, { discardDraft: true });
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
        window.addEventListener('beforeunload', () => {
            persistEditorDraft();
        });
        window.addEventListener('resize', scheduleGroupConnector);
        wireFmtToolbar();
    }

    async function boot() {
        bindUi();
        document.body.classList.add('ux-compact');
        document.body.dataset.mode = 'agent';
        if (!sessionReady) return;
        if (bootInFlight) return bootInFlight;
        bootInFlight = (async () => {
            try {
                await Promise.all([loadConfigIndex(), loadAgents()]);
                currentGroup = 'coordinacion';
                editorMode = 'agent';
                const firstAgent = (agentsMeta.agents || []).find((a) => a.grupo === 'coordinacion');
                if (firstAgent) {
                    await selectAgent(firstAgent.id, { groupAlreadySet: true });
                } else {
                    await selectGroup('especialista');
                }
                renderCompactNav();
                if (workspaceView === 'map') renderMapPanel();
            } catch (e) {
                toast(String(e.message || e));
            }
        })();
        try {
            await bootInFlight;
        } finally {
            bootInFlight = null;
        }
    }

    window.addEventListener('audit-session-ready', (ev) => {
        sessionReady = Boolean(ev.detail?.email);
        if (sessionReady) void boot();
    });

    if (window.__AUDIT_SESSION_EMAIL__) {
        sessionReady = true;
        void boot();
    }
})();
