"""CSS for the WebView-based UI (dark theme + Vazirmatn)."""
import base64
from pathlib import Path
from functools import lru_cache

from dailyplanner.ui.tokens import TOKENS_CSS
from dailyplanner.utils.platform import is_android


def _font_candidates(name: str) -> list[Path]:
    roots = [Path(__file__).parents[i] for i in (4, 3, 2)]
    return [root / "resources" / "fonts" / name for root in roots]


@lru_cache(maxsize=8)
def _load_font_b64(filename: str) -> str:
    if is_android():
        return ""
    for p in _font_candidates(filename):
        if p.exists():
            return base64.b64encode(p.read_bytes()).decode()
    return ""


def _font_face(weight: int, filename: str, fallback: str = "") -> str:
    b64 = _load_font_b64(filename)
    if b64:
        return f"""
@font-face {{
    font-family: 'Vazirmatn';
    src: url('data:font/truetype;base64,{b64}') format('truetype');
    font-weight: {weight};
    font-style: normal;
}}"""
    return fallback


def get_css() -> str:
    font_face = ""
    if not is_android():
        font_face = (
            _font_face(400, "Vazirmatn-Regular.ttf")
            + _font_face(500, "Vazirmatn-Medium.ttf")
            + _font_face(700, "Vazirmatn-Bold.ttf", _font_face(700, "Vazirmatn-Regular.ttf"))
        )

    return f"""
{font_face}

{TOKENS_CSS}

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html {{
    scroll-padding-bottom: var(--keyboard-inset);
}}
html, body {{
    background: var(--gradient-mesh), var(--bg);
    background-attachment: fixed;
    color: var(--text);
    font-family: 'Vazirmatn', -apple-system, Tahoma, sans-serif;
    direction: rtl;
    min-height: 100vh;
    overflow-x: hidden;
    -webkit-tap-highlight-color: transparent;
    -webkit-text-size-adjust: 100%;
    font-size: var(--text-base);
    line-height: 1.5;
    font-variant-numeric: tabular-nums;
}}
html.modal-open,
body.modal-open {{
    overflow: hidden;
}}
body.modal-open .screen {{
    overflow: hidden;
    touch-action: none;
}}
body.modal-open .modal-overlay {{
    touch-action: auto;
}}
body.kb-open:not(.modal-open) {{
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
    touch-action: pan-y;
    max-height: var(--visual-vh, 100dvh);
}}
body.kb-open .content {{
    padding-bottom: calc(24px + var(--keyboard-inset));
}}
body.kb-open .screen {{
    min-height: 0;
}}
body.kb-open.has-bottom-nav .content {{
    padding-bottom: calc(88px + max(48px, var(--safe-bottom)) + var(--keyboard-inset));
}}
body.kb-open .bottom-nav {{
    transform: translateX(-50%) translateY(calc(var(--keyboard-inset) + 100px));
    opacity: 0;
    pointer-events: none;
}}

a {{ text-decoration: none; color: inherit; }}

button, input, select, textarea {{ font-family: inherit; }}
input:not([type="hidden"]), textarea, select {{
    scroll-margin-top: 16px;
    scroll-margin-bottom: calc(var(--keyboard-inset) + 24px);
}}
@media (hover: none) and (pointer: coarse) {{
    .modal-input, .note-input, .search-input, .backup-ta {{
        font-size: 16px;
    }}
}}
button {{ cursor: pointer; }}

button:focus-visible, a:focus-visible, input:focus-visible,
textarea:focus-visible, select:focus-visible {{
    outline: 2px solid var(--primary);
    outline-offset: 2px;
}}

/* ── Layout ── */
.screen {{ display: flex; flex-direction: column; min-height: 100vh; }}
.content {{
    flex: 1;
    padding-bottom: calc(88px + var(--safe-bottom));
    max-width: 520px;
    margin: 0 auto;
    width: 100%;
}}
.screen-enter {{
    animation: screenIn var(--duration-normal) var(--ease-out);
}}

/* ── Bottom Nav — floating dock ── */
.bottom-nav {{
    position: fixed;
    bottom: calc(12px + var(--safe-bottom));
    left: 50%;
    transform: translateX(-50%);
    width: calc(100% - 32px);
    max-width: 520px;
    background: var(--nav-bar);
    backdrop-filter: blur(var(--glass-blur));
    -webkit-backdrop-filter: blur(var(--glass-blur));
    display: flex;
    padding: 6px 8px;
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    z-index: 200;
    box-shadow: var(--shadow-nav);
}}
@supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {{
    .bottom-nav {{ background: var(--surface-deep); }}
}}

/* Android gesture / 3-button nav bar — env() is often 0 in WebView */
@media (hover: none) and (pointer: coarse) {{
    .content {{ padding-bottom: calc(88px + max(48px, var(--safe-bottom))); }}
    .bottom-nav {{ bottom: calc(12px + max(48px, var(--safe-bottom))); }}
}}
.nav-btn {{
    flex: 1;
    color: var(--text-muted);
    font-size: var(--text-sm);
    padding: 6px 4px;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-family: 'Vazirmatn', sans-serif;
    cursor: pointer;
    border-radius: var(--radius-sm);
    margin: 0 2px;
    transition: background var(--duration-fast), color var(--duration-fast), transform var(--duration-fast);
    border: none;
    background: none;
    min-height: 48px;
    position: relative;
}}
.nav-btn:active {{ transform: scale(0.95); background: var(--surface-muted); }}
.nav-btn.active {{
    color: var(--primary);
    background: rgba(99, 102, 241, 0.14);
}}
.nav-btn.active.nav-finance {{
    color: #4DD980;
    background: rgba(77, 217, 128, 0.14);
}}
.nav-btn.active.nav-finance::after {{ background: #4DD980; }}
.nav-btn.active.nav-home {{
    color: #38BDF8;
    background: rgba(56, 189, 248, 0.16);
}}
.nav-btn.active.nav-home::after {{ background: #FBBF24; }}
.nav-btn.active.nav-projects {{
    color: #818CF8;
    background: rgba(99, 102, 241, 0.18);
}}
.nav-btn.active.nav-projects::after {{ background: #818CF8; }}
.nav-btn.active.nav-analytics {{
    color: #A78BFA;
    background: rgba(167, 139, 250, 0.16);
}}
.nav-btn.active.nav-analytics::after {{ background: #A78BFA; }}
.nav-btn.active::after {{
    content: '';
    position: absolute;
    bottom: 4px;
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: var(--primary);
}}

/* ── Date Header — hero zone ── */
.date-header {{
    background: var(--gradient-hero);
    padding: calc(14px + var(--safe-top)) var(--space-4) var(--space-3);
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
    direction: rtl;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: var(--shadow);
    overflow: hidden;
}}
.date-header::before {{
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse at 85% 15%, rgba(255,255,255,0.14), transparent 55%);
    pointer-events: none;
}}
.date-header-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-2);
    position: relative;
    z-index: 1;
}}
.date-header-tools {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    flex-wrap: wrap;
    position: relative;
    z-index: 1;
}}

@media (hover: none) and (pointer: coarse) {{
    .date-header:not(.home-header):not(.fin-header) {{
        padding-top: calc(14px + max(36px, var(--safe-top)));
    }}
    .home-header,
    .fin-header {{
        padding-top: calc(10px + max(36px, var(--safe-top)));
    }}
    .analytics-period {{
        padding-top: max(36px, var(--safe-top));
    }}
}}
.date-title {{
    color: #fff;
    font-size: var(--text-md);
    font-weight: var(--font-bold);
    text-align: center;
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    letter-spacing: 0.02em;
    padding: 0 var(--space-2);
}}
[data-theme="light"] .date-title {{ color: var(--primary-light); }}
.date-nav-btn {{
    background: rgba(255,255,255,0.16);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    color: #fff;
    width: 36px; height: 36px;
    border-radius: 50%;
    font-size: 20px;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer;
    border: 1px solid rgba(255,255,255,0.12);
    transition: background var(--duration-fast), transform var(--duration-fast);
    flex-shrink: 0;
    padding: 0;
    font-family: inherit;
}}
.date-nav-btn .ico {{ width: 18px; height: 18px; }}
[data-theme="light"] .date-nav-btn {{
    background: rgba(99,102,241,0.12);
    color: var(--primary);
    border-color: rgba(99,102,241,0.2);
}}
[data-theme="light"] .date-nav-btn .ico {{ color: var(--primary); }}
.date-nav-btn:hover {{ background: rgba(255,255,255,0.24); }}
.date-nav-btn:active {{ transform: scale(0.92); }}
.today-btn {{
    background: rgba(255,255,255,0.16);
    backdrop-filter: blur(8px);
    color: #fff;
    padding: 5px 12px;
    border-radius: var(--radius-full);
    font-size: var(--text-sm);
    cursor: pointer;
    border: 1px solid rgba(255,255,255,0.2);
    font-family: 'Vazirmatn', sans-serif;
    white-space: nowrap;
    font-weight: var(--font-medium);
    box-shadow: 0 0 16px rgba(255,255,255,0.12);
}}
[data-theme="light"] .today-btn {{
    background: var(--primary);
    color: #fff;
    border-color: transparent;
}}

/* ── Home (Today) screen ── */
.home-page {{ padding-bottom: 8px; }}

.home-header,
.fin-header {{
    padding: calc(10px + var(--safe-top)) 14px 10px;
    gap: 8px;
}}

.home-header {{
    background: linear-gradient(160deg, #0F172A 0%, #0C4A6E 22%, #0369A1 48%, #2563EB 72%, #C2410C 100%);
}}
.home-header::after {{
    content: '';
    position: absolute;
    top: 6px;
    left: 16px;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(251, 191, 36, 0.55) 0%, rgba(251, 191, 36, 0.12) 45%, transparent 70%);
    pointer-events: none;
    z-index: 0;
    filter: blur(1px);
}}
.home-header::before {{
    background:
        radial-gradient(ellipse at 92% 12%, rgba(251, 191, 36, 0.32), transparent 42%),
        radial-gradient(ellipse at 12% 88%, rgba(56, 189, 248, 0.2), transparent 52%);
}}
.home-header-top {{
    display: flex; align-items: center; gap: 8px; direction: rtl;
    position: relative; z-index: 1; margin-bottom: 4px;
}}
.home-header-title {{
    font-size: 16px; font-weight: bold; color: #fff; letter-spacing: 0.01em;
    text-shadow: 0 1px 12px rgba(56, 189, 248, 0.35);
}}
.home-date-title {{ font-size: var(--text-sm); opacity: 0.95; color: #E0F2FE; }}
.home-header .date-nav-btn,
.fin-header .date-nav-btn {{
    width: 32px; height: 32px;
}}
.home-header .date-nav-btn {{
    background: rgba(56, 189, 248, 0.14);
    border-color: rgba(56, 189, 248, 0.32);
    color: #BAE6FD;
}}
.home-header .date-nav-btn .ico {{ color: #7DD3FC; }}
.home-header .home-today-btn,
.fin-header .fin-today-btn {{
    padding: 4px 10px;
    font-size: 12px;
}}
.home-header .home-today-btn {{
    background: rgba(251, 191, 36, 0.2);
    border-color: rgba(251, 191, 36, 0.42);
    color: #FEF3C7;
    box-shadow: 0 0 18px rgba(251, 191, 36, 0.15);
}}
.home-header-tools {{
    gap: 4px !important;
}}
.home-header .home-tool-btn,
.home-header .icon-btn.home-tool-btn {{
    width: 32px; height: 32px;
}}
.home-header .home-tool-btn.wide {{
    height: 32px; padding: 0 8px; font-size: 12px;
}}
.home-header .home-tool-btn {{
    background: rgba(56, 189, 248, 0.1);
    border: 1px solid rgba(125, 211, 252, 0.28);
    color: #E0F2FE;
}}
.home-header .home-tool-btn.wide {{
    color: #E0F2FE;
}}
.home-header .home-tool-btn .ico {{ color: #7DD3FC; }}
.home-header .home-tool-btn .fin-emoji {{
    flex-shrink: 0;
    color: unset;
    -webkit-text-fill-color: initial;
}}
.home-header .urgent-badge {{
    background: #F97316;
    color: #fff;
    box-shadow: 0 0 10px rgba(249, 115, 22, 0.45);
}}
.home-hero-in-header {{
    margin-top: 6px;
    padding: 10px;
    background: rgba(15, 23, 42, 0.35);
    border: 1px solid rgba(56, 189, 248, 0.24);
    border-radius: 14px;
    position: relative;
    z-index: 1;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
}}
.home-hero-stats {{
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 6px;
    direction: rtl;
}}
.home-hero-stat {{
    display: flex; align-items: center; gap: 6px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(125, 211, 252, 0.16);
    border-radius: 10px;
    padding: 7px 8px;
}}
.home-hero-stat .fin-emoji {{
    flex-shrink: 0;
}}
.home-stat-lbl {{
    display: block; font-size: 9px;
    color: rgba(224, 242, 254, 0.62);
}}
.home-stat-val {{
    display: block; font-size: 13px; font-weight: bold;
    color: #F8FAFC; font-variant-numeric: tabular-nums;
}}
.home-hero-stat.eff .home-stat-val {{ color: #FDE68A; }}
.home-hero-stat.useful .home-stat-val {{ color: #6EE7B7; }}
.home-hero-stat.not .home-stat-val {{ color: #FDBA74; }}
.home-hero-stat.tasks .home-stat-val {{ color: #7DD3FC; }}
.home-header-top .fin-emoji,
.fin-header-top .fin-emoji,
.proj-header-brand .fin-emoji,
.analytics-header-top .fin-emoji {{
    flex-shrink: 0;
}}
.home-header-top .fin-emoji-md,
.fin-header-top .fin-emoji-md,
.analytics-header-top .fin-emoji-md,
.proj-header-brand .fin-emoji-md {{
    font-size: 22px;
    min-width: 26px;
    min-height: 26px;
}}
.home-hero-stat .fin-emoji-sm,
.fin-hero-in-header .fin-hero-stat .fin-emoji-sm,
.fin-hero-invest .fin-emoji-sm {{
    font-size: 18px;
    min-width: 22px;
    min-height: 22px;
}}
.analytics-summary-item .fin-emoji-sm,
.proj-summary-item .fin-emoji-sm {{
    font-size: 22px;
    min-width: 26px;
    min-height: 26px;
}}
.home-search-row {{
    padding: 10px 12px 4px;
}}
.home-search-row .search-wrap {{
    background: var(--surface);
    border: 1px solid rgba(56, 189, 248, 0.18);
    border-radius: 14px;
    box-shadow: 0 4px 16px rgba(14, 116, 144, 0.12);
}}
.home-page .add-btn {{
    background: linear-gradient(135deg, #0284C7, #2563EB);
    border-color: transparent;
    box-shadow: 0 4px 16px rgba(37, 99, 235, 0.28);
}}
.home-page .empty-btn {{
    background: linear-gradient(135deg, #0284C7, #0891B2);
    border-color: transparent;
}}
.home-page .empty-state .fin-icon-lg {{
    display: flex; margin: 0 auto 10px;
}}
.home-page .section {{
    margin-left: 12px; margin-right: 12px;
    border-radius: 16px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}}

[data-theme="light"] .home-header {{
    background: linear-gradient(155deg, #FFF7ED 0%, #FFEDD5 30%, #E0F2FE 62%, #F0F9FF 100%);
}}
[data-theme="light"] .home-header::after {{
    background: radial-gradient(circle, rgba(251, 191, 36, 0.65) 0%, rgba(251, 191, 36, 0.15) 50%, transparent 72%);
}}
[data-theme="light"] .home-header::before {{
    background:
        radial-gradient(ellipse at 90% 10%, rgba(251, 191, 36, 0.35), transparent 40%),
        radial-gradient(ellipse at 10% 90%, rgba(56, 189, 248, 0.22), transparent 50%);
}}
[data-theme="light"] .home-header-title {{
    color: #0C4A6E;
    text-shadow: none;
}}
[data-theme="light"] .home-date-title {{ color: #0369A1; opacity: 1; }}
[data-theme="light"] .home-header .date-nav-btn {{
    background: rgba(3, 105, 161, 0.08);
    border-color: rgba(3, 105, 161, 0.16);
    color: #0369A1;
}}
[data-theme="light"] .home-header .date-nav-btn .ico {{ color: #0284C7; }}
[data-theme="light"] .home-header .home-today-btn {{
    background: #F59E0B; color: #fff; border-color: transparent;
    box-shadow: 0 4px 14px rgba(245, 158, 11, 0.35);
}}
[data-theme="light"] .home-header .home-tool-btn {{
    background: rgba(255, 255, 255, 0.82);
    color: #0369A1; border-color: rgba(3, 105, 161, 0.14);
}}
[data-theme="light"] .home-header .home-tool-btn .ico {{ color: #0284C7; }}
[data-theme="light"] .home-hero-in-header {{
    background: rgba(255, 255, 255, 0.82);
    border-color: rgba(3, 105, 161, 0.14);
    box-shadow: 0 4px 18px rgba(14, 116, 144, 0.1);
}}
[data-theme="light"] .home-hero-stat {{
    background: rgba(255, 255, 255, 0.95);
    border-color: rgba(3, 105, 161, 0.1);
}}
[data-theme="light"] .home-stat-lbl {{ color: var(--text-muted); }}
[data-theme="light"] .home-stat-val {{ color: var(--text); }}
[data-theme="light"] .home-hero-stat.eff .home-stat-val {{ color: #D97706; }}
[data-theme="light"] .home-hero-stat.useful .home-stat-val {{ color: var(--success); }}
[data-theme="light"] .home-hero-stat.not .home-stat-val {{ color: var(--warning); }}
[data-theme="light"] .home-hero-stat.tasks .home-stat-val {{ color: #0284C7; }}
[data-theme="light"] .home-search-row .search-wrap {{
    border-color: rgba(3, 105, 161, 0.12);
    box-shadow: 0 2px 12px rgba(14, 116, 144, 0.08);
}}
[data-theme="light"] .home-page .add-btn,
[data-theme="light"] .home-page .empty-btn {{
    background: linear-gradient(135deg, #0284C7, #0369A1);
    box-shadow: 0 4px 14px rgba(2, 132, 199, 0.25);
}}

/* ── Hero stats (legacy fallback) ── */
.hero-stats {{
    display: flex;
    gap: var(--space-2);
    position: relative;
    z-index: 1;
}}
.hero-stat {{
    flex: 1;
    text-align: center;
    background: rgba(255,255,255,0.12);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: var(--radius-sm);
    padding: 8px 6px;
}}
[data-theme="light"] .hero-stat {{
    background: rgba(255,255,255,0.65);
    border-color: rgba(99,102,241,0.15);
}}
.hero-stat-val {{
    display: block;
    font-size: var(--text-md);
    font-weight: var(--font-bold);
    color: #fff;
    font-variant-numeric: tabular-nums;
}}
[data-theme="light"] .hero-stat-val {{ color: var(--text); }}
.hero-stat-lbl {{
    display: block;
    font-size: 10px;
    color: rgba(255,255,255,0.75);
    margin-top: 2px;
}}
[data-theme="light"] .hero-stat-lbl {{ color: var(--text-muted); }}
.hero-stat.useful .hero-stat-val {{ color: #86EFAC; }}
.hero-stat.eff .hero-stat-val {{ color: #C4B5FD; }}
.hero-stat.not .hero-stat-val {{ color: #FDBA74; }}
[data-theme="light"] .hero-stat.useful .hero-stat-val {{ color: var(--success); }}
[data-theme="light"] .hero-stat.eff .hero-stat-val {{ color: var(--primary); }}
[data-theme="light"] .hero-stat.not .hero-stat-val {{ color: var(--warning); }}

/* ── Summary Bar (legacy fallback) ── */
.summary-bar {{
    background: var(--surface-glass);
    backdrop-filter: blur(var(--glass-blur));
    padding: var(--space-2) var(--space-4);
    display: flex;
    justify-content: space-between;
    font-size: var(--text-sm);
    border-bottom: 1px solid var(--divider);
    margin: 0 var(--space-2);
    border-radius: var(--radius-sm);
}}
.sum-useful {{ color: var(--success); }}
.sum-not {{ color: var(--warning); }}
.sum-eff {{ color: var(--primary); }}

/* ── Task Card ── */
.task-list {{
    padding: 8px 8px 4px;
    width: 100%;
    box-sizing: border-box;
}}

.task-card {{
    background: var(--surface);
    border-radius: var(--radius);
    margin-bottom: var(--space-2);
    overflow: hidden;
    border: 1px solid var(--border-subtle);
    box-shadow: var(--elevation-1);
    transition: box-shadow var(--duration-fast);
    width: 100%;
    box-sizing: border-box;
}}
@media (hover: hover) {{
    .task-card:hover {{ box-shadow: var(--elevation-2); }}
}}
.task-header {{
    display: flex;
    align-items: center;
    padding: 12px 12px;
    cursor: pointer;
    direction: rtl;
    gap: 8px;
    width: 100%;
    box-sizing: border-box;
    min-height: 48px;
    color: var(--text);
    -webkit-user-select: none;
    user-select: none;
}}
.task-star-wrap {{
    flex-shrink: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: none;
    border: none;
    padding: 4px;
    margin: -4px;
    cursor: pointer;
    color: inherit;
}}
.task-star {{ color: var(--star); }}
.task-star.empty {{ color: var(--divider); opacity: 0.55; }}
.task-header-end {{
    display: flex;
    align-items: center;
    gap: 6px;
    flex-shrink: 0;
}}
.ico.task-chevron {{
    color: var(--text-muted);
    flex-shrink: 0;
    opacity: 0.7;
    width: 14px;
    height: 14px;
}}
.task-title-wrap {{
    flex: 1;
    min-width: 0;
    font-size: var(--text-md);
    font-weight: normal;
    line-height: 1.4;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    text-align: start;
    color: var(--text);
}}
.task-dur {{
    color: var(--text-muted);
    font-size: 13px;
    font-variant-numeric: tabular-nums;
    flex-shrink: 0;
    white-space: nowrap;
    text-align: end;
}}
.task-dur.running {{
    color: var(--running);
    animation: pulseGlow 2s ease-in-out infinite;
}}
.task-card.is-running .timer-big {{
    animation: pulseGlow 2s ease-in-out infinite;
}}

/* status strip — inset shadow avoids width jump when status changes */
.task-card.is-useful {{ box-shadow: var(--elevation-1), inset -3px 0 0 0 var(--success); }}
.task-card.is-not-useful {{ box-shadow: var(--elevation-1), inset -3px 0 0 0 var(--error); }}
.task-card.is-running {{ box-shadow: var(--elevation-1), inset -3px 0 0 0 var(--running); }}
@media (hover: hover) {{
    .task-card.is-useful:hover {{ box-shadow: var(--elevation-2), inset -3px 0 0 0 var(--success); }}
    .task-card.is-not-useful:hover {{ box-shadow: var(--elevation-2), inset -3px 0 0 0 var(--error); }}
    .task-card.is-running:hover {{ box-shadow: var(--elevation-2), inset -3px 0 0 0 var(--running); }}
}}

/* ── Task Detail ── */
.task-detail {{
    padding: 12px 14px 14px;
    border-top: 1px solid var(--divider);
    direction: rtl;
    background: var(--surface-deep);
    width: 100%;
    box-sizing: border-box;
    overflow: hidden;
}}
.timer-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
    gap: 8px;
    min-width: 0;
}}
.timer-big {{
    font-size: 28px;
    font-weight: var(--font-bold);
    font-variant-numeric: tabular-nums;
    color: var(--running);
    letter-spacing: 2px;
    flex-shrink: 0;
}}
.btn-start {{
    background: var(--running-bg);
    color: var(--running);
    border: 1px solid var(--running);
    padding: 7px 16px;
    border-radius: 20px;
    cursor: pointer;
    font-family: 'Vazirmatn', sans-serif;
    font-size: 13px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}}
.btn-stop {{
    background: var(--error-bg);
    color: var(--error);
    border: 1px solid var(--error);
    padding: 7px 16px;
    border-radius: 20px;
    cursor: pointer;
    font-family: 'Vazirmatn', sans-serif;
    font-size: 13px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}}
.btn-start .ico, .btn-stop .ico {{ width: 14px; height: 14px; }}
.add-btn .ico, .empty-btn .ico {{ width: 16px; height: 16px; flex-shrink: 0; }}
.add-btn, .empty-btn {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    box-sizing: border-box;
}}
.empty-btn {{ display: inline-flex; }}

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
    max-width: 100%;
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
.chip-useful-on   {{ background: var(--success-bg); color: var(--success); border: none; }}
.chip-useful-off  {{ background: var(--surface); color: var(--text-muted); border: 1px solid var(--divider); }}
.chip-notuseful-on{{ background: var(--error-bg); color: var(--warning); border: none; }}
.chip-neutral     {{ background: var(--surface-muted); color: var(--text-muted); border: 1px solid var(--divider); }}
.chip-edit        {{ background: var(--chip-edit-bg); color: var(--chip-edit); border: none; }}
.chip-delete      {{ background: var(--error-bg); color: var(--error); border: none; }}
.chip:active {{ opacity: 0.85; }}

/* ── Section (Finance / Wellness) ── */
.section {{
    background: var(--surface);
    border-radius: var(--radius);
    margin: 6px var(--space-2);
    padding: var(--space-4);
    border: 1px solid var(--border-subtle);
    direction: rtl;
    box-shadow: var(--elevation-1);
}}
.sec-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}}
.sec-title {{
    font-size: var(--text-base);
    font-weight: var(--font-bold);
    color: var(--text);
    display: flex;
    align-items: center;
    gap: var(--space-2);
}}
.sec-title::before {{
    content: '';
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--gradient-accent);
    flex-shrink: 0;
}}
.sec-actions {{ display: flex; gap: 6px; flex-wrap: wrap; }}
.btn-sm-green {{
    background: var(--success-bg); color: var(--success);
    padding: 4px 10px; border-radius: 14px;
    font-size: 12px; cursor: pointer;
    border: none;
    font-family: 'Vazirmatn', sans-serif;
}}
.btn-sm-red {{
    background: var(--error-bg); color: var(--error);
    padding: 4px 10px; border-radius: 14px;
    font-size: 12px; cursor: pointer;
    border: none;
    font-family: 'Vazirmatn', sans-serif;
}}

/* finance summary */
.fin-summary {{
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    padding-bottom: 8px;
    margin-bottom: 8px;
    border-bottom: 1px solid var(--divider);
    flex-wrap: wrap;
    gap: 4px;
}}
.fin-income {{ color: var(--success); }}
.fin-expense {{ color: var(--warning); }}
.fin-investment {{ color: var(--investment); }}
.fin-balance {{ color: var(--primary); }}

.fin-entry {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 0;
    font-size: 13px;
    direction: rtl;
    border-bottom: 1px solid var(--surface-muted);
    gap: 6px;
}}
.fin-entry:last-child {{ border-bottom: none; }}
.fin-type-income {{ color: var(--success); }}
.fin-type-expense {{ color: var(--warning); }}
.fin-type-investment {{ color: var(--investment); }}
.btn-sm-invest {{
    background: var(--surface-muted);
    color: var(--investment);
    padding: 4px 10px; border-radius: 14px;
    font-size: 12px; cursor: pointer;
    border: 1px solid var(--divider);
    font-family: 'Vazirmatn', sans-serif;
}}
.fin-del {{
    background: none; border: none;
    color: var(--error);
    opacity: 0.55;
    font-size: 18px; line-height: 1;
    cursor: pointer; padding: 4px 6px;
    border-radius: 6px;
    min-width: 32px; min-height: 32px;
}}
.fin-del:active {{ background: var(--surface-muted); }}

/* wellness */
.well-row {{
    display: flex; gap: 8px;
    margin-bottom: 10px;
    direction: rtl;
}}
.well-btn {{
    flex: 1; background: var(--surface-muted);
    border: 1px solid var(--divider);
    border-radius: var(--radius-sm);
    padding: 10px 8px;
    text-align: center;
    cursor: pointer;
    font-family: 'Vazirmatn', sans-serif;
    color: var(--text);
    transition: border-color 0.15s, background 0.15s;
}}
.well-btn:active {{ border-color: var(--primary); }}
.well-lbl {{ font-size: 11px; color: var(--text-muted); display: block; margin-bottom: 3px; }}
.well-val {{ font-size: 14px; font-weight: 500; }}

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
    background: rgba(99, 102, 241, 0.22);
    transform: scale(1.2);
    border: 1px solid rgba(99, 102, 241, 0.35);
    box-shadow: 0 0 12px rgba(99, 102, 241, 0.25);
}}

/* ── Add Task Button ── */
.add-btn {{
    display: flex;
    width: auto;
    margin: var(--space-3) var(--space-2) var(--space-2);
    padding: 14px;
    background: var(--gradient-accent);
    color: #fff;
    border-radius: var(--radius);
    font-size: var(--text-md);
    font-weight: var(--font-medium);
    cursor: pointer;
    font-family: 'Vazirmatn', sans-serif;
    box-shadow: var(--shadow);
    border: none;
    transition: transform var(--duration-fast), box-shadow var(--duration-fast);
}}
.add-btn:active {{ transform: scale(0.98); }}

/* ── Modal — bottom sheet ── */
.modal-overlay {{
    position: fixed; inset: 0;
    background: var(--overlay);
    display: flex;
    align-items: flex-end;
    justify-content: center;
    z-index: 600;
    padding: 0;
    direction: rtl;
    overflow: hidden;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
}}
.modal-overlay.modal-viewport-sync {{
    top: var(--vv-top);
    left: var(--vv-left);
    width: var(--vv-width);
    height: var(--vv-height);
    right: auto;
    bottom: auto;
}}
.modal-overlay.modal-center {{
    align-items: center;
    padding: max(12px, env(safe-area-inset-top)) 12px max(12px, env(safe-area-inset-bottom));
}}
.modal-box {{
    background: var(--surface);
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    padding: 8px 16px 0;
    width: 100%;
    max-width: 520px;
    max-height: min(92dvh, calc(var(--visual-vh, 100dvh) - 16px));
    border: 1px solid var(--border-subtle);
    border-bottom: none;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    margin: 0 auto;
    box-shadow: var(--shadow-nav);
    animation: sheetUp var(--duration-normal) var(--ease-out);
    transition: max-height 0.15s ease-out;
}}
.modal-viewport-sync .modal-box {{
    max-height: calc(100% - 8px);
}}
body.kb-open .modal-overlay:not(.modal-viewport-sync) {{
    padding-bottom: var(--keyboard-inset);
    align-items: flex-end;
}}
body.kb-open .modal-overlay:not(.modal-viewport-sync) .modal-box {{
    max-height: calc(var(--visual-vh) - 16px);
}}
.modal-center .modal-box {{
    border-radius: var(--radius-lg);
    border-bottom: 1px solid var(--border-subtle);
    max-height: calc(100dvh - 24px - env(safe-area-inset-top) - env(safe-area-inset-bottom));
    animation: fadeScaleIn var(--duration-normal) var(--ease-out);
}}
.modal-handle {{
    width: 36px;
    height: 4px;
    background: var(--divider);
    border-radius: 2px;
    margin: 4px auto 12px;
    flex-shrink: 0;
}}
.modal-center .modal-handle {{ display: none; }}
.modal-body {{
    flex: 1 1 auto;
    min-height: 0;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
    touch-action: pan-y;
    overscroll-behavior: contain;
    padding-left: 2px;
    padding-right: 2px;
}}
#modal-fields {{
    overflow: visible;
    min-height: 0;
}}
body.kb-open .modal-body {{
    padding-bottom: 8px;
}}
body.kb-open .modal-overlay.modal-center {{
    align-items: flex-start;
    padding-top: max(8px, env(safe-area-inset-top));
    padding-bottom: max(8px, env(safe-area-inset-bottom));
}}
body.kb-open .modal-center .modal-box {{
    max-height: calc(var(--visual-vh, 100dvh) - 16px);
}}
body.modal-open.kb-open .modal-overlay.modal-viewport-sync {{
    touch-action: pan-y;
}}
body.modal-open.kb-open .modal-overlay.modal-viewport-sync .modal-box {{
    max-height: calc(100% - 8px);
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
    color: var(--text-muted);
    margin-bottom: 5px;
}}
.modal-input {{
    width: 100%;
    background: var(--surface-muted);
    border: 1px solid var(--divider);
    border-radius: var(--radius-sm);
    padding: 10px 12px;
    color: var(--text);
    font-size: 14px;
    font-family: 'Vazirmatn', sans-serif;
    direction: rtl;
    margin-bottom: 12px;
    outline: none;
}}
.modal-input:focus {{ border-color: var(--primary); }}

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

.modal-btns {{
    display: flex;
    gap: 8px;
    direction: rtl;
    flex-shrink: 0;
    position: relative;
    z-index: 2;
    background: var(--surface);
    border-top: 1px solid var(--border-subtle);
    margin: 0 -16px;
    padding: 10px 16px calc(10px + var(--safe-bottom));
}}
.modal-center .modal-btns {{
    margin: 0;
    border-top: 1px solid var(--border-subtle);
    padding-bottom: 0;
}}
.modal-confirm {{
    flex: 1;
    background: var(--gradient-accent);
    color: #fff;
    border: none;
    border-radius: var(--radius-sm);
    padding: 12px;
    min-height: 44px;
    font-size: var(--text-base);
    font-weight: var(--font-medium);
    cursor: pointer;
    font-family: 'Vazirmatn', sans-serif;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3);
}}
.modal-cancel {{
    flex: 1;
    background: var(--surface-muted);
    color: var(--text-muted);
    border: 1px solid var(--divider);
    border-radius: var(--radius-sm);
    padding: 10px;
    min-height: 44px;
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
    font-family: 'Vazirmatn', sans-serif;
    color: var(--text);
    min-width: 56px;
    width: 100%;
    text-align: center;
    padding: 6px 4px;
    background: var(--surface-muted);
    border-radius: 10px;
    border: 1px solid var(--divider);
    outline: none;
    box-sizing: border-box;
}}
.time-picker-val:focus {{
    border-color: var(--primary);
    background: var(--surface);
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
.analytics-page {{ padding-bottom: 12px; }}

.analytics-header {{
    padding: calc(14px + var(--safe-top)) var(--space-4) 16px;
    background: linear-gradient(145deg, #1A1A24 0%, #252530 45%, #1E1E28 100%);
    color: #fff;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: var(--shadow);
    overflow: hidden;
    direction: rtl;
}}
.analytics-header::before {{
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse at 85% 15%, rgba(167, 139, 250, 0.2), transparent 55%);
    pointer-events: none;
}}
@media (hover: none) and (pointer: coarse) {{
    .analytics-header {{ padding-top: calc(14px + max(36px, var(--safe-top))); }}
}}
.analytics-header-top {{
    display: flex; align-items: center; gap: 8px;
    position: relative; z-index: 1; margin-bottom: 12px;
}}
.analytics-header-title {{
    font-size: 16px; font-weight: bold; color: #fff;
}}
.analytics-period-in-header {{
    padding: 0 0 8px; position: relative; z-index: 1;
}}
.analytics-header .period-btn {{
    background: rgba(255, 255, 255, 0.06);
    border-color: rgba(167, 139, 250, 0.2);
    color: rgba(255, 255, 255, 0.7);
}}
.analytics-header .period-btn.active {{
    background: rgba(167, 139, 250, 0.22);
    color: #C4B5FD;
    border-color: rgba(167, 139, 250, 0.45);
}}
.analytics-period-label {{
    text-align: center; font-size: 12px;
    color: rgba(255, 255, 255, 0.55);
    padding: 0 0 10px; position: relative; z-index: 1;
}}
.analytics-hero-in-header {{
    margin: 0;
    padding: 12px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(167, 139, 250, 0.2);
    border-radius: 14px;
    position: relative;
    z-index: 1;
}}
.analytics-summary {{
    display: flex; gap: 8px; direction: rtl;
}}
.analytics-summary-item {{
    flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px;
    text-align: center;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(167, 139, 250, 0.14);
    border-radius: 10px; padding: 10px 6px;
}}
.analytics-summary-item .fin-emoji {{ flex-shrink: 0; }}
.analytics-summary-val {{
    display: block; font-size: 15px; font-weight: bold;
    color: #E9D5FF; font-variant-numeric: tabular-nums; line-height: 1.1;
}}
.analytics-summary-lbl {{
    display: block; font-size: 10px;
    color: rgba(255, 255, 255, 0.55);
}}
.analytics-days-title {{ padding: 8px 12px; }}
.day-extra {{ font-size: 11px; color: var(--text-muted); margin-top: 4px; }}
.analytics-page .sparkline {{ color: #A78BFA; }}
.analytics-page .day-bar-fill {{
    background: linear-gradient(90deg, #818CF8, #A78BFA);
}}
.analytics-page .empty-state .fin-icon-lg {{ display: flex; margin: 0 auto 10px; }}

[data-theme="light"] .analytics-header {{
    background: linear-gradient(145deg, #F3F0FF 0%, #EDE9FE 50%, #F5F3FF 100%);
    box-shadow: 0 2px 16px rgba(99, 102, 241, 0.08);
}}
[data-theme="light"] .analytics-header-title {{ color: #4C1D95; }}
[data-theme="light"] .analytics-header .period-btn {{
    background: rgba(255, 255, 255, 0.75);
    border-color: rgba(124, 58, 237, 0.15);
    color: #6B7280;
}}
[data-theme="light"] .analytics-header .period-btn.active {{
    background: rgba(124, 58, 237, 0.12);
    color: #6D28D9;
    border-color: rgba(124, 58, 237, 0.3);
}}
[data-theme="light"] .analytics-period-label {{ color: var(--text-muted); }}
[data-theme="light"] .analytics-hero-in-header {{
    background: rgba(255, 255, 255, 0.72);
    border-color: rgba(124, 58, 237, 0.12);
}}
[data-theme="light"] .analytics-summary-item {{
    background: rgba(255, 255, 255, 0.85);
    border-color: rgba(124, 58, 237, 0.1);
}}
[data-theme="light"] .analytics-summary-val {{ color: #5B21B6; }}
[data-theme="light"] .analytics-summary-lbl {{ color: var(--text-muted); }}

.analytics-period {{
    display: flex; gap: 6px;
    padding: 10px 8px 6px;
    direction: rtl;
}}
.period-btn {{
    flex: 1;
    padding: 8px;
    border-radius: var(--radius-sm);
    text-align: center;
    background: var(--surface-muted);
    color: var(--text-muted);
    border: 1px solid var(--divider);
    cursor: pointer;
    font-family: 'Vazirmatn', sans-serif;
    font-size: 13px;
}}
.period-btn.active {{
    background: rgba(94,92,230,0.2);
    color: var(--primary);
    border-color: rgba(94,92,230,0.33);
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
    background: var(--surface);
    border-radius: 12px;
    padding: 12px;
    border: 1px solid var(--divider);
    text-align: center;
}}
.stat-key {{ font-size: 11px; color: var(--text-muted); margin-bottom: 4px; }}
.stat-val {{ font-size: 16px; font-weight: bold; color: var(--text); }}

.day-card {{
    background: var(--surface);
    border-radius: 12px;
    margin: 4px 8px;
    padding: 10px 12px;
    border: 1px solid var(--divider);
    direction: rtl;
}}
.day-date {{ font-size: 13px; color: var(--text-muted); margin-bottom: 6px; }}
.day-bar {{
    height: 6px;
    border-radius: 3px;
    background: var(--surface-muted);
    overflow: hidden;
    margin-bottom: 6px;
}}
.day-bar-fill {{
    height: 100%;
    border-radius: 3px;
    background: linear-gradient(90deg, var(--primary), var(--success));
}}
.day-stats {{
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: var(--text-muted);
}}

/* ── SPA extras ── */
.loading-state {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 50vh;
    padding: 48px 24px;
    color: var(--text-muted);
    gap: 12px;
}}
.loading-spinner {{
    width: 32px;
    height: 32px;
    border: 3px solid var(--surface-muted);
    border-top-color: var(--primary);
    border-radius: 50%;
    animation: spin 0.75s linear infinite;
}}
.loading-text {{ font-size: 14px; }}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}
.search-row {{ padding: var(--space-2) var(--space-2) var(--space-1); }}
.search-wrap {{
    position: relative;
    display: flex;
    align-items: center;
}}
.search-wrap .ico-search {{
    position: absolute;
    inset-inline-start: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-muted);
    pointer-events: none;
    width: 18px;
    height: 18px;
}}
.search-input {{
    width: 100%;
    background: var(--surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    padding: 11px 12px;
    padding-inline-start: 40px;
    color: var(--text);
    font-family: 'Vazirmatn', sans-serif;
    font-size: var(--text-base);
    outline: none;
    transition: border-color var(--duration-fast), box-shadow var(--duration-fast);
}}
.search-input:focus {{
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}}
.header-actions {{ display: flex; gap: 4px; align-items: center; position: relative; z-index: 1; }}
.icon-btn {{
    background: rgba(255,255,255,0.14);
    backdrop-filter: blur(8px);
    color: #fff;
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: var(--radius-sm);
    width: 36px; height: 36px;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer;
    flex-shrink: 0;
    transition: background var(--duration-fast), transform var(--duration-fast);
}}
[data-theme="light"] .icon-btn {{
    background: rgba(99,102,241,0.1);
    color: var(--primary);
    border-color: rgba(99,102,241,0.18);
}}
.icon-btn.wide {{ width: auto; padding: 0 10px; gap: 4px; font-size: var(--text-sm); }}
.icon-btn:active {{ transform: scale(0.92); }}
.icon-btn .ico {{ width: 18px; height: 18px; }}
.icon-btn.wide .ico {{ width: 14px; height: 14px; }}
.task-progress {{
    height: 4px;
    background: var(--surface-muted);
    margin: 0 12px 4px;
    border-radius: 2px;
    overflow: hidden;
}}
.task-progress-fill {{
    height: 100%;
    background: var(--gradient-progress);
    border-radius: 2px;
    transition: width 0.3s var(--ease-out);
}}
.task-card.is-running .task-progress-fill {{
    background: linear-gradient(90deg, var(--running), var(--primary), var(--running));
    background-size: 200% 100%;
    animation: shimmer 1.8s linear infinite;
}}
.task-remaining {{ font-size: 11px; color: var(--text-muted); padding: 0 12px 8px; }}
.empty-state {{
    text-align: center;
    padding: var(--space-8) var(--space-5);
    color: var(--text-muted);
}}
.empty-icon {{
    margin: 0 auto var(--space-3);
    width: 72px;
    height: 72px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--surface-muted);
    border-radius: 50%;
    color: var(--primary);
}}
.empty-title {{ font-size: var(--text-md); font-weight: var(--font-bold); color: var(--text); margin-bottom: 6px; }}
.empty-sub {{ font-size: var(--text-sm); color: var(--text-muted); line-height: 1.6; max-width: 280px; margin: 0 auto 4px; }}
.empty-btn, .empty-mini {{ margin-top: var(--space-4); }}
.empty-mini {{ text-align: center; font-size: var(--text-sm); color: var(--text-muted); padding: var(--space-3) var(--space-2); }}
.empty-btn {{
    background: var(--gradient-accent);
    color: #fff; border: none; border-radius: var(--radius-sm);
    padding: 11px 22px; cursor: pointer; font-family: 'Vazirmatn', sans-serif;
    font-size: var(--text-sm); font-weight: var(--font-medium); box-shadow: var(--shadow);
}}
.note-section {{ margin-top: 0; }}
.note-input {{
    width: 100%; min-height: 72px; background: var(--surface-muted);
    border: 1px solid var(--divider); border-radius: var(--radius-sm);
    padding: 10px; color: var(--text); font-family: 'Vazirmatn', sans-serif;
    font-size: 14px; resize: vertical; outline: none; margin-top: 8px;
    line-height: 1.6;
}}
.note-input:focus {{ border-color: var(--primary); }}
.note-saved {{
    font-size: 11px; color: var(--success); margin-top: 6px; opacity: 0;
    transition: opacity 0.3s;
}}
.note-saved.show {{ opacity: 1; }}
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
.cal-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-2);
    direction: rtl;
    margin-bottom: 8px;
}}
.cal-title {{
    flex: 1;
    min-width: 0;
    text-align: center;
    font-weight: var(--font-bold);
    font-size: var(--text-sm);
}}
.cal-nav {{
    background: var(--surface-muted);
    border: 1px solid var(--divider);
    color: var(--text);
    width: 36px;
    height: 36px;
    padding: 0;
    border-radius: var(--radius-sm);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    font-family: inherit;
}}
.cal-nav .ico {{ width: 18px; height: 18px; }}
.cal-nav:active {{ background: rgba(99, 102, 241, 0.15); }}
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
.sparkline {{ width: 100%; height: 60px; display: block; color: var(--primary); }}
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
    font-size: var(--text-lg);
    font-weight: var(--font-bold);
}}
.page-header {{
    padding: calc(12px + var(--safe-top)) var(--space-4) 10px;
    background: var(--surface); color: var(--text); border-bottom: 1px solid var(--divider);
    display: flex; align-items: center; gap: 10px; direction: rtl;
    position: sticky; top: 0; z-index: 90;
}}
.page-header .fin-icon {{ width: 32px; height: 32px; font-size: 16px; border-radius: 10px; }}
.back-btn {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    margin: 12px 8px;
    padding: 12px;
    text-align: center;
    background: var(--surface);
    border: 1px solid var(--divider);
    border-radius: var(--radius-sm);
    cursor: pointer;
    color: var(--text);
    font-family: 'Vazirmatn', sans-serif;
    font-size: var(--text-base);
}}
.back-btn .ico {{ width: 16px; height: 16px; color: var(--primary); }}
.collapse-chevron {{ display: inline-flex; align-items: center; justify-content: center; width: 16px; height: 16px; }}
.fin-card-chevron {{ display: inline-flex; align-items: center; line-height: 0; }}
.proj-done-chevron {{ display: inline-flex; align-items: center; margin-right: auto; }}
.setting-row {{ display: flex; justify-content: space-between; align-items: center; padding: 4px 0; }}
.toggle-btn {{
    background: var(--surface-muted); border: 1px solid var(--divider);
    border-radius: 20px; padding: 6px 14px; cursor: pointer;
    font-family: 'Vazirmatn', sans-serif; color: var(--text-muted);
}}
.toggle-btn.on {{ background: var(--primary); color: #fff; border-color: var(--primary); }}
.recur-row {{ display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid var(--divider); }}
.recur-row:last-child {{ border-bottom: none; }}
.modal-error {{ color: var(--error); font-size: 12px; margin-bottom: 8px; text-align: center; flex-shrink: 0; min-height: 0; }}
.modal-textarea {{ min-height: 80px; resize: vertical; }}
.sms-parse-hint {{ font-size: 11px; margin-top: 6px; min-height: 16px; }}
.sms-parse-hint.ok {{ color: var(--success); }}
.sms-parse-hint.err {{ color: var(--error); }}
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
    background: var(--gradient-accent);
    color: #fff;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3);
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
.backup-summary {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 10px;
}}
.backup-summary-chip {{
    font-size: 11px;
    color: var(--text-muted);
    background: var(--surface-muted);
    border: 1px solid var(--divider);
    border-radius: 20px;
    padding: 4px 10px;
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
.backup-copy-btn {{
    display: block;
    width: 100%;
    margin-top: 8px;
    padding: 11px 16px;
    background: var(--surface-muted);
    color: var(--text);
    border: 1px solid var(--divider);
    border-radius: var(--radius-sm);
    font-size: 13px;
    font-family: 'Vazirmatn', sans-serif;
    cursor: pointer;
    text-align: center;
}}
.backup-copy-btn:active {{
    background: var(--primary);
    color: #fff;
    border-color: var(--primary);
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
    scroll-margin-bottom: calc(var(--keyboard-inset) + 32px);
}}
.backup-ta:focus {{ border-color: var(--primary); }}
.backup-ta::placeholder {{ color: var(--text-muted); opacity: 0.7; }}
.backup-preview {{ font-size: 10px; max-height: 200px; }}
.toast {{
    position: fixed;
    top: calc(12px + var(--safe-top));
    left: 50%;
    transform: translateX(-50%) translateY(-8px);
    background: var(--surface-glass);
    backdrop-filter: blur(var(--glass-blur));
    -webkit-backdrop-filter: blur(var(--glass-blur));
    color: var(--text);
    padding: 12px 24px;
    border-radius: var(--radius-full);
    border: 1px solid var(--border-subtle);
    z-index: 700;
    opacity: 0;
    pointer-events: none;
    transition: opacity var(--duration-normal), transform var(--duration-normal);
    font-size: var(--text-sm);
    font-weight: var(--font-medium);
    box-shadow: var(--elevation-2);
    max-width: calc(100vw - 32px);
    text-align: center;
    white-space: pre-wrap;
}}
.toast.show {{ opacity: 1; transform: translateX(-50%) translateY(0); }}
.toast.error {{ border-color: rgba(251, 113, 133, 0.4); color: var(--error); background: var(--error-bg); }}
.toast.success {{ border-color: rgba(52, 211, 153, 0.4); color: var(--success); background: var(--success-bg); }}
.nav-icon, .ico {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    line-height: 0;
}}
.nav-icon {{
    width: 22px;
    height: 22px;
    margin: 0 auto 3px;
}}
.nav-icon svg, .ico svg {{
    width: 100%;
    height: 100%;
    stroke: currentColor;
    fill: none;
    stroke-width: 1.75;
    stroke-linecap: round;
    stroke-linejoin: round;
}}
.ico-fill svg {{ fill: currentColor; stroke: none; }}
.task-star svg {{ width: 18px; height: 18px; }}
.well-static {{ cursor: default; }}

/* ── Finance screen ── */
.fin-page {{ padding-bottom: 8px; }}

.fin-header {{
    background: linear-gradient(145deg, #0F2E28 0%, #1A4034 45%, #162016 100%);
}}
.fin-header::before {{
    background: radial-gradient(ellipse at 85% 15%, rgba(77, 217, 128, 0.18), transparent 55%);
}}
.fin-header-top {{
    display: flex; align-items: center; gap: 8px; direction: rtl;
    position: relative; z-index: 1; margin-bottom: 2px;
}}
.fin-header-title {{
    font-size: 16px; font-weight: bold; color: #fff; letter-spacing: 0.01em;
}}
.fin-month-title {{ font-size: var(--text-sm); opacity: 0.92; }}
.fin-header .date-nav-btn {{
    background: rgba(77, 217, 128, 0.14);
    border-color: rgba(77, 217, 128, 0.28);
    color: #4DD980;
}}
.fin-header .date-nav-btn .ico {{ color: #4DD980; }}
.fin-header .fin-today-btn {{
    background: rgba(77, 217, 128, 0.18);
    border-color: rgba(77, 217, 128, 0.35);
    color: #4DD980;
}}
[data-theme="light"] .fin-header {{
    background: linear-gradient(145deg, #E8F5EE 0%, #F0FAF4 50%, #EAF6F0 100%);
}}
[data-theme="light"] .fin-header-title {{ color: #0F2E28; }}
[data-theme="light"] .fin-month-title {{ color: #1A4034; opacity: 1; }}
[data-theme="light"] .fin-header .date-nav-btn {{
    background: rgba(15, 46, 40, 0.08);
    border-color: rgba(15, 46, 40, 0.12);
    color: #0F2E28;
}}
[data-theme="light"] .fin-header .date-nav-btn .ico {{ color: #0F2E28; }}
[data-theme="light"] .fin-header .fin-today-btn {{
    background: #0F2E28; color: #fff; border-color: transparent;
}}

.fin-hero {{
    margin: 12px 12px 0;
    padding: 20px 18px 16px;
    background: linear-gradient(145deg, #1E1E3A 0%, #1C1C1E 60%, #162016 100%);
    border-radius: 18px;
    border: 1px solid #3C3C5E44;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    text-align: center;
}}
.fin-hero-in-header {{
    margin: 6px 0 0;
    padding: 10px 12px;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(77, 217, 128, 0.18);
    border-radius: 14px;
    box-shadow: none;
    position: relative;
    z-index: 1;
}}
[data-theme="light"] .fin-hero-in-header {{
    background: rgba(255, 255, 255, 0.72);
    border-color: rgba(15, 46, 40, 0.12);
}}
.fin-hero-label {{ font-size: 11px; color: var(--text-muted); margin-bottom: 2px; }}
.fin-hero-in-header .fin-hero-label {{ color: rgba(255,255,255,0.65); }}
[data-theme="light"] .fin-hero-in-header .fin-hero-label {{ color: var(--text-muted); }}
.fin-hero-balance {{
    font-size: 28px; font-weight: bold; letter-spacing: -0.5px;
    font-variant-numeric: tabular-nums; line-height: 1.2;
}}
.fin-hero-in-header .fin-hero-balance {{
    font-size: 24px; line-height: 1.15;
}}
.fin-hero-balance.positive {{ color: #4DD980; }}
.fin-hero-balance.negative {{ color: #FF7359; }}
.fin-hero-unit {{ font-size: 11px; font-weight: normal; color: var(--text-muted); margin-right: 4px; }}
.fin-hero-stats {{
    display: flex; gap: 10px; margin-top: 16px; direction: rtl;
}}
.fin-hero-in-header .fin-hero-stats {{
    margin-top: 8px; gap: 6px;
}}
.fin-hero-stat {{
    flex: 1; display: flex; align-items: center; gap: 8px;
    background: rgba(255,255,255,0.04); border-radius: 12px;
    padding: 10px 12px; border: 1px solid #ffffff0a;
}}
.fin-hero-in-header .fin-hero-stat {{
    padding: 7px 8px; border-radius: 10px; gap: 6px;
}}
.fin-stat-icon {{
    width: 28px; height: 28px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; font-weight: bold; flex-shrink: 0;
}}
.fin-hero-stat .fin-icon {{
    width: 28px; height: 28px; border-radius: 50%; font-size: 14px; font-weight: bold;
}}
.fin-hero-in-header .fin-hero-stat .fin-icon {{
    width: 24px; height: 24px; font-size: 12px;
}}
.fin-hero-in-header .fin-hero-stat .fin-emoji,
.home-hero-stat .fin-emoji,
.fin-hero-invest .fin-emoji {{
    flex-shrink: 0;
    color: unset;
    -webkit-text-fill-color: initial;
}}
.fin-hero-stat.income .fin-stat-icon {{ background: #1A4028; color: #4DD980; }}
.fin-hero-stat.expense .fin-stat-icon {{ background: #3D1818; color: #FF7359; }}
.fin-stat-lbl {{ display: block; font-size: 10px; color: var(--text-muted); }}
.fin-hero-in-header .fin-stat-lbl {{ color: rgba(255,255,255,0.6); }}
.fin-hero-in-header .fin-stat-val {{ color: #fff; font-size: 12px; }}
[data-theme="light"] .fin-hero-in-header .fin-stat-lbl {{ color: var(--text-muted); }}
[data-theme="light"] .fin-hero-in-header .fin-stat-val {{ color: var(--text); }}
.fin-stat-val {{ display: block; font-size: 13px; font-weight: bold; font-variant-numeric: tabular-nums; }}

.fin-actions {{
    display: flex; flex-wrap: wrap; gap: 8px; padding: 12px 12px 4px; direction: rtl;
}}
.fin-action-btn {{
    flex: 1 1 calc(33.333% - 6px); display: flex; align-items: center; justify-content: center; gap: 6px;
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
.fin-action-btn.inst {{ background: #1A3028; color: #5ECFAB; border: 1px solid #5ECFAB33; }}
.fin-inst-card {{ margin: 8px 12px 0; }}
.fin-hero-invest {{
    margin-top: 8px; padding: 6px 10px; border-radius: 10px;
    background: rgba(255,176,32,0.1); border: 1px solid rgba(255,176,32,0.2);
    font-size: 12px; color: #FFB020; display: flex; align-items: center; gap: 6px; justify-content: center;
}}
.fin-hero-invest .fin-icon {{ width: 24px; height: 24px; font-size: 12px; border-radius: 50%; }}
.fin-hero-invest-note {{ font-size: 10px; color: var(--text-muted); }}

.fin-icon {{
    width: 28px; height: 28px; border-radius: 8px;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 14px; flex-shrink: 0; line-height: 1;
}}
.fin-emoji {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    font-family: "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif;
    font-style: normal;
    line-height: 1;
    background: none !important;
    border: none !important;
    box-shadow: none !important;
    color: unset;
    -webkit-text-fill-color: initial;
    opacity: 1;
    filter: none;
}}
.fin-emoji-xs {{ font-size: 17px; min-width: 20px; min-height: 20px; }}
.fin-emoji-sm {{ font-size: 18px; min-width: 22px; min-height: 22px; }}
.fin-emoji-md {{ font-size: 22px; min-width: 26px; min-height: 26px; }}
.fin-emoji-lg {{ font-size: 32px; min-width: 40px; min-height: 40px; }}
.home-header .fin-emoji,
.fin-header .fin-emoji,
.proj-header .fin-emoji,
.analytics-header .fin-emoji {{
    color: unset;
    -webkit-text-fill-color: initial;
}}
.fin-icon-lg {{
    width: 44px; height: 44px; font-size: 22px; border-radius: 12px;
    margin: 0 auto 10px;
}}
.fin-icon-income {{ background: #1A4028; color: #4DD980; }}
.fin-icon-finance {{ background: #1A4028; color: #4DD980; }}
.fin-icon-home {{ background: #0C4A6E; color: #FBBF24; }}
.fin-icon-projects {{ background: #2A2850; color: #818CF8; }}
.fin-icon-analytics {{ background: #2A2540; color: #A78BFA; }}
.fin-icon-expense {{ background: #3D1818; color: #FF7359; }}
.fin-icon-investment {{ background: #3D3018; color: #FFB020; }}
.fin-icon-chart {{ background: #1A1A40; color: #7B8CDE; }}
.fin-icon-budget {{ background: #1A1A40; color: #7B8CDE; }}
.fin-icon-receipt {{ background: #1E2838; color: #8BA4E8; }}
.fin-icon-daily {{ background: #1A2830; color: #5ECFAB; }}
.fin-icon-inst {{ background: #1A3028; color: #5ECFAB; }}
.fin-icon-neutral {{ background: #1E1E28; color: #A0A0B8; }}
.fin-icon-svg .ico {{ width: 18px; height: 18px; }}
.proj-header-brand .fin-icon,
.analytics-header-top .fin-icon {{ width: 34px; height: 34px; border-radius: 10px; }}
.proj-header-brand .fin-icon-svg .ico,
.analytics-header-top .fin-icon-svg .ico {{ width: 20px; height: 20px; }}

.fin-card {{
    background: var(--surface); border-radius: 16px;
    margin: 10px 12px; padding: 14px 14px 12px;
    border: 1px solid var(--divider);
}}
.fin-card-head {{
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 12px; direction: rtl;
}}
.fin-card-collapsible:not(.open) .fin-card-head {{ margin-bottom: 0; }}
.fin-card-toggle {{
    width: 100%; background: none; border: none; cursor: pointer;
    padding: 0; font-family: 'Vazirmatn', sans-serif; color: inherit;
    text-align: inherit;
}}
.fin-card-toggle:active {{ opacity: 0.75; }}
.fin-card-head-end {{ display: flex; align-items: center; gap: 8px; }}
.fin-card-chevron {{ color: var(--text-muted); }}
.fin-card-title {{
    display: flex; align-items: center; gap: 8px;
    font-size: 14px; font-weight: bold;
}}
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
.fin-empty .fin-icon-lg {{ display: flex; }}
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
.fin-txn-cat {{ display: inline-flex; align-items: center; gap: 4px; opacity: 0.95; }}
.fin-txn-cat .fin-icon {{ width: 20px; height: 20px; font-size: 11px; border-radius: 6px; }}
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
.fin-budget-icon {{ flex-shrink: 0; line-height: 0; }}
.fin-budget-icon .fin-icon {{ width: 32px; height: 32px; font-size: 16px; border-radius: 10px; }}
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
    background: linear-gradient(155deg, #1E1B4B 0%, #312E81 38%, #4338CA 72%, #3730A3 100%);
    padding: calc(16px + var(--safe-top)) var(--space-4) 18px;
    box-shadow: var(--shadow);
    position: sticky;
    top: 0;
    z-index: 100;
    overflow: hidden;
    direction: rtl;
}}
.proj-header::before {{
    content: '';
    position: absolute;
    inset: 0;
    background:
        radial-gradient(ellipse at 15% 0%, rgba(129, 140, 248, 0.28), transparent 52%),
        radial-gradient(ellipse at 90% 20%, rgba(196, 181, 253, 0.18), transparent 48%);
    pointer-events: none;
}}
@media (hover: none) and (pointer: coarse) {{
    .proj-header {{ padding-top: calc(16px + max(36px, var(--safe-top))); }}
}}
.proj-header-top {{
    display: flex; align-items: center; justify-content: space-between; gap: 10px;
    margin-bottom: 0; position: relative; z-index: 1;
}}
.proj-header-brand {{
    display: flex; align-items: center; gap: 8px; min-width: 0;
}}
.proj-header-title {{ font-size: 16px; font-weight: bold; color: #fff; }}
.proj-header-add {{
    background: rgba(255, 255, 255, 0.14); color: #F8FAFC;
    border: 1px solid rgba(255, 255, 255, 0.28);
    padding: 8px 14px; border-radius: 20px; font-size: 12px; font-weight: bold;
    cursor: pointer; font-family: 'Vazirmatn', sans-serif; white-space: nowrap;
    backdrop-filter: blur(6px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}}
.proj-header-add:active {{ background: rgba(255, 255, 255, 0.24); }}
.proj-hero-in-header {{
    margin-top: 12px; padding: 14px;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(196, 181, 253, 0.24);
    border-radius: 16px;
    position: relative; z-index: 1;
    backdrop-filter: blur(8px);
}}
.proj-summary {{
    display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; direction: rtl;
}}
.proj-summary-item {{
    display: flex; flex-direction: column; align-items: center; gap: 6px;
    text-align: center; background: rgba(255,255,255,0.07);
    border: 1px solid rgba(196, 181, 253, 0.2); border-radius: 12px; padding: 12px 6px;
}}
.proj-summary-item .fin-emoji {{
    flex-shrink: 0;
}}
.proj-summary-val {{ display: block; font-size: 17px; font-weight: bold; color: #F8FAFC; font-variant-numeric: tabular-nums; line-height: 1.1; }}
.proj-summary-lbl {{ display: block; font-size: 10px; color: rgba(255,255,255,0.62); }}
.proj-page .fin-empty {{
    margin: 12px; background: var(--surface); border: 1px solid var(--divider);
    border-radius: 16px; box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}}
.proj-page .fin-empty .fin-icon-lg {{ display: flex; }}

.proj-section {{ padding: 10px 12px 0; }}
.proj-card-section {{
    background: var(--surface);
    border: 1px solid var(--divider);
    border-radius: 16px;
    margin: 10px 12px 0;
    padding: 14px 12px 12px;
    box-shadow: 0 2px 14px rgba(0, 0, 0, 0.12);
}}
.proj-section-head {{
    display: flex; align-items: center; justify-content: space-between; gap: 8px;
    margin-bottom: 12px;
}}
.proj-section-head .fin-card-title {{ flex: 1; min-width: 0; }}
.proj-section-title {{ font-size: 14px; font-weight: bold; }}
.proj-section-badge {{
    background: rgba(129, 140, 248, 0.16); color: #A5B4FC;
    font-size: 11px; padding: 3px 9px; border-radius: 10px; font-weight: bold;
}}
.proj-empty-mini {{
    text-align: center; color: var(--text-muted); font-size: 13px;
    padding: 24px 12px; background: var(--surface-muted); border-radius: 12px;
}}

.proj-card {{
    position: relative; background: linear-gradient(135deg, var(--surface) 0%, rgba(255,255,255,0.02) 100%);
    border-radius: 18px;
    border: 1px solid rgba(129, 140, 248, 0.14); margin-bottom: 10px; overflow: hidden;
    display: flex; align-items: stretch;
    box-shadow: 0 4px 18px rgba(0,0,0,0.18);
    transition: transform 0.15s, box-shadow 0.15s;
}}
.proj-card:active {{ transform: scale(0.985); box-shadow: 0 2px 10px rgba(0,0,0,0.14); }}
.proj-card.muted {{ opacity: 0.72; }}
.proj-card-accent {{
    width: 6px; flex-shrink: 0; background: var(--project-color, var(--primary));
    box-shadow: 0 0 14px color-mix(in srgb, var(--project-color, var(--primary)) 55%, transparent);
}}
.proj-card-body {{ flex: 1; padding: 15px 12px 15px 14px; cursor: pointer; min-width: 0; }}
.proj-card-top {{ display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }}
.proj-card-info {{ flex: 1; min-width: 0; }}
.proj-card-title {{
    font-size: 16px; font-weight: bold; margin-bottom: 6px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}
.proj-card-meta {{ font-size: 11px; color: var(--text-muted); margin-top: 4px; }}
.proj-card-menu {{
    align-self: stretch; width: 42px; flex-shrink: 0;
    background: rgba(129, 140, 248, 0.06); border: none; border-right: 1px solid var(--divider);
    color: var(--text-muted); font-size: 18px; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
}}
.proj-card-menu:active {{ background: rgba(129, 140, 248, 0.16); }}
.proj-bar {{
    height: 6px; border-radius: 4px; background: var(--surface-muted); overflow: hidden;
}}
.proj-bar-lg {{ height: 8px; border-radius: 4px; margin-top: 4px; }}
.proj-bar-fill {{
    height: 100%; border-radius: inherit;
    background: linear-gradient(90deg, var(--project-color, var(--primary)), color-mix(in srgb, var(--project-color, var(--primary)) 70%, #fff));
    transition: width 0.35s ease;
}}
.proj-ring {{ flex-shrink: 0; color: var(--text); }}

.proj-done-toggle {{
    width: 100%; display: flex; align-items: center; gap: 8px;
    background: rgba(129, 140, 248, 0.08); border: 1px solid rgba(129, 140, 248, 0.2);
    border-radius: 14px;
    padding: 12px 14px; cursor: pointer; font-family: 'Vazirmatn', sans-serif;
    font-size: 13px; color: var(--text-muted); margin-bottom: 0;
    direction: rtl; text-align: right;
}}
.proj-done-toggle .fin-icon {{
    width: 28px; height: 28px; font-size: 12px; border-radius: 8px; flex-shrink: 0;
}}
.proj-done-toggle.open {{
    border-color: rgba(129, 140, 248, 0.45); color: var(--text);
    background: rgba(129, 140, 248, 0.12);
}}
.proj-section-done {{ padding-top: 8px; }}

.proj-deadline-badge {{
    display: inline-block; font-size: 10px; padding: 3px 8px; border-radius: 10px;
    background: rgba(255,255,255,0.06); color: var(--text-muted);
    border: 1px solid var(--divider); margin-top: 2px;
}}
.proj-deadline-badge.overdue {{ background: var(--error-bg); color: var(--error); border-color: #FF595944; }}
.proj-deadline-badge.today {{ background: rgba(255,179,64,0.12); color: #FFB340; border-color: #FFB34044; }}

/* detail page */
.proj-detail-page {{ padding-bottom: 16px; --project-color: var(--primary); }}
.proj-detail-hero {{
    position: relative; padding: calc(12px + var(--safe-top)) 16px 18px;
    background: var(--surface); overflow: hidden;
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
    background: rgba(255,255,255,0.12);
    color: #fff;
    border: none;
    width: 38px; height: 38px;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
}}
.proj-back-btn .ico {{ width: 20px; height: 20px; }}
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
    overflow: hidden;
    touch-action: auto;
}}
body.kb-open .proj-sheet-overlay {{
    padding-bottom: calc(var(--safe-bottom) + var(--keyboard-inset));
}}
.proj-sheet {{
    width: 100%; max-width: 480px; background: var(--surface);
    border-radius: 20px 20px 0 0; padding: 8px 16px calc(16px + var(--safe-bottom));
    border-top: 1px solid var(--divider);
    animation: projSheetUp 0.25s ease;
    max-height: min(85dvh, calc(var(--visual-vh, 100dvh) - 16px));
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
    touch-action: pan-y;
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
    padding: 14px; margin-bottom: 8px; min-height: 44px; font-size: 14px;
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


/* ── Installments ── */
.inst-row {{
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 0;
    border-bottom: 1px solid var(--divider);
}}
.inst-title  {{ flex: 1; font-size: 14px; }}
.inst-amount {{ color: var(--text-muted); font-size: 13px; white-space: nowrap; }}
.inst-footer {{ padding: 8px 0 0; font-size: 13px; color: var(--error); text-align: left; }}

.inst-bar {{
    height: 6px;
    background: var(--surface-muted);
    border-radius: 3px;
    margin: 8px 0 4px;
    overflow: hidden;
}}
.inst-bar-fill {{
    height: 100%;
    background: var(--primary);
    border-radius: 3px;
    transition: width 0.3s;
}}
.inst-stats {{
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: var(--text-muted);
}}
.inst-settled    {{ color: var(--success); font-size: 12px; }}
.inst-paid-month {{ color: var(--success); font-size: 12px; }}
.inst-due        {{ color: var(--text-muted); font-size: 12px; }}
.inst-overdue    {{ color: var(--error); font-size: 12px; }}
.inst-month-row  {{
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    padding: 4px 0;
}}

/* ── Important dates ── */
.dates-btn {{ position: relative; }}
.urgent-badge {{
    position: absolute;
    top: -4px; right: -4px;
    background: var(--error);
    color: #fff;
    font-size: 10px;
    min-width: 16px; height: 16px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    padding: 0 3px;
}}

.dates-group-label {{
    font-size: 11px; font-weight: 600;
    padding: 12px 16px 4px;
    text-transform: uppercase; letter-spacing: 0.5px;
}}
.urgent-label {{ color: var(--error); }}
.soon-label   {{ color: var(--warning); }}
.ok-label     {{ color: var(--text-muted); }}

.date-item {{
    background: var(--surface);
    border-radius: var(--radius-sm);
    padding: 12px 14px;
    margin: 6px 12px;
}}
.date-item-top {{
    display: flex; align-items: center; gap: 8px;
    margin-bottom: 4px;
}}
.date-dot {{
    width: 8px; height: 8px;
    border-radius: 50%; flex-shrink: 0;
}}
.date-dot.overdue, .date-dot.urgent {{ background: var(--error); }}
.date-dot.soon                      {{ background: var(--warning); }}
.date-dot.ok                        {{ background: var(--success); }}

.date-item-title    {{ flex: 1; font-size: 15px; font-weight: 500; }}
.date-item-countdown {{
    font-size: 12px; white-space: nowrap;
}}
.date-item-countdown.overdue,
.date-item-countdown.urgent {{ color: var(--error); }}
.date-item-countdown.soon   {{ color: var(--warning); }}
.date-item-countdown.ok     {{ color: var(--success); }}

.date-item-meta {{
    font-size: 12px; color: var(--text-muted);
    margin-bottom: 8px;
}}
.date-item-actions {{ display: flex; gap: 6px; flex-wrap: wrap; }}

/* ── Animations ── */
@keyframes screenIn {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes sheetUp {{
    from {{ transform: translateY(100%); }}
    to {{ transform: translateY(0); }}
}}
@keyframes fadeScaleIn {{
    from {{ opacity: 0; transform: scale(0.96); }}
    to {{ opacity: 1; transform: scale(1); }}
}}
@keyframes pulseGlow {{
    0%, 100% {{ opacity: 1; text-shadow: 0 0 0 transparent; }}
    50% {{ opacity: 0.85; text-shadow: 0 0 12px var(--running-glow); }}
}}
@keyframes shimmer {{
    0% {{ background-position: 200% 0; }}
    100% {{ background-position: -200% 0; }}
}}

@media (prefers-reduced-motion: reduce) {{
    *, *::before, *::after {{
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }}
    .screen-enter {{ animation: none; }}
    .task-card.is-running .task-progress-fill {{ animation: none; }}
    .task-dur.running, .task-card.is-running .timer-big {{ animation: none; }}
}}

/* ── Light theme extras ── */
[data-theme="light"] .date-header,
[data-theme="light"] .home-header,
[data-theme="light"] .fin-header,
[data-theme="light"] .proj-header,
[data-theme="light"] .analytics-header {{
    box-shadow: 0 2px 16px rgba(99, 102, 241, 0.08);
}}
[data-theme="light"] .proj-section-badge {{ color: #4338CA; background: rgba(67, 56, 202, 0.1); }}
[data-theme="light"] .proj-card-section {{ box-shadow: var(--elevation-1); }}
[data-theme="light"] .proj-header {{
    background: linear-gradient(145deg, #EEF2FF 0%, #E0E7FF 50%, #EDE9FE 100%);
}}
[data-theme="light"] .proj-header-title {{ color: #3730A3; }}
[data-theme="light"] .proj-header-add {{
    background: #4F46E5; color: #fff; border-color: transparent;
}}
[data-theme="light"] .proj-hero-in-header {{
    background: rgba(255, 255, 255, 0.72);
    border-color: rgba(79, 70, 229, 0.12);
}}
[data-theme="light"] .proj-summary-item {{
    background: rgba(255, 255, 255, 0.85);
    border-color: rgba(79, 70, 229, 0.1);
}}
[data-theme="light"] .proj-summary-val {{ color: #3730A3; }}
[data-theme="light"] .proj-summary-lbl {{ color: var(--text-muted); }}
[data-theme="light"] .task-card,
[data-theme="light"] .section,
[data-theme="light"] .stat-card,
[data-theme="light"] .day-card {{
    box-shadow: var(--elevation-1);
    border-color: var(--border-subtle);
}}
[data-theme="light"] .bottom-nav {{
    box-shadow: var(--shadow-nav);
    border-color: var(--border-subtle);
}}
[data-theme="light"] .toast {{
    box-shadow: var(--elevation-2);
}}
[data-theme="light"] .fin-hero {{
    background: linear-gradient(145deg, #EEF2FF 0%, var(--surface) 60%, #ECFDF5 100%);
    border-color: var(--border-subtle);
    box-shadow: var(--elevation-1);
}}
[data-theme="light"] .fin-hero-stat {{
    background: rgba(0,0,0,0.03);
    border-color: var(--border-subtle);
}}
[data-theme="light"] .fin-hero-balance.positive {{ color: var(--success); }}
[data-theme="light"] .fin-hero-balance.negative {{ color: var(--error); }}
[data-theme="light"] .period-btn.active {{
    background: rgba(99, 102, 241, 0.12);
    border-color: rgba(99, 102, 241, 0.25);
}}
"""
