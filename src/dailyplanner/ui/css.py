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
.nav-btn.active.nav-tracking {{
    color: #2DD4BF;
    background: rgba(45, 212, 191, 0.16);
}}
.nav-btn.active.nav-tracking::after {{ background: #2DD4BF; }}
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
    .date-header:not(.home-header):not(.fin-header):not(.track-header) {{
        padding-top: calc(14px + max(36px, var(--safe-top)));
    }}
    .date-header.track-header {{
        padding-top: calc(10px + max(36px, var(--safe-top)));
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
.home-page {{ padding-bottom: 24px; }}

.home-header,
.fin-header {{
    padding: calc(10px + var(--safe-top)) 14px 14px;
    gap: 10px;
}}

.home-header {{
    background:
        linear-gradient(165deg, #020617 0%, #0C4A6E 28%, #0369A1 52%, #1D4ED8 78%, #7C2D12 100%);
    border-bottom: 1px solid rgba(125, 211, 252, 0.12);
}}
.home-header::after {{
    content: '';
    position: absolute;
    top: 8px;
    left: 20px;
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(251, 191, 36, 0.5) 0%, rgba(251, 191, 36, 0.1) 42%, transparent 72%);
    pointer-events: none;
    z-index: 0;
    filter: blur(2px);
    animation: homeSunPulse 4s ease-in-out infinite;
}}
.home-header::before {{
    background:
        radial-gradient(ellipse 80% 60% at 88% 8%, rgba(251, 191, 36, 0.28), transparent 48%),
        radial-gradient(ellipse 55% 45% at 8% 92%, rgba(56, 189, 248, 0.22), transparent 55%),
        radial-gradient(ellipse 40% 30% at 50% 100%, rgba(99, 102, 241, 0.15), transparent 60%);
}}

.home-header-orbs {{
    position: absolute; inset: 0; pointer-events: none; overflow: hidden; z-index: 0;
}}
.home-orb {{
    position: absolute; border-radius: 50%; filter: blur(42px); opacity: 0.5;
    animation: homeOrbFloat 9s ease-in-out infinite;
}}
.home-orb-1 {{
    width: 130px; height: 130px; top: -36px; right: -24px;
    background: rgba(56, 189, 248, 0.38);
}}
.home-orb-2 {{
    width: 100px; height: 100px; bottom: 8px; left: -16px;
    background: rgba(251, 191, 36, 0.28); animation-delay: -3.5s;
}}
.home-orb-3 {{
    width: 70px; height: 70px; top: 42%; left: 42%;
    background: rgba(129, 140, 248, 0.22); animation-delay: -6s;
}}

.home-header-brand {{ position: relative; z-index: 1; }}
.home-header-top {{
    display: flex; align-items: center; gap: 10px; direction: rtl;
    margin-bottom: 6px;
}}
.home-brand-mark {{
    width: 40px; height: 40px; border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(125, 211, 252, 0.28);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.12);
    flex-shrink: 0;
}}
.home-header-titles {{
    flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px;
}}
.home-header-title {{
    font-size: 18px; font-weight: 800; color: #fff; letter-spacing: 0.01em;
    text-shadow: 0 2px 16px rgba(56, 189, 248, 0.35);
    line-height: 1.2;
}}
.home-greeting {{
    font-size: 11px; color: rgba(224, 242, 254, 0.78); font-weight: 500;
}}
.home-today-pill {{
    display: inline-flex; align-items: center; gap: 5px;
    font-size: 10px; font-weight: 600; color: #FEF3C7;
    background: rgba(251, 191, 36, 0.16);
    border: 1px solid rgba(251, 191, 36, 0.35);
    border-radius: 999px; padding: 4px 10px 4px 8px;
    flex-shrink: 0;
    box-shadow: 0 0 20px rgba(251, 191, 36, 0.12);
}}
.home-today-dot {{
    width: 6px; height: 6px; border-radius: 50%;
    background: #FBBF24; box-shadow: 0 0 8px #FBBF24;
    animation: homeLivePulse 1.6s ease-in-out infinite;
}}
.home-date-row {{ margin-top: 2px; }}
.home-date-title {{
    font-size: var(--text-sm); opacity: 0.95; color: #E0F2FE;
    font-weight: var(--font-medium);
}}
.home-header .date-nav-btn,
.fin-header .date-nav-btn {{
    width: 34px; height: 34px;
}}
.home-header .date-nav-btn {{
    background: rgba(56, 189, 248, 0.12);
    border-color: rgba(56, 189, 248, 0.28);
    color: #BAE6FD;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
}}
.home-header .date-nav-btn .ico {{ color: #7DD3FC; }}
.home-header .home-today-btn,
.fin-header .fin-today-btn {{
    padding: 4px 10px;
    font-size: 12px;
}}
.home-header .home-today-btn {{
    background: rgba(251, 191, 36, 0.18);
    border-color: rgba(251, 191, 36, 0.42);
    color: #FEF3C7;
    box-shadow: 0 0 20px rgba(251, 191, 36, 0.14);
}}
.home-header-tools {{
    gap: 5px !important;
}}
.home-header .home-tool-btn,
.home-header .icon-btn.home-tool-btn {{
    width: 34px; height: 34px;
    border-radius: 12px;
}}
.home-header .home-tool-btn.wide {{
    height: 34px; padding: 0 10px; font-size: 12px; width: auto;
}}
.home-header .home-tool-btn {{
    background: rgba(15, 23, 42, 0.35);
    border: 1px solid rgba(125, 211, 252, 0.22);
    color: #E0F2FE;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    transition: background var(--duration-fast), transform var(--duration-fast), border-color var(--duration-fast);
}}
.home-header .home-tool-btn:active {{ transform: scale(0.94); background: rgba(56, 189, 248, 0.18); }}
.home-header .home-tool-btn .ico {{ color: #7DD3FC; }}
.home-header .home-tool-btn .fin-emoji {{
    flex-shrink: 0;
    color: unset;
    -webkit-text-fill-color: initial;
}}
.home-header .urgent-badge {{
    background: linear-gradient(135deg, #F97316, #EA580C);
    color: #fff;
    box-shadow: 0 0 12px rgba(249, 115, 22, 0.5);
}}

/* hero panel */
.home-hero-panel {{
    margin-top: 4px;
    padding: 12px;
    background: rgba(2, 6, 23, 0.42);
    border: 1px solid rgba(56, 189, 248, 0.22);
    border-radius: 18px;
    position: relative;
    z-index: 1;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    box-shadow:
        0 8px 32px rgba(0, 0, 0, 0.22),
        inset 0 1px 0 rgba(255, 255, 255, 0.07);
    animation: homePanelIn 0.45s var(--ease-out) both;
}}
.home-hero-main {{
    display: flex; align-items: center; gap: 14px; direction: rtl;
}}
.home-hero-side {{ flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 8px; }}

.home-eff-ring {{
    position: relative; width: 88px; height: 88px; flex-shrink: 0;
}}
.home-eff-glow {{
    position: absolute; inset: -8px; border-radius: 50%;
    background: radial-gradient(circle, rgba(56, 189, 248, 0.25), transparent 70%);
    animation: homeEffGlow 3s ease-in-out infinite;
}}
.home-eff-svg {{
    position: absolute; inset: 0; width: 100%; height: 100%;
}}
.home-eff-arc {{
    transition: stroke-dasharray 0.6s var(--ease-out);
    filter: drop-shadow(0 0 6px rgba(110, 231, 183, 0.35));
}}
.home-eff-center {{
    position: absolute; inset: 0;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: 1px;
}}
.home-eff-val {{
    font-size: 20px; font-weight: 800; color: #F8FAFC;
    font-variant-numeric: tabular-nums; line-height: 1;
}}
.home-eff-val small {{ font-size: 11px; font-weight: 600; opacity: 0.75; }}
.home-eff-lbl {{
    font-size: 9px; color: rgba(224, 242, 254, 0.62); font-weight: 500;
}}

.home-time-bar {{
    display: flex; height: 5px; border-radius: 999px; overflow: hidden;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(125, 211, 252, 0.12);
}}
.home-time-seg {{ height: 100%; transition: width 0.5s var(--ease-out); }}
.home-time-seg.useful {{
    background: linear-gradient(90deg, #059669, #6EE7B7);
    box-shadow: 0 0 8px rgba(110, 231, 183, 0.35);
}}
.home-time-seg.not {{
    background: linear-gradient(90deg, #EA580C, #FDBA74);
}}

.home-hero-stats {{
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 6px;
    direction: rtl;
}}
.home-hero-stat {{
    display: flex; align-items: center; gap: 8px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(125, 211, 252, 0.14);
    border-radius: 12px;
    padding: 8px 9px;
    transition: border-color var(--duration-fast), background var(--duration-fast);
}}
.home-stat-icon {{
    width: 30px; height: 30px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    background: rgba(255, 255, 255, 0.05);
    flex-shrink: 0;
}}
.home-stat-body {{ min-width: 0; flex: 1; }}
.home-hero-stat .fin-emoji {{ flex-shrink: 0; }}
.home-stat-lbl {{
    display: block; font-size: 9px;
    color: rgba(224, 242, 254, 0.58);
    line-height: 1.2;
}}
.home-stat-val {{
    display: block; font-size: 12px; font-weight: 700;
    color: #F8FAFC; font-variant-numeric: tabular-nums;
    line-height: 1.3;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}}
.home-hero-stat.useful .home-stat-val {{ color: #6EE7B7; }}
.home-hero-stat.not .home-stat-val {{ color: #FDBA74; }}
.home-hero-stat.tasks .home-stat-val {{ color: #7DD3FC; }}
.home-hero-stat.tracked .home-stat-val {{ color: #C4B5FD; }}
.home-hero-stat.useful .home-stat-icon {{ background: rgba(110, 231, 183, 0.12); }}
.home-hero-stat.not .home-stat-icon {{ background: rgba(253, 186, 116, 0.12); }}
.home-hero-stat.tasks .home-stat-icon {{ background: rgba(125, 211, 252, 0.12); }}
.home-hero-stat.tracked .home-stat-icon {{ background: rgba(196, 181, 253, 0.12); }}

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
    font-size: 16px;
    min-width: 20px;
    min-height: 20px;
}}
.analytics-summary-item .fin-emoji-sm,
.proj-summary-item .fin-emoji-sm {{
    font-size: 22px;
    min-width: 26px;
    min-height: 26px;
}}

/* home body */
.home-body {{
    padding: 0 4px;
    animation: homeBodyIn 0.4s var(--ease-out) 0.08s both;
}}
.home-sec-head {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 14px 10px 6px; direction: rtl; gap: 8px;
}}
.home-sec-title {{
    display: flex; align-items: center; gap: 8px;
    font-size: var(--text-base); font-weight: var(--font-bold); color: var(--text);
}}
.home-sec-title .fin-emoji-sm {{ opacity: 0.9; }}
.home-sec-badge {{
    font-size: 11px; font-weight: 700; color: #7DD3FC;
    background: rgba(56, 189, 248, 0.12);
    border: 1px solid rgba(56, 189, 248, 0.22);
    border-radius: 999px; padding: 2px 8px;
    font-variant-numeric: tabular-nums;
}}
.home-running-badge {{
    display: inline-flex; align-items: center; gap: 5px;
    font-size: 10px; font-weight: 600; color: #5EEAD4;
    background: rgba(45, 212, 191, 0.1);
    border: 1px solid rgba(45, 212, 191, 0.28);
    border-radius: 999px; padding: 4px 10px;
}}
.home-running-dot {{
    width: 6px; height: 6px; border-radius: 50%;
    background: #2DD4BF; box-shadow: 0 0 8px #2DD4BF;
    animation: homeLivePulse 1.4s ease-in-out infinite;
}}

.home-search-row {{
    padding: 6px 8px 8px;
}}
.home-search-wrap {{
    background: var(--surface);
    border: 1px solid rgba(56, 189, 248, 0.16);
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(14, 116, 144, 0.1);
    transition: border-color var(--duration-fast), box-shadow var(--duration-fast);
}}
.home-search-wrap:focus-within {{
    border-color: rgba(56, 189, 248, 0.45);
    box-shadow: 0 4px 24px rgba(37, 99, 235, 0.16), 0 0 0 3px rgba(56, 189, 248, 0.1);
}}
.home-search-input {{
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    border-radius: 16px;
}}
.home-search-input:focus {{
    box-shadow: none !important;
}}

.home-task-list {{ padding: 4px 6px 8px; }}
.home-task-card {{
    animation: homeTaskIn 0.38s var(--ease-out) both;
    animation-delay: calc(var(--home-stagger, 0) * 45ms);
    border-radius: 18px;
    transition: transform var(--duration-fast), box-shadow var(--duration-fast);
}}
.home-task-card:active {{ transform: scale(0.985); }}
.home-task-card.is-running {{
    border-color: rgba(45, 212, 191, 0.35);
    box-shadow: var(--elevation-1), inset -4px 0 0 0 var(--running), 0 0 24px rgba(45, 212, 191, 0.08);
}}
.home-task-card .task-header {{ padding: 13px 14px; }}
.home-task-card .task-title-wrap {{ font-weight: var(--font-medium); }}

/* empty state */
.home-empty {{
    padding: var(--space-8) var(--space-4) var(--space-6);
    animation: homePanelIn 0.5s var(--ease-out) both;
}}
.home-empty-visual {{
    position: relative; width: 120px; height: 120px; margin: 0 auto 16px;
}}
.home-empty-ring {{
    position: absolute; border-radius: 50%;
    border: 1px solid rgba(56, 189, 248, 0.2);
    animation: homeEmptyRing 3s ease-in-out infinite;
}}
.home-empty-ring-1 {{
    inset: 0;
    border-color: rgba(56, 189, 248, 0.25);
}}
.home-empty-ring-2 {{
    inset: 12px;
    border-color: rgba(129, 140, 248, 0.2);
    animation-delay: -1.5s;
}}
.home-empty-icon {{
    position: absolute; inset: 24px;
    display: flex; align-items: center; justify-content: center;
    background: linear-gradient(145deg, rgba(56, 189, 248, 0.12), rgba(99, 102, 241, 0.1));
    border-radius: 50%;
    border: 1px solid rgba(125, 211, 252, 0.2);
    box-shadow: 0 8px 24px rgba(14, 116, 144, 0.15);
}}
.home-empty-btn {{
    background: linear-gradient(135deg, #0284C7, #2563EB);
    border-color: transparent;
    border-radius: 14px;
    padding: 12px 24px;
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.32);
}}

/* wellness + notes */
.home-wellness-wrap {{ padding: 0 6px; }}
.home-wellness-wrap .section {{
    margin: 8px 6px;
    border-radius: 18px;
    background: linear-gradient(160deg, var(--surface) 0%, var(--surface-deep) 100%);
    border-color: rgba(56, 189, 248, 0.1);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
}}
.home-wellness-wrap .sec-title::before {{ display: none; }}
.home-wellness-wrap .well-btn {{
    border-radius: 14px;
    transition: border-color var(--duration-fast), background var(--duration-fast);
}}
.home-wellness-wrap .mood-btn {{
    border-radius: 14px;
    transition: transform var(--duration-fast), box-shadow var(--duration-fast);
}}
.home-wellness-wrap .mood-btn.sel {{
    transform: scale(1.08);
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.25);
}}

.home-note-section {{
    margin: 8px 12px 16px !important;
    border-radius: 18px !important;
    background: linear-gradient(160deg, var(--surface) 0%, var(--surface-deep) 100%) !important;
    border-color: rgba(56, 189, 248, 0.1) !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12) !important;
}}
.home-note-title {{
    gap: 8px;
}}
.home-note-title::before {{ display: none; }}
.home-note-input {{
    min-height: 88px;
    border-radius: 14px;
    background: var(--surface-muted);
    border-color: var(--divider);
    transition: border-color var(--duration-fast), box-shadow var(--duration-fast);
}}
.home-note-input:focus {{
    border-color: rgba(56, 189, 248, 0.45);
    box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.1);
}}

/* FAB */
.home-fab {{
    position: fixed;
    bottom: calc(96px + var(--safe-bottom));
    left: max(20px, calc(50% - 240px));
    z-index: 150;
    width: 56px; height: 56px;
    border-radius: 18px;
    border: none;
    background: linear-gradient(145deg, #0284C7, #2563EB);
    color: #fff;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer;
    box-shadow:
        0 8px 28px rgba(37, 99, 235, 0.42),
        0 0 0 1px rgba(255, 255, 255, 0.12) inset;
    transition: transform var(--duration-fast), box-shadow var(--duration-fast);
    animation: homeFabIn 0.4s var(--ease-out) 0.2s both;
}}
.home-fab .ico {{ width: 24px; height: 24px; }}
.home-fab:active {{ transform: scale(0.92); }}
body.kb-open .home-fab {{ display: none; }}

.home-calendar-wrap {{
    padding: 8px 10px 0;
    animation: homePanelIn 0.35s var(--ease-out) both;
}}
.home-calendar-wrap .calendar-panel {{
    margin: 0;
    border-radius: 18px;
    border-color: rgba(56, 189, 248, 0.14);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
}}

.home-page .empty-state .fin-icon-lg {{
    display: flex; margin: 0 auto;
}}

[data-theme="light"] .home-header {{
    background: linear-gradient(155deg, #FFF7ED 0%, #FFEDD5 28%, #E0F2FE 58%, #DBEAFE 82%, #F0F9FF 100%);
    border-bottom-color: rgba(3, 105, 161, 0.1);
}}
[data-theme="light"] .home-header::after {{
    background: radial-gradient(circle, rgba(251, 191, 36, 0.55) 0%, rgba(251, 191, 36, 0.12) 48%, transparent 72%);
}}
[data-theme="light"] .home-header::before {{
    background:
        radial-gradient(ellipse at 90% 10%, rgba(251, 191, 36, 0.32), transparent 42%),
        radial-gradient(ellipse at 10% 90%, rgba(56, 189, 248, 0.2), transparent 50%);
}}
[data-theme="light"] .home-brand-mark {{
    background: rgba(255, 255, 255, 0.75);
    border-color: rgba(3, 105, 161, 0.14);
    box-shadow: 0 4px 14px rgba(14, 116, 144, 0.1);
}}
[data-theme="light"] .home-header-title {{
    color: #0C4A6E;
    text-shadow: none;
}}
[data-theme="light"] .home-greeting {{ color: #0369A1; }}
[data-theme="light"] .home-today-pill {{
    background: rgba(245, 158, 11, 0.14);
    border-color: rgba(245, 158, 11, 0.35);
    color: #B45309;
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
[data-theme="light"] .home-hero-panel {{
    background: rgba(255, 255, 255, 0.78);
    border-color: rgba(3, 105, 161, 0.14);
    box-shadow: 0 6px 24px rgba(14, 116, 144, 0.1);
}}
[data-theme="light"] .home-eff-val {{ color: #0C4A6E; }}
[data-theme="light"] .home-eff-lbl {{ color: var(--text-muted); }}
[data-theme="light"] .home-time-bar {{ background: rgba(3, 105, 161, 0.08); }}
[data-theme="light"] .home-hero-stat {{
    background: rgba(255, 255, 255, 0.9);
    border-color: rgba(3, 105, 161, 0.1);
}}
[data-theme="light"] .home-stat-lbl {{ color: var(--text-muted); }}
[data-theme="light"] .home-stat-val {{ color: var(--text); }}
[data-theme="light"] .home-hero-stat.useful .home-stat-val {{ color: var(--success); }}
[data-theme="light"] .home-hero-stat.not .home-stat-val {{ color: var(--warning); }}
[data-theme="light"] .home-hero-stat.tasks .home-stat-val {{ color: #0284C7; }}
[data-theme="light"] .home-hero-stat.tracked .home-stat-val {{ color: #7C3AED; }}
[data-theme="light"] .home-sec-badge {{
    color: #0284C7;
    background: rgba(2, 132, 199, 0.1);
    border-color: rgba(2, 132, 199, 0.18);
}}
[data-theme="light"] .home-search-wrap {{
    border-color: rgba(3, 105, 161, 0.12);
    box-shadow: 0 2px 12px rgba(14, 116, 144, 0.08);
}}
[data-theme="light"] .home-empty-btn,
[data-theme="light"] .home-fab {{
    background: linear-gradient(135deg, #0284C7, #0369A1);
    box-shadow: 0 6px 20px rgba(2, 132, 199, 0.28);
}}
[data-theme="light"] .home-wellness-wrap .section,
[data-theme="light"] .home-note-section {{
    box-shadow: var(--elevation-1) !important;
    border-color: var(--border-subtle) !important;
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
    align-items: flex-end;
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
.modal-input-grouped {{
    direction: ltr;
    text-align: left;
}}

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
    background: linear-gradient(155deg, #061510 0%, #0F2E28 28%, #1A4034 55%, #0D2818 82%, #162016 100%);
    border-bottom: 1px solid rgba(77, 217, 128, 0.14);
    overflow: hidden;
}}
.fin-header::before {{
    background:
        radial-gradient(ellipse 75% 55% at 88% 10%, rgba(77, 217, 128, 0.22), transparent 52%),
        radial-gradient(ellipse 50% 45% at 10% 90%, rgba(45, 212, 191, 0.14), transparent 55%),
        radial-gradient(ellipse 40% 30% at 50% 100%, rgba(255, 176, 32, 0.08), transparent 60%);
}}
.fin-header::after {{
    content: '';
    position: absolute;
    top: 12px;
    left: 24px;
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(77, 217, 128, 0.35) 0%, rgba(77, 217, 128, 0.08) 45%, transparent 72%);
    pointer-events: none;
    z-index: 0;
    filter: blur(2px);
    animation: finGlowPulse 4s ease-in-out infinite;
}}
.fin-header-orbs {{
    position: absolute; inset: 0; pointer-events: none; overflow: hidden; z-index: 0;
}}
.fin-orb {{
    position: absolute; border-radius: 50%; filter: blur(40px); opacity: 0.45;
    animation: finOrbFloat 10s ease-in-out infinite;
}}
.fin-orb-1 {{
    width: 120px; height: 120px; top: -30px; right: -20px;
    background: rgba(77, 217, 128, 0.32);
}}
.fin-orb-2 {{
    width: 90px; height: 90px; bottom: 10px; left: -10px;
    background: rgba(45, 212, 191, 0.22); animation-delay: -3.5s;
}}
.fin-orb-3 {{
    width: 60px; height: 60px; top: 45%; left: 40%;
    background: rgba(255, 176, 32, 0.18); animation-delay: -6.5s;
}}
.fin-header-brand {{ position: relative; z-index: 1; }}
.fin-header-top {{
    display: flex; align-items: center; gap: 10px; direction: rtl;
    margin-bottom: 4px;
}}
.fin-brand-mark {{
    width: 40px; height: 40px; border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(77, 217, 128, 0.28);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    flex-shrink: 0;
}}
.fin-header-titles {{
    flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px;
}}
.fin-header-title {{
    font-size: 18px; font-weight: 800; color: #fff; letter-spacing: 0.01em;
    text-shadow: 0 2px 14px rgba(77, 217, 128, 0.3);
    line-height: 1.2;
}}
.fin-header-sub {{
    font-size: 11px; color: rgba(167, 243, 208, 0.72); font-weight: 500;
}}
.fin-month-pill {{
    display: inline-flex; align-items: center; gap: 5px;
    font-size: 10px; font-weight: 600; color: #A7F3D0;
    background: rgba(77, 217, 128, 0.14);
    border: 1px solid rgba(77, 217, 128, 0.32);
    border-radius: 999px; padding: 4px 10px 4px 8px;
    flex-shrink: 0;
    box-shadow: 0 0 18px rgba(77, 217, 128, 0.1);
}}
.fin-month-dot {{
    width: 6px; height: 6px; border-radius: 50%;
    background: #4DD980; box-shadow: 0 0 8px #4DD980;
    animation: finLivePulse 1.6s ease-in-out infinite;
}}
.fin-date-row {{ margin-top: 2px; }}
.fin-month-title {{ font-size: var(--text-sm); opacity: 0.95; color: #D1FAE5; font-weight: var(--font-medium); }}
.fin-header .date-nav-btn {{
    background: rgba(77, 217, 128, 0.12);
    border-color: rgba(77, 217, 128, 0.28);
    color: #4DD980;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
}}
.fin-header .date-nav-btn .ico {{ color: #6EE7B7; }}
.fin-header .fin-today-btn {{
    background: rgba(77, 217, 128, 0.16);
    border-color: rgba(77, 217, 128, 0.38);
    color: #A7F3D0;
    box-shadow: 0 0 18px rgba(77, 217, 128, 0.12);
}}
[data-theme="light"] .fin-header {{
    background: linear-gradient(155deg, #ECFDF5 0%, #D1FAE5 35%, #E8F5EE 65%, #F0FAF4 100%);
    border-bottom-color: rgba(15, 46, 40, 0.08);
}}
[data-theme="light"] .fin-header::after {{
    background: radial-gradient(circle, rgba(77, 217, 128, 0.4) 0%, rgba(77, 217, 128, 0.1) 48%, transparent 72%);
}}
[data-theme="light"] .fin-header-title {{ color: #0F2E28; text-shadow: none; }}
[data-theme="light"] .fin-header-sub {{ color: #1A4034; opacity: 0.75; }}
[data-theme="light"] .fin-month-title {{ color: #1A4034; opacity: 1; }}
[data-theme="light"] .fin-month-pill {{
    background: rgba(15, 46, 40, 0.08);
    border-color: rgba(15, 46, 40, 0.14);
    color: #0F2E28;
}}
[data-theme="light"] .fin-brand-mark {{
    background: rgba(255, 255, 255, 0.75);
    border-color: rgba(15, 46, 40, 0.12);
    box-shadow: 0 4px 14px rgba(15, 46, 40, 0.08);
}}
[data-theme="light"] .fin-header .date-nav-btn {{
    background: rgba(15, 46, 40, 0.06);
    border-color: rgba(15, 46, 40, 0.12);
    color: #0F2E28;
}}
[data-theme="light"] .fin-header .date-nav-btn .ico {{ color: #0F2E28; }}
[data-theme="light"] .fin-header .fin-today-btn {{
    background: #0F2E28; color: #fff; border-color: transparent;
}}

/* hero panel */
.fin-hero-panel {{
    margin-top: 6px;
    padding: 12px;
    background: rgba(6, 21, 16, 0.55);
    border: 1px solid rgba(77, 217, 128, 0.22);
    border-radius: 18px;
    position: relative;
    z-index: 1;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    box-shadow:
        0 8px 32px rgba(0, 0, 0, 0.22),
        inset 0 1px 0 rgba(255, 255, 255, 0.06);
    animation: finPanelIn 0.45s var(--ease-out) both;
}}
.fin-hero-main {{
    display: flex; align-items: center; gap: 14px; direction: rtl;
}}
.fin-hero-side {{ flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 6px; }}

.fin-balance-ring {{
    position: relative; width: 84px; height: 84px; flex-shrink: 0;
}}
.fin-ring-glow {{
    position: absolute; inset: -6px; border-radius: 50%;
    background: radial-gradient(circle, rgba(77, 217, 128, 0.2), transparent 70%);
    animation: finRingGlow 3s ease-in-out infinite;
}}
.fin-ring-svg {{ position: absolute; inset: 0; width: 100%; height: 100%; }}
.fin-ring-track {{
    fill: none; stroke: rgba(255, 255, 255, 0.08); stroke-width: 7;
}}
.fin-ring-arc {{
    fill: none; stroke-linecap: round;
    transition: stroke-dashoffset 0.7s var(--ease-out);
    filter: drop-shadow(0 0 4px rgba(77, 217, 128, 0.4));
}}
.fin-ring-center {{
    position: absolute; inset: 0;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: 1px;
}}
.fin-ring-pct {{
    font-size: 17px; font-weight: 800; color: #F8FAFC;
    font-variant-numeric: tabular-nums; line-height: 1;
}}
.fin-ring-lbl {{
    font-size: 8px; color: rgba(209, 250, 229, 0.62); font-weight: 500;
}}

.fin-hero-label {{ font-size: 11px; color: rgba(209, 250, 229, 0.65); margin-bottom: 0; }}
.fin-hero-balance {{
    font-size: 26px; font-weight: 800; letter-spacing: -0.5px;
    font-variant-numeric: tabular-nums; line-height: 1.15;
}}
.fin-hero-balance.positive {{ color: #4DD980; text-shadow: 0 0 20px rgba(77, 217, 128, 0.25); }}
.fin-hero-balance.negative {{ color: #FF7359; text-shadow: 0 0 20px rgba(255, 115, 89, 0.25); }}
.fin-hero-unit {{ font-size: 11px; font-weight: normal; color: rgba(209, 250, 229, 0.55); margin-right: 4px; }}

.fin-cashflow {{ margin-top: 2px; }}
.fin-cashflow-bar {{
    display: flex; height: 5px; border-radius: 999px; overflow: hidden;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(77, 217, 128, 0.12);
}}
.fin-cashflow-inc {{
    height: 100%; background: linear-gradient(90deg, #059669, #4DD980);
    box-shadow: 0 0 8px rgba(77, 217, 128, 0.35);
    transition: width 0.5s var(--ease-out);
}}
.fin-cashflow-exp {{
    height: 100%; background: linear-gradient(90deg, #EA580C, #FF7359);
    transition: width 0.5s var(--ease-out);
}}
.fin-cashflow-labels {{
    display: flex; justify-content: space-between; margin-top: 4px;
    font-size: 9px; font-weight: 600;
}}
.fin-cf-inc {{ color: #6EE7B7; }}
.fin-cf-exp {{ color: #FDBA74; }}

.fin-hero-stats {{
    display: grid; grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 6px; margin-top: 4px; direction: rtl;
}}
.fin-hero-stat {{
    display: flex; align-items: center; gap: 6px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(77, 217, 128, 0.14);
    border-radius: 11px; padding: 7px 8px;
    transition: border-color var(--duration-fast), background var(--duration-fast);
}}
.fin-hero-stat.income {{ border-color: rgba(77, 217, 128, 0.18); }}
.fin-hero-stat.expense {{ border-color: rgba(255, 115, 89, 0.18); }}
.fin-stat-lbl {{ display: block; font-size: 9px; color: rgba(209, 250, 229, 0.58); line-height: 1.2; }}
.fin-stat-val {{
    display: block; font-size: 12px; font-weight: 700;
    color: #F8FAFC; font-variant-numeric: tabular-nums; line-height: 1.3;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}}
.fin-hero-stat.income .fin-stat-val {{ color: #6EE7B7; }}
.fin-hero-stat.expense .fin-stat-val {{ color: #FDBA74; }}

.fin-hero-invest {{
    margin-top: 4px; padding: 6px 10px; border-radius: 10px;
    background: rgba(255, 176, 32, 0.1); border: 1px solid rgba(255, 176, 32, 0.22);
    font-size: 11px; color: #FFB020; display: flex; align-items: center; gap: 6px;
    justify-content: center;
}}
.fin-hero-invest-note {{ font-size: 10px; color: rgba(209, 250, 229, 0.45); }}

[data-theme="light"] .fin-hero-panel {{
    background: rgba(255, 255, 255, 0.72);
    border-color: rgba(15, 46, 40, 0.1);
    box-shadow: 0 8px 28px rgba(15, 46, 40, 0.08);
}}
[data-theme="light"] .fin-ring-pct {{ color: #0F2E28; }}
[data-theme="light"] .fin-ring-lbl {{ color: var(--text-muted); }}
[data-theme="light"] .fin-ring-track {{ stroke: rgba(15, 46, 40, 0.08); }}
[data-theme="light"] .fin-hero-label {{ color: var(--text-muted); }}
[data-theme="light"] .fin-hero-unit {{ color: var(--text-muted); }}
[data-theme="light"] .fin-stat-lbl {{ color: var(--text-muted); }}
[data-theme="light"] .fin-stat-val {{ color: var(--text); }}
[data-theme="light"] .fin-hero-stat {{ background: rgba(15, 46, 40, 0.03); }}

/* body + actions */
.fin-body {{
    padding: 0 2px;
    animation: finBodyIn 0.4s var(--ease-out) 0.06s both;
}}
.fin-actions {{
    display: flex; flex-wrap: wrap; gap: 8px; padding: 12px 10px 6px; direction: rtl;
}}
.fin-action-btn {{
    position: relative; overflow: hidden;
    flex: 1 1 calc(33.333% - 6px);
    display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 3px;
    padding: 12px 6px 10px; border-radius: 14px; border: 1px solid transparent;
    cursor: pointer; font-family: 'Vazirmatn', sans-serif;
    transition: transform var(--duration-fast), box-shadow var(--duration-fast), border-color var(--duration-fast);
}}
.fin-action-btn:active {{ transform: scale(0.94); }}
.fin-action-glow {{
    position: absolute; inset: 0; opacity: 0;
    background: radial-gradient(circle at 50% 0%, rgba(255,255,255,0.12), transparent 70%);
    transition: opacity var(--duration-fast);
    pointer-events: none;
}}
.fin-action-btn:active .fin-action-glow {{ opacity: 1; }}
.fin-action-icon {{
    font-size: 18px; line-height: 1; font-weight: bold;
    width: 32px; height: 32px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
}}
.fin-action-lbl {{ font-size: 11px; font-weight: 700; line-height: 1.2; }}
.fin-action-btn.income {{
    background: linear-gradient(145deg, rgba(26,64,40,0.9), rgba(20,50,32,0.95));
    color: #4DD980; border-color: rgba(77,217,128,0.25);
    box-shadow: 0 4px 16px rgba(77,217,128,0.12);
}}
.fin-action-btn.income .fin-action-icon {{ background: rgba(77,217,128,0.15); }}
.fin-action-btn.expense {{
    background: linear-gradient(145deg, rgba(61,24,24,0.9), rgba(50,18,18,0.95));
    color: #FF7359; border-color: rgba(255,115,89,0.25);
    box-shadow: 0 4px 16px rgba(255,115,89,0.1);
}}
.fin-action-btn.expense .fin-action-icon {{ background: rgba(255,115,89,0.15); }}
.fin-action-btn.invest {{
    background: linear-gradient(145deg, rgba(61,48,24,0.9), rgba(50,38,16,0.95));
    color: #FFB020; border-color: rgba(255,176,32,0.25);
    box-shadow: 0 4px 16px rgba(255,176,32,0.1);
}}
.fin-action-btn.invest .fin-action-icon {{ background: rgba(255,176,32,0.15); }}
.fin-action-btn.budget {{
    background: linear-gradient(145deg, rgba(26,26,64,0.9), rgba(20,20,50,0.95));
    color: #818CF8; border-color: rgba(129,140,248,0.25);
    box-shadow: 0 4px 16px rgba(129,140,248,0.1);
}}
.fin-action-btn.budget .fin-action-icon {{ background: rgba(129,140,248,0.15); }}
.fin-action-btn.inst {{
    background: linear-gradient(145deg, rgba(26,48,40,0.9), rgba(18,38,32,0.95));
    color: #5ECFAB; border-color: rgba(94,207,171,0.25);
    box-shadow: 0 4px 16px rgba(94,207,171,0.1);
}}
.fin-action-btn.inst .fin-action-icon {{ background: rgba(94,207,171,0.15); font-size: 14px; font-weight: normal; }}

/* legacy hero (standalone) */
.fin-hero {{
    margin: 12px 12px 0;
    padding: 20px 18px 16px;
    background: linear-gradient(145deg, #1E1E3A 0%, #1C1C1E 60%, #162016 100%);
    border-radius: 18px;
    border: 1px solid #3C3C5E44;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    text-align: center;
}}
.fin-hero-in-header {{ display: none; }}
.fin-hero-panel .fin-hero-stat .fin-emoji,
.fin-hero-invest .fin-emoji {{
    flex-shrink: 0;
    color: unset;
    -webkit-text-fill-color: initial;
}}
.fin-stat-val {{ display: block; font-size: 13px; font-weight: bold; font-variant-numeric: tabular-nums; }}
.fin-hero-invest .fin-icon {{ width: 24px; height: 24px; font-size: 12px; border-radius: 50%; }}
.fin-inst-card {{ margin-top: 4px; }}
.fin-inst-empty {{
    font-size: 12px; color: var(--text-muted); text-align: center; padding: 8px 0;
}}
.fin-inst-empty a {{ color: var(--primary); }}
.fin-inst-row {{
    display: flex; align-items: center; gap: 8px; direction: rtl;
    padding: 10px 12px; margin: 6px 0;
    background: var(--surface-muted);
    border: 1px solid var(--divider);
    border-radius: 12px;
    animation: finTxnIn 0.35s var(--ease-out) both;
    animation-delay: calc(var(--fin-stagger, 0) * 40ms);
}}
.fin-inst-footer {{
    margin-top: 8px; padding-top: 10px;
    border-top: 1px solid var(--divider);
    font-size: 12px; color: var(--text-muted); text-align: center;
}}
.fin-inst-footer strong {{ color: var(--error); font-weight: 700; }}

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
    background: linear-gradient(160deg, var(--surface) 0%, var(--surface-deep) 100%);
    border-radius: 18px;
    margin: 10px 10px;
    padding: 14px 14px 12px;
    border: 1px solid var(--divider);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.14);
    transition: box-shadow var(--duration-fast);
}}
.fin-card-animate {{
    animation: finCardIn 0.42s var(--ease-out) both;
    animation-delay: calc(var(--fin-card-delay, 0) * 60ms + 80ms);
}}
.fin-card-head {{
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 12px; direction: rtl; gap: 8px;
}}
.fin-card-collapsible:not(.open) .fin-card-head {{ margin-bottom: 0; }}
.fin-card-toggle {{
    width: 100%; background: none; border: none; cursor: pointer;
    padding: 0; font-family: 'Vazirmatn', sans-serif; color: inherit;
    text-align: inherit;
}}
.fin-card-toggle:active {{ opacity: 0.75; }}
.fin-card-toggle-grow {{
    flex: 1; min-width: 0; width: auto;
    display: flex; align-items: center; justify-content: space-between;
}}
.fin-card-head-end {{ display: flex; align-items: center; gap: 8px; }}
.fin-card-chevron {{ color: var(--text-muted); }}
.fin-card-title {{
    display: flex; align-items: center; gap: 8px;
    font-size: 14px; font-weight: bold;
}}
.fin-card-badge {{
    background: rgba(77, 217, 128, 0.1); color: #4DD980;
    font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 10px;
    border: 1px solid rgba(77, 217, 128, 0.18);
    font-variant-numeric: tabular-nums;
}}
.fin-card-actions {{ display: flex; gap: 6px; flex-shrink: 0; }}

.fin-chip-btn {{
    background: var(--surface-muted); border: 1px solid var(--divider);
    color: var(--text-muted); padding: 4px 10px; border-radius: 14px;
    font-size: 11px; cursor: pointer; font-family: 'Vazirmatn', sans-serif;
    transition: background var(--duration-fast), border-color var(--duration-fast);
}}
.fin-chip-btn.primary {{
    background: rgba(77, 217, 128, 0.12); color: #4DD980;
    border-color: rgba(77, 217, 128, 0.28);
}}

.fin-empty {{
    text-align: center; padding: 24px 12px; color: var(--text-muted);
}}
.fin-empty .fin-icon-lg {{ display: flex; margin: 0 auto 12px; }}
.fin-empty p {{ font-size: 12px; margin-bottom: 14px; line-height: 1.7; }}
.fin-empty-btn {{
    background: linear-gradient(135deg, #059669, #4DD980);
    color: #fff; border: none;
    padding: 10px 20px; border-radius: 14px; font-size: 12px; font-weight: 600;
    cursor: pointer; font-family: 'Vazirmatn', sans-serif;
    box-shadow: 0 4px 16px rgba(77, 217, 128, 0.28);
    transition: transform var(--duration-fast);
}}
.fin-empty-btn:active {{ transform: scale(0.96); }}

/* donut chart */
.fin-donut-wrap {{
    display: flex; align-items: center; gap: 16px; direction: rtl;
    padding: 4px 0;
}}
.fin-donut-chart {{
    width: 96px; height: 96px; border-radius: 50%; flex-shrink: 0;
    position: relative;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    animation: finDonutIn 0.6s var(--ease-out) both;
}}
.fin-donut-hole {{
    position: absolute; inset: 22%;
    background: var(--surface);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.12);
}}
.fin-donut-total-lbl {{
    font-size: 8px; color: var(--text-muted); font-weight: 600; text-align: center;
}}
.fin-donut-legend {{ flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 6px; }}
.fin-donut-legend-item {{
    display: flex; align-items: center; gap: 6px; font-size: 11px;
}}
.fin-donut-dot {{
    width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
    box-shadow: 0 0 6px currentColor;
}}
.fin-donut-cat {{ flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
.fin-donut-amt {{ font-weight: 700; font-variant-numeric: tabular-nums; color: var(--text-muted); }}

/* line chart */
.finance-line-chart {{ width: 100%; height: 140px; display: block; }}
.fin-chart-wrap {{
    margin: 0 -4px;
    background: rgba(0, 0, 0, 0.15);
    border-radius: 12px;
    padding: 8px 4px 4px;
    border: 1px solid rgba(255, 255, 255, 0.04);
}}
.fin-chart-grid {{ stroke: rgba(255, 255, 255, 0.06); stroke-width: 0.5; }}
.fin-chart-zero {{ stroke: rgba(129, 140, 248, 0.4); stroke-width: 1; stroke-dasharray: 4,3; }}
.fin-chart-area {{ opacity: 0.3; }}
.fin-chart-line {{ transition: opacity 0.3s; }}
.fin-chart-legend {{
    display: flex; justify-content: center; gap: 12px;
    font-size: 10px; color: var(--text-muted); margin-bottom: 10px; flex-wrap: wrap;
}}
.fin-legend-item {{ display: flex; align-items: center; gap: 4px; font-weight: 500; }}
.fin-legend-dot {{ width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }}
[data-theme="light"] .fin-chart-wrap {{ background: rgba(15, 46, 40, 0.03); border-color: rgba(15, 46, 40, 0.06); }}
[data-theme="light"] .fin-chart-grid {{ stroke: rgba(15, 46, 40, 0.08); }}

.fin-date-chip {{
    font-size: 11px; color: #4DD980; font-weight: 700;
    background: rgba(77, 217, 128, 0.1);
    border: 1px solid rgba(77, 217, 128, 0.18);
    padding: 4px 12px; border-radius: 999px; display: inline-block;
    margin: 10px 0 6px; direction: rtl;
}}
.fin-txn-list {{ padding-top: 4px; }}
.fin-txn {{
    display: flex; align-items: center; gap: 10px;
    padding: 11px 12px; margin-bottom: 6px;
    background: var(--surface-muted);
    border: 1px solid var(--divider);
    border-radius: 14px;
    direction: rtl;
    animation: finTxnIn 0.35s var(--ease-out) both;
    animation-delay: calc(var(--fin-stagger, 0) * 35ms);
    transition: transform var(--duration-fast), border-color var(--duration-fast);
}}
.fin-txn:active {{ transform: scale(0.985); }}
.fin-txn-icon {{
    width: 38px; height: 38px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; font-weight: bold; flex-shrink: 0;
}}
.fin-txn.income .fin-txn-icon {{ background: rgba(77,217,128,0.15); color: #4DD980; border: 1px solid rgba(77,217,128,0.25); }}
.fin-txn.expense .fin-txn-icon {{ background: rgba(255,115,89,0.15); color: #FF7359; border: 1px solid rgba(255,115,89,0.25); }}
.fin-txn.investment .fin-txn-icon {{ background: rgba(255,176,32,0.15); color: #FFB020; border: 1px solid rgba(255,176,32,0.25); }}
.fin-txn.income {{ border-right: 3px solid #4DD980; }}
.fin-txn.expense {{ border-right: 3px solid #FF7359; }}
.fin-txn.investment {{ border-right: 3px solid #FFB020; }}
.fin-txn-body {{ flex: 1; min-width: 0; }}
.fin-txn-title {{ font-size: 14px; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
.fin-txn-meta {{ font-size: 11px; color: var(--text-muted); margin-top: 3px; }}
.fin-txn-cat {{ display: inline-flex; align-items: center; gap: 4px; opacity: 0.95; }}
.fin-txn-cat .fin-icon {{ width: 20px; height: 20px; font-size: 11px; border-radius: 6px; }}
.fin-txn-right {{ text-align: left; flex-shrink: 0; }}
.fin-txn-amount {{ font-size: 14px; font-weight: 800; font-variant-numeric: tabular-nums; }}
.fin-txn.income .fin-txn-amount {{ color: #4DD980; }}
.fin-txn.expense .fin-txn-amount {{ color: #FF7359; }}
.fin-txn.investment .fin-txn-amount {{ color: #FFB020; }}
.fin-txn-tag {{
    font-size: 10px; background: rgba(255,176,32,0.15); color: #FFB020;
    padding: 1px 6px; border-radius: 8px;
}}
.fin-txn-btns {{ display: flex; gap: 2px; justify-content: flex-end; margin-top: 3px; }}
.fin-txn-btn {{
    background: none; border: none; color: var(--text-muted);
    font-size: 14px; cursor: pointer; padding: 3px 6px; border-radius: 8px;
    transition: background var(--duration-fast), color var(--duration-fast);
}}
.fin-txn-btn.del {{ color: #FF595988; }}
.fin-txn-btn:active {{ background: var(--surface); }}

.fin-budget-item {{
    padding: 12px 0; border-bottom: 1px solid var(--surface-muted);
    animation: finTxnIn 0.35s var(--ease-out) both;
    animation-delay: calc(var(--fin-stagger, 0) * 40ms);
}}
.fin-budget-item:last-child {{ border-bottom: none; }}
.fin-budget-item.over {{
    background: rgba(255,89,89,0.05); margin: 0 -8px; padding: 12px 8px;
    border-radius: 12px; border: 1px solid rgba(255,89,89,0.12);
}}
.fin-budget-top {{ display: flex; align-items: center; gap: 8px; direction: rtl; }}
.fin-budget-icon {{ flex-shrink: 0; line-height: 0; }}
.fin-budget-icon .fin-icon {{ width: 34px; height: 34px; font-size: 16px; border-radius: 11px; }}
.fin-budget-info {{ flex: 1; min-width: 0; }}
.fin-budget-name {{ font-size: 13px; font-weight: 700; }}
.fin-budget-sub {{ font-size: 11px; color: var(--text-muted); margin-top: 2px; }}
.fin-budget-pct {{ font-size: 12px; font-weight: bold; color: var(--primary); min-width: 32px; text-align: center; }}
.fin-budget-ring {{
    width: 38px; height: 38px; border-radius: 50%; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    background: conic-gradient(
        var(--fin-budget-color, #4DD980) 0 calc(var(--fin-budget-pct, 0) * 1%),
        var(--surface-muted) calc(var(--fin-budget-pct, 0) * 1%) 100%
    );
    font-size: 9px; font-weight: 800; color: var(--text);
}}
.fin-budget-ring span {{
    width: 28px; height: 28px; border-radius: 50%;
    background: var(--surface);
    display: flex; align-items: center; justify-content: center;
    font-variant-numeric: tabular-nums;
}}
.fin-budget-item.over .fin-budget-pct {{ color: var(--error); }}
.fin-budget-track {{
    height: 6px; border-radius: 999px; background: var(--surface-muted);
    overflow: hidden; margin-top: 10px;
}}
.fin-budget-fill {{
    height: 100%; border-radius: 999px;
    background: linear-gradient(90deg, #059669, #4DD980);
    transition: width 0.5s var(--ease-out);
    box-shadow: 0 0 8px rgba(77, 217, 128, 0.3);
}}
.fin-budget-fill.over {{
    background: linear-gradient(90deg, #FF7359, var(--error));
    box-shadow: 0 0 8px rgba(255, 115, 89, 0.3);
}}
.fin-budget-empty {{ font-size: 11px; color: var(--text-muted); margin-top: 8px; }}
.fin-budget-empty a {{ color: #4DD980; font-weight: 600; }}
.fin-budget-warn {{
    font-size: 10px; color: var(--error); margin-top: 6px; font-weight: 600;
    display: flex; align-items: center; gap: 4px;
}}

.fin-daily-table {{
    direction: rtl;
    background: var(--surface-muted);
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid var(--divider);
}}
.fin-daily-head, .fin-daily-row {{
    display: grid; grid-template-columns: 1.1fr 0.9fr 0.9fr 0.9fr 0.9fr;
    gap: 4px; padding: 8px 10px; font-size: 10px; align-items: center;
}}
.fin-daily-head {{
    color: var(--text-muted); background: rgba(0,0,0,0.15);
    font-weight: 700; font-size: 9px; text-transform: uppercase; letter-spacing: 0.03em;
}}
.fin-daily-row {{
    border-bottom: 1px solid var(--surface-muted);
    animation: finTxnIn 0.3s var(--ease-out) both;
    animation-delay: calc(var(--fin-stagger, 0) * 25ms);
    transition: background var(--duration-fast);
}}
.fin-daily-row:nth-child(even) {{ background: rgba(255,255,255,0.02); }}
.fin-daily-row:last-child {{ border-bottom: none; }}
.fin-daily-date {{ color: var(--text-muted); font-weight: 500; }}
.fin-daily-inc {{ color: #4DD980; font-variant-numeric: tabular-nums; font-weight: 600; }}
.fin-daily-exp {{ color: #FF7359; font-variant-numeric: tabular-nums; font-weight: 600; }}
.fin-daily-inv {{ color: #FFB020; font-variant-numeric: tabular-nums; font-weight: 600; }}
.fin-daily-net {{ font-weight: 800; font-variant-numeric: tabular-nums; }}
.fin-daily-net.pos {{ color: #4DD980; }}
.fin-daily-net.neg {{ color: #FF7359; }}
[data-theme="light"] .fin-daily-head {{ background: rgba(15, 46, 40, 0.04); }}
[data-theme="light"] .fin-daily-row:nth-child(even) {{ background: rgba(15, 46, 40, 0.02); }}
[data-theme="light"] .fin-card-badge {{ background: rgba(15, 46, 40, 0.06); color: #0F2E28; border-color: rgba(15, 46, 40, 0.1); }}
[data-theme="light"] .fin-chip-btn.primary {{ background: rgba(15, 46, 40, 0.08); color: #0F2E28; border-color: rgba(15, 46, 40, 0.14); }}

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
@keyframes homeOrbFloat {{
    0%, 100% {{ transform: translate(0, 0) scale(1); }}
    50% {{ transform: translate(8px, -10px) scale(1.05); }}
}}
@keyframes homeSunPulse {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50% {{ opacity: 0.75; transform: scale(1.08); }}
}}
@keyframes homeLivePulse {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50% {{ opacity: 0.55; transform: scale(0.85); }}
}}
@keyframes homeEffGlow {{
    0%, 100% {{ opacity: 0.6; transform: scale(1); }}
    50% {{ opacity: 1; transform: scale(1.06); }}
}}
@keyframes homePanelIn {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes homeBodyIn {{
    from {{ opacity: 0; transform: translateY(6px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes homeTaskIn {{
    from {{ opacity: 0; transform: translateY(12px) scale(0.98); }}
    to {{ opacity: 1; transform: translateY(0) scale(1); }}
}}
@keyframes homeFabIn {{
    from {{ opacity: 0; transform: scale(0.7); }}
    to {{ opacity: 1; transform: scale(1); }}
}}
@keyframes homeEmptyRing {{
    0%, 100% {{ transform: scale(1); opacity: 0.6; }}
    50% {{ transform: scale(1.04); opacity: 1; }}
}}
@keyframes finOrbFloat {{
    0%, 100% {{ transform: translate(0, 0) scale(1); }}
    50% {{ transform: translate(6px, -8px) scale(1.04); }}
}}
@keyframes finGlowPulse {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50% {{ opacity: 0.7; transform: scale(1.06); }}
}}
@keyframes finLivePulse {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50% {{ opacity: 0.55; transform: scale(0.85); }}
}}
@keyframes finRingGlow {{
    0%, 100% {{ opacity: 0.5; transform: scale(1); }}
    50% {{ opacity: 1; transform: scale(1.05); }}
}}
@keyframes finPanelIn {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes finBodyIn {{
    from {{ opacity: 0; transform: translateY(6px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes finCardIn {{
    from {{ opacity: 0; transform: translateY(14px) scale(0.98); }}
    to {{ opacity: 1; transform: translateY(0) scale(1); }}
}}
@keyframes finTxnIn {{
    from {{ opacity: 0; transform: translateX(8px); }}
    to {{ opacity: 1; transform: translateX(0); }}
}}
@keyframes finDonutIn {{
    from {{ opacity: 0; transform: rotate(-30deg) scale(0.85); }}
    to {{ opacity: 1; transform: rotate(0) scale(1); }}
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
    .home-orb, .home-today-dot, .home-running-dot, .home-eff-glow,
    .home-empty-ring, .home-header::after {{ animation: none; }}
    .home-hero-panel, .home-body, .home-task-card, .home-fab, .home-empty {{ animation: none; }}
    .fin-orb, .fin-month-dot, .fin-header::after, .fin-ring-glow,
    .fin-hero-panel, .fin-body, .fin-card-animate, .fin-txn, .fin-budget-item,
    .fin-daily-row, .fin-inst-row, .fin-donut-chart {{ animation: none; }}
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

/* ── Tracking screen ── */
.track-page {{ padding-bottom: 16px; }}

.track-header {{
    background: linear-gradient(155deg, #0A1F22 0%, #0F2A2E 35%, #134E4A 70%, #0C2328 100%);
    overflow: hidden;
    gap: 0;
    padding: calc(10px + var(--safe-top)) var(--space-4) 8px;
}}
.track-header::before {{
    background:
        radial-gradient(ellipse 70% 55% at 90% 8%, rgba(45, 212, 191, 0.28), transparent 58%),
        radial-gradient(ellipse 50% 40% at 8% 92%, rgba(129, 140, 248, 0.14), transparent 55%);
}}
.track-header-orbs {{
    position: absolute; inset: 0; pointer-events: none; overflow: hidden;
}}
.track-orb {{
    position: absolute; border-radius: 50%; filter: blur(40px); opacity: 0.55;
    animation: trackOrbFloat 8s ease-in-out infinite;
}}
.track-orb-1 {{
    width: 120px; height: 120px; top: -30px; right: -20px;
    background: rgba(45, 212, 191, 0.35);
}}
.track-orb-2 {{
    width: 90px; height: 90px; bottom: 10px; left: -10px;
    background: rgba(129, 140, 248, 0.25); animation-delay: -3s;
}}
.track-orb-3 {{
    width: 60px; height: 60px; top: 40%; left: 45%;
    background: rgba(52, 211, 153, 0.2); animation-delay: -5s;
}}
@keyframes trackOrbFloat {{
    0%, 100% {{ transform: translate(0, 0) scale(1); }}
    50% {{ transform: translate(6px, -8px) scale(1.06); }}
}}
.track-header-top {{
    display: flex; align-items: center; gap: 8px; direction: rtl;
    position: relative; z-index: 1; margin-bottom: 2px;
}}
.track-header-title {{
    font-size: 16px; font-weight: bold; color: #fff; flex: 1;
}}
.track-live-badge {{
    display: inline-flex; align-items: center; gap: 5px;
    font-size: 10px; font-weight: 600; color: #5EEAD4;
    background: rgba(45, 212, 191, 0.12);
    border: 1px solid rgba(45, 212, 191, 0.3);
    border-radius: 999px; padding: 3px 10px 3px 8px;
}}
.track-live-dot {{
    width: 6px; height: 6px; border-radius: 50%;
    background: #2DD4BF; box-shadow: 0 0 8px #2DD4BF;
    animation: trackLivePulse 1.4s ease-in-out infinite;
}}
@keyframes trackLivePulse {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50% {{ opacity: 0.5; transform: scale(0.85); }}
}}
.track-date-label {{
    text-align: center; font-size: 12px;
    color: rgba(255, 255, 255, 0.55);
    padding: 0 0 8px; position: relative; z-index: 1;
}}
.track-date-inline {{
    text-align: unset; font-size: 11px;
    padding: 0; margin-right: auto; flex-shrink: 0;
}}
.track-hero-in-header {{
    margin: 4px 0 0;
    padding: 0;
    position: relative; z-index: 1;
}}
.track-hero-summary {{ text-align: center; }}
.track-hero-label {{
    font-size: 11px; color: rgba(255, 255, 255, 0.6); margin-bottom: 2px;
    letter-spacing: 0.3px;
}}
.track-hero-total {{
    font-size: 30px; font-weight: 800; color: #5EEAD4;
    font-variant-numeric: tabular-nums; letter-spacing: 1px; line-height: 1.05;
    text-shadow: 0 0 24px rgba(45, 212, 191, 0.35);
}}
.track-hero-range {{
    font-size: 11px; color: rgba(255, 255, 255, 0.5); margin-top: 4px;
}}
.track-timer-wrap {{
    display: flex; justify-content: center; padding: 0 0 6px;
    position: relative;
}}
.track-timer-glow {{
    position: absolute; width: 154px; height: 154px; border-radius: 50%;
    background: radial-gradient(circle, rgba(45, 212, 191, 0.2), transparent 70%);
    animation: trackPulse 2.4s ease-in-out infinite;
}}
.track-timer-ring {{
    width: 150px; height: 150px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    position: relative;
}}
.track-timer-svg {{
    position: absolute; inset: 0; width: 100%; height: 100%;
    animation: trackRingSpin 12s linear infinite;
}}
.track-timer-progress {{
    animation: trackRingDash 3s ease-in-out infinite;
}}
@keyframes trackRingSpin {{
    from {{ transform: rotate(0deg); }}
    to {{ transform: rotate(360deg); }}
}}
@keyframes trackRingDash {{
    0%, 100% {{ stroke-dasharray: 80 436; opacity: 0.85; }}
    50% {{ stroke-dasharray: 160 356; opacity: 1; }}
}}
@keyframes trackPulse {{
    0%, 100% {{ transform: scale(1); opacity: 1; }}
    50% {{ transform: scale(1.05); opacity: 0.85; }}
}}
.track-timer-inner {{
    width: 124px; height: 124px; border-radius: 50%;
    background: rgba(8, 12, 14, 0.88);
    border: 1px solid rgba(45, 212, 191, 0.22);
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: 2px; position: relative; z-index: 1;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255,255,255,0.05);
}}
.track-timer-lbl {{
    font-size: 10px; color: rgba(255, 255, 255, 0.5);
}}
.track-timer-val {{
    font-size: 26px; font-weight: 800; color: #5EEAD4;
    font-variant-numeric: tabular-nums; letter-spacing: 1px;
    text-shadow: 0 0 16px rgba(45, 212, 191, 0.3);
}}
.track-hero-stats {{
    display: flex; gap: 5px; direction: rtl;
}}
.track-hero-stat {{
    flex: 1; display: flex; align-items: center; gap: 6px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(45, 212, 191, 0.12);
    border-radius: 10px; padding: 7px 8px;
    transition: border-color var(--duration-fast);
}}
.track-hero-stat .fin-emoji {{ flex-shrink: 0; }}
.track-stat-lbl {{
    display: block; font-size: 10px; color: rgba(255, 255, 255, 0.5);
}}
.track-stat-val {{
    display: block; font-size: 12px; font-weight: bold;
    color: #fff; font-variant-numeric: tabular-nums;
}}

/* active session panel */
.track-active-panel {{
    margin: 12px 12px 0; padding: 14px;
    background: linear-gradient(145deg, rgba(45, 212, 191, 0.08), rgba(99, 102, 241, 0.06));
    border: 1px solid rgba(45, 212, 191, 0.22);
    border-radius: 16px; direction: rtl;
    animation: trackSlideUp 0.35s ease both;
    box-shadow: 0 4px 20px rgba(45, 212, 191, 0.08);
}}
.track-header .track-active-panel.track-active-in-header {{
    margin: 10px 0 0; padding: 10px 0 0;
    background: none; border: none; border-radius: 0;
    border-top: 1px solid rgba(45, 212, 191, 0.2);
    box-shadow: none; animation: none;
}}
.track-header .track-stats-panel.track-stats-in-header {{
    margin: 8px 0 0; padding: 8px 0 0;
    background: none; border: none; border-radius: 0;
    border-top: 1px solid rgba(45, 212, 191, 0.2);
    box-shadow: none; animation: none;
    gap: 10px;
}}
.track-header .track-eff-gauge {{
    width: 76px; height: 76px;
}}
.track-header .track-eff-gauge .track-donut {{
    width: 100%; height: 100%;
}}
.track-header .track-eff-gauge-val {{ font-size: 16px; }}
.track-header .track-stat-card {{
    background: rgba(255, 255, 255, 0.06);
    border-color: rgba(45, 212, 191, 0.15);
    padding: 6px 8px;
}}
.track-header .track-stats-grid {{ gap: 4px; }}
.track-header .track-active-panel-head {{
    margin-bottom: 8px; gap: 10px;
}}
.track-header .track-active-emoji {{
    width: 38px; height: 38px; border-radius: 12px; font-size: 18px;
}}
.track-header .track-label-input-prominent {{
    padding: 10px 12px !important;
}}
.track-header .track-pick-btn-lg {{ min-height: 40px !important; }}
.track-header .track-stat-card-lbl {{ color: rgba(255, 255, 255, 0.55); }}
.track-header .track-stat-card-val {{ color: #fff; }}
.track-header .track-stat-card.useful .track-stat-card-val {{ color: #6EE7B7; }}
.track-header .track-stat-card.not .track-stat-card-val {{ color: #FDBA74; }}
.track-header .track-eff-gauge-val {{ color: #6EE7B7; }}
.track-header .track-eff-gauge-lbl {{ color: rgba(255, 255, 255, 0.55); }}
.track-header .track-active-title {{ color: #fff; }}
.track-header .track-active-since {{ color: rgba(255, 255, 255, 0.55); }}
.track-header .track-label-input-prominent {{
    background: rgba(8, 12, 14, 0.55) !important;
    border-color: rgba(45, 212, 191, 0.28) !important;
    color: #fff !important;
}}
.track-header .track-label-input-prominent::placeholder {{ color: rgba(255, 255, 255, 0.4); }}
.track-header .track-pick-btn-lg {{
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(45, 212, 191, 0.25);
    color: #5EEAD4;
}}
@keyframes trackSlideUp {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
.track-active-panel-head {{
    display: flex; align-items: center; gap: 12px; margin-bottom: 12px;
}}
.track-active-emoji {{
    width: 44px; height: 44px; border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px; flex-shrink: 0;
    background: color-mix(in srgb, var(--avatar-color, #2DD4BF) 18%, transparent);
    border: 1px solid color-mix(in srgb, var(--avatar-color, #2DD4BF) 35%, transparent);
    box-shadow: 0 4px 12px color-mix(in srgb, var(--avatar-color, #2DD4BF) 15%, transparent);
}}
.track-active-meta {{ flex: 1; min-width: 0; }}
.track-active-title {{
    display: block; font-size: 15px; font-weight: 700; color: var(--text);
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}}
.track-active-since {{
    display: block; font-size: 11px; color: var(--text-muted); margin-top: 2px;
    font-variant-numeric: tabular-nums;
}}
.track-active-label-row {{ margin-top: 0; }}
.track-label-input-prominent {{
    font-size: 14px !important; padding: 12px 14px !important;
    background: var(--surface) !important;
    border-color: rgba(45, 212, 191, 0.3) !important;
}}
.track-pick-btn-lg {{ min-height: 44px !important; padding: 0 14px !important; }}

.track-actions {{
    display: flex; flex-direction: column; gap: 8px;
    padding: 12px 12px 0; direction: rtl;
}}
.track-actions-secondary {{
    display: flex; gap: 8px;
}}
.track-btn {{
    border: none; border-radius: 14px; font-family: inherit;
    font-size: 14px; font-weight: 600; cursor: pointer;
    display: flex; align-items: center; justify-content: center; gap: 8px;
    padding: 14px 16px;
    transition: transform var(--duration-fast), box-shadow var(--duration-fast), opacity var(--duration-fast);
}}
.track-btn:active {{ transform: scale(0.97); }}
.track-btn-switch {{
    width: 100%;
    background: linear-gradient(135deg, #0D9488 0%, #2DD4BF 50%, #14B8A6 100%);
    color: #fff;
    box-shadow: 0 6px 24px rgba(45, 212, 191, 0.3), inset 0 1px 0 rgba(255,255,255,0.15);
}}
.track-btn-icon {{ font-size: 18px; line-height: 1; }}
.track-btn-stop {{
    flex: 1;
    background: rgba(251, 113, 133, 0.1);
    color: #FB7185;
    border: 1px solid rgba(251, 113, 133, 0.35);
}}
.track-btn-delete {{
    flex: 1;
    background: var(--error-bg);
    color: var(--error);
    border: 1px solid rgba(251, 113, 133, 0.25);
}}

/* stats & efficiency */
.track-stats-panel {{
    margin: 14px 12px 0; padding: 14px;
    background: var(--surface);
    border: 1px solid var(--divider);
    border-radius: 16px; direction: rtl;
    display: flex; align-items: center; gap: 14px;
    animation: trackSlideUp 0.4s ease both;
}}
.track-eff-gauge {{
    position: relative; flex-shrink: 0;
    width: 88px; height: 88px;
}}
.track-eff-gauge-center {{
    position: absolute; inset: 0;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
}}
.track-eff-gauge-val {{
    font-size: 18px; font-weight: 800; color: var(--success);
    font-variant-numeric: tabular-nums; line-height: 1;
}}
.track-eff-gauge-lbl {{
    font-size: 9px; color: var(--text-muted); margin-top: 2px;
}}
.track-stats-grid {{
    flex: 1; display: flex; flex-direction: column; gap: 6px; min-width: 0;
}}
.track-stat-card {{
    display: flex; align-items: center; gap: 8px;
    padding: 8px 10px; border-radius: 10px;
    background: var(--surface-muted); border: 1px solid var(--divider);
}}
.track-stat-card.useful {{ border-color: rgba(52, 211, 153, 0.25); }}
.track-stat-card.not {{ border-color: rgba(251, 146, 60, 0.25); }}
.track-stat-card .fin-emoji {{ flex-shrink: 0; }}
.track-stat-card-lbl {{
    display: block; font-size: 10px; color: var(--text-muted);
}}
.track-stat-card-val {{
    display: block; font-size: 13px; font-weight: 700;
    color: var(--text); font-variant-numeric: tabular-nums;
}}
.track-stat-card.useful .track-stat-card-val {{ color: var(--success); }}
.track-stat-card.not .track-stat-card-val {{ color: var(--warning); }}

.track-sec-title::before {{ display: none; }}
.track-sec-title .fin-emoji {{ opacity: 0.9; }}

.track-section {{ padding: 16px 12px 0; }}
.track-section .track-sec-title {{ margin-bottom: 12px; }}

/* timeline */
.track-timeline {{
    display: flex; flex-direction: column; gap: 0;
    position: relative; padding-right: 20px;
}}
.track-timeline::before {{
    content: '';
    position: absolute; right: 7px; top: 8px; bottom: 8px;
    width: 2px;
    background: linear-gradient(180deg, var(--running) 0%, var(--divider) 40%, transparent 100%);
    border-radius: 1px; opacity: 0.5;
}}
.track-interval {{
    display: flex; gap: 0; direction: rtl;
    position: relative;
    animation: trackFadeIn 0.35s ease both;
    animation-delay: calc(var(--track-stagger, 0) * 45ms);
    padding-right: 4px;
}}
@keyframes trackFadeIn {{
    from {{ opacity: 0; transform: translateX(8px); }}
    to {{ opacity: 1; transform: translateX(0); }}
}}
.track-timeline-node {{
    position: absolute; right: -20px; top: 18px;
    width: 16px; height: 16px;
    display: flex; align-items: center; justify-content: center;
    z-index: 1;
}}
.track-timeline-dot {{
    width: 10px; height: 10px; border-radius: 50%;
    background: var(--node-color, var(--running));
    border: 2px solid var(--surface);
    box-shadow: 0 0 0 2px color-mix(in srgb, var(--node-color, var(--running)) 30%, transparent);
}}
.track-interval.is-active .track-timeline-dot {{
    animation: trackLivePulse 1.4s ease-in-out infinite;
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--node-color) 25%, transparent),
                0 0 12px color-mix(in srgb, var(--node-color) 40%, transparent);
}}
.track-interval-card {{
    flex: 1; display: flex; gap: 0;
    background: var(--surface);
    border-radius: 14px; border: 1px solid var(--divider);
    overflow: hidden; margin-bottom: 10px;
    transition: border-color var(--duration-fast), box-shadow var(--duration-fast);
}}
.track-interval.is-open .track-interval-card {{
    overflow: visible; border-color: rgba(45, 212, 191, 0.25);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    position: relative; z-index: 2;
}}
.track-interval.is-active .track-interval-card {{
    border-color: rgba(45, 212, 191, 0.35);
    box-shadow: 0 0 0 1px rgba(45, 212, 191, 0.15), 0 4px 16px rgba(45, 212, 191, 0.1);
}}
.track-interval.is-useful .track-interval-card {{
    box-shadow: inset -3px 0 0 0 var(--success);
}}
.track-interval.is-not-useful .track-interval-card {{
    box-shadow: inset -3px 0 0 0 var(--error);
}}
.track-useful-row {{
    display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 10px;
}}
.track-chip {{
    font-size: 12px !important; padding: 6px 12px !important;
    border-radius: 999px !important; display: inline-flex !important;
    align-items: center; gap: 4px;
    transition: transform var(--duration-fast), background var(--duration-fast);
}}
.track-chip:active {{ transform: scale(0.96); }}
.track-interval-accent {{
    width: 4px; flex-shrink: 0;
}}
.track-interval-body {{
    flex: 1; min-width: 0;
}}
.track-interval-header {{
    display: flex; align-items: center; justify-content: space-between;
    gap: 10px; width: 100%; padding: 12px 14px;
    background: none; border: none; cursor: pointer;
    font-family: inherit; color: inherit; text-align: start;
    direction: rtl; box-sizing: border-box;
}}
.track-interval-header:active {{ background: var(--surface-muted); }}
.track-interval-avatar {{
    width: 36px; height: 36px; border-radius: 11px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
    background: color-mix(in srgb, var(--avatar-color, #2DD4BF) 15%, var(--surface-muted));
    border: 1px solid color-mix(in srgb, var(--avatar-color, #2DD4BF) 25%, transparent);
}}
.track-interval-header-main {{
    flex: 1; min-width: 0; display: flex; flex-direction: column;
    gap: 2px; align-items: flex-start;
}}
.track-interval-time-compact {{
    font-size: 11px; color: var(--text-muted);
    font-variant-numeric: tabular-nums;
}}
.track-interval-detail {{
    padding: 0 14px 14px;
    border-top: 1px solid var(--divider);
    direction: rtl; overflow: visible;
}}
.track-interval.is-open .track-interval-header {{
    padding-bottom: 10px;
}}
.track-interval-header .collapse-chevron {{
    color: var(--text-muted); opacity: 0.7;
    width: 14px; height: 14px; flex-shrink: 0;
    transition: transform var(--duration-fast);
}}
.track-interval.is-open .collapse-chevron {{
    transform: rotate(180deg);
}}
.track-interval-top-end {{
    display: flex; align-items: center; gap: 6px; flex-shrink: 0;
}}
.track-interval-del {{
    width: 28px; height: 28px; border: none; border-radius: 8px;
    background: transparent; color: #FF595988;
    font-size: 18px; line-height: 1; cursor: pointer; padding: 0;
    display: inline-flex; align-items: center; justify-content: center;
    transition: background var(--duration-fast), color var(--duration-fast);
}}
.track-interval-del:active {{ background: var(--error-bg); color: var(--error); }}
.track-interval-label {{
    font-size: 14px; font-weight: 600; color: var(--text);
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}}
.track-interval-dur {{
    font-size: 12px; font-weight: 700; color: var(--running);
    font-variant-numeric: tabular-nums; flex-shrink: 0;
    background: var(--running-bg); padding: 3px 9px; border-radius: 8px;
}}
.track-interval-live {{
    font-size: 10px; font-weight: 700; color: #2DD4BF;
    background: rgba(45, 212, 191, 0.12); padding: 3px 8px;
    border-radius: 999px; border: 1px solid rgba(45, 212, 191, 0.3);
    animation: trackLivePulse 1.4s ease-in-out infinite;
}}
.track-interval-pct {{
    font-size: 10px; font-weight: 600; color: var(--text-muted);
    background: var(--surface-muted); padding: 2px 7px; border-radius: 6px;
}}
.track-interval-time {{
    font-size: 11px; color: var(--text-muted); margin: 10px 0 8px;
    font-variant-numeric: tabular-nums;
}}
.track-interval-bar {{
    height: 6px; border-radius: 3px; background: var(--surface-muted);
    overflow: hidden; margin-bottom: 4px;
}}
.track-interval-bar-fill {{
    height: 100%; border-radius: 3px;
    transition: width var(--duration-normal);
    box-shadow: 0 0 8px color-mix(in srgb, currentColor 30%, transparent);
}}
.track-interval-pct-row {{
    display: flex; justify-content: space-between;
    font-size: 10px; color: var(--text-muted); margin-bottom: 10px;
}}
.track-label-row {{
    display: flex; align-items: stretch; gap: 8px; direction: rtl;
}}
.track-label-wrap {{
    position: relative; flex: 1; min-width: 0;
}}
.track-label-suggestions {{
    display: none; position: absolute; top: calc(100% + 4px);
    left: 0; right: 0; z-index: 40;
    background: var(--surface); border: 1px solid var(--divider);
    border-radius: 12px; box-shadow: var(--elevation-2);
    max-height: 200px; overflow-y: auto; -webkit-overflow-scrolling: touch;
    direction: rtl;
}}
.track-label-sug-item {{
    display: flex; align-items: center; gap: 8px; width: 100%;
    padding: 10px 12px; border: none; background: none;
    cursor: pointer; font-family: inherit; font-size: 13px;
    color: var(--text); text-align: start; direction: rtl;
    transition: background var(--duration-fast);
}}
.track-label-sug-item + .track-label-sug-item {{
    border-top: 1px solid var(--divider);
}}
.track-label-sug-item:active {{ background: var(--surface-muted); }}
.track-label-sug-text {{ flex: 1; min-width: 0; }}
.track-label-input {{
    width: 100%; box-sizing: border-box;
    background: var(--surface-muted);
    border: 1px solid var(--divider); border-radius: 10px;
    color: var(--text); font-family: inherit; font-size: 13px;
    padding: 10px 12px; outline: none; direction: rtl;
    transition: border-color var(--duration-fast), box-shadow var(--duration-fast);
}}
.track-label-input:focus {{
    border-color: var(--running);
    box-shadow: 0 0 0 3px rgba(45, 212, 191, 0.12);
}}
.track-label-input::placeholder {{ color: var(--text-muted); }}
.track-pick-btn {{
    flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center;
    gap: 4px; background: rgba(45, 212, 191, 0.12);
    border: 1px solid rgba(45, 212, 191, 0.35); color: var(--running);
    border-radius: 10px; padding: 0 12px; min-height: 40px;
    font-family: inherit; font-size: 12px; font-weight: 600; cursor: pointer;
    transition: background var(--duration-fast), transform var(--duration-fast);
}}
.track-pick-btn:active {{ background: rgba(45, 212, 191, 0.22); transform: scale(0.98); }}
.track-pick-btn .fin-emoji {{ flex-shrink: 0; }}

/* breakdown */
.track-breakdown-section {{ padding-top: 14px; }}
.track-breakdown-card {{
    background: var(--surface); border: 1px solid var(--divider);
    border-radius: 16px; padding: 14px;
    animation: trackSlideUp 0.45s ease both;
}}
.track-breakdown-visual {{
    margin-bottom: 14px;
}}
.track-breakdown-bar {{
    display: flex; height: 10px; border-radius: 5px; overflow: hidden;
    background: var(--surface-muted); width: 100%;
}}
.track-breakdown-bar-lg {{ height: 12px; border-radius: 6px; }}
.track-breakdown-seg {{
    height: 100%; min-width: 4px;
    transition: width 0.6s cubic-bezier(0.34, 1.2, 0.64, 1);
}}
.track-breakdown-legend {{
    display: flex; flex-direction: column; gap: 10px;
}}
.track-legend-item {{
    display: grid; grid-template-columns: 10px 1fr auto;
    grid-template-rows: auto auto; gap: 2px 8px;
    align-items: center; font-size: 13px; direction: rtl;
    animation: trackFadeIn 0.4s ease both;
    animation-delay: calc(var(--track-stagger, 0) * 50ms);
}}
.track-legend-dot {{
    width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0;
    grid-row: 1 / 3;
}}
.track-legend-label {{
    font-weight: 600; color: var(--text);
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}}
.track-legend-bar-wrap {{
    grid-column: 2; height: 4px; border-radius: 2px;
    background: var(--surface-muted); overflow: hidden;
}}
.track-legend-bar {{
    display: block; height: 100%; border-radius: 2px;
    transition: width 0.6s cubic-bezier(0.34, 1.2, 0.64, 1);
}}
.track-legend-val {{
    font-size: 11px; color: var(--text-muted);
    font-variant-numeric: tabular-nums; white-space: nowrap;
}}
.track-donut-seg {{
    transition: stroke-dasharray 0.6s cubic-bezier(0.34, 1.2, 0.64, 1);
}}

/* empty state */
.track-empty-hero {{
    display: flex; justify-content: center; align-items: center;
    padding: 28px 0 8px; position: relative;
}}
.track-empty-rings {{
    position: absolute; width: 140px; height: 140px;
}}
.track-empty-rings span {{
    position: absolute; inset: 0; border-radius: 50%;
    border: 2px solid rgba(45, 212, 191, 0.15);
    animation: trackEmptyRing 3s ease-in-out infinite;
}}
.track-empty-rings span:nth-child(2) {{
    inset: 12px; animation-delay: -1s;
    border-color: rgba(129, 140, 248, 0.12);
}}
.track-empty-rings span:nth-child(3) {{
    inset: 24px; animation-delay: -2s;
    border-color: rgba(45, 212, 191, 0.2);
}}
@keyframes trackEmptyRing {{
    0%, 100% {{ transform: scale(1); opacity: 0.6; }}
    50% {{ transform: scale(1.08); opacity: 1; }}
}}
.track-empty-icon {{
    position: relative; z-index: 1;
    width: 72px; height: 72px; border-radius: 22px;
    display: flex; align-items: center; justify-content: center;
    background: linear-gradient(145deg, rgba(45, 212, 191, 0.15), rgba(99, 102, 241, 0.1));
    border: 1px solid rgba(45, 212, 191, 0.25);
    box-shadow: 0 8px 32px rgba(45, 212, 191, 0.12);
    font-size: 32px;
}}
.track-empty {{ padding-top: 16px; padding-bottom: 8px; }}
.track-empty .empty-title {{ font-size: 20px; }}
.track-start-btn {{
    margin-top: 20px;
    background: linear-gradient(135deg, #0D9488, #2DD4BF) !important;
    box-shadow: 0 6px 24px rgba(45, 212, 191, 0.3) !important;
}}
.track-features {{
    display: flex; gap: 8px; padding: 0 16px 12px; direction: rtl;
}}
.track-feature {{
    flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px;
    padding: 12px 8px; border-radius: 12px;
    background: var(--surface); border: 1px solid var(--divider);
    font-size: 11px; font-weight: 600; color: var(--text-muted);
    text-align: center;
}}
.track-feature-icon {{
    width: 32px; height: 32px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    background: rgba(45, 212, 191, 0.1);
}}
.track-tips {{ padding: 0 16px 16px; }}
.track-tip {{
    display: flex; align-items: flex-start; gap: 8px;
    padding: 12px 14px; background: var(--surface);
    border: 1px solid var(--divider); border-radius: 12px;
    font-size: 12px; color: var(--text-muted); line-height: 1.6;
}}
.track-tip .fin-emoji {{ flex-shrink: 0; }}
.track-restart-wrap {{ padding: 16px 12px 8px; text-align: center; }}
.track-restart-btn {{
    background: linear-gradient(135deg, rgba(45, 212, 191, 0.12), rgba(99, 102, 241, 0.08));
    border: 1px solid rgba(45, 212, 191, 0.3);
    color: var(--running); border-radius: 14px; padding: 14px 28px;
    font-family: inherit; font-size: 14px; font-weight: 600; cursor: pointer;
    display: inline-flex; align-items: center; justify-content: center; gap: 6px;
    transition: transform var(--duration-fast), box-shadow var(--duration-fast);
    box-shadow: 0 4px 16px rgba(45, 212, 191, 0.1);
}}
.track-restart-btn:active {{
    transform: scale(0.97);
    background: rgba(45, 212, 191, 0.18);
}}
.track-restart-plus {{
    display: inline-flex; align-items: center; justify-content: center;
    width: 18px; height: 18px; font-size: 16px; font-weight: 700;
    line-height: 1; flex-shrink: 0;
    background: rgba(45, 212, 191, 0.2); border-radius: 50%;
}}
.track-start-btn .ico,
.track-btn-stop .ico {{
    width: 16px; height: 16px; flex-shrink: 0;
}}

/* activity picker sheet */
.track-act-overlay {{
    position: fixed; inset: 0; background: rgba(0, 0, 0, 0.55);
    z-index: 500; display: flex; align-items: flex-end; justify-content: center;
    padding: 0 0 calc(var(--safe-bottom));
    overflow: hidden; touch-action: auto;
}}
body.kb-open .track-act-overlay {{
    padding-bottom: calc(var(--safe-bottom) + var(--keyboard-inset));
}}
.track-act-sheet {{
    width: 100%; max-width: 520px; background: var(--surface);
    border-radius: 20px 20px 0 0;
    padding: 8px 14px calc(14px + var(--safe-bottom));
    border-top: 1px solid rgba(45, 212, 191, 0.2);
    background-image: linear-gradient(180deg, rgba(45, 212, 191, 0.06) 0%, transparent 80px);
    animation: projSheetUp 0.25s ease;
    max-height: min(88dvh, calc(var(--visual-vh, 100dvh) - 12px));
    display: flex; flex-direction: column; direction: rtl;
}}
.track-act-handle {{
    width: 36px; height: 4px; background: var(--divider);
    border-radius: 2px; margin: 4px auto 10px; flex-shrink: 0;
}}
.track-act-title {{
    font-size: 15px; font-weight: bold; text-align: center;
    margin-bottom: 10px; flex-shrink: 0;
}}
.track-act-search {{
    width: 100%; background: var(--surface-muted);
    border: 1px solid var(--divider); border-radius: 12px;
    padding: 10px 12px; font-family: inherit; font-size: 14px;
    color: var(--text); margin-bottom: 10px; outline: none; flex-shrink: 0;
}}
.track-act-search:focus {{ border-color: var(--running); }}
.track-act-grid {{
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px;
    overflow-y: auto; -webkit-overflow-scrolling: touch;
    flex: 1; min-height: 0; padding-bottom: 8px;
}}
.track-act-item {{
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: 4px; min-height: 76px; padding: 8px 4px;
    background: var(--surface-muted); border: 1px solid var(--divider);
    border-radius: 14px; cursor: pointer; font-family: inherit;
    transition: background var(--duration-fast), border-color var(--duration-fast), transform var(--duration-fast), box-shadow var(--duration-fast);
}}
.track-act-item:active {{
    transform: scale(0.96);
    background: rgba(45, 212, 191, 0.12);
    border-color: rgba(45, 212, 191, 0.35);
    box-shadow: 0 4px 12px rgba(45, 212, 191, 0.12);
}}
.track-act-emoji {{
    font-size: 26px; line-height: 1;
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.15));
}}
.track-act-name {{
    font-size: 11px; color: var(--text); text-align: center;
    line-height: 1.3; max-width: 100%;
    overflow: hidden; text-overflow: ellipsis;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
}}
.track-act-empty {{
    grid-column: 1 / -1; text-align: center; padding: 24px 12px;
    color: var(--text-muted); font-size: 13px;
}}
.track-act-cancel {{
    display: block; width: 100%; margin-top: 6px; flex-shrink: 0;
    background: transparent; border: none; color: var(--text-muted);
    padding: 12px; font-family: inherit; font-size: 14px; cursor: pointer;
}}
[data-theme="light"] .track-pick-btn {{
    background: var(--running-bg); border-color: rgba(13, 148, 136, 0.25);
    color: var(--running);
}}
[data-theme="light"] .track-act-item:active {{
    background: var(--running-bg);
}}

[data-theme="light"] .track-header {{
    background: linear-gradient(155deg, #ECFDF5 0%, #F0FDFA 40%, #E0F2FE 100%);
    box-shadow: 0 2px 16px rgba(13, 148, 136, 0.08);
}}
[data-theme="light"] .track-orb {{ opacity: 0.35; }}
[data-theme="light"] .track-header-title {{ color: #134E4A; }}
[data-theme="light"] .track-date-label {{ color: var(--text-muted); }}
[data-theme="light"] .track-live-badge {{
    color: #0D9488; background: rgba(13, 148, 136, 0.1); border-color: rgba(13, 148, 136, 0.25);
}}
[data-theme="light"] .track-hero-label {{ color: var(--text-muted); }}
[data-theme="light"] .track-hero-total {{ color: #0D9488; text-shadow: none; }}
[data-theme="light"] .track-hero-range {{ color: var(--text-muted); }}
[data-theme="light"] .track-timer-inner {{
    background: rgba(255, 255, 255, 0.95);
    border-color: rgba(13, 148, 136, 0.2);
}}
[data-theme="light"] .track-timer-val {{ color: #0D9488; text-shadow: none; }}
[data-theme="light"] .track-timer-lbl {{ color: var(--text-muted); }}
[data-theme="light"] .track-hero-stat {{
    background: rgba(255, 255, 255, 0.7);
    border-color: rgba(13, 148, 136, 0.12);
}}
[data-theme="light"] .track-stat-lbl {{ color: var(--text-muted); }}
[data-theme="light"] .track-stat-val {{ color: var(--text); }}
[data-theme="light"] .track-active-panel {{
    background: linear-gradient(145deg, rgba(13, 148, 136, 0.06), rgba(99, 102, 241, 0.04));
    border-color: rgba(13, 148, 136, 0.18);
    box-shadow: 0 4px 16px rgba(13, 148, 136, 0.06);
}}
[data-theme="light"] .track-date-inline {{ color: var(--text-muted); }}
[data-theme="light"] .track-header .track-active-panel.track-active-in-header {{
    border-top-color: rgba(13, 148, 136, 0.18);
}}
[data-theme="light"] .track-header .track-stats-panel.track-stats-in-header {{
    border-top-color: rgba(13, 148, 136, 0.18);
}}
[data-theme="light"] .track-header .track-stat-card {{
    background: rgba(255, 255, 255, 0.72);
    border-color: rgba(13, 148, 136, 0.12);
}}
[data-theme="light"] .track-header .track-stat-card-lbl {{ color: var(--text-muted); }}
[data-theme="light"] .track-header .track-stat-card-val {{ color: var(--text); }}
[data-theme="light"] .track-header .track-stat-card.useful .track-stat-card-val {{ color: #059669; }}
[data-theme="light"] .track-header .track-stat-card.not .track-stat-card-val {{ color: #EA580C; }}
[data-theme="light"] .track-header .track-eff-gauge-val {{ color: #059669; }}
[data-theme="light"] .track-header .track-eff-gauge-lbl {{ color: var(--text-muted); }}
[data-theme="light"] .track-header .track-active-since {{ color: var(--text-muted); }}
[data-theme="light"] .track-header .track-label-input-prominent {{
    background: rgba(255, 255, 255, 0.92) !important;
    border-color: rgba(13, 148, 136, 0.22) !important;
    color: var(--text) !important;
}}
[data-theme="light"] .track-header .track-label-input-prominent::placeholder {{ color: var(--text-muted); }}
[data-theme="light"] .track-header .track-pick-btn-lg {{
    background: rgba(255, 255, 255, 0.85);
    border-color: rgba(13, 148, 136, 0.2);
    color: #0D9488;
}}
[data-theme="light"] .track-btn-switch {{
    background: linear-gradient(135deg, #0D9488, #14B8A6);
}}
[data-theme="light"] .track-interval-dur {{
    color: var(--running); background: var(--running-bg);
}}
[data-theme="light"] .track-empty-icon {{
    background: linear-gradient(145deg, rgba(13, 148, 136, 0.1), rgba(99, 102, 241, 0.06));
    border-color: rgba(13, 148, 136, 0.2);
}}
[data-theme="light"] .track-feature {{
    background: rgba(255, 255, 255, 0.9);
}}
[data-theme="light"] .track-feature-icon {{
    background: var(--running-bg);
}}
[data-theme="light"] .track-stats-panel,
[data-theme="light"] .track-breakdown-card {{
    background: rgba(255, 255, 255, 0.95);
}}
[data-theme="light"] .track-restart-btn {{
    background: linear-gradient(135deg, rgba(13, 148, 136, 0.08), rgba(99, 102, 241, 0.05));
    border-color: rgba(13, 148, 136, 0.25);
    color: #0D9488;
}}
[data-theme="light"] .track-timeline::before {{
    background: linear-gradient(180deg, #14B8A6 0%, var(--divider) 40%, transparent 100%);
}}
"""
