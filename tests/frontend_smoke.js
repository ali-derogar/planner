#!/usr/bin/env node
/* Smoke-test SPA render helpers (no jsdom). */
const fs = require('fs');
const vm = require('vm');
const path = require('path');

const rootDir = path.join(__dirname, '..');
const appJs = fs.readFileSync(path.join(rootDir, 'src/dailyplanner/ui/static/app.js'), 'utf8');
const statesPath = process.argv[2];
if (!statesPath || !fs.existsSync(statesPath)) {
    console.error('Usage: node frontend_smoke.js <states.json>');
    process.exit(1);
}
const states = JSON.parse(fs.readFileSync(statesPath, 'utf8'));

class El {
    constructor(tag) {
        this.tagName = (tag || 'div').toUpperCase();
        this.id = '';
        this.classList = {
            _c: new Set(),
            add: (...a) => a.forEach((x) => this.classList._c.add(x)),
            remove: (...a) => a.forEach((x) => this.classList._c.delete(x)),
            toggle: (c, on) => (on === undefined
                ? (this.classList._c.has(c) ? this.classList._c.delete(c) : this.classList._c.add(c))
                : (on ? this.classList._c.add(c) : this.classList._c.delete(c))),
            contains: (c) => this.classList._c.has(c),
        };
        this.style = { display: '', setProperty() {}, removeProperty() {} };
        this.dataset = {};
        this.children = [];
        this.innerHTML = '';
        this.textContent = '';
        this.value = '';
        this.scrollTop = 0;
        this.parentNode = null;
    }
    appendChild(c) { this.children.push(c); c.parentNode = this; return c; }
    insertBefore(c) { this.children.unshift(c); c.parentNode = this; return c; }
    removeAttribute() {}
    querySelector() { return null; }
    querySelectorAll() { return []; }
    setAttribute() {}
    getAttribute() { return null; }
    matches() { return false; }
    focus() {}
    blur() {}
    addEventListener() {}
    contains(el) {
        if (!el) return false;
        if (el === this) return true;
        return this.children.some((c) => c.contains && c.contains(el));
    }
}

const store = { byId: {} };
function mk(id) {
    const el = new El('div');
    el.id = id;
    store.byId[id] = el;
    return el;
}

const appRoot = mk('app-root');
mk('bottom-nav');
mk('toast');
const modal = mk('modal');
modal.style.display = 'none';
mk('modal-box');
mk('modal-title');
mk('modal-fields');
mk('modal-error');
mk('modal-body');

