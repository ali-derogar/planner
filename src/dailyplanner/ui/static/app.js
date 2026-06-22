/* Daily Planner SPA client */
window._actions = [];

function action(cmd, params) {
    window._actions.push({ cmd: cmd, params: params || {} });
}

var _searchTimer = null;
function debounceSearch(q) {
    clearTimeout(_searchTimer);
    _searchTimer = setTimeout(function() { action('set_search', { q: q }); }, 350);
}

function esc(s) {
    return String(s)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function escJs(s) {
    return String(s)
        .replace(/\\/g, '\\\\')
        .replace(/'/g, "\\'")
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function pd(n) {
    var d = '۰۱۲۳۴۵۶۷۸۹';
    return String(n).replace(/\d/g, function(c) { return d[+c]; });
}

/* Toast */
var _toastTimer = null;
function showToast(msg, type) {
    var el = document.getElementById('toast');
    if (!el) return;
    el.textContent = msg;
    el.className = 'toast show ' + (type || '');
    clearTimeout(_toastTimer);
    _toastTimer = setTimeout(function() { el.className = 'toast'; }, 2800);
}

/* Modal */
var _modal = null;
var _modalValidators = {
    hms: function(v) { return /^\d{1,2}:\d{2}(:\d{2})?$/.test(v.trim()); },
    hm: function(v) { return /^\d{1,2}:\d{2}$/.test(v.trim()); },
    amount: function(v) { return parseFloat(v) > 0; },
    budget: function(v) { var n = parseFloat(v); return !isNaN(n) && n >= 0; },
    required: function(v) { return v.trim().length > 0; },
};

function pad2(n) {
    return String(Math.max(0, parseInt(n, 10) || 0)).padStart(2, '0');
}

function secondsToHms(secs) {
    secs = Math.max(0, parseInt(secs, 10) || 0);
    var h = Math.floor(secs / 3600);
    var m = Math.floor((secs % 3600) / 60);
    var s = secs % 60;
    return h + ':' + pad2(m) + ':' + pad2(s);
}

function parseTimeParts(value, includeSeconds) {
    var parts = String(value || '').trim().split(':');
    var h = parseInt(parts[0], 10);
    var m = parseInt(parts[1], 10);
    if (isNaN(h)) h = 0;
    if (isNaN(m)) m = 0;
    var s = 0;
    if (includeSeconds && parts.length > 2) {
        s = parseInt(parts[2], 10);
        if (isNaN(s)) s = 0;
    }
    return { h: h, m: m, s: s };
}

function getTimePickerValue(el) {
    if (!el) return '';
    var h = 0, m = 0, s = 0;
    el.querySelectorAll('.time-picker-col').forEach(function(col) {
        var v = parseInt(col.dataset.val, 10) || 0;
        if (col.dataset.unit === 'h') h = v;
        else if (col.dataset.unit === 'm') m = v;
        else if (col.dataset.unit === 's') s = v;
    });
    if (el.dataset.mode === 'hms') {
        return h + ':' + pad2(m) + ':' + pad2(s);
    }
    return h + ':' + pad2(m);
}

function updateTimePickerPreview(picker) {
    var preview = picker.querySelector('.time-picker-preview');
    if (!preview) return;
    var raw = getTimePickerValue(picker);
    var parts = raw.split(':');
    if (picker.dataset.mode === 'hms') {
        preview.textContent = pd(parts[0]) + ':' + pd(parts[1]) + ':' + pd(parts[2]);
    } else {
        preview.textContent = pd(parts[0]) + ':' + pd(parts[1]);
    }
}

function setTimePickerValues(picker, h, m, s) {
    picker.querySelectorAll('.time-picker-col').forEach(function(col) {
        var unit = col.dataset.unit;
        var max = parseInt(col.dataset.max, 10);
        var val = unit === 'h' ? h : (unit === 'm' ? m : s);
        val = Math.max(0, Math.min(max, val));
        col.dataset.val = val;
        var num = col.querySelector('.time-picker-val');
        if (num) num.textContent = pd(pad2(val));
    });
    updateTimePickerPreview(picker);
}

function stepTimeUnit(picker, unit, delta) {
    var col = picker.querySelector('.time-picker-col[data-unit="' + unit + '"]');
    if (!col) return;
    var max = parseInt(col.dataset.max, 10);
    var val = (parseInt(col.dataset.val, 10) || 0) + delta;
    if (val > max) val = 0;
    if (val < 0) val = max;
    col.dataset.val = val;
    var num = col.querySelector('.time-picker-val');
    if (num) num.textContent = pd(pad2(val));
    updateTimePickerPreview(picker);
}

function buildTimeCol(key, label, val, max, pickerWrap) {
    var col = document.createElement('div');
    col.className = 'time-picker-col';
    col.dataset.unit = key;
    col.dataset.max = String(max);
    col.dataset.val = String(Math.max(0, Math.min(max, val)));

    var up = document.createElement('button');
    up.type = 'button';
    up.className = 'time-picker-btn';
    up.textContent = '▲';
    up.onclick = function(e) {
        e.preventDefault();
        e.stopPropagation();
        stepTimeUnit(pickerWrap, key, 1);
    };

    var num = document.createElement('div');
    num.className = 'time-picker-val';
    num.textContent = pd(pad2(col.dataset.val));

    var down = document.createElement('button');
    down.type = 'button';
    down.className = 'time-picker-btn';
    down.textContent = '▼';
    down.onclick = function(e) {
        e.preventDefault();
        e.stopPropagation();
        stepTimeUnit(pickerWrap, key, -1);
    };

    var lbl = document.createElement('div');
    lbl.className = 'time-picker-lbl';
    lbl.textContent = label;

    col.appendChild(up);
    col.appendChild(num);
    col.appendChild(down);
    col.appendChild(lbl);
    return col;
}

function buildDurationPresets(pickerWrap) {
    var presets = [
        { label: '۱۵ دقیقه', h: 0, m: 15, s: 0 },
        { label: '۳۰ دقیقه', h: 0, m: 30, s: 0 },
        { label: '۴۵ دقیقه', h: 0, m: 45, s: 0 },
        { label: '۱ ساعت', h: 1, m: 0, s: 0 },
        { label: '۱:۳۰', h: 1, m: 30, s: 0 },
        { label: '۲ ساعت', h: 2, m: 0, s: 0 },
    ];
    var row = document.createElement('div');
    row.className = 'time-picker-presets';
    presets.forEach(function(p) {
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'time-preset-btn';
        btn.textContent = p.label;
        btn.onclick = function(e) {
            e.preventDefault();
            e.stopPropagation();
            setTimePickerValues(pickerWrap, p.h, p.m, p.s);
        };
        row.appendChild(btn);
    });
    return row;
}

function buildClockPresets(pickerWrap, kind) {
    var presets = kind === 'sleep'
        ? [{ label: '۲۲:۰۰', h: 22, m: 0 }, { label: '۲۳:۰۰', h: 23, m: 0 }, { label: '۰۰:۰۰', h: 0, m: 0 }]
        : [{ label: '۰۶:۰۰', h: 6, m: 0 }, { label: '۰۷:۰۰', h: 7, m: 0 }, { label: '۰۸:۰۰', h: 8, m: 0 }];
    var row = document.createElement('div');
    row.className = 'time-picker-presets';
    presets.forEach(function(p) {
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'time-preset-btn';
        btn.textContent = p.label;
        btn.onclick = function(e) {
            e.preventDefault();
            e.stopPropagation();
            setTimePickerValues(pickerWrap, p.h, p.m, 0);
        };
        row.appendChild(btn);
    });
    return row;
}

function buildTimePickerEl(field) {
    var includeSeconds = field.type === 'time-hms';
    var parts = parseTimeParts(field.value, includeSeconds);
    var wrap = document.createElement('div');
    wrap.className = 'time-picker';
    wrap.id = 'mf-' + field.key;
    wrap.dataset.key = field.key;
    wrap.dataset.mode = includeSeconds ? 'hms' : 'hm';

    var preview = document.createElement('div');
    preview.className = 'time-picker-preview';
    wrap.appendChild(preview);

    var cols = document.createElement('div');
    cols.className = 'time-picker-cols';
    var units = includeSeconds
        ? [{ k: 'h', label: 'ساعت', max: 99, val: parts.h }, { k: 'm', label: 'دقیقه', max: 59, val: parts.m }, { k: 's', label: 'ثانیه', max: 59, val: parts.s }]
        : [{ k: 'h', label: 'ساعت', max: 23, val: parts.h }, { k: 'm', label: 'دقیقه', max: 59, val: parts.m }];
    units.forEach(function(u) {
        cols.appendChild(buildTimeCol(u.k, u.label, u.val, u.max, wrap));
    });
    wrap.appendChild(cols);

    if (includeSeconds) {
        wrap.appendChild(buildDurationPresets(wrap));
    } else if (field.presetKind) {
        wrap.appendChild(buildClockPresets(wrap, field.presetKind));
    }

    updateTimePickerPreview(wrap);
    return wrap;
}

function showDurationModal(title, cmd, taskId, seconds) {
    showModal({
        title: title,
        cmd: cmd,
        params: { id: taskId },
        fields: [{ label: 'مدت زمان', key: 'value', type: 'time-hms', value: secondsToHms(seconds), validate: 'hms' }],
    });
}

function showClockModal(title, cmd, hmValue, presetKind) {
    showModal({
        title: title,
        cmd: cmd,
        fields: [{ label: 'ساعت', key: 'value', type: 'time-hm', value: hmValue || '00:00', validate: 'hm', presetKind: presetKind }],
    });
}

function showModal(config) {
    _modal = config;
    document.getElementById('modal-title').textContent = config.title || '';
    var fc = document.getElementById('modal-fields');
    fc.innerHTML = '';
    (config.fields || []).forEach(function(f) {
        var lbl = document.createElement('div');
        lbl.className = 'modal-label';
        lbl.textContent = f.label;
        fc.appendChild(lbl);
        if (f.type === 'select') {
            var sel = document.createElement('select');
            sel.className = 'modal-input';
            sel.id = 'mf-' + f.key;
            (f.options || []).forEach(function(opt) {
                var o = document.createElement('option');
                o.value = opt;
                o.textContent = opt;
                if (f.value === opt) o.selected = true;
                sel.appendChild(o);
            });
            fc.appendChild(sel);
        } else if (f.type === 'time-hms' || f.type === 'time-hm') {
            fc.appendChild(buildTimePickerEl(f));
        } else if (f.type === 'textarea') {
            var ta = document.createElement('textarea');
            ta.className = 'modal-input modal-textarea';
            ta.id = 'mf-' + f.key;
            ta.placeholder = f.placeholder || '';
            if (f.value) ta.value = f.value;
            fc.appendChild(ta);
        } else {
            var inp = document.createElement('input');
            inp.type = f.type || 'text';
            inp.className = 'modal-input';
            inp.id = 'mf-' + f.key;
            inp.placeholder = f.placeholder || '';
            if (f.value !== undefined && f.value !== null) inp.value = f.value;
            fc.appendChild(inp);
        }
    });
    document.getElementById('modal-error').textContent = '';
    document.getElementById('modal').style.display = 'flex';
    var first = fc.querySelector('input,select,textarea');
    if (first) setTimeout(function() { first.focus(); }, 80);
}

function confirmModal() {
    if (!_modal) return;
    var params = Object.assign({}, _modal.params || {});
    var valid = true;
    var errEl = document.getElementById('modal-error');
    (_modal.fields || []).forEach(function(f) {
        var el = document.getElementById('mf-' + f.key);
        var val = '';
        if (f.type === 'time-hms' || f.type === 'time-hm') {
            val = getTimePickerValue(el);
        } else {
            val = el ? el.value : '';
        }
        params[f.key] = val;
        if (f.validate && _modalValidators[f.validate]) {
            if (!_modalValidators[f.validate](val)) valid = false;
        }
    });
    if (!valid) {
        errEl.textContent = 'لطفاً فرم را کامل کنید';
        return;
    }
    action(_modal.cmd, params);
    closeModal();
}

function closeModal() {
    document.getElementById('modal').style.display = 'none';
    _modal = null;
}

document.addEventListener('click', function(e) {
    if (e.target.id === 'modal') closeModal();
});

/* Timer update from Python */
function updateTimer(taskId, display) {
    var el1 = document.getElementById('tdur-' + taskId);
    var el2 = document.getElementById('tbig-' + taskId);
    if (el1) el1.textContent = display;
    if (el2) el2.textContent = display;
}

/* SVG chart */
function sparklineSvg(points, w, h) {
    if (!points || points.length === 0) return '';
    var max = Math.max.apply(null, points.concat([1]));
    var step = w / (points.length - 1 || 1);
    var pts = points.map(function(v, i) {
        var x = i * step;
        var y = h - (v / max) * (h - 4) - 2;
        return x.toFixed(1) + ',' + y.toFixed(1);
    }).join(' ');
    return '<svg class="sparkline" viewBox="0 0 ' + w + ' ' + h + '" preserveAspectRatio="none">' +
        '<polyline fill="none" stroke="#5E5CE6" stroke-width="2" points="' + pts + '"/>' +
        '</svg>';
}

function financeLineChartSvg(chart, w, h) {
    if (!chart || !chart.income || !chart.income.length) return '';
    var lines = [
        { points: chart.income, color: '#4DD980', label: 'درآمد', width: 1.5, opacity: 0.85 },
        { points: chart.expense, color: '#FF7359', label: 'هزینه', width: 1.5, opacity: 0.85 },
        { points: chart.investment || chart.income.map(function() { return 0; }), color: '#FFB020', label: 'سرمایه\u200cگذاری', width: 1.5, opacity: 0.85 },
        { points: chart.balance, color: '#5E5CE6', label: 'موجودی', width: 2.5, opacity: 1, fill: true },
    ];
    var allVals = [];
    lines.forEach(function(l) { allVals = allVals.concat(l.points); });
    var min = Math.min.apply(null, allVals.concat([0]));
    var max = Math.max.apply(null, allVals.concat([1]));
    var range = max - min || 1;
    var n = chart.income.length;
    var step = w / (n - 1 || 1);
    var padT = 14, padB = 8, padX = 4;

    function toY(v) {
        return padT + (h - padT - padB) * (1 - (v - min) / range);
    }
    function toPts(arr) {
        return arr.map(function(v, i) {
            return (padX + i * (w - padX * 2) / (n - 1 || 1)).toFixed(1) + ',' + toY(v).toFixed(1);
        });
    }

    var svg = '<svg class="finance-line-chart" viewBox="0 0 ' + w + ' ' + h + '" preserveAspectRatio="none">';
    svg += '<defs><linearGradient id="finGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#5E5CE6"/><stop offset="100%" stop-color="#5E5CE6" stop-opacity="0"/></linearGradient></defs>';
    for (var g = 0; g <= 3; g++) {
        var gy = padT + (h - padT - padB) * g / 3;
        svg += '<line x1="' + padX + '" y1="' + gy.toFixed(1) + '" x2="' + (w - padX) + '" y2="' + gy.toFixed(1) + '" stroke="#2C2C2E" stroke-width="0.5"/>';
    }
    if (min < 0 && max > 0) {
        var zeroY = toY(0).toFixed(1);
        svg += '<line x1="' + padX + '" y1="' + zeroY + '" x2="' + (w - padX) + '" y2="' + zeroY + '" stroke="#5E5CE6" stroke-width="1" stroke-dasharray="4,3" opacity="0.4"/>';
    }
    var balPts = toPts(chart.balance);
    var areaPath = 'M' + balPts[0];
    for (var i = 1; i < balPts.length; i++) areaPath += ' L' + balPts[i];
    var zeroLine = min < 0 ? toY(0) : toY(min);
    areaPath += ' L' + (padX + (n - 1) * (w - padX * 2) / (n - 1 || 1)).toFixed(1) + ',' + zeroLine.toFixed(1);
    areaPath += ' L' + padX + ',' + zeroLine.toFixed(1) + ' Z';
    svg += '<path d="' + areaPath + '" fill="url(#finGrad)" opacity="0.25"/>';
    lines.forEach(function(line) {
        var pts = toPts(line.points).join(' ');
        svg += '<polyline fill="none" stroke="' + line.color + '" stroke-width="' + line.width + '" stroke-linejoin="round" stroke-linecap="round" opacity="' + line.opacity + '" points="' + pts + '"/>';
    });
    svg += '</svg>';

    var legend = '<div class="fin-chart-legend">';
    lines.forEach(function(line) {
        legend += '<span class="fin-legend-item"><span class="fin-legend-dot" style="background:' + line.color + '"></span>' + line.label + '</span>';
    });
    legend += '</div>';
    return legend + '<div class="fin-chart-wrap">' + svg + '</div>';
}

var FIN_CAT_ICONS = {
    'عمومی': '📦', 'غذا': '🍽', 'حمل\u200cونقل': '🚌', 'خانه': '🏠',
    'قبوض': '💡', 'تفریح': '🎬', 'درمان': '💊', 'آموزش': '📚',
    'حقوق': '💼',
    'سهام': '📈', 'طلا': '🥇', 'رمزارز': '₿', 'سپرده بانکی': '🏦',
    'صندوق': '💹', 'املاک': '🏗', 'سایر': '💎',
};
function finCatIcon(cat) { return FIN_CAT_ICONS[cat] || '💳'; }

function finTypeInfo(type) {
    if (type === 'income') return { cls: 'income', arrow: '↑', label: 'درآمد' };
    if (type === 'investment') return { cls: 'investment', arrow: '◆', label: 'سرمایه\u200cگذاری' };
    return { cls: 'expense', arrow: '↓', label: 'هزینه' };
}

function finEmptyState(icon, msg, btnLabel, btnOnclick) {
    var html = '<div class="fin-empty"><span class="fin-empty-icon">' + icon + '</span><p>' + msg + '</p>';
    if (btnLabel) html += '<button class="fin-empty-btn" onclick="' + btnOnclick + '">' + btnLabel + '</button>';
    return html + '</div>';
}

function heatmapHtml(heatmap) {
    if (!heatmap || !heatmap.length) return '';
    var html = '<div class="heatmap">';
    heatmap.forEach(function(d) {
        var cls = 'hm-cell';
        if (d.eff >= 70) cls += ' hm-high';
        else if (d.eff >= 40) cls += ' hm-mid';
        else if (d.total > 0) cls += ' hm-low';
        else cls += ' hm-empty';
        html += '<div class="' + cls + '" title="' + esc(d.date) + '"></div>';
    });
    return html + '</div>';
}

/* Task card */
function taskCard(t) {
    var cardCls = 'task-card';
    if (t.is_running) cardCls += ' is-running';
    else if (t.is_useful === true) cardCls += ' is-useful';
    else if (t.is_useful === false) cardCls += ' is-not-useful';

    var star = t.is_starred ? '★' : '☆';
    var starCls = t.is_starred ? 'task-star' : 'task-star empty';
    var durCls = t.is_running ? 'task-dur running' : 'task-dur';
    var chev = t.is_expanded ? '▲' : '▼';

    var progress = '';
    if (t.estimated > 0) {
        progress = '<div class="task-progress"><div class="task-progress-fill" style="width:' + t.progress + '%"></div></div>';
        if (t.remaining_fmt) {
            progress += '<div class="task-remaining">مانده: ' + esc(t.remaining_fmt) + '</div>';
        }
    }

    var header = '<a href="javascript:void(0)" onclick="action(\'toggle_task\',{id:' + t.id + '})" class="task-header">' +
        '<span class="' + starCls + '" onclick="event.preventDefault();event.stopPropagation();action(\'toggle_star\',{id:' + t.id + '})">' + star + '</span>' +
        '<span class="task-title-wrap">' + esc(t.title) + '</span>' +
        '<span class="' + durCls + '" id="tdur-' + t.id + '">' + esc(t.display_fmt) + '</span>' +
        '<span class="task-chevron">' + chev + '</span></a>' + progress;

    var detail = '';
    if (t.is_expanded) {
        var timerBtn = t.is_running
            ? '<button class="btn-stop" onclick="action(\'stop_timer\',{id:' + t.id + '})">⏹ توقف</button>'
            : '<button class="btn-start" onclick="action(\'start_timer\',{id:' + t.id + '})">▶ شروع</button>';
        var uCls = t.is_useful === true ? 'chip-useful-on' : 'chip-useful-off';
        var nuCls = t.is_useful === false ? 'chip-notuseful-on' : 'chip-neutral';
        detail = '<div class="task-detail">' +
            '<div class="timer-row"><span class="timer-big" id="tbig-' + t.id + '">' + esc(t.display_fmt) + '</span>' + timerBtn + '</div>' +
            '<div class="est-row"><span>تخمین: ' + esc(t.estimated_fmt) + '</span>' +
            '<a href="javascript:void(0)" onclick="showDurationModal(\'تنظیم تخمین\',\'set_estimated\',' + t.id + ',' + t.estimated + ')" class="chip chip-edit">ویرایش</a></div>' +
            '<div class="chips">' +
            '<a href="javascript:void(0)" onclick="action(\'set_useful\',{id:' + t.id + ',value:\'true\'})" class="chip ' + uCls + '">✔ مفید</a>' +
            '<a href="javascript:void(0)" onclick="action(\'set_useful\',{id:' + t.id + ',value:\'false\'})" class="chip ' + nuCls + '">✖ نامفید</a>' +
            '<a href="javascript:void(0)" onclick="showModal({title:\'ویرایش عنوان\',cmd:\'edit_title\',params:{id:' + t.id + '},fields:[{label:\'عنوان\',key:\'value\',value:\'' + escJs(t.title) + '\',validate:\'required\'}]})" class="chip chip-edit">✎ عنوان</a>' +
            '<a href="javascript:void(0)" onclick="showDurationModal(\'ویرایش مدت\',\'set_duration\',' + t.id + ',' + t.display_sec + ')" class="chip chip-edit">⏱ مدت</a>' +
            '<a href="javascript:void(0)" onclick="action(\'copy_task\',{id:' + t.id + '})" class="chip chip-edit">📋 فردا</a>' +
            '<a href="javascript:void(0)" onclick="action(\'move_task\',{id:' + t.id + ',dir:\'up\'})" class="chip chip-neutral">↑</a>' +
            '<a href="javascript:void(0)" onclick="action(\'move_task\',{id:' + t.id + ',dir:\'down\'})" class="chip chip-neutral">↓</a>' +
            '<a href="javascript:void(0)" onclick="action(\'delete_task\',{id:' + t.id + '})" class="chip chip-delete">حذف</a>' +
            '</div></div>';
    }
    return '<div class="' + cardCls + '">' + header + detail + '</div>';
}

/* Screens */
function renderHome(h) {
    var calBtn = '<button class="icon-btn" onclick="action(\'toggle_calendar\')">📅</button>';
    var recurBtn = '<button class="icon-btn" style="width:auto;padding:0 8px;gap:3px" onclick="action(\'navigate\',{screen:\'recurring\'})" title="تکراری">★ ' + pd(h.recurring_count) + '</button>';
    var settingsBtn = '<button class="icon-btn" onclick="action(\'navigate\',{screen:\'settings\'})">⚙</button>';

    var html = '<div class="date-header">' +
        '<a href="javascript:void(0)" onclick="action(\'next_day\')" class="date-nav-btn">‹</a>' +
        '<span class="date-title">' + esc(h.date_label) + '</span>' +
        '<div class="header-actions">' +
        (h.is_today ? '' : '<a href="javascript:void(0)" onclick="action(\'today\')" class="today-btn">امروز</a>') +
        calBtn + recurBtn + settingsBtn +
        '<a href="javascript:void(0)" onclick="action(\'prev_day\')" class="date-nav-btn">›</a></div></div>';

    if (h.show_calendar && h.calendar) {
        html += renderCalendar(h.calendar);
    }

    html += '<div class="summary-bar">' +
        '<span class="sum-useful">مفید: ' + esc(h.useful_fmt) + '</span>' +
        '<span class="sum-eff">بازده: ' + pd(h.efficiency) + '٪</span>' +
        '<span class="sum-not">نامفید: ' + esc(h.not_useful_fmt) + '</span></div>';

    html += '<div class="search-row"><input class="search-input" placeholder="جستجو..." value="' + esc(h.search) + '" oninput="debounceSearch(this.value)" /></div>';

    html += '<div class="task-list">';
    if (h.tasks.length === 0) {
        html += '<div class="empty-state"><div class="empty-icon">📝</div><div>هیچ تسکی وجود ندارد</div>' +
            '<button class="empty-btn" onclick="showModal({title:\'افزودن تسک\',cmd:\'add_task\',fields:[{label:\'عنوان\',key:\'title\',validate:\'required\'}]})">+ افزودن تسک</button></div>';
    } else {
        h.tasks.forEach(function(t) { html += taskCard(t); });
    }
    html += '</div>';

    html += renderFinance(h.finance);
    html += renderWellness(h.wellness);
    html += '<div class="section note-section"><div class="sec-title">یادداشت روز من</div>' +
        '<textarea class="note-input" placeholder="یادداشت بنویس..." onchange="action(\'set_note\',{value:this.value})">' + esc(h.daily_note) + '</textarea></div>';
    html += '<a href="javascript:void(0)" onclick="showModal({title:\'افزودن تسک\',cmd:\'add_task\',fields:[{label:\'عنوان\',key:\'title\',validate:\'required\'}]})" class="add-btn">+ افزودن تسک</a>';
    return html;
}

function renderCalendar(cal) {
    var html = '<div class="calendar-panel"><div class="cal-header">' +
        '<button class="cal-nav" onclick="action(\'cal_next_month\')">‹</button>' +
        '<span>' + esc(cal.month_name) + ' ' + pd(cal.year) + '</span>' +
        '<button class="cal-nav" onclick="action(\'cal_prev_month\')">›</button></div><div class="cal-grid">';
    cal.cells.forEach(function(c) {
        var cls = 'cal-day';
        if (c.has_data) cls += ' has-data';
        if (c.eff >= 70) cls += ' eff-high';
        html += '<button class="' + cls + '" onclick="action(\'pick_date\',{date:\'' + c.date + '\'})">' + pd(c.day) + '</button>';
    });
    return html + '</div></div>';
}

function renderFinance(fin) {
    window._finEntries = fin.entries;
    var rows = fin.entries.map(function(e) {
        var info = finTypeInfo(e.type);
        return '<div class="fin-entry">' +
            '<span class="fin-type-' + info.cls + '">' + info.arrow + ' ' + esc(e.title) + ' <span class="fin-cat">' + esc(e.category) + '</span></span>' +
            '<span>' + esc(e.amount_fmt) + '</span>' +
            '<button class="fin-edit" onclick="showEditFinanceById(' + e.id + ')">✎</button>' +
            '<button class="fin-del" onclick="action(\'delete_finance\',{id:' + e.id + '})">×</button></div>';
    }).join('');
    if (!rows) rows = '<div class="empty-mini">هیچ ورودی ندارید</div>';
    var balCls = fin.balance >= 0 ? 'fin-income' : 'fin-expense';
    var invLine = fin.investment > 0 ? '<span class="fin-investment">سرمایه\u200cگذاری: ' + esc(fin.investment_fmt) + '</span>' : '';
    return '<div class="section"><div class="sec-header"><span class="sec-title">امور مالی</span><div class="sec-actions">' +
        '<a href="javascript:void(0)" onclick="showAddFinance(\'income\')" class="btn-sm-green">+ درآمد</a>' +
        '<a href="javascript:void(0)" onclick="showAddFinance(\'expense\')" class="btn-sm-red">+ هزینه</a>' +
        '<a href="javascript:void(0)" onclick="showAddFinance(\'investment\')" class="btn-sm-invest">+ سرمایه</a></div></div>' +
        '<div class="fin-donut-row"><div class="fin-donut" style="--income-pct:' + (fin.income + fin.expense ? fin.income / (fin.income + fin.expense) * 100 : 50) + '"></div>' +
        '<div class="fin-summary"><span class="fin-income">درآمد: ' + esc(fin.income_fmt) + '</span>' +
        '<span class="' + balCls + '">موجودی: ' + esc(fin.balance_fmt) + '</span>' +
        '<span class="fin-expense">هزینه: ' + esc(fin.expense_fmt) + '</span>' +
        invLine + '</div></div>' + rows + '</div>';
}

function showEditFinance(entry) {
    var isInvest = entry.type === 'investment';
    showModal({
        title: 'ویرایش',
        cmd: 'edit_finance',
        params: { id: entry.id },
        fields: [
            { label: 'عنوان', key: 'title', value: entry.title, validate: 'required' },
            { label: 'مبلغ', key: 'amount', value: String(entry.amount), type: 'number', validate: 'amount' },
            { label: isInvest ? 'نوع سرمایه' : 'دسته', key: 'category', type: 'select', value: entry.category, options: isInvest ? window._investCategories : window._categories },
        ],
    });
}

function showEditFinanceById(id) {
    var entry = (window._finEntries || []).find(function(e) { return e.id === id; });
    if (entry) showEditFinance(entry);
}

function showAddFinance(type) {
    var titles = { income: 'افزودن درآمد', expense: 'افزودن هزینه', investment: 'ثبت سرمایه\u200cگذاری' };
    var isInvest = type === 'investment';
    var cats = isInvest ? (window._investCategories || []) : (window._categories || []);
    var defaultCat = isInvest ? (cats[0] || 'سایر') : 'عمومی';
    showModal({
        title: titles[type] || 'ثبت مالی',
        cmd: 'add_finance',
        params: { type: type },
        fields: [
            { label: 'عنوان', key: 'title', validate: 'required', placeholder: isInvest ? 'مثلاً خرید سهام' : '' },
            { label: 'مبلغ (تومان)', key: 'amount', type: 'number', validate: 'amount' },
            { label: isInvest ? 'نوع سرمایه' : 'دسته', key: 'category', type: 'select', value: defaultCat, options: cats },
        ],
    });
}

function showAddCategory() {
    showModal({
        title: 'افزودن دسته',
        cmd: 'add_finance_category',
        fields: [
            { label: 'نام دسته', key: 'name', validate: 'required', placeholder: 'مثلاً سرگرمی' },
        ],
    });
}

function showAddBudget(preselectedCategory, currentAmount) {
    var cats = window._categories || [];
    if (!cats.length) {
        showToast('ابتدا یک دسته اضافه کنید', 'error');
        return;
    }
    var cat = preselectedCategory || cats[0];
    var fields = [
        { label: 'دسته', key: 'category', type: 'select', value: cat, options: cats },
        { label: 'بودجه ماهانه (تومان)', key: 'amount', type: 'number', validate: 'budget', placeholder: '۰' },
    ];
    if (currentAmount !== undefined && currentAmount !== null) {
        fields[1].value = String(currentAmount);
    }
    showModal({
        title: preselectedCategory ? 'ویرایش بودجه' : 'تعیین بودجه',
        cmd: 'set_budget',
        fields: fields,
    });
}

function renderWellness(w) {
    var moods = '';
    window._moodEmojis.forEach(function(emoji, i) {
        var score = i + 1;
        var sel = w.mood === score ? ' sel' : '';
        moods += '<button class="mood-btn' + sel + '" onclick="action(\'set_mood\',{score:' + score + '})">' + emoji + '</button>';
    });
    return '<div class="section"><div class="sec-header"><span class="sec-title">سلامتی من</span></div>' +
        '<div class="well-row">' +
        '<a href="javascript:void(0)" onclick="showClockModal(\'ساعت خواب\',\'set_sleep\',\'' + escJs(w.sleep_raw) + '\',\'sleep\')" class="well-btn"><span class="well-lbl">خواب</span><span class="well-val">' + esc(w.sleep) + '</span></a>' +
        '<a href="javascript:void(0)" onclick="showClockModal(\'ساعت بیداری\',\'set_wake\',\'' + escJs(w.wake_raw) + '\',\'wake\')" class="well-btn"><span class="well-lbl">بیداری</span><span class="well-val">' + esc(w.wake) + '</span></a>' +
        '<div class="well-btn well-static"><span class="well-lbl">مدت خواب</span><span class="well-val">' + esc(w.sleep_dur) + '</span></div></div>' +
        '<div class="mood-row">' + moods + '</div></div>';
}

function renderAnalytics(a) {
    var p7 = a.period === 7 ? 'period-btn active' : 'period-btn';
    var p30 = a.period === 30 ? 'period-btn active' : 'period-btn';
    var s = a.stats;
    var html = '<div class="analytics-header sticky-sub"><span class="analytics-title">آمار کلی</span></div>' +
        '<div class="analytics-period">' +
        '<a href="javascript:void(0)" onclick="action(\'set_period\',{days:7})" class="' + p7 + '">۷ روز</a>' +
        '<a href="javascript:void(0)" onclick="action(\'set_period\',{days:30})" class="' + p30 + '">۳۰ روز</a></div>' +
        '<div class="period-label">' + esc(a.start_label) + ' تا ' + esc(a.end_label) + '</div>' +
        '<div class="streak-badge">🔥 ' + pd(s.streak) + ' روز پشت سر هم</div>' +
        '<div class="chart-box">' + sparklineSvg(a.chart_points, 300, 60) + '</div>' +
        heatmapHtml(a.heatmap) +
        '<div class="stat-cards">' +
        statCard('کل زمان', s.total_fmt) +
        statCard('مفید', s.useful_fmt, '#4DD980') +
        statCard('نامفید', s.not_useful_fmt, '#FF7359') +
        statCard('بازده', pd(s.eff) + '٪', '#5E5CE6') +
        statCard('درآمد', s.income_fmt, '#4DD980') +
        statCard('هزینه', s.expense_fmt, '#FF7359') +
        statCard('موجودی', s.balance_fmt, '#5E5CE6') +
        statCard('خلق و خو', s.avg_mood) +
        statCard('خواب', s.avg_sleep) +
        '</div><div class="sec-title" style="padding:8px 12px">روزهای گذشته</div>';

    if (!a.days.length) {
        html += '<div class="empty-state">در این بازه زمانی داده‌ای ندارید</div>';
    } else {
        a.days.forEach(function(d) {
            html += '<div class="day-card"><div class="day-date">' + esc(d.date_label) + '</div>' +
                '<div class="day-bar"><div class="day-bar-fill" style="width:' + d.eff + '%"></div></div>' +
                '<div class="day-stats"><span>کل: ' + esc(d.total_fmt) + '</span>' +
                '<span style="color:#4DD980">مفید: ' + esc(d.useful_fmt) + '</span>' +
                '<span style="color:#5E5CE6">بازده: ' + pd(d.eff) + '٪</span></div>' +
                (d.sleep || d.mood ? '<div class="day-extra">' + esc(d.sleep) + ' ' + esc(d.mood) + '</div>' : '') +
                '</div>';
        });
    }
    return html;
}

function statCard(key, val, color) {
    return '<div class="stat-card"><div class="stat-key">' + esc(key) + '</div>' +
        '<div class="stat-val" style="color:' + (color || '') + '">' + esc(val) + '</div></div>';
}

function renderSettings(s) {
    var dark = s.theme === 'dark';
    return '<div class="page-header">⚙ تنظیمات</div>' +
        '<div class="section"><div class="setting-row"><span>تم رنگی</span>' +
        '<button class="toggle-btn' + (dark ? ' on' : '') + '" onclick="action(\'set_theme\',{theme:\'' + (dark ? 'light' : 'dark') + '\'})">' +
        (dark ? 'تاریک' : 'روشن') + '</button></div></div>' +
        '<div class="section"><button class="add-btn" onclick="action(\'export_data\')">خروجی داده JSON</button>' +
        '<p class="hint">داده‌ها در کلیپ‌بورد WebView ذخیره شدند</p></div>' +
        '<button class="back-btn" onclick="action(\'navigate\',{screen:\'home\'})">← برگشت</button>';
}

function renderRecurring(list) {
    var rows = list.map(function(r) {
        return '<div class="recur-row"><span>' + esc(r.title) + '</span>' +
            '<button class="chip chip-delete" onclick="action(\'delete_recurring\',{id:' + r.id + '})">حذف</button></div>';
    }).join('');
    if (!rows) rows = '<div class="empty-mini">هیچ وظیفه تکراری ندارید</div>';
    return '<div class="page-header">★ وظایف تکراری</div><div class="section">' + rows + '</div>' +
        '<button class="back-btn" onclick="action(\'navigate\',{screen:\'home\'})">← برگشت</button>';
}

function renderFinanceScreen(f) {
    window._finEntries = f.entries;
    var t = f.totals;
    var balCls = t.balance >= 0 ? 'positive' : 'negative';

    var html = '<div class="fin-page">' +
        '<div class="date-header fin-header">' +
        '<a href="javascript:void(0)" onclick="action(\'finance_next_month\')" class="date-nav-btn">‹</a>' +
        '<span class="date-title">' + esc(f.month_label) + '</span>' +
        '<div class="header-actions">' +
        (f.is_current_month ? '' : '<a href="javascript:void(0)" onclick="action(\'finance_current_month\')" class="today-btn">ماه جاری</a>') +
        '<a href="javascript:void(0)" onclick="action(\'finance_prev_month\')" class="date-nav-btn">›</a></div></div>';

    html += '<div class="fin-hero">' +
        '<div class="fin-hero-label">موجودی این ماه</div>' +
        '<div class="fin-hero-balance ' + balCls + '">' + esc(t.balance_fmt) + '<span class="fin-hero-unit">تومان</span></div>' +
        '<div class="fin-hero-stats">' +
        '<div class="fin-hero-stat income"><span class="fin-stat-icon">↑</span><div><span class="fin-stat-lbl">درآمد</span><span class="fin-stat-val">' + esc(t.income_fmt) + '</span></div></div>' +
        '<div class="fin-hero-stat expense"><span class="fin-stat-icon">↓</span><div><span class="fin-stat-lbl">هزینه</span><span class="fin-stat-val">' + esc(t.expense_fmt) + '</span></div></div>' +
        '</div>' +
        (t.investment > 0 ? '<div class="fin-hero-invest"><span class="fin-stat-icon">◆</span> سرمایه\u200cگذاری: ' + esc(t.investment_fmt) + ' <span class="fin-hero-invest-note">(جزء هزینه نیست)</span></div>' : '') +
        '</div>';

    html += '<div class="fin-actions">' +
        '<button class="fin-action-btn income" onclick="showAddFinance(\'income\')"><span class="fin-action-icon">+</span>درآمد</button>' +
        '<button class="fin-action-btn expense" onclick="showAddFinance(\'expense\')"><span class="fin-action-icon">+</span>هزینه</button>' +
        '<button class="fin-action-btn invest" onclick="showAddFinance(\'investment\')"><span class="fin-action-icon">◆</span>سرمایه</button>' +
        '<button class="fin-action-btn budget" onclick="showAddBudget()"><span class="fin-action-icon">◎</span>بودجه</button>' +
        '</div>';

    html += '<div class="fin-card"><div class="fin-card-head"><span class="fin-card-title">📈 روند ماهانه</span></div>';
    if (f.chart && f.chart.has_data) {
        html += financeLineChartSvg(f.chart, 320, 130);
    } else {
        html += finEmptyState('📊', 'با ثبت اولین تراکنش، نمودار روند مالی نمایش داده می‌شود', '+ ثبت هزینه', 'showAddFinance(\'expense\')');
    }
    html += '</div>';

    html += '<div class="fin-card"><div class="fin-card-head">' +
        '<span class="fin-card-title">🧾 تراکنش‌ها</span>' +
        '<span class="fin-card-badge">' + pd(f.entries.length) + '</span></div>';
    if (!f.entries.length) {
        html += finEmptyState('🧾', 'هنوز تراکنشی ثبت نشده', '+ ثبت درآمد', 'showAddFinance(\'income\')');
    } else {
        var lastDate = '';
        f.entries.slice().reverse().forEach(function(e) {
            if (e.date_label !== lastDate) {
                lastDate = e.date_label;
                html += '<div class="fin-date-chip">' + esc(e.date_label) + '</div>';
            }
            var info = finTypeInfo(e.type);
            var rowCls = 'fin-txn ' + info.cls;
            html += '<div class="' + rowCls + '">' +
                '<div class="fin-txn-icon">' + info.arrow + '</div>' +
                '<div class="fin-txn-body">' +
                '<div class="fin-txn-title">' + esc(e.title) + '</div>' +
                '<div class="fin-txn-meta"><span class="fin-txn-cat">' + finCatIcon(e.category) + ' ' + esc(e.category) + '</span>' +
                (e.type === 'investment' ? ' <span class="fin-txn-tag">سرمایه\u200cگذاری</span>' : '') +
                '</div></div>' +
                '<div class="fin-txn-right">' +
                '<div class="fin-txn-amount">' + esc(e.amount_fmt) + '</div>' +
                '<div class="fin-txn-btns">' +
                '<button class="fin-txn-btn" onclick="showEditFinanceById(' + e.id + ')">✎</button>' +
                '<button class="fin-txn-btn del" onclick="action(\'delete_finance\',{id:' + e.id + '})">×</button>' +
                '</div></div></div>';
        });
    }
    html += '</div>';

    html += '<div class="fin-card"><div class="fin-card-head">' +
        '<span class="fin-card-title">🎯 بودجه دسته‌ها</span>' +
        '<div class="fin-card-actions">' +
        '<button class="fin-chip-btn" onclick="showAddCategory()">+ دسته</button>' +
        '<button class="fin-chip-btn primary" onclick="showAddBudget()">+ بودجه</button>' +
        '</div></div>';
    if (!f.by_category.length) {
        html += finEmptyState('🎯', 'بودجه ماهانه برای دسته‌ها تعیین نشده', '+ تعیین بودجه', 'showAddBudget()');
    } else {
        f.by_category.forEach(function(c) {
            var barCls = c.over_budget ? 'fin-budget-fill over' : 'fin-budget-fill';
            var barWidth = c.budget > 0 ? Math.min(c.used_pct, 100) : 0;
            var pctLbl = c.budget > 0 ? pd(c.used_pct) + '٪' : '—';
            html += '<div class="fin-budget-item' + (c.over_budget ? ' over' : '') + '">' +
                '<div class="fin-budget-top">' +
                '<span class="fin-budget-icon">' + finCatIcon(c.category) + '</span>' +
                '<div class="fin-budget-info">' +
                '<div class="fin-budget-name">' + esc(c.category) + '</div>' +
                '<div class="fin-budget-sub">' + esc(c.expense_fmt) + ' از ' + (c.budget > 0 ? esc(c.budget_fmt) : '—') + '</div>' +
                '</div>' +
                '<span class="fin-budget-pct">' + pctLbl + '</span>' +
                '<button class="fin-txn-btn" onclick="showAddBudget(\'' + escJs(c.category) + '\',' + c.budget + ')">✎</button>' +
                '</div>' +
                (c.budget > 0
                    ? '<div class="fin-budget-track"><div class="' + barCls + '" style="width:' + barWidth + '%"></div></div>'
                    : '<div class="fin-budget-empty">بودجه تعیین نشده — <a href="javascript:void(0)" onclick="showAddBudget(\'' + escJs(c.category) + '\',0)">تنظیم</a></div>') +
                (c.over_budget ? '<div class="fin-budget-warn">⚠ بیش از بودجه</div>' : '') +
                '</div>';
        });
    }
    html += '</div>';

    if (f.daily_series.length) {
        html += '<div class="fin-card"><div class="fin-card-head"><span class="fin-card-title">📅 خلاصه روزانه</span></div>' +
            '<div class="fin-daily-table">' +
            '<div class="fin-daily-head"><span>تاریخ</span><span>درآمد</span><span>هزینه</span><span>سرمایه</span><span>خالص</span></div>';
        f.daily_series.forEach(function(d) {
            var netCls = d.net >= 0 ? 'pos' : 'neg';
            html += '<div class="fin-daily-row">' +
                '<span class="fin-daily-date">' + esc(d.date_label) + '</span>' +
                '<span class="fin-daily-inc">' + esc(d.income_fmt) + '</span>' +
                '<span class="fin-daily-exp">' + esc(d.expense_fmt) + '</span>' +
                '<span class="fin-daily-inv">' + esc(d.investment_fmt) + '</span>' +
                '<span class="fin-daily-net ' + netCls + '">' + esc(d.net_fmt) + '</span></div>';
        });
        html += '</div></div>';
    }

    return html + '</div>';
}

function renderNav(screen) {
    var home = screen === 'home' ? 'nav-btn active' : 'nav-btn';
    var fin = screen === 'finance' ? 'nav-btn active' : 'nav-btn';
    var anal = screen === 'analytics' ? 'nav-btn active' : 'nav-btn';
    return '<a href="javascript:void(0)" onclick="action(\'navigate\',{screen:\'home\'})" class="' + home + '"><span class="nav-icon">🏠</span>امروز</a>' +
        '<a href="javascript:void(0)" onclick="action(\'navigate\',{screen:\'finance\'})" class="' + fin + '"><span class="nav-icon">💰</span>مالی</a>' +
        '<a href="javascript:void(0)" onclick="action(\'navigate\',{screen:\'analytics\'})" class="' + anal + '"><span class="nav-icon">📊</span>آمار</a>';
}

/* Main render */
function renderApp(state) {
    window._categories = state.finance_categories || [];
    window._investCategories = state.investment_categories || [];
    window._moodEmojis = state.mood_emojis || [];
    document.documentElement.setAttribute('data-theme', state.theme || 'dark');

    var root = document.getElementById('app-root');
    if (!root) return;

    var html = '';
    if (state.screen === 'home' && state.home) html = renderHome(state.home);
    else if (state.screen === 'finance' && state.finance_screen) html = renderFinanceScreen(state.finance_screen);
    else if (state.screen === 'analytics' && state.analytics) html = renderAnalytics(state.analytics);
    else if (state.screen === 'settings' && state.settings) html = renderSettings(state.settings);
    else if (state.screen === 'recurring' && state.recurring) html = renderRecurring(state.recurring);

    root.innerHTML = html;

    var nav = document.getElementById('bottom-nav');
    if (nav && (state.screen === 'home' || state.screen === 'finance' || state.screen === 'analytics')) {
        nav.innerHTML = renderNav(state.screen);
        nav.style.display = 'flex';
    } else if (nav) {
        nav.style.display = 'none';
    }

    if (state.toast) showToast(state.toast.message, state.toast.type);
}
