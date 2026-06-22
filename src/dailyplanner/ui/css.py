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
.fin-investment {{ color: #FFB020; }}
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
.fin-type-investment {{ color: #FFB020; }}
.btn-sm-invest {{
    background: #3D3018; color: #FFB020;
    padding: 4px 10px; border-radius: 14px;
    font-size: 12px; cursor: pointer;
    border: 1px solid #FFB02044;
    font-family: 'Vazirmatn', sans-serif;
}}
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
    z-index: 600;
    padding: max(12px, env(safe-area-inset-top)) 12px max(12px, env(safe-area-inset-bottom));
    direction: rtl;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
}}
.modal-box {{
    background: #1C1C1E;
    border-radius: 18px;
    padding: 20px 16px 16px;
    width: 100%;
    max-width: 360px;
    max-height: calc(100dvh - 24px - env(safe-area-inset-top) - env(safe-area-inset-bottom));
    border: 1px solid #3C3C3E;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    margin: auto;
}}
#modal-fields {{
    overflow-y: auto;
    flex: 1;
    min-height: 0;
    -webkit-overflow-scrolling: touch;
    padding-left: 2px;
    padding-right: 2px;
}}
.modal-title {{
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 14px;
    text-align: center;
    flex-shrink: 0;
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

.color-picker {{ margin-bottom: 12px; }}
.color-picker-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    direction: rtl;
    justify-items: center;
}}
.color-swatch {{
    width: 48px;
    height: 48px;
    border-radius: 50%;
    border: 3px solid transparent;
    cursor: pointer;
    padding: 0;
    flex-shrink: 0;
    box-shadow: inset 0 0 0 1px rgba(255,255,255,0.12);
    transition: transform 0.15s, border-color 0.15s;
    -webkit-tap-highlight-color: transparent;
}}
.color-swatch.selected {{
    border-color: #fff;
    transform: scale(1.06);
    box-shadow: 0 0 0 2px var(--primary), inset 0 0 0 1px rgba(255,255,255,0.2);
}}
.color-picker-label {{
    text-align: center;
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 8px;
}}

.modal-btns {{ display: flex; gap: 8px; direction: rtl; flex-shrink: 0; padding-top: 10px; }}
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
.cal-day.selected {{
    background: var(--primary) !important;
    color: #fff;
    font-weight: bold;
}}
.cal-day.today {{ box-shadow: inset 0 0 0 2px var(--primary); }}
.cal-day-empty {{ visibility: hidden; pointer-events: none; }}
.cal-weekdays {{
    display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px;
    margin-bottom: 4px; text-align: center; font-size: 10px; color: var(--text-muted);
}}
.date-picker {{ margin-bottom: 12px; }}
.date-picker-cal {{ margin: 0; padding: 8px; }}
.date-picker-label {{
    text-align: center; font-size: 13px; color: var(--text);
    margin-bottom: 8px; font-weight: bold;
}}
.date-picker-clear {{
    display: block; width: 100%; margin-top: 8px;
    background: var(--surface-muted); color: var(--text-muted);
    border: 1px solid var(--divider); border-radius: var(--radius-sm);
    padding: 10px 8px; font-size: 12px; cursor: pointer;
    font-family: 'Vazirmatn', sans-serif;
    -webkit-tap-highlight-color: transparent;
}}
.date-picker-cal .cal-day {{
    padding: 6px 2px; font-size: 11px; min-height: 32px;
}}
.date-picker-cal .cal-nav {{ padding: 6px 10px; font-size: 16px; }}
.streak-badge {{
    text-align: center; font-size: 13px; color: var(--warning);
    padding: 4px 8px; margin: 0 8px;
}}
.chart-box {{ padding: 8px 12px; }}
.sparkline {{ width: 100%; height: 60px; display: block; }}
.fin-chart-legend {{
    display: flex; justify-content: center; gap: 16px;
    font-size: 11px; color: var(--text-muted); margin-bottom: 6px; flex-wrap: wrap;
}}
.fin-legend-item {{ display: flex; align-items: center; gap: 4px; }}
.fin-legend-dot {{ width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }}
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
.modal-error {{ color: var(--error); font-size: 12px; margin-bottom: 8px; text-align: center; flex-shrink: 0; }}
.modal-textarea {{ min-height: 80px; resize: vertical; }}
.hint {{ font-size: 11px; color: var(--text-muted); text-align: center; margin-top: 8px; }}

