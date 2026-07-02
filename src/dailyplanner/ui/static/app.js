/* Daily Planner SPA client */
window._actions = [];

function flushPendingNote() {
    if (!_noteTimer) return;
    clearTimeout(_noteTimer);
    _noteTimer = null;
    var el = document.getElementById('daily-note');
    if (el) {
        window._actions.push({ cmd: 'set_note', params: { value: el.value } });
    }
}

function flushPendingSearch() {
    if (!_searchTimer) return;
    clearTimeout(_searchTimer);
    _searchTimer = null;
    var el = document.querySelector('.search-input');
    if (el) {
        window._actions.push({ cmd: 'set_search', params: { q: el.value } });
    }
}

function action(cmd, params) {
    if (cmd !== 'set_note') {
        flushPendingNote();
    }
    if (cmd !== 'set_search') {
        flushPendingSearch();
    }
    if (cmd !== 'set_tracking_label') {
        flushPendingTrackLabels();
    }
    window._actions.push({ cmd: cmd, params: params || {} });
}

var _searchTimer = null;
function applyHomeSearchFilter(q) {
    q = (q || '').trim().toLowerCase();
    var list = document.querySelector('.home-task-list');
    if (!list) return;
    var cards = list.querySelectorAll('.task-card');
    var visible = 0;
    cards.forEach(function(card) {
        var titleEl = card.querySelector('.task-title-wrap');
        var text = titleEl
            ? (titleEl.getAttribute('title') || titleEl.textContent || '').toLowerCase()
            : '';
        var show = !q || text.indexOf(q) !== -1;
        card.style.display = show ? '' : 'none';
        if (show) visible += 1;
    });
    var empty = list.querySelector('.home-search-empty');
    if (q && cards.length && visible === 0) {
        if (!empty) {
            empty = document.createElement('div');
            empty.className = 'empty-state home-search-empty';
            empty.innerHTML = '<div class="empty-title">نتیجه\u200cای یافت نشد</div>' +
                '<div class="empty-sub">عبارت جستجو را تغییر دهید</div>';
            list.appendChild(empty);
        }
        empty.style.display = '';
    } else if (empty) {
        empty.style.display = 'none';
    }
}

function debounceSearch(q) {
    window._liveSearchQuery = q;
    applyHomeSearchFilter(q);
    clearTimeout(_searchTimer);
    _searchTimer = setTimeout(function() { action('set_search', { q: q }); }, 350);
}

var _noteTimer = null;
var _noteSavedTimer = null;
var _trackLabelTimers = {};

function debounceTrackLabel(intervalId, val) {
    clearTimeout(_trackLabelTimers[intervalId]);
    _trackLabelTimers[intervalId] = setTimeout(function() {
        delete _trackLabelTimers[intervalId];
        setTrackLabel(intervalId, val);
    }, 600);
}

function flushPendingTrackLabels() {
    Object.keys(_trackLabelTimers).forEach(function(id) {
        clearTimeout(_trackLabelTimers[id]);
        delete _trackLabelTimers[id];
        var el = document.querySelector('.track-label-input[data-interval-id="' + id + '"]');
        if (el) setTrackLabel(+id, el.value);
    });
}

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
        .replace(/\r/g, '\\r')
        .replace(/\n/g, '\\n')
        .replace(/\u2028/g, '\\u2028')
        .replace(/\u2029/g, '\\u2029')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function pd(n) {
    if (n == null || (typeof n === 'number' && isNaN(n))) return '۰';
    var d = '۰۱۲۳۴۵۶۷۸۹';
    return String(n).replace(/\d/g, function(c) { return d[+c]; });
}

function fmtElapsed(secs) {
    secs = Math.max(0, Math.floor(secs));
    var h = Math.floor(secs / 3600);
    var m = Math.floor((secs % 3600) / 60);
    var s = secs % 60;
    var digits = '۰۱۲۳۴۵۶۷۸۹';
    function p(n) {
        return (n < 10 ? '0' + n : '' + n).replace(/[0-9]/g, function(d) { return digits[+d]; });
    }
    return p(h) + ':' + p(m) + ':' + p(s);
}

function stopTrackingTicker() {
    window._trackingEpoch = null;
    if (window._trackTicker) {
        clearInterval(window._trackTicker);
        window._trackTicker = null;
    }
}

function syncTrackingTicker() {
    var el = document.getElementById('tracking-live');
    if (!el || !el.dataset.startedEpoch) {
        stopTrackingTicker();
        return;
    }
    window._trackingEpoch = parseFloat(el.dataset.startedEpoch);
    if (!window._trackTicker) {
        window._trackTicker = setInterval(function() {
            var e = document.getElementById('tracking-live');
            if (!e || !e.dataset.startedEpoch) {
                stopTrackingTicker();
                return;
            }
            window._trackingEpoch = parseFloat(e.dataset.startedEpoch);
            e.textContent = fmtElapsed(Math.floor(Date.now() / 1000 - window._trackingEpoch));
        }, 1000);
    }
    el.textContent = fmtElapsed(Math.floor(Date.now() / 1000 - window._trackingEpoch));
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
    tracking: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="13" r="7"/><path d="M12 10v3l2 2"/><path d="M9 3h6"/><path d="M12 3v3"/></svg>',
    invest: '<svg viewBox="0 0 24 24"><path d="M12 2 15 9h7l-5.5 4.5L18 21l-6-4-6 4 1.5-7.5L2 9h7z"/></svg>',
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
    var map = { home: '#0C4A6E', finance: '#0F2E28', investments: '#2A1F0A', projects: '#6366F1', analytics: '#1A1A24', tracking: '#0F2A2E' };
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
    hms: function(v) {
        var m = normalizeDigits(v).trim().match(/^(\d{1,2}):(\d{2})(?::(\d{2}))?$/);
        return !!(m && +m[1] <= 99 && +m[2] < 60 && (!m[3] || +m[3] < 60));
    },
    hm: function(v) {
        var m = normalizeDigits(v).trim().match(/^(\d{1,2}):(\d{2})$/);
        return !!(m && +m[1] < 24 && +m[2] < 60);
    },
    amount: function(v) { return parseFloat(normalizeNumber(v)) > 0; },
    budget: function(v) { var n = parseFloat(normalizeNumber(v)); return !isNaN(n) && n >= 0; },
    required: function(v) { return v.trim().length > 0; },
    repeatMonths: function(v) {
        var n = parseInt(normalizeNumber(v), 10);
        return !isNaN(n) && n >= 1 && n <= 120;
    },
    installmentTotal: function(v) {
        var n = parseInt(normalizeNumber(v), 10);
        return !isNaN(n) && n >= 1 && n <= 360;
    },
    dueDay: function(v) {
        var n = parseInt(normalizeNumber(v), 10);
        return !isNaN(n) && n >= 1 && n <= 31;
    },
};

var _PERSIAN_DIGITS = '۰۱۲۳۴۵۶۷۸۹';
var _ARABIC_DIGITS = '٠١٢٣٤٥٦٧٨٩';

function normalizeDigits(text) {
    if (text == null) return '';
    return String(text).replace(/[۰-۹]/g, function(c) {
        return String(_PERSIAN_DIGITS.indexOf(c));
    }).replace(/[٠-٩]/g, function(c) {
        return String(_ARABIC_DIGITS.indexOf(c));
    });
}

function stripGroupSeparators(text) {
    return String(text || '').replace(/[,،]/g, '');
}

function normalizeNumber(text) {
    return stripGroupSeparators(normalizeDigits(text));
}

function formatNumberGrouped(text) {
    var raw = normalizeNumber(text).replace(/[^\d]/g, '');
    if (!raw) return '';
    return raw.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

function isGroupedAmountField(f) {
    return f.validate === 'amount' || f.validate === 'budget' || f.grouped === true;
}

function bindGroupedNumberInput(el) {
    function applyFormat() {
        var start = el.selectionStart;
        var end = el.selectionEnd;
        var before = el.value;
        var digitsBefore = before.slice(0, start).replace(/[^\d]/g, '').length;
        var formatted = formatNumberGrouped(before);
        el.value = formatted;
        var pos = formatted.length;
        var count = 0;
        for (var i = 0; i < formatted.length; i++) {
            if (/\d/.test(formatted[i])) {
                count++;
                if (count >= digitsBefore) {
                    pos = i + 1;
                    break;
                }
            }
        }
        el.setSelectionRange(pos, pos);
    }
    el.addEventListener('input', applyFormat);
    el.addEventListener('paste', function() { setTimeout(applyFormat, 0); });
}

function parseBankSms(text) {
    var empty = { amount: 0, direction: null };
    if (!text || !String(text).trim()) return empty;
    var t = normalizeDigits(String(text)).trim();
    var amount = 0;
    var direction = null;
    var lines = t.split(/\r?\n/);
    for (var i = 0; i < lines.length; i++) {
        var m = lines[i].trim().match(/^([+-])\s*([\d,\u060c]+)$/);
        if (m) {
            var a = parseInt(m[2].replace(/[,،]/g, ''), 10);
            if (!isNaN(a) && a > 0) {
                amount = Math.floor(a / 10);
                direction = m[1] === '+' ? 'income' : 'expense';
                break;
            }
        }
    }
    return { amount: amount, direction: direction };
}

function insertSmsField(fields, amountKey) {
    amountKey = amountKey || 'amount';
    if ((fields || []).some(function(f) { return f.key === 'sms'; })) return fields;
    var smsField = {
        label: 'متن پیامک (اختیاری)',
        key: 'sms',
        type: 'textarea',
        placeholder: 'پیام بانکی را بچسبانید — مبلغ به‌صورت خودکار تشخیص داده می‌شود',
        parseAmountTarget: amountKey,
    };
    var result = [];
    var inserted = false;
    (fields || []).forEach(function(f) {
        if (!inserted && f.key === amountKey) {
            result.push(smsField);
            inserted = true;
        }
        result.push(f);
    });
    if (!inserted) result.unshift(smsField);
    return result;
}

function updateSmsParseHint(parsed) {
    var hint = document.getElementById('sms-parse-hint');
    if (!hint) return;
    if (parsed.amount > 0) {
        var dirLbl = parsed.direction === 'income' ? 'واریز' : (parsed.direction === 'expense' ? 'برداشت' : 'تراکنش');
        hint.textContent = '✓ ' + dirLbl + ': ' + pd(String(parsed.amount).replace(/\B(?=(\d{3})+(?!\d))/g, '،')) + ' تومان';
        hint.className = 'sms-parse-hint ok';
    } else if (hint.dataset.hasText === '1') {
        hint.textContent = 'مبلغی در پیامک پیدا نشد';
        hint.className = 'sms-parse-hint err';
    } else {
        hint.textContent = '';
        hint.className = 'sms-parse-hint';
    }
}

function bindSmsAmountAutofill(amountKey) {
    amountKey = amountKey || 'amount';
    var smsEl = document.getElementById('mf-sms');
    if (!smsEl) return;
    var hint = document.createElement('div');
    hint.id = 'sms-parse-hint';
    hint.className = 'sms-parse-hint';
    smsEl.parentNode.appendChild(hint);
    function apply() {
        hint.dataset.hasText = smsEl.value.trim() ? '1' : '0';
        var parsed = parseBankSms(smsEl.value);
        var amountEl = document.getElementById('mf-' + amountKey);
        if (parsed.amount > 0 && amountEl) amountEl.value = formatNumberGrouped(String(parsed.amount));
        updateSmsParseHint(parsed);
    }
    smsEl.addEventListener('input', apply);
    smsEl.addEventListener('paste', function() { setTimeout(apply, 0); });
}

function applySmsAmountInModal(params, fields) {
    var sms = (params.sms || '').trim();
    if (!sms) return;
    var targetKey = 'amount';
    (fields || []).some(function(f) {
        if (f.key === 'sms' && f.parseAmountTarget) {
            targetKey = f.parseAmountTarget;
            return true;
        }
        return false;
    });
    var parsed = parseBankSms(sms);
    var current = parseFloat(normalizeNumber(params[targetKey] || ''));
    if (parsed.amount > 0 && (isNaN(current) || current <= 0)) {
        params[targetKey] = String(parsed.amount);
    }
}

var REPEAT_TYPE_OPTIONS = [
    { value: 'none', label: 'بدون تکرار' },
    { value: 'yearly', label: 'سالانه' },
    { value: 'custom', label: 'هر چند ماه (سفارشی)' },
];

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

function syncTimePickerColDisplay(col) {
    var input = col.querySelector('.time-picker-val');
    if (!input) return;
    var val = parseInt(col.dataset.val, 10) || 0;
    input.value = pd(pad2(val));
}

function commitTimePickerCol(col, pickerWrap, skipPreview) {
    var input = col.querySelector('.time-picker-val');
    if (!input) return;
    var max = parseInt(col.dataset.max, 10);
    var raw = normalizeDigits(input.value).trim();
    var val = parseInt(raw, 10);
    if (isNaN(val)) val = parseInt(col.dataset.val, 10) || 0;
    val = Math.max(0, Math.min(max, val));
    col.dataset.val = String(val);
    syncTimePickerColDisplay(col);
    if (!skipPreview) updateTimePickerPreview(pickerWrap);
}

function commitTimePicker(picker) {
    if (!picker) return;
    picker.querySelectorAll('.time-picker-col').forEach(function(col) {
        commitTimePickerCol(col, picker, true);
    });
    updateTimePickerPreview(picker);
}

function readTimePickerParts(el) {
    var h = 0, m = 0, s = 0;
    el.querySelectorAll('.time-picker-col').forEach(function(col) {
        var v = parseInt(col.dataset.val, 10) || 0;
        if (col.dataset.unit === 'h') h = v;
        else if (col.dataset.unit === 'm') m = v;
        else if (col.dataset.unit === 's') s = v;
    });
    return { h: h, m: m, s: s };
}

function getTimePickerValue(el) {
    if (!el) return '';
    commitTimePicker(el);
    var parts = readTimePickerParts(el);
    if (el.dataset.mode === 'hms') {
        return parts.h + ':' + pad2(parts.m) + ':' + pad2(parts.s);
    }
    return parts.h + ':' + pad2(parts.m);
}

function updateTimePickerPreview(picker) {
    var preview = picker.querySelector('.time-picker-preview');
    if (!preview) return;
    var parts = readTimePickerParts(picker);
    if (picker.dataset.mode === 'hms') {
        preview.textContent = pd(parts.h) + ':' + pd(pad2(parts.m)) + ':' + pd(pad2(parts.s));
    } else {
        preview.textContent = pd(parts.h) + ':' + pd(pad2(parts.m));
    }
}

function setTimePickerValues(picker, h, m, s) {
    picker.querySelectorAll('.time-picker-col').forEach(function(col) {
        var unit = col.dataset.unit;
        var max = parseInt(col.dataset.max, 10);
        var val = unit === 'h' ? h : (unit === 'm' ? m : s);
        val = Math.max(0, Math.min(max, val));
        col.dataset.val = String(val);
        syncTimePickerColDisplay(col);
    });
    updateTimePickerPreview(picker);
}

function carryTimeUnit(picker, unit, delta) {
    var order = picker.dataset.mode === 'hms' ? ['s', 'm', 'h'] : ['m', 'h'];
    var idx = order.indexOf(unit);
    if (idx < 0 || idx >= order.length - 1) return;
    stepTimeUnit(picker, order[idx + 1], delta);
}

function stepTimeUnit(picker, unit, delta) {
    var col = picker.querySelector('.time-picker-col[data-unit="' + unit + '"]');
    if (!col) return;
    var max = parseInt(col.dataset.max, 10);
    var val = (parseInt(col.dataset.val, 10) || 0) + delta;
    if (val > max) {
        val = 0;
        carryTimeUnit(picker, unit, 1);
    } else if (val < 0) {
        val = max;
        carryTimeUnit(picker, unit, -1);
    }
    col.dataset.val = String(val);
    syncTimePickerColDisplay(col);
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

    var num = document.createElement('input');
    num.type = 'text';
    num.inputMode = 'numeric';
    num.autocomplete = 'off';
    num.spellcheck = false;
    num.className = 'time-picker-val';
    num.setAttribute('aria-label', label);
    num.value = pd(pad2(col.dataset.val));
    num.addEventListener('focus', function() {
        num.select();
    });
    num.addEventListener('blur', function() {
        commitTimePickerCol(col, pickerWrap);
    });
    num.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            e.stopPropagation();
            commitTimePickerCol(col, pickerWrap);
            num.blur();
            return;
        }
        if (e.key === 'ArrowUp') {
            e.preventDefault();
            stepTimeUnit(pickerWrap, key, 1);
            return;
        }
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            stepTimeUnit(pickerWrap, key, -1);
            return;
        }
    });

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

function isModalFieldVisible(f) {
    if (!f.showWhen) return true;
    var el = document.getElementById('mf-' + f.showWhen.key);
    return el && el.value === f.showWhen.value;
}

function syncModalConditionalFields() {
    var fc = document.getElementById('modal-fields');
    if (!fc) return;
    fc.querySelectorAll('.modal-field-group[data-show-when]').forEach(function(grp) {
        var parts = grp.dataset.showWhen.split(':');
        var key = parts[0];
        var want = parts.slice(1).join(':');
        var el = document.getElementById('mf-' + key);
        grp.style.display = (el && el.value === want) ? '' : 'none';
    });
}

function bindModalConditionalListeners(fc) {
    if (!fc || fc.dataset.condBound) return;
    fc.dataset.condBound = '1';
    fc.addEventListener('change', function(e) {
        if (e.target.matches('select, input')) syncModalConditionalFields();
    });
}

function modalLayoutFields(fields) {
    return (fields || []).filter(function(f) { return f.key !== 'sms'; });
}

function modalHasTallFields(fields) {
    return modalLayoutFields(fields).some(function(f) {
        return f.type === 'jalali-date' || f.type === 'time-hms' || f.type === 'time-hm'
            || f.type === 'color-select' || f.type === 'textarea';
    });
}

function shouldUseCenterModal(config) {
    if (isMobileTouch()) return false;
    return true;
}

function ensureModalStructure() {
    var box = document.getElementById('modal-box');
    if (!box || document.getElementById('modal-body')) return;
    var fields = document.getElementById('modal-fields');
    var err = document.getElementById('modal-error');
    var btns = box.querySelector('.modal-btns');
    if (!fields) return;
    var body = document.createElement('div');
    body.className = 'modal-body';
    body.id = 'modal-body';
    box.insertBefore(body, btns || null);
    body.appendChild(fields);
    if (err) body.appendChild(err);
}

function showModal(config) {
    ensureModalStructure();
    closeProjectSheet();
    closeActivityPicker();
    _modal = config;
    var titleEl = document.getElementById('modal-title');
    if (titleEl) titleEl.textContent = config.title || '';
    var fc = document.getElementById('modal-fields');
    if (!fc) return;
    fc.innerHTML = '';
    fc.removeAttribute('data-cond-bound');
    if (config.html) {
        fc.innerHTML = config.html;
    } else {
    (config.fields || []).forEach(function(f) {
        var grp = document.createElement('div');
        grp.className = 'modal-field-group';
        grp.id = 'mfg-' + f.key;
        if (f.showWhen) {
            grp.dataset.showWhen = f.showWhen.key + ':' + f.showWhen.value;
        }
        var lbl = document.createElement('div');
        lbl.className = 'modal-label';
        lbl.textContent = f.label;
        grp.appendChild(lbl);
        if (f.type === 'color-select') {
            grp.appendChild(buildColorPickerEl(f));
        } else if (f.type === 'jalali-date') {
            grp.appendChild(buildDatePickerEl(f));
        } else if (f.type === 'select') {
            var sel = document.createElement('select');
            sel.className = 'modal-input';
            sel.id = 'mf-' + f.key;
            (f.options || []).forEach(function(opt) {
                var o = document.createElement('option');
                if (opt && typeof opt === 'object') {
                    o.value = opt.value;
                    o.textContent = opt.label;
                } else {
                    o.value = opt;
                    o.textContent = opt;
                }
                if (f.value === o.value) o.selected = true;
                sel.appendChild(o);
            });
            grp.appendChild(sel);
        } else if (f.type === 'time-hms' || f.type === 'time-hm') {
            grp.appendChild(buildTimePickerEl(f));
        } else if (f.type === 'textarea') {
            var ta = document.createElement('textarea');
            ta.className = 'modal-input modal-textarea';
            ta.id = 'mf-' + f.key;
            ta.placeholder = f.placeholder || '';
            if (f.value) ta.value = f.value;
            grp.appendChild(ta);
        } else {
            var inp = document.createElement('input');
            var grouped = isGroupedAmountField(f);
            inp.type = grouped ? 'text' : (f.type || 'text');
            inp.className = 'modal-input';
            inp.id = 'mf-' + f.key;
            inp.placeholder = f.placeholder || '';
            if (grouped) {
                inp.inputMode = 'numeric';
                inp.autocomplete = 'off';
                inp.className = 'modal-input modal-input-grouped';
            }
            if (f.value !== undefined && f.value !== null) {
                inp.value = grouped ? formatNumberGrouped(String(f.value)) : f.value;
            }
            grp.appendChild(inp);
            if (grouped) bindGroupedNumberInput(inp);
        }
        fc.appendChild(grp);
    });
    }
    bindModalConditionalListeners(fc);
    syncModalConditionalFields();
    if (config.investmentCascade !== undefined) {
        bindInvestmentCascade(config.investmentCascade);
        bindInvestmentFieldSync();
    }
    if (config.allocationCascade) {
        bindAllocationCascade();
    }
    var errEl = document.getElementById('modal-error');
    if (errEl) errEl.textContent = '';
    var confirmBtn = document.querySelector('#modal .modal-confirm');
    if (confirmBtn) confirmBtn.style.display = config.hideSubmit ? 'none' : '';
    var modalEl = document.getElementById('modal');
    if (!modalEl) return;
    var useCenter = shouldUseCenterModal(config);
    modalEl.style.display = 'flex';
    modalEl.classList.toggle('modal-center', useCenter);
    modalEl.classList.toggle('modal-viewport-sync', !useCenter);
    var modalBody = document.getElementById('modal-body');
    if (modalBody) modalBody.scrollTop = 0;
    fc.scrollTop = 0;
    _modalOpenVvHeight = useCenter ? null : visibleViewportHeight();
    syncBodyScrollLock();
    syncModalViewport();
    syncKeyboardLayout();
    if ((config.fields || []).some(function(f) { return f.key === 'sms'; })) {
        var smsTarget = 'amount';
        (config.fields || []).some(function(f) {
            if (f.key === 'sms' && f.parseAmountTarget) {
                smsTarget = f.parseAmountTarget;
                return true;
            }
            return false;
        });
        bindSmsAmountAutofill(smsTarget);
    }
    var first = fc.querySelector('input:not([type="hidden"]), textarea, select');
    if (!first) first = fc.querySelector('button.color-swatch');
    if (first) {
        setTimeout(function() {
            syncModalViewport();
            syncKeyboardLayout();
            if (first.focus) {
                try { first.focus({ preventScroll: true }); } catch (e) { first.focus(); }
                ensureFieldVisible(first);
            }
        }, useCenter ? 100 : 150);
    } else {
        syncModalViewport();
        syncKeyboardLayout();
    }
}

var _modalConfirming = false;

function handleModalConfirm(e) {
    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }
    confirmModal();
}

function confirmModal() {
    if (!_modal || _modalConfirming) return;
    var params = Object.assign({}, _modal.params || {});
    var valid = true;
    var errEl = document.getElementById('modal-error');
    (_modal.fields || []).forEach(function(f) {
        if (!isModalFieldVisible(f)) {
            if (f.key === 'repeat_months') params[f.key] = 0;
            return;
        }
        var el = document.getElementById('mf-' + f.key);
        var val = '';
        if (f.type === 'time-hms' || f.type === 'time-hm') {
            if (!el) { params[f.key] = ''; return; }
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
        if ((f.type === 'number' || f.validate === 'amount' || f.validate === 'budget'
                || f.validate === 'repeatMonths' || f.validate === 'installmentTotal'
                || f.validate === 'dueDay') && val) {
            val = normalizeNumber(val);
        }
        params[f.key] = val;
    });
    applySmsAmountInModal(params, _modal.fields);
    (_modal.fields || []).forEach(function(f) {
        if (!isModalFieldVisible(f)) return;
        var val = params[f.key];
        if (f.key === 'sms') return;
        if (f.validate && _modalValidators[f.validate]) {
            if (!_modalValidators[f.validate](String(val || ''))) valid = false;
        }
    });
    if (!valid) {
        if (errEl) errEl.textContent = 'لطفاً فیلدهای مشخص‌شده را به‌درستی پر کنید';
        var modalBody = document.getElementById('modal-body');
        if (modalBody) modalBody.scrollTop = modalBody.scrollHeight;
        return;
    }
    if (_modal.onSubmit) {
        params = _modal.onSubmit(params, Object.assign({}, _modal.params || {})) || params;
    }
    if (_modal.cmd === 'set_investment_allocation_target') {
        if (params.alloc_market && !params.market) {
            params.market = params.alloc_market;
            delete params.alloc_market;
        }
        if (params.alloc_asset && !params.asset) {
            params.asset = params.alloc_asset;
            delete params.alloc_asset;
        }
        if (params.asset_key && !params.market) {
            var akParts = String(params.asset_key).split('|');
            params.market = akParts[0] || '';
            params.asset = akParts[1] || '';
            delete params.asset_key;
        }
    }
    var cmd = _modal.cmd;
    _modalConfirming = true;
    closeModal();
    action(cmd, params);
    setTimeout(function() { _modalConfirming = false; }, 400);
}

function closeModal() {
    var modal = document.getElementById('modal');
    if (!modal) return;
    var active = document.activeElement;
    if (active && modal.contains(active) && active.blur) {
        active.blur();
    }
    modal.style.display = 'none';
    modal.classList.remove('modal-viewport-sync', 'modal-center');
    _modal = null;
    _modalOpenVvHeight = null;
    syncBodyScrollLock();
    setTimeout(syncKeyboardLayout, 150);
}

document.addEventListener('click', function(e) {
    if (e.target.id === 'modal') closeModal();
});

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        if (isActivityPickerVisible()) {
            closeActivityPicker();
            return;
        }
        if (isProjectSheetVisible()) {
            closeProjectSheet();
            return;
        }
        var modal = document.getElementById('modal');
        if (modal && modal.style.display !== 'none') {
            closeModal();
        }
        return;
    }
    var modal = document.getElementById('modal');
    var modalOpen = modal && modal.style.display !== 'none';
    if (e.key === 'Enter' && !e.shiftKey && modalOpen && _modal) {
        var t = e.target;
        if (!t || t.tagName === 'TEXTAREA' || t.tagName === 'BUTTON') return;
        if (t.matches && t.matches('.time-picker-val')) return;
        if (t.matches && t.matches('input:not([type="hidden"]), select') && modal.contains(t)) {
            e.preventDefault();
            confirmModal();
        }
    }
});