const docEl = new El('html');
docEl.style = { setProperty() {}, removeProperty() {} };
const body = new El('body');
body.classList = docEl.classList;
const doc = {
    documentElement: docEl,
    body,
    getElementById: (id) => store.byId[id] || null,
    querySelector: () => null,
    querySelectorAll: () => [],
    createElement: () => new El('div'),
    addEventListener: () => {},
    activeElement: null,
    scrollingElement: docEl,
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
        _investCategories: ['عیار'],
        _investTaxonomy: {
            risks: [
                { value: 'بدون ریسک', label: 'بدون ریسک', emoji: '🛡️' },
                { value: 'کم ریسک', label: 'کم ریسک', emoji: '🟢' },
            ],
            markets: [
                { value: 'صندوق', label: 'صندوق', emoji: '💹' },
                { value: 'رمزارز', label: 'رمزارز', emoji: '₿' },
            ],
            markets_by_risk: {
                'بدون ریسک': [{ value: 'صندوق', label: 'صندوق', emoji: '💹' }],
                'کم ریسک': [{ value: 'صندوق', label: 'صندوق', emoji: '💹' }],
            },
            assets: {
                'صندوق': [{ value: 'عیار', label: 'عیار', emoji: '✨' }],
                'رمزارز': [{ value: 'BTC/USDT', label: 'BTC/USDT', emoji: '₿' }],
            },
        },
        _moodEmojis: ['😀'],
        _dateCategories: ['سایر'],
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

const errors = [];

function balanceDivs(html) {
    let depth = 0;
    const re = /<\/?div[\s>]/g;
    let m;
    while ((m = re.exec(html))) {
        if (m[0].startsWith('</')) {
            if (depth <= 0) return false;
            depth--;
        } else {
            depth++;
        }
    }
    return depth === 0;
}

if (ctx.escJs('a\nb') !== 'a\\nb') errors.push('escJs: newline not escaped');
if (ctx.escJs("a'b") !== "a\\'b") errors.push('escJs: quote not escaped');
if (!ctx._modalValidators.hms('25:00:00')) errors.push('hms: 25h should be valid');
if (ctx._modalValidators.hms('100:00:00')) errors.push('hms: 100h should be invalid');
if (!ctx._modalValidators.hm('22:30')) errors.push('hm: clock should be valid');
if (ctx._modalValidators.hm('25:00')) errors.push('hm: 25h clock should be invalid');

const SECTIONS = [
    ['home', () => ctx.renderHome({
        date_label: 'test', is_today: true, search: '', show_calendar: false,
        useful_fmt: '0', not_useful_fmt: '0', efficiency: 0, tasks: [],
        wellness: { sleep: '—', wake: '—', sleep_dur: '—', mood: null, sleep_raw: '', wake_raw: '' },
        daily_note: '', recurring_count: 0, urgent_dates_count: 0,
    })],
    ['home+tasks', () => ctx.renderHome({
        date_label: 'test', is_today: false, search: 'q', show_calendar: true,
        calendar: { month_name: 'تیر', year: 1404, weekday_offset: 0, cells: [{ day: 1, date: '2026-06-22', eff: 50, has_data: true }] },
        useful_fmt: '1h', not_useful_fmt: '0', efficiency: 100, tasks: [{
            id: 1, title: "t\n<script>", display_fmt: '25:00:00', estimated_fmt: '—',
            estimated: 0, display_sec: 90000, progress: 0, is_useful: null, is_starred: false,
            is_running: false, is_expanded: true, remaining_fmt: null,
        }],
        wellness: { sleep: '22:00', wake: '07:00', sleep_dur: '9h', mood: 5, sleep_raw: '22:00', wake_raw: '07:00' },
        daily_note: 'note', recurring_count: 1, urgent_dates_count: 2,
    })],
    ['finance', () => ctx.renderFinanceScreen({
        month_label: 'تیر', is_current_month: true,
        totals: { balance: 100, balance_fmt: '100', income_fmt: '200', expense_fmt: '100', investment: 0, investment_fmt: '0' },
        entries: [], by_category: [], daily_series: [], chart: { has_data: false },
        installments: { count: 0, items: [], total_unpaid_fmt: '0' },
    })],
    ['investments', () => ctx.renderInvestmentsScreen({
        filter: { mode: 'all', label: 'همه', period_stat_label: 'کل' },
        totals: {
            balance: 700, balance_fmt: '700',
            period_buys: 200, period_buys_fmt: '200',
            month_investment: 200, month_investment_fmt: '200',
            net_invested: 500, net_invested_fmt: '500',
            portfolio_total: 500, portfolio_total_fmt: '500',
            estimated_value: 520, estimated_value_fmt: '520',
            has_market_values: true,
        },
        positions: [{
            asset: 'عیار', market: 'صندوق', display: '✨ عیار · 💹 صندوق',
            asset_emoji: '✨', cost_basis_fmt: '200', estimated_value_fmt: '220',
            has_market_price: true, current_unit_price: 110,
        }],
        entries: [{
            id: 1, title: 'خرید عیار', amount: 200, amount_fmt: '200', type: 'investment',
            category: 'عیار', date: '2026-06-22', date_label: '1',
            category_display: '✨ عیار · 💹 صندوق · 🟢 کم ریسک',
            investment_meta: {
                risk: 'کم ریسک', market: 'صندوق', asset: 'عیار',
                asset_emoji: '✨', market_emoji: '💹', risk_emoji: '🟢',
                display: '✨ عیار · 💹 صندوق · 🟢 کم ریسک',
            },
        }],
        by_category: [{ category: 'عیار', amount: 200, amount_fmt: '200', pct: 100 }],
        portfolio_by_risk: [{ category: 'کم ریسک', amount: 520, amount_fmt: '520', pct: 100 }],
    })],
    ['investments-empty', () => ctx.renderInvestmentsScreen({
        filter: { mode: 'all', label: 'همه', period_stat_label: 'کل' },
        totals: {
            balance: 0, balance_fmt: '0',
            period_buys: 0, period_buys_fmt: '0',
            month_investment: 0, month_investment_fmt: '0',
            net_invested: 0, net_invested_fmt: '0',
            portfolio_total: 0, portfolio_total_fmt: '0',
        },
        positions: [], entries: [], by_category: [],
    })],
    ['analytics', () => ctx.renderAnalytics({
        period: 7, start_label: 'a', end_label: 'b', stats: { streak: 1, eff: 50, total_fmt: '1h', useful_fmt: '30m', not_useful_fmt: '30m', income_fmt: '0', expense_fmt: '0', investment_fmt: '0', balance_fmt: '0', avg_mood: '5', avg_sleep: '8h' },
        chart_points: [0, 50, 100], heatmap: [{ date: '2026-01-01', eff: 50, total: 3600 }], days: [],
    })],
    ['settings', () => ctx.renderSettings({ theme: 'dark', export_path: '/x/backup.json', backup_summary: { tasks: 1, finance: 0, notes: 0, projects: 0, installments: 0, important_dates: 0, recurring: 0 } })],
    ['recurring', () => ctx.renderRecurring([{ id: 1, title: 'daily' }])],
    ['recurring-empty', () => ctx.renderRecurring([])],
    ['projects', () => ctx.renderProjects({ list: [{ id: 1, title: 'P', color: '#5E5CE6', progress: 50, done: 1, total: 2, is_done: false, deadline_label: '', deadline_overdue: false }], colors: ['#5E5CE6'] })],
    ['project_detail', () => ctx.renderProjectDetail({ id: 1, title: 'P', color: '#5E5CE6', progress: 50, done: 0, total: 1, is_done: false, deadline_label: '', deadline_overdue: false, tasks: [], colors: ['#5E5CE6'] })],
    ['installments', () => ctx.renderInstallments({ list: [], month_label: 'تیر', month_total_due_fmt: '0', month_total_unpaid_fmt: '0', total_remaining_fmt: '0' })],
    ['important_dates', () => ctx.renderImportantDates({ items: [], categories: ['سایر'] })],
    ['important_dates+edit', () => ctx.renderImportantDates({
        items: [{
            id: 1, title: 'a"b', date_label: '1', category: 'سایر', urgency: 'ok',
            countdown: '5 روز', date_fmt: '1404/01/01', repeat_type: 'none', is_repeating: false,
        }],
        categories: ['سایر'],
    })],
    ['installments+edit', () => ctx.renderInstallments({
        list: [{
            id: 2, title: 'loan', amount_fmt: '10', remaining_fmt: '50', progress: 50,
            paid_count: 1, total_count: 6, is_settled: false, is_overdue: false,
            due_label: 'ماه جاری', paid_this_month: false,
        }],
        month_label: 'تیر', month_total_due_fmt: '10', month_total_unpaid_fmt: '10', total_remaining_fmt: '50',
    })],
    ['calendar', () => ctx.renderCalendar({ month_name: 'تیر', year: 1404, weekday_offset: 2, cells: [{ day: 1, date: '2026-06-22', eff: 0, has_data: false }] }, '2026-06-22')],
    ['tracking-empty', () => ctx.renderTracking({ has_data: false, session: null, date_label: 't', intervals: [] })],
    ['tracking-active', () => ctx.renderTracking({ has_data: true, session: { id: 1, is_active: true, started_label: '10:00' }, date_label: 't', intervals: [{ id: 1, session_id: 1, is_active: true, started_label: '10:00' }], day_total_secs: 0, day_total_label: '0', completed_count: 0, session_count: 1, efficiency: 50, useful_label: '1h' })],
    ['taskCard', () => ctx.taskCard({ id: 1, title: 'x', display_fmt: '0:00', estimated_fmt: '—', estimated: 0, display_sec: 0, progress: 0, is_useful: true, is_starred: true, is_running: true, is_expanded: true, remaining_fmt: '1h' })],
    ['finChart', () => ctx.financeLineChartSvg({ income: [1, 2], expense: [1, 1], balance: [0, 1], investment: [0, 0] }, 320, 130)],
    ['invChartMultiAsset', () => {
        var chart = ctx.buildInvestmentChart({
            filter: { mode: 'month', start: '2026-06-01', end: '2026-06-30' },
            all_entries: [
                { amount: 200, date: '2026-06-10', investment_meta: { asset: 'طلا', group_key: 'طلا', asset_emoji: '🥇' } },
                { amount: 300, date: '2026-06-15', investment_meta: { asset: 'عیار', group_key: 'عیار', asset_emoji: '✨' } },
            ],
        });
        var html = ctx.investmentTrendChartSvg(chart, 320, 130);
        if (!html.includes('inv-chart-line-hit')) throw new Error('missing chart hit areas');
        if (!html.includes('invChartTooltip')) throw new Error('missing chart tooltip');
        return html;
    }],
];

for (const [name, fn] of SECTIONS) {
    try {
        const html = fn();
        if (!html || html.length < 10) errors.push(`section ${name}: empty`);
        if (!balanceDivs(html)) errors.push(`section ${name}: unbalanced divs`);
        if (/undefined|NaN|\[object Object\]/.test(html)) errors.push(`section ${name}: bad token`);
        if (/showEdit(ImportantDate|Installment)\(\{/.test(html)) errors.push(`section ${name}: broken JSON onclick`);
        if (html.includes('<script>')) errors.push(`section ${name}: XSS`);
    } catch (e) {
        errors.push(`section ${name}: ${e.message}`);
    }
}

const MODALS = [
    ['addFinance', () => ctx.showAddFinance('expense')],
    ['addIncome', () => ctx.showAddFinance('income')],
    ['addBudget', () => ctx.showAddBudget()],
    ['addCategory', () => ctx.showAddCategory()],
    ['durationModal', () => ctx.showDurationModal('t', 'set_duration', 1, 90000)],
    ['clockModal', () => ctx.showClockModal('t', 'set_sleep', '22:00', 'sleep')],
    ['simpleModal', () => ctx.showModal({ title: 't', cmd: 'add_task', fields: [{ label: 'x', key: 'title', validate: 'required' }] })],
];
for (const [name, fn] of MODALS) {
    try { fn(); modal.style.display = 'none'; }
    catch (e) { errors.push(`modal ${name}: ${e.message}`); }
}

// Jalali-date modals need full DOM; covered by Python build_state + renderApp tests.
['showAddProject', 'showAddInstallment', 'showAddImportantDate', 'showEditImportantDateById',
    'showEditInstallmentById', 'showInvestmentModal', 'showUpdateAssetPrice', 'flushPendingSearch'].forEach((fnName) => {
    if (typeof ctx[fnName] !== 'function') errors.push(`missing ${fnName}`);
});

for (const [screen, state] of Object.entries(states)) {
    try {
        ctx.renderApp(state);
        const html = appRoot.innerHTML;
        if (!html || html.length < 50) errors.push(`${screen}: empty render`);
        if (!balanceDivs(html)) errors.push(`${screen}: unbalanced divs`);
        if (/undefined|NaN|\[object Object\]/.test(html)) errors.push(`${screen}: bad token`);
        if (html.includes('<script>')) errors.push(`${screen}: XSS leak`);
    } catch (e) {
        errors.push(`${screen}: ${e.message}`);
    }
}

if (errors.length) {
    console.error(errors.join('\n'));
    process.exit(1);
}
console.log(`OK: ${Object.keys(states).length} screens, ${SECTIONS.length} sections, ${MODALS.length} modals`);
