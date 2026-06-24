#!/usr/bin/env node
/* Audit all render helpers for div balance, tokens, XSS, header/body nesting. */
const fs = require('fs');
const vm = require('vm');
const path = require('path');

const appJs = fs.readFileSync(path.join(__dirname, '../src/dailyplanner/ui/static/app.js'), 'utf8');

class El {
    constructor(tag) {
        this.tagName = (tag || 'div').toUpperCase();
        this.children = [];
        this.innerHTML = '';
        this.id = '';
        this.style = { display: '', setProperty() {}, removeProperty() {} };
        this.classList = {
            _c: new Set(),
            add(...a) { a.forEach((x) => this._c.add(x)); },
            remove(...a) { a.forEach((x) => this._c.delete(x)); },
            toggle(c, on) {
                if (on === undefined) {
                    this._c.has(c) ? this._c.delete(c) : this._c.add(c);
                } else if (on) {
                    this._c.add(c);
                } else {
                    this._c.delete(c);
                }
            },
            contains(c) { return this._c.has(c); },
        };
        this.dataset = {};
        this.addEventListener = () => {};
        this.appendChild = (c) => { this.children.push(c); return c; };
        this.querySelector = () => null;
        this.querySelectorAll = () => [];
        this.setAttribute = () => {};
        this.getAttribute = () => null;
        this.focus = () => {};
        this.blur = () => {};
    }
}

const store = {};
['app-root', 'bottom-nav', 'toast', 'modal', 'modal-box', 'modal-title', 'modal-fields', 'modal-error', 'modal-body']
    .forEach((id) => { const e = new El(); e.id = id; store[id] = e; });

const docEl = new El('html');
docEl.style = { setProperty() {}, removeProperty() {} };
const body = new El('body');
body.classList = docEl.classList;
const doc = {
    documentElement: docEl,
    body,
    scrollingElement: docEl,
    getElementById: (id) => store[id],
    querySelector: () => null,
    querySelectorAll: () => [],
    createElement: (t) => new El(t),
    addEventListener: () => {},
    activeElement: null,
};

const ctx = {
    window: {
        _actions: [],
        innerHeight: 800,
        innerWidth: 400,
        matchMedia: () => ({ matches: false }),
        addEventListener: () => {},
        visualViewport: null,
        _exportData: '',
        _importDraft: '',
        _categories: ['عمومی'],
        _investCategories: ['سایر'],
        _moodEmojis: ['😀', '🙂'],
        _dateCategories: ['سایر'],
        _projectColors: ['#5E5CE6'],
        requestAnimationFrame: (fn) => fn(),
        setTimeout: (fn, ms) => { if (!ms || ms <= 150) fn(); return 1; },
        clearTimeout: () => {},
    },
    document: doc,
    console,
    setTimeout: (fn, ms) => { if (!ms || ms <= 150) fn(); return 1; },
    clearTimeout: () => {},
    requestAnimationFrame: (fn) => fn(),
};
ctx.window.document = doc;
vm.runInContext(appJs, vm.createContext(ctx));

function balanceDivs(html) {
    let depth = 0;
    const re = /<\/?div[\s>]/g;
    let m;
    while ((m = re.exec(html))) {
        if (m[0].startsWith('</')) {
            if (depth <= 0) return -1;
            depth--;
        } else {
            depth++;
        }
    }
    return depth;
}

function bodyOutsideHeader(html, bodyCls, headerCls) {
    const stack = [];
    let bad = false;
    const re = /<\/?div[^>]*>/g;
    let m;
    while ((m = re.exec(html))) {
        const cls = (m[0].match(/class="([^"]+)"/) || [])[1] || '';
        if (!m[0].startsWith('</')) {
            if (cls.includes(bodyCls) && stack.some((s) => s.includes(headerCls))) bad = true;
            stack.push(cls);
        } else {
            stack.pop();
        }
    }
    return !bad;
}

const task = {
    id: 1, title: 't\n<script>', display_fmt: '25:00:00', estimated_fmt: '—',
    estimated: 0, display_sec: 90000, progress: 0, is_useful: null, is_starred: false,
    is_running: false, is_expanded: true, remaining_fmt: null,
};