/* ── Settings / Backup ── */
.settings-page {{ padding-bottom: 16px; }}
.settings-section {{ margin-top: 10px; }}
.section-desc {{
    font-size: 12px;
    color: var(--text-muted);
    line-height: 1.6;
    margin: 6px 0 12px;
}}
.setting-label {{ display: flex; flex-direction: column; gap: 2px; }}
.setting-name {{ font-size: 14px; color: var(--text); }}
.setting-desc {{ font-size: 11px; color: var(--text-muted); }}
.section-btn {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    width: 100%;
    padding: 13px 16px;
    border-radius: var(--radius-sm);
    font-size: 14px;
    font-family: 'Vazirmatn', sans-serif;
    cursor: pointer;
    border: none;
    margin-top: 4px;
}}
.section-btn-icon {{ font-size: 16px; line-height: 1; }}
.section-btn-primary {{
    background: linear-gradient(135deg, #3D5AFE, #8B00E0);
    color: #fff;
    box-shadow: 0 4px 14px rgba(61,90,254,0.3);
}}
.section-btn-danger {{
    background: var(--error-bg);
    color: var(--error);
    border: 1px solid rgba(255,89,89,0.35);
    margin-top: 10px;
}}
.backup-meta {{
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 10px;
}}
.backup-file-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    color: var(--text-muted);
    background: var(--surface-muted);
    border: 1px solid var(--divider);
    border-radius: 20px;
    padding: 5px 12px;
    direction: ltr;
    font-family: monospace;
}}
.backup-toggle {{
    display: block;
    width: 100%;
    margin-top: 10px;
    padding: 8px;
    background: none;
    border: none;
    color: var(--primary);
    font-size: 12px;
    font-family: 'Vazirmatn', sans-serif;
    cursor: pointer;
    text-align: center;
}}
.import-section {{
    border-color: rgba(255,115,89,0.25);
}}
.import-warning {{
    display: flex;
    align-items: flex-start;
    gap: 8px;
    background: rgba(255,115,89,0.08);
    border: 1px solid rgba(255,115,89,0.22);
    border-radius: var(--radius-sm);
    padding: 10px 12px;
    margin-bottom: 10px;
    font-size: 12px;
    line-height: 1.6;
    color: var(--warning);
}}
.import-warning-icon {{
    flex-shrink: 0;
    font-size: 15px;
    line-height: 1.4;
}}
.backup-ta {{
    width: 100%;
    min-height: 120px;
    max-height: 240px;
    background: var(--surface-muted);
    color: var(--text);
    border: 1px solid var(--divider);
    border-radius: var(--radius-sm);
    padding: 10px 12px;
    font-size: 11px;
    font-family: 'Courier New', Courier, monospace;
    direction: ltr;
    text-align: left;
    resize: vertical;
    box-sizing: border-box;
    margin-top: 8px;
    outline: none;
    line-height: 1.5;
}}
.backup-ta:focus {{ border-color: var(--primary); }}
.backup-ta::placeholder {{ color: var(--text-muted); opacity: 0.7; }}
.backup-preview {{ font-size: 10px; max-height: 200px; }}
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

/* ── Finance screen ── */
.fin-page {{ padding-bottom: 8px; }}

