# Design tokens - single source for CSS variables

TOKENS_CSS = """
:root {
    --bg: #121212;
    --surface: #1C1C1E;
    --surface-muted: #2C2C2E;
    --surface-deep: #161616;
    --nav-bar: #0D0D0D;
    --primary: #5E5CE6;
    --primary-light: #3D5AFE;
    --success: #4DD980;
    --success-bg: #1A4028;
    --error: #FF5959;
    --error-bg: #471F1F;
    --warning: #FF7359;
    --running: #00D9C7;
    --running-bg: #143838;
    --investment: #FFB020;
    --star: #FFC208;
    --chip-edit: #7B8CDE;
    --chip-edit-bg: #1A1A40;
    --text: #FFFFFF;
    --text-muted: #8E8E93;
    --divider: #38383B;
    --overlay: rgba(0,0,0,0.72);
    --radius: 14px;
    --radius-sm: 10px;
    --shadow: 0 2px 12px rgba(61,90,254,0.25);
    --safe-top: env(safe-area-inset-top, 0px);
    --safe-bottom: env(safe-area-inset-bottom, 0px);
}

[data-theme="light"] {
    --bg: #F2F2F7;
    --surface: #FFFFFF;
    --surface-muted: #E5E5EA;
    --surface-deep: #F5F5F8;
    --nav-bar: #FFFFFF;
    --primary: #5E5CE6;
    --primary-light: #3D5AFE;
    --success: #28A745;
    --success-bg: #E6F9ED;
    --error: #DC3545;
    --error-bg: #FFECEC;
    --warning: #E8590C;
    --running: #0D9488;
    --running-bg: #E0F9F6;
    --investment: #D97706;
    --chip-edit: #5E5CE6;
    --chip-edit-bg: #EEF0FF;
    --text: #1C1C1E;
    --text-muted: #636366;
    --divider: #C6C6C8;
    --overlay: rgba(0,0,0,0.45);
    --shadow: 0 2px 12px rgba(61,90,254,0.12);
}
"""

FINANCE_CATEGORIES = [
    "\u0639\u0645\u0648\u0645\u06cc",
    "\u063a\u0630\u0627",
    "\u062d\u0645\u0644\u200c\u0648\u0646\u0642\u0644",
    "\u062e\u0627\u0646\u0647",
    "\u0642\u0628\u0648\u0636",
    "\u062a\u0641\u0631\u06cc\u062d",
    "\u062f\u0631\u0645\u0627\u0646",
    "\u0622\u0645\u0648\u0632\u0634",
]

# Income-only categories — hidden from expense budget section
BUDGET_EXCLUDED_CATEGORIES = {
    "\u062d\u0642\u0648\u0642",
}

INVESTMENT_CATEGORIES = [
    "\u0633\u0647\u0627\u0645",
    "\u0637\u0644\u0627",
    "\u0631\u0645\u0632\u0627\u0631\u0632",
    "\u0633\u067e\u0631\u062f\u0647 \u0628\u0627\u0646\u06a9\u06cc",
    "\u0635\u0646\u062f\u0648\u0642",
    "\u0627\u0645\u0644\u0627\u0643",
    "\u0633\u0627\u06cc\u0631",
]

MOOD_EMOJIS = [
    "\U0001F62D", "\U0001F61E", "\U0001F615", "\U0001F610", "\U0001F642",
    "\U0001F60A", "\U0001F604", "\U0001F929", "\U0001F973", "\U0001F60D",
]

PROJECT_COLORS = [
    "#5E5CE6",  # بنفش
    "#4DD980",  # سبز
    "#FF7359",  # قرمز
    "#FFB340",  # نارنجی
    "#5AC8FA",  # آبی
    "#FF6B9D",  # صورتی
    "#A8E063",  # سبز روشن
    "#8E8E93",  # خاکستری
]