const tests = [
    ['renderHome', () => ctx.renderHome({
        date_label: 't', is_today: true, search: 'q', show_calendar: true,
        calendar: { month_name: 't', year: 1404, weekday_offset: 0, cells: [{ day: 1, date: '2026-06-22', eff: 50, has_data: true }] },
        useful_fmt: '1h', not_useful_fmt: '0', efficiency: 100, tasks: [task],
        wellness: { sleep: '22:00', wake: '07:00', sleep_dur: '9h', mood: 5, sleep_raw: '22:00', wake_raw: '07:00' },
        daily_note: 'note', recurring_count: 1, urgent_dates_count: 2,
    })],
    ['renderHome-empty', () => ctx.renderHome({
        date_label: 't', is_today: false, search: '', show_calendar: false,
        useful_fmt: '0', not_useful_fmt: '0', efficiency: 0, tasks: [],
        wellness: { sleep: '—', wake: '—', sleep_dur: '—', mood: null, sleep_raw: '', wake_raw: '' },
        daily_note: '', recurring_count: 0, urgent_dates_count: 0,
    })],
    ['renderAnalytics', () => ctx.renderAnalytics({
        period: 7, start_label: 'a', end_label: 'b',
        stats: { streak: 1, eff: 50, total_fmt: '1h', useful_fmt: '30m', not_useful_fmt: '30m', income_fmt: '0', expense_fmt: '0', investment_fmt: '0', balance_fmt: '0', avg_mood: '5', avg_sleep: '8h' },
        chart_points: [0, 50, 100], heatmap: [{ date: '2026-01-01', eff: 50, total: 3600 }],
        days: [{ date_label: 'd', eff: 50, total_fmt: '1h', useful_fmt: '30m', not_useful_fmt: '30m' }],
    })],
    ['renderFinanceScreen', () => ctx.renderFinanceScreen({
        month_label: 't', is_current_month: false,
        totals: { balance: 100, balance_fmt: '100', income: 200, expense: 100, investment: 50, income_fmt: '200', expense_fmt: '100', investment_fmt: '50' },
        entries: [{ id: 1, title: 'x', amount_fmt: '100', category: 'غذا', type: 'expense', date_label: '1' }],
        by_category: [{ category: 'غذا', expense: 100, expense_fmt: '100', budget: 200, budget_fmt: '200', used_pct: 50, over_budget: false }],
        daily_series: [{ date_label: '1', income_fmt: '0', expense_fmt: '100', investment_fmt: '0', net: 0, net_fmt: '0' }],
        chart: { has_data: true, income: [1, 2], expense: [1, 1], balance: [0, 1], investment: [0, 0] },
        installments: { count: 1, items: [{ id: 1, title: 'loan', amount_fmt: '10', remaining_fmt: '50', is_settled: false, paid_this_month: false }], total_unpaid_fmt: '50' },
    })],
    ['renderProjects', () => ctx.renderProjects({
        list: [
            { id: 1, title: 'P', color: '#5E5CE6', progress: 50, done: 1, total: 2, is_done: false, deadline_label: '', deadline_overdue: false },
            { id: 2, title: 'D', color: '#5E5CE6', progress: 100, done: 2, total: 2, is_done: true, deadline_label: '', deadline_overdue: false },
        ],
        colors: ['#5E5CE6'],
    })],
    ['renderProjects-empty', () => ctx.renderProjects({ list: [], colors: ['#5E5CE6'] })],
    ['renderProjectDetail', () => ctx.renderProjectDetail({
        id: 1, title: 'P', color: '#5E5CE6', progress: 50, done: 0, total: 1, is_done: false,
        deadline_label: '', deadline_overdue: false, tasks: [{ id: 1, title: 't', is_done: false }], colors: ['#5E5CE6'],
    })],
    ['renderTracking-empty', () => ctx.renderTracking({ has_data: false, session: null, date_label: 't', intervals: [] })],
    ['renderTracking-active', () => ctx.renderTracking({
        has_data: true, session: { id: 1, is_active: true, started_label: '10:00' }, date_label: 't',
        intervals: [{ id: 1, session_id: 1, is_active: true, started_label: '10:00', started_epoch: 1 }],
        day_total_secs: 100, day_total_label: '1m', completed_count: 0, session_count: 1, efficiency: 50, useful_label: '1h', not_useful_label: '0',
    })],
    ['renderTracking-done', () => ctx.renderTracking({
        has_data: true, session: { id: 1, is_active: false }, date_label: 't',
        intervals: [{ id: 1, session_id: 1, is_active: false, started_label: '10:00', ended_label: '11:00', duration_label: '1h', duration_secs: 3600, is_useful: true }],
        day_total_secs: 3600, day_total_label: '1h', completed_count: 1, session_count: 1, efficiency: 80, useful_label: '1h', not_useful_label: '0',
        breakdown: [{ label: 'work', pct: 100, duration_label: '1h' }], earlier_intervals: [],
    })],
    ['renderSettings', () => ctx.renderSettings({ theme: 'dark', export_path: '/x/backup.json', backup_summary: { tasks: 1, finance: 0, notes: 0, projects: 0, installments: 0, important_dates: 0, recurring: 0 } })],
    ['renderRecurring', () => ctx.renderRecurring([{ id: 1, title: 'daily' }])],
    ['renderInstallments', () => ctx.renderInstallments({
        list: [{
            id: 1, title: 'loan', amount_fmt: '10', remaining_fmt: '50', progress: 50,
            paid_count: 1, total_count: 6, is_settled: false, is_overdue: false,
            due_label: 'ماه جاری', paid_this_month: false,
        }],
        month_label: 't', month_total_due_fmt: '10', month_total_unpaid_fmt: '10', total_remaining_fmt: '50',
    })],
    ['renderImportantDates', () => ctx.renderImportantDates({ items: [{ id: 1, title: 'bday', date_label: '1', category: 'سایر', urgency: 'urgent', countdown: '۵ روز مانده', date_fmt: '1404/01/01', repeat_type: 'none', is_repeating: false }], categories: ['سایر'] })],
    ['renderCalendar', () => ctx.renderCalendar({ month_name: 't', year: 1404, weekday_offset: 0, cells: [{ day: 1, date: '2026-06-22', eff: 50, has_data: true }] }, '2026-06-22')],
    ['taskCard', () => ctx.taskCard(task)],
    ['trackingIntervalCard', () => ctx.trackingIntervalCard({ id: 1, is_active: false, label: 'work', started_label: '10:00', ended_label: '11:00', duration_label: '1h', duration_secs: 3600, is_useful: true }, 3600, { stagger: 0 })],
    ['trackingHeader', () => ctx.trackingHeader({ date_label: 't' }, '<div>hero</div>', { live: true })],
];

