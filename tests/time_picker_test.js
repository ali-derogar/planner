#!/usr/bin/env node
/* Unit tests for time picker helpers in app.js */
const fs = require('fs');
const vm = require('vm');
const path = require('path');

const appJs = fs.readFileSync(
    path.join(__dirname, '..', 'src', 'dailyplanner', 'ui', 'static', 'app.js'),
    'utf8'
);

function walk(node, pred, out) {
    if (!node) return;
    if (pred(node)) out.push(node);
    (node.children || []).forEach((c) => walk(c, pred, out));
}

class El {
    constructor(tag) {
        this.tagName = (tag || 'div').toUpperCase();
        this.id = '';
        this._className = '';
        this.classList = {
            _c: new Set(),
            add: (...a) => { a.forEach((x) => this.classList._c.add(x)); this._syncClassName(); },
            remove: (...a) => { a.forEach((x) => this.classList._c.delete(x)); this._syncClassName(); },
            contains: (c) => this.classList._c.has(c),
        };
        this.dataset = {};
        this.children = [];
        this.textContent = '';
        this.value = '';
        this.type = 'text';
        this.parentNode = null;
    }
    _syncClassName() {
        this._className = [...this.classList._c].join(' ');
    }
    get className() {
        return this._className;
    }
    set className(v) {
        this._className = v || '';
        this.classList._c.clear();
        this._className.split(/\s+/).filter(Boolean).forEach((c) => this.classList._c.add(c));
    }
    appendChild(c) {
        this.children.push(c);
        c.parentNode = this;
        return c;
    }
    querySelector(sel) {
        const found = [];
        walk(this, () => true, found);
        if (sel === '.time-picker-preview') {
            return found.find((c) => c.classList.contains('time-picker-preview')) || null;
        }
        if (sel === '.time-picker-val') {
            return found.find((c) => c.classList.contains('time-picker-val')) || null;
        }
        const unitMatch = sel.match(/\.time-picker-col\[data-unit="([^"]+)"\]/);
        if (unitMatch) {
            return found.find(
                (c) => c.classList.contains('time-picker-col') && c.dataset.unit === unitMatch[1]
            ) || null;
        }
        return null;
    }
    querySelectorAll(sel) {
        const found = [];
        walk(this, () => true, found);
        if (sel === '.time-picker-col') {
            return found.filter((c) => c.classList.contains('time-picker-col'));
        }
        return [];
    }
    setAttribute() {}
    addEventListener() {}
    focus() {}
    blur() {}
    select() {}
}

const bodyClassList = {
    _c: new Set(),
    add: (...a) => a.forEach((x) => bodyClassList._c.add(x)),
    remove: (...a) => a.forEach((x) => bodyClassList._c.delete(x)),
    contains: (c) => bodyClassList._c.has(c),
    toggle: (c, on) => (on === undefined
        ? (bodyClassList._c.has(c) ? bodyClassList._c.delete(c) : bodyClassList._c.add(c))
        : (on ? bodyClassList._c.add(c) : bodyClassList._c.delete(c))),
};

const doc = {
    createElement(tag) {
        return new El(tag);
    },
    getElementById: () => null,
    querySelector: () => null,
    querySelectorAll: () => [],
    body: { classList: bodyClassList, style: {} },
    documentElement: { style: { setProperty() {}, removeProperty() {} } },
    addEventListener: () => {},
};

const ctx = {
    document: doc,
    window: {
        innerHeight: 800,
        innerWidth: 400,
        matchMedia: () => ({ matches: false }),
        addEventListener: () => {},
        visualViewport: null,
        setTimeout: (fn) => { fn(); return 1; },
        clearTimeout: () => {},
    },
    console,
    setTimeout: (fn) => { fn(); return 1; },
    clearTimeout: () => {},
    requestAnimationFrame: (fn) => fn(),
};
ctx.window.document = doc;
vm.runInContext(appJs, vm.createContext(ctx));

const errors = [];

function assert(cond, msg) {
    if (!cond) errors.push(msg);
}

function assertEq(a, b, msg) {
    if (a !== b) errors.push(`${msg}: expected ${JSON.stringify(b)}, got ${JSON.stringify(a)}`);
}

/* no stack overflow when building + updating preview */
try {
    const hms = ctx.buildTimePickerEl({ key: 'value', type: 'time-hms', value: '1:30:45' });
    ctx.updateTimePickerPreview(hms);
    ctx.getTimePickerValue(hms);
    assertEq(ctx.getTimePickerValue(hms), '1:30:45', 'hms initial value');
} catch (e) {
    errors.push(`hms build/preview: ${e.message}`);
}

try {
    const hm = ctx.buildTimePickerEl({ key: 'value', type: 'time-hm', value: '22:15', presetKind: 'sleep' });
    ctx.updateTimePickerPreview(hm);
    assertEq(ctx.getTimePickerValue(hm), '22:15', 'hm initial value');
} catch (e) {
    errors.push(`hm build/preview: ${e.message}`);
}

