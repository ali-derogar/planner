# Design tokens - single source for CSS variables

TOKENS_CSS = """
:root {
    /* ── Aurora Dark palette ── */
    --bg: #0A0A0F;
    --bg-elevated: #12121A;
    --surface: #1A1A24;
    --surface-muted: #252532;
    --surface-deep: #14141C;
    --surface-glass: rgba(26, 26, 36, 0.72);
    --nav-bar: rgba(18, 18, 26, 0.85);
    --border-subtle: rgba(255, 255, 255, 0.06);

    --primary: #6366F1;
    --primary-glow: #818CF8;
    --primary-light: #4338CA;
    --success: #34D399;
    --success-bg: #0F2E22;
    --error: #FB7185;
    --error-bg: #3D1520;
    --warning: #FB923C;
    --running: #2DD4BF;
    --running-bg: #0F2E28;
    --running-glow: rgba(45, 212, 191, 0.35);
    --investment: #FBBF24;
    --star: #FBBF24;
    --chip-edit: #A5B4FC;
    --chip-edit-bg: #1E1B4B;
    --text: #F4F4F5;
    --text-muted: #71717A;
    --divider: rgba(255, 255, 255, 0.08);
    --overlay: rgba(0, 0, 0, 0.65);

    /* ── Gradients ── */
    --gradient-hero: linear-gradient(135deg, #4338CA 0%, #6366F1 45%, #A855F7 100%);
    --gradient-accent: linear-gradient(135deg, var(--primary-light), #A855F7);
    --gradient-progress: linear-gradient(90deg, var(--primary), var(--success));
    --gradient-mesh:
        radial-gradient(ellipse 80% 50% at 15% -10%, rgba(99, 102, 241, 0.12), transparent),
        radial-gradient(ellipse 60% 40% at 90% 100%, rgba(168, 85, 247, 0.08), transparent);

    /* ── Spacing ── */
    --space-1: 4px;
    --space-2: 8px;
    --space-3: 12px;
    --space-4: 16px;
    --space-5: 20px;
    --space-6: 24px;
    --space-8: 32px;

    /* ── Typography ── */
    --text-xs: 11px;
    --text-sm: 12px;
    --text-base: 14px;
    --text-md: 15px;
    --text-lg: 18px;
    --text-xl: 24px;
    --font-medium: 500;
    --font-bold: 700;

    /* ── Radius & elevation ── */
    --radius: 16px;
    --radius-sm: 12px;
    --radius-lg: 20px;
    --radius-full: 999px;
    --shadow: 0 4px 24px rgba(99, 102, 241, 0.18);
    --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.25);
    --shadow-nav: 0 8px 32px rgba(0, 0, 0, 0.45);
    --elevation-1: 0 1px 3px rgba(0, 0, 0, 0.2);
    --elevation-2: 0 4px 16px rgba(0, 0, 0, 0.28);

    /* ── Motion ── */
    --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
    --duration-fast: 150ms;
    --duration-normal: 250ms;
    --glass-blur: 16px;

    --safe-top: env(safe-area-inset-top, 0px);
    --safe-bottom: env(safe-area-inset-bottom, 0px);
    --keyboard-inset: 0px;
    --visual-vh: 100dvh;
    --vv-top: 0px;
    --vv-left: 0px;
    --vv-width: 100%;
    --vv-height: 100dvh;
}

[data-theme="light"] {
    --bg: #FAFAFC;
    --bg-elevated: #FFFFFF;
    --surface: #FFFFFF;
    --surface-muted: #F4F4F5;
    --surface-deep: #F9FAFB;
    --surface-glass: rgba(255, 255, 255, 0.82);
    --nav-bar: rgba(255, 255, 255, 0.92);
    --border-subtle: rgba(0, 0, 0, 0.06);

    --primary: #6366F1;
    --primary-glow: #818CF8;
    --primary-light: #4338CA;
    --success: #059669;
    --success-bg: #ECFDF5;
    --error: #E11D48;
    --error-bg: #FFF1F2;
    --warning: #EA580C;
    --running: #0D9488;
    --running-bg: #F0FDFA;
    --running-glow: rgba(13, 148, 136, 0.2);
    --investment: #D97706;
    --star: #F59E0B;
    --chip-edit: #6366F1;
    --chip-edit-bg: #EEF2FF;
    --text: #18181B;
    --text-muted: #71717A;
    --divider: rgba(0, 0, 0, 0.08);
    --overlay: rgba(0, 0, 0, 0.4);

    --gradient-hero: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 50%, #F5F3FF 100%);
    --gradient-accent: linear-gradient(135deg, #6366F1, #A855F7);
    --gradient-mesh:
        radial-gradient(ellipse 80% 50% at 15% -10%, rgba(99, 102, 241, 0.08), transparent),
        radial-gradient(ellipse 60% 40% at 90% 100%, rgba(168, 85, 247, 0.05), transparent);

    --shadow: 0 4px 20px rgba(99, 102, 241, 0.1);
    --shadow-sm: 0 1px 4px rgba(0, 0, 0, 0.06);
    --shadow-nav: 0 4px 24px rgba(0, 0, 0, 0.08);
    --elevation-1: 0 1px 3px rgba(0, 0, 0, 0.06);
    --elevation-2: 0 4px 16px rgba(0, 0, 0, 0.08);
}
"""

FINANCE_CATEGORIES = [
    "\u0639\u0645\u0648\u0645\u06cc",
    "\u063a\u0630\u0627",
    "\u062d\u0645\u0644\u200c\u0648\u0646\u0642\u0644",
    "\u062e\u0627\u0646\u0647",
    "\u0642\u0628\u0648\u0636",
    "\u0627\u0642\u0633\u0627\u0637",
    "\u062a\u0641\u0631\u06cc\u062d",
    "\u062f\u0631\u0645\u0627\u0646",
    "\u0622\u0645\u0648\u0632\u0634",
]

# Income-only categories — hidden from expense budget section
BUDGET_EXCLUDED_CATEGORIES = {
    "\u062d\u0642\u0648\u0642",
}

from dailyplanner.investments import all_investment_asset_labels, get_investment_taxonomy

INVESTMENT_CATEGORIES = all_investment_asset_labels()

MOOD_EMOJIS = [
    "\U0001F62D", "\U0001F61E", "\U0001F615", "\U0001F610", "\U0001F642",
    "\U0001F60A", "\U0001F604", "\U0001F929", "\U0001F973", "\U0001F60D",
]

IMPORTANT_DATE_CATEGORIES = [
    "خودرو", "اسناد", "مالی", "پزشکی", "خانه", "سایر"
]

PROJECT_COLORS = [
    "#6366F1",
    "#34D399",
    "#FB7185",
    "#FBBF24",
    "#38BDF8",
    "#F472B6",
    "#A3E635",
    "#71717A",
]
