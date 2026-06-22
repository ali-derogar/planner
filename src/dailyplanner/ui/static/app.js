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

var _noteTimer = null;
var _noteSavedTimer = null;
function debounceNote(val) {
    clearTimeout(_noteTimer);
    _noteTimer = setTimeout(function() {
        action('set_note', { value: val });
        showNoteSaved();
    }, 600);
}

function showNoteSaved() {
    var el = document.getElementById('note-saved');
    if (!el) return;
    el.classList.add('show');
    clearTimeout(_noteSavedTimer);
    _noteSavedTimer = setTimeout(function() { el.classList.remove('show'); }, 1800);
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

/* SVG icons */
var ICON = {
    home: '<svg viewBox="0 0 24 24"><path d="M4 10.5 12 4l8 6.5V19a1 1 0 0 1-1 1h-5v-6H10v6H5a1 1 0 0 1-1-1v-8.5z"/></svg>',
    wallet: '<svg viewBox="0 0 24 24"><path d="M3 7h18a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V8a1 1 0 0 1 1-1z"/><path d="M17 12.5h4"/><path d="M3 10h18"/></svg>',
    folder: '<svg viewBox="0 0 24 24"><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7z"/></svg>',
    chart: '<svg viewBox="0 0 24 24"><path d="M5 20V11"/><path d="M12 20V4"/><path d="M19 20v-7"/></svg>',
    calendar: '<svg viewBox="0 0 24 24"><path d="M7 3v2"/><path d="M17 3v2"/><path d="M4 8h16"/><path d="M5 5h14a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1z"/></svg>',
    settings: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m4.93 19.07 1.41-1.41"/><path d="m17.66 6.34 1.41-1.41"/></svg>',
    bell: '<svg viewBox="0 0 24 24"><path d="M8 17h8"/><path d="M12 3a5 5 0 0 1 5 5v3l1 2H6l1-2V8a5 5 0 0 1 5-5z"/><path d="M10 17a2 2 0 0 0 4 0"/></svg>',
    star: '<svg viewBox="0 0 24 24"><polygon points="12 2 15 9 22 9.5 17 14.5 18.5 22 12 18.5 5.5 22 7 14.5 2 9.5 9 9"/></svg>',
    starOutline: '<svg viewBox="0 0 24 24"><polygon fill="none" points="12 2 15 9 22 9.5 17 14.5 18.5 22 12 18.5 5.5 22 7 14.5 2 9.5 9 9"/></svg>',
    search: '<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="6"/><path d="m20 20-3.5-3.5"/></svg>',
    chevDown: '<svg viewBox="0 0 24 24"><path d="m6 9 6 6 6-6"/></svg>',
    chevUp: '<svg viewBox="0 0 24 24"><path d="m18 15-6-6-6 6"/></svg>',
    chevLeft: '<svg viewBox="0 0 24 24"><path d="m15 18-6-6 6-6"/></svg>',
    chevRight: '<svg viewBox="0 0 24 24"><path d="m9 18 6-6-6-6"/></svg>',
    play: '<svg viewBox="0 0 24 24"><polygon points="8 5 19 12 8 19"/></svg>',
    stop: '<svg viewBox="0 0 24 24"><rect x="7" y="7" width="10" height="10" rx="1.5"/></svg>',
    plus: '<svg viewBox="0 0 24 24"><path d="M12 5v14"/><path d="M5 12h14"/></svg>',
    list: '<svg viewBox="0 0 24 24"><path d="M9 6h12"/><path d="M9 12h12"/><path d="M9 18h12"/><circle cx="4" cy="6" r="1"/><circle cx="4" cy="12" r="1"/><circle cx="4" cy="18" r="1"/></svg>',
    check: '<svg viewBox="0 0 24 24"><path d="M5 12l4 4L19 6"/></svg>',
};

function ico(name, cls) {
    cls = cls || 'ico';
    var fillCls = (name === 'star' || name === 'play') ? ' ico-fill' : '';
    return '<span class="' + cls + fillCls + '" aria-hidden="true">' + (ICON[name] || '') + '</span>';
}

function emptyListIcon() {
    return '<div class="empty-icon">' + ico('list', 'ico') + '</div>';
}

/** RTL nav: prev (earlier) on the right, next (later) on the left. */
function navArrowBtn(kind, onclick, label, btnClass) {
    var icon = kind === 'prev' ? 'chevRight' : 'chevLeft';
    var cls = btnClass || 'date-nav-btn';
    return '<button type="button" class="' + cls + '" aria-label="' + esc(label) + '" onclick="' + onclick + '">' +
        ico(icon, 'ico') + '</button>';
}

function calNavBtn(kind, extraCls) {
    var icon = kind === 'prev' ? 'chevRight' : 'chevLeft';
    var label = kind === 'prev' ? 'ماه قبل' : 'ماه بعد';
    var cls = 'cal-nav date-cal-' + kind + (extraCls ? ' ' + extraCls : '');
    return '<button type="button" class="' + cls + '" aria-label="' + label + '">' + ico(icon, 'ico') + '</button>';
}

function backBtn(screen, label) {
    label = label || 'برگشت';
    return '<button type="button" class="back-btn" onclick="action(\'navigate\',{screen:\'' + screen + '\'})">' +
        ico('chevRight', 'ico') + '<span>' + label + '</span></button>';
}

function collapseChevron(open) {
    return ico(open ? 'chevUp' : 'chevDown', 'ico collapse-chevron');
}

function themeColorForScreen(screen, theme) {
    if (theme === 'light') return '#FAFAFC';
    var map = { home: '#4338CA', finance: '#0F2E28', projects: '#6366F1', analytics: '#1A1A24' };
    return map[screen] || '#0A0A0F';
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

var JALALI_MONTH_NAMES = [
    '', 'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
    'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند',
];
var JALALI_WEEKDAYS = ['ش', 'ی', 'د', 'س', 'چ', 'پ', 'ج'];

function isJalaaliLeap(jy) {
    var r = jy % 33;
    return [1, 5, 9, 13, 17, 22, 26, 30].indexOf(r) !== -1;
}

function jalaaliMonthLength(jy, jm) {
    if (jm <= 6) return 31;
    if (jm <= 11) return 30;
    return isJalaaliLeap(jy) ? 30 : 29;
}

function toJalaali(gy, gm, gd) {
    var g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
    var gy2 = gm > 2 ? gy + 1 : gy;
    var days = 355666 + (365 * gy) + Math.floor((gy2 + 3) / 4) - Math.floor((gy2 + 99) / 100) +
        Math.floor((gy2 + 399) / 400) + gd + g_d_m[gm - 1];
    var jy = -1595 + (33 * Math.floor(days / 12053));
    days %= 12053;
    jy += 4 * Math.floor(days / 1461);
    days %= 1461;
    if (days > 365) {
        jy += Math.floor((days - 1) / 365);
        days = (days - 1) % 365;
    }
    var jm, jd;
    if (days < 186) {
        jm = 1 + Math.floor(days / 31);
        jd = 1 + (days % 31);
    } else {
        jm = 7 + Math.floor((days - 186) / 30);
        jd = 1 + ((days - 186) % 30);
    }
    return { jy: jy, jm: jm, jd: jd };
}

function toGregorian(jy, jm, jd) {
    var jy2 = jy + 1595;
    var days = -355668 + (365 * jy2) + Math.floor(jy2 / 33) * 8 + Math.floor(((jy2 % 33) + 3) / 4) +
        jd + (jm < 7 ? (jm - 1) * 31 : ((jm - 7) * 30) + 186);
    var gy = 400 * Math.floor(days / 146097);
    days %= 146097;
    if (days > 36524) {
        gy += 100 * Math.floor(--days / 36524);
        days %= 36524;
        if (days >= 365) days++;
    }
    gy += 4 * Math.floor(days / 1461);
    days %= 1461;
    if (days > 365) {
        gy += Math.floor((days - 1) / 365);
        days = (days - 1) % 365;
    }
    var gd = days + 1;
    var sal_a = [0, 31, ((gy % 4 === 0 && gy % 100 !== 0) || (gy % 400 === 0)) ? 29 : 28,
        31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    var gm = 0;
    for (gm = 0; gm < 13 && gd > sal_a[gm]; gm++) gd -= sal_a[gm];
    return { gy: gy, gm: gm, gd: gd };
}

function parseIsoDate(s) {
    if (!s) return null;
    var p = String(s).trim().split('-');
    if (p.length !== 3) return null;
    var y = parseInt(p[0], 10), m = parseInt(p[1], 10), d = parseInt(p[2], 10);
    if (isNaN(y) || isNaN(m) || isNaN(d)) return null;
    return { y: y, m: m, d: d };
}

function isoFromGregorian(gy, gm, gd) {
    return gy + '-' + pad2(gm) + '-' + pad2(gd);
}

function persianWeekday(gy, gm, gd) {
    var dt = new Date(gy, gm - 1, gd);
    return (dt.getDay() + 1) % 7;
}

function formatJalaliIso(iso) {
    if (!iso) return 'بدون ددلاین';
    var p = parseIsoDate(iso);
    if (!p) return iso;
    var j = toJalaali(p.y, p.m, p.d);
    return pd(j.jd) + ' ' + JALALI_MONTH_NAMES[j.jm] + ' ' + pd(j.jy);
}

function buildDatePickerEl(field) {
    var wrap = document.createElement('div');
    wrap.className = 'date-picker';
    wrap.id = 'mf-' + field.key;

    var hidden = document.createElement('input');
    hidden.type = 'hidden';
    hidden.id = 'mf-' + field.key + '-val';
    hidden.value = field.value || '';
    wrap.appendChild(hidden);

    var now = new Date();
    var initGreg = { y: now.getFullYear(), m: now.getMonth() + 1, d: now.getDate() };
    if (field.value) {
        var parsed = parseIsoDate(field.value);
        if (parsed) initGreg = parsed;
    }
    var initJ = toJalaali(initGreg.y, initGreg.m, initGreg.d);
    var state = { jy: initJ.jy, jm: initJ.jm };

    var labelEl = document.createElement('div');
    labelEl.className = 'date-picker-label';
    wrap.appendChild(labelEl);

    var calPanel = document.createElement('div');
    calPanel.className = 'calendar-panel date-picker-cal';
    wrap.appendChild(calPanel);

    var clearBtn = document.createElement('button');
    clearBtn.type = 'button';
    clearBtn.className = 'date-picker-clear';
    clearBtn.textContent = field.clearLabel || 'بدون ددلاین';
    clearBtn.onclick = function() {
        hidden.value = '';
        refresh();
    };
    if (field.clearable !== false) {
        wrap.appendChild(clearBtn);
    }

    var emptyLabel = field.emptyLabel || (field.clearable === false ? 'تاریخ را انتخاب کنید' : 'بدون ددلاین');

    function renderMonth() {
        var jy = state.jy;
        var jm = state.jm;
        var daysInMonth = jalaaliMonthLength(jy, jm);
        var g1 = toGregorian(jy, jm, 1);
        var wd = persianWeekday(g1.gy, g1.gm, g1.gd);
        var selectedIso = hidden.value;
        var todayIso = isoFromGregorian(now.getFullYear(), now.getMonth() + 1, now.getDate());

        var html = '<div class="cal-header">' +
            calNavBtn('prev') +
            '<span class="cal-title">' + esc(JALALI_MONTH_NAMES[jm]) + ' ' + pd(jy) + '</span>' +
            calNavBtn('next') +
            '</div>' +
            '<div class="cal-weekdays">' +
            JALALI_WEEKDAYS.map(function(w) { return '<span>' + w + '</span>'; }).join('') +
            '</div><div class="cal-grid">';

        for (var i = 0; i < wd; i++) html += '<span class="cal-day cal-day-empty"></span>';
        for (var day = 1; day <= daysInMonth; day++) {
            var g = toGregorian(jy, jm, day);
            var iso = isoFromGregorian(g.gy, g.gm, g.gd);
            var cls = 'cal-day';
            if (iso === selectedIso) cls += ' selected';
            if (iso === todayIso) cls += ' today';
            html += '<button type="button" class="' + cls + '" data-iso="' + iso + '">' + pd(day) + '</button>';
        }
        html += '</div>';
        calPanel.innerHTML = html;

        calPanel.querySelector('.date-cal-next').onclick = function() {
            if (state.jm === 12) { state.jm = 1; state.jy++; } else state.jm++;
            renderMonth();
        };
        calPanel.querySelector('.date-cal-prev').onclick = function() {
            if (state.jm === 1) { state.jm = 12; state.jy--; } else state.jm--;
            renderMonth();
        };
        calPanel.querySelectorAll('.cal-day[data-iso]').forEach(function(btn) {
            btn.onclick = function() {
                hidden.value = btn.getAttribute('data-iso');
                refresh();
            };
        });
    }

    function refresh() {
        labelEl.textContent = hidden.value ? formatJalaliIso(hidden.value) : emptyLabel;
        renderMonth();
    }

    refresh();
    return wrap;
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

var DEFAULT_PROJECT_COLORS = [
    '#5E5CE6', '#4DD980', '#FF7359', '#FFB340',
    '#5AC8FA', '#FF6B9D', '#A8E063', '#8E8E93',
];
var PROJECT_COLOR_LABELS = {
    '#5E5CE6': 'بنفش',
    '#4DD980': 'سبز',
    '#FF7359': 'قرمز',
    '#FFB340': 'نارنجی',
    '#5AC8FA': 'آبی',
    '#FF6B9D': 'صورتی',
    '#A8E063': 'سبز روشن',
    '#8E8E93': 'خاکستری',
};

function normColor(c) {
    return String(c || '').trim().toUpperCase();
}

function buildColorPickerEl(field) {
    var colors = field.options && field.options.length ? field.options : DEFAULT_PROJECT_COLORS;
    var selected = field.value || colors[0];
    var selectedNorm = normColor(selected);
    var wrap = document.createElement('div');
    wrap.className = 'color-picker';
    wrap.id = 'mf-' + field.key;

    var hidden = document.createElement('input');
    hidden.type = 'hidden';
    hidden.id = 'mf-' + field.key + '-val';
    hidden.value = selected;
    wrap.appendChild(hidden);

    var grid = document.createElement('div');
    grid.className = 'color-picker-grid';
    colors.forEach(function(c) {
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'color-swatch' + (normColor(c) === selectedNorm ? ' selected' : '');
        btn.style.backgroundColor = c;
        btn.title = PROJECT_COLOR_LABELS[c] || c;
        btn.setAttribute('aria-label', PROJECT_COLOR_LABELS[c] || c);
        btn.onclick = function() {
            hidden.value = c;
            grid.querySelectorAll('.color-swatch').forEach(function(s) { s.classList.remove('selected'); });
            btn.classList.add('selected');
            var lbl = wrap.querySelector('.color-picker-label');
            if (lbl) lbl.textContent = PROJECT_COLOR_LABELS[c] || c;
        };
        grid.appendChild(btn);
    });
    wrap.appendChild(grid);

    var labelEl = document.createElement('div');
    labelEl.className = 'color-picker-label';
    labelEl.textContent = PROJECT_COLOR_LABELS[selected] || PROJECT_COLOR_LABELS[colors.find(function(c) { return normColor(c) === selectedNorm; })] || selected;
    wrap.appendChild(labelEl);

    return wrap;
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
        if (f.type === 'color-select') {
            fc.appendChild(buildColorPickerEl(f));
        } else if (f.type === 'jalali-date') {
            fc.appendChild(buildDatePickerEl(f));
        } else if (f.type === 'select') {
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
    var modalEl = document.getElementById('modal');
    modalEl.style.display = 'flex';
    modalEl.classList.remove('modal-center');
    fc.scrollTop = 0;
    var first = fc.querySelector('input,select,textarea,button.color-swatch');
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
        } else if (f.type === 'color-select') {
            var hiddenColor = document.getElementById('mf-' + f.key + '-val');
            val = hiddenColor ? hiddenColor.value : '';
        } else if (f.type === 'jalali-date') {
            var hiddenDate = document.getElementById('mf-' + f.key + '-val');
            val = hiddenDate ? hiddenDate.value : '';
        } else {
            val = el ? el.value : '';
        }
        params[f.key] = val;
        if (f.validate && _modalValidators[f.validate]) {
            if (!_modalValidators[f.validate](val)) valid = false;
        }
    });
    if (!valid) {
        errEl.textContent = 'لطفاً فیلدهای مشخص‌شده را به‌درستی پر کنید';
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

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        var modal = document.getElementById('modal');
        if (modal && modal.style.display !== 'none') closeModal();
    }
});

(function initModalBox() {
    function bind() {
        var box = document.getElementById('modal-box');
        if (box && !box.dataset.bound) {
            box.dataset.bound = '1';
            box.addEventListener('click', function(e) { e.stopPropagation(); });
        }
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', bind);
    } else {
        bind();
    }
})();

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
        '<polyline fill="none" stroke="currentColor" stroke-width="2" points="' + pts + '"/>' +
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

    var starIcon = t.is_starred ? ico('star', 'task-star') : ico('starOutline', 'task-star empty');
    var durCls = t.is_running ? 'task-dur running' : 'task-dur';
    var chev = t.is_expanded ? ico('chevUp', 'ico task-chevron') : ico('chevDown', 'ico task-chevron');

    var progress = '';
    if (t.estimated > 0) {
        progress = '<div class="task-progress"><div class="task-progress-fill" style="width:' + t.progress + '%"></div></div>';
        if (t.remaining_fmt) {
            progress += '<div class="task-remaining">مانده: ' + esc(t.remaining_fmt) + '</div>';
        }
    }

    var header = '<div class="task-header" role="button" tabindex="0" onclick="action(\'toggle_task\',{id:' + t.id + '})">' +
        '<button type="button" class="task-star-wrap" aria-label="' + (t.is_starred ? 'حذف ستاره' : 'ستاره‌دار کردن') + '" onclick="event.stopPropagation();action(\'toggle_star\',{id:' + t.id + '})">' + starIcon + '</button>' +
        '<span class="task-title-wrap" title="' + esc(t.title) + '">' + esc(t.title) + '</span>' +
        '<span class="task-header-end">' +
        '<span class="' + durCls + '" id="tdur-' + t.id + '">' + esc(t.display_fmt) + '</span>' +
        chev + '</span></div>' + progress;

    var detail = '';
    if (t.is_expanded) {
        var timerBtn = t.is_running
            ? '<button class="btn-stop" onclick="action(\'stop_timer\',{id:' + t.id + '})">' + ico('stop', 'ico') + ' توقف</button>'
            : '<button class="btn-start" onclick="action(\'start_timer\',{id:' + t.id + '})">' + ico('play', 'ico') + ' شروع</button>';
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
    var taskCount = h.tasks ? h.tasks.length : 0;
    var calBtn = '<button type="button" class="icon-btn" aria-label="تقویم" onclick="action(\'toggle_calendar\')">' + ico('calendar', 'ico') + '</button>';
    var recurBtn = '<button type="button" class="icon-btn wide" onclick="action(\'navigate\',{screen:\'recurring\'})" aria-label="وظایف تکراری">' +
        ico('star', 'ico') + ' ' + pd(h.recurring_count) + '</button>';
    var settingsBtn = '<button type="button" class="icon-btn" aria-label="تنظیمات" onclick="action(\'navigate\',{screen:\'settings\'})">' + ico('settings', 'ico') + '</button>';
    var urgentCount = h.urgent_dates_count || 0;
    var badge = urgentCount > 0
        ? ' <span class="urgent-badge">' + pd(urgentCount) + '</span>'
        : '';
    var datesBtn = '<button type="button" class="icon-btn dates-btn"'
        + ' onclick="action(\'navigate\',{screen:\'important_dates\'})"'
        + ' aria-label="تاریخ\u200cهای مهم">' + ico('bell', 'ico') + badge + '</button>';

    var html = '<div class="date-header">' +
        '<div class="date-header-row">' +
        navArrowBtn('prev', 'action(\'prev_day\')', 'روز قبل') +
        '<span class="date-title">' + esc(h.date_label) + '</span>' +
        navArrowBtn('next', 'action(\'next_day\')', 'روز بعد') +
        '</div>' +
        '<div class="date-header-tools">' +
        (h.is_today ? '' : '<button type="button" onclick="action(\'today\')" class="today-btn">امروز</button>') +
        calBtn + recurBtn + datesBtn + settingsBtn +
        '</div>' +
        '<div class="hero-stats">' +
        '<div class="hero-stat eff"><span class="hero-stat-val">' + pd(h.efficiency) + '٪</span><span class="hero-stat-lbl">بازده</span></div>' +
        '<div class="hero-stat useful"><span class="hero-stat-val">' + esc(h.useful_fmt) + '</span><span class="hero-stat-lbl">مفید</span></div>' +
        '<div class="hero-stat not"><span class="hero-stat-val">' + esc(h.not_useful_fmt) + '</span><span class="hero-stat-lbl">نامفید</span></div>' +
        '<div class="hero-stat"><span class="hero-stat-val">' + pd(taskCount) + '</span><span class="hero-stat-lbl">تسک</span></div>' +
        '</div></div>';

    if (h.show_calendar && h.calendar) {
        html += renderCalendar(h.calendar);
    }

    html += '<div class="search-row"><div class="search-wrap">' + ico('search', 'ico-search') +
        '<input class="search-input" placeholder="جستجو در تسک\u200cها..." value="' + esc(h.search) + '" oninput="debounceSearch(this.value)" aria-label="جستجو در تسک\u200cها" /></div></div>';

    html += '<div class="task-list">';
    if (h.tasks.length === 0) {
        html += '<div class="empty-state">' + emptyListIcon() + '<div class="empty-title">هیچ تسکی وجود ندارد</div>' +
            '<div class="empty-sub">اولین تسک امروز را اضافه کنید و زمان خود را مدیریت کنید</div>' +
            '<button type="button" class="empty-btn" onclick="showModal({title:\'افزودن تسک\',cmd:\'add_task\',fields:[{label:\'عنوان\',key:\'title\',validate:\'required\'}]})">' + ico('plus', 'ico') + ' افزودن تسک</button></div>';
    } else {
        h.tasks.forEach(function(t) { html += taskCard(t); });
    }
    html += '</div>';

    html += renderFinance(h.finance);
    html += renderWellness(h.wellness);
    html += '<div class="section note-section"><div class="sec-title">یادداشت روز من</div>' +
        '<textarea class="note-input" id="daily-note" placeholder="افکار، اهداف یا یادآوری‌های امروز..." oninput="debounceNote(this.value)" aria-label="یادداشت روز">' + esc(h.daily_note) + '</textarea>' +
        '<div class="note-saved" id="note-saved" aria-live="polite">ذخیره شد ✓</div></div>';
    if (h.tasks.length > 0) {
        html += '<button type="button" onclick="showModal({title:\'افزودن تسک\',cmd:\'add_task\',fields:[{label:\'عنوان\',key:\'title\',validate:\'required\'}]})" class="add-btn">' + ico('plus', 'ico') + ' افزودن تسک</button>';
    }
    return html;
}

function renderCalendar(cal) {
    var html = '<div class="calendar-panel"><div class="cal-header">' +
        navArrowBtn('prev', 'action(\'cal_prev_month\')', 'ماه قبل', 'cal-nav') +
        '<span class="cal-title">' + esc(cal.month_name) + ' ' + pd(cal.year) + '</span>' +
        navArrowBtn('next', 'action(\'cal_next_month\')', 'ماه بعد', 'cal-nav') +
        '</div><div class="cal-grid">';
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
    var moodLabels = ['خیلی بد', 'بد', 'نه چندان خوب', 'معمولی', 'نسبتاً خوب', 'خوب', 'خیلی خوب', 'عالی', 'فوق‌العاده', 'عاشقانه'];
    var moods = '';
    window._moodEmojis.forEach(function(emoji, i) {
        var score = i + 1;
        var sel = w.mood === score ? ' sel' : '';
        var lbl = moodLabels[i] || ('امتیاز ' + pd(score));
        moods += '<button type="button" class="mood-btn' + sel + '" onclick="action(\'set_mood\',{score:' + score + '})" aria-label="' + lbl + '" aria-pressed="' + (w.mood === score ? 'true' : 'false') + '">' + emoji + '</button>';
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
        html += '<div class="empty-state"><div class="empty-icon">📊</div><div class="empty-title">داده‌ای برای نمایش نیست</div>' +
            '<div class="empty-sub">چند روز تسک انجام دهید تا آمار بازدهی اینجا نمایش داده شود</div></div>';
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
    var fileName = 'dailyplanner_backup.json';
    if (s.export_path) {
        var parts = s.export_path.replace(/\\/g, '/').split('/');
        fileName = parts[parts.length - 1] || fileName;
    }
    var hasExport = !!window._exportData;
    var importDraft = window._importDraft || '';

    var html = '<div class="settings-page">';
    html += '<div class="page-header">⚙ تنظیمات</div>';

    html += '<div class="section settings-section">'
          + '<div class="sec-title">ظاهر</div>'
          + '<div class="setting-row">'
          + '<div class="setting-label">'
          + '<span class="setting-name">تم رنگی</span>'
          + '<span class="setting-desc">' + (dark ? 'پس‌زمینه تیره' : 'پس‌زمینه روشن') + '</span>'
          + '</div>'
          + '<button class="toggle-btn' + (dark ? ' on' : '') + '"'
          + ' onclick="action(\'set_theme\',{theme:\'' + (dark ? 'light' : 'dark') + '\'})">'
          + (dark ? 'تاریک' : 'روشن') + '</button>'
          + '</div></div>';

    html += '<div class="section settings-section backup-section">'
          + '<div class="sec-title">پشتیبان‌گیری</div>'
          + '<p class="section-desc">تمام داده‌های شما در یک فایل JSON ذخیره می‌شود. '
          + 'می‌توانید آن را کپی کنید یا از فایل ذخیره‌شده در حافظه داخلی اپ استفاده کنید.</p>'
          + '<button type="button" class="section-btn section-btn-primary"'
          + ' onclick="action(\'export_data\')">'
          + '<span class="section-btn-icon">💾</span>ذخیره بکاپ</button>'
          + '<div class="backup-meta"><span class="backup-file-badge">' + esc(fileName) + '</span></div>'
          + '<button type="button" class="backup-toggle" id="export-toggle"'
          + (hasExport ? '' : ' style="display:none"')
          + ' onclick="toggleExportPreview()">نمایش محتوای JSON</button>'
          + '<textarea id="export-ta" class="backup-ta backup-preview" style="display:none"'
          + ' placeholder="JSON بکاپ اینجا نمایش داده می‌شود..." readonly></textarea>'
          + '<button type="button" class="backup-copy-btn" id="export-copy-btn" style="display:none"'
          + ' onclick="copyExportJson()">📋 کپی در کلیپ‌بورد</button>'
          + '</div>';

    html += '<div class="section settings-section import-section">'
          + '<div class="sec-title">بازگردانی</div>'
          + '<div class="import-warning">'
          + '<span class="import-warning-icon">⚠</span>'
          + '<span>این عملیات همه داده‌های فعلی را پاک و با محتوای بکاپ جایگزین می‌کند. '
          + 'قبل از ادامه حتماً بکاپ بگیرید.</span>'
          + '</div>'
          + '<p class="section-desc">محتوای فایل JSON بکاپ را در کادر زیر قرار دهید.</p>'
          + '<textarea id="import-ta" class="backup-ta"'
          + ' placeholder="JSON بکاپ را اینجا paste کنید..."'
          + ' oninput="window._importDraft=this.value">' + esc(importDraft) + '</textarea>'
          + '<button type="button" class="section-btn section-btn-danger"'
          + ' onclick="submitImport()">'
          + '<span class="section-btn-icon">📥</span>بازگردانی داده‌ها</button>'
          + '</div>';

    html += backBtn('home');
    html += '</div>';
    return html;
}

function toggleExportPreview() {
    var ta = document.getElementById('export-ta');
    var btn = document.getElementById('export-toggle');
    var copyBtn = document.getElementById('export-copy-btn');
    if (!ta) return;
    var show = ta.style.display === 'none';
    ta.style.display = show ? 'block' : 'none';
    if (btn) btn.textContent = show ? 'پنهان کردن JSON' : 'نمایش محتوای JSON';
    if (copyBtn) copyBtn.style.display = show ? 'block' : 'none';
}

function copyExportJson() {
    var ta = document.getElementById('export-ta');
    var text = (ta && ta.value) ? ta.value : (window._exportData || '');
    if (!text) {
        showToast('محتوایی برای کپی وجود ندارد', 'error');
        return;
    }

    function copied() {
        showToast('در کلیپ‌بورد کپی شد', 'success');
    }

    function fallbackCopy() {
        if (ta) {
            ta.style.display = 'block';
            ta.focus();
            ta.select();
            ta.setSelectionRange(0, text.length);
            try {
                if (document.execCommand('copy')) {
                    copied();
                    return;
                }
            } catch (e) {}
        }
        showToast('کپی نشد — متن را دستی انتخاب کنید', 'error');
    }

    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(copied).catch(fallbackCopy);
    } else {
        fallbackCopy();
    }
}

function submitImport() {
    var ta = document.getElementById('import-ta');
    if (!ta || !ta.value.trim()) {
        showToast('داده‌ای وارد نشده', 'error');
        return;
    }
    window._importDraft = ta.value.trim();
    action('import_data', { json: ta.value.trim() });
}

function renderRecurring(list) {
    var rows = list.map(function(r) {
        return '<div class="recur-row"><span>' + esc(r.title) + '</span>' +
            '<button class="chip chip-delete" onclick="action(\'delete_recurring\',{id:' + r.id + '})">حذف</button></div>';
    }).join('');
    if (!rows) rows = '<div class="empty-mini">هیچ وظیفه تکراری ندارید</div>';
    return '<div class="page-header">★ وظایف تکراری</div><div class="section">' + rows + '</div>' +
        backBtn('home');
}

function renderInstallmentCard(inst) {
    inst = inst || { count: 0, items: [], total_unpaid_fmt: pd(0) };
    var rows;
    if (inst.count === 0) {
        rows = '<div class="empty-mini">هنوز قسطی ثبت نشده — '
            + '<a href="javascript:void(0)" onclick="action(\'navigate\',{screen:\'installments\'})">'
            + '+ افزودن قسط</a></div>';
    } else {
        rows = inst.items.map(function(i) {
            var statusBtn = i.is_settled
                ? '<span class="inst-settled">✓ تسویه</span>'
                : i.paid_this_month
                    ? '<span class="inst-paid-month">✓ این ماه پرداخت شد</span>'
                    : '<button class="btn-sm-green" onclick="action(\'pay_installment\',{id:'
                      + i.id + '})">پرداخت کردم</button>';
            return '<div class="inst-row">'
                + '<span class="inst-title">' + esc(i.title) + '</span>'
                + '<span class="inst-amount">' + esc(i.amount_fmt) + '</span>'
                + statusBtn + '</div>';
        }).join('');
    }
    return '<div class="section fin-inst-card">'
        + '<div class="sec-header">'
        + '<span class="sec-title">اقساط این ماه</span>'
        + '<a href="javascript:void(0)"'
        + ' onclick="action(\'navigate\',{screen:\'installments\'})"'
        + ' class="chip chip-edit">مدیریت</a></div>'
        + rows
        + (inst.count > 0
            ? '<div class="inst-footer">جمع پرداخت نشده: ' + esc(inst.total_unpaid_fmt) + '</div>'
            : '')
        + '</div>';
}

function renderFinanceScreen(f) {
    window._finEntries = f.entries;
    var t = f.totals;
    var balCls = t.balance >= 0 ? 'positive' : 'negative';

    var html = '<div class="fin-page">' +
        '<div class="date-header fin-header">' +
        '<div class="date-header-row">' +
        navArrowBtn('prev', 'action(\'finance_prev_month\')', 'ماه قبل') +
        '<span class="date-title">' + esc(f.month_label) + '</span>' +
        navArrowBtn('next', 'action(\'finance_next_month\')', 'ماه بعد') +
        '</div>' +
        (f.is_current_month ? '' : '<div class="date-header-tools">' +
        '<button type="button" onclick="action(\'finance_current_month\')" class="today-btn">ماه جاری</button></div>') +
        '</div>';

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
        '<button class="fin-action-btn inst" onclick="action(\'navigate\',{screen:\'installments\'})"><span class="fin-action-icon">📋</span>اقساط</button>' +
        '</div>';

    html += renderInstallmentCard(f.installments);

    html += '<div class="fin-card"><div class="fin-card-head"><span class="fin-card-title">📈 روند ماهانه</span></div>';
    if (f.chart && f.chart.has_data) {
        html += financeLineChartSvg(f.chart, 320, 130);
    } else {
        html += finEmptyState('📊', 'با ثبت اولین تراکنش، نمودار روند مالی نمایش داده می‌شود', '+ ثبت هزینه', 'showAddFinance(\'expense\')');
    }
    html += '</div>';

    html += '<div class="fin-card fin-card-collapsible' + (_showFinanceTransactions ? ' open' : '') + '">'
        + '<button type="button" class="fin-card-head fin-card-toggle"'
        + ' onclick="_showFinanceTransactions=!_showFinanceTransactions;renderApp(window._lastState)">'
        + '<span class="fin-card-title">🧾 تراکنش‌ها</span>'
        + '<span class="fin-card-head-end">'
        + '<span class="fin-card-badge">' + pd(f.entries.length) + '</span>'
        + '<span class="fin-card-chevron">' + collapseChevron(_showFinanceTransactions) + '</span>'
        + '</span></button>';
    if (_showFinanceTransactions) {
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
                '<div class="fin-txn-btns">' +
                '<button class="fin-txn-btn" onclick="showAddBudget(\'' + escJs(c.category) + '\',' + c.budget + ')">✎</button>' +
                (c.budget > 0
                    ? '<button class="fin-txn-btn del" onclick="action(\'delete_budget\',{category:\'' + escJs(c.category) + '\'})">×</button>'
                    : '') +
                '</div></div>' +
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

function renderInstallments(data) {
    var html = '<div class="page-header">📋 مدیریت اقساط</div>';

    html += '<div class="section">'
        + '<div class="sec-title">این ماه — ' + esc(data.month_label) + '</div>'
        + '<div class="inst-month-row">'
        + '<span>کل تعهدات: ' + esc(data.month_total_due_fmt) + '</span>'
        + '<span style="color:var(--error)">پرداخت نشده: '
        + esc(data.month_total_unpaid_fmt) + '</span></div>'
        + '<div class="hint">مجموع باقیمانده همه اقساط: '
        + esc(data.total_remaining_fmt) + '</div>'
        + '</div>';

    html += '<a href="javascript:void(0)" class="add-btn"'
        + ' onclick="showAddInstallment()">+ افزودن قسط</a>';

    if (!data.list.length) {
        html += '<div class="empty-state">'
            + '<div class="empty-icon">📋</div>'
            + '<div>هیچ قسطی ندارید</div></div>';
    } else {
        data.list.forEach(function(i) {
            html += renderInstallmentItem(i);
        });
    }

    html += backBtn('finance');
    return html;
}

function renderImportantDates(data) {
    var html = '<div class="page-header">🔔 تاریخ\u200cهای مهم</div>';

    html += '<a href="javascript:void(0)" class="add-btn"'
        + ' onclick="showAddImportantDate(window._dateCategories)">+ افزودن تاریخ مهم</a>';

    if (!data.items.length) {
        html += '<div class="empty-state">'
            + '<div class="empty-icon">📅</div>'
            + '<div>هیچ تاریخ مهمی ثبت نشده</div></div>';
    } else {
        var overdue = data.items.filter(function(i) { return i.urgency === 'overdue'; });
        var urgent  = data.items.filter(function(i) { return i.urgency === 'urgent'; });
        var soon    = data.items.filter(function(i) { return i.urgency === 'soon'; });
        var ok      = data.items.filter(function(i) { return i.urgency === 'ok'; });

        if (overdue.length || urgent.length) {
            html += '<div class="dates-group-label urgent-label">فوری</div>';
            overdue.concat(urgent).forEach(function(i) {
                html += renderDateItem(i);
            });
        }
        if (soon.length) {
            html += '<div class="dates-group-label soon-label">این ماه</div>';
            soon.forEach(function(i) { html += renderDateItem(i); });
        }
        if (ok.length) {
            html += '<div class="dates-group-label ok-label">بعداً</div>';
            ok.forEach(function(i) { html += renderDateItem(i); });
        }
    }

    html += backBtn('home');
    return html;
}

function renderDateItem(i) {
    var urgencyCls = {
        overdue: 'date-dot overdue',
        urgent:  'date-dot urgent',
        soon:    'date-dot soon',
        ok:      'date-dot ok',
    }[i.urgency] || 'date-dot ok';

    var renewBtn = '<button class="chip chip-edit"'
        + ' onclick="action(\'renew_important_date\',{id:' + i.id + '})">'
        + (i.is_repeating ? 'تمدید کردم' : 'تموم شد') + '</button>';

    var editBtn = '<button class="chip chip-neutral"'
        + ' onclick="showEditImportantDate(' + JSON.stringify(i) + ')">✎</button>';

    var delBtn = '<button class="chip chip-delete"'
        + ' onclick="action(\'delete_important_date\',{id:' + i.id + '})">حذف</button>';

    var repeatLabel = '';
    if (i.repeat_type === 'yearly') repeatLabel = ' · سالانه';
    else if (i.repeat_type === 'custom')
        repeatLabel = ' · هر ' + pd(i.repeat_months) + ' ماه';

    return '<div class="date-item">'
        + '<div class="date-item-top">'
        + '<span class="' + urgencyCls + '"></span>'
        + '<span class="date-item-title">' + esc(i.title) + '</span>'
        + '<span class="date-item-countdown ' + i.urgency + '">'
        + esc(i.countdown) + '</span></div>'
        + '<div class="date-item-meta">'
        + esc(i.category) + ' · ' + esc(i.date_fmt) + repeatLabel
        + (i.notes ? ' · ' + esc(i.notes) : '') + '</div>'
        + '<div class="date-item-actions">'
        + renewBtn + editBtn + delBtn + '</div></div>';
}

function showAddImportantDate(categories) {
    var now = new Date();
    var todayIso = isoFromGregorian(now.getFullYear(), now.getMonth() + 1, now.getDate());
    showModal({
        title: 'تاریخ مهم جدید',
        cmd: 'add_important_date',
        fields: [
            { label: 'عنوان', key: 'title', validate: 'required' },
            { label: 'تاریخ', key: 'date',
              type: 'jalali-date', value: todayIso, validate: 'required', clearable: false },
            { label: 'دسته', key: 'category', type: 'select',
              value: 'سایر', options: categories },
            { label: 'تکرار', key: 'repeat_type', type: 'select',
              value: 'none',
              options: ['none', 'yearly', 'custom'] },
            { label: 'یادداشت (اختیاری)', key: 'notes',
              placeholder: '' },
        ],
    });
}

function showEditImportantDate(i) {
    showModal({
        title: 'ویرایش تاریخ مهم',
        cmd: 'edit_important_date',
        params: { id: i.id },
        fields: [
            { label: 'عنوان', key: 'title',
              value: i.title, validate: 'required' },
            { label: 'تاریخ', key: 'date',
              type: 'jalali-date', value: i.date, validate: 'required', clearable: false },
            { label: 'دسته', key: 'category', type: 'select',
              value: i.category, options: window._dateCategories },
            { label: 'تکرار', key: 'repeat_type', type: 'select',
              value: i.repeat_type,
              options: ['none', 'yearly', 'custom'] },
            { label: 'یادداشت', key: 'notes', value: i.notes },
        ],
    });
}

function renderInstallmentItem(i) {
    var settledBadge = i.is_settled
        ? '<span class="inst-settled">✓ تسویه شد</span>' : '';
    var dueBadge = !i.is_settled
        ? '<span class="' + (i.is_overdue ? 'inst-overdue' : 'inst-due') + '">'
          + esc(i.due_label) + '</span>'
        : '';
    var payBtn = (!i.is_settled && !i.paid_this_month)
        ? '<button class="btn-sm-green" onclick="action(\'pay_installment\',{id:'
          + i.id + '})">پرداخت کردم</button>' : '';
    var paidMonthBadge = (!i.is_settled && i.paid_this_month)
        ? '<span class="inst-paid-month">✓ این ماه پرداخت شد</span>' : '';

    return '<div class="section" style="margin-bottom:8px">'
        + '<div class="sec-header">'
        + '<span class="sec-title">' + esc(i.title) + '</span>'
        + '<div style="display:flex;gap:6px;align-items:center">'
        + settledBadge + dueBadge
        + '<button class="chip chip-edit" onclick="showEditInstallment('
        + JSON.stringify(i) + ')">✎</button>'
        + '<button class="chip chip-delete" onclick="action(\'delete_installment\',{id:'
        + i.id + '})">حذف</button>'
        + '</div></div>'
        + '<div class="inst-bar"><div class="inst-bar-fill" style="width:'
        + i.progress + '%' + (i.is_settled ? ';background:var(--success)' : '') + '"></div></div>'
        + '<div class="inst-stats">'
        + '<span>' + pd(i.paid_count) + ' از ' + pd(i.total_count) + ' قسط</span>'
        + '<span>' + esc(i.amount_fmt) + ' / ماه</span>'
        + '<span style="color:var(--error)">باقیمانده: '
        + esc(i.remaining_fmt) + '</span></div>'
        + (payBtn || paidMonthBadge ? '<div style="margin-top:8px">' + payBtn + paidMonthBadge + '</div>' : '')
        + '</div>';
}

function showAddInstallment() {
    var now = new Date();
    var todayIso = isoFromGregorian(now.getFullYear(), now.getMonth() + 1, now.getDate());
    showModal({
        title: 'افزودن قسط',
        cmd: 'add_installment',
        fields: [
            { label: 'عنوان (مثلاً: اقساط گوشی)', key: 'title',
              validate: 'required' },
            { label: 'مبلغ هر قسط (تومان)', key: 'amount',
              type: 'number', validate: 'amount' },
            { label: 'تعداد کل اقساط', key: 'total_count',
              type: 'number', placeholder: '12', validate: 'required' },
            { label: 'تاریخ اولین قسط', key: 'start_date',
              type: 'jalali-date', value: todayIso, validate: 'required', clearable: false },
            { label: 'سررسید (چندم هر ماه)', key: 'due_day',
              type: 'number', placeholder: '15', validate: 'required' },
        ],
    });
}

function showEditInstallment(i) {
    showModal({
        title: 'ویرایش قسط',
        cmd: 'edit_installment',
        params: { id: i.id },
        fields: [
            { label: 'عنوان', key: 'title',
              value: i.title, validate: 'required' },
            { label: 'مبلغ هر قسط (تومان)', key: 'amount',
              type: 'number', value: i.amount, validate: 'amount' },
            { label: 'تعداد کل اقساط', key: 'total_count',
              type: 'number', value: i.total_count, validate: 'required' },
            { label: 'تاریخ اولین قسط', key: 'start_date',
              type: 'jalali-date', value: i.start_date, validate: 'required', clearable: false },
            { label: 'سررسید (چندم هر ماه)', key: 'due_day',
              type: 'number', value: i.due_day, validate: 'required' },
        ],
    });
}

var _showCompletedProjects = false;
var _showFinanceTransactions = false;

function getProjectById(id) {
    return (window._projectsList || []).find(function(x) { return x.id === id; });
}

function closeProjectSheet() {
    var o = document.getElementById('proj-sheet');
    if (o) o.style.display = 'none';
}

function showProjectSheet(id) {
    closeProjectSheet();
    var p = getProjectById(id);
    if (!p) return;
    var overlay = document.getElementById('proj-sheet');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'proj-sheet';
        overlay.className = 'proj-sheet-overlay';
        document.body.appendChild(overlay);
    }
    var doneLabel = p.is_done ? '↩ بازگردانی به فعال' : '✓ علامت‌گذاری تموم‌شده';
    overlay.innerHTML =
        '<div class="proj-sheet" onclick="event.stopPropagation()">' +
        '<div class="proj-sheet-handle"></div>' +
        '<div class="proj-sheet-title">' + esc(p.title) + '</div>' +
        '<button type="button" class="proj-sheet-btn" onclick="closeProjectSheet();showEditProject(' + id + ',window._projectColors)">✎ ویرایش پروژه</button>' +
        '<button type="button" class="proj-sheet-btn" onclick="closeProjectSheet();action(\'toggle_project_done\',{id:' + id + '})">' + doneLabel + '</button>' +
        '<button type="button" class="proj-sheet-btn danger" onclick="closeProjectSheet();action(\'delete_project\',{id:' + id + '})">🗑 حذف پروژه</button>' +
        '<button type="button" class="proj-sheet-btn cancel" onclick="closeProjectSheet()">انصراف</button></div>';
    overlay.style.display = 'flex';
    overlay.onclick = closeProjectSheet;
}

function projectProgressRing(pct, color, size) {
    size = size || 48;
    var r = (size - 8) / 2;
    var c = 2 * Math.PI * r;
    var offset = c * (1 - Math.min(100, Math.max(0, pct)) / 100);
    var cx = size / 2;
    return '<svg class="proj-ring" width="' + size + '" height="' + size + '" viewBox="0 0 ' + size + ' ' + size + '" aria-hidden="true">' +
        '<circle cx="' + cx + '" cy="' + cx + '" r="' + r + '" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="4"/>' +
        '<circle cx="' + cx + '" cy="' + cx + '" r="' + r + '" fill="none" stroke="' + esc(color) + '" stroke-width="4" ' +
        'stroke-dasharray="' + c.toFixed(2) + '" stroke-dashoffset="' + offset.toFixed(2) + '" ' +
        'stroke-linecap="round" transform="rotate(-90 ' + cx + ' ' + cx + ')"/>' +
        '<text x="' + cx + '" y="' + (cx + 4) + '" text-anchor="middle" fill="currentColor" font-size="11" font-weight="bold">' +
        pd(pct) + '٪</text></svg>';
}

function projectDeadlineBadge(p) {
    if (!p.deadline_label) return '';
    var cls = 'proj-deadline-badge';
    if (p.deadline_overdue) cls += ' overdue';
    else if (p.deadline_label === 'امروز') cls += ' today';
    return '<span class="' + cls + '">📅 ' + esc(p.deadline_label) + '</span>';
}

function showAddProject(colors) {
    colors = colors || window._projectColors || DEFAULT_PROJECT_COLORS;
    showModal({
        title: 'پروژه جدید',
        cmd: 'add_project',
        fields: [
            { label: 'عنوان', key: 'title', validate: 'required' },
            { label: 'ددلاین (اختیاری)', key: 'deadline', type: 'jalali-date', value: '' },
            { label: 'رنگ', key: 'color', type: 'color-select', value: '#5E5CE6', options: colors },
        ],
    });
}

function showEditProject(id, colors) {
    closeProjectSheet();
    colors = colors || window._projectColors || DEFAULT_PROJECT_COLORS;
    var p = (window._projectsList || []).find(function(x) { return x.id === id; });
    if (!p && window._projectDetail && window._projectDetail.id === id) p = window._projectDetail;
    if (!p) return;
    var colorVal = p.color;
    if (colors.indexOf(colorVal) === -1) colors = colors.concat([colorVal]);
    showModal({
        title: 'ویرایش پروژه',
        cmd: 'edit_project',
        params: { id: id },
        fields: [
            { label: 'عنوان', key: 'title', value: p.title, validate: 'required' },
            { label: 'ددلاین (اختیاری)', key: 'deadline', type: 'jalali-date', value: p.deadline || '' },
            { label: 'رنگ', key: 'color', type: 'color-select', value: colorVal, options: colors },
        ],
    });
}

function renderProjectCard(p, muted) {
    var mutedCls = muted ? ' muted' : '';
    var progress = p.progress || 0;
    var html = '<div class="proj-card' + mutedCls + '" style="--project-color:' + esc(p.color) + '">';
    html += '<div class="proj-card-accent"></div>';
    html += '<div class="proj-card-body" onclick="action(\'open_project\',{id:' + p.id + '})">';
    html += '<div class="proj-card-top">';
    html += '<div class="proj-card-info">';
    html += '<div class="proj-card-title">' + esc(p.title) + '</div>';
    html += projectDeadlineBadge(p);
    html += '<div class="proj-card-meta">' + pd(p.done) + ' از ' + pd(p.total) + ' تسک انجام‌شده</div>';
    html += '</div>';
    html += projectProgressRing(progress, p.color, 52);
    html += '</div>';
    html += '<div class="proj-bar"><div class="proj-bar-fill" style="width:' + progress + '%"></div></div>';
    html += '</div>';
    html += '<button type="button" class="proj-card-menu" onclick="event.stopPropagation();showProjectSheet(' + p.id + ')" aria-label="گزینه‌ها">⋮</button>';
    html += '</div>';
    return html;
}

function renderProjects(data) {
    window._projectsList = data.list;
    window._projectColors = data.colors;
    var active = data.list.filter(function(p) { return !p.is_done; });
    var done = data.list.filter(function(p) { return p.is_done; });
    var totalTasks = 0;
    var doneTasks = 0;
    active.forEach(function(p) { totalTasks += p.total; doneTasks += p.done; });
    var overallPct = totalTasks > 0 ? Math.round(doneTasks / totalTasks * 100) : 0;

    var html = '<div class="proj-page">';

    html += '<div class="proj-header">' +
        '<div class="proj-header-top">' +
        '<span class="proj-header-title">📋 پروژه‌ها</span>' +
        '<button type="button" class="proj-header-add" onclick="showAddProject(window._projectColors)">+ پروژه جدید</button>' +
        '</div>';

    if (data.list.length) {
        html += '<div class="proj-summary">' +
            '<div class="proj-summary-item"><span class="proj-summary-val">' + pd(active.length) + '</span><span class="proj-summary-lbl">فعال</span></div>' +
            '<div class="proj-summary-item"><span class="proj-summary-val">' + pd(doneTasks) + '/' + pd(totalTasks) + '</span><span class="proj-summary-lbl">تسک</span></div>' +
            '<div class="proj-summary-item"><span class="proj-summary-val">' + pd(overallPct) + '٪</span><span class="proj-summary-lbl">پیشرفت</span></div>' +
            '</div>';
    }
    html += '</div>';

    if (!data.list.length) {
        html += finEmptyState('📋', 'هنوز پروژه‌ای ندارید.<br>اولین پروژه‌تان را بسازید و تسک‌ها را مدیریت کنید.', '+ ساخت پروژه', 'showAddProject(window._projectColors)');
        return html + '</div>';
    }

    if (active.length) {
        html += '<div class="proj-section"><div class="proj-section-head"><span class="proj-section-title">در جریان</span>' +
            '<span class="proj-section-badge">' + pd(active.length) + '</span></div>';
        active.forEach(function(p) { html += renderProjectCard(p, false); });
        html += '</div>';
    } else {
        html += '<div class="proj-section"><div class="proj-empty-mini">پروژه فعالی ندارید</div></div>';
    }

    if (done.length) {
        html += '<div class="proj-section proj-section-done">';
        html += '<button type="button" class="proj-done-toggle' + (_showCompletedProjects ? ' open' : '') +
            '" onclick="_showCompletedProjects=!_showCompletedProjects;renderApp(window._lastState)">' +
            '<span>✓ پروژه‌های تموم‌شده</span><span class="proj-section-badge">' + pd(done.length) + '</span>' +
            '<span class="proj-done-chevron">' + collapseChevron(_showCompletedProjects) + '</span></button>';
        if (_showCompletedProjects) {
            done.forEach(function(p) { html += renderProjectCard(p, true); });
        }
        html += '</div>';
    }

    return html + '</div>';
}

function renderProjectDetail(p) {
    window._projectDetail = p;
    window._projectColors = p.colors;
    var progress = p.progress || 0;

    var html = '<div class="proj-detail-page" style="--project-color:' + esc(p.color) + '">';

    html += '<div class="proj-detail-hero">' +
        '<div class="proj-detail-nav">' +
        '<button type="button" class="proj-back-btn" aria-label="برگشت به پروژه\u200cها" onclick="action(\'navigate\',{screen:\'projects\'})">' + ico('chevRight', 'ico') + '</button>' +
        '<div class="proj-detail-actions-top">' +
        '<button type="button" class="proj-icon-btn" onclick="showEditProject(' + p.id + ',window._projectColors)" title="ویرایش">✎</button>' +
        '<button type="button" class="proj-icon-btn danger" onclick="action(\'delete_project\',{id:' + p.id + '})" title="حذف">🗑</button>' +
        '</div></div>' +
        '<div class="proj-detail-hero-body">' +
        '<div class="proj-detail-hero-text">' +
        '<div class="proj-detail-name">' + esc(p.title) + '</div>' +
        projectDeadlineBadge(p) +
        '<div class="proj-detail-sub">' + pd(p.done) + ' از ' + pd(p.total) + ' تسک انجام‌شده</div>' +
        '</div>' +
        projectProgressRing(progress, p.color, 72) +
        '</div>' +
        '<div class="proj-bar proj-bar-lg"><div class="proj-bar-fill" style="width:' + progress + '%"></div></div>' +
        '<button type="button" class="proj-done-toggle-btn' + (p.is_done ? ' on' : '') +
        '" onclick="action(\'toggle_project_done\',{id:' + p.id + '})">' +
        (p.is_done ? '✓ پروژه تموم شده — بازگردانی' : '✓ علامت‌گذاری پروژه به عنوان تموم‌شده') +
        '</button></div>';

    html += '<div class="proj-tasks-card">' +
        '<div class="proj-section-head"><span class="proj-section-title">تسک‌ها</span>' +
        '<span class="proj-section-badge">' + pd(p.tasks.length) + '</span></div>';

    if (!p.tasks.length) {
        html += finEmptyState('☑', 'هنوز تسکی اضافه نکرده‌اید', '+ افزودن تسک',
            'showModal({title:\'تسک جدید\',cmd:\'add_project_task\',params:{project_id:' + p.id +
            '},fields:[{label:\'عنوان\',key:\'title\',validate:\'required\'}]})');
    } else {
        html += '<div class="proj-task-list">';
        p.tasks.forEach(function(task) {
            var rowCls = 'proj-task-item' + (task.is_done ? ' done' : '');
            html += '<div class="' + rowCls + '">';
            html += '<button type="button" class="proj-task-check' + (task.is_done ? ' checked' : '') +
                '" onclick="action(\'toggle_project_task\',{id:' + task.id + '})">' +
                (task.is_done ? '✓' : '') + '</button>';
            html += '<div class="proj-task-body" onclick="showModal({title:\'ویرایش تسک\',cmd:\'edit_project_task_title\',params:{id:' + task.id +
                '},fields:[{label:\'عنوان\',key:\'value\',value:\'' + escJs(task.title) + '\',validate:\'required\'}]})">' +
                '<div class="proj-task-title">' + esc(task.title) + '</div></div>';
            html += '<div class="proj-task-actions">';
            if (task.scheduled_today) {
                html += '<span class="proj-today-chip done">✓ امروز</span>';
            } else if (!task.is_done) {
                html += '<button type="button" class="proj-today-chip" onclick="action(\'send_task_to_today\',{id:' + task.id + '})">+ امروز</button>';
            }
            html += '<button type="button" class="proj-task-del" onclick="action(\'delete_project_task\',{id:' + task.id + '})" title="حذف">×</button>';
            html += '</div></div>';
        });
        html += '</div>';
    }

    html += '<button type="button" class="proj-add-task-btn" onclick="showModal({title:\'تسک جدید\',cmd:\'add_project_task\',params:{project_id:' + p.id +
        '},fields:[{label:\'عنوان\',key:\'title\',validate:\'required\'}]})">+ افزودن تسک</button>';
    html += '</div></div>';

    return html;
}

function renderNav(screen) {
    function item(id, label, iconName) {
        var cls = screen === id ? 'nav-btn active' : 'nav-btn';
        var current = screen === id ? ' aria-current="page"' : '';
        return '<button type="button" onclick="action(\'navigate\',{screen:\'' + id + '\'})" class="' + cls + '"' + current +
            ' aria-label="' + label + '"><span class="nav-icon" aria-hidden="true">' + (ICON[iconName] || '') + '</span>' + label + '</button>';
    }
    return item('home', 'امروز', 'home') +
        item('finance', 'مالی', 'wallet') +
        item('projects', 'پروژه\u200cها', 'folder') +
        item('analytics', 'آمار', 'chart');
}

/* Main render */
function renderApp(state) {
    closeProjectSheet();
    window._categories = state.finance_categories || [];
    window._investCategories = state.investment_categories || [];
    window._moodEmojis = state.mood_emojis || [];
    window._dateCategories = state.important_dates
        ? (state.important_dates.categories || []) : window._dateCategories || [];
    document.documentElement.setAttribute('data-theme', state.theme || 'dark');
    var themeMeta = document.querySelector('meta[name="theme-color"]');
    if (themeMeta) {
        themeMeta.setAttribute('content', themeColorForScreen(state.screen, state.theme));
    }

    var root = document.getElementById('app-root');
    if (!root) return;

    var html = '';
    if (state.screen === 'home' && state.home) html = renderHome(state.home);
    else if (state.screen === 'finance' && state.finance_screen) html = renderFinanceScreen(state.finance_screen);
    else if (state.screen === 'installments' && state.installments) html = renderInstallments(state.installments);
    else if (state.screen === 'analytics' && state.analytics) html = renderAnalytics(state.analytics);
    else if (state.screen === 'settings' && state.settings) html = renderSettings(state.settings);
    else if (state.screen === 'recurring' && state.recurring) html = renderRecurring(state.recurring);
    else if (state.screen === 'projects' && state.projects) html = renderProjects(state.projects);
    else if (state.screen === 'project_detail' && state.project_detail) html = renderProjectDetail(state.project_detail);
    else if (state.screen === 'important_dates' && state.important_dates) html = renderImportantDates(state.important_dates);

    window._lastState = state;

    var focused = document.activeElement;
    var restoreSearch = focused && focused.classList && focused.classList.contains('search-input');
    var searchCaret = restoreSearch ? focused.selectionStart : null;
    var restoreNote = focused && focused.id === 'daily-note';
    var noteCaret = restoreNote ? focused.selectionStart : null;

    var screenChanged = window._renderedScreen !== state.screen;
    window._renderedScreen = state.screen;

    root.innerHTML = html;

    if (screenChanged) {
        root.classList.add('screen-enter');
        requestAnimationFrame(function() { root.classList.remove('screen-enter'); });
    }

    if (restoreSearch) {
        var searchInput = document.querySelector('.search-input');
        if (searchInput) {
            searchInput.focus();
            if (searchCaret != null) {
                try { searchInput.setSelectionRange(searchCaret, searchCaret); } catch (e) {}
            }
        }
    } else if (restoreNote) {
        var noteInput = document.getElementById('daily-note');
        if (noteInput) {
            noteInput.focus();
            if (noteCaret != null) {
                try { noteInput.setSelectionRange(noteCaret, noteCaret); } catch (e) {}
            }
        }
    }

    if (state.screen === 'settings' && window._exportData) {
        var exportTa = document.getElementById('export-ta');
        if (exportTa) exportTa.value = window._exportData;
    }

    var nav = document.getElementById('bottom-nav');
    if (nav && (state.screen === 'home' || state.screen === 'finance' || state.screen === 'analytics' || state.screen === 'projects')) {
        nav.innerHTML = renderNav(state.screen);
        nav.style.display = 'flex';
    } else if (nav) {
        nav.style.display = 'none';
    }

    if (state.toast) showToast(state.toast.message, state.toast.type);
}
