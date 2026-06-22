"""CSS for the WebView-based UI (dark theme + Vazirmatn)."""
import base64
from pathlib import Path
from functools import lru_cache

from dailyplanner.ui.tokens import TOKENS_CSS
from dailyplanner.utils.platform import is_android


@lru_cache(maxsize=2)
def _load_font_b64() -> str:
    if is_android():
        return ""
    candidates = [
        Path(__file__).parents[4] / "resources" / "fonts" / "Vazirmatn-Regular.ttf",
        Path(__file__).parents[3] / "resources" / "fonts" / "Vazirmatn-Regular.ttf",
        Path(__file__).parents[2] / "resources" / "fonts" / "Vazirmatn-Regular.ttf",
    ]
    for p in candidates:
        if p.exists():
            return base64.b64encode(p.read_bytes()).decode()
    return ""


def get_css() -> str:
    font_b64 = _load_font_b64()
    font_face = ""
    if font_b64:
        font_face = f"""
@font-face {{
    font-family: 'Vazirmatn';
    src: url('data:font/truetype;base64,{font_b64}') format('truetype');
    font-weight: normal;
    font-style: normal;
}}"""

    return f"""
{font_face}

{TOKENS_CSS}

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body {{
    background-color: var(--bg);
    color: var(--text);
    font-family: 'Vazirmatn', -apple-system, Tahoma, sans-serif;
    direction: rtl;
    min-height: 100vh;
    overflow-x: hidden;
    -webkit-tap-highlight-color: transparent;
    -webkit-text-size-adjust: 100%;
    font-size: 14px;
    line-height: 1.5;
}}

a {{ text-decoration: none; color: inherit; }}

/* ── Layout ── */
.screen {{ display: flex; flex-direction: column; min-height: 100vh; }}
.content {{ flex: 1; padding-bottom: calc(68px + var(--safe-bottom)); }}

/* ── Bottom Nav ── */
.bottom-nav {{
    position: fixed;
    bottom: 0; left: 0; right: 0;
    background: #0D0D0D;
    display: flex;
    padding: 6px 0 calc(8px + var(--safe-bottom));
    border-top: 1px solid #2C2C2E;
    z-index: 200;
}}

/* Android gesture / 3-button nav bar — env() is often 0 in WebView */
@media (hover: none) and (pointer: coarse) {{
    .content {{ padding-bottom: calc(68px + max(48px, var(--safe-bottom))); }}
    .bottom-nav {{ padding-bottom: calc(8px + max(48px, var(--safe-bottom))); }}
}}
.nav-btn {{
    flex: 1;
    color: #8E8E93;
    font-size: 13px;
    padding: 6px 4px;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-family: 'Vazirmatn', sans-serif;
    cursor: pointer;
    border-radius: 8px;
    margin: 0 4px;
    transition: background 0.15s;
}}
.nav-btn.active {{
    color: #5E5CE6;
    background: rgba(94,92,230,0.15);
}}

/* ── Date Header ── */
.date-header {{
    background: linear-gradient(135deg, #3D5AFE 0%, #8B00E0 100%);
    padding: calc(14px + var(--safe-top)) 16px 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    direction: rtl;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 2px 12px rgba(61,90,254,0.3);
}}

@media (hover: none) and (pointer: coarse) {{
    .date-header {{
        padding-top: calc(14px + max(36px, var(--safe-top)));
    }}
    .analytics-period {{
        padding-top: max(36px, var(--safe-top));
    }}
}}
.date-title {{
    color: #fff;
    font-size: 15px;
    font-weight: bold;
    text-align: center;
    flex: 1;
}}
.date-nav-btn {{
    background: rgba(255,255,255,0.18);
    color: #fff;
    width: 34px; height: 34px;
    border-radius: 50%;
    font-size: 20px;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer;
    border: none;
    transition: background 0.15s;
}}
.date-nav-btn:hover {{ background: rgba(255,255,255,0.28); }}
.today-btn {{
    background: rgba(255,255,255,0.18);
    color: #fff;
    padding: 4px 10px;
    border-radius: 14px;
    font-size: 12px;
    cursor: pointer;
    border: none;
    font-family: 'Vazirmatn', sans-serif;
    white-space: nowrap;
}}

/* ── Summary Bar ── */
.summary-bar {{
    background: #1C1C1E;
    padding: 8px 16px;
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    border-bottom: 1px solid #2C2C2E;
}}
.sum-useful {{ color: #4DD980; }}
.sum-not {{ color: #FF7359; }}
.sum-eff {{ color: #5E5CE6; }}

/* ── Task Card ── */
.task-list {{ padding: 8px 8px 4px; }}

.task-card {{
    background: #1C1C1E;
    border-radius: 14px;
    margin-bottom: 8px;
    overflow: hidden;
    border: 1px solid #2C2C2E;
}}
.task-header {{
    display: flex;
    align-items: center;
    padding: 12px 12px;
    cursor: pointer;
    direction: rtl;
    gap: 8px;
}}
.task-star {{ font-size: 18px; color: #FFC208; flex-shrink: 0; }}
.task-star.empty {{ color: #38383B; }}
.task-title-wrap {{
    flex: 1;
    font-size: 14px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}}
.task-dur {{
    color: #8E8E93;
    font-size: 13px;
    font-variant-numeric: tabular-nums;
    flex-shrink: 0;
    min-width: 68px;
    text-align: center;
}}
.task-dur.running {{
    color: #00D9C7;
}}
.task-chevron {{ color: #555; font-size: 11px; flex-shrink: 0; }}

/* useful indicator strip on left */
.task-card.is-useful {{ border-right: 3px solid #4DD980; }}
.task-card.is-not-useful {{ border-right: 3px solid #FF5959; }}
.task-card.is-running {{ border-right: 3px solid #00D9C7; }}

/* ── Task Detail ── */
.task-detail {{
    padding: 12px 14px 14px;
    border-top: 1px solid #2C2C2E;
    direction: rtl;
    background: #161616;
}}
.timer-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
}}
.timer-big {{
    font-size: 22px;
    font-variant-numeric: tabular-nums;
    color: #00D9C7;
    letter-spacing: 2px;
}}
.btn-start {{
    background: #143838;
    color: #00D9C7;
    border: 1px solid #00D9C7;
    padding: 7px 16px;
    border-radius: 20px;
    cursor: pointer;
    font-family: 'Vazirmatn', sans-serif;
    font-size: 13px;
}}
.btn-stop {{
    background: #471F1F;
    color: #FF5959;
    border: 1px solid #FF5959;
    padding: 7px 16px;
    border-radius: 20px;
    cursor: pointer;
    font-family: 'Vazirmatn', sans-serif;
    font-size: 13px;
}}

/* estimated */
.est-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 12px;
    color: #8E8E93;
    margin-bottom: 10px;
}}
.est-val {{ color: #FFFFFF99; }}

/* chips row */
.chips {{
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    direction: rtl;
}}
.chip {{
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 12px;
    cursor: pointer;
    font-family: 'Vazirmatn', sans-serif;
    border: none;
    display: inline-block;
    white-space: nowrap;
}}
.chip-useful-on   {{ background: #1A4028; color: #4DD980; border: 1px solid #4DD98055; }}
.chip-useful-off  {{ background: #1C1C1E; color: #8E8E93; border: 1px solid #38383B; }}
.chip-notuseful-on{{ background: #471F1F; color: #FF7359; border: 1px solid #FF595955; }}
.chip-neutral     {{ background: #2C2C2E; color: #8E8E93; border: 1px solid #38383B; }}
.chip-edit        {{ background: #1A1A40; color: #7B8CDE; border: 1px solid #5E5CE633; }}
.chip-delete      {{ background: #3D1818; color: #FF5959; border: 1px solid #FF595933; }}

/* ── Section (Finance / Wellness) ── */
.section {{
    background: #1C1C1E;
    border-radius: 14px;
    margin: 6px 8px;
    padding: 14px;
    border: 1px solid #2C2C2E;
    direction: rtl;
}}
.sec-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}}
.sec-title {{
    font-size: 14px;
    font-weight: bold;
    color: #FFFFFF;
}}
.sec-actions {{ display: flex; gap: 6px; }}
.btn-sm-green {{
    background: #1A4028; color: #4DD980;
    padding: 4px 10px; border-radius: 14px;
    font-size: 12px; cursor: pointer;
    border: 1px solid #4DD98044;
    font-family: 'Vazirmatn', sans-serif;
}}
.btn-sm-red {{
    background: #3D1818; color: #FF5959;
    padding: 4px 10px; border-radius: 14px;
    font-size: 12px; cursor: pointer;
    border: 1px solid #FF595944;
    font-family: 'Vazirmatn', sans-serif;
}}

/* finance summary */
.fin-summary {{
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    padding-bottom: 8px;
    margin-bottom: 8px;
    border-bottom: 1px solid #2C2C2E;
}}
.fin-income {{ color: #4DD980; }}
.fin-expense {{ color: #FF7359; }}
.fin-balance {{ color: #5E5CE6; }}

.fin-entry {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 5px 0;
    font-size: 13px;
    direction: rtl;
    border-bottom: 1px solid #1C1C1E;
}}
.fin-entry:last-child {{ border-bottom: none; }}
.fin-type-income {{ color: #4DD980; }}
.fin-type-expense {{ color: #FF7359; }}
.fin-del {{
    background: none; border: none;
    color: #FF595988; font-size: 16px;
    cursor: pointer; padding: 0 6px;
}}

/* wellness */
.well-row {{
    display: flex; gap: 8px;
    margin-bottom: 10px;
    direction: rtl;
}}
.well-btn {{
    flex: 1; background: #2C2C2E;
    border: 1px solid #38383B;
    border-radius: 10px;
    padding: 10px 8px;
    text-align: center;
    cursor: pointer;
    font-family: 'Vazirmatn', sans-serif;
    color: #fff;
}}
.well-lbl {{ font-size: 11px; color: #8E8E93; display: block; margin-bottom: 3px; }}
.well-val {{ font-size: 14px; }}

/* mood */
.mood-row {{
    display: flex;
    justify-content: space-between;
    direction: rtl;
    padding-top: 4px;
}}
.mood-btn {{
    font-size: 20px;
    cursor: pointer;
    padding: 4px;
    border-radius: 50%;
    opacity: 0.45;
    background: none;
    border: none;
    transition: all 0.1s;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 36px; height: 36px;
}}
.mood-btn.sel {{
    opacity: 1;
    background: rgba(94,92,230,0.25);
    transform: scale(1.25);
    border: 1px solid #5E5CE644;
}}

/* ── Add Task Button ── */
.add-btn {{
    display: block;
    margin: 10px 8px 6px;
    padding: 14px;
    background: linear-gradient(135deg, #3D5AFE, #8B00E0);
    color: #fff;
    border-radius: 14px;
    text-align: center;
    font-size: 15px;
    cursor: pointer;
    font-family: 'Vazirmatn', sans-serif;
    box-shadow: 0 4px 16px rgba(61,90,254,0.35);
    border: none;
}}

/* ── Modal ── */
.modal-overlay {{
    position: fixed; inset: 0;
    background: rgba(0,0,0,0.72);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 500;
    padding: 20px;
    direction: rtl;
}}
.modal-box {{
    background: #1C1C1E;
    border-radius: 18px;
    padding: 24px 20px 20px;
    width: 100%;
    max-width: 360px;
    border: 1px solid #3C3C3E;
}}
.modal-title {{
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 14px;
    text-align: center;
}}
.modal-label {{
    font-size: 12px;
    color: #8E8E93;
    margin-bottom: 5px;
}}
.modal-input {{
    width: 100%;
    background: #2C2C2E;
    border: 1px solid #38383B;
    border-radius: 10px;
    padding: 10px 12px;
    color: #fff;
    font-size: 14px;
    font-family: 'Vazirmatn', sans-serif;
    direction: rtl;
    margin-bottom: 12px;
    outline: none;
}}
.modal-input:focus {{ border-color: #5E5CE6; }}
.modal-btns {{ display: flex; gap: 8px; direction: rtl; }}
.modal-confirm {{
    flex: 1;
    background: linear-gradient(135deg, #3D5AFE, #8B00E0);
    color: #fff;
    border: none;
    border-radius: 10px;
    padding: 10px;
    font-size: 14px;
    cursor: pointer;
    font-family: 'Vazirmatn', sans-serif;
}}
.modal-cancel {{
    flex: 1;
    background: #2C2C2E;
    color: #8E8E93;
    border: 1px solid #38383B;
    border-radius: 10px;
    padding: 10px;
    font-size: 14px;
    cursor: pointer;
    font-family: 'Vazirmatn', sans-serif;
}}

/* ── Time Picker ── */
.time-picker {{
    margin-bottom: 12px;
}}
.time-picker-preview {{
    text-align: center;
    font-size: 32px;
    font-weight: bold;
    font-variant-numeric: tabular-nums;
    color: var(--primary);
    margin-bottom: 12px;
    letter-spacing: 1px;
}}
.time-picker-cols {{
    display: flex;
    justify-content: center;
    gap: 10px;
    direction: ltr;
}}
.time-picker-col {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    flex: 1;
    max-width: 88px;
}}
.time-picker-btn {{
    width: 100%;
    background: var(--surface-muted);
    border: 1px solid var(--divider);
    color: var(--text);
    border-radius: 10px;
    padding: 8px 0;
    font-size: 14px;
    cursor: pointer;
    font-family: 'Vazirmatn', sans-serif;
    line-height: 1;
    transition: background 0.15s, border-color 0.15s;
}}
.time-picker-btn:active {{
    background: rgba(94,92,230,0.25);
    border-color: var(--primary);
}}
.time-picker-val {{
    font-size: 28px;
    font-weight: bold;
    font-variant-numeric: tabular-nums;
    min-width: 56px;
    text-align: center;
    padding: 6px 0;
    background: var(--surface-muted);
    border-radius: 10px;
    border: 1px solid var(--divider);
}}
.time-picker-lbl {{
    font-size: 11px;
    color: var(--text-muted);
    direction: rtl;
}}
.time-picker-presets {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    justify-content: center;
    margin-top: 14px;
    direction: rtl;
}}
.time-preset-btn {{
    background: var(--surface-muted);
    border: 1px solid var(--divider);
    color: var(--text-muted);
    border-radius: 20px;
    padding: 5px 10px;
    font-size: 11px;
    cursor: pointer;
    font-family: 'Vazirmatn', sans-serif;
    transition: background 0.15s, color 0.15s, border-color 0.15s;
}}
.time-preset-btn:active {{
    background: rgba(94,92,230,0.2);
    color: var(--primary);
    border-color: var(--primary);
}}

/* ── Analytics ── */
.analytics-period {{
    display: flex; gap: 6px;
    padding: 10px 8px 6px;
    direction: rtl;
}}
.period-btn {{
    flex: 1;
    padding: 8px;
    border-radius: 10px;
    text-align: center;
    background: #2C2C2E;
    color: #8E8E93;
    border: 1px solid #38383B;
    cursor: pointer;
    font-family: 'Vazirmatn', sans-serif;
    font-size: 13px;
}}
.period-btn.active {{
    background: rgba(94,92,230,0.2);
    color: #5E5CE6;
    border-color: #5E5CE655;
}}

.stat-cards {{
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    padding: 0 8px 8px;
    direction: rtl;
}}
.stat-card {{
    flex: 1;
    min-width: calc(50% - 4px);
    background: #1C1C1E;
    border-radius: 12px;
    padding: 12px;
    border: 1px solid #2C2C2E;
    text-align: center;
}}
.stat-key {{ font-size: 11px; color: #8E8E93; margin-bottom: 4px; }}
.stat-val {{ font-size: 16px; font-weight: bold; }}

.day-card {{
    background: #1C1C1E;
    border-radius: 12px;
    margin: 4px 8px;
    padding: 10px 12px;
    border: 1px solid #2C2C2E;
    direction: rtl;
}}
.day-date {{ font-size: 13px; color: #8E8E93; margin-bottom: 6px; }}
.day-bar {{
    height: 6px;
    border-radius: 3px;
    background: #2C2C2E;
    overflow: hidden;
    margin-bottom: 6px;
}}
.day-bar-fill {{
    height: 100%;
    border-radius: 3px;
    background: linear-gradient(90deg, #5E5CE6, #4DD980);
}}
.day-stats {{
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: #8E8E93;
}}

/* ── SPA extras ── */
.loading-state {{ text-align: center; padding: 48px; color: var(--text-muted); }}
.search-row {{ padding: 8px 8px 4px; }}
.search-input {{
    width: 100%; background: var(--surface); border: 1px solid var(--divider);
    border-radius: var(--radius-sm); padding: 10px 12px; color: var(--text);
    font-family: 'Vazirmatn', sans-serif; font-size: 14px; outline: none;
}}
.search-input:focus {{ border-color: var(--primary); }}
.header-actions {{ display: flex; gap: 4px; align-items: center; }}
.icon-btn {{
    background: rgba(255,255,255,0.18); color: #fff; border: none;
    border-radius: 8px;
    width: 34px; height: 34px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; cursor: pointer;
    flex-shrink: 0;
}}
.task-progress {{
    height: 4px; background: var(--surface-muted); margin: 0 12px 4px;
}}
.task-progress-fill {{
    height: 100%; background: linear-gradient(90deg, var(--primary), var(--success));
    border-radius: 2px; transition: width 0.3s;
}}
.task-remaining {{ font-size: 11px; color: var(--text-muted); padding: 0 12px 8px; }}
.empty-state {{
    text-align: center; padding: 32px 16px; color: var(--text-muted);
}}
.empty-icon {{ font-size: 40px; margin-bottom: 8px; }}
.empty-btn, .empty-mini {{ margin-top: 12px; }}
.empty-mini {{ text-align: center; font-size: 12px; color: var(--text-muted); padding: 8px; }}
.empty-btn {{
    background: var(--primary); color: #fff; border: none; border-radius: var(--radius-sm);
    padding: 8px 16px; cursor: pointer; font-family: 'Vazirmatn', sans-serif;
}}
.note-section {{ margin-top: 0; }}
.note-input {{
    width: 100%; min-height: 72px; background: var(--surface-muted);
    border: 1px solid var(--divider); border-radius: var(--radius-sm);
    padding: 10px; color: var(--text); font-family: 'Vazirmatn', sans-serif;
    font-size: 14px; resize: vertical; outline: none; margin-top: 8px;
}}
.fin-donut-row {{ display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }}
.fin-donut {{
    width: 48px; height: 48px; border-radius: 50%;
    background: conic-gradient(var(--success) 0 calc(var(--income-pct) * 1%), var(--error) calc(var(--income-pct) * 1%) 100%);
    flex-shrink: 0;
}}
.fin-cat {{ font-size: 10px; opacity: 0.7; }}
.fin-edit {{
    background: none; border: none; color: var(--primary); cursor: pointer; padding: 0 4px;
}}
.calendar-panel {{
    background: var(--surface); margin: 4px 8px; border-radius: var(--radius);
    padding: 10px; border: 1px solid var(--divider);
}}
.cal-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }}
.cal-nav {{ background: var(--surface-muted); border: none; color: var(--text); padding: 4px 12px; border-radius: 8px; cursor: pointer; }}
.cal-grid {{ display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; }}
.cal-day {{
    background: var(--surface-muted); border: none; border-radius: 8px;
    padding: 8px 4px; font-size: 12px; cursor: pointer; color: var(--text);
    font-family: 'Vazirmatn', sans-serif;
}}
.cal-day.has-data {{ font-weight: bold; }}
.cal-day.eff-high {{ background: rgba(77,217,128,0.25); }}
.streak-badge {{
    text-align: center; font-size: 13px; color: var(--warning);
    padding: 4px 8px; margin: 0 8px;
}}
.chart-box {{ padding: 8px 12px; }}
.sparkline {{ width: 100%; height: 60px; display: block; }}
.heatmap {{ display: flex; gap: 3px; padding: 4px 12px 8px; flex-wrap: wrap; }}
.hm-cell {{ width: 10px; height: 10px; border-radius: 2px; background: var(--surface-muted); }}
.hm-high {{ background: var(--success); }}
.hm-mid {{ background: var(--primary); }}
.hm-low {{ background: var(--warning); }}
.analytics-header, .page-header {{
    padding: calc(12px + var(--safe-top)) 16px 10px;
    font-size: 16px; font-weight: bold;
    background: linear-gradient(135deg, #3D5AFE 0%, #8B00E0 100%);
    color: #fff; position: sticky; top: 0; z-index: 90;
}}
.sticky-sub {{ margin-bottom: 0; }}
.period-label {{ text-align: center; color: var(--text-muted); font-size: 12px; padding: 4px 8px; }}
.day-extra {{ font-size: 11px; color: var(--text-muted); margin-top: 4px; }}
.page-header {{ background: var(--surface); color: var(--text); border-bottom: 1px solid var(--divider); }}
.back-btn {{
    display: block; margin: 12px 8px; padding: 12px; text-align: center;
    background: var(--surface); border: 1px solid var(--divider);
    border-radius: var(--radius-sm); cursor: pointer; color: var(--text);
    font-family: 'Vazirmatn', sans-serif;
}}
.setting-row {{ display: flex; justify-content: space-between; align-items: center; padding: 4px 0; }}
.toggle-btn {{
    background: var(--surface-muted); border: 1px solid var(--divider);
    border-radius: 20px; padding: 6px 14px; cursor: pointer;
    font-family: 'Vazirmatn', sans-serif; color: var(--text-muted);
}}
.toggle-btn.on {{ background: var(--primary); color: #fff; border-color: var(--primary); }}
.recur-row {{ display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid var(--divider); }}
.recur-row:last-child {{ border-bottom: none; }}
.modal-error {{ color: var(--error); font-size: 12px; margin-bottom: 8px; text-align: center; }}
.modal-textarea {{ min-height: 80px; resize: vertical; }}
.hint {{ font-size: 11px; color: var(--text-muted); text-align: center; margin-top: 8px; }}
.toast {{
    position: fixed; top: calc(12px + var(--safe-top)); left: 50%; transform: translateX(-50%);
    background: var(--surface); color: var(--text); padding: 10px 20px;
    border-radius: 20px; border: 1px solid var(--divider); z-index: 600;
    opacity: 0; pointer-events: none; transition: opacity 0.2s; font-size: 13px;
}}
.toast.show {{ opacity: 1; }}
.toast.error {{ border-color: var(--error); color: var(--error); }}
.nav-icon {{
    display: block;
    font-size: 20px;
    line-height: 1;
    width: 24px;
    height: 24px;
    text-align: center;
    margin: 0 auto 2px;
}}
.well-static {{ cursor: default; }}
"""