.fin-hero {{
    margin: 12px 12px 0;
    padding: 20px 18px 16px;
    background: linear-gradient(145deg, #1E1E3A 0%, #1C1C1E 60%, #162016 100%);
    border-radius: 18px;
    border: 1px solid #3C3C5E44;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    text-align: center;
}}
.fin-hero-label {{ font-size: 12px; color: var(--text-muted); margin-bottom: 4px; }}
.fin-hero-balance {{
    font-size: 28px; font-weight: bold; letter-spacing: -0.5px;
    font-variant-numeric: tabular-nums; line-height: 1.2;
}}
.fin-hero-balance.positive {{ color: #4DD980; }}
.fin-hero-balance.negative {{ color: #FF7359; }}
.fin-hero-unit {{ font-size: 12px; font-weight: normal; color: var(--text-muted); margin-right: 4px; }}
.fin-hero-stats {{
    display: flex; gap: 10px; margin-top: 16px; direction: rtl;
}}
.fin-hero-stat {{
    flex: 1; display: flex; align-items: center; gap: 8px;
    background: rgba(255,255,255,0.04); border-radius: 12px;
    padding: 10px 12px; border: 1px solid #ffffff0a;
}}
.fin-stat-icon {{
    width: 28px; height: 28px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; font-weight: bold; flex-shrink: 0;
}}
.fin-hero-stat.income .fin-stat-icon {{ background: #1A4028; color: #4DD980; }}
.fin-hero-stat.expense .fin-stat-icon {{ background: #3D1818; color: #FF7359; }}
.fin-stat-lbl {{ display: block; font-size: 10px; color: var(--text-muted); }}
.fin-stat-val {{ display: block; font-size: 13px; font-weight: bold; font-variant-numeric: tabular-nums; }}

.fin-actions {{
    display: flex; gap: 8px; padding: 12px 12px 4px; direction: rtl;
}}
.fin-action-btn {{
    flex: 1; display: flex; align-items: center; justify-content: center; gap: 6px;
    padding: 11px 8px; border-radius: 12px; border: none; cursor: pointer;
    font-family: 'Vazirmatn', sans-serif; font-size: 13px; font-weight: bold;
    transition: opacity 0.15s;
}}
.fin-action-btn:active {{ opacity: 0.75; }}
.fin-action-icon {{ font-size: 16px; line-height: 1; }}
.fin-action-btn.income {{ background: #1A4028; color: #4DD980; border: 1px solid #4DD98033; }}
.fin-action-btn.expense {{ background: #3D1818; color: #FF7359; border: 1px solid #FF595933; }}
.fin-action-btn.invest {{ background: #3D3018; color: #FFB020; border: 1px solid #FFB02033; }}
.fin-action-btn.budget {{ background: #1A1A40; color: #7B8CDE; border: 1px solid #5E5CE633; }}
.fin-hero-invest {{
    margin-top: 12px; padding: 8px 12px; border-radius: 10px;
    background: rgba(255,176,32,0.1); border: 1px solid rgba(255,176,32,0.2);
    font-size: 12px; color: #FFB020; display: flex; align-items: center; gap: 6px; justify-content: center;
}}
.fin-hero-invest-note {{ font-size: 10px; color: var(--text-muted); }}

.fin-card {{
    background: var(--surface); border-radius: 16px;
    margin: 10px 12px; padding: 14px 14px 12px;
    border: 1px solid var(--divider);
}}
.fin-card-head {{
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 12px; direction: rtl;
}}
.fin-card-title {{ font-size: 14px; font-weight: bold; }}
.fin-card-badge {{
    background: var(--surface-muted); color: var(--text-muted);
    font-size: 11px; padding: 2px 8px; border-radius: 10px;
}}
.fin-card-actions {{ display: flex; gap: 6px; }}

.fin-chip-btn {{
    background: var(--surface-muted); border: 1px solid var(--divider);
    color: var(--text-muted); padding: 4px 10px; border-radius: 14px;
    font-size: 11px; cursor: pointer; font-family: 'Vazirmatn', sans-serif;
}}
.fin-chip-btn.primary {{ background: rgba(94,92,230,0.15); color: var(--primary); border-color: #5E5CE644; }}

.fin-empty {{
    text-align: center; padding: 20px 12px; color: var(--text-muted);
}}
.fin-empty-icon {{ font-size: 32px; display: block; margin-bottom: 8px; opacity: 0.6; }}
.fin-empty p {{ font-size: 12px; margin-bottom: 12px; line-height: 1.6; }}
.fin-empty-btn {{
    background: var(--primary); color: #fff; border: none;
    padding: 8px 18px; border-radius: 20px; font-size: 12px;
    cursor: pointer; font-family: 'Vazirmatn', sans-serif;
}}

.finance-line-chart {{ width: 100%; height: 130px; display: block; }}
.fin-chart-wrap {{ margin: 0 -4px; }}
.fin-chart-legend {{
    display: flex; justify-content: center; gap: 14px;
    font-size: 11px; color: var(--text-muted); margin-bottom: 8px; flex-wrap: wrap;
}}
.fin-legend-item {{ display: flex; align-items: center; gap: 4px; }}
.fin-legend-dot {{ width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }}

.fin-date-chip {{
    font-size: 11px; color: var(--primary); background: rgba(94,92,230,0.12);
    padding: 3px 10px; border-radius: 10px; display: inline-block;
    margin: 8px 0 4px; font-weight: bold;
}}
.fin-txn {{
    display: flex; align-items: center; gap: 10px;
    padding: 10px 0; border-bottom: 1px solid var(--surface-muted);
    direction: rtl;
}}
.fin-txn:last-child {{ border-bottom: none; }}
.fin-txn-icon {{
    width: 36px; height: 36px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; font-weight: bold; flex-shrink: 0;
}}
.fin-txn.income .fin-txn-icon {{ background: #1A4028; color: #4DD980; }}
.fin-txn.expense .fin-txn-icon {{ background: #3D1818; color: #FF7359; }}
.fin-txn.income {{ border-right: 3px solid #4DD980; padding-right: 8px; margin-right: -3px; }}
.fin-txn.expense {{ border-right: 3px solid #FF7359; padding-right: 8px; margin-right: -3px; }}
.fin-txn-body {{ flex: 1; min-width: 0; }}
.fin-txn-title {{ font-size: 14px; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
.fin-txn-meta {{ font-size: 11px; color: var(--text-muted); margin-top: 2px; }}
.fin-txn-cat {{ opacity: 0.85; }}
.fin-txn-right {{ text-align: left; flex-shrink: 0; }}
.fin-txn-amount {{ font-size: 14px; font-weight: bold; font-variant-numeric: tabular-nums; }}
.fin-txn.income .fin-txn-amount {{ color: #4DD980; }}
.fin-txn.expense .fin-txn-amount {{ color: #FF7359; }}
.fin-txn.investment .fin-txn-icon {{ background: #3D3018; color: #FFB020; }}
.fin-txn.investment {{ border-right: 3px solid #FFB020; padding-right: 8px; margin-right: -3px; }}
.fin-txn.investment .fin-txn-amount {{ color: #FFB020; }}
.fin-txn-tag {{
    font-size: 10px; background: rgba(255,176,32,0.15); color: #FFB020;
    padding: 1px 6px; border-radius: 8px;
}}
.fin-txn-btns {{ display: flex; gap: 2px; justify-content: flex-end; margin-top: 2px; }}
.fin-txn-btn {{
    background: none; border: none; color: var(--text-muted);
    font-size: 14px; cursor: pointer; padding: 2px 5px; border-radius: 6px;
}}
.fin-txn-btn.del {{ color: #FF595988; }}
.fin-txn-btn:active {{ background: var(--surface-muted); }}

.fin-budget-item {{
    padding: 10px 0; border-bottom: 1px solid var(--surface-muted);
}}
.fin-budget-item:last-child {{ border-bottom: none; }}
.fin-budget-item.over {{ background: rgba(255,89,89,0.04); margin: 0 -8px; padding: 10px 8px; border-radius: 10px; }}
.fin-budget-top {{ display: flex; align-items: center; gap: 8px; direction: rtl; }}
.fin-budget-icon {{ font-size: 20px; flex-shrink: 0; }}
.fin-budget-info {{ flex: 1; min-width: 0; }}
.fin-budget-name {{ font-size: 13px; font-weight: bold; }}
.fin-budget-sub {{ font-size: 11px; color: var(--text-muted); margin-top: 1px; }}
.fin-budget-pct {{ font-size: 12px; font-weight: bold; color: var(--primary); min-width: 32px; text-align: center; }}
.fin-budget-item.over .fin-budget-pct {{ color: var(--error); }}
.fin-budget-track {{
    height: 5px; border-radius: 3px; background: var(--surface-muted);
    overflow: hidden; margin-top: 8px;
}}
.fin-budget-fill {{
    height: 100%; border-radius: 3px;
    background: linear-gradient(90deg, var(--primary), var(--success));
    transition: width 0.4s ease;
}}
.fin-budget-fill.over {{ background: linear-gradient(90deg, #FF7359, var(--error)); }}
.fin-budget-empty {{ font-size: 11px; color: var(--text-muted); margin-top: 6px; }}
.fin-budget-empty a {{ color: var(--primary); }}
.fin-budget-warn {{ font-size: 10px; color: var(--error); margin-top: 4px; }}

.fin-daily-table {{ direction: rtl; }}
.fin-daily-head, .fin-daily-row {{
    display: grid; grid-template-columns: 1.1fr 0.9fr 0.9fr 0.9fr 0.9fr;
    gap: 4px; padding: 6px 0; font-size: 10px; align-items: center;
}}
.fin-daily-head {{ color: var(--text-muted); border-bottom: 1px solid var(--divider); font-weight: bold; }}
.fin-daily-row {{ border-bottom: 1px solid var(--surface-muted); }}
.fin-daily-row:last-child {{ border-bottom: none; }}
.fin-daily-date {{ color: var(--text-muted); }}
.fin-daily-inc {{ color: #4DD980; font-variant-numeric: tabular-nums; }}
.fin-daily-exp {{ color: #FF7359; font-variant-numeric: tabular-nums; }}
.fin-daily-inv {{ color: #FFB020; font-variant-numeric: tabular-nums; }}
.fin-daily-net {{ font-weight: bold; font-variant-numeric: tabular-nums; }}
.fin-daily-net.pos {{ color: #4DD980; }}
.fin-daily-net.neg {{ color: #FF7359; }}

/* legacy budget styles (home screen) */
.budget-row {{ margin-bottom: 12px; }}
.budget-row:last-child {{ margin-bottom: 0; }}
.budget-row-head {{
    display: flex; align-items: center; justify-content: space-between;
    font-size: 13px; margin-bottom: 4px; gap: 6px;
}}
.budget-cat {{ flex: 1; font-weight: bold; }}
.budget-amounts {{ font-size: 12px; color: var(--text-muted); }}
.budget-bar {{
    height: 6px; border-radius: 3px; background: var(--surface-muted); overflow: hidden;
}}
.budget-bar-fill {{
    height: 100%; border-radius: 3px;
    background: linear-gradient(90deg, var(--primary), var(--success));
    transition: width 0.3s;
}}
.budget-bar-fill.over {{ background: var(--error); }}
.budget-over {{ font-size: 11px; color: var(--error); margin-top: 2px; }}
.budget-none {{ font-size: 11px; color: var(--text-muted); margin-top: 2px; }}
.fin-date-header {{
    font-size: 12px; color: var(--text-muted); padding: 8px 0 4px;
    border-bottom: 1px solid var(--divider); margin-bottom: 4px;
}}
.daily-fin-row {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 6px 0; font-size: 12px; border-bottom: 1px solid var(--surface-muted);
    gap: 4px; flex-wrap: wrap;
}}
.daily-fin-row:last-child {{ border-bottom: none; }}
.daily-fin-date {{ color: var(--text-muted); min-width: 72px; }}

/* ── Projects ── */
.proj-page {{ padding-bottom: 12px; }}

.proj-header {{
    background: linear-gradient(135deg, #3D5AFE 0%, #5E5CE6 50%, #8B00E0 100%);
    padding: calc(16px + var(--safe-top)) 16px 18px;
    box-shadow: 0 4px 20px rgba(94,92,230,0.35);
}}
@media (hover: none) and (pointer: coarse) {{
    .proj-header {{ padding-top: calc(16px + max(36px, var(--safe-top))); }}
}}
.proj-header-top {{
    display: flex; align-items: center; justify-content: space-between; gap: 10px;
    margin-bottom: 14px;
}}
.proj-header-title {{ font-size: 18px; font-weight: bold; color: #fff; }}
.proj-header-add {{
    background: rgba(255,255,255,0.18); color: #fff; border: 1px solid rgba(255,255,255,0.25);
    padding: 8px 14px; border-radius: 20px; font-size: 12px; font-weight: bold;
    cursor: pointer; font-family: 'Vazirmatn', sans-serif; white-space: nowrap;
    backdrop-filter: blur(4px);
}}
.proj-header-add:active {{ background: rgba(255,255,255,0.28); }}
.proj-summary {{
    display: flex; gap: 8px; direction: rtl;
}}
.proj-summary-item {{
    flex: 1; text-align: center; background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.15); border-radius: 12px; padding: 10px 6px;
}}
.proj-summary-val {{ display: block; font-size: 16px; font-weight: bold; color: #fff; font-variant-numeric: tabular-nums; }}
.proj-summary-lbl {{ display: block; font-size: 10px; color: rgba(255,255,255,0.75); margin-top: 2px; }}

.proj-section {{ padding: 12px 12px 0; }}
.proj-section-head {{
    display: flex; align-items: center; gap: 8px; margin-bottom: 10px;
}}
.proj-section-title {{ font-size: 14px; font-weight: bold; }}
.proj-section-badge {{
    background: var(--surface-muted); color: var(--text-muted);
    font-size: 11px; padding: 2px 8px; border-radius: 10px;
}}
.proj-empty-mini {{
    text-align: center; color: var(--text-muted); font-size: 13px; padding: 20px 12px;
}}

.proj-card {{
    position: relative; background: var(--surface); border-radius: 16px;
    border: 1px solid var(--divider); margin-bottom: 10px; overflow: hidden;
    display: flex; align-items: stretch; box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    transition: transform 0.15s;
}}
.proj-card:active {{ transform: scale(0.985); }}
.proj-card.muted {{ opacity: 0.7; }}
.proj-card-accent {{
    width: 5px; flex-shrink: 0; background: var(--project-color, var(--primary));
}}
.proj-card-body {{ flex: 1; padding: 14px 10px 14px 14px; cursor: pointer; min-width: 0; }}
.proj-card-top {{ display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }}
.proj-card-info {{ flex: 1; min-width: 0; }}
.proj-card-title {{
    font-size: 15px; font-weight: bold; margin-bottom: 6px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}
.proj-card-meta {{ font-size: 11px; color: var(--text-muted); margin-top: 6px; }}
.proj-card-menu {{
    align-self: stretch; width: 40px; flex-shrink: 0;
    background: none; border: none; border-right: 1px solid var(--divider);
    color: var(--text-muted); font-size: 18px; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
}}
.proj-card-menu:active {{ background: var(--surface-muted); }}

.proj-deadline-badge {{
    display: inline-block; font-size: 10px; padding: 3px 8px; border-radius: 10px;
    background: rgba(255,255,255,0.06); color: var(--text-muted);
    border: 1px solid var(--divider); margin-top: 2px;
}}
.proj-deadline-badge.overdue {{ background: var(--error-bg); color: var(--error); border-color: #FF595944; }}
.proj-deadline-badge.today {{ background: rgba(255,179,64,0.12); color: #FFB340; border-color: #FFB34044; }}

.proj-bar {{
    height: 5px; border-radius: 3px; background: var(--surface-muted); overflow: hidden;
}}
.proj-bar-lg {{ height: 8px; border-radius: 4px; margin-top: 4px; }}
.proj-bar-fill {{
    height: 100%; border-radius: inherit; background: var(--project-color, var(--primary));
    transition: width 0.35s ease;
}}
.proj-ring {{ flex-shrink: 0; color: var(--text); }}

.proj-done-toggle {{
    width: 100%; display: flex; align-items: center; gap: 8px;
    background: var(--surface); border: 1px solid var(--divider); border-radius: 12px;
    padding: 12px 14px; cursor: pointer; font-family: 'Vazirmatn', sans-serif;
    font-size: 13px; color: var(--text-muted); margin-bottom: 10px;
}}
.proj-done-toggle.open {{ border-color: var(--primary); color: var(--text); }}
.proj-done-chevron {{ margin-right: auto; font-size: 12px; }}

/* detail page */
.proj-detail-page {{ padding-bottom: 16px; --project-color: var(--primary); }}
.proj-detail-hero {{
    position: relative; padding: calc(12px + var(--safe-top)) 16px 18px;
    background: #1C1C1E; overflow: hidden;
}}
@media (hover: none) and (pointer: coarse) {{
    .proj-detail-hero {{ padding-top: calc(12px + max(36px, var(--safe-top))); }}
}}
.proj-detail-hero::before {{
    content: ''; position: absolute; inset: 0;
    background: linear-gradient(145deg, var(--project-color) 0%, transparent 55%);
    opacity: 0.22; pointer-events: none;
}}
.proj-detail-nav {{
    position: relative; display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 16px;
}}
.proj-back-btn {{
    background: rgba(255,255,255,0.12); color: #fff; border: none;
    width: 38px; height: 38px; border-radius: 50%; font-size: 18px;
    cursor: pointer; display: flex; align-items: center; justify-content: center;
}}
.proj-detail-actions-top {{ display: flex; gap: 8px; }}
.proj-icon-btn {{
    background: rgba(255,255,255,0.1); color: #fff; border: 1px solid rgba(255,255,255,0.15);
    width: 38px; height: 38px; border-radius: 50%; font-size: 15px; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
}}
.proj-icon-btn.danger {{ background: rgba(255,89,89,0.15); border-color: #FF595944; }}
.proj-detail-hero-body {{
    position: relative; display: flex; align-items: center; gap: 16px; margin-bottom: 14px;
}}
.proj-detail-hero-text {{ flex: 1; min-width: 0; }}
.proj-detail-name {{ font-size: 20px; font-weight: bold; margin-bottom: 8px; line-height: 1.3; }}
.proj-detail-sub {{ font-size: 12px; color: var(--text-muted); margin-top: 8px; }}
.proj-detail-hero .proj-deadline-badge {{
    background: rgba(255,255,255,0.12); color: rgba(255,255,255,0.92);
    border-color: rgba(255,255,255,0.2);
}}
.proj-detail-hero .proj-deadline-badge.overdue {{ background: rgba(255,89,89,0.2); color: #FF8A8A; border-color: #FF595966; }}
.proj-detail-hero .proj-deadline-badge.today {{ background: rgba(255,179,64,0.2); color: #FFD080; border-color: #FFB34066; }}
.proj-done-toggle-btn {{
    position: relative; width: 100%; margin-top: 14px;
    background: rgba(255,255,255,0.06); color: var(--text-muted);
    border: 1px dashed var(--divider); border-radius: 12px;
    padding: 11px; font-size: 12px; cursor: pointer;
    font-family: 'Vazirmatn', sans-serif;
}}
.proj-done-toggle-btn.on {{
    background: var(--success-bg); color: var(--success); border-style: solid; border-color: #4DD98044;
}}

.proj-tasks-card {{
    background: var(--surface); border-radius: 16px;
    margin: 12px; padding: 14px; border: 1px solid var(--divider);
}}
.proj-task-list {{ margin-bottom: 12px; }}
.proj-task-item {{
    display: flex; align-items: center; gap: 10px;
    padding: 10px 0; border-bottom: 1px solid var(--surface-muted);
}}
.proj-task-item:last-child {{ border-bottom: none; }}
.proj-task-item.done {{ opacity: 0.75; }}
.proj-task-check {{
    width: 26px; height: 26px; border-radius: 50%; flex-shrink: 0;
    border: 2px solid var(--divider); background: transparent;
    color: transparent; font-size: 13px; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Vazirmatn', sans-serif; transition: all 0.15s;
}}
.proj-task-check.checked {{
    background: var(--success); border-color: var(--success); color: #fff;
}}
.proj-task-body {{ flex: 1; min-width: 0; cursor: pointer; }}
.proj-task-title {{ font-size: 14px; line-height: 1.4; word-break: break-word; }}
.proj-task-item.done .proj-task-title {{ text-decoration: line-through; color: var(--text-muted); }}
.proj-task-actions {{ display: flex; align-items: center; gap: 6px; flex-shrink: 0; }}
.proj-today-chip {{
    font-size: 10px; padding: 4px 10px; border-radius: 12px;
    background: rgba(90,200,250,0.12); color: #5AC8FA;
    border: 1px solid #5AC8FA44; cursor: pointer;
    font-family: 'Vazirmatn', sans-serif; white-space: nowrap;
}}
.proj-today-chip.done {{
    background: var(--success-bg); color: var(--success); border-color: #4DD98055; cursor: default;
}}
.proj-task-del {{
    width: 28px; height: 28px; border-radius: 50%; border: none;
    background: var(--surface-muted); color: var(--text-muted);
    font-size: 16px; cursor: pointer; display: flex; align-items: center; justify-content: center;
}}
.proj-task-del:active {{ background: var(--error-bg); color: var(--error); }}
.proj-add-task-btn {{
    width: 100%; background: rgba(94,92,230,0.12); color: var(--primary);
    border: 1px dashed #5E5CE655; border-radius: 12px; padding: 12px;
    font-size: 13px; font-weight: bold; cursor: pointer;
    font-family: 'Vazirmatn', sans-serif;
}}
.proj-add-task-btn:active {{ background: rgba(94,92,230,0.2); }}

/* action sheet */
.proj-sheet-overlay {{
    position: fixed; inset: 0; background: rgba(0,0,0,0.55);
    z-index: 500; display: flex; align-items: flex-end; justify-content: center;
    padding: 0 0 calc(var(--safe-bottom));
}}
.proj-sheet {{
    width: 100%; max-width: 480px; background: var(--surface);
    border-radius: 20px 20px 0 0; padding: 8px 16px calc(16px + var(--safe-bottom));
    border-top: 1px solid var(--divider);
    animation: projSheetUp 0.25s ease;
}}
@keyframes projSheetUp {{
    from {{ transform: translateY(100%); }}
    to {{ transform: translateY(0); }}
}}
.proj-sheet-handle {{
    width: 36px; height: 4px; background: var(--divider); border-radius: 2px;
    margin: 4px auto 12px;
}}
.proj-sheet-title {{
    font-size: 14px; font-weight: bold; text-align: center;
    margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid var(--divider);
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}
.proj-sheet-btn {{
    display: block; width: 100%; text-align: center;
    background: var(--surface-muted); color: var(--text);
    border: 1px solid var(--divider); border-radius: 12px;
    padding: 14px; margin-bottom: 8px; font-size: 14px;
    cursor: pointer; font-family: 'Vazirmatn', sans-serif;
}}
.proj-sheet-btn.danger {{ background: var(--error-bg); color: var(--error); border-color: #FF595933; }}
.proj-sheet-btn.cancel {{ background: transparent; color: var(--text-muted); border: none; margin-top: 4px; }}

/* Projects — mobile tweaks */
@media (max-width: 400px) {{
    .proj-header-title {{ font-size: 16px; }}
    .proj-header-add {{ padding: 7px 10px; font-size: 11px; }}
    .proj-summary-val {{ font-size: 14px; }}
    .proj-card-body {{ padding: 12px 8px 12px 12px; }}
    .proj-card-top {{ gap: 8px; }}
    .proj-ring {{ transform: scale(0.9); transform-origin: center; }}
    .proj-detail-name {{ font-size: 17px; word-break: break-word; }}
    .proj-detail-hero-body {{ gap: 10px; }}
    .proj-detail-hero-body .proj-ring {{ transform: scale(0.82); transform-origin: center; }}
    .proj-done-toggle-btn {{ font-size: 11px; padding: 10px 8px; line-height: 1.5; }}
    .proj-task-item {{ gap: 8px; flex-wrap: wrap; }}
    .proj-task-body {{ flex: 1 1 calc(100% - 38px); order: 1; }}
    .proj-task-check {{ order: 0; }}
    .proj-task-actions {{ order: 2; margin-right: auto; }}
    .proj-tasks-card {{ margin: 10px 8px; padding: 12px; }}
    .proj-section {{ padding: 10px 8px 0; }}
    .color-swatch {{ width: 44px; height: 44px; }}
}}
@media (max-width: 340px) {{
    .nav-btn {{ font-size: 11px; padding: 5px 2px; }}
    .nav-icon {{ font-size: 18px; }}
    .color-picker-grid {{ gap: 6px; }}
    .color-swatch {{ width: 40px; height: 40px; }}
}}
"""
