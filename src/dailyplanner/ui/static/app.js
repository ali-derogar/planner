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
    required: function(v) { return v.trim().length > 0; },
};

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
        var val = el ? el.value : '';
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
            '<a href="javascript:void(0)" onclick="showModal({title:\'تنظیم تخمین\',cmd:\'set_estimated\',params:{id:' + t.id + '},fields:[{label:\'مدت\',key:\'value\',placeholder:\'00:00:00\',validate:\'hms\'}]})" class="chip chip-edit">ویرایش</a></div>' +
            '<div class="chips">' +
            '<a href="javascript:void(0)" onclick="action(\'set_useful\',{id:' + t.id + ',value:\'true\'})" class="chip ' + uCls + '">✔ مفید</a>' +
            '<a href="javascript:void(0)" onclick="action(\'set_useful\',{id:' + t.id + ',value:\'false\'})" class="chip ' + nuCls + '">✖ نامفید</a>' +
            '<a href="javascript:void(0)" onclick="showModal({title:\'ویرایش عنوان\',cmd:\'edit_title\',params:{id:' + t.id + '},fields:[{label:\'عنوان\',key:\'value\',value:\'' + escJs(t.title) + '\',validate:\'required\'}]})" class="chip chip-edit">✎ عنوان</a>' +
            '<a href="javascript:void(0)" onclick="showModal({title:\'ویرایش مدت\',cmd:\'set_duration\',params:{id:' + t.id + '},fields:[{label:\'مدت\',key:\'value\',validate:\'hms\'}]})" class="chip chip-edit">⏱ مدت</a>' +
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
    var recurBtn = '<button class="icon-btn" onclick="action(\'navigate\',{screen:\'recurring\'})" title="تکراری">★ ' + pd(h.recurring_count) + '</button>';
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
    var rows = fin.entries.map(function(e) {
        var cls = e.type === 'income' ? 'fin-type-income' : 'fin-type-expense';
        var arrow = e.type === 'income' ? '↑' : '↓';
        return '<div class="fin-entry">' +
            '<span class="' + cls + '">' + arrow + ' ' + esc(e.title) + ' <span class="fin-cat">' + esc(e.category) + '</span></span>' +
            '<span>' + esc(e.amount_fmt) + '</span>' +
            '<button class="fin-edit" onclick="showModal({title:\'ویرایش\',cmd:\'edit_finance\',params:{id:' + e.id + '},fields:[{label:\'عنوان\',key:\'title\',value:\'' + escJs(e.title) + '\',validate:\'required\'},{label:\'مبلغ\',key:\'amount\',value:\'' + e.amount + '\',type:\'number\',validate:\'amount\'},{label:\'دسته\',key:\'category\',type:\'select\',value:\'' + escJs(e.category) + '\',options:window._categories}]})">✎</button>' +
            '<button class="fin-del" onclick="action(\'delete_finance\',{id:' + e.id + '})">×</button></div>';
    }).join('');
    if (!rows) rows = '<div class="empty-mini">هیچ ورودی ندارید</div>';
    var balCls = fin.balance >= 0 ? 'fin-income' : 'fin-expense';
    return '<div class="section"><div class="sec-header"><span class="sec-title">امور مالی</span><div class="sec-actions">' +
        '<a href="javascript:void(0)" onclick="showAddFinance(\'income\')" class="btn-sm-green">+ درآمد</a>' +
        '<a href="javascript:void(0)" onclick="showAddFinance(\'expense\')" class="btn-sm-red">+ هزینه</a></div></div>' +
        '<div class="fin-donut-row"><div class="fin-donut" style="--income-pct:' + (fin.income + fin.expense ? fin.income / (fin.income + fin.expense) * 100 : 50) + '"></div>' +
        '<div class="fin-summary"><span class="fin-income">درآمد: ' + esc(fin.income_fmt) + '</span>' +
        '<span class="' + balCls + '">موجودی: ' + esc(fin.balance_fmt) + '</span>' +
        '<span class="fin-expense">هزینه: ' + esc(fin.expense_fmt) + '</span></div></div>' + rows + '</div>';
}

function showAddFinance(type) {
    showModal({
        title: type === 'income' ? 'افزودن درآمد' : 'افزودن هزینه',
        cmd: 'add_finance',
        params: { type: type },
        fields: [
            { label: 'عنوان', key: 'title', validate: 'required' },
            { label: 'مبلغ (تومان)', key: 'amount', type: 'number', validate: 'amount' },
            { label: 'دسته', key: 'category', type: 'select', value: 'عمومی', options: window._categories },
        ],
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
        '<a href="javascript:void(0)" onclick="showModal({title:\'ساعت خواب\',cmd:\'set_sleep\',fields:[{label:\'HH:MM\',key:\'value\',value:\'' + w.sleep_raw + '\',validate:\'hm\'}]})" class="well-btn"><span class="well-lbl">خواب</span><span class="well-val">' + esc(w.sleep) + '</span></a>' +
        '<a href="javascript:void(0)" onclick="showModal({title:\'ساعت بیداری\',cmd:\'set_wake\',fields:[{label:\'HH:MM\',key:\'value\',value:\'' + w.wake_raw + '\',validate:\'hm\'}]})" class="well-btn"><span class="well-lbl">بیداری</span><span class="well-val">' + esc(w.wake) + '</span></a>' +
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

function renderNav(screen) {
    var home = screen === 'home' ? 'nav-btn active' : 'nav-btn';
    var anal = screen === 'analytics' ? 'nav-btn active' : 'nav-btn';
    return '<a href="javascript:void(0)" onclick="action(\'navigate\',{screen:\'home\'})" class="' + home + '"><span class="nav-icon">🏠</span>امروز</a>' +
        '<a href="javascript:void(0)" onclick="action(\'navigate\',{screen:\'analytics\'})" class="' + anal + '"><span class="nav-icon">📊</span>آمار</a>';
}

/* Main render */
function renderApp(state) {
    window._categories = state.finance_categories || [];
    window._moodEmojis = state.mood_emojis || [];
    document.documentElement.setAttribute('data-theme', state.theme || 'dark');

    var root = document.getElementById('app-root');
    if (!root) return;

    var html = '';
    if (state.screen === 'home' && state.home) html = renderHome(state.home);
    else if (state.screen === 'analytics' && state.analytics) html = renderAnalytics(state.analytics);
    else if (state.screen === 'settings' && state.settings) html = renderSettings(state.settings);
    else if (state.screen === 'recurring' && state.recurring) html = renderRecurring(state.recurring);

    root.innerHTML = html;

    var nav = document.getElementById('bottom-nav');
    if (nav && (state.screen === 'home' || state.screen === 'analytics')) {
        nav.innerHTML = renderNav(state.screen);
        nav.style.display = 'flex';
    } else if (nav) {
        nav.style.display = 'none';
    }

    if (state.toast) showToast(state.toast.message, state.toast.type);
}