const headerBody = [
    ['renderHome', 'home-body', 'home-header'],
    ['renderFinanceScreen', 'fin-body', 'fin-header'],
    ['renderAnalytics', 'analytics-body', 'analytics-header'],
    ['renderProjects', 'proj-body', 'proj-header'],
    ['renderTracking-active', 'track-actions', 'track-header'],
];

const errors = [];
for (const [name, fn] of tests) {
    try {
        const html = fn();
        const bal = balanceDivs(html);
        if (bal !== 0) errors.push(`${name}: div imbalance ${bal}`);
        if (!html || html.length < 5) errors.push(`${name}: empty`);
        if (/undefined|NaN|\[object Object\]/.test(html)) errors.push(`${name}: bad token`);
        if (html.includes('<script>')) errors.push(`${name}: XSS`);
    } catch (e) {
        errors.push(`${name}: ${e.message}`);
    }
}

for (const [name, bodyCls, headerCls] of headerBody) {
    const fn = tests.find((t) => t[0] === name)[1];
    const html = fn();
    const outside = bodyOutsideHeader(html, bodyCls, headerCls);
    if (outside === false) errors.push(`${name}: ${bodyCls} nested inside ${headerCls}`);
}

if (errors.length) {
    console.error(errors.join('\n'));
    process.exit(1);
}
console.log(`OK: ${tests.length} render checks`);