/* step buttons */
try {
    const picker = ctx.buildTimePickerEl({ key: 'value', type: 'time-hm', value: '10:00' });
    ctx.stepTimeUnit(picker, 'm', 15);
    assertEq(ctx.getTimePickerValue(picker), '10:15', 'step minutes');
    ctx.stepTimeUnit(picker, 'h', 1);
    assertEq(ctx.getTimePickerValue(picker), '11:15', 'step hours');
} catch (e) {
    errors.push(`step: ${e.message}`);
}

/* wrap-around at max */
try {
    const picker = ctx.buildTimePickerEl({ key: 'value', type: 'time-hm', value: '23:59' });
    ctx.stepTimeUnit(picker, 'm', 1);
    assertEq(ctx.getTimePickerValue(picker), '23:00', 'minute wrap at 59');
    ctx.stepTimeUnit(picker, 'h', 1);
    assertEq(ctx.getTimePickerValue(picker), '0:00', 'hour wrap at 23');
} catch (e) {
    errors.push(`wrap: ${e.message}`);
}

/* direct edit via input (Persian digits) */
try {
    const picker = ctx.buildTimePickerEl({ key: 'value', type: 'time-hm', value: '00:00' });
    const hourCol = picker.querySelector('.time-picker-col[data-unit="h"]');
    const hourInput = hourCol.querySelector('.time-picker-val');
    hourInput.value = '۱۴';
    ctx.commitTimePickerCol(hourCol, picker);
    assertEq(ctx.getTimePickerValue(picker), '14:00', 'persian hour edit');
} catch (e) {
    errors.push(`persian edit: ${e.message}`);
}

/* clamp out-of-range values */
try {
    const picker = ctx.buildTimePickerEl({ key: 'value', type: 'time-hm', value: '12:00' });
    const minCol = picker.querySelector('.time-picker-col[data-unit="m"]');
    const minInput = minCol.querySelector('.time-picker-val');
    minInput.value = '99';
    ctx.commitTimePickerCol(minCol, picker);
    assertEq(ctx.getTimePickerValue(picker), '12:59', 'clamp minutes to 59');
} catch (e) {
    errors.push(`clamp: ${e.message}`);
}

/* empty input reverts to previous */
try {
    const picker = ctx.buildTimePickerEl({ key: 'value', type: 'time-hm', value: '08:30' });
    const minCol = picker.querySelector('.time-picker-col[data-unit="m"]');
    const minInput = minCol.querySelector('.time-picker-val');
    minInput.value = '';
    ctx.commitTimePickerCol(minCol, picker);
    assertEq(ctx.getTimePickerValue(picker), '8:30', 'empty input keeps previous minute');
} catch (e) {
    errors.push(`empty revert: ${e.message}`);
}

/* presets */
try {
    const picker = ctx.buildTimePickerEl({ key: 'value', type: 'time-hms', value: '0:00:00' });
    ctx.setTimePickerValues(picker, 2, 0, 0);
    assertEq(ctx.getTimePickerValue(picker), '2:00:00', 'preset 2h');
} catch (e) {
    errors.push(`presets: ${e.message}`);
}

/* validator compatibility with picker output */
try {
    const picker = ctx.buildTimePickerEl({ key: 'value', type: 'time-hms', value: '25:00:00' });
    const val = ctx.getTimePickerValue(picker);
    assert(ctx._modalValidators.hms(val), 'hms validator accepts 25h output');
    assert(!ctx._modalValidators.hms('100:00:00'), 'hms validator rejects 100h');
} catch (e) {
    errors.push(`validator: ${e.message}`);
}

try {
    const picker = ctx.buildTimePickerEl({ key: 'value', type: 'time-hm', value: '23:00' });
    const val = ctx.getTimePickerValue(picker);
    assert(ctx._modalValidators.hm(val), 'hm validator accepts 23:00');
    ctx.setTimePickerValues(picker, 23, 59, 0);
    assert(ctx._modalValidators.hm(ctx.getTimePickerValue(picker)), 'hm validator accepts 23:59');
} catch (e) {
    errors.push(`hm validator: ${e.message}`);
}

/* secondsToHms for large task durations */
try {
    assertEq(ctx.secondsToHms(90000), '25:00:00', 'secondsToHms 90000');
    const picker = ctx.buildTimePickerEl({
        key: 'value',
        type: 'time-hms',
        value: ctx.secondsToHms(90000),
    });
    assertEq(ctx.getTimePickerValue(picker), '25:00:00', 'large duration roundtrip');
} catch (e) {
    errors.push(`large duration: ${e.message}`);
}

if (errors.length) {
    console.error(errors.join('\n'));
    process.exit(1);
}
console.log(`OK: ${12} time picker checks`);