(function initModalBox() {
    function bind() {
        ensureModalStructure();
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

var FIN_CHART_COLORS = ['#4DD980', '#FF7359', '#FFB020', '#818CF8', '#2DD4BF', '#F472B6', '#A3E635'];

function financeLineChartSvg(chart, w, h) {
    if (!chart || !chart.income || !chart.income.length) return '';
    var lines = [
        { points: chart.income, color: '#4DD980', label: 'درآمد', width: 1.8, opacity: 0.9, glow: 'rgba(77,217,128,0.35)' },
        { points: chart.expense, color: '#FF7359', label: 'هزینه', width: 1.8, opacity: 0.9, glow: 'rgba(255,115,89,0.35)' },
        { points: chart.investment || chart.income.map(function() { return 0; }), color: '#FFB020', label: 'سرمایه\u200cگذاری', width: 1.8, opacity: 0.85, glow: 'rgba(255,176,32,0.3)' },
        { points: chart.balance, color: '#818CF8', label: 'موجودی', width: 2.8, opacity: 1, fill: true, glow: 'rgba(129,140,248,0.45)' },
    ];
    var allVals = [];
    lines.forEach(function(l) { allVals = allVals.concat(l.points); });
    var min = Math.min.apply(null, allVals.concat([0]));
    var max = Math.max.apply(null, allVals.concat([1]));
    var range = max - min || 1;
    var n = chart.income.length;
    var padT = 16, padB = 10, padX = 6;

    function toY(v) {
        return padT + (h - padT - padB) * (1 - (v - min) / range);
    }
    function toPts(arr) {
        return arr.map(function(v, i) {
            return (padX + i * (w - padX * 2) / (n - 1 || 1)).toFixed(1) + ',' + toY(v).toFixed(1);
        });
    }

    var svg = '<svg class="finance-line-chart" viewBox="0 0 ' + w + ' ' + h + '" preserveAspectRatio="none">';
    svg += '<defs>';
    svg += '<linearGradient id="finGradBal" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#818CF8" stop-opacity="0.35"/><stop offset="100%" stop-color="#818CF8" stop-opacity="0"/></linearGradient>';
    svg += '<filter id="finGlow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>';
    svg += '</defs>';
    for (var g = 0; g <= 3; g++) {
        var gy = padT + (h - padT - padB) * g / 3;
        svg += '<line class="fin-chart-grid" x1="' + padX + '" y1="' + gy.toFixed(1) + '" x2="' + (w - padX) + '" y2="' + gy.toFixed(1) + '"/>';
    }
    if (min < 0 && max > 0) {
        var zeroY = toY(0).toFixed(1);
        svg += '<line class="fin-chart-zero" x1="' + padX + '" y1="' + zeroY + '" x2="' + (w - padX) + '" y2="' + zeroY + '"/>';
    }
    var balPts = toPts(chart.balance);
    var areaPath = 'M' + balPts[0];
    for (var i = 1; i < balPts.length; i++) areaPath += ' L' + balPts[i];
    var zeroLine = min < 0 ? toY(0) : toY(min);
    areaPath += ' L' + (padX + (n - 1) * (w - padX * 2) / (n - 1 || 1)).toFixed(1) + ',' + zeroLine.toFixed(1);
    areaPath += ' L' + padX + ',' + zeroLine.toFixed(1) + ' Z';
    svg += '<path class="fin-chart-area" d="' + areaPath + '" fill="url(#finGradBal)"/>';
    lines.forEach(function(line) {
        var pts = toPts(line.points).join(' ');
        var filter = line.fill ? ' filter="url(#finGlow)"' : '';
        svg += '<polyline class="fin-chart-line" fill="none" stroke="' + line.color + '" stroke-width="' + line.width + '" stroke-linejoin="round" stroke-linecap="round" opacity="' + line.opacity + '" points="' + pts + '"' + filter + '/>';
    });
    svg += '</svg>';

    var legend = '<div class="fin-chart-legend">';
    lines.forEach(function(line) {
        legend += '<span class="fin-legend-item"><span class="fin-legend-dot" style="background:' + line.color + ';box-shadow:0 0 6px ' + (line.glow || line.color) + '"></span>' + line.label + '</span>';
    });
    legend += '</div>';
    return legend + '<div class="fin-chart-wrap">' + svg + '</div>';
}

function finBalanceRing(income, expense, balance) {
    var savingsRate = income > 0 ? Math.round((balance / income) * 100) : (balance >= 0 ? 100 : 0);
    savingsRate = Math.max(0, Math.min(100, savingsRate));
    var r = 36, cx = 42, cy = 42, sw = 7;
    var circ = 2 * Math.PI * r;
    var offset = circ * (1 - savingsRate / 100);
    var ringColor = balance >= 0 ? '#4DD980' : '#FF7359';
    return '<div class="fin-balance-ring" aria-hidden="true">' +
        '<div class="fin-ring-glow"></div>' +
        '<svg viewBox="0 0 84 84" class="fin-ring-svg">' +
        '<circle cx="' + cx + '" cy="' + cy + '" r="' + r + '" class="fin-ring-track"/>' +
        '<circle cx="' + cx + '" cy="' + cy + '" r="' + r + '" class="fin-ring-arc"' +
        ' stroke="' + ringColor + '" stroke-dasharray="' + circ.toFixed(1) + '" stroke-dashoffset="' + offset.toFixed(1) + '"' +
        ' stroke-width="' + sw + '" transform="rotate(-90 ' + cx + ' ' + cy + ')"/>' +
        '</svg>' +
        '<div class="fin-ring-center">' +
        '<span class="fin-ring-pct">' + pd(savingsRate) + '٪</span>' +
        '<span class="fin-ring-lbl">پس\u200cانداز</span></div></div>';
}

function finCashFlowBar(income, expense) {
    var total = income + expense;
    if (total <= 0) return '';
    var incPct = Math.round(income / total * 100);
    var expPct = 100 - incPct;
    return '<div class="fin-cashflow">' +
        '<div class="fin-cashflow-bar">' +
        '<div class="fin-cashflow-inc" style="width:' + incPct + '%"></div>' +
        '<div class="fin-cashflow-exp" style="width:' + expPct + '%"></div></div>' +
        '<div class="fin-cashflow-labels">' +
        '<span class="fin-cf-inc">درآمد ' + pd(incPct) + '٪</span>' +
        '<span class="fin-cf-exp">هزینه ' + pd(expPct) + '٪</span></div></div>';
}

function finExpenseDonut(categories) {
    var expenses = (categories || []).filter(function(c) { return c.expense > 0; });
    if (!expenses.length) return '';
    expenses.sort(function(a, b) { return b.expense - a.expense; });
    var top = expenses.slice(0, 5);
    var total = expenses.reduce(function(s, c) { return s + c.expense; }, 0);
    var segs = [];
    var start = 0;
    var gradientParts = [];
    top.forEach(function(c, i) {
        var pct = c.expense / total * 100;
        var color = FIN_CHART_COLORS[i % FIN_CHART_COLORS.length];
        segs.push({ cat: c.category, pct: pct, color: color, expense_fmt: c.expense_fmt });
        gradientParts.push(color + ' ' + start.toFixed(1) + '% ' + (start + pct).toFixed(1) + '%');
        start += pct;
    });
    var legend = segs.map(function(s) {
        return '<div class="fin-donut-legend-item">' +
            '<span class="fin-donut-dot" style="background:' + s.color + '"></span>' +
            '<span class="fin-donut-cat">' + esc(s.cat) + '</span>' +
            '<span class="fin-donut-amt">' + esc(s.expense_fmt) + '</span></div>';
    }).join('');
    return '<div class="fin-donut-wrap">' +
        '<div class="fin-donut-chart" style="background:conic-gradient(' + gradientParts.join(', ') + ')">' +
        '<div class="fin-donut-hole"><span class="fin-donut-total-lbl">کل هزینه</span></div></div>' +
        '<div class="fin-donut-legend">' + legend + '</div></div>';
}

function invCategoryDonut(categories, totalFmt, centerLabel) {
    centerLabel = centerLabel || 'این ماه';
    var items = (categories || []).filter(function(c) { return Math.abs(c.amount) > 0; });
    if (!items.length) return '';
    items.sort(function(a, b) { return b.amount - a.amount; });
    var top = items.slice(0, 5);
    var total = items.reduce(function(s, c) { return s + c.amount; }, 0);
    var segs = [];
    var start = 0;
    var gradientParts = [];
    top.forEach(function(c, i) {
        var pct = c.amount / total * 100;
        var color = FIN_CHART_COLORS[i % FIN_CHART_COLORS.length];
        segs.push({ cat: c.category, pct: pct, color: color, amount_fmt: c.amount_fmt });
        gradientParts.push(color + ' ' + start.toFixed(1) + '% ' + (start + pct).toFixed(1) + '%');
        start += pct;
    });
    var legend = segs.map(function(s) {
        return '<div class="fin-donut-legend-item">' +
            '<span class="fin-donut-dot" style="background:' + s.color + '"></span>' +
            '<span class="fin-donut-cat">' + finIcon('investment', findInvestAssetEmoji(s.cat)) + ' ' + esc(s.cat) + '</span>' +
            '<span class="fin-donut-amt">' + esc(s.amount_fmt) + '</span></div>';
    }).join('');
    return '<div class="fin-donut-wrap">' +
        '<div class="fin-donut-chart" style="background:conic-gradient(' + gradientParts.join(', ') + ')">' +
        '<div class="fin-donut-hole inv-donut-hole"><span class="fin-donut-total-lbl">' + esc(centerLabel) + '</span>' +
        (totalFmt ? '<span class="inv-donut-total">' + esc(totalFmt) + '</span>' : '') +
        '</div></div>' +
        '<div class="fin-donut-legend">' + legend + '</div></div>';
}

function investSignedAmount(e) {
    return e.is_sell ? -e.amount : e.amount;
}

function investAssetKey(e) {
    var m = e.investment_meta || {};
    if (m.market && m.asset) return m.market + '|' + m.asset;
    return m.group_key || m.asset || m.market || e.category || 'سایر';
}

function investAssetLabel(e) {
    var m = e.investment_meta || {};
    var emoji = m.asset_emoji || '💎';
    var name = m.asset || m.market || e.category || 'سایر';
    return emoji + ' ' + name;
}

function investChartEntryAmount(e, chartMode) {
    if (chartMode === 'sell') return e.amount;
    if (chartMode === 'buy') return e.is_sell ? 0 : e.amount;
    return investSignedAmount(e);
}

function addGregorianDays(iso, days) {
    var p = parseIsoDate(iso);
    if (!p) return null;
    var dt = new Date(p.y, p.m - 1, p.d);
    dt.setDate(dt.getDate() + days);
    return isoFromGregorian(dt.getFullYear(), dt.getMonth() + 1, dt.getDate());
}

function jalaliDayLabel(iso) {
    var p = parseIsoDate(iso);
    if (!p) return '';
    var j = toJalaali(p.y, p.m, p.d);
    return pd(j.jd);
}

function jalaliDateLabel(iso) {
    var p = parseIsoDate(iso);
    if (!p) return '';
    var j = toJalaali(p.y, p.m, p.d);
    var jm = j.jm < 10 ? '0' + j.jm : String(j.jm);
    var jd = j.jd < 10 ? '0' + j.jd : String(j.jd);
    return pd(j.jy + '/' + jm + '/' + jd);
}

function fmtInvAmount(n) {
    if (n == null || (typeof n === 'number' && isNaN(n))) return '۰';
    var neg = n < 0;
    var abs = Math.abs(Math.round(n));
    var s = String(abs);
    var out = '';
    for (var i = 0; i < s.length; i++) {
        if (i > 0 && (s.length - i) % 3 === 0) out += ',';
        out += s[i];
    }
    return (neg ? '\u2212' : '') + pd(out);
}

window._investChartMode = window._investChartMode || 'both';

function setInvestChartMode(mode) {
    window._investChartMode = mode;
    if (window._lastState) renderApp(window._lastState);
}

function buildInvestmentChart(d) {
    var f = d.filter || {};
    var chartMode = window._investChartMode || 'both';
    var source = d.all_entries || d.entries || [];
    var categoryFiltered = filterInvestEntries(source);
    var periodEntries = categoryFiltered;
    if (chartMode === 'buy') {
        periodEntries = periodEntries.filter(function(e) { return !e.is_sell; });
    } else if (chartMode === 'sell') {
        periodEntries = periodEntries.filter(function(e) { return e.is_sell; });
    }
    if (!periodEntries.length && !categoryFiltered.length) {
        return { has_data: false, investment: [], portfolio: [], labels: [], dates: [], assets: [] };
    }

    var now = new Date();
    var todayIso = isoFromGregorian(now.getFullYear(), now.getMonth() + 1, now.getDate());
    var startIso;
    var endIso = todayIso;
    if (f.mode === 'month' || f.mode === 'range') {
        if (!f.start) return { has_data: false, investment: [], portfolio: [], labels: [], dates: [], assets: [] };
        startIso = f.start;
        endIso = f.end || todayIso;
    } else {
        var sortedDates = categoryFiltered.map(function(e) { return e.date; }).sort();
        startIso = sortedDates[0] || todayIso;
    }
    if (startIso > endIso) {
        var tmp = startIso;
        startIso = endIso;
        endIso = tmp;
    }

    var dailyAmt = {};
    var dailyNetAmt = {};
    var dailyByAsset = {};
    var assetInfo = {};
    categoryFiltered.forEach(function(e) {
        dailyNetAmt[e.date] = (dailyNetAmt[e.date] || 0) + investSignedAmount(e);
    });
    periodEntries.forEach(function(e) {
        var amt = investChartEntryAmount(e, chartMode);
        var key = investAssetKey(e);
        assetInfo[key] = investAssetLabel(e);
        dailyAmt[e.date] = (dailyAmt[e.date] || 0) + amt;
        if (!dailyByAsset[key]) dailyByAsset[key] = {};
        dailyByAsset[key][e.date] = (dailyByAsset[key][e.date] || 0) + amt;
    });

    var portfolioBase = 0;
    var assetBase = {};
    categoryFiltered.forEach(function(e) {
        if (e.date >= startIso) return;
        var amt = investSignedAmount(e);
        var key = investAssetKey(e);
        portfolioBase += amt;
        assetBase[key] = (assetBase[key] || 0) + amt;
    });

    var cumPeriod = 0;
    var labels = [];
    var dates = [];
    var investment = [];
    var portfolio = [];
    var cursor = startIso;
    while (cursor && cursor <= endIso) {
        var dayAmt = dailyAmt[cursor] || 0;
        var netAmt = dailyNetAmt[cursor] || 0;
        cumPeriod += dayAmt;
        portfolioBase += netAmt;
        investment.push(cumPeriod);
        portfolio.push(portfolioBase);
        labels.push(jalaliDayLabel(cursor));
        dates.push(cursor);
        cursor = addGregorianDays(cursor, 1);
    }

    var assets = Object.keys(dailyByAsset).sort().map(function(key, i) {
        var base = assetBase[key] || 0;
        var points = [];
        var day = startIso;
        while (day && day <= endIso) {
            base += dailyByAsset[key][day] || 0;
            points.push(base);
            day = addGregorianDays(day, 1);
        }
        return {
            key: key,
            label: assetInfo[key] || key,
            points: points,
            color: FIN_CHART_COLORS[i % FIN_CHART_COLORS.length],
        };
    });

    var hasData = investment.some(function(v, i) {
        return v !== 0 || portfolio[i] !== 0;
    }) || assets.some(function(a) {
        return a.points.some(function(v) { return v !== 0; });
    });
    return {
        has_data: hasData,
        investment: investment,
        portfolio: portfolio,
        assets: assets,
        labels: labels,
        dates: dates,
        mode: chartMode,
    };
}

function onInvestChartLineClick(ev, lineIdx) {
    if (ev && ev.stopPropagation) ev.stopPropagation();
    var snap = window._investChartSnapshot;
    if (!snap || !snap.lines[lineIdx]) return;
    var svg = (ev.currentTarget && ev.currentTarget.ownerSVGElement) ||
        (ev.currentTarget && ev.currentTarget.closest && ev.currentTarget.closest('svg'));
    if (!svg) {
        selectInvestChartLine(lineIdx, null);
        return;
    }
    var rect = svg.getBoundingClientRect();
    if (!rect.width) {
        selectInvestChartLine(lineIdx, null);
        return;
    }
    var clientX = ev.clientX;
    if (clientX == null && ev.touches && ev.touches[0]) clientX = ev.touches[0].clientX;
    var x = (clientX - rect.left) / rect.width * snap.width;
    var n = snap.lines[lineIdx].points.length;
    var span = snap.width - snap.padX * 2;
    var idx = Math.round((x - snap.padX) / (span / (Math.max(n - 1, 1))));
    idx = Math.max(0, Math.min(n - 1, idx));
    selectInvestChartLine(lineIdx, idx);
}

function selectInvestChartLine(lineIdx, pointIdx) {
    var snap = window._investChartSnapshot;
    if (!snap || !snap.lines[lineIdx]) return;
    var n = snap.lines[lineIdx].points.length;
    if (pointIdx == null || pointIdx < 0) pointIdx = n - 1;
    pointIdx = Math.max(0, Math.min(n - 1, pointIdx));
    window._investChartSelected = { lineIdx: lineIdx, pointIdx: pointIdx };

    var line = snap.lines[lineIdx];
    var val = line.points[pointIdx];
    var dateIso = (snap.dates && snap.dates[pointIdx]) || '';

    var tooltip = document.getElementById('invChartTooltip');
    if (tooltip) {
        tooltip.hidden = false;
        tooltip.innerHTML =
            '<span class="inv-chart-tip-dot" style="background:' + esc(line.color) + '"></span>' +
            '<div class="inv-chart-tip-body">' +
            '<span class="inv-chart-tip-name">' + esc(line.label) + '</span>' +
            '<span class="inv-chart-tip-val">' + esc(fmtInvAmount(val)) +
            '<span class="inv-chart-tip-unit">تومان</span></span>' +
            (dateIso ? '<span class="inv-chart-tip-date">' + esc(jalaliDateLabel(dateIso)) + '</span>' : '') +
            '</div>';
    }

    var wrap = document.querySelector('.inv-chart-interactive');
    if (!wrap) return;
    wrap.querySelectorAll('.inv-chart-line-group').forEach(function(g, i) {
        g.classList.toggle('active', i === lineIdx);
        g.classList.toggle('dimmed', i !== lineIdx);
    });
    wrap.querySelectorAll('.inv-chart-legend-item').forEach(function(el, i) {
        el.classList.toggle('active', i === lineIdx);
    });
    var marker = wrap.querySelector('.inv-chart-marker');
    if (marker && snap.coords && snap.coords[lineIdx] && snap.coords[lineIdx][pointIdx]) {
        var pt = snap.coords[lineIdx][pointIdx];
        marker.setAttribute('cx', pt[0]);
        marker.setAttribute('cy', pt[1]);
        marker.setAttribute('fill', line.color);
        marker.removeAttribute('hidden');
    }
}

function renderInvestChartModeChips() {
    var modes = [
        { id: 'both', label: 'هر دو' },
        { id: 'period', label: 'خالص بازه' },
        { id: 'portfolio', label: 'کل پرتفوی' },
        { id: 'buy', label: 'خرید' },
        { id: 'sell', label: 'فروش' },
    ];
    var active = window._investChartMode || 'both';
    var html = '<div class="inv-chart-mode-row">';
    modes.forEach(function(m) {
        html += '<button type="button" class="inv-chart-mode-chip' +
            (active === m.id ? ' active' : '') +
            '" onclick="setInvestChartMode(\'' + escJs(m.id) + '\')">' +
            esc(m.label) + '</button>';
    });
    return html + '</div>';
}

function investmentTrendChartSvg(chart, w, h) {
    if (!chart || !chart.investment || !chart.investment.length) return '';
    var mode = chart.mode || window._investChartMode || 'both';
    var assetLines = chart.assets || [];
    var lines = [];
    if (mode === 'both' || mode === 'period') {
        lines.push({ points: chart.investment, color: '#FFB020', label: 'خالص بازه', width: 2.4, opacity: 1 });
    }
    if (mode === 'both' || mode === 'portfolio') {
        if (assetLines.length) {
            assetLines.forEach(function(a) {
                lines.push({ points: a.points, color: a.color, label: a.label, width: 2, opacity: 0.92 });
            });
        } else {
            lines.push({
                points: chart.portfolio || chart.investment,
                color: '#818CF8',
                label: 'کل پرتفوی',
                width: 2,
                opacity: 0.9,
            });
        }
    }
    if (mode === 'buy' || mode === 'sell') {
        if (assetLines.length) {
            assetLines.forEach(function(a) {
                lines.push({ points: a.points, color: a.color, label: a.label, width: 2.2, opacity: 0.95 });
            });
        } else {
            lines.push({
                points: chart.investment,
                color: mode === 'sell' ? '#4DD980' : '#FFB020',
                label: mode === 'sell' ? 'فروش تجمعی' : 'خرید تجمعی',
                width: 2.4,
                opacity: 1,
            });
        }
    }
    if (!lines.length) return '';
    var allVals = [];
    lines.forEach(function(l) { allVals = allVals.concat(l.points); });
    var min = Math.min.apply(null, allVals.concat([0]));
    var max = Math.max.apply(null, allVals.concat([1]));
    var range = max - min || 1;
    var n = chart.investment.length;
    var padT = 16, padB = 10, padX = 6;
    function toY(v) {
        return padT + (h - padT - padB) * (1 - (v - min) / range);
    }
    function toPts(arr) {
        return arr.map(function(v, i) {
            return (padX + i * (w - padX * 2) / (n - 1 || 1)).toFixed(1) + ',' + toY(v).toFixed(1);
        });
    }
    function ptsToCoords(pts) {
        return pts.map(function(p) {
            var parts = p.split(',');
            return [parseFloat(parts[0]), parseFloat(parts[1])];
        });
    }
    var coords = [];
    lines.forEach(function(line) {
        coords.push(ptsToCoords(toPts(line.points)));
    });
    window._investChartSnapshot = {
        lines: lines,
        labels: chart.labels || [],
        dates: chart.dates || [],
        width: w,
        padX: padX,
        coords: coords,
    };

    var svg = '<svg class="finance-line-chart inv-trend-chart" viewBox="0 0 ' + w + ' ' + h + '" preserveAspectRatio="none">';
    for (var g = 0; g <= 3; g++) {
        var gy = padT + (h - padT - padB) * g / 3;
        svg += '<line class="fin-chart-grid" x1="' + padX + '" y1="' + gy.toFixed(1) + '" x2="' + (w - padX) + '" y2="' + gy.toFixed(1) + '"/>';
    }
    if (min < 0 && max > 0) {
        var zeroY = toY(0).toFixed(1);
        svg += '<line class="fin-chart-zero" x1="' + padX + '" y1="' + zeroY + '" x2="' + (w - padX) + '" y2="' + zeroY + '"/>';
    }
    lines.forEach(function(line, idx) {
        var pts = toPts(line.points);
        var d = 'M' + pts.join(' L');
        svg += '<g class="inv-chart-line-group" data-idx="' + idx + '">' +
            '<path class="inv-chart-line-hit" d="' + d + '" fill="none" stroke="transparent" stroke-width="18" ' +
            'stroke-linecap="round" stroke-linejoin="round" pointer-events="stroke" ' +
            'onclick="onInvestChartLineClick(event,' + idx + ')" ontouchstart="onInvestChartLineClick(event,' + idx + ')"/>' +
            '<path class="inv-chart-line" d="' + d + '" fill="none" stroke="' + line.color + '" stroke-width="' + line.width + '" ' +
            'stroke-linecap="round" stroke-linejoin="round" opacity="' + (line.opacity || 1) + '" pointer-events="none"/></g>';
    });
    svg += '<circle class="inv-chart-marker" r="4.5" stroke="#fff" stroke-width="1.5" hidden="hidden"/>';
    svg += '</svg>';

    var tooltip = '<div class="inv-chart-tooltip" id="invChartTooltip" hidden></div>';
    var legend = lines.map(function(l, idx) {
        return '<button type="button" class="inv-chart-legend-item" onclick="selectInvestChartLine(' + idx + ',null)">' +
            '<span class="inv-chart-dot" style="background:' + l.color + '"></span>' + esc(l.label) + '</button>';
    }).join('');
    return '<div class="inv-chart-interactive">' +
        '<div class="inv-chart-wrap">' + svg + tooltip + '</div>' +
        '<div class="inv-chart-legend">' + legend + '</div></div>';
}

var FIN_CAT_ICONS = {
    'عمومی': '📦', 'غذا': '🍽', 'حمل\u200cونقل': '🚌', 'خانه': '🏠',
    'قبوض': '💡', 'تفریح': '🎬', 'درمان': '💊', 'آموزش': '📚',
    'حقوق': '💼',
    'سهام': '📈', 'طلا': '🥇', 'رمزارز': '₿', 'سپرده بانکی': '🏦',
    'صندوق': '💹', 'املاک': '🏗', 'سایر': '💎',
};
function finCatIcon(cat) { return FIN_CAT_ICONS[cat] || '💳'; }

function finCatIconType(cat) {
    var invest = window._investCategories || [];
    if (invest.indexOf(cat) !== -1) return 'investment';
    if (cat === 'حقوق') return 'income';
    return 'expense';
}

function finEmoji(emoji, size) {
    size = size || 'md';
    return '<span class="fin-emoji fin-emoji-' + size + '" aria-hidden="true">' + emoji + '</span>';
}

function finIcon(type, content, size) {
    var cls = 'fin-icon fin-icon-' + (type || 'neutral');
    if (size === 'lg') cls += ' fin-icon-lg';
    return '<span class="' + cls + '" aria-hidden="true">' + content + '</span>';
}

function finIconSvg(type, iconName) {
    return '<span class="fin-icon fin-icon-' + (type || 'neutral') + ' fin-icon-svg" aria-hidden="true">' + ico(iconName, 'ico') + '</span>';
}

function finCatIconHtml(cat) {
    return finIcon(finCatIconType(cat), finCatIcon(cat));
}

function finCardTitle(type, icon, label) {
    return '<span class="fin-card-title">' + finIcon(type, icon) + '<span>' + label + '</span></span>';
}

function finTypeInfo(type) {
    if (type === 'income') return { cls: 'income', arrow: '↑', label: 'درآمد' };
    if (type === 'investment') return { cls: 'investment', arrow: '◆', label: 'سرمایه\u200cگذاری' };
    return { cls: 'expense', arrow: '↓', label: 'هزینه' };
}

function finEmptyState(icon, msg, btnLabel, btnOnclick, iconType) {
    var html = '<div class="fin-empty">' + finIcon(iconType || 'neutral', icon, 'lg') + '<p>' + msg + '</p>';
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

/* Home helpers */
function homeGreeting(isToday) {
    if (!isToday) return '';
    var hour = new Date().getHours();
    if (hour >= 5 && hour < 12) return 'صبح بخیر ☀️';
    if (hour >= 12 && hour < 17) return 'ظهر بخیر 🌤';
    if (hour >= 17 && hour < 21) return 'عصر بخیر 🌅';
    return 'شب بخیر 🌙';
}

function homeEffRing(eff, classified) {
    var pct = classified > 0 ? Math.min(100, Math.max(0, eff)) : 0;
    var r = 36;
    var circ = 2 * Math.PI * r;
    var dash = (pct / 100) * circ;
    var gap = circ - dash;
    var stroke = pct >= 70 ? '#6EE7B7' : pct >= 40 ? '#FDE68A' : pct > 0 ? '#FDBA74' : 'rgba(125, 211, 252, 0.28)';
    return '<div class="home-eff-ring" aria-hidden="true">' +
        '<div class="home-eff-glow"></div>' +
        '<svg viewBox="0 0 80 80" class="home-eff-svg">' +
        '<circle cx="40" cy="40" r="' + r + '" fill="none" stroke="rgba(125,211,252,0.14)" stroke-width="5.5"/>' +
        '<circle cx="40" cy="40" r="' + r + '" fill="none" stroke="' + stroke + '" stroke-width="5.5" ' +
        'stroke-linecap="round" stroke-dasharray="' + dash.toFixed(2) + ' ' + gap.toFixed(2) + '" ' +
        'transform="rotate(-90 40 40)" class="home-eff-arc"/>' +
        '</svg>' +
        '<div class="home-eff-center">' +
        '<span class="home-eff-val">' + pd(eff) + '<small>٪</small></span>' +
        '<span class="home-eff-lbl">بازده</span></div></div>';
}

function homeTimeBar(useful, notUseful) {
    var total = (useful || 0) + (notUseful || 0);
    if (total <= 0) return '';
    var uPct = Math.round(useful / total * 100);
    return '<div class="home-time-bar" role="presentation" aria-hidden="true">' +
        '<div class="home-time-seg useful" style="width:' + uPct + '%" title="مفید"></div>' +
        '<div class="home-time-seg not" style="width:' + (100 - uPct) + '%" title="نامفید"></div>' +
        '</div>';
}

function homeFmtSecs(secs) {
    if (!secs || secs <= 0) return '—';
    var h = Math.floor(secs / 3600);
    var m = Math.floor((secs % 3600) / 60);
    if (h > 0) return pd(h) + 'س ' + pd(m) + 'د';
    if (m > 0) return pd(m) + ' دقیقه';
    return pd(secs) + ' ثانیه';
}

function homeStatCard(cls, emoji, lbl, val) {
    return '<div class="home-hero-stat ' + cls + '">' +
        '<div class="home-stat-icon">' + finEmoji(emoji, 'sm') + '</div>' +
        '<div class="home-stat-body"><span class="home-stat-lbl">' + lbl + '</span>' +
        '<span class="home-stat-val">' + val + '</span></div></div>';
}

function onRoleButtonKey(e) {
    if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        e.currentTarget.click();
    }
}

function flushTrackLabelOnBlur(intervalId, input) {
    clearTimeout(_trackLabelTimers[intervalId]);
    delete _trackLabelTimers[intervalId];
    setTrackLabel(intervalId, input.value, true);
    hideTrackLabelSuggestionsDelayed(intervalId);
}

/* Task card */
function taskCard(t, index) {
    var cardCls = 'task-card home-task-card';
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

    var header = '<div class="task-header" role="button" tabindex="0" onclick="action(\'toggle_task\',{id:' + t.id + '})" onkeydown="onRoleButtonKey(event)">' +
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
    var stagger = typeof index === 'number' ? ' style="--home-stagger:' + Math.min(index, 14) + '"' : '';
    return '<div class="' + cardCls + '"' + stagger + '>' + header + detail + '</div>';
}

/* Screens */
function renderHome(h) {
    var taskCount = h.tasks ? h.tasks.length : 0;
    var runningCount = (h.tasks || []).filter(function(t) { return t.is_running; }).length;
    var classified = (h.useful || 0) + (h.not_useful || 0);
    var greeting = homeGreeting(h.is_today);
    var calBtn = '<button type="button" class="icon-btn home-tool-btn" aria-label="تقویم" onclick="action(\'toggle_calendar\')">' + finEmoji('📅', 'xs') + '</button>';
    var recurBtn = '<button type="button" class="icon-btn home-tool-btn wide" onclick="action(\'navigate\',{screen:\'recurring\'})" aria-label="وظایف تکراری">' +
        finEmoji('⭐', 'xs') + ' ' + pd(h.recurring_count) + '</button>';
    var settingsBtn = '<button type="button" class="icon-btn home-tool-btn" aria-label="تنظیمات" onclick="action(\'navigate\',{screen:\'settings\'})">' + finEmoji('⚙️', 'xs') + '</button>';
    var urgentCount = h.urgent_dates_count || 0;
    var badge = urgentCount > 0
        ? ' <span class="urgent-badge">' + pd(urgentCount) + '</span>'
        : '';
    var datesBtn = '<button type="button" class="icon-btn home-tool-btn dates-btn"'
        + ' onclick="action(\'navigate\',{screen:\'important_dates\'})"'
        + ' aria-label="تاریخ\u200cهای مهم">' + finEmoji('🔔', 'xs') + badge + '</button>';
    var addTaskModal = 'showModal({title:\'افزودن تسک\',cmd:\'add_task\',fields:[{label:\'عنوان\',key:\'title\',validate:\'required\'}]})';

    var html = '<div class="home-page">' +
        '<div class="date-header home-header">' +
        '<div class="home-header-orbs" aria-hidden="true">' +
        '<div class="home-orb home-orb-1"></div>' +
        '<div class="home-orb home-orb-2"></div>' +
        '<div class="home-orb home-orb-3"></div></div>' +
        '<div class="home-header-brand">' +
        '<div class="home-header-top">' +
        '<div class="home-brand-mark">' + finEmoji('🏠', 'md') + '</div>' +
        '<div class="home-header-titles">' +
        '<span class="home-header-title">امروز</span>' +
        (greeting ? '<span class="home-greeting">' + greeting + '</span>' : '') +
        '</div>' +
        (h.is_today ? '<span class="home-today-pill"><span class="home-today-dot"></span>امروز</span>' : '') +
        '</div>' +
        '<div class="date-header-row home-date-row">' +
        navArrowBtn('prev', 'action(\'prev_day\')', 'روز قبل') +
        '<span class="date-title home-date-title">' + esc(h.date_label) + '</span>' +
        navArrowBtn('next', 'action(\'next_day\')', 'روز بعد') +
        '</div>' +
        '<div class="date-header-tools home-header-tools">' +
        (h.is_today ? '' : '<button type="button" onclick="action(\'today\')" class="today-btn home-today-btn">امروز</button>') +
        calBtn + recurBtn + datesBtn + settingsBtn +
        '</div></div>' +
        '<div class="home-hero-panel">' +
        '<div class="home-hero-main">' +
        homeEffRing(h.efficiency, classified) +
        '<div class="home-hero-side">' +
        homeTimeBar(h.useful, h.not_useful) +
        '<div class="home-hero-stats">' +
        homeStatCard('useful', '✅', 'مفید', esc(h.useful_fmt)) +
        homeStatCard('not', '⚠️', 'نامفید', esc(h.not_useful_fmt)) +
        homeStatCard('tasks', '📝', 'تسک', pd(taskCount)) +
        homeStatCard('tracked', '⏱', 'کل زمان', homeFmtSecs(classified)) +
        '</div></div></div></div></div>';

    html += '<div class="page-glass-zone">';

    if (h.show_calendar && h.calendar) {
        html += '<div class="home-calendar-wrap">' + renderCalendar(h.calendar, h.date) + '</div>';
    }

    html += '<div class="home-body">';
    if (taskCount > 0 || h.search) {
        html += '<div class="home-sec-head">' +
            '<div class="home-sec-title">' + finEmoji('📋', 'sm') + '<span>تسک\u200cها</span>' +
            '<span class="home-sec-badge">' + pd(taskCount) + '</span></div>' +
            (runningCount > 0
                ? '<span class="home-running-badge"><span class="home-running-dot"></span>' + pd(runningCount) + ' فعال</span>'
                : '') +
            '</div>';
    }

    html += '<div class="search-row home-search-row"><div class="search-wrap home-search-wrap">' + ico('search', 'ico-search') +
        '<input class="search-input home-search-input" placeholder="جستجو در تسک\u200cها..." value="' + esc(h.search) + '" oninput="debounceSearch(this.value)" onblur="flushPendingSearch()" aria-label="جستجو در تسک\u200cها" /></div></div>';

    html += '<div class="task-list home-task-list">';
    if (!(h.tasks && h.tasks.length)) {
        html += '<div class="empty-state home-empty">' +
            '<div class="home-empty-visual" aria-hidden="true">' +
            '<div class="home-empty-ring home-empty-ring-1"></div>' +
            '<div class="home-empty-ring home-empty-ring-2"></div>' +
            '<div class="home-empty-icon">' + finIcon('home', '☑', 'lg') + '</div></div>' +
            '<div class="empty-title">هیچ تسکی وجود ندارد</div>' +
            '<div class="empty-sub">اولین تسک امروز را اضافه کنید و زمان خود را مدیریت کنید</div>' +
            '<button type="button" class="empty-btn home-empty-btn" onclick="' + addTaskModal + '">' + ico('plus', 'ico') + ' افزودن تسک</button></div>';
    } else {
        (h.tasks || []).forEach(function(t, i) { html += taskCard(t, i); });
    }
    html += '</div></div>';

    html += '<div class="home-wellness-wrap">' + renderWellness(h.wellness) + '</div>';
    html += '<div class="section note-section home-note-section">' +
        '<div class="sec-title home-note-title">' + finEmoji('✍️', 'sm') + ' یادداشت روز من</div>' +
        '<textarea class="note-input home-note-input" id="daily-note" placeholder="افکار، اهداف یا یادآوری‌های امروز..." oninput="debounceNote(this.value)" onblur="flushPendingNote()" aria-label="یادداشت روز">' + esc(h.daily_note) + '</textarea>' +
        '<div class="note-saved" id="note-saved" aria-live="polite">ذخیره شد ✓</div></div>';
    html += '</div>';
    if (taskCount > 0) {
        html += '<button type="button" class="home-fab" onclick="' + addTaskModal + '" aria-label="افزودن تسک">' + ico('plus', 'ico') + '</button>';
    }
    return html + '</div>';
}

function renderCalendar(cal, selectedDate) {
    var html = '<div class="calendar-panel"><div class="cal-header">' +
        navArrowBtn('prev', 'action(\'cal_prev_month\')', 'ماه قبل', 'cal-nav') +
        '<span class="cal-title">' + esc(cal.month_name) + ' ' + pd(cal.year) + '</span>' +
        navArrowBtn('next', 'action(\'cal_next_month\')', 'ماه بعد', 'cal-nav') +
        '</div>' +
        '<div class="cal-weekdays">' +
        JALALI_WEEKDAYS.map(function(w) { return '<span>' + w + '</span>'; }).join('') +
        '</div><div class="cal-grid">';
    var wd = cal.weekday_offset || 0;
    for (var i = 0; i < wd; i++) html += '<span class="cal-day cal-day-empty"></span>';
    var now = new Date();
    var todayIso = isoFromGregorian(now.getFullYear(), now.getMonth() + 1, now.getDate());
    (cal.cells || []).forEach(function(c) {
        var cls = 'cal-day';
        if (c.has_data) cls += ' has-data';
        if (c.eff >= 70) cls += ' eff-high';
        if (selectedDate && c.date === selectedDate) cls += ' selected';
        if (c.date === todayIso) cls += ' today';
        html += '<button type="button" class="' + cls + '" onclick="action(\'pick_date\',{date:\'' + c.date + '\'})">' + pd(c.day) + '</button>';
    });
    return html + '</div></div>';
}

function showEditFinance(entry) {
    if (entry && entry.type === 'investment') {
        showInvestmentModal(entry);
        return;
    }
    showModal({
        title: 'ویرایش',
        cmd: 'edit_finance',
        params: { id: entry.id },
        fields: insertSmsField([
            { label: 'عنوان', key: 'title', value: entry.title, validate: 'required' },
            { label: 'مبلغ', key: 'amount', value: String(entry.amount), type: 'number', validate: 'amount' },
            { label: 'دسته', key: 'category', type: 'select', value: entry.category, options: window._categories },
        ]),
    });
}

function showEditFinanceById(id) {
    var entry = (window._finEntries || []).find(function(e) { return e.id == id; });
    if (!entry) {
        showToast('تراکنش یافت نشد — صفحه را تازه کنید', 'error');
        return;
    }
    showEditFinance(entry);
}

function showAddInvestment() {
    showInvestmentModal();
}

function investOptionLabel(item, showUnit) {
    if (!item) return '';
    var text = (item.emoji ? item.emoji + ' ' : '') + (item.label || item.value || '');
    if (showUnit && item.unit) text += ' (' + item.unit + ')';
    return text;
}

function investAssetOptionLabel(market, item) {
    if (!item) return '';
    return investOptionLabel(item, true);
}

function investMarketHint(marketValue) {
    var tax = window._investTaxonomy || {};
    return (tax.market_hints && tax.market_hints[marketValue]) || '';
}

function investAssetUnit(market, assetValue) {
    var tax = window._investTaxonomy || {};
    var units = tax.units || {};
    var key = market + '|' + assetValue;
    if (units[key]) return units[key];
    var assets = (tax.assets && tax.assets[market]) || [];
    for (var i = 0; i < assets.length; i++) {
        if ((assets[i].value || assets[i].label) === assetValue) return assets[i].unit || 'واحد';
    }
    return 'واحد';
}

function investMarketsForRisk(riskValue) {
    var tax = window._investTaxonomy || {};
    var byRisk = tax.markets_by_risk || {};
    if (byRisk[riskValue] && byRisk[riskValue].length) return byRisk[riskValue];
    return tax.markets || [];
}

function updateInvestMarketHint(marketValue) {
    var hintEl = document.getElementById('inv-market-hint');
    if (!hintEl) return;
    var hint = investMarketHint(marketValue);
    hintEl.textContent = hint || '';
    hintEl.style.display = hint ? '' : 'none';
}

function updateInvestQuantityLabel(marketValue, assetValue) {
    var grp = document.getElementById('mfg-quantity');
    if (!grp) return;
    var lbl = grp.querySelector('.modal-label');
    if (!lbl) return;
    var unit = investAssetUnit(marketValue, assetValue);
    lbl.textContent = unit === 'تومان' ? 'مبلغ سپرده (اختیاری)' : 'تعداد (' + unit + ') — اختیاری';
}

function ensureInvestAssetSearchWrap() {
    var grp = document.getElementById('mfg-invest_asset');
    if (!grp) return;
    if (grp.querySelector('.inv-asset-select-wrap')) return;
    var sel = document.getElementById('mf-invest_asset');
    if (!sel) return;
    var wrap = document.createElement('div');
    wrap.className = 'inv-asset-select-wrap';
    var search = document.createElement('input');
    search.type = 'search';
    search.className = 'modal-input inv-asset-search';
    search.id = 'mf-invest_asset_search';
    search.placeholder = 'جستجوی دارایی...';
    search.autocomplete = 'off';
    grp.insertBefore(wrap, sel);
    wrap.appendChild(search);
    wrap.appendChild(sel);
    search.addEventListener('input', function() {
        var marketSel = document.getElementById('mf-invest_market');
        var assetSel = document.getElementById('mf-invest_asset');
        rebuildInvestAssetSelect(
            marketSel ? marketSel.value : '',
            assetSel ? assetSel.value : null,
            search.value
        );
    });
}

function assetMatchesSearch(item, query) {
    if (!query || !String(query).trim()) return true;
    var q = String(query).trim().toLowerCase();
    var parts = [
        item.value || '',
        item.label || '',
        item.subgroup || '',
        item.unit || '',
    ];
    (item.search_tags || []).forEach(function(t) { parts.push(t); });
    return parts.join(' ').toLowerCase().indexOf(q) >= 0;
}

function rebuildInvestMarketSelect(riskValue, selectedMarket) {
    var marketSel = document.getElementById('mf-invest_market');
    if (!marketSel) return;
    var markets = investMarketsForRisk(riskValue);
    if (selectedMarket && !markets.some(function(m) { return (m.value || m.label) === selectedMarket; })) {
        var all = (window._investTaxonomy || {}).markets || [];
        for (var i = 0; i < all.length; i++) {
            if ((all[i].value || all[i].label) === selectedMarket) {
                markets = markets.concat([all[i]]);
                break;
            }
        }
    }
    marketSel.innerHTML = '';
    markets.forEach(function(m) {
        var o = document.createElement('option');
        o.value = m.value || m.label;
        o.textContent = investOptionLabel(m);
        if (selectedMarket && selectedMarket === o.value) o.selected = true;
        marketSel.appendChild(o);
    });
    if (!selectedMarket && marketSel.options.length) marketSel.selectedIndex = 0;
    updateInvestMarketHint(marketSel.value);
    rebuildInvestAssetSelect(marketSel.value, null, null);
}

function appendInvestAssetOptions(assetSel, marketValue, assets, selectedAsset) {
    var subgroups = {};
    var ungrouped = [];
    assets.forEach(function(a) {
        if (a.subgroup) {
            if (!subgroups[a.subgroup]) subgroups[a.subgroup] = [];
            subgroups[a.subgroup].push(a);
        } else {
            ungrouped.push(a);
        }
    });
    function addOption(parent, a) {
        var o = document.createElement('option');
        o.value = a.value || a.label;
        o.textContent = investAssetOptionLabel(marketValue, a);
        if (selectedAsset && selectedAsset === o.value) o.selected = true;
        parent.appendChild(o);
    }
    ungrouped.forEach(function(a) { addOption(assetSel, a); });
    Object.keys(subgroups).sort().forEach(function(sg) {
        var og = document.createElement('optgroup');
        og.label = sg;
        subgroups[sg].forEach(function(a) { addOption(og, a); });
        assetSel.appendChild(og);
    });
}

function rebuildInvestAssetSelect(marketValue, selectedAsset, searchQuery) {
    var assetSel = document.getElementById('mf-invest_asset');
    if (!assetSel) return;
    ensureInvestAssetSearchWrap();
    var tax = window._investTaxonomy || {};
    var allAssets = (tax.assets && tax.assets[marketValue]) || [];
    var assets = allAssets.filter(function(a) { return assetMatchesSearch(a, searchQuery); });
    var prev = selectedAsset || assetSel.value;
    assetSel.innerHTML = '';
    if (!assets.length) {
        var empty = document.createElement('option');
        empty.value = '';
        empty.textContent = searchQuery ? 'نتیجه‌ای یافت نشد' : '—';
        assetSel.appendChild(empty);
        updateInvestQuantityLabel(marketValue, '');
        return;
    }
    appendInvestAssetOptions(assetSel, marketValue, assets, prev);
    if (prev && assets.some(function(a) { return (a.value || a.label) === prev; })) {
        assetSel.value = prev;
    } else if (assetSel.options.length) {
        assetSel.selectedIndex = 0;
    }
    updateInvestQuantityLabel(marketValue, assetSel.value);
}

function bindInvestmentCascade(initial) {
    initial = initial || {};
    var riskSel = document.getElementById('mf-invest_risk');
    var marketSel = document.getElementById('mf-invest_market');
    var marketGrp = document.getElementById('mfg-invest_market');
    if (!riskSel || !marketSel) return;
    if (marketGrp && !document.getElementById('inv-market-hint')) {
        var hintEl = document.createElement('div');
        hintEl.id = 'inv-market-hint';
        hintEl.className = 'inv-market-hint';
        marketGrp.appendChild(hintEl);
    }
    rebuildInvestMarketSelect(riskSel.value, initial.market);
    rebuildInvestAssetSelect(marketSel.value, initial.asset, null);
    riskSel.onchange = function() {
        var searchEl = document.getElementById('mf-invest_asset_search');
        if (searchEl) searchEl.value = '';
        var preserveMarket = initial.isEdit ? marketSel.value : null;
        rebuildInvestMarketSelect(riskSel.value, preserveMarket);
    };
    marketSel.onchange = function() {
        var searchEl = document.getElementById('mf-invest_asset_search');
        if (searchEl) searchEl.value = '';
        updateInvestMarketHint(marketSel.value);
        rebuildInvestAssetSelect(marketSel.value, null, null);
    };
    marketSel.addEventListener('change', function() {
        updateInvestMarketHint(marketSel.value);
    });
    var assetSel = document.getElementById('mf-invest_asset');
    if (assetSel) {
        assetSel.onchange = function() {
            updateInvestQuantityLabel(marketSel.value, assetSel.value);
        };
    }
}

function bindInvestmentFieldSync() {
    var lastTouch = null;
    var lock = false;

    function fieldEl(key) {
        return document.getElementById('mf-' + key);
    }

    function readFieldNum(key, asFloat) {
        var el = fieldEl(key);
        if (!el || el.value === '') return null;
        var n = parseFloat(normalizeNumber(el.value));
        if (isNaN(n)) return null;
        return asFloat ? n : Math.round(n);
    }

    function writeFieldNum(key, val, grouped) {
        var el = fieldEl(key);
        if (!el) return;
        lock = true;
        if (val == null || val === '' || !isFinite(val)) {
            el.value = '';
        } else if (grouped) {
            el.value = formatNumberGrouped(String(Math.round(val)));
        } else {
            var text = val % 1 === 0 ? String(val) : String(parseFloat(val.toFixed(4)));
            el.value = text;
        }
        lock = false;
    }

    function recompute() {
        if (lock) return;
        var qty = readFieldNum('quantity', true);
        var unit = readFieldNum('unit_price', false);
        var amt = readFieldNum('amount', false);
        var cur = readFieldNum('current_unit_price', false);
        var pnl = readFieldNum('pnl_percent', true);

        if (lastTouch === 'quantity' || lastTouch === 'unit_price') {
            if (qty > 0 && unit > 0) writeFieldNum('amount', qty * unit, true);
        } else if (lastTouch === 'amount') {
            if (qty > 0 && amt > 0) writeFieldNum('unit_price', amt / qty, true);
            else if (unit > 0 && amt > 0) writeFieldNum('quantity', amt / unit, false);
        }

        if (unit > 0) {
            if (lastTouch === 'current_unit_price' && cur != null) {
                writeFieldNum('pnl_percent', ((cur - unit) / unit) * 100, false);
            } else if (lastTouch === 'pnl_percent' && pnl != null) {
                writeFieldNum('current_unit_price', unit * (1 + pnl / 100), true);
            } else if (lastTouch === 'unit_price') {
                if (cur != null) writeFieldNum('pnl_percent', ((cur - unit) / unit) * 100, false);
                else if (pnl != null) writeFieldNum('current_unit_price', unit * (1 + pnl / 100), true);
            }
        }
    }

    ['quantity', 'unit_price', 'amount', 'current_unit_price', 'pnl_percent'].forEach(function(key) {
        var el = fieldEl(key);
        if (!el) return;
        el.addEventListener('input', function() {
            lastTouch = key;
            recompute();
        });
    });

    var dirSel = fieldEl('invest_direction');
    if (dirSel) {
        dirSel.addEventListener('change', syncModalConditionalFields);
    }

    var unit = readFieldNum('unit_price', false);
    var cur = readFieldNum('current_unit_price', false);
    if (unit > 0 && cur != null && !readFieldNum('pnl_percent', true)) {
        writeFieldNum('pnl_percent', ((cur - unit) / unit) * 100, false);
    }
}

function buildInvestmentFields(entry) {
    entry = entry || {};
    var meta = entry.investment_meta || {};
    var tax = window._investTaxonomy || { risks: [], markets: [], assets: {} };
    var riskVal = meta.risk || (tax.risks[0] && tax.risks[0].value) || '';
    var marketsForRisk = investMarketsForRisk(riskVal);
    var marketVal = meta.market || (marketsForRisk[0] && marketsForRisk[0].value) || '';
    var assetVal = meta.asset || '';
    var direction = entry.investment_direction || 'buy';
    var pnlVal = '';
    if (entry.unit_price > 0 && entry.current_unit_price > 0) {
        pnlVal = String(((entry.current_unit_price - entry.unit_price) / entry.unit_price * 100).toFixed(2));
    }
    var now = new Date();
    var todayIso = isoFromGregorian(now.getFullYear(), now.getMonth() + 1, now.getDate());
    var invState = (window._lastState && window._lastState.investments) || {};
    var invFilter = invState.filter || {};
    var defaultDate = todayIso;
    if (invFilter.mode === 'month' && invFilter.is_current_month) {
        defaultDate = todayIso;
    } else if (invFilter.start) {
        defaultDate = invFilter.start;
    }
    return [
        { label: 'تاریخ', key: 'date', type: 'jalali-date', value: entry.date || defaultDate, validate: 'required' },
        { label: 'نوع تراکنش', key: 'invest_direction', type: 'select', value: direction, validate: 'required',
            options: [
                { value: 'buy', label: '📥 خرید / واریز' },
                { value: 'sell', label: '📤 فروش / برداشت' },
            ] },
        { label: 'عنوان (اختیاری)', key: 'title', value: entry.title || '', placeholder: 'مثلاً خرید دوره\u200cای' },
        { label: 'سطح ریسک', key: 'invest_risk', type: 'select', value: riskVal, validate: 'required',
            options: (tax.risks || []).map(function(r) { return { value: r.value, label: investOptionLabel(r) }; }) },
        { label: 'نوع بازار', key: 'invest_market', type: 'select', value: marketVal, validate: 'required',
            options: marketsForRisk.map(function(m) { return { value: m.value, label: investOptionLabel(m) }; }) },
        { label: 'انتخاب دارایی', key: 'invest_asset', type: 'select', value: assetVal, validate: 'required', options: [] },
        { label: 'تعداد (اختیاری)', key: 'quantity', type: 'number', value: entry.quantity != null ? String(entry.quantity) : '', placeholder: 'مثلاً 2' },
        { label: 'قیمت خرید واحد (تومان)', key: 'unit_price', type: 'number', grouped: true,
            value: entry.unit_price != null ? String(entry.unit_price) : '', placeholder: 'مثلاً 1500000' },
        { label: 'قیمت فعلی واحد (تومان)', key: 'current_unit_price', type: 'number', grouped: true,
            showWhen: { key: 'invest_direction', value: 'buy' },
            value: entry.current_unit_price != null ? String(entry.current_unit_price) : '', placeholder: 'قیمت الان بازار' },
        { label: 'درصد سود/ضرر', key: 'pnl_percent', type: 'number',
            showWhen: { key: 'invest_direction', value: 'buy' },
            value: pnlVal, placeholder: 'مثلاً ۱۲ یا -۵' },
        { label: 'مبلغ (تومان)', key: 'amount', type: 'number', validate: 'amount', grouped: true,
            value: entry.amount ? String(entry.amount) : '' },
    ];
}

function showInvestmentModal(entry) {
    var isEdit = !!(entry && entry.id);
    var meta = (entry && entry.investment_meta) || {};
    showModal({
        title: isEdit ? 'ویرایش سرمایه\u200cگذاری' : 'ثبت سرمایه\u200cگذاری',
        cmd: isEdit ? 'edit_finance' : 'add_finance',
        params: isEdit ? { id: entry.id, type: 'investment' } : { type: 'investment' },
        fields: insertSmsField(buildInvestmentFields(entry)),
        investmentCascade: Object.assign({}, meta, { isEdit: isEdit }),
    });
}

function showEditInvestmentById(id) {
    var pool = window._investAllEntries || window._investEntries || [];
    var entry = pool.find(function(e) { return e.id == id; });
    if (!entry) {
        showToast('سرمایه\u200cگذاری یافت نشد — صفحه را تازه کنید', 'error');
        return;
    }
    showInvestmentModal(entry);
}

function renderInvestPeriodFilter(d) {
    var f = d.filter || { mode: 'all', label: 'همه' };
    var mode = f.mode || 'all';
    var isCurrentMonth = mode === 'month' && f.is_current_month;
    var html = '<div class="inv-period-filter">' +
        '<div class="inv-period-chips">' +
        '<button type="button" class="inv-period-chip' + (mode === 'all' ? ' active' : '') +
            '" onclick="action(\'invest_set_filter\',{mode:\'all\'})">همه</button>' +
        '<button type="button" class="inv-period-chip' + (isCurrentMonth ? ' active' : '') +
            '" onclick="action(\'invest_set_filter\',{mode:\'month\'})">این ماه</button>' +
        '<button type="button" class="inv-period-chip' + (mode === 'month' && !isCurrentMonth ? ' active' : '') +
            '" onclick="showInvestMonthFilter()">📅 ماه</button>' +
        '<button type="button" class="inv-period-chip' + (mode === 'range' ? ' active' : '') +
            '" onclick="showInvestRangeFilter()">📆 بازه</button>' +
        '</div>';
    if (mode !== 'all' && f.label) {
        html += '<div class="inv-period-label">' + esc(f.label) + '</div>';
    }
    return html + '</div>';
}

function showInvestMonthFilter() {
    var d = (window._lastState && window._lastState.investments) || {};
    var f = d.filter || {};
    var now = new Date();
    var cur = toJalaali(now.getFullYear(), now.getMonth() + 1, now.getDate());
    var yearVal = f.year || cur.jy;
    var monthVal = f.month || cur.jm;
    var years = [];
    for (var y = cur.jy - 5; y <= cur.jy + 1; y++) years.push(y);
    var monthOpts = [];
    for (var m = 1; m <= 12; m++) {
        monthOpts.push({ value: String(m), label: JALALI_MONTH_NAMES[m] });
    }
    showModal({
        title: 'فیلتر بر اساس ماه',
        cmd: 'invest_set_filter',
        params: { mode: 'month' },
        fields: [
            { label: 'سال', key: 'year', type: 'select', validate: 'required', value: String(yearVal),
                options: years.map(function(y) { return { value: String(y), label: pd(y) }; }) },
            { label: 'ماه', key: 'month', type: 'select', validate: 'required', value: String(monthVal),
                options: monthOpts },
        ],
    });
}

function showInvestRangeFilter() {
    var d = (window._lastState && window._lastState.investments) || {};
    var f = d.filter || {};
    var now = new Date();
    var todayIso = isoFromGregorian(now.getFullYear(), now.getMonth() + 1, now.getDate());
    showModal({
        title: 'فیلتر بازه زمانی',
        cmd: 'invest_set_filter',
        params: { mode: 'range' },
        fields: [
            { label: 'از تاریخ', key: 'start', type: 'jalali-date', validate: 'required',
                value: f.start || todayIso },
            { label: 'تا تاریخ', key: 'end', type: 'jalali-date', validate: 'required',
                value: f.end || todayIso },
        ],
    });
}

window._investFilter = window._investFilter || { risk: '', market: '', asset: '' };

function setInvestFilter(key, value) {
    if (!window._investFilter) window._investFilter = { risk: '', market: '', asset: '' };
    var f = window._investFilter;
    var next = f[key] === value ? '' : value;
    f[key] = next;
    if (key === 'risk') {
        f.market = '';
        f.asset = '';
    } else if (key === 'market') {
        f.asset = '';
    }
    if (window._lastState) renderApp(window._lastState);
}

function filterInvestEntriesByPeriod(entries, filter) {
    filter = filter || {};
    if (filter.mode === 'all' || !filter.start) return entries || [];
    var start = filter.start;
    var end = filter.end || start;
    return (entries || []).filter(function(e) {
        var d = e.date || '';
        return d >= start && d <= end;
    });
}

function filterInvestEntries(entries) {
    var f = window._investFilter || {};
    return (entries || []).filter(function(e) {
        var m = e.investment_meta || {};
        if (f.risk && m.risk !== f.risk) return false;
        if (f.market && m.market !== f.market) return false;
        if (f.asset && m.asset !== f.asset) return false;
        return true;
    });
}

function renderInvestFilterChips(scope) {
    var tax = window._investTaxonomy || { risks: [], markets: [], assets: {} };
    var f = window._investFilter || {};
    var scopeCls = scope ? ' inv-filter-row-' + scope : '';
    var html = '<div class="inv-filter-row' + scopeCls + '">';
    (tax.risks || []).forEach(function(r) {
        var val = r.value || r.label;
        var active = f.risk === val ? ' active' : '';
        html += '<button type="button" class="inv-filter-chip' + active + '" onclick="setInvestFilter(\'risk\',\'' + escJs(val) + '\')">' + esc(investOptionLabel(r)) + '</button>';
    });
    html += '<span class="inv-filter-sep"></span>';
    var markets = f.risk ? investMarketsForRisk(f.risk) : (tax.markets || []);
    markets.forEach(function(m) {
        var val = m.value || m.label;
        var active = f.market === val ? ' active' : '';
        html += '<button type="button" class="inv-filter-chip' + active + '" onclick="setInvestFilter(\'market\',\'' + escJs(val) + '\')">' + esc(investOptionLabel(m)) + '</button>';
    });
    var assetSet = {};
    if (f.market && tax.assets && tax.assets[f.market]) {
        (tax.assets[f.market] || []).forEach(function(a) {
            var val = a.value || a.label;
            assetSet[val] = a.emoji || '💎';
        });
    }
    (window._investEntries || []).forEach(function(e) {
        var m = e.investment_meta || {};
        if (f.market && m.market !== f.market) return;
        if (f.risk && m.risk !== f.risk) return;
        if (m.asset) assetSet[m.asset] = m.asset_emoji || assetSet[m.asset] || '💎';
    });
    var assetKeys = Object.keys(assetSet);
    if (assetKeys.length) {
        html += '<span class="inv-filter-sep"></span>';
        assetKeys.sort().forEach(function(asset) {
            var active = f.asset === asset ? ' active' : '';
            html += '<button type="button" class="inv-filter-chip' + active + '" onclick="setInvestFilter(\'asset\',\'' + escJs(asset) + '\')">' +
                esc((assetSet[asset] || '💎') + ' ' + asset) + '</button>';
        });
    }
    if (f.risk || f.market || f.asset) {
        html += '<button type="button" class="inv-filter-clear" onclick="window._investFilter={risk:\'\',market:\'\',asset:\'\'};renderApp(window._lastState)">پاک کردن</button>';
    }
    html += '</div>';
    return html;
}

function showSetInvestmentGoal(currentAmount) {
    var inv = (window._lastState && window._lastState.investments) || {};
    var f = inv.filter || {};
    if (f.mode !== 'month') {
        showToast('ابتدا فیلتر «این ماه» یا یک ماه مشخص را انتخاب کنید', 'error');
        return;
    }
    showModal({
        title: 'هدف واریز ماهانه',
        cmd: 'set_investment_goal',
        fields: [
            { label: 'حداقل واریز ماه (تومان)', key: 'amount', type: 'number', validate: 'budget',
                value: currentAmount !== undefined && currentAmount !== null ? String(currentAmount) : '', placeholder: '۰' },
        ],
    });
}

window._investTab = window._investTab || 'summary';

function setInvestTab(tab) {
    window._investTab = tab;
    if (window._lastState) renderApp(window._lastState);
}

function renderInvestTabs(active) {
    active = active || window._investTab || 'summary';
    return '<div class="inv-tabs">' +
        '<button type="button" class="inv-tab' + (active === 'summary' ? ' active' : '') +
            '" onclick="setInvestTab(\'summary\')">خلاصه</button>' +
        '<button type="button" class="inv-tab' + (active === 'transactions' ? ' active' : '') +
            '" onclick="setInvestTab(\'transactions\')">تراکنش\u200cها</button>' +
        '</div>';
}

function showUpdateAssetPrice(market, asset, currentPrice) {
    showModal({
        title: 'به\u200cروزرسانی قیمت — ' + asset,
        cmd: 'set_investment_asset_price',
        params: { market: market, asset: asset },
        fields: [
            { label: 'قیمت فعلی واحد (تومان)', key: 'price', type: 'number', validate: 'amount', grouped: true,
                value: currentPrice ? String(currentPrice) : '', placeholder: 'قیمت بازار' },
        ],
    });
}

function renderInvestPositions(positions) {
    positions = positions || [];
    if (!positions.length) {
        return '<div class="fin-card inv-card fin-card-animate" style="--fin-card-delay:1">' +
            '<div class="fin-card-head">' + finCardTitle('investment', '💼', 'دارایی\u200cهای من') + '</div>' +
            finEmptyState('💼', 'با ثبت خرید، موقعیت دارایی اینجا نمایش داده می\u200cشود', '+ ثبت سرمایه\u200cگذاری', 'showAddInvestment()', 'investment') +
            '</div>';
    }
    var html = '<div class="fin-card inv-card fin-card-animate" style="--fin-card-delay:1">' +
        '<div class="fin-card-head">' + finCardTitle('investment', '💼', 'دارایی\u200cهای من') +
        '<span class="fin-card-badge">' + pd(positions.length) + '</span></div>' +
        '<div class="inv-pos-list">';
    positions.forEach(function(p, idx) {
        var pnlLine = '';
        if (p.unrealized_pnl_fmt && p.has_market_price) {
            pnlLine = '<div class="inv-pos-pnl ' + (p.pnl_positive ? 'profit' : 'loss') + '">' +
                esc(p.unrealized_pnl_fmt) +
                (p.unrealized_pnl_pct_fmt ? ' (' + esc(p.unrealized_pnl_pct_fmt) + ')' : '') +
                '</div>';
        } else if (p.qty_display || p.quantity_fmt) {
            pnlLine = '<div class="inv-pos-qty">' + esc(p.qty_display || p.quantity_fmt) + '</div>';
        }
        html += '<div class="inv-pos-item" style="--fin-stagger:' + idx + '">' +
            '<div class="inv-pos-icon">' + finEmoji(p.asset_emoji || '💎', 'sm') + '</div>' +
            '<div class="inv-pos-body">' +
            '<div class="inv-pos-title">' + esc(p.display || p.asset) + '</div>' +
            pnlLine +
            '<div class="inv-pos-cost">بهای تمام\u200cشده: ' + esc(p.cost_basis_fmt) + '</div>' +
            '</div>' +
            '<div class="inv-pos-right">' +
            '<div class="inv-pos-val">' + esc(p.estimated_value_fmt) + '</div>' +
            '<button type="button" class="inv-pos-price-btn" onclick="showUpdateAssetPrice(\'' +
                escJs(p.market) + '\',\'' + escJs(p.asset) + '\',' + (p.current_unit_price || 0) + ')">قیمت</button>' +
            '</div></div>';
    });
    return html + '</div></div>';
}

function renderInvestActions(d) {
    var f = d.filter || {};
    var goalBtn = f.mode === 'month'
        ? '<button type="button" class="inv-action-chip" onclick="showSetInvestmentGoal(' + (d.goal || 0) + ')">🎯 هدف ماه</button>'
        : '';
    return '<div class="inv-actions">' +
        '<button type="button" class="inv-add-btn" onclick="showAddInvestment()">' +
        ico('plus', 'ico') + '<span>سرمایه\u200cگذاری جدید</span></button>' +
        goalBtn +
        '<button type="button" class="inv-action-chip" onclick="showAllocationTargets()">📊 تخصیص</button>' +
        '<button type="button" class="inv-action-chip" onclick="showAddInvestmentAsset()">+ دارایی</button>' +
        '<button type="button" class="inv-action-chip" onclick="showManageCustomAssets()">⚙️ دارایی\u200cها</button>' +
        '<button type="button" class="inv-action-chip" onclick="exportInvestmentsCsv()">⬇ CSV</button>' +
        '</div>';
}

function showAddInvestmentAsset() {
    var tax = window._investTaxonomy || { markets: [], market_hints: {} };
    var markets = tax.markets || [];
    showModal({
        title: 'افزودن دارایی سفارشی',
        cmd: 'add_investment_asset',
        fields: [
            { label: 'نوع بازار', key: 'market', type: 'select', validate: 'required',
                options: markets.map(function(m) { return { value: m.value, label: investOptionLabel(m) }; }) },
            { label: 'نام دارایی', key: 'name', validate: 'required', placeholder: 'مثلاً فملی' },
            { label: 'واحد (اختیاری)', key: 'unit', placeholder: 'مثلاً سهم، گرم، دستگاه' },
            { label: 'ایموجی (اختیاری)', key: 'emoji', placeholder: '💎' },
        ],
    });
}

function showManageCustomAssets() {
    var assets = (window._lastState && window._lastState.investments && window._lastState.investments.custom_assets) || [];
    if (!assets.length) {
        showToast('دارایی سفارشی ثبت نشده', 'error');
        return;
    }
    var html = '<div class="inv-custom-list">';
    assets.forEach(function(a) {
        html += '<div class="inv-custom-item">' +
            '<div class="inv-custom-info">' +
            finEmoji(a.emoji || '💎', 'sm') +
            '<span class="inv-custom-name">' + esc(a.label || a.value) + '</span>' +
            '<span class="inv-custom-market">' + esc(a.market) + '</span>' +
            '</div>' +
            '<div class="inv-custom-actions">' +
            '<button type="button" class="inv-custom-btn" onclick="showEditCustomAsset(\'' +
                escJs(a.market) + '\',\'' + escJs(a.value) + '\',\'' + escJs(a.label || a.value) + '\',\'' +
                escJs(a.emoji || '💎') + '\')">ویرایش</button>' +
            '<button type="button" class="inv-custom-btn danger" onclick="confirmDeleteCustomAsset(\'' +
                escJs(a.market) + '\',\'' + escJs(a.value) + '\',\'' + escJs(a.label || a.value) + '\')">حذف</button>' +
            '</div></div>';
    });
    html += '</div>';
    showModal({
        title: 'دارایی\u200cهای سفارشی',
        html: html,
        hideSubmit: true,
    });
}

function showEditCustomAsset(market, value, label, emoji) {
    closeModal();
    showModal({
        title: 'ویرایش دارایی — ' + label,
        cmd: 'edit_investment_asset',
        params: { market: market, value: value },
        fields: [
            { label: 'نام نمایشی', key: 'label', validate: 'required', value: label || value },
            { label: 'شناسه (انگلیسی/فارسی)', key: 'new_value', value: value, placeholder: value },
            { label: 'ایموجی', key: 'emoji', value: emoji || '💎' },
        ],
    });
}

function confirmDeleteCustomAsset(market, value, label) {
    closeModal();
    if (!confirm('حذف دارایی «' + label + '»؟\n(فقط اگر در تراکنش استفاده نشده باشد)')) return;
    action('delete_investment_asset', { market: market, value: value });
}

function showAllocationTargets() {
    var inv = (window._lastState && window._lastState.investments) || {};
    var positions = inv.positions || [];
    var allocation = inv.allocation || [];
    var targetsTotal = inv.allocation_targets_total || 0;
    var html = '';
    if (allocation.length) {
        html += '<div class="inv-alloc-list">';
        allocation.forEach(function(a) {
            if (!a.target_pct) return;
            var driftCls = a.over_target ? ' over' : (a.under_target ? ' under' : '');
            html += '<div class="inv-alloc-item' + driftCls + '">' +
                '<div class="inv-alloc-head">' +
                finEmoji(a.asset_emoji || '💎', 'sm') +
                '<span class="inv-alloc-name">' + esc(a.asset) + '</span>' +
                '<span class="inv-alloc-pcts">' + pd(a.actual_pct) + '٪ / ' + pd(a.target_pct) + '٪</span>' +
                '</div>' +
                '<div class="inv-alloc-bar">' +
                '<div class="inv-alloc-fill actual" style="width:' + Math.min(a.actual_pct, 100) + '%"></div>' +
                '<div class="inv-alloc-marker" style="left:' + Math.min(a.target_pct, 100) + '%"></div>' +
                '</div>' +
                (a.drift_fmt ? '<div class="inv-alloc-drift">انحراف: ' + esc(a.drift_fmt) + '</div>' : '') +
                '<button type="button" class="inv-alloc-edit" onclick="showSetAllocationTarget(\'' +
                    escJs(a.market) + '\',\'' + escJs(a.asset) + '\',' + (a.target_pct || 0) + ')">ویرایش</button>' +
                '</div>';
        });
        html += '</div>';
    }
    if (targetsTotal > 100) {
        html += '<div class="inv-alloc-warn">⚠️ جمع اهداف ' + pd(targetsTotal) + '٪ است — باید حداکثر ۱۰۰٪ باشد</div>';
    }
    html += renderRebalanceSection(inv.rebalance || {}, false);
    html += '<button type="button" class="inv-alloc-add" onclick="showSetAllocationTarget()">+ هدف تخصیص جدید</button>';
    showModal({
        title: 'اهداف تخصیص پرتفوی',
        html: html,
        hideSubmit: true,
    });
}

function showSetAllocationTarget(market, asset, currentPct) {
    closeModal();
    var inv = (window._lastState && window._lastState.investments) || {};
    var positions = inv.positions || [];
    var tax = window._investTaxonomy || { assets: {} };
    var fields = [
        { label: 'هدف تخصیص (٪)', key: 'pct', type: 'number', validate: 'required',
            value: currentPct !== undefined && currentPct !== null ? String(currentPct) : '', placeholder: 'مثلاً ۳۰' },
    ];
    if (!market || !asset) {
        var marketOpts = (tax.markets || []).map(function(m) {
            return { value: m.value, label: investOptionLabel(m) };
        });
        fields.unshift(
            { label: 'نوع بازار', key: 'alloc_market', type: 'select', validate: 'required', options: marketOpts },
            { label: 'دارایی', key: 'alloc_asset', type: 'select', validate: 'required', options: [] }
        );
        showModal({
            title: 'هدف تخصیص جدید',
            cmd: 'set_investment_allocation_target',
            params: {},
            fields: fields,
            allocationCascade: true,
        });
        return;
    }
    showModal({
        title: market && asset ? 'هدف تخصیص — ' + asset : 'هدف تخصیص جدید',
        cmd: 'set_investment_allocation_target',
        params: market && asset ? { market: market, asset: asset } : {},
        fields: fields,
    });
}

function bindAllocationCascade() {
    var marketSel = document.getElementById('mf-alloc_market');
    var assetSel = document.getElementById('mf-alloc_asset');
    if (!marketSel || !assetSel) return;
    function rebuild() {
        var tax = window._investTaxonomy || { assets: {} };
        var assets = (tax.assets && tax.assets[marketSel.value]) || [];
        var prev = assetSel.value;
        assetSel.innerHTML = '';
        appendInvestAssetOptions(assetSel, marketSel.value, assets, prev);
        if (!assetSel.options.length) {
            var empty = document.createElement('option');
            empty.value = '';
            empty.textContent = '—';
            assetSel.appendChild(empty);
        }
    }
    rebuild();
    marketSel.onchange = rebuild;
}

function renderAllocationCard(allocation, totals) {
    allocation = (allocation || []).filter(function(a) { return a.target_pct > 0; });
    if (!allocation.length) return '';
    var html = '<div class="fin-card inv-card fin-card-animate" style="--fin-card-delay:2">' +
        '<div class="fin-card-head">' + finCardTitle('investment', '🎯', 'هدف تخصیص') +
        '<button type="button" class="inv-card-link" onclick="showAllocationTargets()">مدیریت</button></div>' +
        '<div class="inv-alloc-list compact">';
    allocation.slice(0, 5).forEach(function(a) {
        var driftCls = a.over_target ? ' over' : (a.under_target ? ' under' : '');
        html += '<div class="inv-alloc-item' + driftCls + '">' +
            '<div class="inv-alloc-head">' +
            finEmoji(a.asset_emoji || '💎', 'sm') +
            '<span class="inv-alloc-name">' + esc(a.asset) + '</span>' +
            '<span class="inv-alloc-pcts">' + pd(a.actual_pct) + '٪ ← ' + pd(a.target_pct) + '٪</span>' +
            '</div>' +
            '<div class="inv-alloc-bar">' +
            '<div class="inv-alloc-fill actual" style="width:' + Math.min(a.actual_pct, 100) + '%"></div>' +
            '<div class="inv-alloc-marker" style="left:' + Math.min(a.target_pct, 100) + '%"></div>' +
            '</div></div>';
    });
    html += '</div>';
    html += renderRebalanceSection((window._lastState && window._lastState.investments && window._lastState.investments.rebalance) || {}, true);
    return html + '</div>';
}

function renderRebalanceSection(rebalance, compact) {
    rebalance = rebalance || {};
    var items = (rebalance.items || []).filter(function(i) {
        return i.action === 'buy' || i.action === 'sell';
    });
    if (!items.length) {
        if (rebalance.targets_valid === false) return '';
        if ((rebalance.portfolio_value || 0) <= 0) return '';
        return compact ? '' : '<div class="inv-rebalance-ok">✓ سبد با اهداف تخصیص هم‌خوان است</div>';
    }
    var html = '<div class="inv-rebalance' + (compact ? ' compact' : '') + '">';
    if (!compact) {
        html += '<div class="inv-rebalance-head">' + finEmoji('⚖️', 'sm') + ' پیشنهاد ریبالانس</div>';
    } else {
        html += '<div class="inv-rebalance-head compact">⚖️ پیشنهاد ریبالانس</div>';
    }
    html += '<div class="inv-rebalance-list">';
    items.forEach(function(i) {
        var cls = i.action === 'buy' ? ' buy' : ' sell';
        html += '<div class="inv-rebalance-item' + cls + '">' +
            '<span class="inv-rebalance-asset">' + finEmoji(i.asset_emoji || '💎', 'sm') + ' ' + esc(i.asset) + '</span>' +
            '<span class="inv-rebalance-action">' + esc(i.action_label) + '</span>' +
            '<span class="inv-rebalance-amt">' + esc(i.amount_fmt) + '</span>' +
            '</div>';
    });
    html += '</div>';
    html += '<div class="inv-rebalance-summary">';
    if (rebalance.total_buy > 0) {
        html += '<span class="inv-rebalance-sum buy">خرید کل: ' + esc(rebalance.total_buy_fmt) + '</span>';
    }
    if (rebalance.total_sell > 0) {
        html += '<span class="inv-rebalance-sum sell">فروش کل: ' + esc(rebalance.total_sell_fmt) + '</span>';
    }
    if (rebalance.net_cash_needed > 0) {
        html += '<span class="inv-rebalance-sum need">نیاز نقد: ' + esc(rebalance.net_cash_needed_fmt) + '</span>';
    } else if (rebalance.can_rebalance) {
        html += '<span class="inv-rebalance-sum ok">✓ با موجودی فعلی قابل اجراست</span>';
    }
    html += '</div></div>';
    return html;
}

function exportInvestmentsCsv() {
    var inv = (window._lastState && window._lastState.investments) || {};
    var source = filterInvestEntriesByPeriod(
        window._investAllEntries || window._investEntries || [],
        inv.filter || {}
    );
    var entries = filterInvestEntries(source);
    if (!entries.length) {
        showToast('رکوردی برای خروجی وجود ندارد', 'error');
        return;
    }
    var rows = [['تاریخ', 'عنوان', 'نوع', 'ریسک', 'بازار', 'دارایی', 'تعداد', 'قیمت خرید', 'قیمت فعلی', 'سود/ضرر', 'مبلغ'].join(',')];
    entries.forEach(function(e) {
        var m = e.investment_meta || {};
        rows.push([
            e.date_label || e.date || '',
            e.title || '',
            e.is_sell ? 'فروش' : 'خرید',
            m.risk || '',
            m.market || '',
            m.asset || '',
            e.quantity != null ? e.quantity : '',
            e.unit_price != null ? e.unit_price : '',
            e.current_unit_price != null ? e.current_unit_price : '',
            e.pnl_fmt || '',
            e.amount || '',
        ].map(function(v) { return '"' + String(v).replace(/"/g, '""') + '"'; }).join(','));
    });
    var blob = new Blob(['\ufeff' + rows.join('\n')], { type: 'text/csv;charset=utf-8;' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = 'investments.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast('فایل CSV دانلود شد');
}

function findInvestAssetEmoji(assetName) {
    var tax = window._investTaxonomy || {};
    var markets = tax.assets || {};
    var key;
    for (key in markets) {
        if (!Object.prototype.hasOwnProperty.call(markets, key)) continue;
        var list = markets[key] || [];
        for (var i = 0; i < list.length; i++) {
            if (list[i].value === assetName || list[i].label === assetName) {
                return list[i].emoji || '💎';
            }
        }
    }
    return '💎';
}

function investEntryDisplay(e) {
    if (e.category_display) return e.category_display;
    if (e.investment_meta && e.investment_meta.display) return e.investment_meta.display;
    return e.category || '—';
}

function investEntryIcon(e) {
    var m = e.investment_meta || {};
    return m.asset_emoji || findInvestAssetEmoji(e.category) || '💎';
}

function showAddFinance(type) {
    if (type === 'investment') {
        showInvestmentModal();
        return;
    }
    var titles = { income: 'افزودن درآمد', expense: 'افزودن هزینه', investment: 'ثبت سرمایه\u200cگذاری' };
    var cats = window._categories || [];
    showModal({
        title: titles[type] || 'ثبت مالی',
        cmd: 'add_finance',
        params: { type: type },
        fields: insertSmsField([
            { label: 'عنوان', key: 'title', validate: 'required', placeholder: '' },
            { label: 'مبلغ (تومان)', key: 'amount', type: 'number', validate: 'amount' },
            { label: 'دسته', key: 'category', type: 'select', value: 'عمومی', options: cats },
        ]),
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
        fields: insertSmsField(fields),
    });
}

function renderWellness(w) {
    w = w || {};
    var moodLabels = ['خیلی بد', 'بد', 'نه چندان خوب', 'معمولی', 'نسبتاً خوب', 'خوب', 'خیلی خوب', 'عالی', 'فوق‌العاده', 'عاشقانه'];
    var moods = '';
    (window._moodEmojis || []).forEach(function(emoji, i) {
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

function analyticsEffChart(points, w, h) {
    if (!points || !points.length) return '';
    var max = Math.max.apply(null, points.concat([1]));
    var min = 0;
    var range = max - min || 1;
    var n = points.length;
    var padT = 14, padB = 8, padX = 8;
    function toY(v) {
        return padT + (h - padT - padB) * (1 - (v - min) / range);
    }
    function toPts(arr) {
        return arr.map(function(v, i) {
            return (padX + i * (w - padX * 2) / (n - 1 || 1)).toFixed(1) + ',' + toY(v).toFixed(1);
        });
    }
    var pts = toPts(points);
    var linePts = pts.join(' ');
    var areaPath = 'M' + pts[0];
    for (var i = 1; i < pts.length; i++) areaPath += ' L' + pts[i];
    var baseY = (h - padB).toFixed(1);
    areaPath += ' L' + pts[pts.length - 1].split(',')[0] + ',' + baseY;
    areaPath += ' L' + pts[0].split(',')[0] + ',' + baseY + ' Z';
    var last = pts[pts.length - 1].split(',');
    var svg = '<svg class="analytics-eff-chart" viewBox="0 0 ' + w + ' ' + h + '" preserveAspectRatio="none">' +
        '<defs>' +
        '<linearGradient id="anEffGrad" x1="0" y1="0" x2="0" y2="1">' +
        '<stop offset="0%" stop-color="#A78BFA" stop-opacity="0.42"/>' +
        '<stop offset="100%" stop-color="#A78BFA" stop-opacity="0"/>' +
        '</linearGradient>' +
        '<filter id="anEffGlow" x="-20%" y="-20%" width="140%" height="140%">' +
        '<feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>' +
        '</filter></defs>';
    for (var g = 0; g <= 3; g++) {
        var gy = padT + (h - padT - padB) * g / 3;
        svg += '<line class="analytics-chart-grid" x1="' + padX + '" y1="' + gy.toFixed(1) + '" x2="' + (w - padX) + '" y2="' + gy.toFixed(1) + '"/>';
    }
    svg += '<path class="analytics-chart-area" d="' + areaPath + '" fill="url(#anEffGrad)"/>';
    svg += '<polyline class="analytics-chart-line" fill="none" stroke="#C4B5FD" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round" points="' + linePts + '" filter="url(#anEffGlow)"/>';
    svg += '<circle class="analytics-chart-dot" cx="' + last[0] + '" cy="' + last[1] + '" r="3.5" fill="#E9D5FF" stroke="#7C3AED" stroke-width="1.5"/>';
    svg += '</svg>';
    return '<div class="analytics-chart-wrap">' + svg + '</div>';
}

function analyticsHeatmapCard(heatmap) {
    if (!heatmap || !heatmap.length) return '';
    var cells = heatmap.map(function(d) {
        var cls = 'analytics-hm-cell';
        if (d.eff >= 70) cls += ' hm-high';
        else if (d.eff >= 40) cls += ' hm-mid';
        else if (d.total > 0) cls += ' hm-low';
        else cls += ' hm-empty';
        var tip = esc(d.date);
        if (d.total > 0) tip += ' · ' + pd(d.eff) + '٪';
        return '<div class="' + cls + '" title="' + tip + '"></div>';
    }).join('');
    return '<div class="analytics-heatmap">' + cells + '</div>' +
        '<div class="analytics-hm-legend">' +
        '<span class="analytics-hm-leg-item"><span class="analytics-hm-leg-dot hm-empty"></span>بدون فعالیت</span>' +
        '<span class="analytics-hm-leg-item"><span class="analytics-hm-leg-dot hm-low"></span>کم</span>' +
        '<span class="analytics-hm-leg-item"><span class="analytics-hm-leg-dot hm-mid"></span>متوسط</span>' +
        '<span class="analytics-hm-leg-item"><span class="analytics-hm-leg-dot hm-high"></span>عالی</span>' +
        '</div>';
}

function analyticsMetricCard(cls, emoji, key, val) {
    return '<div class="analytics-metric ' + cls + '">' +
        '<div class="analytics-metric-icon">' + finEmoji(emoji, 'sm') + '</div>' +
        '<div class="analytics-metric-body">' +
        '<span class="analytics-metric-key">' + esc(key) + '</span>' +
        '<span class="analytics-metric-val">' + val + '</span></div></div>';
}

function analyticsDayCard(d, idx) {
    var effCls = d.eff >= 70 ? 'great' : d.eff >= 40 ? 'ok' : d.eff > 0 ? 'low' : 'none';
    var extra = '';
    if (d.sleep || d.mood) {
        extra = '<div class="analytics-day-wellness">' +
            (d.sleep ? '<span class="analytics-day-well-item">' + finEmoji('😴', 'sm') + esc(d.sleep) + '</span>' : '') +
            (d.mood ? '<span class="analytics-day-well-item">' + esc(d.mood) + '</span>' : '') +
            '</div>';
    }
    return '<div class="analytics-day-card" style="--an-day-delay:' + idx + '">' +
        '<div class="analytics-day-rail"><div class="analytics-day-dot ' + effCls + '"></div></div>' +
        '<div class="analytics-day-body">' +
        '<div class="analytics-day-head">' +
        '<span class="analytics-day-date">' + esc(d.date_label) + '</span>' +
        '<span class="analytics-day-eff ' + effCls + '">' + pd(d.eff) + '٪</span></div>' +
        '<div class="analytics-day-bar"><div class="analytics-day-bar-fill ' + effCls + '" style="width:' + d.eff + '%"></div></div>' +
        '<div class="analytics-day-stats">' +
        '<span class="analytics-day-stat"><span class="analytics-day-stat-lbl">کل</span>' + esc(d.total_fmt) + '</span>' +
        '<span class="analytics-day-stat useful"><span class="analytics-day-stat-lbl">مفید</span>' + esc(d.useful_fmt) + '</span>' +
        '</div>' + extra + '</div></div>';
}

function renderAnalytics(a) {
    var period = a.period || 7;
    var p7 = period === 7 ? 'analytics-period-btn active' : 'analytics-period-btn';
    var p30 = period === 30 ? 'analytics-period-btn active' : 'analytics-period-btn';
    var s = a.stats || {
        streak: 0, eff: 0, useful: 0, not_useful: 0,
        total_fmt: '—', useful_fmt: '—', not_useful_fmt: '—',
        income: 0, expense: 0, income_fmt: '—', expense_fmt: '—',
        investment_fmt: '—', balance_fmt: '—', balance: 0,
        avg_mood: '—', avg_sleep: '—',
    };
    var classified = (s.useful || 0) + (s.not_useful || 0);
    var balCls = (s.balance || 0) >= 0 ? 'positive' : 'negative';
    var hasChart = a.chart_points && a.chart_points.some(function(v) { return v > 0; });

    var html = '<div class="analytics-page">' +
        '<div class="analytics-header">' +
        '<div class="analytics-header-orbs" aria-hidden="true">' +
        '<div class="analytics-orb analytics-orb-1"></div>' +
        '<div class="analytics-orb analytics-orb-2"></div>' +
        '<div class="analytics-orb analytics-orb-3"></div></div>' +
        '<div class="analytics-header-brand">' +
        '<div class="analytics-header-top">' +
        '<div class="analytics-brand-mark">' + finEmoji('📊', 'md') + '</div>' +
        '<div class="analytics-header-titles">' +
        '<span class="analytics-header-title">آمار</span>' +
        '<span class="analytics-header-sub">تحلیل عملکرد و روند</span>' +
        '</div>' +
        (s.streak > 0 ? '<span class="analytics-streak-pill">' + finEmoji('🔥', 'sm') + pd(s.streak) + ' روز</span>' : '') +
        '</div>' +
        '<div class="analytics-period-row">' +
        '<a href="javascript:void(0)" onclick="action(\'set_period\',{days:7})" class="' + p7 + '">۷ روز</a>' +
        '<a href="javascript:void(0)" onclick="action(\'set_period\',{days:30})" class="' + p30 + '">۳۰ روز</a>' +
        '</div>' +
        '<div class="analytics-range-label">' + esc(a.start_label) + ' — ' + esc(a.end_label) + '</div>' +
        '<div class="analytics-hero-panel">' +
        '<div class="analytics-hero-main">' +
        homeEffRing(s.eff, classified) +
        '<div class="analytics-hero-side">' +
        '<div class="analytics-hero-label">میانگین بازده دوره</div>' +
        '<div class="analytics-hero-eff">' + pd(s.eff) + '<span class="analytics-hero-unit">٪</span></div>' +
        homeTimeBar(s.useful, s.not_useful) +
        '<div class="analytics-hero-stats">' +
        '<div class="analytics-hero-stat streak">' + finEmoji('🔥', 'sm') + '<div><span class="analytics-stat-lbl">استریک</span><span class="analytics-stat-val">' + pd(s.streak) + '</span></div></div>' +
        '<div class="analytics-hero-stat time">' + finEmoji('⏱️', 'sm') + '<div><span class="analytics-stat-lbl">کل زمان</span><span class="analytics-stat-val">' + esc(s.total_fmt) + '</span></div></div>' +
        '</div></div></div></div></div></div>' +
        '<div class="analytics-body">';

    html += '<div class="fin-card fin-card-animate analytics-card" style="--fin-card-delay:0">' +
        '<div class="fin-card-head">' + finCardTitle('chart', '📈', 'روند بازدهی') + '</div>';
    if (hasChart) {
        html += analyticsEffChart(a.chart_points, 320, 120);
    } else {
        html += '<div class="analytics-chart-empty">' + finIcon('chart', '📉', 'lg') +
            '<p>با ثبت فعالیت روزانه، نمودار بازدهی اینجا نمایش داده می‌شود</p></div>';
    }
    html += '</div>';

    if (a.heatmap && a.heatmap.length) {
        html += '<div class="fin-card fin-card-animate analytics-card" style="--fin-card-delay:1">' +
            '<div class="fin-card-head">' + finCardTitle('analytics', '🗓', 'نقشه فعالیت') + '</div>' +
            analyticsHeatmapCard(a.heatmap) + '</div>';
    }

    html += '<div class="analytics-metrics-section fin-card-animate" style="--fin-card-delay:2">' +
        '<div class="analytics-metrics-head"><span class="analytics-metrics-icon">' + finEmoji('⏳', 'sm') + '</span><span>زمان</span></div>' +
        '<div class="analytics-metrics-grid">' +
        analyticsMetricCard('total', '⏱️', 'کل زمان', esc(s.total_fmt)) +
        analyticsMetricCard('useful', '✅', 'مفید', esc(s.useful_fmt)) +
        analyticsMetricCard('not', '⚠️', 'نامفید', esc(s.not_useful_fmt)) +
        analyticsMetricCard('eff', '🎯', 'بازده', pd(s.eff) + '٪') +
        '</div></div>';

    html += '<div class="analytics-metrics-section fin-card-animate" style="--fin-card-delay:3">' +
        '<div class="analytics-metrics-head"><span class="analytics-metrics-icon">' + finEmoji('💰', 'sm') + '</span><span>مالی</span></div>' +
        '<div class="analytics-metrics-grid">' +
        analyticsMetricCard('income', '📈', 'درآمد', esc(s.income_fmt)) +
        analyticsMetricCard('expense', '💸', 'هزینه', esc(s.expense_fmt)) +
        analyticsMetricCard('invest', '💎', 'سرمایه\u200cگذاری', esc(s.investment_fmt)) +
        analyticsMetricCard('balance ' + balCls, '🏦', 'موجودی', esc(s.balance_fmt)) +
        '</div></div>';

    html += '<div class="analytics-metrics-section fin-card-animate" style="--fin-card-delay:4">' +
        '<div class="analytics-metrics-head"><span class="analytics-metrics-icon">' + finEmoji('🌙', 'sm') + '</span><span>سلامت</span></div>' +
        '<div class="analytics-metrics-grid analytics-metrics-grid-2">' +
        analyticsMetricCard('mood', '😊', 'خلق و خو', esc(s.avg_mood)) +
        analyticsMetricCard('sleep', '😴', 'میانگین خواب', esc(s.avg_sleep)) +
        '</div></div>';

    html += '<div class="analytics-days-section fin-card-animate" style="--fin-card-delay:5">' +
        '<div class="analytics-days-head">' +
        '<span class="analytics-days-title">روزهای گذشته</span>' +
        '<span class="analytics-days-badge">' + pd((a.days && a.days.length) || 0) + ' روز</span></div>';

    if (!(a.days && a.days.length)) {
        html += '<div class="analytics-empty">' + finIcon('analytics', '📊', 'lg') +
            '<div class="analytics-empty-title">داده\u200cای برای نمایش نیست</div>' +
            '<div class="analytics-empty-sub">چند روز تسک انجام دهید تا آمار بازدهی اینجا نمایش داده شود</div></div>';
    } else {
        html += '<div class="analytics-day-list">';
        a.days.forEach(function(d, i) { html += analyticsDayCard(d, i); });
        html += '</div>';
    }
    return html + '</div></div></div>';
}

function renderBackupSummary(summary) {
    if (!summary) return '';
    var items = [
        ['تسک', summary.tasks],
        ['تراکنش مالی', summary.finance],
        ['یادداشت روزانه', summary.notes],
        ['پروژه', summary.projects],
        ['قسط', summary.installments],
        ['تاریخ مهم', summary.important_dates],
        ['تکرار روزانه', summary.recurring],
    ];
    var html = '<div class="backup-summary">';
    items.forEach(function(item) {
        if (item[1] > 0) {
            html += '<span class="backup-summary-chip">' + item[1] + ' ' + item[0] + '</span>';
        }
    });
    html += '</div>';
    return html;
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
    var summaryHtml = renderBackupSummary(s.backup_summary);

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
          + summaryHtml
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
    if (show) {
        syncKeyboardLayout();
        ensureFieldVisible(ta);
    }
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
    var rows = (list || []).map(function(r) {
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
        rows = '<div class="fin-inst-empty">هنوز قسطی ثبت نشده — '
            + '<a href="javascript:void(0)" onclick="action(\'navigate\',{screen:\'installments\'})">'
            + '+ افزودن قسط</a></div>';
    } else {
        rows = (inst.items || []).map(function(i, idx) {
            var statusBtn = i.is_settled
                ? '<span class="inst-settled">✓ تسویه</span>'
                : i.paid_this_month
                    ? '<span class="inst-paid-month">✓ این ماه پرداخت شد</span>'
                    : '<button class="btn-sm-green" onclick="action(\'pay_installment\',{id:'
                      + i.id + '})">پرداخت کردم</button>';
            return '<div class="fin-inst-row" style="--fin-stagger:' + idx + '">'
                + '<span class="inst-title">' + esc(i.title) + '</span>'
                + '<span class="inst-amount">' + esc(i.amount_fmt) + '</span>'
                + '<button type="button" class="fin-inst-edit" onclick="showEditInstallmentById('
                + i.id + ')" aria-label="ویرایش">✎</button>'
                + statusBtn + '</div>';
        }).join('');
    }
    return '<div class="fin-card fin-inst-card">'
        + '<div class="fin-card-head">'
        + finCardTitle('inst', '📋', 'اقساط این ماه')
        + '<a href="javascript:void(0)"'
        + ' onclick="action(\'navigate\',{screen:\'installments\'})"'
        + ' class="fin-chip-btn primary">مدیریت</a></div>'
        + rows
        + (inst.count > 0
            ? '<div class="fin-inst-footer">جمع پرداخت نشده: <strong>' + esc(inst.total_unpaid_fmt) + '</strong></div>'
            : '')
        + '</div>';
}

function renderFinanceScreen(f) {
    var entries = f.entries || [];
    window._finEntries = entries;
    if (f.installments && f.installments.items) {
        window._installmentsList = f.installments.items;
    }
    var t = f.totals || { balance: 0, balance_fmt: '۰', income: 0, expense: 0, income_fmt: '۰', expense_fmt: '۰', investment: 0, investment_fmt: '۰' };
    var balCls = t.balance >= 0 ? 'positive' : 'negative';
    var budgetCats = f.by_category || [];
    var hasExpenseData = budgetCats.some(function(c) { return c.expense > 0; });

    var html = '<div class="fin-page">' +
        '<div class="date-header fin-header">' +
        '<div class="fin-header-orbs" aria-hidden="true">' +
        '<div class="fin-orb fin-orb-1"></div>' +
        '<div class="fin-orb fin-orb-2"></div>' +
        '<div class="fin-orb fin-orb-3"></div></div>' +
        '<div class="fin-header-brand">' +
        '<div class="fin-header-top">' +
        '<div class="fin-brand-mark">' + finEmoji('💰', 'md') + '</div>' +
        '<div class="fin-header-titles">' +
        '<span class="fin-header-title">مالی</span>' +
        '<span class="fin-header-sub">مدیریت درآمد و هزینه</span>' +
        '</div>' +
        (f.is_current_month ? '<span class="fin-month-pill"><span class="fin-month-dot"></span>ماه جاری</span>' : '') +
        '</div>' +
        '<div class="date-header-row fin-date-row">' +
        navArrowBtn('prev', 'action(\'finance_prev_month\')', 'ماه قبل') +
        '<span class="date-title fin-month-title">' + esc(f.month_label) + '</span>' +
        navArrowBtn('next', 'action(\'finance_next_month\')', 'ماه بعد') +
        '</div>' +
        (f.is_current_month ? '' : '<div class="date-header-tools fin-header-tools">' +
        '<button type="button" onclick="action(\'finance_current_month\')" class="today-btn fin-today-btn">ماه جاری</button></div>') +
        '<div class="fin-hero-panel">' +
        '<div class="fin-hero-main">' +
        finBalanceRing(t.income || 0, t.expense || 0, t.balance || 0) +
        '<div class="fin-hero-side">' +
        '<div class="fin-hero-label">موجودی این ماه</div>' +
        '<div class="fin-hero-balance ' + balCls + '">' + esc(t.balance_fmt) + '<span class="fin-hero-unit">تومان</span></div>' +
        finCashFlowBar(t.income || 0, t.expense || 0) +
        '<div class="fin-hero-stats">' +
        '<div class="fin-hero-stat income">' + finEmoji('📈', 'sm') + '<div><span class="fin-stat-lbl">درآمد</span><span class="fin-stat-val">' + esc(t.income_fmt) + '</span></div></div>' +
        '<div class="fin-hero-stat expense">' + finEmoji('💸', 'sm') + '<div><span class="fin-stat-lbl">هزینه</span><span class="fin-stat-val">' + esc(t.expense_fmt) + '</span></div></div>' +
        '</div>' +
        (t.investment > 0 ? '<div class="fin-hero-invest"><a href="javascript:void(0)" onclick="action(\'navigate\',{screen:\'investments\'})">' + finEmoji('💎', 'sm') + ' سرمایه\u200cگذاری: ' + esc(t.investment_fmt) + '</a> <span class="fin-hero-invest-note">(جزء هزینه نیست)</span></div>' : '') +
        '</div></div></div></div></div>';

    html += '<div class="fin-body">';

    html += '<div class="fin-actions">' +
        '<button class="fin-action-btn income" onclick="showAddFinance(\'income\')"><span class="fin-action-glow"></span><span class="fin-action-icon">↑</span><span class="fin-action-lbl">درآمد</span></button>' +
        '<button class="fin-action-btn expense" onclick="showAddFinance(\'expense\')"><span class="fin-action-glow"></span><span class="fin-action-icon">↓</span><span class="fin-action-lbl">هزینه</span></button>' +
        '<button class="fin-action-btn invest" onclick="action(\'navigate\',{screen:\'investments\'})"><span class="fin-action-glow"></span><span class="fin-action-icon">◆</span><span class="fin-action-lbl">سرمایه</span></button>' +
        '<button class="fin-action-btn budget" onclick="showAddBudget()"><span class="fin-action-glow"></span><span class="fin-action-icon">◎</span><span class="fin-action-lbl">بودجه</span></button>' +
        '<button class="fin-action-btn inst" onclick="action(\'navigate\',{screen:\'installments\'})"><span class="fin-action-glow"></span><span class="fin-action-icon">📋</span><span class="fin-action-lbl">اقساط</span></button>' +
        '</div>';

    html += renderInstallmentCard(f.installments);

    if (hasExpenseData) {
        html += '<div class="fin-card fin-card-animate" style="--fin-card-delay:0">' +
            '<div class="fin-card-head">' + finCardTitle('expense', '🥧', 'توزیع هزینه\u200cها') + '</div>' +
            finExpenseDonut(budgetCats) +
            '</div>';
    }

    html += '<div class="fin-card fin-card-animate" style="--fin-card-delay:1"><div class="fin-card-head">' + finCardTitle('chart', '📈', 'روند ماهانه') + '</div>';
    if (f.chart && f.chart.has_data) {
        html += financeLineChartSvg(f.chart, 320, 140);
    } else {
        html += finEmptyState('📊', 'با ثبت اولین تراکنش، نمودار روند مالی نمایش داده می‌شود', '+ ثبت هزینه', 'showAddFinance(\'expense\')', 'chart');
    }
    html += '</div>';

    html += '<div class="fin-card fin-card-collapsible fin-card-animate' + (_showFinanceTransactions ? ' open' : '') + '" style="--fin-card-delay:2">'
        + '<button type="button" class="fin-card-head fin-card-toggle"'
        + ' onclick="_showFinanceTransactions=!_showFinanceTransactions;renderApp(window._lastState)">'
        + finCardTitle('receipt', '🧾', 'تراکنش\u200cها')
        + '<span class="fin-card-head-end">'
        + '<span class="fin-card-badge">' + pd(entries.length) + '</span>'
        + '<span class="fin-card-chevron">' + collapseChevron(_showFinanceTransactions) + '</span>'
        + '</span></button>';
    if (_showFinanceTransactions) {
        if (!entries.length) {
            html += finEmptyState('🧾', 'هنوز تراکنشی ثبت نشده', '+ ثبت درآمد', 'showAddFinance(\'income\')', 'income');
        } else {
            html += '<div class="fin-txn-list">';
            var lastDate = '';
            var txnIdx = 0;
            entries.slice().reverse().forEach(function(e) {
                if (e.date_label !== lastDate) {
                    lastDate = e.date_label;
                    html += '<div class="fin-date-chip">' + esc(e.date_label) + '</div>';
                }
                var info = finTypeInfo(e.type);
                var rowCls = 'fin-txn ' + info.cls;
                html += '<div class="' + rowCls + '" style="--fin-stagger:' + txnIdx + '">' +
                    '<div class="fin-txn-icon">' + info.arrow + '</div>' +
                    '<div class="fin-txn-body">' +
                    '<div class="fin-txn-title">' + esc(e.title) + '</div>' +
                    '<div class="fin-txn-meta"><span class="fin-txn-cat">' +
                    (e.type === 'investment'
                        ? finIcon('investment', investEntryIcon(e)) + ' ' + esc(investEntryDisplay(e))
                        : finCatIconHtml(e.category) + ' ' + esc(e.category)) +
                    '</span>' +
                    (e.type === 'investment' ? ' <span class="fin-txn-tag">سرمایه\u200cگذاری</span>' : '') +
                    '</div></div>' +
                    '<div class="fin-txn-right">' +
                    '<div class="fin-txn-amount">' + esc(e.amount_fmt) + '</div>' +
                    '<div class="fin-txn-btns">' +
                    '<button class="fin-txn-btn" onclick="showEditFinanceById(' + e.id + ')">✎</button>' +
                    '<button class="fin-txn-btn del" onclick="action(\'delete_finance\',{id:' + e.id + '})">×</button>' +
                    '</div></div></div>';
                txnIdx++;
            });
            html += '</div>';
        }
    }
    html += '</div>';

    html += '<div class="fin-card fin-card-collapsible fin-card-animate' + (_showFinanceBudgets ? ' open' : '') + '" style="--fin-card-delay:3">'
        + '<div class="fin-card-head">'
        + '<button type="button" class="fin-card-toggle fin-card-toggle-grow"'
        + ' onclick="_showFinanceBudgets=!_showFinanceBudgets;renderApp(window._lastState)">'
        + finCardTitle('budget', '🎯', 'بودجه دسته\u200cها')
        + '<span class="fin-card-head-end">'
        + '<span class="fin-card-badge">' + pd(budgetCats.length) + '</span>'
        + '<span class="fin-card-chevron">' + collapseChevron(_showFinanceBudgets) + '</span>'
        + '</span></button>'
        + '<div class="fin-card-actions">'
        + '<button type="button" class="fin-chip-btn" onclick="event.stopPropagation();showAddCategory()">+ دسته</button>'
        + '<button type="button" class="fin-chip-btn primary" onclick="event.stopPropagation();showAddBudget()">+ بودجه</button>'
        + '</div></div>';
    if (_showFinanceBudgets) {
        if (!budgetCats.length) {
            html += finEmptyState('🎯', 'بودجه ماهانه برای دسته‌ها تعیین نشده', '+ تعیین بودجه', 'showAddBudget()', 'budget');
        } else {
            budgetCats.forEach(function(c, idx) {
                var barCls = c.over_budget ? 'fin-budget-fill over' : 'fin-budget-fill';
                var barWidth = c.budget > 0 ? Math.min(c.used_pct, 100) : 0;
                var pctLbl = c.budget > 0 ? pd(c.used_pct) + '٪' : '—';
                html += '<div class="fin-budget-item' + (c.over_budget ? ' over' : '') + '" style="--fin-stagger:' + idx + '">' +
                    '<div class="fin-budget-top">' +
                    '<span class="fin-budget-icon">' + finCatIconHtml(c.category) + '</span>' +
                    '<div class="fin-budget-info">' +
                    '<div class="fin-budget-name">' + esc(c.category) + '</div>' +
                    '<div class="fin-budget-sub">' + esc(c.expense_fmt) + ' از ' + (c.budget > 0 ? esc(c.budget_fmt) : '—') + '</div>' +
                    '</div>' +
                    (c.budget > 0 ? '<div class="fin-budget-ring" style="--fin-budget-pct:' + Math.min(c.used_pct, 100) + ';--fin-budget-color:' + (c.over_budget ? '#FF7359' : '#4DD980') + '"><span>' + pctLbl + '</span></div>' : '<span class="fin-budget-pct">' + pctLbl + '</span>') +
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
    }
    html += '</div>';

    if (f.daily_series && f.daily_series.length) {
        html += '<div class="fin-card fin-card-animate" style="--fin-card-delay:4"><div class="fin-card-head">' + finCardTitle('daily', '📅', 'خلاصه روزانه') + '</div>' +
            '<div class="fin-daily-table">' +
            '<div class="fin-daily-head"><span>تاریخ</span><span>درآمد</span><span>هزینه</span><span>سرمایه</span><span>خالص</span></div>';
        f.daily_series.forEach(function(d, idx) {
            var netCls = d.net >= 0 ? 'pos' : 'neg';
            html += '<div class="fin-daily-row" style="--fin-stagger:' + idx + '">' +
                '<span class="fin-daily-date">' + esc(d.date_label) + '</span>' +
                '<span class="fin-daily-inc">' + esc(d.income_fmt) + '</span>' +
                '<span class="fin-daily-exp">' + esc(d.expense_fmt) + '</span>' +
                '<span class="fin-daily-inv">' + esc(d.investment_fmt) + '</span>' +
                '<span class="fin-daily-net ' + netCls + '">' + esc(d.net_fmt) + '</span></div>';
        });
        html += '</div></div>';
    }

    return html + '</div></div>';
}

function renderInvestmentsScreen(d) {
    var entries = d.entries || [];
    window._investEntries = entries;
    window._investAllEntries = d.all_entries || entries;
    var filtered = filterInvestEntries(entries);
    var f = d.filter || {};
    var periodLbl = f.period_stat_label || 'در بازه';
    var t = d.totals || {
        balance: 0, balance_fmt: '۰', period_investment: 0, period_investment_fmt: '۰',
        period_buys: 0, period_buys_fmt: '۰',
        month_investment: 0, month_investment_fmt: '۰',
        net_invested: 0, net_invested_fmt: '۰',
        portfolio_total: 0, portfolio_total_fmt: '۰',
        estimated_value: 0, estimated_value_fmt: '۰', has_market_values: false,
    };
    var tab = window._investTab || 'summary';
    var netFmt = t.net_invested_fmt || t.portfolio_total_fmt || '۰';
    var ringVal = t.has_market_values ? (t.estimated_value_fmt || netFmt) : netFmt;
    var ringLbl = t.has_market_values ? 'ارزش تخمینی' : 'سرمایه خالص';
    var periodFmt = t.period_buys_fmt || t.period_investment_fmt || t.month_investment_fmt || '۰';
    var balCls = t.balance >= 0 ? 'positive' : 'negative';
    var byCat = d.by_category || [];
    var portfolioByCat = d.portfolio_by_category || [];
    var portfolioByRisk = d.portfolio_by_risk || [];
    var positions = d.positions || [];
    var chart = buildInvestmentChart(d);
    var chartTitle = (f.mode === 'all' || !f.start) ? 'روند کل پرتفوی' : 'روند دوره';

    var html = '<div class="inv-page">' +
        '<div class="date-header inv-header">' +
        '<div class="inv-header-orbs" aria-hidden="true">' +
        '<div class="inv-orb inv-orb-1"></div>' +
        '<div class="inv-orb inv-orb-2"></div>' +
        '<div class="inv-orb inv-orb-3"></div></div>' +
        '<div class="inv-header-brand">' +
        '<div class="inv-header-top">' +
        '<div class="inv-brand-mark">' + finIconSvg('investment', 'invest') + '</div>' +
        '<div class="inv-header-titles">' +
        '<span class="inv-header-title">سرمایه\u200cگذاری</span>' +
        '<span class="inv-header-sub">مدیریت پرتفوی و دارایی\u200cها</span>' +
        '</div>' +
        '</div>' +
        '<div class="inv-hero-panel">' +
        '<div class="inv-hero-main">' +
        '<div class="inv-portfolio-ring">' +
        '<div class="inv-ring-glow"></div>' +
        '<div class="inv-ring-inner">' +
        '<span class="inv-ring-val">' + esc(ringVal) + '</span>' +
        '<span class="inv-ring-lbl">' + esc(ringLbl) + '</span></div></div>' +
        '<div class="inv-hero-side">' +
        '<div class="inv-hero-label">موجودی قابل استفاده</div>' +
        '<div class="inv-hero-balance ' + balCls + '">' + esc(t.balance_fmt) + '<span class="inv-hero-unit">تومان</span></div>' +
        '<div class="inv-hero-stats">' +
        (t.has_market_values
            ? '<div class="inv-hero-stat net"><span class="inv-stat-lbl">سرمایه خالص</span><span class="inv-stat-val">' + esc(netFmt) + '</span></div>'
            : '') +
        (t.unrealized_pnl_fmt
            ? '<div class="inv-hero-stat pnl ' + (t.unrealized_pnl_positive ? 'profit' : 'loss') + '"><span class="inv-stat-lbl">' +
                (t.pnl_partial ? 'سود/ضرر (بخشی)' : 'سود/ضرر') +
                '</span><span class="inv-stat-val">' +
                (t.unrealized_pnl_positive ? '+' : '') + esc(t.unrealized_pnl_fmt) + '</span></div>'
            : '') +
        '<div class="inv-hero-stat month">' + finEmoji('📅', 'sm') + '<div><span class="inv-stat-lbl">واریز ' + esc(periodLbl) + '</span><span class="inv-stat-val">' + esc(periodFmt) + '</span></div></div>' +
        '<div class="inv-hero-stat count">' + finEmoji('💎', 'sm') + '<div><span class="inv-stat-lbl">دارایی</span><span class="inv-stat-val">' + pd(positions.length) + '</span></div></div>' +
        '</div>';

    if (d.goal > 0 && f.mode === 'month') {
        var goalPct = Math.min(d.goal_pct || 0, 100);
        var goalBarCls = d.over_goal ? ' inv-goal-over' : '';
        html += '<div class="inv-goal-wrap' + goalBarCls + '">' +
            '<div class="inv-goal-top"><span>هدف واریز: ' + esc(d.goal_fmt) + '</span><span>' + pd(goalPct) + '٪</span></div>' +
            '<div class="inv-goal-bar"><div class="inv-goal-fill" style="width:' + goalPct + '%"></div></div>' +
            '</div>';
    }

    html += '<div class="inv-hero-note">خرید از موجودی کسر می\u200cشود — فروش/برداشت به موجودی برمی\u200cگردد</div>' +
        '</div></div></div></div></div>';

    html += '<div class="inv-body">';
    html += renderInvestPeriodFilter(d);
    html += renderInvestTabs(tab);
    html += renderInvestActions(d);

    if (tab === 'summary') {
        html += renderInvestPositions(positions);
        html += renderAllocationCard(d.allocation || [], t);

        html += '<div class="fin-card inv-card inv-chart-card fin-card-animate" style="--fin-card-delay:2">' +
            '<div class="fin-card-head">' + finCardTitle('investment', '📈', chartTitle) + '</div>' +
            renderInvestChartModeChips() +
            (chart.has_data
                ? investmentTrendChartSvg(chart, 320, 130)
                : finEmptyState('📈', entries.length ? 'با این فیلتر داده\u200cای برای نمودار نیست' : 'با ثبت سرمایه\u200cگذاری نمودار نمایش داده می\u200cشود', null, null, 'investment')) +
            '</div>';

        if (portfolioByRisk.length) {
            html += '<div class="fin-card inv-card fin-card-animate" style="--fin-card-delay:3">' +
                '<div class="fin-card-head">' + finCardTitle('investment', '⚖️', 'تخصیص بر اساس ریسک') + '</div>' +
                invCategoryDonut(portfolioByRisk, t.has_market_values ? t.estimated_value_fmt : netFmt, 'بر اساس ریسک') +
                '</div>';
        } else if (portfolioByCat.length) {
            html += '<div class="fin-card inv-card fin-card-animate" style="--fin-card-delay:3">' +
                '<div class="fin-card-head">' + finCardTitle('investment', '💼', 'تخصیص پرتفوی') + '</div>' +
                invCategoryDonut(portfolioByCat, t.has_market_values ? t.estimated_value_fmt : netFmt, 'کل پرتفوی') +
                '</div>';
        }
    } else {
        html += '<div class="fin-card inv-card fin-card-animate" style="--fin-card-delay:1">' +
            '<div class="fin-card-head">' + finCardTitle('investment', '📋', 'سرمایه\u200cگذاری\u200cها') +
            '<span class="fin-card-badge">' + pd(filtered.length) + '</span></div>' +
            renderInvestFilterChips('list');

        if (!filtered.length) {
            html += finEmptyState('💎', entries.length ? 'با این فیلتر موردی نیست' : 'هنوز سرمایه\u200cگذاری ثبت نشده', '+ ثبت سرمایه\u200cگذاری', 'showAddInvestment()', 'investment');
        } else {
            html += '<div class="fin-txn-list">';
            var lastDate = '';
            filtered.forEach(function(e, idx) {
                if (e.date_label !== lastDate) {
                    lastDate = e.date_label;
                    html += '<div class="fin-date-chip">' + esc(e.date_label) + '</div>';
                }
                var sellCls = e.is_sell ? ' sell' : '';
                var dirTag = e.is_sell
                    ? ' <span class="fin-txn-tag inv-tag-sell">برداشت</span>'
                    : ' <span class="fin-txn-tag">خرید</span>';
                var qtyLine = e.qty_display
                    ? '<div class="fin-txn-qty">' + esc(e.qty_display) + '</div>' : '';
                var pnlLine = e.pnl_fmt && !e.is_sell
                    ? '<div class="fin-txn-qty inv-pnl ' + (e.pnl_positive ? 'profit' : 'loss') + '">' +
                        esc(e.pnl_fmt) +
                        (e.current_unit_price_fmt ? ' · ' + esc(e.current_unit_price_fmt) : '') +
                        '</div>' : '';
                html += '<div class="fin-txn investment' + sellCls + '" style="--fin-stagger:' + idx + '">' +
                    '<div class="fin-txn-icon">' + investEntryIcon(e) + '</div>' +
                    '<div class="fin-txn-body">' +
                    '<div class="fin-txn-title">' + esc(e.title) + '</div>' +
                    '<div class="fin-txn-meta"><span class="fin-txn-cat">' + esc(investEntryDisplay(e)) + '</span>' + dirTag + '</div>' +
                    qtyLine + pnlLine +
                    '</div>' +
                    '<div class="fin-txn-right">' +
                    '<div class="fin-txn-amount">' + (e.is_sell ? '+' : '') + esc(e.amount_fmt) + '</div>' +
                    '<div class="fin-txn-btns">' +
                    '<button class="fin-txn-btn" onclick="showEditInvestmentById(' + e.id + ')">✎</button>' +
                    '<button class="fin-txn-btn del" onclick="action(\'delete_finance\',{id:' + e.id + '})">×</button>' +
                    '</div></div></div>';
            });
            html += '</div>';
        }
        html += '</div>';

        if (byCat.length && (f.mode !== 'all')) {
            html += '<div class="fin-card inv-card fin-card-animate" style="--fin-card-delay:2">' +
                '<div class="fin-card-head">' + finCardTitle('investment', '💎', 'توزیع بازه') + '</div>' +
                invCategoryDonut(byCat, periodFmt, periodLbl) +
                '</div>';
        }
    }

    html += '<div class="inv-finance-link">' +
        '<a href="javascript:void(0)" onclick="action(\'navigate\',{screen:\'finance\'})">' +
        finEmoji('💰', 'sm') + ' مشاهده بخش مالی</a></div>';

    return html + '</div></div>';
}

function renderInstallments(data) {
    window._installmentsList = data.list || [];
    var html = '<div class="page-header">' + finIcon('inst', '📋') + ' مدیریت اقساط</div>';

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

    if (!(data.list && data.list.length)) {
        html += '<div class="empty-state">'
            + '<div class="empty-icon fin-icon fin-icon-inst fin-icon-lg">📋</div>'
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
    window._importantDateItems = data.items || [];
    var html = '<div class="page-header">🔔 تاریخ\u200cهای مهم</div>';

    html += '<a href="javascript:void(0)" class="add-btn"'
        + ' onclick="showAddImportantDate(window._dateCategories)">+ افزودن تاریخ مهم</a>';

    if (!(data.items && data.items.length)) {
        html += '<div class="empty-state">'
            + '<div class="empty-icon">📅</div>'
            + '<div>هیچ تاریخ مهمی ثبت نشده</div></div>';
    } else {
        var overdue = data.items.filter(function(i) { return i.urgency === 'overdue'; });
        var urgent  = data.items.filter(function(i) { return i.urgency === 'urgent'; });
        var soon    = data.items.filter(function(i) { return i.urgency === 'soon'; });
        var ok      = data.items.filter(function(i) {
            return i.urgency === 'ok' || ['overdue', 'urgent', 'soon', 'ok'].indexOf(i.urgency) < 0;
        });

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
    var urgency = i.urgency || 'ok';
    var urgencyCls = {
        overdue: 'date-dot overdue',
        urgent:  'date-dot urgent',
        soon:    'date-dot soon',
        ok:      'date-dot ok',
    }[urgency] || 'date-dot ok';

    var renewBtn = '<button class="chip chip-edit"'
        + ' onclick="action(\'renew_important_date\',{id:' + i.id + '})">'
        + (i.is_repeating ? 'تمدید کردم' : 'تموم شد') + '</button>';

    var editBtn = '<button class="chip chip-neutral"'
        + ' onclick="showEditImportantDateById(' + i.id + ')">✎</button>';

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
        + '<span class="date-item-countdown ' + urgency + '">'
        + esc(i.countdown || '') + '</span></div>'
        + '<div class="date-item-meta">'
        + esc(i.category || '') + ' · ' + esc(i.date_fmt || '') + repeatLabel
        + (i.notes ? ' · ' + esc(i.notes) : '') + '</div>'
        + '<div class="date-item-actions">'
        + renewBtn + editBtn + delBtn + '</div></div>';
}

function importantDateFields(item, categories) {
    item = item || {};
    var repeat = item.repeat_type || 'none';
    var months = item.repeat_months > 0 ? item.repeat_months : 3;
    return [
        { label: 'عنوان', key: 'title', value: item.title || '', validate: 'required' },
        { label: 'تاریخ', key: 'date',
          type: 'jalali-date', value: item.date || '', validate: 'required', clearable: false },
        { label: 'دسته', key: 'category', type: 'select',
          value: item.category || 'سایر', options: categories },
        { label: 'تکرار', key: 'repeat_type', type: 'select',
          value: repeat, options: REPEAT_TYPE_OPTIONS },
        { label: 'هر چند ماه یکبار؟', key: 'repeat_months', type: 'number',
          value: String(months), placeholder: 'مثلاً ۳', validate: 'repeatMonths',
          showWhen: { key: 'repeat_type', value: 'custom' } },
        { label: 'یادداشت (اختیاری)', key: 'notes',
          type: 'textarea', value: item.notes || '', placeholder: '' },
    ];
}

function showAddImportantDate(categories) {
    var now = new Date();
    var todayIso = isoFromGregorian(now.getFullYear(), now.getMonth() + 1, now.getDate());
    showModal({
        title: 'تاریخ مهم جدید',
        cmd: 'add_important_date',
        fields: importantDateFields({ date: todayIso }, categories),
    });
}

function showEditImportantDate(i) {
    showModal({
        title: 'ویرایش تاریخ مهم',
        cmd: 'edit_important_date',
        params: { id: i.id },
        fields: importantDateFields(i, window._dateCategories),
    });
}

function showEditImportantDateById(id) {
    var item = (window._importantDateItems || []).find(function(x) { return x.id == id; });
    if (!item) {
        showToast('تاریخ مهم یافت نشد — از صفحه تاریخ\u200cها دوباره تلاش کنید', 'error');
        return;
    }
    showEditImportantDate(item);
}

function renderInstallmentItem(i) {
    var progress = i.progress != null ? i.progress : 0;
    var paidCount = i.paid_count != null ? i.paid_count : 0;
    var totalCount = i.total_count != null ? i.total_count : 0;
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
        + '<button class="chip chip-edit" onclick="showEditInstallmentById('
        + i.id + ')">✎</button>'
        + '<button class="chip chip-delete" onclick="action(\'delete_installment\',{id:'
        + i.id + '})">حذف</button>'
        + '</div></div>'
        + '<div class="inst-bar"><div class="inst-bar-fill" style="width:'
        + progress + '%' + (i.is_settled ? ';background:var(--success)' : '') + '"></div></div>'
        + '<div class="inst-stats">'
        + '<span>' + pd(paidCount) + ' از ' + pd(totalCount) + ' قسط</span>'
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
        fields: insertSmsField([
            { label: 'عنوان (مثلاً: اقساط گوشی)', key: 'title',
              validate: 'required' },
            { label: 'مبلغ هر قسط (تومان)', key: 'amount',
              type: 'number', validate: 'amount' },
            { label: 'تعداد کل اقساط', key: 'total_count',
              type: 'number', placeholder: '12', validate: 'installmentTotal' },
            { label: 'تاریخ اولین قسط', key: 'start_date',
              type: 'jalali-date', value: todayIso, validate: 'required', clearable: false },
            { label: 'سررسید (چندم هر ماه)', key: 'due_day',
              type: 'number', placeholder: '15', validate: 'dueDay' },
        ]),
    });
}

function showEditInstallment(i) {
    showModal({
        title: 'ویرایش قسط',
        cmd: 'edit_installment',
        params: { id: i.id },
        fields: insertSmsField([
            { label: 'عنوان', key: 'title',
              value: i.title, validate: 'required' },
            { label: 'مبلغ هر قسط (تومان)', key: 'amount',
              type: 'number', value: i.amount, validate: 'amount' },
            { label: 'تعداد کل اقساط', key: 'total_count',
              type: 'number', value: i.total_count, validate: 'installmentTotal' },
            { label: 'تاریخ اولین قسط', key: 'start_date',
              type: 'jalali-date', value: i.start_date, validate: 'required', clearable: false },
            { label: 'سررسید (چندم هر ماه)', key: 'due_day',
              type: 'number', value: i.due_day, validate: 'dueDay' },
        ]),
    });
}

function showEditInstallmentById(id) {
    var item = (window._installmentsList || []).find(function(x) { return x.id == id; });
    if (!item) {
        showToast('قسط یافت نشد — از صفحه اقساط دوباره تلاش کنید', 'error');
        return;
    }
    showEditInstallment(item);
}

var _showCompletedProjects = false;
var _showFinanceTransactions = false;
var _showFinanceBudgets = false;
var _expandedTrackingIntervals = {};

function toggleTrackingInterval(id) {
    if (_expandedTrackingIntervals[id]) {
        delete _expandedTrackingIntervals[id];
    } else {
        _expandedTrackingIntervals[id] = true;
    }
    if (window._lastState) renderApp(window._lastState);
}

function getProjectById(id) {
    var p = (window._projectsList || []).find(function(x) { return x.id == id; });
    if (!p && window._projectDetail && window._projectDetail.id == id) {
        p = window._projectDetail;
    }
    return p;
}

function closeProjectSheet() {
    var o = document.getElementById('proj-sheet');
    if (o) o.style.display = 'none';
    syncBodyScrollLock();
    setTimeout(syncKeyboardLayout, 150);
}

function showProjectSheet(id) {
    closeActivityPicker();
    closeProjectSheet();
    var p = getProjectById(id);
    if (!p) {
        showToast('پروژه یافت نشد — صفحه را تازه کنید', 'error');
        return;
    }
    var overlay = document.getElementById('proj-sheet');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'proj-sheet';
        overlay.className = 'proj-sheet-overlay';
        document.body.appendChild(overlay);
    }
    var doneLabel = p.is_done ? '↩ بازگردانی به فعال' : '✓ علامت‌گذاری تموم‌شده';
    var progress = p.progress || 0;
    overlay.innerHTML =
        '<div class="proj-sheet" style="--project-color:' + esc(p.color) + '" onclick="event.stopPropagation()">' +
        '<div class="proj-sheet-accent"></div>' +
        '<div class="proj-sheet-handle"></div>' +
        '<div class="proj-sheet-head">' +
        projectProgressRing(progress, p.color, 52) +
        '<div class="proj-sheet-meta">' +
        '<div class="proj-sheet-title">' + esc(p.title) + '</div>' +
        '<div class="proj-sheet-sub">' + pd(p.done) + ' از ' + pd(p.total) + ' تسک · ' + pd(progress) + '٪</div>' +
        projectDeadlineBadge(p) +
        '</div></div>' +
        '<button type="button" class="proj-sheet-btn" onclick="closeProjectSheet();showEditProject(' + id + ',window._projectColors)">✎ ویرایش پروژه</button>' +
        '<button type="button" class="proj-sheet-btn" onclick="closeProjectSheet();action(\'toggle_project_done\',{id:' + id + '})">' + doneLabel + '</button>' +
        '<button type="button" class="proj-sheet-btn danger" onclick="closeProjectSheet();action(\'delete_project\',{id:' + id + '})">🗑 حذف پروژه</button>' +
        '<button type="button" class="proj-sheet-btn cancel" onclick="closeProjectSheet()">انصراف</button></div>';
    overlay.style.display = 'flex';
    overlay.onclick = closeProjectSheet;
    syncBodyScrollLock();
    syncKeyboardLayout();
}

function projectProgressRing(pct, color, size) {
    size = size || 48;
    var sw = size >= 68 ? 5 : 4;
    var r = (size - sw * 2 - 2) / 2;
    var c = 2 * Math.PI * r;
    var clamped = Math.min(100, Math.max(0, pct));
    var offset = c * (1 - clamped / 100);
    var cx = size / 2;
    return '<div class="proj-ring-wrap" style="--project-color:' + esc(color) + '">' +
        '<div class="proj-ring-glow" aria-hidden="true"></div>' +
        '<svg class="proj-ring" width="' + size + '" height="' + size + '" viewBox="0 0 ' + size + ' ' + size + '" aria-hidden="true">' +
        '<circle class="proj-ring-track" cx="' + cx + '" cy="' + cx + '" r="' + r + '" fill="none" stroke-width="' + sw + '"/>' +
        '<circle class="proj-ring-arc" cx="' + cx + '" cy="' + cx + '" r="' + r + '" fill="none" stroke="' + esc(color) + '" stroke-width="' + sw + '" ' +
        'stroke-dasharray="' + c.toFixed(2) + '" stroke-dashoffset="' + offset.toFixed(2) + '" ' +
        'stroke-linecap="round" transform="rotate(-90 ' + cx + ' ' + cx + ')"/>' +
        '<text class="proj-ring-text" x="' + cx + '" y="' + (cx + (size >= 68 ? 5 : 4)) + '" text-anchor="middle" fill="currentColor" font-size="' + (size >= 68 ? 13 : 11) + '" font-weight="bold">' +
        pd(clamped) + '٪</text></svg></div>';
}

function projectOverallRing(pct) {
    var size = 92;
    var sw = 7;
    var r = (size - sw * 2 - 4) / 2;
    var c = 2 * Math.PI * r;
    var clamped = Math.min(100, Math.max(0, pct));
    var offset = c * (1 - clamped / 100);
    var cx = size / 2;
    return '<div class="proj-overall-ring" aria-hidden="true">' +
        '<div class="proj-ring-glow proj-ring-glow-lg"></div>' +
        '<svg width="' + size + '" height="' + size + '" viewBox="0 0 ' + size + ' ' + size + '" class="proj-overall-svg">' +
        '<defs><linearGradient id="projOverallGrad" x1="0%" y1="0%" x2="100%" y2="100%">' +
        '<stop offset="0%" stop-color="#818CF8"/><stop offset="50%" stop-color="#6366F1"/><stop offset="100%" stop-color="#A78BFA"/>' +
        '</linearGradient></defs>' +
        '<circle class="proj-ring-track" cx="' + cx + '" cy="' + cx + '" r="' + r + '" fill="none" stroke-width="' + sw + '"/>' +
        '<circle class="proj-ring-arc" cx="' + cx + '" cy="' + cx + '" r="' + r + '" fill="none" stroke="url(#projOverallGrad)" stroke-width="' + sw + '" ' +
        'stroke-dasharray="' + c.toFixed(2) + '" stroke-dashoffset="' + offset.toFixed(2) + '" ' +
        'stroke-linecap="round" transform="rotate(-90 ' + cx + ' ' + cx + ')"/>' +
        '</svg>' +
        '<div class="proj-overall-inner">' +
        '<span class="proj-overall-pct">' + pd(clamped) + '٪</span>' +
        '<span class="proj-overall-lbl">کل پیشرفت</span></div></div>';
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
    var p = getProjectById(id);
    if (!p) {
        showToast('پروژه یافت نشد — صفحه را تازه کنید', 'error');
        return;
    }
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

function projSummaryItem(emoji, val, lbl, variant) {
    variant = variant || 'default';
    return '<div class="proj-summary-item proj-summary-' + variant + '">' + finEmoji(emoji, 'sm') +
        '<span class="proj-summary-val">' + val + '</span>' +
        '<span class="proj-summary-lbl">' + lbl + '</span></div>';
}

function projSectionHead(type, icon, title, badge) {
    return '<div class="proj-section-head">' + finCardTitle(type, icon, title) +
        (badge !== undefined && badge !== null
            ? '<span class="proj-section-badge">' + pd(badge) + '</span>' : '') +
        '</div>';
}

function renderProjectCard(p, muted, idx) {
    var mutedCls = muted ? ' muted' : '';
    var progress = p.progress || 0;
    var html = '<div class="proj-card proj-card-animate' + mutedCls + '" style="--project-color:' + esc(p.color) + ';--proj-stagger:' + (idx || 0) + '">';
    html += '<div class="proj-card-glow" aria-hidden="true"></div>';
    html += '<div class="proj-card-accent"></div>';
    html += '<div class="proj-card-body" onclick="action(\'open_project\',{id:' + p.id + '})">';
    html += '<div class="proj-card-top">';
    html += '<div class="proj-card-info">';
    html += '<div class="proj-card-title-row">';
    html += '<span class="proj-card-dot" aria-hidden="true"></span>';
    html += '<div class="proj-card-title">' + esc(p.title) + '</div>';
    html += '</div>';
    html += '<div class="proj-card-badges">' + projectDeadlineBadge(p) + '</div>';
    html += '<div class="proj-card-meta">' + pd(p.done) + ' از ' + pd(p.total) + ' تسک انجام‌شده</div>';
    html += '</div>';
    html += projectProgressRing(progress, p.color, 56);
    html += '</div>';
    html += '<div class="proj-bar"><div class="proj-bar-fill" style="width:' + progress + '%"></div></div>';
    html += '</div>';
    html += '<button type="button" class="proj-card-menu" onclick="event.stopPropagation();showProjectSheet(' + p.id + ')" aria-label="گزینه‌ها"><span class="proj-menu-dots" aria-hidden="true"></span></button>';
    html += '</div>';
    return html;
}

function renderProjects(data) {
    var list = data.list || [];
    window._projectsList = list;
    window._projectColors = data.colors;
    var active = list.filter(function(p) { return !p.is_done; });
    var done = list.filter(function(p) { return p.is_done; });
    var totalTasks = 0;
    var doneTasks = 0;
    active.forEach(function(p) { totalTasks += p.total; doneTasks += p.done; });
    var overallPct = totalTasks > 0 ? Math.round(doneTasks / totalTasks * 100) : 0;

    var html = '<div class="proj-page">';

    html += '<div class="proj-header date-header">' +
        '<div class="proj-header-orbs" aria-hidden="true">' +
        '<div class="proj-orb proj-orb-1"></div>' +
        '<div class="proj-orb proj-orb-2"></div>' +
        '<div class="proj-orb proj-orb-3"></div></div>' +
        '<div class="proj-header-brand">' +
        '<div class="proj-header-top">' +
        '<div class="proj-brand-mark">' + finIconSvg('projects', 'folder') + '</div>' +
        '<div class="proj-header-titles">' +
        '<span class="proj-header-title">پروژه\u200cها</span>' +
        '<span class="proj-header-sub">مدیریت تسک\u200cها و پیشرفت</span>' +
        '</div>' +
        (active.length ? '<span class="proj-live-pill"><span class="proj-live-dot"></span>' + pd(active.length) + ' فعال</span>' : '') +
        '</div>' +
        '<div class="proj-hero-panel">' +
        '<div class="proj-hero-main">' +
        projectOverallRing(overallPct) +
        '<div class="proj-hero-side">' +
        '<div class="proj-hero-stats">' +
        projSummaryItem('🚀', pd(active.length), 'فعال', 'active') +
        projSummaryItem('✅', pd(doneTasks) + '/' + pd(totalTasks), 'تسک', 'tasks') +
        projSummaryItem('🏆', pd(done.length), 'تمام\u200cشده', 'done') +
        '</div>' +
        '<button type="button" class="proj-header-add" onclick="showAddProject(window._projectColors)">' +
        ico('plus', 'ico') + '<span>پروژه جدید</span></button>' +
        '</div></div></div></div></div>';

    html += '<div class="proj-body">';

    if (!list.length) {
        html += finEmptyState('📋', 'هنوز پروژه\u200cای ندارید.<br>اولین پروژه\u200cتان را بسازید و تسک\u200cها را مدیریت کنید.', '+ ساخت پروژه', 'showAddProject(window._projectColors)', 'projects');
        return html + '</div></div>';
    }

    if (active.length) {
        html += '<div class="proj-card-section proj-card-animate" style="--proj-stagger:0">' + projSectionHead('projects', '◆', 'در جریان', active.length);
        active.forEach(function(p, i) { html += renderProjectCard(p, false, i); });
        html += '</div>';
    } else {
        html += '<div class="proj-card-section proj-card-animate" style="--proj-stagger:0"><div class="proj-empty-mini">' +
            finIcon('projects', '📁') + '<p>پروژه فعالی ندارید</p>' +
            '<button type="button" class="proj-empty-mini-btn" onclick="showAddProject(window._projectColors)">+ ساخت پروژه</button></div></div>';
    }

    if (done.length) {
        html += '<div class="proj-card-section proj-section-done proj-card-animate" style="--proj-stagger:1">';
        html += '<button type="button" class="proj-done-toggle' + (_showCompletedProjects ? ' open' : '') +
            '" onclick="_showCompletedProjects=!_showCompletedProjects;renderApp(window._lastState)">' +
            finIcon('projects', '✓') +
            '<span>پروژه\u200cهای تموم\u200cشده</span><span class="proj-section-badge">' + pd(done.length) + '</span>' +
            '<span class="proj-done-chevron">' + collapseChevron(_showCompletedProjects) + '</span></button>';
        if (_showCompletedProjects) {
            done.forEach(function(p, i) { html += renderProjectCard(p, true, i); });
        }
        html += '</div>';
    }

    return html + '</div></div>';
}

function renderProjectDetail(p) {
    window._projectDetail = p;
    window._projectColors = p.colors;
    var tasks = p.tasks || [];
    var progress = p.progress || 0;
    var pendingTasks = tasks.filter(function(t) { return !t.is_done; }).length;

    var html = '<div class="proj-detail-page" style="--project-color:' + esc(p.color) + '">';

    html += '<div class="proj-detail-hero">' +
        '<div class="proj-detail-blob" aria-hidden="true"></div>' +
        '<div class="proj-detail-nav">' +
        '<button type="button" class="proj-back-btn" aria-label="برگشت به پروژه\u200cها" onclick="action(\'navigate\',{screen:\'projects\'})">' + ico('chevRight', 'ico') + '</button>' +
        '<div class="proj-detail-actions-top">' +
        '<button type="button" class="proj-icon-btn" onclick="showEditProject(' + p.id + ',window._projectColors)" title="ویرایش">✎</button>' +
        '<button type="button" class="proj-icon-btn danger" onclick="action(\'delete_project\',{id:' + p.id + '})" title="حذف">🗑</button>' +
        '</div></div>' +
        '<div class="proj-detail-hero-body">' +
        '<div class="proj-detail-hero-text">' +
        '<div class="proj-detail-name-row">' +
        '<span class="proj-detail-dot" aria-hidden="true"></span>' +
        '<div class="proj-detail-name">' + esc(p.title) + '</div></div>' +
        '<div class="proj-detail-badges">' + projectDeadlineBadge(p) + '</div>' +
        '<div class="proj-detail-stats">' +
        '<span class="proj-detail-stat"><strong>' + pd(p.done) + '</strong> انجام\u200cشده</span>' +
        '<span class="proj-detail-stat-sep">·</span>' +
        '<span class="proj-detail-stat"><strong>' + pd(pendingTasks) + '</strong> باقی\u200cمانده</span>' +
        '<span class="proj-detail-stat-sep">·</span>' +
        '<span class="proj-detail-stat"><strong>' + pd(p.total) + '</strong> کل</span>' +
        '</div></div>' +
        projectProgressRing(progress, p.color, 76) +
        '</div>' +
        '<div class="proj-bar proj-bar-lg"><div class="proj-bar-fill" style="width:' + progress + '%"></div></div>' +
        '<button type="button" class="proj-done-toggle-btn' + (p.is_done ? ' on' : '') +
        '" onclick="action(\'toggle_project_done\',{id:' + p.id + '})">' +
        (p.is_done ? '✓ پروژه تموم شده — بازگردانی' : '✓ علامت‌گذاری پروژه به عنوان تموم‌شده') +
        '</button></div>';

    html += '<div class="proj-tasks-card proj-card-animate" style="--proj-stagger:0">' +
        '<div class="proj-section-head">' +
        finCardTitle('projects', '☑', 'تسک\u200cها') +
        '<span class="proj-section-badge">' + pd(tasks.length) + '</span></div>';

    if (!tasks.length) {
        html += finEmptyState('☑', 'هنوز تسکی اضافه نکرده\u200cاید', '+ افزودن تسک',
            'showModal({title:\'تسک جدید\',cmd:\'add_project_task\',params:{project_id:' + p.id +
            '},fields:[{label:\'عنوان\',key:\'title\',validate:\'required\'}]})', 'projects');
    } else {
        html += '<div class="proj-task-list">';
        tasks.forEach(function(task, idx) {
            var rowCls = 'proj-task-item proj-task-animate' + (task.is_done ? ' done' : '');
            html += '<div class="' + rowCls + '" style="--proj-stagger:' + idx + '">';
            html += '<button type="button" class="proj-task-check' + (task.is_done ? ' checked' : '') +
                '" onclick="action(\'toggle_project_task\',{id:' + task.id + '})">' +
                (task.is_done ? ico('check', 'ico proj-check-ico') : '') + '</button>';
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
        '},fields:[{label:\'عنوان\',key:\'title\',validate:\'required\'}]})">' + ico('plus', 'ico') + '<span>افزودن تسک</span></button>';
    html += '</div></div>';

    return html;
}

var TRACK_ACTIVITIES = [
    { e: '😴', l: 'خواب' }, { e: '💼', l: 'کار' }, { e: '📱', l: 'گوشی' },
    { e: '☕', l: 'استراحت' }, { e: '🍽️', l: 'غذا' }, { e: '🏃', l: 'ورزش' },
    { e: '🚇', l: 'مترو' }, { e: '🚗', l: 'ماشین' }, { e: '🚌', l: 'اتوبوس' },
    { e: '🚕', l: 'تاکسی' }, { e: '🚶', l: 'پیاده\u200cروی' }, { e: '🚴', l: 'دوچرخه' },
    { e: '🎬', l: 'سینما' }, { e: '📺', l: 'تلویزیون' }, { e: '📚', l: 'مطالعه' },
    { e: '🎮', l: 'بازی' }, { e: '🛒', l: 'خرید' }, { e: '🧹', l: 'نظافت' },
    { e: '🍳', l: 'آشپزی' }, { e: '🚿', l: 'دوش' }, { e: '🕌', l: 'نماز' },
    { e: '👨‍👩‍👧', l: 'خانواده' }, { e: '👥', l: 'دوستان' }, { e: '💬', l: 'گفتگو' },
    { e: '📞', l: 'تماس' }, { e: '🏥', l: 'پزشکی' }, { e: '💊', l: 'دارو' },
    { e: '🧘', l: 'مدیتشن' }, { e: '🎵', l: 'موسیقی' }, { e: '🎨', l: 'هنر' },
    { e: '✍️', l: 'نوشتن' }, { e: '💻', l: 'کامپیوتر' }, { e: '🏫', l: 'کلاس' },
    { e: '📝', l: 'امتحان' }, { e: '🏋️', l: 'بدنسازی' }, { e: '⚽', l: 'فوتبال' },
    { e: '☕', l: 'کافه' }, { e: '🍕', l: 'فست\u200cفود' }, { e: '🧋', l: 'نوشیدنی' },
    { e: '🐕', l: 'حیوان خانگی' }, { e: '🌳', l: 'پارک' }, { e: '🏖️', l: 'تفریح' },
    { e: '✈️', l: 'سفر' }, { e: '💤', l: 'چرت' }, { e: '🧑‍💼', l: 'جلسه' },
    { e: '📊', l: 'پروژه' }, { e: '🔧', l: 'تعمیرات' }, { e: '🏠', l: 'خانه' },
    { e: '🛏️', l: 'دراز کشیدن' }, { e: '📰', l: 'اخبار' }, { e: '🎧', l: 'پادکست' },
    { e: '🛍️', l: 'مرکز خرید' }, { e: '💇', l: 'آرایشگاه' }, { e: '🏦', l: 'بانک' },
    { e: '📦', l: 'کارهای اداری' }, { e: '🚬', l: 'سیگار' }, { e: '🧺', l: 'رختشویی' },
    { e: '👶', l: 'مراقبت کودک' }, { e: '🍵', l: 'چای' }, { e: '🌙', l: 'شب\u200cبیداری' },
    { e: '🏍️', l: 'موتور' }, { e: '🚆', l: 'قطار' }, { e: '🛫', l: 'فرودگاه' },
    { e: '🛵', l: 'اسکوتر' }, { e: '🚁', l: 'هلیکوپتر' }, { e: '⛵', l: 'قایق\u200cسواری' },
    { e: '🦷', l: 'دندانپزشکی' }, { e: '🩺', l: 'آزمایش' }, { e: '💉', l: 'ویزیت پزشک' },
    { e: '🧴', l: 'فیزیوتراپی' }, { e: '💆', l: 'ماساژ' }, { e: '💅', l: 'آرایش' },
    { e: '✂️', l: 'اصلاح' }, { e: '🧵', l: 'خیاطی' }, { e: '🪴', l: 'باغبانی' },
    { e: '🎉', l: 'مهمانی' }, { e: '🎂', l: 'تولد' }, { e: '🕯️', l: 'مراسم' },
    { e: '🏕️', l: 'کمپینگ' }, { e: '⛰️', l: 'کوهنوردی' }, { e: '🏊', l: 'شنا' },
    { e: '🏐', l: 'والیبال' }, { e: '🏀', l: 'بسکتبال' }, { e: '🎾', l: 'تنیس' },
    { e: '🧘‍♀️', l: 'یوگا' }, { e: '🤸', l: 'پیلاتس' }, { e: '🏃‍♂️', l: 'دویدن' },
    { e: '⛸️', l: 'اسکیت' }, { e: '🎿', l: 'اسکی' }, { e: '🎣', l: 'ماهیگیری' },
    { e: '♟️', l: 'شطرنج' }, { e: '🧩', l: 'پازل' }, { e: '🖌️', l: 'نقاشی' },
    { e: '📷', l: 'عکاسی' }, { e: '🎥', l: 'فیلمبرداری' }, { e: '🎞️', l: 'ویرایش ویدیو' },
    { e: '👨‍💻', l: 'برنامه\u200cنویسی' }, { e: '🖥️', l: 'طراحی' }, { e: '🗣️', l: 'یادگیری زبان' },
    { e: '🎓', l: 'دوره آنلاین' }, { e: '📡', l: 'وبینار' }, { e: '🔢', l: 'ریاضی' },
    { e: '📖', l: 'تکلیف درسی' }, { e: '🎹', l: 'تمرین موسیقی' }, { e: '🎤', l: 'آواز' },
    { e: '🎸', l: 'گیتار' }, { e: '🎻', l: 'ویولن' }, { e: '💃', l: 'رقص' },
    { e: '🎭', l: 'تئاتر' }, { e: '🎫', l: 'کنسرت' }, { e: '🏛️', l: 'موزه' },
    { e: '📚', l: 'کتابخانه' }, { e: '📱', l: 'شبکه\u200cهای اجتماعی' }, { e: '▶️', l: 'یوتیوب' },
    { e: '📸', l: 'اینستاگرام' }, { e: '💬', l: 'تلگرام' }, { e: '📧', l: 'ایمیل' },
    { e: '🌐', l: 'اینترنت' }, { e: '🛒', l: 'خرید آنلاین' }, { e: '🏪', l: 'بازار' },
    { e: '🍎', l: 'میوه\u200cفروشی' }, { e: '🥖', l: 'نانوایی' }, { e: '🥩', l: 'قصابی' },
    { e: '💊', l: 'داروخانه' }, { e: '📮', l: 'پست' }, { e: '⛽', l: 'پمپ بنزین' },
    { e: '🚗', l: 'کارواش' }, { e: '🔩', l: 'تعویض روغن' }, { e: '🅿️', l: 'پارکینگ' },
    { e: '🚦', l: 'ترافیک' }, { e: '⏳', l: 'انتظار' }, { e: '🧍', l: 'صف' },
    { e: '🤝', l: 'قرار ملاقات' }, { e: '👔', l: 'مصاحبه' }, { e: '📽️', l: 'ارائه' },
    { e: '📋', l: 'یادداشت\u200cبرداری' }, { e: '🗓️', l: 'برنامه\u200cریزی' }, { e: '🗂️', l: 'سازماندهی' },
    { e: '🗄️', l: 'بایگانی' }, { e: '💾', l: 'پشتیبان\u200cگیری' }, { e: '🧾', l: 'پرداخت قبوض' },
    { e: '💰', l: 'حسابداری' }, { e: '📑', l: 'مالیات' }, { e: '🛠️', l: 'کار فنی' },
    { e: '🔨', l: 'نجاری' }, { e: '⚡', l: 'برق\u200cکاری' }, { e: '🚰', l: 'لوله\u200cکشی' },
    { e: '🖌️', l: 'رنگ\u200cآمیزی' }, { e: '🪟', l: 'شستن پنجره' }, { e: '🧽', l: 'ظرفشویی' },
];
var TRACK_COLORS = ['#2DD4BF', '#818CF8', '#F472B6', '#FBBF24', '#FB7185', '#34D399', '#38BDF8'];
var _dayTrackLabelColors = {};

function trackLabelKey(label) {
    return (label || '').trim() || 'بدون عنوان';
}

function buildTrackingLabelColors(intervals) {
    var colors = {};
    var idx = 0;
    var sorted = (intervals || []).slice().sort(function(a, b) {
        return (a.started_epoch || 0) - (b.started_epoch || 0);
    });
    for (var i = 0; i < sorted.length; i++) {
        var lbl = trackLabelKey(sorted[i].label);
        if (!colors[lbl]) {
            colors[lbl] = TRACK_COLORS[idx % TRACK_COLORS.length];
            idx += 1;
        }
    }
    return colors;
}

function trackColorForLabel(label) {
    var key = trackLabelKey(label);
    if (_dayTrackLabelColors[key]) return _dayTrackLabelColors[key];
    if (!key || key === 'بدون عنوان') return '#71717A';
    var hash = 0;
    for (var i = 0; i < key.length; i++) {
        hash = ((hash << 5) - hash) + key.charCodeAt(i);
        hash |= 0;
    }
    return TRACK_COLORS[Math.abs(hash) % TRACK_COLORS.length];
}

function trackEmojiForLabel(label) {
    var s = (label || '').trim();
    if (!s) return '⏱';
    for (var i = 0; i < TRACK_ACTIVITIES.length; i++) {
        var a = TRACK_ACTIVITIES[i];
        if (trackActivityLabel(a) === s || a.l === s) return a.e;
    }
    var sp = s.indexOf(' ');
    if (sp > 0) {
        var prefix = s.slice(0, sp);
        if (prefix.length <= 4) return prefix;
    }
    return '⏱';
}

function trackActivityLabel(a) {
    return a.e + ' ' + a.l;
}

function trackLabelQuery(raw) {
    var s = (raw || '').trim();
    if (!s) return '';
    var m = s.match(/[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+.*$/);
    return (m ? m[0] : s).trim();
}

function matchTrackActivities(query) {
    var raw = (query || '').trim();
    if (!raw) return TRACK_ACTIVITIES.slice();
    var q = trackLabelQuery(raw);
    if (!q) return [];
    return TRACK_ACTIVITIES.filter(function(a) {
        return a.l.indexOf(q) !== -1;
    });
}

function buildActivityGrid(intervalId, query) {
    var html = '';
    matchTrackActivities(query).forEach(function(a) {
        var full = trackActivityLabel(a);
        html += '<button type="button" class="track-act-item" onclick="pickTrackActivity(' + intervalId + ',\'' + escJs(full) + '\')">' +
            '<span class="track-act-emoji">' + a.e + '</span>' +
            '<span class="track-act-name">' + esc(a.l) + '</span></button>';
    });
    return html || '<div class="track-act-empty">فعالیتی یافت نشد</div>';
}

function filterActivityPicker(query) {
    var grid = document.getElementById('track-act-grid');
    var sid = window._trackActIntervalId;
    if (grid && sid != null) grid.innerHTML = buildActivityGrid(sid, query);
}

function closeActivityPicker() {
    var o = document.getElementById('track-act-sheet');
    if (o) {
        o.style.display = 'none';
        o.classList.remove('track-act-viewport-sync');
    }
    window._trackActIntervalId = null;
    _sheetOpenVvHeight = null;
    syncBodyScrollLock();
    setTimeout(syncKeyboardLayout, 150);
}

function pickTrackActivity(intervalId, label) {
    document.querySelectorAll('.track-label-input').forEach(function(el) { el.blur(); });
    closeActivityPicker();
    var input = document.querySelector('.track-label-input[data-interval-id="' + intervalId + '"]');
    if (input) input.value = label;
    setTrackLabel(intervalId, label, true);
}

function showActivityPicker(intervalId) {
    document.querySelectorAll('.track-label-input').forEach(function(el) { el.blur(); });
    closeActivityPicker();
    closeProjectSheet();
    window._trackActIntervalId = intervalId;
    var overlay = document.getElementById('track-act-sheet');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'track-act-sheet';
        overlay.className = 'track-act-overlay track-act-viewport-sync';
        document.body.appendChild(overlay);
    }
    overlay.classList.add('track-act-viewport-sync');
    overlay.innerHTML =
        '<div class="track-act-sheet" onclick="event.stopPropagation()">' +
        '<div class="track-act-handle"></div>' +
        '<div class="track-act-title">انتخاب فعالیت</div>' +
        '<input type="search" class="track-act-search" placeholder="جستجو..." oninput="filterActivityPicker(this.value)" aria-label="جستجوی فعالیت">' +
        '<div class="track-act-grid" id="track-act-grid">' + buildActivityGrid(intervalId, '') + '</div>' +
        '<button type="button" class="track-act-cancel" onclick="closeActivityPicker()">بستن</button></div>';
    overlay.style.display = 'flex';
    overlay.onclick = closeActivityPicker;
    _sheetOpenVvHeight = visibleViewportHeight();
    syncBodyScrollLock();
    syncSheetViewport();
    syncKeyboardLayout();
}

function trackSecTitle(icon, text) {
    return '<div class="sec-title track-sec-title">' + finEmoji(icon, 'sm') +
        '<span>' + text + '</span></div>';
}

function trackDonutSvg(segments, size, strokeWidth) {
    size = size || 120;
    strokeWidth = strokeWidth || 12;
    var r = (size - strokeWidth) / 2;
    var c = 2 * Math.PI * r;
    var cx = size / 2;
    var offset = 0;
    var rings = '';
    segments.forEach(function(seg) {
        if (!seg.pct) return;
        var dash = Math.max((seg.pct / 100) * c, 0.5);
        rings += '<circle class="track-donut-seg" cx="' + cx + '" cy="' + cx + '" r="' + r + '" fill="none" ' +
            'stroke="' + seg.color + '" stroke-width="' + strokeWidth + '" stroke-linecap="round" ' +
            'stroke-dasharray="' + dash + ' ' + (c - dash) + '" stroke-dashoffset="' + (-offset) + '" ' +
            'transform="rotate(-90 ' + cx + ' ' + cx + ')" />';
        offset += dash;
    });
    return '<svg class="track-donut" width="' + size + '" height="' + size + '" viewBox="0 0 ' + size + ' ' + size + '" aria-hidden="true">' +
        '<circle cx="' + cx + '" cy="' + cx + '" r="' + r + '" fill="none" stroke="var(--surface-muted)" stroke-width="' + strokeWidth + '" />' +
        rings + '</svg>';
}

function trackLiveTimerHtml(startedEpoch) {
    var attrs = startedEpoch ? ' data-started-epoch="' + startedEpoch + '"' : '';
    return '<div class="track-timer-wrap">' +
        '<div class="track-timer-glow"></div>' +
        '<div class="track-timer-ring">' +
        '<svg class="track-timer-svg" viewBox="0 0 180 180" aria-hidden="true">' +
        '<defs><linearGradient id="trackTimerGrad" x1="0%" y1="0%" x2="100%" y2="100%">' +
        '<stop offset="0%" stop-color="#2DD4BF"/><stop offset="50%" stop-color="#818CF8"/><stop offset="100%" stop-color="#2DD4BF"/>' +
        '</linearGradient></defs>' +
        '<circle class="track-timer-track" cx="90" cy="90" r="82" fill="none" stroke="rgba(45,212,191,0.12)" stroke-width="6"/>' +
        '<circle class="track-timer-progress" cx="90" cy="90" r="82" fill="none" stroke="url(#trackTimerGrad)" stroke-width="6" ' +
        'stroke-linecap="round" stroke-dasharray="120 396" transform="rotate(-90 90 90)"/>' +
        '</svg>' +
        '<div class="track-timer-inner">' +
        '<div class="track-timer-lbl">فعالیت فعلی</div>' +
        '<div id="tracking-live" class="track-timer-val"' + attrs + '>۰۰:۰۰:۰۰</div>' +
        '</div></div></div>';
}

function refreshTrackLabelDisplay(intervalId, label) {
    var trimmed = (label || '').trim();
    var displayLabel = trimmed || 'بدون عنوان';
    var emoji = trackEmojiForLabel(trimmed);
    var color = trackColorForLabel(trimmed);

    var input = document.querySelector('.track-label-input[data-interval-id="' + intervalId + '"]');
    if (!input) return;

    var activePanel = input.closest('.track-active-panel');
    if (activePanel) {
        var title = activePanel.querySelector('.track-active-title');
        var emojiEl = activePanel.querySelector('.track-active-emoji');
        if (title) title.textContent = trimmed ? displayLabel : 'عنوان فعالیت را وارد کنید';
        if (emojiEl) {
            emojiEl.textContent = emoji;
            emojiEl.style.setProperty('--avatar-color', color);
        }
    }

    var card = input.closest('.track-interval');
    if (card) {
        var lbl = card.querySelector('.track-interval-label');
        var avatar = card.querySelector('.track-interval-avatar');
        var accent = card.querySelector('.track-interval-accent');
        var node = card.querySelector('.track-timeline-node');
        if (lbl) lbl.textContent = displayLabel;
        if (avatar) {
            avatar.textContent = emoji;
            avatar.style.setProperty('--avatar-color', color);
        }
        if (accent) accent.style.background = color;
        if (node) node.style.setProperty('--node-color', color);
    }
}

function setTrackLabel(intervalId, label, updateUi) {
    action('set_tracking_label', { interval_id: intervalId, label: label });
    if (updateUi) refreshTrackLabelDisplay(intervalId, label);
}

function hideTrackLabelSuggestions(intervalId) {
    var box = document.getElementById('track-label-sug-' + intervalId);
    if (box) {
        box.style.display = 'none';
        box.innerHTML = '';
    }
}

function hideTrackLabelSuggestionsDelayed(intervalId) {
    setTimeout(function() { hideTrackLabelSuggestions(intervalId); }, 150);
}

function pickTrackLabelSuggestion(intervalId, label) {
    var input = document.querySelector('.track-label-input[data-interval-id="' + intervalId + '"]');
    if (input) {
        input.value = label;
        input.blur();
    }
    hideTrackLabelSuggestions(intervalId);
    setTrackLabel(intervalId, label, true);
}

function onTrackLabelInput(intervalId, input) {
    debounceTrackLabel(intervalId, input.value);
    refreshTrackLabelDisplay(intervalId, input.value);
    var trimmed = (input.value || '').trim();
    var query = trackLabelQuery(trimmed);
    var box = document.getElementById('track-label-sug-' + intervalId);
    if (!box) return;

    if (!query) {
        hideTrackLabelSuggestions(intervalId);
        return;
    }

    if (TRACK_ACTIVITIES.some(function(a) {
        return trackActivityLabel(a) === trimmed || a.l === trimmed;
    })) {
        hideTrackLabelSuggestions(intervalId);
        return;
    }

    var matches = matchTrackActivities(trimmed).slice(0, 6);
    if (!matches.length) {
        hideTrackLabelSuggestions(intervalId);
        return;
    }

    var html = '';
    matches.forEach(function(a) {
        var full = trackActivityLabel(a);
        html += '<button type="button" class="track-label-sug-item" ' +
            'onmousedown="event.preventDefault();pickTrackLabelSuggestion(' + intervalId + ',\'' + escJs(full) + '\')">' +
            '<span class="track-act-emoji">' + a.e + '</span>' +
            '<span class="track-label-sug-text">' + esc(a.l) + '</span></button>';
    });
    box.innerHTML = html;
    box.style.display = 'block';
}

function trackingHeader(t, heroInner, opts) {
    opts = opts || {};
    var html = '<div class="date-header track-header">';
    html += '<div class="track-header-orbs" aria-hidden="true"><span class="track-orb track-orb-1"></span><span class="track-orb track-orb-2"></span><span class="track-orb track-orb-3"></span></div>';
    html += '<div class="track-header-brand">';
    html += '<div class="track-header-top">';
    html += '<div class="track-brand-mark">' + finEmoji('⏱️', 'md') + '</div>';
    html += '<div class="track-header-titles">';
    html += '<span class="track-header-title">ردیابی روز</span>';
    html += '<span class="track-header-sub">ثبت و تحلیل زمان</span>';
    html += '</div>';
    if (opts.live) {
        html += '<span class="track-live-badge"><span class="track-live-dot"></span>در حال ثبت</span>';
    }
    html += '</div>';
    html += '<div class="track-date-label">' + esc(t.date_label) + '</div>';
    if (heroInner) html += '<div class="track-hero-panel">' + heroInner + '</div>';
    html += '</div></div>';
    return html;
}

function trackingIntervalCard(iv, totalSecs, opts) {
    opts = opts || {};
    var isExpanded = !!_expandedTrackingIntervals[iv.id];
    var pct = totalSecs > 0 && iv.duration_secs ? Math.round(iv.duration_secs / totalSecs * 100) : 0;
    var label = (iv.label || '').trim();
    var color = trackColorForLabel(label);
    var emoji = trackEmojiForLabel(label);
    var displayLabel = label || 'بدون عنوان';
    var cardCls = 'track-interval' + (isExpanded ? ' is-open' : '');
    if (iv.is_active) cardCls += ' is-active';
    if (iv.is_useful === true) cardCls += ' is-useful';
    else if (iv.is_useful === false) cardCls += ' is-not-useful';

    var timeCompact = '';
    if (iv.started_label) {
        timeCompact = esc(iv.started_label);
        if (iv.ended_label) timeCompact += ' ← ' + esc(iv.ended_label);
    }

    var html = '<div class="' + cardCls + '"' + (opts.stagger != null ? ' style="--track-stagger:' + opts.stagger + '"' : '') + '>';
    html += '<div class="track-timeline-node" style="--node-color:' + color + '"><span class="track-timeline-dot"></span></div>';
    html += '<div class="track-interval-card">';
    html += '<div class="track-interval-accent" style="background:' + color + '"></div>';
    html += '<div class="track-interval-body">';
    html += '<button type="button" class="track-interval-header" onclick="toggleTrackingInterval(' + iv.id + ')">';
    html += '<span class="track-interval-avatar" style="--avatar-color:' + color + '">' + emoji + '</span>';
    html += '<span class="track-interval-header-main">';
    html += '<span class="track-interval-label">' + esc(displayLabel) + '</span>';
    if (timeCompact) {
        html += '<span class="track-interval-time-compact">' + timeCompact + '</span>';
    }
    html += '</span>';
    html += '<span class="track-interval-top-end">';
    if (iv.duration_label) {
        html += '<span class="track-interval-dur">' + esc(iv.duration_label) + '</span>';
    } else if (iv.is_active) {
        html += '<span class="track-interval-live">زنده</span>';
    }
    if (pct > 0 && !isExpanded) {
        html += '<span class="track-interval-pct">' + pd(pct) + '٪</span>';
    }
    html += collapseChevron(isExpanded);
    if (!iv.is_active) {
        html += '<span role="button" tabindex="0" class="track-interval-del" onclick="event.stopPropagation();action(\'delete_tracking_interval\',{interval_id:' + iv.id + '})" onkeydown="onRoleButtonKey(event)" title="حذف" aria-label="حذف بازه">×</span>';
    }
    html += '</span></button>';

    if (isExpanded) {
        html += '<div class="track-interval-detail">';
        if (iv.started_label) {
            html += '<div class="track-interval-time">' + esc(iv.started_label);
            if (iv.ended_label) html += ' ← ' + esc(iv.ended_label);
            html += '</div>';
        }
        if (pct > 0) {
            html += '<div class="track-interval-bar"><div class="track-interval-bar-fill" style="width:' + pct + '%;background:' + color + '"></div></div>';
            html += '<div class="track-interval-pct-row"><span>سهم از کل روز</span><span>' + pd(pct) + '٪</span></div>';
        }
        html += trackingUsefulChips(iv.id, iv.is_useful);
        html += '<div class="track-label-row">';
        html += '<div class="track-label-wrap">';
        html += '<input type="text" class="track-label-input" data-interval-id="' + iv.id + '" ' +
            'placeholder="عنوان فعالیت..." value="' + esc(label) + '" autocomplete="off" ' +
            'oninput="onTrackLabelInput(' + iv.id + ', this)" ' +
            'onblur="flushTrackLabelOnBlur(' + iv.id + ', this)" ' +
            'onchange="setTrackLabel(' + iv.id + ', this.value, true)">';
        html += '<div class="track-label-suggestions" id="track-label-sug-' + iv.id + '"></div>';
        html += '</div>';
        html += '<button type="button" class="track-pick-btn" onclick="showActivityPicker(' + iv.id + ')" aria-label="انتخاب از لیست فعالیت\u200cها">' +
            finEmoji('📋', 'sm') + '<span>انتخاب</span></button>';
        html += '</div></div>';
    }

    html += '</div></div></div>';
    return html;
}

function trackingActivePanel(iv, opts) {
    opts = opts || {};
    if (!iv) return '';
    var label = (iv.label || '').trim();
    var emoji = trackEmojiForLabel(label);
    var color = trackColorForLabel(label);
    var displayLabel = label || 'عنوان فعالیت را وارد کنید';
    var panelCls = 'track-active-panel' + (opts.inHeader ? ' track-active-in-header' : '');
    var html = '<div class="' + panelCls + '">';
    html += '<div class="track-active-panel-head">';
    html += '<span class="track-active-emoji" style="--avatar-color:' + color + '">' + emoji + '</span>';
    html += '<div class="track-active-meta">';
    html += '<span class="track-active-title">' + esc(displayLabel) + '</span>';
    if (iv.started_label) {
        html += '<span class="track-active-since">از ' + esc(iv.started_label) + '</span>';
    }
    html += '</div></div>';
    html += '<div class="track-label-row track-active-label-row">';
    html += '<div class="track-label-wrap">';
    html += '<input type="text" class="track-label-input track-label-input-prominent" data-interval-id="' + iv.id + '" ' +
        'placeholder="چه کاری انجام می\u200cدهید؟" value="' + esc(label) + '" autocomplete="off" ' +
        'oninput="onTrackLabelInput(' + iv.id + ', this)" ' +
        'onblur="flushTrackLabelOnBlur(' + iv.id + ', this)" ' +
        'onchange="setTrackLabel(' + iv.id + ', this.value, true)">';
    html += '<div class="track-label-suggestions" id="track-label-sug-' + iv.id + '"></div>';
    html += '</div>';
    html += '<button type="button" class="track-pick-btn track-pick-btn-lg" onclick="showActivityPicker(' + iv.id + ')" aria-label="انتخاب فعالیت">' +
        finEmoji('📋', 'sm') + '<span>انتخاب</span></button>';
    html += '</div></div>';
    return html;
}

function trackingUsefulChips(intervalId, isUseful) {
    var uCls = isUseful === true ? 'chip-useful-on' : 'chip-useful-off';
    var nuCls = isUseful === false ? 'chip-notuseful-on' : 'chip-neutral';
    return '<div class="track-useful-row">' +
        '<a href="javascript:void(0)" onclick="action(\'set_tracking_useful\',{interval_id:' + intervalId + ',value:\'true\'})" class="chip track-chip ' + uCls + '">' + finEmoji('✅', 'sm') + ' مفید</a>' +
        '<a href="javascript:void(0)" onclick="action(\'set_tracking_useful\',{interval_id:' + intervalId + ',value:\'false\'})" class="chip track-chip ' + nuCls + '">' + finEmoji('⚠️', 'sm') + ' نامفید</a>' +
        '</div>';
}

function trackingEfficiencyRow(t, opts) {
    opts = opts || {};
    if (!t.useful_label && !t.not_useful_label && t.efficiency == null) return '';
    var segments = [];
    if (t.efficiency != null) {
        segments.push({ color: '#34D399', pct: t.efficiency });
        if (t.not_useful_label) {
            segments.push({ color: '#FB923C', pct: 100 - t.efficiency });
        }
    }
    var panelCls = 'track-stats-panel' + (opts.inHeader ? ' track-stats-in-header' : '');
    var html = '<div class="' + panelCls + '">';
    if (t.efficiency != null && segments.length) {
        html += '<div class="track-eff-gauge">';
        html += trackDonutSvg(segments, 88, 10);
        html += '<div class="track-eff-gauge-center"><span class="track-eff-gauge-val">' + pd(t.efficiency) + '٪</span><span class="track-eff-gauge-lbl">بازده</span></div>';
        html += '</div>';
    }
    html += '<div class="track-stats-grid">';
    if (t.useful_label) {
        html += '<div class="track-stat-card useful">' + finEmoji('✅', 'sm') +
            '<div><span class="track-stat-card-lbl">مفید</span><span class="track-stat-card-val">' + esc(t.useful_label) + '</span></div></div>';
    }
    if (t.not_useful_label) {
        html += '<div class="track-stat-card not">' + finEmoji('⚠️', 'sm') +
            '<div><span class="track-stat-card-lbl">نامفید</span><span class="track-stat-card-val">' + esc(t.not_useful_label) + '</span></div></div>';
    }
    if (t.completed_count) {
        html += '<div class="track-stat-card neutral">' + finEmoji('📋', 'sm') +
            '<div><span class="track-stat-card-lbl">بازه\u200cها</span><span class="track-stat-card-val">' + pd(t.completed_count) + '</span></div></div>';
    }
    html += '</div></div>';
    return html;
}

function trackingBreakdownSection(breakdown, totalSecs) {
    if (!breakdown || !breakdown.length || !totalSecs) return '';
    var pcts = breakdown.map(function(b) { return Math.max(0, b.pct || 0); });
    var sum = pcts.reduce(function(a, b) { return a + b; }, 0);
    var widths = sum > 0
        ? pcts.map(function(p) { return (p / sum) * 100; })
        : pcts.map(function() { return 0; });
    var html = '<div class="track-section track-breakdown-section">';
    html += trackSecTitle('📊', 'توزیع زمان');
    html += '<div class="track-breakdown-card">';
    html += '<div class="track-breakdown-visual">';
    html += '<div class="track-breakdown-bar track-breakdown-bar-lg">';
    breakdown.forEach(function(b, idx) {
        var w = widths[idx];
        html += '<div class="track-breakdown-seg" style="width:' + w + '%;min-width:2px;background:' + trackColorForLabel(b.label) + '" title="' + esc(b.label) + ' · ' + pd(b.pct) + '٪"></div>';
    });
    html += '</div></div>';
    html += '<div class="track-breakdown-legend">';
    breakdown.forEach(function(b, idx) {
        html += '<div class="track-legend-item" style="--track-stagger:' + idx + '">' +
            '<span class="track-legend-dot" style="background:' + trackColorForLabel(b.label) + '"></span>' +
            '<span class="track-legend-label">' + esc(b.label) + '</span>' +
            '<span class="track-legend-bar-wrap"><span class="track-legend-bar" style="width:' + widths[idx] + '%;background:' + trackColorForLabel(b.label) + '"></span></span>' +
            '<span class="track-legend-val">' + esc(b.duration_label) + ' · ' + pd(b.pct) + '٪</span></div>';
    });
    html += '</div></div></div>';
    return html;
}

function renderTracking(t) {
    _dayTrackLabelColors = buildTrackingLabelColors(t.intervals || []);
    var session = t.session;
    var hasData = t.has_data;
    var dayTotalSecs = t.day_total_secs || 0;
    var dayTotalLabel = t.day_total_label || '۰۰:۰۰';
    var html = '<div class="track-page">';

    if (!hasData && !session) {
        html += trackingHeader(t);
        html += '<div class="page-glass-zone track-body">';
        html += '<div class="track-empty-hero" aria-hidden="true">' +
            '<div class="track-empty-rings"><span></span><span></span><span></span></div>' +
            '<div class="track-empty-icon">' + finEmoji('⏱️', 'lg') + '</div></div>';
        html += '<div class="empty-state track-empty">' +
            '<div class="empty-title">روز خود را ردیابی کنید</div>' +
            '<div class="empty-sub">هر فعالیت را ثبت کنید و در پایان روز ببینید وقتتان کجا رفته — با یک ضربه شروع کنید</div>' +
            '<button type="button" class="empty-btn track-start-btn" onclick="action(\'start_tracking\',{})">' +
            ico('play', 'ico') + ' شروع ردیابی</button></div>';
        html += '<div class="track-features">' +
            '<div class="track-feature"><span class="track-feature-icon">' + finEmoji('🎯', 'sm') + '</span><span>بازده روزانه</span></div>' +
            '<div class="track-feature"><span class="track-feature-icon">' + finEmoji('📊', 'sm') + '</span><span>نمودار توزیع</span></div>' +
            '<div class="track-feature"><span class="track-feature-icon">' + finEmoji('⚡', 'sm') + '</span><span>تعویض سریع</span></div>' +
            '</div>';
        html += '<div class="track-tips"><div class="track-tip">' + finEmoji('💡', 'sm') +
            ' عنوان را بنویسید یا از دکمه «انتخاب» یکی از فعالیت\u200cهای رایج را برگزینید</div></div>';
        return html + '</div></div>';
    }

    var sid = session ? session.id : null;
    var intervals = t.intervals || [];
    var earlierIntervals = t.earlier_intervals || [];
    var completedCount = t.completed_count || 0;
    var sessionCount = t.session_count || 0;

    if (session && session.is_active) {
        var activeInterval = null;
        var currentCompleted = [];
        for (var i = 0; i < intervals.length; i++) {
            if (intervals[i].session_id === sid && intervals[i].is_active) {
                activeInterval = intervals[i];
            } else if (intervals[i].session_id === sid && !intervals[i].is_active) {
                currentCompleted.push(intervals[i]);
            }
        }

        var heroHtml = '<div class="track-hero-in-header">';
        heroHtml += trackLiveTimerHtml(activeInterval ? activeInterval.started_epoch : null);
        heroHtml += '<div class="track-hero-stats">';
        heroHtml += '<div class="track-hero-stat">' + finEmoji('🕐', 'sm') + '<div><span class="track-stat-lbl">شروع</span><span class="track-stat-val">' + esc(session.started_label) + '</span></div></div>';
        heroHtml += '<div class="track-hero-stat">' + finEmoji('📋', 'sm') + '<div><span class="track-stat-lbl">بازه\u200cها</span><span class="track-stat-val">' + pd(completedCount) + '</span></div></div>';
        heroHtml += '<div class="track-hero-stat">' + finEmoji('⏳', 'sm') + '<div><span class="track-stat-lbl">کل امروز</span><span class="track-stat-val">' + esc(dayTotalLabel) + '</span></div></div>';
        heroHtml += '</div></div>';
        heroHtml += trackingActivePanel(activeInterval, { inHeader: true });
        heroHtml += trackingEfficiencyRow(t, { inHeader: true });

        html += trackingHeader(t, heroHtml, { live: true });

        html += '<div class="page-glass-zone track-body">';
        html += '<div class="track-actions">';
        html += '<button type="button" class="track-btn track-btn-switch" onclick="action(\'switch_tracking\',{session_id:' + sid + '})">';
        html += '<span class="track-btn-icon">⇄</span><span class="track-btn-text">تعویض فعالیت</span></button>';
        html += '<div class="track-actions-secondary">';
        html += '<button type="button" class="track-btn track-btn-stop" onclick="action(\'stop_tracking\',{session_id:' + sid + '})">';
        html += ico('stop', 'ico') + '<span>توقف</span></button>';
        html += '<button type="button" class="track-btn track-btn-delete" onclick="action(\'delete_tracking_session\',{session_id:' + sid + '})">';
        html += '<span aria-hidden="true">🗑</span><span>حذف</span></button>';
        html += '</div></div>';

        if (currentCompleted.length) {
            html += '<div class="track-section"><div class="track-timeline">';
            html += trackSecTitle('🕓', 'بازه\u200cهای این دور');
            for (var j = currentCompleted.length - 1; j >= 0; j--) {
                html += trackingIntervalCard(currentCompleted[j], dayTotalSecs, { stagger: currentCompleted.length - 1 - j });
            }
            html += '</div></div>';
        }

        if (earlierIntervals.length) {
            html += '<div class="track-section"><div class="track-timeline">';
            html += trackSecTitle('📅', 'ردیابی\u200cهای قبلی امروز');
            for (var k = earlierIntervals.length - 1; k >= 0; k--) {
                html += trackingIntervalCard(earlierIntervals[k], dayTotalSecs, { stagger: earlierIntervals.length - 1 - k });
            }
            html += '</div></div>';
        }
    } else {
        var sessionNote = sessionCount > 1
            ? '<div class="track-hero-range">' + pd(sessionCount) + ' دور ردیابی</div>' : '';
        var summaryHero = '<div class="track-hero-in-header track-hero-summary">' +
            '<div class="track-hero-label">مجموع امروز</div>' +
            '<div class="track-hero-total">' + esc(dayTotalLabel) + '</div>' +
            sessionNote +
            '</div>';
        summaryHero += trackingEfficiencyRow(t, { inHeader: true });
        html += trackingHeader(t, summaryHero);

        html += '<div class="page-glass-zone track-body">';
        html += trackingBreakdownSection(t.breakdown, dayTotalSecs);

        html += '<div class="track-section"><div class="track-timeline">';
        html += trackSecTitle('🗓️', 'جدول زمانی امروز');
        var timelineIdx = 0;
        intervals.forEach(function(iv2) {
            if (!iv2.duration_label) return;
            html += trackingIntervalCard(iv2, dayTotalSecs, { stagger: timelineIdx });
            timelineIdx += 1;
        });
        html += '</div></div>';

        html += '<div class="track-restart-wrap">';
        html += '<button type="button" class="track-restart-btn" onclick="action(\'start_tracking\',{})">' +
            '<span class="track-restart-plus" aria-hidden="true">+</span> شروع ردیابی جدید</button></div>';
    }

    html += '</div></div>';
    return html;
}

function renderNav(screen) {
    function item(id, label, iconName) {
        var cls = screen === id ? 'nav-btn active nav-' + id : 'nav-btn';
        var current = screen === id ? ' aria-current="page"' : '';
        return '<button type="button" onclick="action(\'navigate\',{screen:\'' + id + '\'})" class="' + cls + '"' + current +
            ' aria-label="' + label + '"><span class="nav-icon" aria-hidden="true">' + (ICON[iconName] || '') + '</span>' + label + '</button>';
    }
    return item('home', 'امروز', 'home') +
        item('tracking', 'ردیابی', 'tracking') +
        item('finance', 'مالی', 'wallet') +
        item('investments', 'سرمایه', 'invest') +
        item('projects', 'پروژه\u200cها', 'folder') +
        item('analytics', 'آمار', 'chart');
}

/* Main render */
function renderApp(state) {
    var screenChanged = window._renderedScreen !== state.screen;
    if (!isModalVisible() && screenChanged) {
        closeProjectSheet();
        closeActivityPicker();
    }

    flushPendingNote();
    flushPendingSearch();
    flushPendingTrackLabels();

    var trackLabelDrafts = {};
    document.querySelectorAll('.track-label-input').forEach(function(el) {
        if (el.dataset.intervalId) trackLabelDrafts[el.dataset.intervalId] = el.value;
    });

    window._categories = state.finance_categories || [];
    window._investCategories = state.investment_categories || [];
    window._investTaxonomy = state.investment_taxonomy || window._investTaxonomy || { risks: [], markets: [], assets: {} };
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
    else if (state.screen === 'investments' && state.investments) html = renderInvestmentsScreen(state.investments);
    else if (state.screen === 'installments' && state.installments) html = renderInstallments(state.installments);
    else if (state.screen === 'analytics' && state.analytics) html = renderAnalytics(state.analytics);
    else if (state.screen === 'settings' && state.settings) html = renderSettings(state.settings);
    else if (state.screen === 'recurring' && state.recurring) html = renderRecurring(state.recurring);
    else if (state.screen === 'projects' && state.projects) html = renderProjects(state.projects);
    else if (state.screen === 'project_detail' && state.project_detail) html = renderProjectDetail(state.project_detail);
    else if (state.screen === 'important_dates' && state.important_dates) html = renderImportantDates(state.important_dates);
    else if (state.screen === 'tracking' && state.tracking) html = renderTracking(state.tracking);

    window._lastState = state;

    var focused = document.activeElement;
    var restoreSearch = focused && focused.classList && focused.classList.contains('search-input');
    var searchCaret = restoreSearch ? focused.selectionStart : null;
    var restoreNote = focused && focused.id === 'daily-note';
    var noteCaret = restoreNote ? focused.selectionStart : null;
    var restoreImport = focused && focused.id === 'import-ta';
    var importCaret = restoreImport ? focused.selectionStart : null;
    var restoreExport = focused && focused.id === 'export-ta';
    var exportCaret = restoreExport ? focused.selectionStart : null;
    var restoreTrackLabel = focused && focused.classList && focused.classList.contains('track-label-input');
    var trackLabelIntervalId = restoreTrackLabel ? focused.dataset.intervalId : null;
    var trackLabelCaret = restoreTrackLabel ? focused.selectionStart : null;
    var restoreTrackActSearch = focused && focused.classList && focused.classList.contains('track-act-search');
    var trackActSearchValue = restoreTrackActSearch ? focused.value : null;
    var trackActSearchCaret = restoreTrackActSearch ? focused.selectionStart : null;
    var restoreModal = isModalVisible() && focused && focused.id && focused.id.indexOf('mf-') === 0;
    var modalFocusId = restoreModal ? focused.id : null;
    var modalCaret = restoreModal && focused.selectionStart != null ? focused.selectionStart : null;

    window._renderedScreen = state.screen;

    root.innerHTML = html;

    Object.keys(trackLabelDrafts).forEach(function(id) {
        var el = document.querySelector('.track-label-input[data-interval-id="' + id + '"]');
        if (el) el.value = trackLabelDrafts[id];
    });

    if (screenChanged) {
        root.classList.add('screen-enter');
        requestAnimationFrame(function() { root.classList.remove('screen-enter'); });
    }

    if (restoreModal && modalFocusId) {
        var modalInput = document.getElementById(modalFocusId);
        if (modalInput) {
            modalInput.focus();
            if (modalCaret != null) {
                try { modalInput.setSelectionRange(modalCaret, modalCaret); } catch (e) {}
            }
            syncKeyboardLayout();
            ensureFieldVisible(modalInput);
        }
    } else if (restoreSearch) {
        var searchInput = document.querySelector('.search-input');
        if (searchInput) {
            searchInput.focus();
            if (searchCaret != null) {
                try { searchInput.setSelectionRange(searchCaret, searchCaret); } catch (e) {}
            }
            syncKeyboardLayout();
            ensureFieldVisible(searchInput);
        }
    } else if (restoreNote) {
        var noteInput = document.getElementById('daily-note');
        if (noteInput) {
            noteInput.focus();
            if (noteCaret != null) {
                try { noteInput.setSelectionRange(noteCaret, noteCaret); } catch (e) {}
            }
            syncKeyboardLayout();
            ensureFieldVisible(noteInput);
        }
    } else if (restoreImport) {
        var importInput = document.getElementById('import-ta');
        if (importInput) {
            importInput.focus();
            if (importCaret != null) {
                try { importInput.setSelectionRange(importCaret, importCaret); } catch (e) {}
            }
            syncKeyboardLayout();
            ensureFieldVisible(importInput);
        }
    } else if (restoreExport) {
        var exportInput = document.getElementById('export-ta');
        if (exportInput && exportInput.style.display !== 'none') {
            exportInput.focus();
            if (exportCaret != null) {
                try { exportInput.setSelectionRange(exportCaret, exportCaret); } catch (e) {}
            }
            syncKeyboardLayout();
            ensureFieldVisible(exportInput);
        }
    } else if (restoreTrackActSearch && isActivityPickerVisible()) {
        var actSearch = document.querySelector('.track-act-search');
        if (actSearch) {
            if (trackActSearchValue != null) actSearch.value = trackActSearchValue;
            actSearch.focus();
            if (trackActSearchCaret != null) {
                try { actSearch.setSelectionRange(trackActSearchCaret, trackActSearchCaret); } catch (e) {}
            }
            syncKeyboardLayout();
            ensureFieldVisible(actSearch);
        }
    } else if (restoreTrackLabel && trackLabelIntervalId && !isActivityPickerVisible()) {
        var trackInput = document.querySelector('.track-label-input[data-interval-id="' + trackLabelIntervalId + '"]');
        if (trackInput) {
            trackInput.focus();
            if (trackLabelCaret != null) {
                try { trackInput.setSelectionRange(trackLabelCaret, trackLabelCaret); } catch (e) {}
            }
            syncKeyboardLayout();
            ensureFieldVisible(trackInput);
        }
    }

    document.body.classList.toggle(
        'has-bottom-nav',
        state.screen === 'home' || state.screen === 'finance'
            || state.screen === 'investments'
            || state.screen === 'analytics' || state.screen === 'projects'
            || state.screen === 'tracking'
    );

    if (state.screen === 'settings' && window._exportData) {
        var exportTa = document.getElementById('export-ta');
        if (exportTa) exportTa.value = window._exportData;
    }

    var nav = document.getElementById('bottom-nav');
    if (nav && (state.screen === 'home' || state.screen === 'finance' || state.screen === 'investments' || state.screen === 'analytics' || state.screen === 'projects' || state.screen === 'tracking')) {
        nav.innerHTML = renderNav(state.screen);
        nav.style.display = 'flex';
    } else if (nav) {
        nav.style.display = 'none';
    }

    if (state.toast) showToast(state.toast.message, state.toast.type);

    if (state.screen === 'home' && state.home) {
        applyHomeSearchFilter(
            window._liveSearchQuery != null ? window._liveSearchQuery : (state.home.search || '')
        );
    }

    syncTrackingTicker();

    if (isModalVisible()) {
        syncBodyScrollLock();
        syncModalViewport();
        syncKeyboardLayout();
    }
}

/* Mobile keyboard — keep text fields visible above the virtual keyboard */
var KEYBOARD_THRESHOLD = 80;
var _modalOpenVvHeight = null;
var _sheetOpenVvHeight = null;

function lockBodyForModal() {
    document.documentElement.classList.add('modal-open');
    document.body.classList.add('modal-open');
}

function unlockBodyFromModal() {
    document.documentElement.classList.remove('modal-open');
    document.body.classList.remove('modal-open');
}

function isModalVisible() {
    var modal = document.getElementById('modal');
    return !!(modal && modal.style.display !== 'none');
}

function isProjectSheetVisible() {
    var sheet = document.getElementById('proj-sheet');
    return !!(sheet && sheet.style.display !== 'none');
}

function isActivityPickerVisible() {
    var sheet = document.getElementById('track-act-sheet');
    return !!(sheet && sheet.style.display !== 'none');
}

function syncBodyScrollLock() {
    if (isModalVisible() || isProjectSheetVisible() || isActivityPickerVisible()) {
        lockBodyForModal();
    } else {
        unlockBodyFromModal();
    }
}

function getModalScrollContainer() {
    return document.getElementById('modal-body') || document.getElementById('modal-fields');
}

function isMobileTouch() {
    return window.matchMedia('(hover: none) and (pointer: coarse)').matches;
}

function isTextInput(el) {
    return !!(el && el.matches && el.matches('input:not([type="hidden"]), textarea, select'));
}

function viewportHandlesKeyboard() {
    var vv = window.visualViewport;
    if (!vv) return false;
    return (window.innerHeight - vv.height - vv.offsetTop) >= KEYBOARD_THRESHOLD;
}

function keyboardHeight() {
    var vv = window.visualViewport;
    if (vv) {
        var gap = Math.max(0, window.innerHeight - vv.height - vv.offsetTop);
        if (gap >= KEYBOARD_THRESHOLD) return gap;
        var baseline = _sheetOpenVvHeight || _modalOpenVvHeight || window.innerHeight;
        var measured = Math.max(0, baseline - vv.height);
        if (measured >= KEYBOARD_THRESHOLD) return measured;
        return 0;
    }
    if (!isMobileTouch() || !isTextInput(document.activeElement)) return 0;
    return Math.round(window.innerHeight * 0.42);
}

function layoutKeyboardInset(kb) {
    if (viewportHandlesKeyboard()) return 0;
    return kb;
}

function visibleViewportHeight() {
    var vv = window.visualViewport;
    if (vv && viewportHandlesKeyboard()) return vv.height;
    var kb = keyboardHeight();
    if (vv) {
        if (kb >= KEYBOARD_THRESHOLD && vv.height >= window.innerHeight - kb - 20) {
            return window.innerHeight - kb;
        }
        return vv.height;
    }
    if (kb >= KEYBOARD_THRESHOLD) return window.innerHeight - kb;
    return window.innerHeight;
}

function visibleViewportBounds() {
    var vv = window.visualViewport;
    if (vv && viewportHandlesKeyboard()) {
        return { top: vv.offsetTop + 12, bottom: vv.offsetTop + vv.height - 16 };
    }
    var kb = keyboardHeight();
    var top = vv ? vv.offsetTop + 12 : 12;
    var bottom = vv ? vv.offsetTop + vv.height - 16 : window.innerHeight - 16;
    if (kb >= KEYBOARD_THRESHOLD && (!vv || vv.height >= window.innerHeight - kb - 20)) {
        bottom = Math.min(bottom, window.innerHeight - kb - 16);
    }
    return { top: top, bottom: bottom };
}

function syncModalViewport() {
    if (!isModalVisible()) return;
    var root = document.documentElement;
    var vv = window.visualViewport;
    var kb = keyboardHeight();
    if (!vv) {
        var fallbackH = window.innerHeight - (kb >= KEYBOARD_THRESHOLD && !viewportHandlesKeyboard() ? kb : 0);
        root.style.setProperty('--vv-top', '0px');
        root.style.setProperty('--vv-left', '0px');
        root.style.setProperty('--vv-width', window.innerWidth + 'px');
        root.style.setProperty('--vv-height', fallbackH + 'px');
        return;
    }
    var height = vv.height;
    if (!viewportHandlesKeyboard() && kb >= KEYBOARD_THRESHOLD && height >= window.innerHeight - kb - 20) {
        height = window.innerHeight - kb;
    }
    root.style.setProperty('--vv-top', vv.offsetTop + 'px');
    root.style.setProperty('--vv-left', vv.offsetLeft + 'px');
    root.style.setProperty('--vv-width', vv.width + 'px');
    root.style.setProperty('--vv-height', height + 'px');
}

function syncSheetViewport() {
    if (!isActivityPickerVisible()) return;
    var root = document.documentElement;
    var vv = window.visualViewport;
    var kb = keyboardHeight();
    if (!vv) {
        var fallbackH = window.innerHeight - (kb >= KEYBOARD_THRESHOLD && !viewportHandlesKeyboard() ? kb : 0);
        root.style.setProperty('--vv-top', '0px');
        root.style.setProperty('--vv-left', '0px');
        root.style.setProperty('--vv-width', window.innerWidth + 'px');
        root.style.setProperty('--vv-height', fallbackH + 'px');
        return;
    }
    var height = vv.height;
    if (!viewportHandlesKeyboard() && kb >= KEYBOARD_THRESHOLD && height >= window.innerHeight - kb - 20) {
        height = window.innerHeight - kb;
    }
    root.style.setProperty('--vv-top', vv.offsetTop + 'px');
    root.style.setProperty('--vv-left', vv.offsetLeft + 'px');
    root.style.setProperty('--vv-width', vv.width + 'px');
    root.style.setProperty('--vv-height', height + 'px');
}

function syncKeyboardLayout() {
    var kb = keyboardHeight();
    var open = kb >= KEYBOARD_THRESHOLD;
    var root = document.documentElement;
    root.style.setProperty('--keyboard-inset', open ? layoutKeyboardInset(kb) + 'px' : '0px');
    root.style.setProperty('--visual-vh', visibleViewportHeight() + 'px');
    document.body.classList.toggle('kb-open', open);
    if (document.body.classList.contains('modal-open')) {
        syncModalViewport();
    }
    if (isActivityPickerVisible()) {
        syncSheetViewport();
    }
}

function scrollFieldInContainer(el, container) {
    var bounds = visibleViewportBounds();
    var elRect = el.getBoundingClientRect();
    var contRect = container.getBoundingClientRect();
    var limitBottom = Math.min(contRect.bottom, bounds.bottom);
    var limitTop = Math.max(contRect.top, bounds.top);
    if (elRect.bottom > limitBottom) {
        container.scrollTop += elRect.bottom - limitBottom + 24;
    } else if (elRect.top < limitTop) {
        container.scrollTop -= limitTop - elRect.top + 12;
    }
}

function getScrollRoot() {
    return document.scrollingElement || document.documentElement;
}

function scrollFieldIntoView(el) {
    var bounds = visibleViewportBounds();
    var rect = el.getBoundingClientRect();
    var delta = 0;
    if (rect.bottom > bounds.bottom) {
        delta = rect.bottom - bounds.bottom + 24;
    } else if (rect.top < bounds.top) {
        delta = rect.top - bounds.top - 12;
    }
    if (!delta) return;
    getScrollRoot().scrollTop += delta;
}

function ensureFieldVisible(el) {
    if (!el || !document.contains(el)) return;
    if (!isTextInput(el)) return;
    [0, 50, 180, 400, 700].forEach(function(ms) {
        setTimeout(function() {
            if (!document.contains(el)) return;
            syncKeyboardLayout();
            var modalFields = getModalScrollContainer();
            if (modalFields && modalFields.contains(el)) {
                scrollFieldInContainer(el, modalFields);
            } else {
                scrollFieldIntoView(el);
            }
        }, ms);
    });
}

(function initMobileKeyboard() {
    function bind() {
        syncKeyboardLayout();
        if (window.visualViewport) {
            window.visualViewport.addEventListener('resize', syncKeyboardLayout);
            window.visualViewport.addEventListener('scroll', syncKeyboardLayout);
        }
        window.addEventListener('resize', syncKeyboardLayout);
        document.addEventListener('focusin', function(e) {
            syncKeyboardLayout();
            ensureFieldVisible(e.target);
        });
        document.addEventListener('click', function(e) {
            if (isTextInput(e.target)) {
                setTimeout(function() { ensureFieldVisible(e.target); }, 120);
            }
        }, true);
        document.addEventListener('focusout', function() {
            setTimeout(syncKeyboardLayout, 150);
        });
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', bind);
    } else {
        bind();
    }
    window.addEventListener('pagehide', function() {
        if (typeof flushPendingNote === 'function') flushPendingNote();
        if (typeof flushPendingSearch === 'function') flushPendingSearch();
        if (typeof flushPendingTrackLabels === 'function') flushPendingTrackLabels();
    });
})();
